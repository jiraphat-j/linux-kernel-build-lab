# 03 - Step-by-Step Build Process

## 3.1 Preparing the Build Environment
*   We began by enabling the source repositories according to the Ubuntu kernel documentation (adding `deb-src` to `/etc/apt/sources.list.d/ubuntu.sources`).
*   We installed all necessary dependencies required for building the kernel, utilizing `apt install` for build essentials and `apt-get build-dep linux` for kernel-specific prerequisites.
*   Before downloading the source, we verified that there was sufficient disk space available in the VM and configured a 4.0 GiB swapfile to prevent Out of Memory (OOM) errors during compilation.
*   Evidence such as disk usage before the build and outputs from dependency installations are stored in the `evidence/build/` and `evidence/before/` directories.

## 3.2 Getting the Kernel Source
*   We downloaded the kernel source package corresponding to our current Ubuntu version using the `apt source linux` command and verified it could be fetched successfully.
*   After navigating into the source directory, we cleaned and prepared the build environment.
*   Crucially, we modified the ABI/version number by adding a custom suffix (`-cpe-os-v1`) into the `localversion` file.
*   This version change ensures our custom kernel is easily distinguishable from standard Canonical kernels.
*   To optimize the build time and disk usage, we disabled heavy debug symbols (such as `DEBUG_INFO`) using the `scripts/config` utility and applied defaults with `make olddefconfig`.
*   We captured evidence showing the source directory configuration was ready for the build process (e.g., using `pwd`, `ls -la`, and `uname -r`).

## 3.3 Building the Kernel
*   We ensured a clean configuration state immediately prior to starting the build.
*   The kernel package build process was initiated using the `make -j4 bindeb-pkg` command to utilize multiple CPU cores and allowed to run until completion.
*   We verified that the build was successful by checking for the newly generated `.deb` packages (`linux-image`, `linux-headers`, and `linux-libc-dev`) using the `ls -lh *.deb` command.
*   The complete list of commands used during this phase is documented in `commands/build-commands.md`.
*   Build logs and screenshots of the generated `.deb` packages are saved in `logs/build-log.md` and the `evidence/build/` folder.
