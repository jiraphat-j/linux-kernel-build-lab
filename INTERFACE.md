# Scheduler Profiler: Interface

โครงสร้าง: module เดียว `sched_profiler.ko` รวมจากหลายไฟล์ .c
ห้ามแก้ sched_profiler.h ฝ่ายเดียว ต้องแจ้งในกลุ่มและแก้ไฟล์นี้ก่อน

## ข้อมูลไหล
/proc/sched_profiler --(write PID)--> procfs.c --sp_start(pid)--> tracepoints.c
/proc/sched_profiler <--(read)-- procfs.c <--sp_get_stats()-- tracepoints.c

วิธีใช้งาน:
- เขียน PID เข้า `/proc/sched_profiler` = เริ่มวัด
- เขียน `0` เข้า `/proc/sched_profiler` = หยุดวัด
- อ่านค่าจาก `/proc/sched_profiler` = แสดงผลสถิติ

## ใครทำอะไร
| ไฟล์ | เจ้าของ | หน้าที่ |
|---|---|---|
| main.c, Makefile, sched_profiler.h | คนที่ 1 | init/exit, build |
| tracepoints.c | คนที่ 2, 3 | ตัวนับ + tracepoint |
| procfs.c | คนที่ 4 | รับ PID / แสดงผล |

การแยกไฟล์ของคนที่ 2 กับ 3 (เช่น `probe_switch.c`, `probe_events.c`) ต้องตกลงในกลุ่มก่อน แล้วเพิ่มใน `sched_profiler-y` ของ Makefile

ข้อเสนอการแยกไฟล์ (คนที่ 2):
| ไฟล์ | เจ้าของ | หน้าที่ |
|---|---|---|
| tracepoints.c | คนที่ 2 (core), คนที่ 3 เพิ่มแค่ 2 บรรทัดในตาราง `sp_probes[]` | หา tracepoint ตามชื่อ, register/unregister, ตัวนับ, sp_start/stop/get_stats |
| sp_internal.h | คนที่ 2, 3 | ประกาศตัวนับ + prototype ของ probe (ใช้ภายใน ไม่ใช่ของ procfs.c) |
| probe_switch.c | คนที่ 2 | probe sched_switch -> switch_in / switch_out |
| probe_events.c | คนที่ 3 | probe sched_wakeup, sched_migrate_task -> wakeups / migrations |

## Function
- int sp_start(pid_t pid): เริ่มวัด, 0 = ok
- void sp_stop(void): หยุดวัด (ข้อกำหนด: ต้อง unregister probe ทุกตัว และเรียก tracepoint_synchronize_unregister() ให้เสร็จก่อน return เพื่อกัน kernel panic ตอน rmmod)
- int sp_get_stats(struct sched_stats *out): อ่านค่า, 0 = ok
- pid_t sp_target_pid(void): คืน PID ที่กำลังวัด, 0 = ไม่ได้วัดอยู่

## Error code
| code | เมื่อ |
|---|---|
| -EINVAL | pid <= 0 หรือข้อความไม่ใช่ตัวเลข |
| -ESRCH | ไม่พบ PID (ตรวจด้วย find_get_pid + pid_task) |
| -EBUSY | กำลังวัดอยู่แล้ว (ต้องเขียน 0 เพื่อหยุดก่อน) |
| -ENOENT | หา tracepoint ตามชื่อใน kernel ไม่เจอ (ดู dmesg) |
| -ENODATA | ยังไม่เคย start |

หมายเหตุ: นับตาม `task->pid` (thread id) เหมือน `prev_pid` / `next_pid` ใน ftrace
ถ้าโปรแกรมมีหลาย thread จะนับเฉพาะ thread ที่ระบุ

## ตัวนับ
ใช้ atomic_long_t ภายใน (ตกลงแล้ว) แล้วคัดลอกใส่ struct sched_stats ตอน get_stats

## รูปแบบ output (คนที่ 5 ใช้เทียบผล)
pid:        <pid>
switch_in:  <n>
switch_out: <n>
wakeups:    <n>
migrations: <n>
