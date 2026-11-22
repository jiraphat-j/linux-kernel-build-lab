#include <linux/errno.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/string.h>
#include <linux/uaccess.h>
#include "sched_profiler.h"

#define SP_WRITE_MAX_LEN 32

static struct proc_dir_entry *ent;

static int sp_show(struct seq_file *m, void *v)
{
	struct sched_stats s;
	int ret = sp_get_stats(&s);

	if (ret) {
		seq_printf(m, "error: %d\n", ret);
		return 0;
	}

	seq_printf(m, "pid:        %d\n", sp_target_pid());
	seq_printf(m, "switch_in:  %lu\n", s.switch_in);
	seq_printf(m, "switch_out: %lu\n", s.switch_out);
	seq_printf(m, "wakeups:    %lu\n", s.wakeups);
	seq_printf(m, "migrations: %lu\n", s.migrations);
	return 0;
}

static int sp_open(struct inode *inode, struct file *file)
{
	return single_open(file, sp_show, NULL);
}

static ssize_t sp_write(struct file *file, const char __user *buf,
			size_t count, loff_t *ppos)
{
	char kbuf[SP_WRITE_MAX_LEN + 1];
	char *trimmed;
	int pid, ret;

	if (count == 0 || count > SP_WRITE_MAX_LEN)
		return -EINVAL;

	if (copy_from_user(kbuf, buf, count))
		return -EFAULT;

	if (memchr(kbuf, '\0', count))
		return -EINVAL;

	kbuf[count] = '\0';
	trimmed = strim(kbuf);
	if (*trimmed == '\0')
		return -EINVAL;

	ret = kstrtoint(trimmed, 10, &pid);
	if (ret)
		return ret;

	if (pid == 0) {
		sp_stop();
		return count;
	}

	ret = sp_start(pid);
	if (ret)
		return ret;

	return count;
}

static const struct proc_ops sp_ops = {
	.proc_open    = sp_open,
	.proc_read    = seq_read,
	.proc_write   = sp_write,
	.proc_lseek   = seq_lseek,
	.proc_release = single_release,
};

int sp_procfs_init(void)
{
	ent = proc_create("sched_profiler", 0666, NULL, &sp_ops);
	return ent ? 0 : -ENOMEM;
}

void sp_procfs_exit(void)
{
	proc_remove(ent);
}
