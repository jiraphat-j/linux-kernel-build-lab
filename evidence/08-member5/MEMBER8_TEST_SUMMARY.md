# สรุปผลสำหรับสมาชิก #8

ทดสอบ scheduler profiler จาก `mini2` commit `45fd877` บน Ubuntu Server 26.04 ใน VirtualBox 2 vCPU และ kernel `7.0.0-43-generic`. Build เฉพาะ `sched_profiler.ko` ผ่าน และผลจาก module ตรงกับ ftrace ทุกตัวนับเมื่อเทียบ TID และช่วงวัดเดียวกัน.

| Workload | Schedule-in | Schedule-out | Wakeup | Migration |
| --- | ---: | ---: | ---: | ---: |
| CPU-bound | 152 | 152 | 1 | 2 |
| Sleep-heavy | 47 | 47 | 44 | 0 |
| สลับ CPU affinity | 61 | 61 | 55 | 7 |

กรณี migration นับได้ 7 ครั้งจากการตรึง CPU ครั้งแรก 1 ครั้งและสลับ CPU 6 ครั้ง. ทดสอบ input, start/stop และการสิ้นสุดของ target ผ่าน. โหลดและถอดรวม 11 รอบ โดยไม่พบ kernel fault ใหม่ในช่วงทดสอบ.

ใช้ [ภาพผลจาก SSH](08-live-ssh-results.png) หรือ [ภาพ migration](06-migration.png) ในสไลด์. รายละเอียดการเทียบ, raw logs, build warning และข้อจำกัดของผลหนึ่งรอบต่อ workload อยู่ใน [TEST_REPORT.md](TEST_REPORT.md).
