# Troubleshooting Log

- **Role:** Troubleshooting Owner
- **Git Branch:** `troubleshooting`
- **Scope:** Every problem hit during the kernel build and install, with root cause, fix, and evidence. Incidents are listed in chronological order. Phase numbers follow [`logs/build-log.md`](build-log.md).

---

## 1. Environments

Two VMs were used. The build that produced the final kernel ran on the **Builder VM**.

| Item | Builder VM | Troubleshooter VM |
| :--- | :--- | :--- |
| Prompt | `vboxuser@Ubuntu` | `tassawan@tassawan-VirtualBox` |
| Hypervisor | Oracle VirtualBox | Oracle VirtualBox |
| Ubuntu release | Same kernel as troubleshooter VM (see note) | Ubuntu 26.04.1 LTS (`resolute`) |
| Baseline kernel | `7.0.0-31-generic` | `7.0.0-31-generic` |
| vCPU | 4 (host: AMD Ryzen 5 220) | 2 |
| RAM | 1.6 GiB at baseline, raised to 3.3 GiB before build | 3.3 GiB |
| Root disk (`/dev/sda2`) | 25 GB (17 GB free at baseline) | 7.8 GB (746 MB free) |
| `/tmp` | `tmpfs`, 821 MB | not captured |
| Build method | `make -j4 bindeb-pkg` with `localversion` = `-cpe-os-v1` | not built yet |

> **Note:** `README.md` says Ubuntu 24.04, but both VMs run kernel `7.0.0-31-generic` from the `resolute` (26.04) archive. The Canonical guide linked in the assignment uses `fakeroot debian/rules binary`; this team used the upstream `make bindeb-pkg` target instead. The report must state and justify this.

---

## 2. Incident Summary

| ID | Time (2026) | Phase | Title | Severity | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| TS-01 | 09-19 19:10 | 2 | Troubleshooter VM too small to build | High | OPEN |
| TS-02 | 09-19 23:43 | 3 | `deb-src` still not active after editing `ubuntu.sources` | Medium | OPEN |
| TS-03 | 09-20 13:30 | 4 | Low RAM, no swap: OOM risk for `make -j4` | Medium | RESOLVED |
| TS-04 | 09-20 ≈13:35 | 5 | Typo in `scripts/config` left debug info enabled | High | ROOT CAUSE of TS-05 |
| TS-05 | 09-20 ≈14:58 | 6 | `Disk quota exceeded` while packing the `-dbg` package | High | WORKAROUND |
| TS-06 | 09-20 | 7 | Custom `linux-libc-dev` replaced the distro package | Low | OPEN |

---

## 3. Incident Details

### TS-01: Troubleshooter VM too small to build

| Attribute | Details |
| :--- | :--- |
| **Phase** | Phase 2: Baseline capture |
| **Timestamp** | 2026-09-19 19:10 |
| **Severity** | High (blocks build on this VM) |
| **Observation** | `df -h /` showed `/dev/sda2` 7.8 GB total, 6.7 GB used, **746 MB free (91%)**. `nproc` = 2, `free -h` = 3.3 GiB RAM, 0 B swap. |
| **Root Cause** | VM was created with the VirtualBox default disk size. A kernel build needs roughly 30 GB free (Canonical guide minimum); source unpacking alone needs about 2 GB. |
| **Fix / Solution** | Recreate the VM with a **60 GB dynamically allocated** disk, 4 vCPU and 6–8 GB RAM if the host allows. Recreating is safer than resizing the `.vdi` and then growing the partition with GParted. |
| **Evidence** | [`evidence/errors/ts01-vm-spec-insufficient.png`](../evidence/errors/ts01-vm-spec-insufficient.png) |
| **Resolution Status** | **OPEN.** Not blocking the team, because the final build ran on the Builder VM. |

---

### TS-02: `deb-src` still not active after editing `ubuntu.sources`

