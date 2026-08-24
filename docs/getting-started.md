# Getting Started

This public repository hosts the Demo/Evaluation landing page, docs, and a gated demo code package.

## View locally

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## Evaluate performance claims

See [benchmark-results.md](benchmark-results.md) for tested runtime and reconstruction metrics captured from stress runs.

## Run the gated demo package

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
toroidal-demo-benchmark --length 1024 --dimensions 3 --scale 1
```

Demo limits:

- max samples: `4096`
- max dimensions: `3`
- entropy compression is disabled

## Need production access?

- Pro subscription checkout:
  - https://clearsolutions.lemonsqueezy.com/checkout/buy/f7172d35-feea-4d25-8adf-1a71b8ff992c
- Enterprise API access:
  - mailto:contact@epsilonframework.org?subject=Enterprise%20Pipeline%20Inquiry
