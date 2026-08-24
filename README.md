# Toroidal Compression (Demo / Evaluation Edition)

> Topology-driven compression for multi-variable telemetry, sensor streams, and structured numeric data.

[![GitHub Pages](https://github.com/probe6621/toroidal-compression-public/actions/workflows/pages.yml/badge.svg)](https://github.com/probe6621/toroidal-compression-public/actions/workflows/pages.yml)
[![Tests](https://github.com/probe6621/toroidal-compression-public/actions/workflows/pytest.yml/badge.svg)](https://github.com/probe6621/toroidal-compression-public/actions/workflows/pytest.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Quick Links

- [Live Landing Page](https://probe6621.github.io/toroidal-compression-public/)
- [Getting Started](docs/getting-started.md)
- [Benchmark Results](docs/benchmark-results.md)
- [FAQ](docs/faq.md)

## Overview

Toroidal Compression projects linear data into a toroidal manifold, applies residual correction for exact reconstruction, and optionally uses `lz4` entropy packaging at the serialization boundary.

This public Demo Edition is designed for evaluation and technical trust:

- transparent architecture and positioning
- reproducible benchmark methodology
- documented stress-test telemetry
- CI-backed repo health checks

## Run the Demo Code

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
toroidal-demo-benchmark --length 1024 --dimensions 3 --scale 1
```

Demo limits are intentionally enforced:

- max samples: `4096`
- max dimensions: `3`
- entropy packaging disabled in demo

## Demo Edition vs Pro / Enterprise

| Feature | Demo Edition (Free) | Pro / Enterprise |
| :--- | :---: | :---: |
| Landing Page + Docs | ✅ | ✅ |
| Architecture + benchmark telemetry | ✅ | ✅ |
| Commercial build package | ❌ | ✅ |
| Managed updates | ❌ | ✅ |
| Commercial deployment license | ❌ | ✅ |
| Hosted API / integration support | ❌ | ✅ |
| Priority support / SLA targets | ❌ | ✅ |

Need production access?

- [Upgrade to Pro ($149/mo)](https://clearsolutions.lemonsqueezy.com/checkout/buy/f7172d35-feea-4d25-8adf-1a71b8ff992c)
- [Request Enterprise API Access](mailto:contact@epsilonframework.org?subject=Enterprise%20Pipeline%20Inquiry)

## License

Distributed under the MIT License. See [LICENSE](/Users/paulroberts/.copilot/chats/9dc5a12f-20f3-443c-883d-4e2b93fc2b66/toroidal-compression-public/LICENSE).
