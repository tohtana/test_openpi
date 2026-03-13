#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
TEST_OPENPI_ROOT = SCRIPT_DIR.parents[1]
OPENPI_ROOT = TEST_OPENPI_ROOT / "openpi"
sys.path.insert(0, str(OPENPI_ROOT / "src"))

from openpi.training import pi05_batch_profile_sweep as sweep  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sweep packed PI0.5 batch-size timing and memory profiles.")
    parser.add_argument(
        "--run-id",
        default=f"packed-profile-sweep-{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}",
    )
    parser.add_argument(
        "--artifacts-root",
        default=str(TEST_OPENPI_ROOT / "tasks" / "pi05-batch-profile-sweep"),
    )
    parser.add_argument(
        "--wrapper-script",
        default=str(TEST_OPENPI_ROOT / "scripts" / "openpi" / "run_pi05_libero_finetune_example_pytorch.sh"),
    )
    parser.add_argument(
        "--module-benchmark-script",
        default=str(OPENPI_ROOT / "scripts" / "benchmark_pi05_modules.py"),
    )
    parser.add_argument("--config-name", default="pi05_libero")
    parser.add_argument("--cuda-visible-devices", default="0")
    parser.add_argument("--vision-encoder-image-mode", default="packed", choices=("iterative", "packed"))
    parser.add_argument("--precision", default="bfloat16", choices=("bfloat16", "float32"))
    parser.add_argument("--module-step-kind", default="forward_only", choices=("forward_only", "train_like"))
    parser.add_argument("--start-batch-size", type=int, default=1)
    parser.add_argument("--max-batch-size", type=int)
    parser.add_argument("--num-train-steps", type=int, default=100)
    parser.add_argument("--save-interval", type=int, default=100)
    parser.add_argument("--log-interval", type=int, default=1)
    parser.add_argument("--profiling-warmup-steps", type=int, default=50)
    parser.add_argument("--converted-weight-dir")
    parser.add_argument("--checkpoint-base-dir")
    parser.add_argument("--jax-checkpoint-dir")
    parser.add_argument(
        "--aggregate-run-dirs",
        nargs="+",
        help="Existing sweep run directories to merge into one consolidated artifact bundle.",
    )
    parser.add_argument("--allow-overwrite", action="store_true")
    return parser.parse_args()


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_norm_stats_available() -> str:
    target_path = OPENPI_ROOT / "assets" / "pi05_libero" / "physical-intelligence" / "libero" / "norm_stats.json"
    if target_path.exists():
        return str(target_path)

    checkpoint_root = Path("/mnt/local_storage/experiments/openpi_pytorch_checkpoints/pi05_libero")
    candidates = sorted(
        checkpoint_root.glob("*/*/assets/physical-intelligence/libero/norm_stats.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise SystemExit(
            "Could not find pi05_libero norm_stats.json locally. "
            "Expected either the worktree asset or a prior checkpoint asset under "
            "/mnt/local_storage/experiments/openpi_pytorch_checkpoints/pi05_libero."
        )

    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidates[0], target_path)
    return str(target_path)


def run_command(command: list[str], *, cwd: Path, stdout_path: Path, stderr_path: Path, env: dict[str, str] | None = None):
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    return result


def build_wrapper_command(args: argparse.Namespace, batch_size: int, wrapper_runs_root: Path) -> list[str]:
    command = [
        args.wrapper_script,
        "--exp-name",
        f"{args.run_id}_b{batch_size}",
        "--run-id",
        f"b{batch_size}",
        "--batch-size",
        str(batch_size),
        "--num-train-steps",
        str(args.num_train_steps),
        "--save-interval",
        str(args.save_interval),
        "--log-interval",
        str(args.log_interval),
        "--enable-profiling",
        "--profiling-warmup-steps",
        str(args.profiling_warmup_steps),
        "--vision-encoder-image-mode",
        args.vision_encoder_image_mode,
        "--cuda-visible-devices",
        args.cuda_visible_devices,
        "--artifacts-root",
        str(wrapper_runs_root),
        "--allow-overwrite",
    ]
    if args.converted_weight_dir:
        command.extend(["--converted-weight-dir", args.converted_weight_dir])
    if args.checkpoint_base_dir:
        command.extend(["--checkpoint-base-dir", args.checkpoint_base_dir])
    if args.jax_checkpoint_dir:
        command.extend(["--jax-checkpoint-dir", args.jax_checkpoint_dir])
    return command