| Attribute | Details |
| :--- | :--- |
| **Phase** | Phase 3: Source repo setup |
| **Timestamp** | 2026-09-19 23:43 (edit), 23:58 (error) |
| **Severity** | Medium (blocks `apt source` and `apt build-dep`) |
| **Error Message** | `Error: You must put some 'deb-src' URIs in your sources.list` (from both `apt source --print-uris ...` and `sudo apt build-dep -y linux ...`) |
| **Root Cause (most likely)** | Both blocks in `/etc/apt/sources.list.d/ubuntu.sources` were changed to `Types: deb deb-src`, but the nano title bar still shows `ubuntu.sources *`, meaning the file was **not saved**. The following `sudo apt update` fetched only `Packages` indexes and no `Sources` indexes, which confirms that apt did not see any `deb-src` entry. |
| **Secondary issue** | The check command was typed as `apt source --print-uris linux-image-unsigned-$(uname -r) head`; the pipe `\|` before `head` is missing. |
| **Fix / Solution** | 1. Reopen the file, press `Ctrl+O` then `Enter` to save, `Ctrl+X` to exit.<br>2. `sudo apt update`, which must now show `... Sources` lines.<br>3. `apt source --print-uris linux-image-unsigned-$(uname -r) \| head` must print URLs.<br>Alternative used on the Builder VM: `sudo sed -i 's/^Types: deb$/Types: deb deb-src/' /etc/apt/sources.list.d/ubuntu.sources` |
| **Evidence** | [`evidence/errors/ts02-ubuntu-sources-unsaved.png`](../evidence/errors/ts02-ubuntu-sources-unsaved.png), [`evidence/errors/ts02-deb-src-error.png`](../evidence/errors/ts02-deb-src-error.png) |
| **Resolution Status** | **OPEN** on the troubleshooter VM (needs the verification output from step 3). Not an issue on the Builder VM: `apt-get build-dep -y linux` succeeded there ([`evidence/build/build-dep-start.png`](../evidence/build/build-dep-start.png)). |

---

### TS-03: Low RAM, no swap: OOM risk for `make -j4`

| Attribute | Details |
| :--- | :--- |
| **Phase** | Phase 4: Virtual memory expansion |
| **Timestamp** | 2026-09-20 13:30 |
| **Severity** | Medium (preventive) |
| **Observation** | Baseline `free -h` showed **1.6 GiB RAM, 0 B swap**. Four parallel GCC jobs can exceed this and trigger the OOM killer. |
| **Fix / Solution** | 1. VM RAM raised to **3.3 GiB** (the `free -h` in the swap screenshot shows `Mem: 3.3Gi`).<br>2. 4 GiB swapfile created: `sudo dd if=/dev/zero of=/swapfile bs=1M count=4096`, `sudo chmod 600 /swapfile`, `sudo mkswap /swapfile`, `sudo swapon /swapfile`.<br>3. Two typos along the way (`sudosawpon`, `sudo sawpon`) returned `command not found` and were corrected to `swapon`. |
| **Side effects** | The swapfile sits on the root disk and uses 4 GB of the 17 GB that were free. It is not in `/etc/fstab`, so it disappears after reboot unless added there. |
| **Evidence** | [`evidence/before/uname-before.png`](../evidence/before/uname-before.png) (1.6 GiB, 0 B swap), [`evidence/build/swapfile-setup.png`](../evidence/build/swapfile-setup.png) (3.3 GiB + 4.0 GiB swap) |
| **Resolution Status** | **RESOLVED.** RAM + swap = about 7.3 GiB. The build finished its compile stage with no OOM kill (`real 82m40.657s`). |

---

### TS-04: Typo in `scripts/config` left debug info enabled

