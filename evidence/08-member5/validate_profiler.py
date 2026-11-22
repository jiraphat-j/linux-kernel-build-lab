#!/usr/bin/env python3
"""Run functional tests and compare scheduler counters against isolated ftrace."""

import errno
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path


CONTROL = Path('/proc/sched_profiler')
TRACE = Path('/sys/kernel/tracing')
COUNTERS = ('switch_in', 'switch_out', 'wakeups', 'migrations')
EVENTS = ('sched_switch', 'sched_wakeup', 'sched_migrate_task')
WORKLOADS = {
    'cpu-bound': 'while True: pass',
    'sleep-heavy': 'import time\nwhile True: time.sleep(0.04)',
    'migration': 'import time\nwhile True: time.sleep(0.02)',
}


def command(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def write(path, value):
    path.write_text(f'{value}\n')


def read_stats():
    return dict((key, int(value)) for key, value in
                (line.split(':', 1) for line in CONTROL.read_text().splitlines()))


def check(condition, label):
    if not condition:
        raise RuntimeError(label)
    print(f'PASS: {label}', flush=True)


def write_error(value, expected):
    try:
        write(CONTROL, value)
    except OSError as exc:
        check(exc.errno == expected, f'{value!r}: {errno.errorcode[expected]}')
    else:
        raise RuntimeError(f'Accepted invalid or busy input {value!r}')


def workload(name, cpu):
    return subprocess.Popen(['taskset', '-c', str(cpu), sys.executable, '-c',
                             WORKLOADS[name]])


def park(task):
    task.send_signal(signal.SIGSTOP)
    _, status = os.waitpid(task.pid, os.WUNTRACED)
    if not os.WIFSTOPPED(status):
        raise RuntimeError(f'TID {task.pid} did not stop')


def dispose(task):
    task.kill()
    task.wait(timeout=5)


def proc_status(tid):
    return Path(f'/proc/{tid}/status').read_text()


def proc_sched(tid):
    return Path(f'/proc/{tid}/sched').read_text()


def trace_counts(lines, tid):
    counts = dict.fromkeys(COUNTERS, 0)
    for line in lines:
        match = re.search(r': (sched_switch|sched_wakeup|sched_migrate_task): (.*)', line)
        if not match:
            continue
        event, fields = match.groups()
        for field, key in {'sched_switch': [('next_pid', 'switch_in'), ('prev_pid', 'switch_out')],
                           'sched_wakeup': [('pid', 'wakeups')],
                           'sched_migrate_task': [('pid', 'migrations')]}[event]:
            if re.search(rf'\b{field}={tid}\b', fields):
                counts[key] += 1
    return counts


def compare_case(instance, out, name, cpus):
    case = out / name
    case.mkdir()
    task = workload(name, cpus[0])
    competitor = workload('cpu-bound', cpus[0]) if name == 'cpu-bound' else None
    try:
        park(task)
        for event in EVENTS:
            path = instance / 'events' / 'sched' / event
            expr = (f'prev_pid == {task.pid} || next_pid == {task.pid}'
                    if event == 'sched_switch' else f'pid == {task.pid}')
            write(path / 'filter', expr)
            write(path / 'enable', 1)
        write(instance / 'trace', '')
        (case / 'status-before.txt').write_text(proc_status(task.pid))
        (case / 'sched-before.txt').write_text(proc_sched(task.pid))
        write(instance / 'tracing_on', 1)
        write(instance / 'trace_marker', 'CPE333_OUTER_BEGIN')
        write(CONTROL, task.pid)
        write(instance / 'trace_marker', 'CPE333_INNER_BEGIN')
        task.send_signal(signal.SIGCONT)
        if name == 'migration':
            moves = []
            for index in range(6):
                time.sleep(0.25)
                moves.append(command('taskset', '-pc', str(cpus[(index + 1) % 2]), str(task.pid)))
            (case / 'taskset.log').write_text(''.join(moves))
        else:
            time.sleep(2)
        park(task)
        write(instance / 'trace_marker', 'CPE333_INNER_END')
        write(CONTROL, 0)
        write(instance / 'trace_marker', 'CPE333_OUTER_END')
        write(instance / 'tracing_on', 0)
        module_text = CONTROL.read_text()
        (case / 'module.txt').write_text(module_text)
        (case / 'status-after.txt').write_text(proc_status(task.pid))
        (case / 'sched-after.txt').write_text(proc_sched(task.pid))
        trace_text = (instance / 'trace').read_text()
        (case / 'trace.txt').write_text(trace_text)
        ring_stats = ''.join(f'{path.parent.name}\n{path.read_text()}\n'
                             for path in sorted(instance.glob('per_cpu/cpu*/stats')))
        (case / 'trace-stats.txt').write_text(ring_stats)
        check(bool(ring_stats) and all(int(x) == 0 for x in
              re.findall(r'(?mi)^.*(?:overrun|dropped events):\s*(\d+)', ring_stats)),
              f'{name}: no trace buffer loss')
        lines = trace_text.splitlines()
        positions = [next(i for i, line in enumerate(lines) if marker in line) for marker in
                     ('CPE333_OUTER_BEGIN', 'CPE333_INNER_BEGIN',
                      'CPE333_INNER_END', 'CPE333_OUTER_END')]
        check(positions == sorted(positions), f'{name}: trace marker order')
        outer_start, inner_start, inner_end, outer_end = positions
        inner = trace_counts(lines[inner_start + 1:inner_end], task.pid)
        outer = trace_counts(lines[outer_start + 1:outer_end], task.pid)
        module = {key: read_stats()[key] for key in COUNTERS}
        matched = all(inner[key] <= module[key] <= outer[key] for key in COUNTERS)
        exercised = {'cpu-bound': min(inner['switch_in'], inner['switch_out']) > 0,
                     'sleep-heavy': inner['wakeups'] > 0,
                     'migration': inner['migrations'] >= 6}[name]
        result = {'case': name, 'tid': task.pid, 'module': module,
                  'ftrace': inner, 'boundary_events': {key: outer[key] - inner[key]
                                                       for key in COUNTERS},
                  'pass': matched and exercised}
        (case / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result), flush=True)
        check(result['pass'], f'{name}: workload coverage and counter comparison')
    finally:
        write(instance / 'tracing_on', 0)
        (instance / 'events' / 'enable').write_text('0\n')
        write(CONTROL, 0)
        dispose(task)
        if competitor:
            dispose(competitor)


