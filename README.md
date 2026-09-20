# CPE 333 Operating Systems: Mini-Project 1
## Ubuntu 24.04 Kernel Compilation and Installation
King Mongkut's University of Technology Thonburi (KMUTT)  
Department of Computer Engineering

---

## 1. Project Overview & Definition of Done

Build, customize, and install an Ubuntu 24.04 LTS kernel with custom suffix `cpe-os-v1`.

### Definition of Done
- [ ] Baseline captured (`uname -a`, `uname -r`, `/boot`).
- [ ] Kernel built from source into `.deb` packages.
- [ ] Kernel installed via `dpkg -i`.
- [ ] VM rebooted and booted into custom kernel.
- [ ] After-state verified (`uname -r` shows `cpe-os-v1`).
- [ ] Troubleshooting log completed.
- [ ] Teammates contributed via Git branches and PRs.
- [ ] Final report compiled in `final/final-report.pdf`.

---

## 2. Team Responsibility Matrix

| Role | Member | Git Branch | Responsibilities | Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Lead / Builder 1** | (Lead) | `main`, `build` | Repo setup, VM kernel build, PR review, final review | Scaffolding, build commands, `.deb` packages |
| **Builder 2** | (Builder 2) | `build` | Assist build, validate commands, record resource usage | `logs/build-log.md`, screenshots |
| **Report Writer 1** | (Writer 1) | `report` | Intro, environment setup, build process docs | `report/01-introduction.md`, `02-environment.md`, `03-build-process.md` |
| **Report Writer 2** | (Writer 2) | `report` | Install, boot verification, conclusion docs | `report/04-installation.md`, `05-verification.md`, `06-conclusion.md` |
| **Troubleshooting Owner** | (Troubleshooter) | `troubleshooting` | Error logs, root cause analysis, fixes | `logs/troubleshooting-log.md`, `evidence/errors/` |
| **Before/After Owner** | (Auditor) | `comparison` | Baseline and after evidence, comparison table | `comparison/before-after.md`, `evidence/before/`, `evidence/after/` |

---

## 3. Cybersecurity Relevance (DFIR / Blue Team)

- **Kernel Privilege (Ring 0):** Controls processes, memory, and system calls. Attackers below user-space evade standard EDRs.
- **DFIR Auditing:** Verifying `/boot` integrity, kernel hashes, and `uname` detects tampering.
- **Baseline Verification:** Comparing system state before and after package changes is essential for security audits.

---

## 4. Repository Structure

```text
os-mini-project-1-kernel-build/
├── README.md
├── .gitignore
├── commands/
│   ├── build-commands.md
│   └── verification-commands.md
├── report/
│   ├── 01-introduction.md
│   ├── 02-environment.md
│   ├── 03-build-process.md
│   ├── 04-installation.md
│   ├── 05-verification.md
│   └── 06-conclusion.md
├── evidence/
│   ├── before/
│   ├── build/
│   ├── install/
│   ├── after/
│   ├── grub/
│   └── errors/
├── logs/
│   ├── build-log.md
│   └── troubleshooting-log.md
├── comparison/
│   └── before-after.md
└── final/
    └── final-report.pdf
```

---

## 5. Git Workflow

### Rules
1. Do not commit directly to `main`. Use Pull Requests (PR).
2. Do not commit `.deb`, `.iso`, object files, or kernel source folders.
3. Use descriptive screenshot names (e.g., `evidence/before/uname-baseline.png`).

### Workflow Commands
```bash
# 1. Clone repo
git clone https://github.com/<your-username>/<repo-name>.git
cd os-mini-project-1-kernel-build

# 2. Checkout assigned branch (build, report, troubleshooting, comparison)
git checkout <branch-name>
git pull origin <branch-name>

# 3. Work, add, and commit
git add .
git commit -m "feat(<scope>): short description"

# 4. Push and open PR
git push origin <branch-name>
```
