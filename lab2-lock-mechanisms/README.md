# Problem Session 08: Lock Mechanisms

การศึกษา วิเคราะห์ และนำเสนอ Lock Mechanisms นอกเหนือจากในบทเรียน (3-6 สไลด์ต่อ Algorithm)  
ส่งสไลด์นำเสนอ (PDF) และลิงก์คลิปวิดีโอผ่าน LEB2

---

## ตารางแบ่งหน้าที่สมาชิกกลุ่ม (8 คน)

| ลำดับ | สมาชิก | หน้าที่ / หัวข้อ | ไฟล์ที่รับผิดชอบ |
| :--- | :--- | :--- | :--- |
| **คน 1** | (ระบุชื่อ) | Peterson's Algorithm: หลักการ + Pseudocode + ตัวอย่างการทำงาน | `01-peterson/pseudo.md`, `01-peterson/concept.md` |
| **คน 2** | (ระบุชื่อ) | Peterson's Algorithm: วิเคราะห์ Correctness + Performance | `01-peterson/concept.md`, `01-peterson/code/` |
| **คน 3** | บีม | Load-Linked / Store-Conditional: หลักการ + Pseudocode + ตัวอย่าง | `02-ll-sc/pseudo.md`, `02-ll-sc/concept.md` |
| **คน 4** | เฟิส | Load-Linked / Store-Conditional: วิเคราะห์ Correctness + Performance | `02-ll-sc/concept.md`, `02-ll-sc/code/` |
| **คน 5** | ฟิม | Dekker's Algorithm: หลักการ + Pseudocode + ตัวอย่าง | `03-dekker/pseudo.md`, `03-dekker/concept.md` |
| **คน 6** | โบ | Dekker's Algorithm: วิเคราะห์ Correctness + Performance | `03-dekker/concept.md`, `03-dekker/code/` |
| **คน 7** | เฟียต | Comparison: รวบรวมข้อมูลทั้ง 3 algorithms และทำตารางเปรียบเทียบ | `comparison/comparison.md` |
| **คน 8** | โดนัท | รวมงาน: รวบรวมเนื้อหา, จัด PowerPoint (3-6 หน้า/Algo), ตรวจสอบเกณฑ์ | สไลด์รวม PDF + Video link |

---

## โครงสร้างโฟลเดอร์

```text
lab2-lock-mechanisms/
├── README.md                 # ตารางหน้าที่และข้อกำหนด
├── 01-peterson/              # คน 1-2
│   ├── concept.md            # หลักการ, Correctness, Performance
│   ├── pseudo.md             # Pseudocode และ Flow การทำงาน
│   └── code/                 # โค้ดภาษา C (peterson.c)
├── 02-ll-sc/                 # คน 3-4 (บีม, เฟิส)
│   ├── concept.md            # หลักการ, Correctness, Performance
│   ├── pseudo.md             # Pseudocode และคำสั่ง hardware
│   └── code/                 # โค้ดภาษา C / Mock (llsc.c)
├── 03-dekker/                # คน 5-6 (ฟิม, โบ)
│   ├── concept.md            # หลักการ, Correctness, Performance
│   ├── pseudo.md             # Pseudocode และ Flow การทำงาน
│   └── code/                 # โค้ดภาษา C (dekker.c)
└── comparison/               # คน 7 (เฟียต)
    └── comparison.md         # ตารางสรุปเปรียบเทียบทุก Algorithm
```

---

## เกณฑ์การวิเคราะห์ในแต่ละ Algorithm (ตาม OSTEP)

1. **How it works:** Shared variables (flag, turn ฯลฯ), กลไก `lock()` และ `unlock()`
2. **Correctness (Mutual Exclusion):** ป้องกันไม่ให้เข้า Critical Section พร้อมกันได้จริงไหม เกิด Deadlock หรือไม่
3. **Fairness:** รับประกันลำดับคิวไหม เกิด Starvation (มีเธรดอดตาย) หรือไม่
4. **Performance:** Spin-wait overhead บน Single-CPU vs Multi-CPU