def evaluate_batch(
    args: argparse.Namespace,
    artifact_dir: Path,
    batch_size: int,
) -> dict[str, object]:
    batch_dir = artifact_dir / "batches" / f"b{batch_size}"
    batch_dir.mkdir(parents=True, exist_ok=True)
    wrapper_runs_root = artifact_dir / "wrapper_runs"
    wrapper_stdout = batch_dir / "wrapper.stdout.log"
    wrapper_stderr = batch_dir / "wrapper.stderr.log"
    wrapper_command = build_wrapper_command(args, batch_size, wrapper_runs_root)

    wrapper_result = run_command(
        wrapper_command,
        cwd=TEST_OPENPI_ROOT,
        stdout_path=wrapper_stdout,
        stderr_path=wrapper_stderr,
    )

    wrapper_run_dir = wrapper_runs_root / f"b{batch_size}"
    train_log_path = wrapper_run_dir / "train_pytorch.log"
    wrapper_summary_path = wrapper_run_dir / "result.json"
    combined_wrapper_text = wrapper_result.stdout + "\n" + wrapper_result.stderr
    if train_log_path.exists():
        combined_wrapper_text += "\n" + train_log_path.read_text(encoding="utf-8", errors="replace")

    if wrapper_result.returncode != 0:
        status = "oom" if sweep.is_cuda_oom(combined_wrapper_text) else "error"
        payload = {
            "batch_size": batch_size,
            "status": status,
            "failed_phase": "training_wrapper",
            "wrapper_returncode": wrapper_result.returncode,
            "wrapper_command": wrapper_command,
            "wrapper_run_dir": str(wrapper_run_dir),
        }
        write_json(batch_dir / "summary.json", payload)
        return payload

    wrapper_summary = json.loads(wrapper_summary_path.read_text(encoding="utf-8"))
    train_log_text = Path(wrapper_summary["train_log"]).read_text(encoding="utf-8", errors="replace")
    profile_records = sweep.parse_profile_lines(train_log_text)
    training_summary = sweep.summarize_training_profile(profile_records)

    benchmark_output = batch_dir / "module_memory.json"
    benchmark_stdout = batch_dir / "module_benchmark.stdout.log"
    benchmark_stderr = batch_dir / "module_benchmark.stderr.log"
    benchmark_command = [
        "uv",
        "run",
        args.module_benchmark_script,
        "--config-name",
        args.config_name,
        "--batch-size",
        str(batch_size),
        "--pytorch-weight-path",
        wrapper_summary["converted_weight_dir"],
        "--vision-encoder-image-mode",
        args.vision_encoder_image_mode,
        "--precision",
        args.precision,
        "--module-step-kind",
        args.module_step_kind,
        "--device",
        "cuda:0" if args.cuda_visible_devices else "cpu",
        "--output",
        str(benchmark_output),
    ]
    benchmark_env = {
        **dict(os.environ),
        "CUDA_VISIBLE_DEVICES": args.cuda_visible_devices,
    }
    benchmark_result = run_command(
        benchmark_command,
        cwd=OPENPI_ROOT,
        stdout_path=benchmark_stdout,
        stderr_path=benchmark_stderr,
        env=benchmark_env,
    )
    benchmark_summary = json.loads(benchmark_output.read_text(encoding="utf-8"))

    if benchmark_result.returncode != 0 or benchmark_summary["status"] != "ok":
        payload = {
            "batch_size": batch_size,
            "status": benchmark_summary["status"],
            "failed_phase": "module_benchmark",
            "wrapper_returncode": wrapper_result.returncode,
            "benchmark_returncode": benchmark_result.returncode,
            "wrapper_run_dir": str(wrapper_run_dir),
            "training_summary": training_summary,
            "module_benchmark": benchmark_summary,
        }
        write_json(batch_dir / "summary.json", payload)
        return payload

    payload = {
        "batch_size": batch_size,
        "status": "ok",
        "failed_phase": None,
        "wrapper_returncode": wrapper_result.returncode,
        "benchmark_returncode": benchmark_result.returncode,
        "wrapper_command": wrapper_command,
        "benchmark_command": benchmark_command,
        "wrapper_run_dir": str(wrapper_run_dir),
        "training_summary": training_summary,
        "module_benchmark": benchmark_summary,
    }
    write_json(batch_dir / "summary.json", payload)
    return payload


