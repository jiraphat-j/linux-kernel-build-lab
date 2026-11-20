/*
 * probe_events.c - คนที่ 3: นับ wakeups และ migrations ของ PID เป้าหมาย
 *
 * sched_wakeup       : p = task ที่ "ถูกปลุก"  => wakeups++ ถ้า p == target
 * sched_migrate_task : p = task ที่ถูกย้าย CPU => migrations++ ถ้า p == target
 * นับตาม task->pid (thread id) ตาม INTERFACE.md
 */
#include <linux/sched.h>
#include <linux/mm_types.h>	/* struct folio: กัน warning จาก sched/numa_balancing.h */
#include <trace/events/sched.h>
#include "sp_internal.h"

void sp_probe_sched_wakeup(void *data, struct task_struct *p)
{
	pid_t t = READ_ONCE(sp_target);

	if (!t)
		return;
	if (p->pid == t)
		atomic_long_inc(&sp_wakeups);
}

void sp_probe_sched_migrate_task(void *data, struct task_struct *p, int dest_cpu)
{
	pid_t t = READ_ONCE(sp_target);

	if (!t)
		return;
	if (p->pid == t)
		atomic_long_inc(&sp_migrations);
}

/* ตรวจ signature ตอน compile (เทคนิคเดียวกับ probe_switch.c) */
static void __maybe_unused sp_events_typecheck(void)
{
	(void)sizeof(register_trace_sched_wakeup(sp_probe_sched_wakeup, NULL));
	(void)sizeof(register_trace_sched_migrate_task(sp_probe_sched_migrate_task, NULL));
}
