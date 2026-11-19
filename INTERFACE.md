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

## Function
- int sp_start(pid_t pid): เริ่มวัด, 0 = ok
- void sp_stop(void): หยุดวัด (ข้อกำหนด: ต้อง unregister probe ทุกตัว และเรียก tracepoint_synchronize_unregister() ให้เสร็จก่อน return เพื่อกัน kernel panic ตอน rmmod)
- int sp_get_stats(struct sched_stats *out): อ่านค่า, 0 = ok
- pid_t sp_target_pid(void): คืน PID ที่กำลังวัด, 0 = ไม่ได้วัดอยู่

## Error code
| code | เมื่อ |
|---|---|
| -EINVAL | pid <= 0 หรือข้อความไม่ใช่ตัวเลข |
| -ESRCH | ไม่พบ PID (ตรวจด้วย find_get_pid) — TODO คนที่ 2, 3 |
| -EBUSY | กำลังวัดอยู่แล้ว — TODO คนที่ 2, 3 |
| -ENODATA | ยังไม่เคย start |

(หมายเหตุ: ปัจจุบันโค้ด stub ของ sp_start คืนแค่ -EINVAL ส่วน -ESRCH และ -EBUSY ยังเป็น TODO ของคนที่ 2-3)

## ตัวนับ
ใช้ atomic_long_t ภายใน (ตกลงแล้ว) แล้วคัดลอกใส่ struct sched_stats ตอน get_stats

## รูปแบบ output (คนที่ 5 ใช้เทียบผล)
pid:        <pid>
switch_in:  <n>
switch_out: <n>
wakeups:    <n>
migrations: <n>
