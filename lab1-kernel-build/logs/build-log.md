# Kernel Build Execution Log (Builder 2)

- **Role:** Builder 2 (Build Assistant & Evidence Capture)
- **Git Branch:** `build`
- **Target Kernel:** Ubuntu Linux 7.0.14 (`7.0.14-cpe-os-v1`)
- **Execution Date:** September 20, 2026
- **Status:** **SUCCESSFUL** (Kernel compiled, packaged into `.deb`, installed, and booted verified)

---

## 1. Environment & VM Specifications

Captured from initial VM diagnostics prior to build:

| Parameter | Specification / Observed Value | Evidence Screenshot |
| :--- | :--- | :--- |
| **Guest OS** | Ubuntu Linux (x86_64) | [`evidence/before/uname-before.png`](../evidence/before/uname-before.png) |
| **Baseline Kernel** | `7.0.0-31-generic` (`#31-Ubuntu SMP PREEMPT_DYNAMIC Sat Aug 1 04:26:38 UTC 2026`) | [`evidence/before/uname-before.png`](../evidence/before/uname-before.png) |
| **Virtualization** | Oracle VirtualBox / KVM Full Virtualization | [`evidence/before/lscpu-hardware-spec.png`](../evidence/before/lscpu-hardware-spec.png) |
| **vCPU Allocation** | 4 Cores (Host: AMD Ryzen 5 220 w/ Radeon 740M Graphics) | [`evidence/before/lscpu-hardware-spec.png`](../evidence/before/lscpu-hardware-spec.png) |
| **Base Memory (RAM)**| 1.6 GiB Total (1.1 GiB used, 520 MiB available) | [`evidence/before/uname-before.png`](../evidence/before/uname-before.png) |
| **Swap Space (Added)**| 4.0 GiB swapfile configured at `/swapfile` | [`evidence/build/swapfile-setup.png`](../evidence/build/swapfile-setup.png) |
| **Storage Allocation**| Root partition `/dev/sda2`: 25 GiB total (6.7 GiB used, 17 GiB free / 29% use) | [`evidence/before/uname-before.png`](../evidence/before/uname-before.png) |

---

## 2. Step-by-Step Command Validation & Execution

### Phase 2: Baseline Capture
```bash
# Check baseline kernel version and full system release
uname -a
uname -r

# Check initial boot directory artifacts
ls -lh /boot

# Verify initial disk and RAM capacity
df -h
free -h
lscpu
```
- **Observed Result:** System running baseline kernel `7.0.0-31-generic`. Root disk has 17GB available; RAM is 1.6GB without swap.
- **Evidence:** 
  - [`evidence/before/uname-before.png`](../evidence/before/uname-before.png)
  - [`evidence/before/lscpu-hardware-spec.png`](../evidence/before/lscpu-hardware-spec.png)

---

### Phase 3: Build Dependencies & Source Repo Setup
```bash
# 1. Install toolchain and compiler utilities
sudo apt install -y build-essential libncurses-dev bison flex libssl-dev libelf-dev fakeroot debhelper dwarves bc cpio rsync kmod htop git

# 2. Fetch Ubuntu kernel build dependencies
sudo apt-get build-dep -y linux
```
- **Purpose:** Prepares GCC, Make, parser generators (bison, flex), ELF manipulation tools (libelf-dev, dwarves for BTF/pahole), packaging helpers (debhelper, fakeroot), and kernel dependencies (requires 1,754 MB download).
- **Evidence:**
  - [`evidence/build/deps-install.png`](../evidence/build/deps-install.png) (Prerequisites installed)
  - [`evidence/build/build-dep-start.png`](../evidence/build/build-dep-start.png) (Build dependency resolution)
  - [`evidence/build/build-dep-finish.png`](../evidence/build/build-dep-finish.png) (Dependency completion)

---

### Phase 4: Virtual Memory Expansion (Swapfile)
Because VM base memory was 1.6 GiB, compiling with multiple threads would trigger OOM (Out Of Memory) killer. A 4.0 GiB swapfile was created:
```bash
# Allocate swapfile
sudo dd if=/dev/zero of=/swapfile bs=1M count=4096 status=progress

# Set secure permissions
sudo chmod 600 /swapfile

# Format and activate swap
sudo mkswap /swapfile
sudo swapon /swapfile

# Verify swap status
free -h
```
- **Observed Result:** Swap initialized to `4.0Gi` total.
- **Evidence:** [`evidence/build/swapfile-setup.png`](../evidence/build/swapfile-setup.png)

---

