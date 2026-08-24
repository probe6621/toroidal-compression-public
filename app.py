from __future__ import annotations

import io
import json
from pathlib import Path

import gradio as gr
import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from toroidal_compression_demo.codec import DemoToroidalCompressor, UPGRADE_URL

matplotlib.use("Agg")


def _generate_signal(length: int, dimensions: int, signal_type: str) -> np.ndarray:
    if length > DemoToroidalCompressor.MAX_SAMPLES:
        raise ValueError(
            f"Demo limit exceeded: max samples is {DemoToroidalCompressor.MAX_SAMPLES}. "
            f"Upgrade to Pro for production scales: {UPGRADE_URL}"
        )
    if dimensions > DemoToroidalCompressor.MAX_DIMENSIONS:
        raise ValueError(
            f"Demo limit exceeded: max dimensions is {DemoToroidalCompressor.MAX_DIMENSIONS}. "
            f"Upgrade to Pro for production scales: {UPGRADE_URL}"
        )

    t = np.linspace(0.0, 1.0, length, endpoint=False)
    if signal_type == "sine":
        base = np.sin(2.0 * np.pi * t)
    elif signal_type == "mixed":
        base = np.sin(2.0 * np.pi * 3.0 * t) + 0.35 * np.cos(2.0 * np.pi * 11.0 * t)
    elif signal_type == "step":
        base = np.sign(np.sin(2.0 * np.pi * 2.0 * t))
    else:
        raise ValueError(f"Unsupported signal type: {signal_type}")

    signals = [base]
    if dimensions >= 2:
        signals.append(np.cos(2.0 * np.pi * (t + 0.37)))
    if dimensions >= 3:
        signals.append(np.sin(2.0 * np.pi * (t * 2.5 + 0.11)))

    signal = np.column_stack(signals[:dimensions]) if dimensions > 1 else base.reshape(-1, 1)
    return np.asarray(signal, dtype=np.float64)


def _read_upload(file_obj) -> np.ndarray:
    if file_obj is None:
        raise ValueError("Upload a CSV file to test a custom signal.")

    if isinstance(file_obj, (str, Path)):
        file_path = Path(file_obj)
        text = file_path.read_text(encoding="utf-8")
    else:
        try:
            bytes_data = file_obj.read()
        except AttributeError:
            bytes_data = file_obj
        text = bytes_data.decode("utf-8") if isinstance(bytes_data, (bytes, bytearray)) else str(bytes_data)

    rows = [line for line in text.splitlines() if line.strip()]
    if not rows:
        raise ValueError("The uploaded CSV file appears to be empty.")

    try:
        array = np.genfromtxt(io.StringIO(text), delimiter=",", ndmin=2)
    except ValueError as exc:
        raise ValueError("Could not parse the uploaded file as numeric CSV data.") from exc

    array = np.asarray(array, dtype=np.float64)
    if array.ndim == 1:
        array = array.reshape(-1, 1)
    if array.ndim != 2:
        raise ValueError("Expected a 1D or 2D numeric array in CSV format.")
    if array.shape[0] > DemoToroidalCompressor.MAX_SAMPLES:
        raise ValueError(
            f"Demo limit exceeded: max samples is {DemoToroidalCompressor.MAX_SAMPLES}. "
            f"Upgrade to Pro for production scales: {UPGRADE_URL}"
        )
    if array.shape[1] > DemoToroidalCompressor.MAX_DIMENSIONS:
        raise ValueError(
            f"Demo limit exceeded: max dimensions is {DemoToroidalCompressor.MAX_DIMENSIONS}. "
            f"Upgrade to Pro for production scales: {UPGRADE_URL}"
        )
    return array


