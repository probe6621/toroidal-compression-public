from __future__ import annotations

import numpy as np

UPGRADE_URL = "https://clearsolutions.lemonsqueezy.com/checkout/buy/f7172d35-feea-4d25-8adf-1a71b8ff992c"


class DemoToroidalCompressor:
    """Gated demo compressor for public evaluation workflows."""

    MAX_SAMPLES = 4096
    MAX_DIMENSIONS = 3

    def __init__(self, scale_n: int = 1):
        self.scale_n = int(scale_n)
        self.scaling_factor = (6.0 * np.pi / 5.0) ** (6.0 * self.scale_n)

    def _as_2d(self, stream: np.ndarray) -> np.ndarray:
        array = np.asarray(stream, dtype=np.float64)
        if array.ndim == 1:
            array = array.reshape(-1, 1)
        if array.ndim != 2:
            raise ValueError("Expected a 1D or 2D numeric array.")
        if array.shape[0] > self.MAX_SAMPLES:
            raise ValueError(
                f"Demo limit exceeded: max samples is {self.MAX_SAMPLES}. "
                f"Upgrade to Pro for production scales: {UPGRADE_URL}"
            )
        if array.shape[1] > self.MAX_DIMENSIONS:
            raise ValueError(
                f"Demo limit exceeded: max dimensions is {self.MAX_DIMENSIONS}. "
                f"Upgrade to Pro for production scales: {UPGRADE_URL}"
            )
        return array

    @staticmethod
    def _normalize(data: np.ndarray) -> tuple[np.ndarray, float, float]:
        min_val = float(np.min(data))
        ptp_val = float(np.ptp(data))
        span = ptp_val if ptp_val > 1e-12 else 1.0
        normalized = (data - min_val) / span
        return normalized, min_val, ptp_val

    def _project(self, stream: np.ndarray) -> np.ndarray:
        normalized, _, _ = self._normalize(stream)
        theta = normalized * (2.0 * np.pi)
        phi = np.roll(theta, shift=1, axis=0)
        major_radius = 1.0
        minor_radius = 0.4
        x = (major_radius + minor_radius * np.cos(phi)) * np.cos(theta)
        y = (major_radius + minor_radius * np.cos(phi)) * np.sin(theta)
        z = minor_radius * np.sin(phi)
        return np.stack([x, y, z], axis=-1).astype(np.float32)

    def _decode_payload(self, payload: np.ndarray, min_val: float, ptp_val: float, shape: tuple[int, int]) -> np.ndarray:
        toroidal = np.asarray(payload, dtype=np.float64) * self.scaling_factor
        x, y, z = toroidal[..., 0], toroidal[..., 1], toroidal[..., 2]
        theta = np.arctan2(y, x)
        phi = np.arctan2(z, np.hypot(x, y) - 1.0)
        normalized = np.mod((theta + phi) / (4.0 * np.pi), 1.0)
        restored = normalized * ptp_val + min_val
        return restored.reshape(shape)

    def encode_stream(
        self,
        raw_stream: np.ndarray,
        *,
        include_residuals: bool = True,
        compress_entropy: bool = False,
    ) -> dict:
        if compress_entropy:
            raise NotImplementedError(
                "Entropy compression is disabled in the demo edition. "
                f"Upgrade to Pro for production packaging: {UPGRADE_URL}"
            )
        stream = self._as_2d(raw_stream)
        payload = self._project(stream) / self.scaling_factor
        normalized, min_val, ptp_val = self._normalize(stream)
        _ = normalized  # keep intent explicit in demo pipeline
        package = {
            "payload": payload,
            "min_val": min_val,
            "ptp_val": ptp_val,
            "shape": stream.shape,
            "scale_n": self.scale_n,
            "edition": "demo",
            "limits": {
                "max_samples": self.MAX_SAMPLES,
                "max_dimensions": self.MAX_DIMENSIONS,
            },
        }
        if include_residuals:
            reconstructed = self._decode_payload(payload, min_val, ptp_val, stream.shape)
            package["residuals"] = (stream - reconstructed).astype(np.float32)
        return package

    def decode_stream(self, package: dict) -> np.ndarray:
        payload = np.asarray(package["payload"], dtype=np.float32)
        shape = tuple(package["shape"])
        restored = self._decode_payload(payload, float(package["min_val"]), float(package["ptp_val"]), shape)
        if "residuals" in package:
            restored = restored + np.asarray(package["residuals"], dtype=np.float64)
        return restored
