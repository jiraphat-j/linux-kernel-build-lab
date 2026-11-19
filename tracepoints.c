#include <linux/module.h>
#include <linux/errno.h>
#include "sched_profiler.h"

static pid_t target;
static bool started;

int sp_start(pid_t pid)
{
	if (pid <= 0)
		return -EINVAL;
	target = pid;
	started = true;
	return 0;
}

void sp_stop(void)
{
	target = 0;
}

int sp_get_stats(struct sched_stats *out)
{
	if (!started)
		return -ENODATA;
	/* ค่าตายตัว: คนที่ 2, 3 มาแทนด้วยค่าจริง */
	out->switch_in  = 10;
	out->switch_out = 9;
	out->wakeups    = 5;
	out->migrations = 2;
	return 0;
}

pid_t sp_target_pid(void)
{
	return target;
}
