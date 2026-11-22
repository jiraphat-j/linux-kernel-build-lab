#include <linux/module.h>
#include <linux/kernel.h>
#include "sched_profiler.h"

static int __init sp_init(void)
{
	int ret = sp_procfs_init();
	if (ret)
		return ret;
	pr_info("sched_profiler: loaded\n");
	return 0;
}

static void __exit sp_exit(void)
{
	/* Drain procfs callbacks before the final stop. */
	sp_procfs_exit();
	sp_stop();
	pr_info("sched_profiler: unloaded\n");
}

module_init(sp_init);
module_exit(sp_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("CPE333 Mini-project 2 group");
MODULE_DESCRIPTION("Process scheduler profiler");
