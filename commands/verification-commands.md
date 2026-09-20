# Verification & Evidence Commands

---

## 1. Baseline Capture (Before Build)

Run in Ubuntu VM before building. Save outputs to `evidence/before/`:

```bash
mkdir -p evidence/before evidence/after evidence/grub evidence/build evidence/install

uname -r | tee evidence/before/uname-r-before.txt
uname -a | tee evidence/before/uname-a-before.txt
ls -lh /boot | tee evidence/before/boot-before.txt
df -h | tee evidence/before/df-before.txt
free -h | tee evidence/before/free-before.txt
lscpu | tee evidence/before/lscpu-before.txt
dpkg -l | grep -E "linux-image|linux-headers" | tee evidence/before/dpkg-kernel-before.txt
```

Screenshots to capture:
- `evidence/before/uname-before.png`
- `evidence/before/boot-before.png`

---

## 2. Post-Boot Verification (After Install & Reboot)

Run after booting into `cpe-os-v1`. Save outputs to `evidence/after/`:

```bash
uname -r | tee evidence/after/uname-r-after.txt
uname -a | tee evidence/after/uname-a-after.txt
ls -lh /boot | tee evidence/after/boot-after.txt
df -h | tee evidence/after/df-after.txt
dpkg -l | grep -E "linux-image|linux-headers" | tee evidence/after/dpkg-kernel-after.txt
dmesg | head -n 30 | tee evidence/after/dmesg-boot-after.txt
```

Screenshots to capture:
- `evidence/grub/grub-menu.png` (GRUB menu showing new kernel)
- `evidence/after/uname-after.png` (Terminal showing `uname -r`)
- `evidence/after/boot-after.png` (Terminal showing new `/boot` files)

---

## 3. Security & Integrity Checks

```bash
sha256sum /boot/vmlinuz-* | tee evidence/after/vmlinuz-checksums.txt
cat /proc/sys/kernel/tainted | tee evidence/after/kernel-taint.txt
cat /proc/cmdline | tee evidence/after/kernel-cmdline.txt
```