def summarize_results(results: Iterable[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], int | None, dict[str, object] | None]:
    sorted_results = sorted(results, key=lambda result: int(result["batch_size"]))
    successful = [result for result in sorted_results if result["status"] == "ok"]
    timing_rows = []
    memory_rows = []
    for result in successful:
        training_summary = result["training_summary"]
        batch_size = int(result["batch_size"])
        timing_rows.append(
            {
                "batch_size": batch_size,
                "entire_ms": training_summary["entire_ms"],
                "vision_ms": training_summary["vision_ms"],
                "llm_ms": training_summary["llm_ms"],
                "action_ms": training_summary["action_ms"],
                "entire_peak_allocated_mb": training_summary["entire_peak_allocated_mb"],
                "entire_peak_reserved_mb": training_summary["entire_peak_reserved_mb"],
                "profile_sample_count": int(training_summary["profile_sample_count"]),
            }
        )
        memory_rows.append(
            {
                "batch_size": batch_size,
                "module": "entire",
                "source": "training_profile",
                "elapsed_ms": training_summary["entire_ms"],
                "peak_allocated_mb": training_summary["entire_peak_allocated_mb"],
                "peak_reserved_mb": training_summary["entire_peak_reserved_mb"],
            }
        )
        for module in ("vision", "llm", "action"):
            module_result = result["module_benchmark"]["results"][module]
            memory_rows.append(
                {
                    "batch_size": batch_size,
                    "module": module,
                    "source": "isolated_module_benchmark",
                    "elapsed_ms": module_result["elapsed_ms"],
                    "peak_allocated_mb": module_result["peak_allocated_mb"],
                    "peak_reserved_mb": module_result["peak_reserved_mb"],
                }
            )

    max_feasible_batch_size = None if not successful else max(int(result["batch_size"]) for result in successful)
    first_failure = next((result for result in sorted_results if result["status"] != "ok"), None)
    return timing_rows, memory_rows, max_feasible_batch_size, first_failure


def write_outputs(
    artifact_dir: Path,
    *,
    manifest: dict[str, object],
    results: Iterable[dict[str, object]],
) -> None:
    timing_rows, memory_rows, max_feasible_batch_size, first_failure = summarize_results(results)
    write_json(artifact_dir / "manifest.json", manifest)
    sweep.write_csv(
        artifact_dir / "summary.csv",
        [
            "batch_size",
            "entire_ms",
            "vision_ms",
            "llm_ms",
            "action_ms",
            "entire_peak_allocated_mb",
            "entire_peak_reserved_mb",
            "profile_sample_count",
        ],
        timing_rows,
    )
    sweep.write_csv(
        artifact_dir / "memory_summary.csv",
        ["batch_size", "module", "source", "elapsed_ms", "peak_allocated_mb", "peak_reserved_mb"],
        memory_rows,
    )
    if not timing_rows:
        raise SystemExit("No feasible batch size produced a successful profile run.")
    sweep.plot_timing_curves(timing_rows, artifact_dir)

    results_payload = {
        "schema_version": 1,
        "run_id": manifest["run_id"],
        "max_feasible_batch_size": max_feasible_batch_size,
        "first_infeasible_batch_size": None if first_failure is None else first_failure["batch_size"],
        "limit_source": None if first_failure is None else first_failure["failed_phase"],
        "timing_rows": timing_rows,
        "memory_rows": memory_rows,
    }
    write_json(artifact_dir / "summary.json", results_payload)