| Attribute | Details |
| :--- | :--- |
| **Phase** | Phase 5: Kernel source configuration |
| **Timestamp** | 2026-09-20, before build start (≈13:35, derived from the end time minus `real 82m40s`) |
| **Severity** | High (caused TS-05) |
| **Commands actually run** | `scripts/config --disable DEBUG_INFO`<br>`scripts/config --disable DEBUG_INFO_DWARF_TOOLCHAIN_DFFAULT`<br>`scripts/config --disable DEBUG_INFO_BTF`<br>`scripts/config --disable DEBUG_INFO_NONE`<br>`make olddefconfig` |
| **Root Cause** | Two mistakes:<br>1. **Typo:** `DFFAULT` instead of `DEFAULT`. `scripts/config` does not validate names, so it silently edited a non-existent option and `DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT` stayed **enabled**.<br>2. **Wrong direction:** `DEBUG_INFO_NONE` is the choice that means "no debug info"; it must be **enabled**, not disabled.<br>Proof that debug info stayed on: `bindeb-pkg` only builds a `linux-image-*-dbg` package when `CONFIG_DEBUG_INFO=y`, and the build log shows it building `linux-image-7.0.14-cpe-os-v1-dbg`. |
| **Fix / Solution** | Correct commands (these also match `commands/build-commands.md` Step 4):<br>`scripts/config --enable DEBUG_INFO_NONE`<br>`scripts/config --disable DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT`<br>`scripts/config --disable DEBUG_INFO_DWARF4`<br>`scripts/config --disable DEBUG_INFO_DWARF5`<br>`scripts/config --disable DEBUG_INFO_BTF`<br>`make olddefconfig`<br>`grep -E 'DEBUG_INFO' .config` must show `CONFIG_DEBUG_INFO_NONE=y` and no `CONFIG_DEBUG_INFO=y`. |
| **Evidence** | [`evidence/build/config-ready.png`](../evidence/build/config-ready.png) (typo visible on line 2) |
| **Resolution Status** | **Documented.** Applies to the next build (Mini-Project 2). The installed kernel was built with debug info still enabled. |

---

### TS-05: `Disk quota exceeded` while packing the `-dbg` package

| Attribute | Details |
| :--- | :--- |
| **Phase** | Phase 6: Compilation and Debian package creation (`make -j4 bindeb-pkg`) |
| **Timestamp** | 2026-09-20 ≈14:58 (the error appears right after `linux-libc-dev` was built; that `.deb` is timestamped 14:58) |
| **Severity** | High (build exits with an error) |
| **Error Message** | `dpkg-deb (subprocess): compressing tar member: zstd write error: Disk quota exceeded`<br>`dh_builddeb: error: dpkg-deb --root-owner-group --build debian/linux-image-7.0.14-cpe-os-v1-dbg .. died with signal 13`<br>`make[3]: *** [debian/rules:66: binary-image-dbg] Error 25`<br>`make: *** [Makefile:248: __sub-make] Error 2` |
| **Root Cause** | **Direct cause:** because of TS-04, the build had to pack a debug-symbols package. With full DWARF for every module, this package is several GB before compression.<br>**Why "quota" and not "no space":** a full ext4 disk normally reports `No space left on device` (ENOSPC). `Disk quota exceeded` (EDQUOT) points at a size limit on the write target instead. The root disk had 17 GB free at baseline, but `/tmp` is a **821 MB `tmpfs`**, and `dpkg-deb` stages compressed members in the temp directory. The most likely explanation is that the `-dbg` data exceeded the `/tmp` limit. Disk use of the build tree plus the 4 GB swapfile (TS-03) may also have contributed. |
| **Verification (pending)** | Run on the Builder VM and attach output:<br>`findmnt /tmp` (look for `tmpfs` and any `quota` option)<br>`df -h / /tmp`<br>`du -sh ~/kernel-build` |
| **Fix / Solution** | **What the team did:** the three required packages were already created in the same run before the failure (`linux-image` 107 MB at 14:51, `linux-headers` 10 MB at 14:53, `linux-libc-dev` 1.5 MB at 14:58). The `-dbg` package is not needed to boot, so the team proceeded to install. There is no evidence of a re-run after the error.<br>**Permanent fix for the next build:** apply the corrected config from TS-04, and if a debug package is ever needed, point temp files at the real disk: `mkdir -p ~/kernel-build/tmp && export TMPDIR=~/kernel-build/tmp` before `make bindeb-pkg`. |
| **Evidence** | [`evidence/errors/build-error-disk-quota.png`](../evidence/errors/build-error-disk-quota.png), [`evidence/build/deb-packages-created.png`](../evidence/build/deb-packages-created.png), [`evidence/before/uname-before.png`](../evidence/before/uname-before.png) (`/tmp` = tmpfs 821M) |
| **Resolution Status** | **WORKAROUND.** Kernel installed and booted as `7.0.14-cpe-os-v1` ([`evidence/after/uname-after.png`](../evidence/after/uname-after.png)). Exact limit (tmpfs vs root disk) still to be confirmed with the verification commands above. |