### Phase 5: Kernel Source Configuration
```bash
# Disable bloated debug information to reduce compilation time and disk usage
scripts/config --disable DEBUG_INFO
scripts/config --disable DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT
scripts/config --disable DEBUG_INFO_BTF
scripts/config --disable DEBUG_INFO_NONE

# Apply configuration defaults
make olddefconfig
```
- **Purpose:** Stripping debug info reduces build disk footprint by >30GB and compilation time from multi-hours to manageable duration. Output writes directly to `.config`.
- **Evidence:** [`evidence/build/config-ready.png`](../evidence/build/config-ready.png)

---

### Phase 6: Compilation and Debian Package Creation
```bash
make -j4 bindeb-pkg
```
- **Build Metrics:**
  - **Execution Time:** `82m46.657s` (Real: 82m46s, User: 45m2.1s, Sys: 28m54.4s)
  - **Error Encountered:** `zstd write error: Disk quota exceeded` during building `linux-image-*-dbg` (debug symbols package), recorded in [`evidence/errors/build-error-disk-quota.png`](../evidence/errors/build-error-disk-quota.png).
  - **Outcome:** The required kernel installation debian packages were generated successfully in `~/kernel-build/`:
    1. `linux-headers-7.0.14-cpe-os-v1_7.0.14-11_amd64.deb` (10 MB)
    2. `linux-image-7.0.14-cpe-os-v1_7.0.14-11_amd64.deb` (107 MB)
    3. `linux-libc-dev_7.0.14-11_amd64.deb` (1.5 MB)
- **Evidence:** [`evidence/build/deb-packages-created.png`](../evidence/build/deb-packages-created.png)

---

### Phase 7: Kernel Installation
```bash
sudo dpkg -i ~/kernel-build/*.deb
```
- **Purpose:** Installs custom kernel modules, headers, and vmlinuz image. Automatically invokes `dracut` to create initial RAM disk (`/boot/initrd.img-7.0.14-cpe-os-v1`) and updates GRUB boot configurations.
- **Evidence:** [`evidence/install/dpkg-install-packages.png`](../evidence/install/dpkg-install-packages.png)

---

### Phase 8: Reboot & Post-Boot Verification
```bash
# Check current active kernel
uname -r
# Expected output: 7.0.14-cpe-os-v1

# Check full system info
uname -a

# Inspect /boot files for custom kernel
ls -lh /boot | grep cpe-os-v1
```
- **Observed Result:**
  - `uname -r` -> `7.0.14-cpe-os-v1`
  - `uname -a` -> `Linux Ubuntu 7.0.14-cpe-os-v1 #11 SMP PREEMPT_DYNAMIC Sun Sep 20 14:04:33 UTC 2026 x86_64 GNU/Linux`
  - Boot files present in `/boot`:
    - `System.map-7.0.14-cpe-os-v1` (10M)
    - `config-7.0.14-cpe-os-v1` (302K)
    - `initrd.img-7.0.14-cpe-os-v1` (34M)
    - `vmlinuz-7.0.14-cpe-os-v1` (15M)
- **Evidence:** [`evidence/after/uname-after.png`](../evidence/after/uname-after.png)

---

## 3. Evidence Index & File Mapping

| Screenshot File Name | Evidence Location | Description |
| :--- | :--- | :--- |
| `uname-before.png` | `evidence/before/` | Pre-build baseline: `uname -a`, `uname -r`, `/boot` listing, `df -h`, `free -h` |
| `lscpu-hardware-spec.png` | `evidence/before/` | Hardware & CPU virtualization specifications (AMD Ryzen 5, 4 vCPUs) |
| `deps-install.png` | `evidence/build/` | `apt install build-essential` and core kernel packaging tools |
| `build-dep-start.png` | `evidence/build/` | `apt-get build-dep -y linux` initial package resolution and download |
| `build-dep-finish.png` | `evidence/build/` | Completion of build dependencies setup |
| `swapfile-setup.png` | `evidence/build/` | Creation and activation of 4GB swapfile to prevent OOM errors |
| `config-ready.png` | `evidence/build/` | Debug symbol stripping and `make olddefconfig` generation of `.config` |
| `deb-packages-created.png`| `evidence/build/` | Verification of 3 generated `.deb` packages (image, headers, libc-dev) |
| `build-error-disk-quota.png` | `evidence/errors/` | Build log error: disk quota exceeded on debug package compression |
| `dpkg-install-packages.png` | `evidence/install/` | `dpkg -i` installation of debian packages and dracut initramfs generation |
| `uname-after.png` | `evidence/after/` | Post-boot verification confirming active kernel `7.0.14-cpe-os-v1` |

---

## 4. Conclusion & Confirmation
The custom kernel build process succeeded. The system now boots into `7.0.14-cpe-os-v1` with custom suffix verification. All build metrics, commands, and screenshot evidence have been cataloged and validated.
