# Evidence Catalog

This directory contains visual screenshot evidence captured during each phase of the Ubuntu Linux Kernel Build and Installation experiment.

All screenshots follow the project repository guidelines: stored in their respective structured directories and given clear, descriptive names.

---

## Directory Overview

```text
evidence/
├── before/
│   ├── uname-before.png              # Baseline system info (uname, /boot, disk, RAM)
│   ├── baseline-system-state.png     # Alias/copy of baseline system info
│   └── lscpu-hardware-spec.png       # Host CPU & VM virtualization specs
├── build/
│   ├── deps-install.png              # apt install build-essential & packaging dependencies
│   ├── build-dep-start.png           # apt-get build-dep -y linux execution start
│   ├── build-dep-finish.png          # apt-get build-dep completion & terminal prompt
│   ├── swapfile-setup.png            # 4GB swapfile creation & swapon free -h check
│   ├── config-ready.png              # scripts/config debug stripping & make olddefconfig
│   └── deb-packages-created.png      # ls -lh of 3 generated .deb packages in ~/kernel-build
├── errors/
│   └── build-error-disk-quota.png    # zstd write error: Disk quota exceeded on debug pkg
├── install/
│   └── dpkg-install-packages.png     # sudo dpkg -i of .deb packages & dracut initrd generation
└── after/
    ├── uname-after.png               # uname -r, uname -a, ls -lh /boot showing 7.0.14-cpe-os-v1
    └── uname-boot-after.png          # Alias/copy of post-boot verification
```

---

## Detailed Evidence Descriptions

### 1. `evidence/before/uname-before.png`
- **Phase:** Phase 2 (Baseline Capture)
- **Commands Shown:**
  - `uname -a`: `Linux Ubuntu 7.0.0-31-generic #31-Ubuntu SMP PREEMPT_DYNAMIC Sat Aug 1 04:26:38 UTC 2026 x86_64 GNU/Linux`
  - `uname -r`: `7.0.0-31-generic`
  - `ls -lh /boot`: Default stock kernel images (`vmlinuz-7.0.0-30-generic`, `vmlinuz-7.0.0-31-generic`)
  - `df -h`: Root partition `/dev/sda2` has 17GB available (29% used)
  - `free -h`: Base RAM 1.6 GiB total, Swap: 0B
- **Purpose:** Establishes the ground truth / baseline before any kernel compilation or package modification.

### 2. `evidence/before/lscpu-hardware-spec.png`
- **Phase:** Phase 2 (Baseline Capture / VM Diagnostics)
- **Commands Shown:**
  - `lscpu`: 4 vCPUs allocated, x86_64 architecture, AMD Ryzen 5 220 w/ Radeon 740M Graphics, Full KVM virtualization.
- **Purpose:** Documents the virtual machine hardware environment for reproducible benchmarking.

### 3. `evidence/build/deps-install.png`
- **Phase:** Phase 3 (Build Environment Setup)
- **Commands Shown:**
  - `sudo apt install -y build-essential libncurses-dev bison flex libssl-dev libelf-dev fakeroot debhelper dwarves bc cpio rsync kmod htop git`
- **Purpose:** Validates the installation of the core toolchain (compilers, parser generators, libelf/dwarves for BTF, and packaging utilities).

### 4. `evidence/build/build-dep-start.png`
- **Phase:** Phase 3 (Source Repository Dependencies)
- **Commands Shown:**
  - `sudo apt-get build-dep -y linux`
  - Package dependency solver resolving 1,754 MB of kernel build dependencies.
- **Purpose:** Proves that the source package repositories (`deb-src`) were successfully enabled and package build dependencies retrieved.

### 5. `evidence/build/build-dep-finish.png`
- **Phase:** Phase 3 (Build Dependency Completion)
- **Commands Shown:**
  - OpenJDK headless setup completion and clean return to `vboxuser@Ubuntu:~$` prompt without errors.