---

### TS-06: Custom `linux-libc-dev` replaced the distro package

| Attribute | Details |
| :--- | :--- |
| **Phase** | Phase 7: Kernel installation |
| **Timestamp** | 2026-09-20 (during `dpkg -i`) |
| **Severity** | Low |
| **Observation** | `sudo dpkg -i ~/kernel-build/*.deb` installed all three packages. The output shows `Unpacking linux-libc-dev:amd64 (7.0.14-11) over (7.0.0-31.31)`. |
| **Root Cause** | The wildcard `*.deb` included `linux-libc-dev`. `commands/build-commands.md` Step 6 installs only `linux-image-*.deb` and `linux-headers-*.deb`. `linux-libc-dev` holds the userspace kernel headers used to compile normal programs, so it is not needed to boot the new kernel. |
| **Impact** | Userspace headers now come from the custom build instead of Ubuntu. A later `apt upgrade` may try to replace it back. |
| **Fix / Solution** | Optional revert: `sudo apt install --reinstall --allow-downgrades linux-libc-dev=7.0.0-31.31`. For the next build, install only image and headers as in Step 6. |
| **Evidence** | [`evidence/install/dpkg-install-packages.png`](../evidence/install/dpkg-install-packages.png) |
| **Resolution Status** | **OPEN** (team decision: revert or keep). |

---

## 4. Benign Warnings (No Action Needed)

| Message | Where | Why it is harmless |
| :--- | :--- | :--- |
| `security/apparmor/Kconfig:120:warning: multi-line strings not supported` | `make olddefconfig` | Parser notice in the Kconfig tool; `.config` was still written. |
| `dpkg-gencontrol: warning: email address 'vboxuser <vboxuser@Ubuntu>' with single label domain` | `bindeb-pkg` | Maintainer field auto-filled from the VM user. Set `DEBEMAIL` to silence it. |
| `Warning: os-prober will not be executed to detect other bootable partitions` | `dpkg -i` (GRUB update) | Single-OS VM; there are no other systems to detect. |

---

## 5. Open Questions

1. `uname -a` shows build number `#11`, and the packages are revision `7.0.14-11`, which means the kernel tree was built 11 times. Only one build run is documented. Errors from the earlier attempts should be collected from the Builder.
2. Build time is `real 82m40.657s` in the screenshot but `82m46.657s` in `logs/build-log.md`.

---

## 6. Prevention Checklist for Mini-Project 2

1. Disk: at least 40 GB free on `/` before starting (`df -h /`).
2. Memory: RAM + swap of at least 6 GiB for `-j4`; add the swapfile to `/etc/fstab` if it must survive reboot.
3. After editing `ubuntu.sources`, confirm `sudo apt update` fetches `Sources` indexes.
4. After every `scripts/config` change, verify with `grep` on `.config`; the tool does not reject misspelled names.
5. Set `TMPDIR` to a directory on the real disk before `make bindeb-pkg`.
6. Install only `linux-image` and `linux-headers`.
7. Take a VirtualBox snapshot before `dpkg -i`.