def _summarize(signal: np.ndarray, restored: np.ndarray, package: dict) -> dict:
    residual = signal - restored
    max_abs_error = float(np.max(np.abs(residual)))
    rms_error = float(np.sqrt(np.mean(residual**2)))
    relative_error = float(np.linalg.norm(residual) / max(np.linalg.norm(signal), 1e-9))

    payload_array = np.asarray(package["payload"], dtype=np.float32)
    payload_bytes = float(payload_array.nbytes)
    if "residuals" in package:
        residuals = np.asarray(package["residuals"], dtype=np.float32)
        payload_bytes += float(residuals.nbytes)
    original_bytes = float(np.asarray(signal).nbytes)
    compression_ratio = float(original_bytes / max(payload_bytes, 1e-9))

    return {
        "length": int(signal.shape[0]),
        "dimensions": int(signal.shape[1]),
        "max_abs_error": max_abs_error,
        "rms_error": rms_error,
        "relative_error": relative_error,
        "compression_ratio": compression_ratio,
        "max_samples": DemoToroidalCompressor.MAX_SAMPLES,
        "max_dimensions": DemoToroidalCompressor.MAX_DIMENSIONS,
        "edition": "demo",
        "entropy_packaging_enabled": False,
        "upgrade_url": UPGRADE_URL,
    }


def _make_plot(signal: np.ndarray, restored: np.ndarray) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 4.25))
    x_axis = np.arange(signal.shape[0])
    if signal.shape[1] == 1:
        ax.plot(x_axis, signal[:, 0], label="Input", alpha=0.85)
        ax.plot(x_axis, restored[:, 0], label="Reconstructed", alpha=0.9)
    else:
        for idx in range(signal.shape[1]):
            ax.plot(x_axis, signal[:, idx], label=f"Input dim {idx + 1}", alpha=0.8)
            ax.plot(x_axis, restored[:, idx], linestyle="--", alpha=0.8, label=f"Rebuilt dim {idx + 1}")
    ax.set_title("Toroidal Compression Demo Reconstruction")
    ax.set_xlabel("Sample index")
    ax.set_ylabel("Signal value")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    return fig


def process_signal(length: int, dimensions: int, signal_type: str, uploaded_file) -> tuple[plt.Figure, str, dict]:
    if uploaded_file is not None:
        signal = _read_upload(uploaded_file)
    else:
        signal = _generate_signal(length, dimensions, signal_type)

    compressor = DemoToroidalCompressor()
    package = compressor.encode_stream(signal, include_residuals=True, compress_entropy=False)
    restored = compressor.decode_stream(package)
    plot = _make_plot(signal, restored)
    summary = _summarize(signal, restored, package)
    summary_text = (
        "Demo mode is intentionally limited to keep the public build aligned with the open evaluation edition. "
        "The full production engine unlocks larger datasets, production packaging, and commercial deployment support."
    )
    return plot, summary_text, summary


with gr.Blocks(title="Toroidal Compression Demo") as demo:
    gr.Markdown(
        """
        # Toroidal Compression Demo

        This demo is intentionally capped to show the core topology-driven compression workflow without exposing the commercial production engine.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            length = gr.Slider(minimum=32, maximum=4096, step=32, value=512, label="Samples")
            dimensions = gr.Slider(minimum=1, maximum=3, step=1, value=2, label="Dimensions")
            signal_type = gr.Dropdown(["sine", "mixed", "step"], value="mixed", label="Signal pattern")
            uploaded_file = gr.File(label="Optional CSV upload (1D or 2D numeric data)", file_types=[".csv"])
            run_button = gr.Button("Run demo", variant="primary")
        with gr.Column(scale=2):
            plot_output = gr.Plot(label="Original vs reconstructed signal")
            summary_output = gr.JSON(label="Demo metrics")
            result_text = gr.Markdown(label="Demo notes")

    run_button.click(
        fn=process_signal,
        inputs=[length, dimensions, signal_type, uploaded_file],
        outputs=[plot_output, result_text, summary_output],
    )

    gr.Markdown(
        """
        ### Demo limitations
        - Max samples: 4096
        - Max dimensions: 3
        - Entropy packaging is disabled in this public evaluation build
        - Upgrade to Pro for a production package, managed updates, and commercial deployment terms
        """
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
