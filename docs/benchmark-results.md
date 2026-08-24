# Benchmark Results

Stress-test telemetry summary from the core build:

- High-volume benchmark: `100000 x 5`, `n=2`, entropy enabled
  - Raw bytes: `4,000,000`
  - Serialized package bytes: `9,993,751`
  - Encode time: `0.297 s`
  - Decode time: `0.042 s`
  - Max absolute reconstruction error: `1.11e-16`

Sweep coverage executed successfully across:

- scale factors: `n = 1, 2, 3`
- shapes: `10000x5`, `50000x3`, `50000x5`
- entropy modes: enabled and disabled

Raw sweep output is included as JSON data at `assets/data/benchmark-highlights.json`.
