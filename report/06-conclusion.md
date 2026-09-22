# 06 - Conclusion

## 1. Project Summary
Our group successfully achieved the project's Definition of Done by compiling and installing a custom Ubuntu kernel within a Linux VM. The virtual machine boots normally into the new kernel. This success is verified by our before-and-after baseline comparisons, which include updated system outputs for `uname -a` and `uname -r`, new file additions in the `/boot` directory, and the custom kernel's presence in the GRUB menu.

## 2. Troubleshooting Overview
Throughout the build process, we encountered and resolved several issues, such as a "Disk quota exceeded" error during the kernel package compression due to massive debug symbols, and an Out of Memory (OOM) risk caused by insufficient RAM during the multi-core build phase. We successfully identified the root causes and documented reproducible fixes, such as disabling specific debug configurations (e.g., `DEBUG_INFO`) and creating a 4GB swapfile. A complete record of all errors, causes, and solutions is available in our `logs/troubleshooting-log.md` file.

## 3. Lessons Learned
This project expanded our technical understanding of operating systems and provided practical insights into cybersecurity:

*   **OS & Build Environment:** We gained hands-on experience preparing a Linux build environment, modifying kernel source files, and installing compiled `.deb` packages.
*   **Blue Team & DFIR Perspective:** We learned how a system's kernel version changes and what specific artifacts—such as `/boot` contents, GRUB configurations, and package histories—are essential for investigating potential kernel tampering. We now understand how to use before/after comparisons to detect system anomalies.
*   **Red Team Awareness:** We understand why advanced attackers target levels below user-space (like the kernel, modules, or boot chain). Altering the kernel can obscure the visibility of security tools, which highlights a critical attack surface that defenders must be prepared to monitor.
