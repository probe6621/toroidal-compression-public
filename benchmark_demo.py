from __future__ import annotations

import argparse
import time

import numpy as np

from toroidal_compression_demo import DemoToroidalCompressor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Toroidal Compression demo benchmark.")
    parser.add_argument("--length", type=int, default=1024, help="Samples (max 4096 in demo).")
    parser.add_argument("--dimensions", type=int, default=3, help="Dimensions (max 3 in demo).")
    parser.add_argument("--scale", type=int, default=1, help="Scale n.")
    return parser


def generate_stream(length: int, dimensions: int) -> np.ndarray:
    t = np.linspace(0.0, 10.0 * np.pi, length, dtype=np.float64)
    axis = np.arange(1, dimensions + 1, dtype=np.float64)
    stream = np.sin(t[:, None] * axis[None, :] * 0.9)
    stream += 0.25 * np.cos(t[:, None] * axis[None, :] * 1.2)
    return stream


def main() -> None:
    args = build_parser().parse_args()
    stream = generate_stream(args.length, args.dimensions)
    codec = DemoToroidalCompressor(scale_n=args.scale)

    encode_start = time.perf_counter()
    package = codec.encode_stream(stream, include_residuals=True, compress_entropy=False)
    encode_seconds = time.perf_counter() - encode_start

    decode_start = time.perf_counter()
    restored = codec.decode_stream(package)
    decode_seconds = time.perf_counter() - decode_start

    max_abs_error = float(np.max(np.abs(restored - stream)))

    print("Edition: demo")
    print(f"Stream shape: {stream.shape}")
    print(f"Scale n: {args.scale}")
    print(f"Encode seconds: {encode_seconds:.6f}")
    print(f"Decode seconds: {decode_seconds:.6f}")
    print(f"Max absolute error: {max_abs_error:.12e}")
    print("Demo limits: max_samples=4096, max_dimensions=3")


if __name__ == "__main__":
    main()
