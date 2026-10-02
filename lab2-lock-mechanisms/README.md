# Problem Session 08: Lock Mechanisms


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