def run(module, out):
    cpus = sorted(os.sched_getaffinity(0))
    check(len(cpus) >= 2, 'at least two usable CPUs')
    check(not CONTROL.exists(), 'profiler was unloaded at start')
    out.mkdir(parents=True, exist_ok=True)
    print(command('uname', '-r').strip(), flush=True)
    print(command('modinfo', '-F', 'vermagic', str(module)).strip(), flush=True)
    (out / 'dmesg-before.log').write_text(command('dmesg', '--color=never'))
    command('insmod', str(module))
    try:
        check(read_stats() == {'error': -errno.ENODATA}, 'read before first start')
        write_error('abc', errno.EINVAL)
        write_error('-5', errno.EINVAL)
        write_error('99999999', errno.ESRCH)
        with subprocess.Popen(['sleep', '1']) as target:
            write(CONTROL, f'  {target.pid}  ')
            write_error(target.pid, errno.EBUSY)
            target.wait(timeout=3)
            check(read_stats()['pid'] == target.pid, 'read after target exit')
            write(CONTROL, '  0  ')
            stopped = read_stats()
            time.sleep(0.1)
            check(stopped['pid'] == 0 and stopped == read_stats(), 'stop retains frozen totals')
        instance = TRACE / 'instances' / f'cpe333-{os.getpid()}'
        instance.mkdir()
        try:
            write(instance / 'tracing_on', 0)
            write(instance / 'trace_clock', 'mono')
            for name in WORKLOADS:
                compare_case(instance, out, name, cpus)
        finally:
            instance.rmdir()
    finally:
        command('rmmod', 'sched_profiler')
    check(not CONTROL.exists(), 'proc entry removed after unload')
    for _ in range(10):
        command('insmod', str(module))
        command('rmmod', 'sched_profiler')
    check(not CONTROL.exists(), '10 additional load/unload cycles')
    before = (out / 'dmesg-before.log').read_text()
    after = command('dmesg', '--color=never')
    (out / 'dmesg-after.log').write_text(after)
    check(after.startswith(before), 'kernel log comparison window available')
    added = after[len(before):]
    (out / 'dmesg-test-window.log').write_text(added)
    check(not re.search(r'BUG:|Oops:|WARNING:|Call Trace:|kernel panic', added, re.I),
          'no new kernel fault or warning during tests')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Usage: sudo python3 validate_profiler.py MODULE.ko EVIDENCE_DIR')
    run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
