"""Export a local audio classifier to ONNX and optionally dynamic-int8 quantize it."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("HF_HOME", "./.cache/hf")

import torch
from transformers import AutoModelForAudioClassification


class LogitsOnly(torch.nn.Module):
    def __init__(self, model): super().__init__(); self.model = model
    def forward(self, input_values): return self.model(input_values=input_values).logits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("local_model", type=Path)
    parser.add_argument("output_onnx", type=Path)
    parser.add_argument("--int8", action="store_true", help="Apply ONNX Runtime dynamic int8 quantization")
    args = parser.parse_args()
    model = AutoModelForAudioClassification.from_pretrained(args.local_model, local_files_only=True, use_safetensors=True).eval().cpu()
    wrapper = LogitsOnly(model).eval()
    dummy = torch.zeros(1, 48_000, dtype=torch.float32)
    args.output_onnx.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(wrapper, dummy, str(args.output_onnx), input_names=["input_values"], output_names=["logits"],
                      dynamic_axes={"input_values": {0: "batch", 1: "samples"}, "logits": {0: "batch"}},
                      opset_version=17, dynamo=False)
    if args.int8:
        from onnxruntime.quantization import QuantType, quantize_dynamic
        quantized = args.output_onnx.with_name(args.output_onnx.stem + ".int8.onnx")
        quantize_dynamic(str(args.output_onnx), str(quantized), weight_type=QuantType.QInt8)
        print(f"Wrote dynamic-int8 model to {quantized}")
    else:
        print(f"Wrote ONNX model to {args.output_onnx}; pass --int8 to quantize")


if __name__ == "__main__": main()
