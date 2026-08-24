import numpy as np
import pytest

from toroidal_compression_demo import DemoToroidalCompressor


def test_demo_round_trip_within_limits():
    stream = np.sin(np.linspace(0, 20, 3000)).reshape(1000, 3)
    codec = DemoToroidalCompressor(scale_n=1)
    package = codec.encode_stream(stream, include_residuals=True)
    restored = codec.decode_stream(package)

    assert package["edition"] == "demo"
    assert restored.shape == stream.shape
    assert np.isfinite(restored).all()
    assert np.allclose(restored, stream, rtol=0.0, atol=1e-6)


def test_demo_limit_samples_enforced():
    stream = np.ones((5000, 2), dtype=np.float64)
    codec = DemoToroidalCompressor(scale_n=1)
    with pytest.raises(ValueError, match="max samples"):
        codec.encode_stream(stream)


def test_demo_limit_dimensions_enforced():
    stream = np.ones((128, 5), dtype=np.float64)
    codec = DemoToroidalCompressor(scale_n=1)
    with pytest.raises(ValueError, match="max dimensions"):
        codec.encode_stream(stream)


def test_demo_entropy_disabled():
    stream = np.ones((128, 2), dtype=np.float64)
    codec = DemoToroidalCompressor(scale_n=1)
    with pytest.raises(NotImplementedError, match="disabled in the demo"):
        codec.encode_stream(stream, compress_entropy=True)
