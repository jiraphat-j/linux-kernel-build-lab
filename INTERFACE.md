# Scheduler Profiler: Interface

โครงสร้าง: module เดียว `sched_profiler.ko` รวมจากหลายไฟล์ .c
ห้ามแก้ sched_profiler.h ฝ่ายเดียว ต้องแจ้งในกลุ่มและแก้ไฟล์นี้ก่อน

## ข้อมูลไหล
/proc/sched_profiler --(write PID)--> procfs.c --sp_start(pid)--> tracepoints.c
/proc/sched_profiler <--(read)-- procfs.c <--sp_get_stats()-- tracepoints.c

## ใครทำอะไร
| ไฟล์ | เจ้าของ | หน้าที่ |
|---|---|---|
| main.c, Makefile, sched_profiler.h | คนที่ 1 | init/exit, build |
| tracepoints.c | คนที่ 2, 3 | ตัวนับ + tracepoint |
| procfs.c | คนที่ 4 | รับ PID / แสดงผล |

## Function
- int sp_start(pid_t pid): เริ่มวัด, 0 = ok
- void sp_stop(void): หยุดวัด
- int sp_get_stats(struct sched_stats *out): อ่านค่า, 0 = ok

## Error code
| code | เมื่อ |
|---|---|
| -EINVAL | pid <= 0 หรือข้อความไม่ใช่ตัวเลข |
| -ESRCH | ไม่พบ PID |
| -EBUSY | กำลังวัดอยู่แล้ว |
| -ENODATA | ยังไม่เคย start |

## ตัวนับ
ใช้ atomic_long_t ภายใน (ตกลงแล้ว) แล้วคัดลอกใส่ struct sched_stats ตอน get_stats

## รูปแบบ output (คนที่ 5 ใช้เทียบผล)
pid:        <pid>
switch_in:  <n>
switch_out: <n>
wakeups:    <n>
migrations: <n>
