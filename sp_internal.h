/*
 * sp_internal.h - ใช้ภายในระหว่าง tracepoints.c (core) กับไฟล์ probe ของคนที่ 2, 3
 * ไม่ใช่ interface ให้ procfs.c (นั่นคือ sched_profiler.h ซึ่งห้ามแก้)
 */
#ifndef SP_INTERNAL_H
#define SP_INTERNAL_H

#include <linux/atomic.h>
#include <linux/types.h>

struct task_struct;

/* PID ที่กำลังวัด (0 = ไม่ได้วัด) ใน probe ให้อ่านด้วย READ_ONCE() */
extern pid_t sp_target;

/* ตัวนับ (atomic_long_t ตามที่ตกลงใน INTERFACE.md) */
extern atomic_long_t sp_switch_in;
extern atomic_long_t sp_switch_out;
extern atomic_long_t sp_wakeups;
extern atomic_long_t sp_migrations;

/* probe_switch.c (คนที่ 2) */
void sp_probe_sched_switch(void *data, bool preempt,
			   struct task_struct *prev,
			   struct task_struct *next,
			   unsigned int prev_state);

/* probe ของคนที่ 3 (sched_wakeup, sched_migrate_task) ประกาศเพิ่มตรงนี้ */

#endif
