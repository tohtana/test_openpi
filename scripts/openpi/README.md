# Scripted OpenPI LIBERO Fine-Tune Example

This directory contains thin wrappers around the documented OpenPI `pi05_libero`
fine-tuning flow.

JAX entrypoint:

```bash
scripts/openpi/run_pi05_libero_finetune_example.sh --exp-name my_run
```

Default behavior:

- reuses `openpi/assets/pi05_libero/physical-intelligence/libero/norm_stats.json` if it already exists
- runs a bounded training example with `--num-train-steps 1`
- writes logs and manifests under `tasks/openpi-scripted-libero-finetune-example/runs/<run-id>/`
- writes checkpoints under `/mnt/local_storage/experiments/openpi_checkpoints/pi05_libero/<exp-name>/`
- sets `OPENPI_DATA_HOME=/mnt/local_storage/.cache/openpi` by default so OpenPI-downloaded weights and assets stay on local storage

To force a fresh bounded norm-stats pass before training:

```bash
scripts/openpi/run_pi05_libero_finetune_example.sh \
  --exp-name my_run \
  --refresh-norm-stats \
  --max-frames 256
```

The script sets cache-related environment variables to `/mnt/local_storage` by
default so repeated runs reuse local artifacts.

PyTorch entrypoint:

```bash
scripts/openpi/run_pi05_libero_finetune_example_pytorch.sh --exp-name my_run
```

To switch between the baseline iterative path and the packed candidate path:

```bash
scripts/openpi/run_pi05_libero_finetune_example_pytorch.sh \
  --exp-name my_run_iterative \
  --vision-encoder-image-mode iterative

scripts/openpi/run_pi05_libero_finetune_example_pytorch.sh \
  --exp-name my_run_packed \
  --vision-encoder-image-mode packed
```

To capture the same per-step timing breakdown while running the packed path:

```bash
scripts/openpi/run_pi05_libero_finetune_example_pytorch.sh \
  --exp-name my_profiled_packed_run \
  --num-train-steps 100 \
  --save-interval 100 \
  --enable-profiling \
  --profiling-warmup-steps 50 \
  --vision-encoder-image-mode packed
```

To capture a TensorBoard-compatible PyTorch profiler trace with a 50-step warmup
and 3 active steps:

```bash
scripts/openpi/run_pi05_libero_finetune_example_pytorch.sh \
  --exp-name my_timeline_run \
  --num-train-steps 53 \
  --save-interval 53 \
  --enable-torch-profiler \
  --torch-profiler-warmup-steps 50 \
  --torch-profiler-active-steps 3
```

The trace is written under
`tasks/openpi-scripted-libero-finetune-example-pytorch/<run-id>/torch_profiler/`.
To inspect it in TensorBoard:

```bash
tensorboard --logdir tasks/openpi-scripted-libero-finetune-example-pytorch/<run-id>/torch_profiler
```

Default PyTorch behavior:

- ensures the local `.venv` has OpenPI's patched `transformers` files without reusing hardlinked cache files
- resolves `gs://openpi-assets/checkpoints/pi05_base` through OpenPI's downloader and converts it to a PyTorch checkpoint if needed
- runs a bounded `scripts/train_pytorch.py pi05_libero` example with `--batch-size 4 --num-train-steps 1`
- keeps `iterative` as the default vision path and exposes `--vision-encoder-image-mode {iterative,packed}` for side-by-side measurement
- exposes `--enable-profiling` and `--profiling-warmup-steps` for per-step timing breakdowns in either vision path
- exposes `--enable-torch-profiler`, `--torch-profiler-warmup-steps`, and `--torch-profiler-active-steps` for bounded kernel timelines
- requires `--num-train-steps >= --torch-profiler-warmup-steps + --torch-profiler-active-steps` when torch profiler tracing is enabled
- writes logs and manifests under `tasks/openpi-scripted-libero-finetune-example-pytorch/<run-id>/`
- writes torch profiler traces under `tasks/openpi-scripted-libero-finetune-example-pytorch/<run-id>/torch_profiler/`
- writes checkpoints under `/mnt/local_storage/experiments/openpi_pytorch_checkpoints/pi05_libero/<exp-name>/`
- sets `OPENPI_DATA_HOME=/mnt/local_storage/.cache/openpi` by default so OpenPI-downloaded weights and assets stay on local storage
