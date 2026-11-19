/*
 * probe_switch.c - คนที่ 2: นับ schedule in / schedule out ด้วย tracepoint sched_switch
 *
 * sched_switch เกิดทุกครั้งที่ CPU เปลี่ยนจาก task prev ไปเป็น task next
 *   prev == target -> target ถูกเอาออกจาก CPU  => switch_out++
 *   next == target -> target ได้ขึ้น CPU        => switch_in++
 * (event เดียวกันจะไม่มี prev == next เพราะ scheduler ไม่ switch ถ้าเป็น task เดิม)
 */
#include <linux/sched.h>
#include <trace/events/sched.h>
#include "sp_internal.h"

void sp_probe_sched_switch(void *data, bool preempt,
			   struct task_struct *prev,
			   struct task_struct *next,
			   unsigned int prev_state)
{
	pid_t t = READ_ONCE(sp_target);

	/* กัน PID 0 (idle/swapper) ถูกนับตอน start/stop */
	if (!t)
		return;

	if (prev->pid == t)
		atomic_long_inc(&sp_switch_out);
	if (next->pid == t)
		atomic_long_inc(&sp_switch_in);
}

/*
 * ตรวจตอน compile ว่า signature ของ probe ตรงกับ TP_PROTO ของ sched_switch
 * ใน headers ของ kernel ที่ใช้อยู่ ถ้าไม่ตรง compiler จะ error
 * (incompatible pointer type) แทนที่จะไปพังตอนรัน
 * sizeof() ไม่ได้เรียกฟังก์ชันจริง จึงไม่ต้องใช้ symbol __tracepoint_sched_switch
 * ที่ kernel ไม่ได้ export ให้ module
 */
static void __maybe_unused sp_switch_typecheck(void)
{
	(void)sizeof(register_trace_sched_switch(sp_probe_sched_switch, NULL));
}