def load_batch_results(run_dir: Path) -> list[dict[str, object]]:
    results = []
    for summary_path in sorted(run_dir.glob("batches/b*/summary.json")):
        results.append(json.loads(summary_path.read_text(encoding="utf-8")))
    if not results:
        raise SystemExit(f"No batch summaries found under {run_dir}")
    return results


def aggregate_existing_runs(args: argparse.Namespace, artifact_dir: Path) -> int:
    source_dirs = [Path(path).resolve() for path in args.aggregate_run_dirs]
    all_results = []
    for run_dir in source_dirs:
        all_results.extend(load_batch_results(run_dir))

    manifest = {
        "schema_version": 1,
        "run_id": args.run_id,
        "mode": "aggregate_existing_runs",
        "artifacts_root": str(artifact_dir),
        "source_run_dirs": [str(path) for path in source_dirs],
    }
    write_outputs(artifact_dir, manifest=manifest, results=all_results)
    return 0


def discover_maximum_batch_size(args: argparse.Namespace, artifact_dir: Path, cache: dict[int, dict[str, object]]):
    lower = 0
    current = args.start_batch_size
    first_failure: dict[str, object] | None = None
    while True:
        if args.max_batch_size is not None and current > args.max_batch_size:
            break
        result = cache.setdefault(current, evaluate_batch(args, artifact_dir, current))
        if result["status"] == "ok":
            lower = current
            current *= 2
            continue
        first_failure = result
        break

    if args.max_batch_size is not None and current > args.max_batch_size:
        return lower, None

    if first_failure is None:
        return lower, None

    upper = int(first_failure["batch_size"]) - 1
    low = lower + 1
    high = upper
    while low <= high:
        mid = (low + high) // 2
        result = cache.setdefault(mid, evaluate_batch(args, artifact_dir, mid))
        if result["status"] == "ok":
            lower = mid
            low = mid + 1
        else:
            first_failure = result
            high = mid - 1

    return lower, first_failure


def main() -> int:
    args = parse_args()
    artifact_dir = Path(args.artifacts_root) / args.run_id
    if artifact_dir.exists():
        if not args.allow_overwrite:
            raise SystemExit(f"Artifact directory already exists: {artifact_dir} (use --allow-overwrite to reuse it)")
        shutil.rmtree(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    if args.aggregate_run_dirs:
        return aggregate_existing_runs(args, artifact_dir)

    norm_stats_path = ensure_norm_stats_available()

    manifest = {
        "schema_version": 1,
        "run_id": args.run_id,
        "artifacts_root": str(artifact_dir),
        "wrapper_script": args.wrapper_script,
        "module_benchmark_script": args.module_benchmark_script,
        "config_name": args.config_name,
        "norm_stats_path": norm_stats_path,
        "cuda_visible_devices": args.cuda_visible_devices,
        "vision_encoder_image_mode": args.vision_encoder_image_mode,
        "precision": args.precision,
        "module_step_kind": args.module_step_kind,
        "num_train_steps": args.num_train_steps,
        "save_interval": args.save_interval,
        "log_interval": args.log_interval,
        "profiling_warmup_steps": args.profiling_warmup_steps,
        "start_batch_size": args.start_batch_size,
        "max_batch_size": args.max_batch_size,
    }

    cache: dict[int, dict[str, object]] = {}
    if args.max_batch_size is not None:
        for batch_size in range(args.start_batch_size, args.max_batch_size + 1):
            cache[batch_size] = evaluate_batch(args, artifact_dir, batch_size)
    else:
        max_feasible_batch_size, _ = discover_maximum_batch_size(args, artifact_dir, cache)
        for batch_size in range(args.start_batch_size, max_feasible_batch_size + 1):
            cache.setdefault(batch_size, evaluate_batch(args, artifact_dir, batch_size))

    write_outputs(artifact_dir, manifest=manifest, results=cache.values())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
