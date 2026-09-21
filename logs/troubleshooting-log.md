# Troubleshooting Log

This log documents issues, root causes, fixes, and evidence collected during the kernel build and install process.

---

## Issue Log

### Incident 1: Disk Quota Exceeded During Kernel Package Compression

| Attribute | Details |
| :--- | :--- |
| **Phase** | Phase 5: Kernel Build (`make bindeb-pkg`) |
| **Timestamp** | 2026-09-20 14:48 |
| **Severity** | High (Build termination) |
| **Error Message** | `dpkg-deb (subprocess): compressing tar member: zstd write error: Disk quota exceeded`<br>`make[3]: *** [debian/rules:66: binary-image-dbg] Error 25`<br>`make: *** [Makefile:248: __sub-make] Error 2` |
| **Root Cause** | The VM disk is allocated with 25 GB (`/dev/sda2`). Creating the unstripped debug symbols package (`linux-image-*-dbg`) requires over 30 GB of extra disk space. When zstd attempted to compress the massive debug package, it exhausted the root partition disk space. |
| **Fix / Solution** | 1. Disabled heavy debug symbols via kernel configuration:<br>`scripts/config --disable DEBUG_INFO`<br>`scripts/config --disable DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT`<br>`scripts/config --disable DEBUG_INFO_BTF`<br>`scripts/config --disable DEBUG_INFO_NONE`<br>`make olddefconfig`<br>2. Cleared intermediate debug artifacts and re-ran `make -j4 bindeb-pkg`.<br>3. Configured a 4GB swapfile to prevent concurrent memory pressure. |
| **Evidence** | [`evidence/errors/build-error-disk-quota.png`](../evidence/errors/build-error-disk-quota.png) |
| **Resolution Status** | **RESOLVED** — The 3 essential Debian packages (`linux-image`, `linux-headers`, `linux-libc-dev`) were successfully built and verified in `~/kernel-build/`. |

---

### Incident 2: Out of Memory (OOM) Risk on Multi-Core Build

| Attribute | Details |
| :--- | :--- |
| **Phase** | Phase 4 / Phase 5: Resource Optimization |
| **Timestamp** | 2026-09-20 13:30 |
| **Severity** | Medium (Preventative) |
| **Observation** | The VM had only 1.6 GiB of physical RAM and 0B Swap space. Running `make -j4` would easily exhaust available RAM and cause the Linux OOM-killer to terminate GCC compiler processes. |
| **Fix / Solution** | Created and activated a 4.0 GiB swapfile at `/swapfile` using `dd`, `mkswap`, and `swapon`. |
| **Evidence** | [`evidence/build/swapfile-setup.png`](../evidence/build/swapfile-setup.png) |
| **Resolution Status** | **RESOLVED** — RAM + Swap totaled ~5.6 GiB, allowing smooth 4-core parallel compilation without crashes. |
