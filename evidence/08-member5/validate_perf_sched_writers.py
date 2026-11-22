#!/usr/bin/env python3
"""Exercise perf sched and concurrent start control in a disposable test VM."""

import errno
import json
import os
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from validate_profiler import CONTROL, command, dispose, read_stats, write


def perf_sched(out):
    target = subprocess.Popen([
        sys.executable, '-c', 'import time\nwhile True: time.sleep(0.02)',
    ])
    try:
        write(CONTROL, target.pid)
        recording = out / 'perf-sched.data'
        record = command('perf', 'sched', 'record', '-o', str(recording), '--', 'sleep', '1.5')
        (out / 'perf-sched-record.log').write_text(record)
        write(CONTROL, 0)
        result = read_stats()
        text = command('perf', 'sched', 'timehist', '-i', str(recording), '-p', str(target.pid))
        (out / 'perf-sched-timehist.log').write_text(text)
        entries = [line for line in text.splitlines() if re.search(rf'\b{target.pid}\b', line)]
        verified = bool(entries) and result['switch_out'] > 0 and result['wakeups'] > 0
        details = {'tid': target.pid, 'timehist_rows': len(entries), 'module': result, 'pass': verified}
        (out / 'perf-sched-check.json').write_text(json.dumps(details, indent=2) + '\n')
        print(f'perf sched timehist: TID {target.pid} | rows={len(entries)} | PASS={verified}', flush=True)
        for line in entries[:4]:
            print(line, flush=True)
        return verified
    finally:
        write(CONTROL, 0)
        dispose(target)


def try_start(tid, ready):
    ready.wait(timeout=5)
    try:
        write(CONTROL, tid)
    except OSError as exc:
        return tid, exc.errno
    return tid, 0


def concurrent_starts(out, rounds=25):
    targets = [subprocess.Popen(['sleep', '60']) for _ in range(2)]
    rows = []
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            for index in range(rounds):
                ready = threading.Barrier(2)
                writes = [pool.submit(try_start, target.pid, ready) for target in targets]
                first, second = [entry.result(timeout=6) for entry in writes]
                winner = next((tid for tid, status in (first, second) if status == 0), None)
                active = read_stats()['pid']
                write(CONTROL, 0)
                stopped = read_stats()['pid'] == 0
                passed = sorted((first[1], second[1])) == [0, errno.EBUSY] and active == winner and stopped
                rows.append({'round': index + 1, 'writes': [first, second], 'active_tid': active,
                             'stopped': stopped, 'pass': passed})
    finally:
        write(CONTROL, 0)
        for target in targets:
            dispose(target)
    (out / 'concurrent-writers.json').write_text(json.dumps(rows, indent=2) + '\n')
    passed = sum(row['pass'] for row in rows)
    print(f'Concurrent starts: {passed}/{rounds} PASS | one success and one EBUSY per round', flush=True)
    return passed == rounds


def run(module, out):
    if os.geteuid() != 0 or CONTROL.exists():
        raise RuntimeError('Start the test as root with the profiler unloaded')
    out.mkdir(parents=True, exist_ok=False)
    print(command('uname', '-r').strip(), flush=True)
    print(command('perf', '--version').strip(), flush=True)
    before = command('dmesg', '--color=never')
    command('insmod', str(module))
    try:
        perf_ok = False
        try:
            perf_ok = perf_sched(out)
        except subprocess.CalledProcessError as exc:
            (out / 'perf-sched-error.log').write_text(exc.output)
            print(f'perf sched exited {exc.returncode}; see perf-sched-error.log', flush=True)
        writers_ok = concurrent_starts(out)
    finally:
        command('rmmod', 'sched_profiler')
    after = command('dmesg', '--color=never')
    if not after.startswith(before):
        raise RuntimeError('Cannot isolate new dmesg entries for this run')
    delta = after[len(before):]
    (out / 'dmesg-test-window.log').write_text(delta)
    clean = not re.search(r'BUG:|Oops:|WARNING:|Call Trace:|kernel panic', delta, re.I)
    removed = not CONTROL.exists()
    print(f'Profiler unloaded: {removed} | No new kernel fault or warning: {clean}', flush=True)
    return 0 if perf_ok and writers_ok and clean and removed else 1


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Usage: sudo python3 validate_perf_sched_writers.py MODULE.ko NEW_EVIDENCE_DIR')
    sys.exit(run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()))
