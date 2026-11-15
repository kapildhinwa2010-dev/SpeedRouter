# SpeedRouter

[![CI](https://github.com/kapildhinwa2010-dev/SpeedRouter/actions/workflows/ci.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/SpeedRouter/actions/workflows/ci.yml)
[![CodeQL](https://github.com/kapildhinwa2010-dev/SpeedRouter/actions/workflows/codeql.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/SpeedRouter/actions/workflows/codeql.yml)

Route batches to the expert predicted to serve them fastest.

## What it does

Each expert declares a latency model (base ms + per-item ms) and a maximum
batch size. For a batch of n items the router predicts every expert latency
and picks the fastest one that can accept the batch; declared cost breaks ties.

    from speedrouter import SpeedRouter

    router = SpeedRouter()
    router.add_expert("slow-start", 50.0, 0.1, max_items=1000)
    router.add_expert("fast-start", 1.0, 5.0, max_items=100)
    print(router.route_and_handle(4))

## API

- estimate_latency(base_ms, per_item_ms, n_items) - linear latency model
- SpeedExpert(name, base_ms, per_item_ms, max_items, cost)
- SpeedRouter.add_expert / route / route_and_handle / latency_report

## Honest results and limitations

- Latencies are declared estimates, not measurements. The router is only as
  honest as the numbers you give it; it does not benchmark anything itself.
- The latency model is linear in batch size; real serving often has queueing,
  caching, or batching effects it does not model.
- Cross-over behaviour depends entirely on the declared parameters.

## Status

Part of the kapildhinwa2010-dev toolkit experiments. CI and CodeQL run on
every push to main. License: MIT.
