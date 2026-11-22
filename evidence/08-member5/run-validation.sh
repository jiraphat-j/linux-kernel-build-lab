#!/usr/bin/env bash
set -eu -o pipefail

if [[ $EUID -ne 0 || -z ${SUDO_USER:-} ]]; then
    printf 'Run this script with sudo from the Ubuntu VM.\n' >&2
    exit 1
fi

home_dir=$(getent passwd "$SUDO_USER" | cut -d: -f6)
evidence_dir="$home_dir/cpe333-evidence"
repo_dir="$home_dir/linux-kernel-build-lab"
run_dir=$(mktemp -d "$evidence_dir/run-XXXXXX")
chmod 755 "$run_dir"
printf '%s\n' "$run_dir" > "$evidence_dir/latest-run.txt"
if ! mountpoint -q /sys/kernel/tracing; then
    mount -t tracefs tracefs /sys/kernel/tracing
fi

set +e
python3 "$evidence_dir/validate_profiler.py" "$repo_dir/sched_profiler.ko" "$run_dir" 2>&1 | tee "$run_dir/results.log"
validation_status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$validation_status" > "$run_dir/exit-code.txt"
printf 'Evidence: %s\n' "$run_dir"
exit "$validation_status"
