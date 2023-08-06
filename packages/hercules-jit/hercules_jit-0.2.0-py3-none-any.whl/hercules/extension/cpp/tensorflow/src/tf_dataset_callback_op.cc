// Copyright 2022 ByteDance Ltd. and/or its affiliates.
/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

#include <hercules/pipeline/tx_session.h>
#include <hercules/runtime/utf8_util.h>

#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/op_kernel.h"

#include "tf_utils.h"

namespace {
typedef Eigen::ThreadPoolDevice CPUDevice;
typedef tensorflow::gtl::InlinedVector<tensorflow::int64, 4> ShapeContainer;

class HerculesTFDatasetCallbackOp : public tensorflow::OpKernel {
 private:
  ::hercules::runtime::OpKernel* op_impl_ = nullptr;

  void initAttributes(tensorflow::OpKernelConstruction* context) {
    std::string op_addr_s;
    TF_CHECK_OK(context->GetAttr("op_addr", &op_addr_s));
    auto op_addr = std::strtoull(op_addr_s.c_str(), nullptr, 10);
    CHECK(op_addr != 0);
    // TODO: check we need own this ptr
    op_impl_ = static_cast<::hercules::runtime::OpKernel*>((void*)(op_addr));
  }

 public:
  explicit HerculesTFDatasetCallbackOp(tensorflow::OpKernelConstruction* context)
      : tensorflow::OpKernel(context) {
    // Get attr
    initAttributes(context);
  }

  void Compute(tensorflow::OpKernelContext* context) override;
};

template <typename Iterator>
void SetMultiResult(Iterator first, Iterator last, tensorflow::OpKernelContext* context) {
  for (int i = 0; first != last; ++first, ++i) {
    ::hercules::runtime::tf_utils::ToTFTensor(
        first->template As<::hercules::runtime::NDArray>(), context, i);
  }
}

void HerculesTFDatasetCallbackOp::Compute(tensorflow::OpKernelContext* context) {
  // the last input is output shape spec
  const int num_inputs = context->num_inputs();
  std::vector<ShapeContainer> shapes(num_inputs);

  // Prepare op inputs
  std::vector<::hercules::runtime::RTValue> values;
  values.reserve(num_inputs);

  for (int i = 0; i < num_inputs; ++i) {
    // Grab the input tensor
    auto& input_tensor = context->input(i);

    // Create shape container, should keep ref during execution
    shapes[i] = input_tensor.shape().dim_sizes();
    const auto ndims = input_tensor.shape().dims();

    switch (input_tensor.dtype()) {
      case tensorflow::DT_STRING: {
        const auto& flatten = input_tensor.flat<tensorflow::tstring>();
        if (ndims == 0u) {
          auto& value = flatten(0);
          // TODO: zero copy
          // ::hercules::runtime::string_view value_view(value.data(), value.size());
          // values.emplace_back(::hercules::runtime::RTView(value_view));
          values.emplace_back(::hercules::runtime::RTValue(
              ::hercules::runtime::String(value.data(), value.size())));
        } else if (ndims == 1u) {
          size_t sz = input_tensor.dim_size(0);
          auto list = ::hercules::runtime::List();
          list.reserve(sz);
          for (size_t i = 0; i < sz; ++i) {
            auto& value_i = flatten(i);
            list.append(::hercules::runtime::RTValue(
                ::hercules::runtime::String(value_i.data(), value_i.size())));
          }
          values.emplace_back(std::move(list));
        } else {
          context->SetStatus(tensorflow::Status(tensorflow::error::INVALID_ARGUMENT,
                                                "string tensor only support dim=0/1"));
          return;
        }
      } break;
      case tensorflow::DT_FLOAT: {
        if (ndims == 0u) {
          values.emplace_back(::hercules::runtime::RTValue(input_tensor.scalar<float>()(0)));
        } else {
          auto tx_tensor = ::hercules::runtime::tf_utils::FromTFTensor(input_tensor);
          values.emplace_back(std::move(tx_tensor));
        }
      } break;
      case tensorflow::DT_DOUBLE: {
        if (ndims == 0u) {
          values.emplace_back(::hercules::runtime::RTValue(input_tensor.scalar<double>()(0)));
        } else {
          auto tx_tensor = ::hercules::runtime::tf_utils::FromTFTensor(input_tensor);
          values.emplace_back(std::move(tx_tensor));
        }
      } break;
      case tensorflow::DT_INT32: {
        if (ndims == 0u) {
          int32_t value = input_tensor.scalar<tensorflow::int32>()(0);
          values.emplace_back(::hercules::runtime::RTValue(value));
        } else {
          auto tx_tensor = ::hercules::runtime::tf_utils::FromTFTensor(input_tensor);
          values.emplace_back(std::move(tx_tensor));
        }
      } break;
      case tensorflow::DT_INT64: {
        if (ndims == 0u) {
          int64_t value = input_tensor.scalar<tensorflow::int64>()(0);
          values.emplace_back(::hercules::runtime::RTValue(value));
        } else {
          auto tx_tensor = ::hercules::runtime::tf_utils::FromTFTensor(input_tensor);
          values.emplace_back(std::move(tx_tensor));
        }
      } break;
      default: {
        context->SetStatus(tensorflow::Status(
            tensorflow::error::INVALID_ARGUMENT,
            "unsupported tensorflow dtype: " + tensorflow::DataType_Name(input_tensor.dtype())));
        return;
      }
    }
  }

  ::hercules::runtime::RTValue result;
  try {
    result = op_impl_->Process(::hercules::runtime::PyArgs(values.data(), values.size()));
  } catch (std::exception& e) {
    context->SetStatus(tensorflow::Status(tensorflow::error::ABORTED, e.what()));
    return;
  } catch (...) {
    context->SetStatus(
        tensorflow::Status(tensorflow::error::ABORTED, "run hercules op failed!!!"));
    return;
  }

  // output to tensorflow
  switch (result.type_code()) {
    case ::hercules::runtime::TypeIndex::kRuntimeNDArray: {
      ::hercules::runtime::tf_utils::ToTFTensor(
          result.AsNoCheck<::hercules::runtime::NDArray>(), context, 0);
    } break;
    case ::hercules::runtime::TypeIndex::kRuntimeTuple: {
      auto multi_outputs = result.AsNoCheck<::hercules::runtime::Tuple>();
      SetMultiResult(multi_outputs.begin(), multi_outputs.end(), context);
    } break;
    case ::hercules::runtime::TypeIndex::kRuntimeList: {
      auto multi_outputs = result.AsNoCheck<::hercules::runtime::List>();
      SetMultiResult(multi_outputs.begin(), multi_outputs.end(), context);
    } break;
    default: {
      auto errmsg = "unsupported hercules result type: " + result.type_name();
      context->SetStatus(tensorflow::Status(tensorflow::error::INTERNAL,
                                            tensorflow::StringPiece(errmsg.data(), errmsg.size())));
      return;
    } break;
  }
  // end
}

REGISTER_KERNEL_BUILDER(Name("HerculesTFDatasetCallbackOp").Device(tensorflow::DEVICE_CPU),
                        HerculesTFDatasetCallbackOp);

REGISTER_OP("HerculesTFDatasetCallbackOp")
    .Input("input_args: ListT")
    .Attr("ListT: list({string, float32, float64, int32, int64})")
    .Output("output: output_dtype")
    .Attr("op_addr: string")
    .Attr("output_dtype: list({float32, int32, int64})");

}  // namespace
