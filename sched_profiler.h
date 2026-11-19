#ifndef SCHED_PROFILER_H
#define SCHED_PROFILER_H

#include <linux/types.h>

struct sched_stats {
	unsigned long switch_in;
	unsigned long switch_out;
	unsigned long wakeups;
	unsigned long migrations;
};

/* tracepoints.c (คนที่ 2, 3) */
int  sp_start(pid_t pid);                  /* 0 = ok, -EINVAL, -ESRCH, -EBUSY */
void sp_stop(void);
int  sp_get_stats(struct sched_stats *out); /* 0 = ok, -ENODATA ถ้ายังไม่เคย start */
pid_t sp_target_pid(void);                 /* 0 = ไม่ได้วัดอยู่ */

/* procfs.c (คนที่ 4) */
int  sp_procfs_init(void);
void sp_procfs_exit(void);

#endif
