# CPE333 Mini-Project 2 — ผลทดสอบของสมาชิก #5

**ผล — ผ่านสำหรับกรณีที่รัน.** `sched_profiler.ko` build และโหลดสำเร็จ. ตัวนับทั้งสี่ตรงกับ ftrace ใน workload ทั้งสาม และถอด module ได้รวม 11 รอบ. ข้อมูลมาจาก VM run `run-xdr9RD` วันที่ 22 พ.ย. 2026.

## สภาพแวดล้อม

| รายการ | ค่าที่บันทึก |
| --- | --- |
| Source | `mini2` commit `45fd877a5da9a62859f9e82d62ba810b1654cbfb` |
| VM | Ubuntu Server 26.04 LTS, VirtualBox, 2 vCPU, snapshot `before-profiler-test` |
| Kernel และ module vermagic | `7.0.0-43-generic` |
| เครื่องมือ build | GCC `15.2.0-16ubuntu1`, `pahole` `v1.31` |
| Output | `sched_profiler.ko`, 843 KiB ตาม `ls -lh` |

`make` build เฉพาะ external module. kbuild แจ้งเตือนเรื่องชื่อ executable ของ GCC โดยทั้ง kernel และ module ใช้ GCC package version เดียวกัน. ข้าม BTF ของ `.ko` เพราะไม่มี `vmlinux` ใน build tree. ทั้งสองข้อความอยู่ใน [build log](02-build.log).

## ผลเทียบตัวนับ

ทุกคู่แสดง **module / ftrace** ใน session เดียวกันและ TID เดียวกัน.

| Workload | TID | Schedule-in | Schedule-out | Wakeup | Migration | ผล |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| CPU-bound พร้อม task แย่ง CPU | 4609 | 152 / 152 | 152 / 152 | 1 / 1 | 2 / 2 | PASS |
| Sleep-heavy | 4612 | 47 / 47 | 47 / 47 | 44 / 44 | 0 / 0 | PASS |
| สลับ affinity ระหว่าง CPU 0 และ 1 | 4613 | 61 / 61 | 61 / 61 | 55 / 55 | 7 / 7 | PASS |

ใช้ ftrace instance แยกจาก tracer หลัก. กรอง `sched_switch` ด้วย `prev_pid` และ `next_pid` และกรอง `sched_wakeup` กับ `sched_migrate_task` ด้วย TID ใน field `pid`. บันทึก marker ก่อนและหลัง start/stop. ทั้งสามกรณีมีศูนย์ events ในขอบระหว่าง markers และไม่พบ trace buffer loss. ตัวนับอ้างอิงเป็นราย thread เพราะ kernel probes เทียบกับ TID ของ task.

`taskset -pc` สลับ CPU สำเร็จ 6 ครั้ง. ftrace ยังจับการย้ายจาก CPU 1 ไป CPU 0 ตอน `taskset` ตรึง workload ครั้งแรกภายในช่วงวัด จึงได้ 7 events จากทั้ง module และ ftrace. เก็บทั้ง [ผล `taskset`](run-xdr9RD/migration/taskset.log) และ [raw trace](run-xdr9RD/migration/trace.txt).

ตรวจประกอบจาก `/proc/<tid>/status` และ `/proc/<tid>/sched` รอบเดียวกัน. ผลต่าง `voluntary_ctxt_switches + nonvoluntary_ctxt_switches` และ `nr_switches` เท่ากับ 152, 47 และ 61 ตามลำดับ ตรงกับ switch-out. ผลต่าง `se.nr_migrations` เท่ากับ 2, 0 และ 7 ตรงกับ migration. เก็บ snapshots ก่อนและหลังในแต่ละโฟลเดอร์ workload เพื่อให้ตรวจซ้ำได้.

## การควบคุมและถอด module

- อ่านก่อน start ได้ `error: -61`. Input ที่ไม่ใช่ตัวเลขและ PID ติดลบคืน `EINVAL`. PID ที่ไม่พบคืน `ESRCH` และ start ซ้อนคืน `EBUSY`.
- เริ่มและหยุดด้วยข้อความที่มีช่องว่างได้. อ่านผลได้หลัง target สิ้นสุด และหลัง stop ค่า PID เป็น `0` พร้อมคงยอดตัวนับไว้. Workload ถัดไปแต่ละชุดให้ผลตรงกับ ftrace ของ session ใหม่.
- ถอด module หลังทดสอบ และทดสอบ load/unload เพิ่มอีก 10 รอบ. `/proc/sched_profiler` หายหลังจบ. สคริปต์ออกด้วยรหัส `0`.
- Kernel log ช่วงทดสอบมีข้อความ taint จาก out-of-tree และ module ที่ไม่มีลายเซ็น. ไม่พบ `BUG`, `Oops`, `WARNING`, `Call Trace` หรือ panic ใหม่ในช่วงนี้. Baseline มี watchdog soft lockup ก่อนโหลด module จึงเก็บแยกไว้ใน [watchdog baseline excerpt](run-xdr9RD/dmesg-before-watchdog.log).

## วิธีทำซ้ำใน Linux VM

ใช้ headers ที่ตรงกับ `uname -r` และสร้าง snapshot ก่อนทดสอบ. ใช้ copy ของ `validate_profiler.py` และ `run-validation.sh` จากโฟลเดอร์หลักฐาน หลัง checkout ให้คัดลอกทั้งสองไฟล์จาก `evidence/08-member5/` ไปไว้ใน `~/cpe333-evidence`.

```bash
sudo apt install build-essential pahole
cd ~/linux-kernel-build-lab
git switch --detach 45fd877
mkdir -p ~/cpe333-evidence
(set -o pipefail; make 2>&1 | tee ~/cpe333-evidence/02-build.log)
modinfo -F vermagic ./sched_profiler.ko
sudo bash ~/cpe333-evidence/run-validation.sh
```

สคริปต์ใช้ `taskset`, Python และ ftrace โดยตรง. รอบนี้มีหนึ่งรอบต่อ workload. การทดสอบไม่ได้รวม stress ของ concurrent procfs writers, unload ขณะ session ยัง active หรือการวัดแยกด้วย `perf`/`trace-cmd`.

## หลักฐานสำหรับรายงาน

- [Build log](02-build.log) และ [ภาพ build](02-build.png)
- [ผลทดสอบแบบข้อความ](run-xdr9RD/results.log) และ [ภาพผลจาก SSH ของผู้ทดสอบ](08-live-ssh-results.png)
- [CPU-bound](04-cpu-bound.png), [Sleep-heavy](05-sleep-heavy.png), [Migration](06-migration.png), [Unload](07-unload.png)
- [Kernel log เฉพาะช่วงทดสอบ](run-xdr9RD/dmesg-test-window.log)

ภาพแยกกรณีมาจากหน้าคอนโซล VirtualBox ที่แสดงข้อมูลจาก log และผลวัดที่เก็บไว้หลังการรัน. ภาพ SSH แสดงผลที่ออกตอนรันชุดทดสอบจริง.
