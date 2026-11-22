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

ตรวจประกอบจาก `/proc/<tid>/status` และ `/proc/<tid>/sched` รอบเดียวกัน. ผลต่าง `voluntary_ctxt_switches + nonvoluntary_ctxt_switches` และ `nr_switches` เท่ากับ 152, 47 และ 61 ตามลำดับ ตรงกับ switch-out. ผลต่าง `se.nr_migrations` เท่ากับ 2, 0 และ 7 ตรงกับ migration. ดู [ข้อมูล `/proc` ก่อนและหลังทั้งสาม workload](run-xdr9RD/proc-snapshots.txt).

## การควบคุมและถอด module

- อ่านก่อน start ได้ `error: -61`. Input ที่ไม่ใช่ตัวเลขและ PID ติดลบคืน `EINVAL`. PID ที่ไม่พบคืน `ESRCH` และ start ซ้อนคืน `EBUSY`.
- เริ่มและหยุดด้วยข้อความที่มีช่องว่างได้. อ่านผลได้หลัง target สิ้นสุด และหลัง stop ค่า PID เป็น `0` พร้อมคงยอดตัวนับไว้. Workload ถัดไปแต่ละชุดให้ผลตรงกับ ftrace ของ session ใหม่.
- ถอด module หลังทดสอบ และทดสอบ load/unload เพิ่มอีก 10 รอบ. `/proc/sched_profiler` หายหลังจบ. สคริปต์ออกด้วยรหัส `0`.
- Kernel log ช่วงทดสอบมีข้อความ taint จาก out-of-tree และ module ที่ไม่มีลายเซ็น. ไม่พบ `BUG`, `Oops`, `WARNING`, `Call Trace` หรือ panic ใหม่ในช่วงนี้. Baseline มี watchdog soft lockup ก่อนโหลด module.

## วิธีทำซ้ำใน Linux VM

ใช้ headers ที่ตรงกับ `uname -r` และสร้าง snapshot ก่อนทดสอบ. รันจาก checkout ที่มีโฟลเดอร์ `evidence/08-member5` เพื่อคัดลอกสคริปต์ก่อนสลับไปยัง commit ที่วัดจริง.

```bash
sudo apt install build-essential pahole
cd ~/linux-kernel-build-lab
mkdir -p ~/cpe333-evidence
cp evidence/08-member5/{validate_profiler.py,run-validation.sh} ~/cpe333-evidence/
git switch --detach 45fd877
(set -o pipefail; make 2>&1 | tee ~/cpe333-evidence/02-build.log)
modinfo -F vermagic ./sched_profiler.ko
sudo bash ~/cpe333-evidence/run-validation.sh
```

สคริปต์ใช้ `taskset`, Python และ ftrace โดยตรง. ตารางด้านบนมาจากหนึ่งรอบต่อ workload. ดูผลทดสอบ `perf` และ lifecycle รอบเพิ่มเติมด้านล่าง.

## หลักฐานสำหรับรายงาน

- [Build log](02-build.log)
- [ผลทดสอบแบบข้อความ](run-xdr9RD/results.log) และ [ผลเทียบแบบ JSON](run-xdr9RD/comparison.json)
- ftrace ราย workload [CPU-bound](run-xdr9RD/cpu-bound/trace.txt) · [Sleep-heavy](run-xdr9RD/sleep-heavy/trace.txt) · [Migration](run-xdr9RD/migration/trace.txt)
- [Kernel log เฉพาะช่วงทดสอบ](run-xdr9RD/dmesg-test-window.log)

## ผลรอบเพิ่มเติม

ทดสอบ commit `45fd877` บน Ubuntu Server 26.04 ใน VirtualBox 2 vCPU, kernel `7.0.0-43-generic` และ `perf 7.0.14`. ผลด้านล่างมาจากการรันใหม่แยกจากตาราง ftrace ด้านบน.

| การทดสอบ | ผลจริง |
| --- | --- |
| `perf stat` ต่อ TID `4146` | `context-switches` 62 ตรงกับ `switch_out` 62. `cpu-migrations` 6 ตรงกับ `migrations` 6 |
| `rmmod` ขณะกำลังเฝ้า TID `4309` | ถอดสำเร็จ, `/proc/sched_profiler` หาย และ target ยังทำงาน |
| `perf sched timehist` ต่อ TID `1899` | พบ 73 แถวใน timeline ของ target. การเทียบตัวนับใช้ `perf stat` และ ftrace |
| ส่ง start พร้อมกันจากตัวเขียน 2 ตัว | ผ่าน 25/25 รอบ. ทุกรอบมีหนึ่งคำสั่งสำเร็จ อีกคำสั่งได้ `EBUSY` และ PID ที่แสดงตรงกับคำสั่งที่สำเร็จ |

ทั้งสองชุดออกด้วยรหัส `0`. Kernel log ช่วงทดสอบไม่พบ fault หรือ warning ใหม่.

เก็บ [ผลทดสอบแยกกรณี](followup/results.json), [perf stat CSV](followup/perf-stat.csv), [perf sched timehist](followup/perf-sched-timehist.log), [kernel log](followup/dmesg-test-windows.log) และ [ภาพคอนโซล VM ขณะรันจริง](followup/terminal-live.png).

ทำซ้ำใน VM ที่มี `perf` ตรงกับ kernel โดยคัดลอกสคริปต์เพิ่มไปคู่กับ `validate_profiler.py` ใน `~/cpe333-evidence` ก่อนสลับไป build ที่ commit ที่ทดสอบ. ทั้งสองคำสั่งสร้างโฟลเดอร์ผลใหม่.

```bash
sudo python3 ~/cpe333-evidence/validate_perf_unload.py \
  ./sched_profiler.ko ~/cpe333-evidence/perf-unload-run
sudo python3 ~/cpe333-evidence/validate_perf_sched_writers.py \
  ./sched_profiler.ko ~/cpe333-evidence/perf-sched-writers-run
```
