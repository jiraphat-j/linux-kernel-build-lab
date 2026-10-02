# Problem Session 08: Lock Mechanisms

---

## โครงสร้างโฟลเดอร์

```text
lab2-lock-mechanisms/
├── README.md
├── 01-peterson/
│   ├── concept.md
│   ├── pseudo.md
│   └── code/
├── 02-ll-sc/
│   ├── concept.md
│   ├── pseudo.md
│   └── code/
├── 03-dekker/
│   ├── concept.md
│   ├── pseudo.md
│   └── code/
└── comparison/
    └── comparison.md
```

---

## หัวข้อการวิเคราะห์ในแต่ละ Algorithm

1. **How it works:** Shared variables และกลไก `lock()` / `unlock()`
2. **Correctness (Mutual Exclusion):** ป้องกันการเข้า Critical Section พร้อมกัน และปราศจาก Deadlock
3. **Fairness:** Bounded waiting และการป้องกัน Starvation
4. **Performance:** Spin-wait overhead บน Single-Core เทียบกับ Multi-Core
