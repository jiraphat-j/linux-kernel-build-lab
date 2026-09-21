# System State Before & After Kernel Installation

This comparison documents the system state of the Ubuntu VM before and after compiling and installing the custom kernel `7.0.14-cpe-os-v1`.

---

## 1. Comparison Summary Table

| Metric / Attribute | Baseline (Before) | Custom Kernel (After) | Verification Result |
| :--- | :--- | :--- | :--- |
| **Kernel Release (`uname -r`)** | `7.0.0-31-generic` | `7.0.14-cpe-os-v1` | **Changed** (Custom suffix active) |
| **Kernel Full String (`uname -a`)** | `Linux Ubuntu 7.0.0-31-generic #31-Ubuntu SMP PREEMPT_DYNAMIC Sat Aug 1 04:26:38 UTC 2026 x86_64 GNU/Linux` | `Linux Ubuntu 7.0.14-cpe-os-v1 #11 SMP PREEMPT_DYNAMIC Sun Sep 20 14:04:33 UTC 2026 x86_64 GNU/Linux` | **Verified** (`#11`, built Sep 20, 2026) |
| **Kernel Image in `/boot`** | `vmlinuz-7.0.0-31-generic` | `vmlinuz-7.0.14-cpe-os-v1` (15M) | **Added & Active** |
| **Initramfs in `/boot`** | `initrd.img-7.0.0-31-generic` | `initrd.img-7.0.14-cpe-os-v1` (34M) | **Generated via Dracut** |
| **System Map in `/boot`** | `System.map-7.0.0-31-generic` | `System.map-7.0.14-cpe-os-v1` (10M) | **Added** |
| **Kernel Config in `/boot`**| `config-7.0.0-31-generic` | `config-7.0.14-cpe-os-v1` (302K) | **Added** |
| **Virtual Memory (Swap)** | `0B` | `4.0GiB` (`/swapfile`) | **Expanded** |
| **Debian Packages Installed** | Stock Ubuntu packages | `linux-headers-7.0.14-cpe-os-v1`<br>`linux-image-7.0.14-cpe-os-v1`<br>`linux-libc-dev` | **Installed via dpkg** |

---

## 2. Screenshot References

- **Baseline Evidence:**
  - [`evidence/before/uname-before.png`](../evidence/before/uname-before.png)
  - [`evidence/before/lscpu-hardware-spec.png`](../evidence/before/lscpu-hardware-spec.png)
- **Installation Evidence:**
  - [`evidence/install/dpkg-install-packages.png`](../evidence/install/dpkg-install-packages.png)
- **After Verification Evidence:**
  - [`evidence/after/uname-after.png`](../evidence/after/uname-after.png)
