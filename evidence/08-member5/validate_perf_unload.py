#!/usr/bin/env python3
"""Compare two per-thread perf counters and verify active-session unload."""

import csv
import json
import os
import re
import select
import signal
import subprocess
import sys
import time
from pathlib import Path

from validate_profiler import CONTROL, command, dispose, park, read_stats, workload, write


PERF_EVENTS = ('context-switches', 'cpu-migrations')
PERF_TO_MODULE = dict(zip(PERF_EVENTS, ('switch_out', 'migrations')))


def control_perf(control_fd, ack_fd, action):
    os.write(control_fd, f'{action}\n'.encode())
    if not select.select([ack_fd], [], [], 4)[0]:
        raise RuntimeError(f'perf did not acknowledge {action}; inspect perf-stat.csv')
    # perf writes the C string terminator after the acknowledgement line.
    reply = os.read(ack_fd, 16).rstrip(b'\x00\r\n')
    if reply != b'ack':
        raise RuntimeError(f'Unexpected perf acknowledgement for {action}: {reply!r}')


def comparison(out, cpus):
    task = workload('migration', cpus[0])
    request_read, request_write = os.pipe()
    ack_read, ack_write = os.pipe()
    stat_path = out / 'perf-stat.csv'
    try:
        time.sleep(0.10)
        park(task)
        args = ['perf', 'stat', '-x,', '--no-big-num', '--delay=-1', '--timeout', '7000',
                '--control', f'fd:{request_read},{ack_write}', '-t', str(task.pid),
                '-e', ','.join(PERF_EVENTS)]
        with stat_path.open('w') as raw, subprocess.Popen(
            args, stderr=raw, pass_fds=(request_read, ack_write),
            env={**os.environ, 'LC_ALL': 'C'},
        ) as stats:
            try:
                control_perf(request_write, ack_read, 'enable')
                write(CONTROL, task.pid)
                task.send_signal(signal.SIGCONT)
                for index in range(6):
                    time.sleep(0.20)
                    command('taskset', '-pc', str(cpus[(index + 1) % 2]), str(task.pid))
                park(task)
                write(CONTROL, 0)
                control_perf(request_write, ack_read, 'disable')
                module = read_stats()
                (out / 'perf-module.txt').write_text(CONTROL.read_text())
            except BaseException:
                stats.terminate()
                raise
            if stats.wait(timeout=10):
                raise RuntimeError('perf stat failed; inspect perf-stat.csv')
        perf = {row[2]: int(row[0]) for row in csv.reader(stat_path.read_text().splitlines())
                if len(row) > 2 and row[2] in PERF_EVENTS and row[0].isdigit()}
        if set(perf) != set(PERF_EVENTS):
            raise RuntimeError('perf did not return both requested counters')
        result = {event: {'module': module[PERF_TO_MODULE[event]], 'perf': perf[event]}
                  for event in PERF_EVENTS}
        (out / 'perf-comparison.json').write_text(json.dumps({'tid': task.pid, **result}, indent=2) + '\n')
        return result
    finally:
        for fd in (request_read, request_write, ack_read, ack_write):
            os.close(fd)
        if CONTROL.exists():
            write(CONTROL, 0)
        dispose(task)


def active_unload(out, cpu):
    task = workload('sleep-heavy', cpu)
    try:
        write(CONTROL, task.pid)
        time.sleep(0.20)
        before = read_stats()
        if before['pid'] != task.pid or task.poll() is not None:
            raise RuntimeError('No live monitoring target before the unload check')
        command('rmmod', 'sched_profiler')
        removed = not CONTROL.exists()
        alive = task.poll() is None
        result = {'tid': task.pid, 'before_unload': before, 'proc_removed': removed,
                  'target_still_alive': alive, 'pass': removed and alive}
        (out / 'active-unload.json').write_text(json.dumps(result, indent=2) + '\n')
        return result
    finally:
        dispose(task)


def run(module, out):
    cpus = sorted(os.sched_getaffinity(0))
    if os.geteuid() != 0 or len(cpus) < 2 or CONTROL.exists():
        raise RuntimeError('Run as root with two usable CPUs and the module unloaded')
    out.mkdir(parents=True, exist_ok=False)
    print(command('uname', '-r').strip(), flush=True)
    print(command('perf', '--version').strip(), flush=True)
    before_log = command('dmesg', '--color=never')
    (out / 'dmesg-before.log').write_text(before_log)
    perf_ok = False
    unload_ok = False
    command('insmod', str(module))
    try:
        try:
            perf_result = comparison(out, cpus)
            perf_ok = all(counts['module'] == counts['perf'] for counts in perf_result.values())
            print('perf comparison:', json.dumps(perf_result), flush=True)
            print(f'perf counts match: {perf_ok}', flush=True)
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            (out / 'perf-error.txt').write_text(f'{exc}\n')
            print(f'perf comparison incomplete: {exc}', flush=True)
        unload_result = active_unload(out, cpus[0])
        unload_ok = unload_result['pass']
        print('active unload:', json.dumps(unload_result), flush=True)
    finally:
        if CONTROL.exists():
            command('rmmod', 'sched_profiler')
        after_log = command('dmesg', '--color=never')
        (out / 'dmesg-after.log').write_text(after_log)
    if not after_log.startswith(before_log):
        raise RuntimeError('Kernel log changed outside the test window; inspect the saved logs')
    test_log = after_log[len(before_log):]
    (out / 'dmesg-test-window.log').write_text(test_log)
    fault = re.search(r'BUG:|Oops:|WARNING:|Call Trace:|kernel panic', test_log, re.I)
    print(f'new kernel fault or warning: {bool(fault)}', flush=True)
    return 0 if perf_ok and unload_ok and not fault else 1


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Usage: sudo python3 validate_perf_unload.py MODULE.ko NEW_EVIDENCE_DIR')
    sys.exit(run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()))
