PWD := $(CURDIR)

obj-m += sched_profiler.o
sched_profiler-y := main.o tracepoints.o procfs.o probe_switch.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules
clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