- **Purpose:** Confirms all kernel build dependencies are satisfied and ready for compilation.

### 6. `evidence/build/swapfile-setup.png`
- **Phase:** Phase 4 (VM Resource Optimization)
- **Commands Shown:**
  - `sudo dd if=/dev/zero of=/swapfile bs=1M count=4096 status=progress`
  - `sudo chmod 600 /swapfile`
  - `sudo mkswap /swapfile`
  - `sudo swapon /swapfile`
  - `free -h`: Shows Swap increased from 0B to 4.0Gi.
- **Purpose:** Prevents Out-Of-Memory (OOM) compilation crashes given the VM's 1.6 GiB base physical RAM.

### 7. `evidence/build/config-ready.png`
- **Phase:** Phase 5 (Kernel Configuration)
- **Commands Shown:**
  - `scripts/config --disable DEBUG_INFO`
  - `scripts/config --disable DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT`
  - `scripts/config --disable DEBUG_INFO_BTF`
  - `scripts/config --disable DEBUG_INFO_NONE`
  - `make olddefconfig`
  - Output: `# configuration written to .config`
- **Purpose:** Strips unnecessary and colossal debug symbols to save >30GB disk space, ensuring compilation fits within VM disk constraints.

### 8. `evidence/errors/build-error-disk-quota.png`
- **Phase:** Phase 5 (Compilation & Troubleshooting)
- **Commands Shown:**
  - `dpkg-deb (subprocess): compressing tar member: zstd write error: Disk quota exceeded`
  - `make[3]: *** [debian/rules:66: binary-image-dbg] Error 25`
  - Build time: `real 82m46.657s`
- **Purpose:** Serves as critical evidence for the troubleshooting log, documenting disk exhaustion when attempting to compress huge debug packages.

### 9. `evidence/build/deb-packages-created.png`
- **Phase:** Phase 5 (Kernel Build Package Output)
- **Commands Shown:**
  - `ls -lh ~/kernel-build/*.deb`
    - `linux-headers-7.0.14-cpe-os-v1_7.0.14-11_amd64.deb` (10M)
    - `linux-image-7.0.14-cpe-os-v1_7.0.14-11_amd64.deb` (107M)
    - `linux-libc-dev_7.0.14-11_amd64.deb` (1.5M)
- **Purpose:** Verifies that all 3 required Debian binary packages were produced successfully with custom suffix `cpe-os-v1`.

### 10. `evidence/install/dpkg-install-packages.png`
- **Phase:** Phase 6 (Kernel Installation)
- **Commands Shown:**
  - `sudo dpkg -i ~/kernel-build/*.deb`
  - Package unpacking and configuration
  - `dracut: Generating /boot/initrd.img-7.0.14-cpe-os-v1`
  - GRUB auto-detection and entry creation for `vmlinuz-7.0.14-cpe-os-v1`
- **Purpose:** Proves custom kernel packages were installed cleanly into the OS and boot loader.

### 11. `evidence/after/uname-after.png`
- **Phase:** Phase 7 (Post-Boot & Verification)
- **Commands Shown:**
  - `uname -r`: `7.0.14-cpe-os-v1`
  - `uname -a`: `Linux Ubuntu 7.0.14-cpe-os-v1 #11 SMP PREEMPT_DYNAMIC Sun Sep 20 14:04:33 UTC 2026 x86_64 GNU/Linux`
  - `ls -lh /boot | grep cpe-os-v1`:
    - `System.map-7.0.14-cpe-os-v1` (10M)
    - `config-7.0.14-cpe-os-v1` (302K)
    - `initrd.img-7.0.14-cpe-os-v1` (34M)
    - `vmlinuz-7.0.14-cpe-os-v1` (15M)
- **Purpose:** Ultimate verification demonstrating that the Ubuntu VM successfully booted into the newly compiled custom kernel `7.0.14-cpe-os-v1`.
