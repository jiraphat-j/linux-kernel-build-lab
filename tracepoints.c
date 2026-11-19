/*
 * tracepoints.c - core ของตัวนับ: หา tracepoint, register/unregister probe,
 * และ implement sp_start / sp_stop / sp_get_stats / sp_target_pid
 *
 * tracepoint ของ scheduler (sched_switch ฯลฯ) ไม่ได้ export ให้ module ใช้
 * register_trace_<name>() ตรงๆ จึงหาตามชื่อด้วย for_each_kernel_tracepoint()
 * แล้วลงทะเบียนด้วย tracepoint_probe_register()
 */
#include <linux/module.h>
#include <linux/errno.h>
#include <linux/mutex.h>
#include <linux/pid.h>
#include <linux/rcupdate.h>
#include <linux/sched.h>
#include <linux/string.h>
#include <linux/tracepoint.h>
#include "sched_profiler.h"
#include "sp_internal.h"

pid_t sp_target;
atomic_long_t sp_switch_in  = ATOMIC_LONG_INIT(0);
atomic_long_t sp_switch_out = ATOMIC_LONG_INIT(0);
atomic_long_t sp_wakeups    = ATOMIC_LONG_INIT(0);
atomic_long_t sp_migrations = ATOMIC_LONG_INIT(0);

/* กัน sp_start / sp_stop ถูกเรียกพร้อมกัน (เช่น เขียน /proc จากสอง shell) */
static DEFINE_MUTEX(sp_lock);
static bool started;	/* เคย start แล้ว: get_stats อ่านค่าได้ แม้ stop ไปแล้ว */
static bool running;	/* probe ลงทะเบียนอยู่ */

struct sp_probe {
	const char *name;
	void *func;
	struct tracepoint *tp;
	bool registered;
};

static struct sp_probe sp_probes[] = {
	{ .name = "sched_switch", .func = sp_probe_sched_switch },	/* คนที่ 2 */
	/* คนที่ 3: เพิ่ม { .name = "sched_wakeup", ... } และ sched_migrate_task ตรงนี้ */
};

static void sp_match_tp(struct tracepoint *tp, void *priv)
{
	int i;

	for (i = 0; i < ARRAY_SIZE(sp_probes); i++)
		if (!sp_probes[i].tp && strcmp(tp->name, sp_probes[i].name) == 0)
			sp_probes[i].tp = tp;
}

static int sp_lookup_tracepoints(void)
{
	int i;

	for_each_kernel_tracepoint(sp_match_tp, NULL);
	for (i = 0; i < ARRAY_SIZE(sp_probes); i++) {
		if (!sp_probes[i].tp) {
			pr_err("sched_profiler: tracepoint %s not found\n",
			       sp_probes[i].name);
			return -ENOENT;
		}
	}
	return 0;
}

/* เรียกโดยถือ sp_lock แล้ว */
static void sp_unregister_all(void)
{
	int i;

	for (i = 0; i < ARRAY_SIZE(sp_probes); i++) {
		if (!sp_probes[i].registered)
			continue;
		tracepoint_probe_unregister(sp_probes[i].tp, sp_probes[i].func, NULL);
		sp_probes[i].registered = false;
	}
	/* รอให้ probe ที่กำลังรันอยู่บน CPU อื่นจบก่อน ไม่งั้น rmmod แล้ว panic */
	tracepoint_synchronize_unregister();
	running = false;
}

static void sp_reset_counters(void)
{
	atomic_long_set(&sp_switch_in, 0);
	atomic_long_set(&sp_switch_out, 0);
	atomic_long_set(&sp_wakeups, 0);
	atomic_long_set(&sp_migrations, 0);
}

static bool sp_pid_alive(pid_t nr)
{
	struct pid *p = find_get_pid(nr);
	bool alive;

	if (!p)
		return false;
	rcu_read_lock();
	alive = pid_task(p, PIDTYPE_PID) != NULL;
	rcu_read_unlock();
	put_pid(p);
	return alive;
}

int sp_start(pid_t pid)
{
	int i, ret = 0;

	if (pid <= 0)
		return -EINVAL;
	if (!sp_pid_alive(pid))
		return -ESRCH;

	mutex_lock(&sp_lock);
	if (running) {
		ret = -EBUSY;
		goto out;
	}

	ret = sp_lookup_tracepoints();
	if (ret)
		goto out;

	/* reset ก่อนตั้ง target และก่อน register เพื่อไม่ให้ค่ารอบเก่าค้าง */
	sp_reset_counters();
	WRITE_ONCE(sp_target, pid);

	for (i = 0; i < ARRAY_SIZE(sp_probes); i++) {
		ret = tracepoint_probe_register(sp_probes[i].tp, sp_probes[i].func, NULL);
		if (ret) {
			pr_err("sched_profiler: register %s failed: %d\n",
			       sp_probes[i].name, ret);
			sp_unregister_all();
			WRITE_ONCE(sp_target, 0);
			goto out;
		}
		sp_probes[i].registered = true;
	}

	running = true;
	started = true;
	pr_info("sched_profiler: start pid %d\n", pid);
out:
	mutex_unlock(&sp_lock);
	return ret;
}

void sp_stop(void)
{
	mutex_lock(&sp_lock);
	if (running) {
		sp_unregister_all();
		pr_info("sched_profiler: stop pid %d\n", sp_target);
	}
	WRITE_ONCE(sp_target, 0);
	mutex_unlock(&sp_lock);
}

int sp_get_stats(struct sched_stats *out)
{
	if (!started)
		return -ENODATA;
	out->switch_in  = atomic_long_read(&sp_switch_in);
	out->switch_out = atomic_long_read(&sp_switch_out);
	out->wakeups    = atomic_long_read(&sp_wakeups);
	out->migrations = atomic_long_read(&sp_migrations);
	return 0;
}

pid_t sp_target_pid(void)
{
	return READ_ONCE(sp_target);
}
