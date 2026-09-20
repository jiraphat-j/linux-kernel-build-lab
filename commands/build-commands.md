# Ubuntu 24.04 Kernel Build Commands
## Step-by-Step for Lead / Builder 1

---

## Step 0: Pre-Flight VM Checklist
- Cores: 2-4 vCPUs
- RAM: 4GB-8GB
- Disk: 35GB-50GB free
- Take VirtualBox snapshot: `Machine -> Take Snapshot` (Name: `Baseline`)

---

## Step 1: Enable Source & Install Dependencies

```bash
# Enable deb-src in Ubuntu 24.04 (deb822 format)
sudo sed -i 's/^Types: deb$/Types: deb deb-src/' /etc/apt/sources.list.d/ubuntu.sources
sudo apt update

# Install build dependencies
sudo apt install -y build-essential libncurses-dev bison flex libssl-dev \
  libelf-dev fakeroot debhelper libudev-dev libpci-dev libiberty-dev \
  dwarves bc cpio rsync kmod htop git
sudo apt-get build-dep -y linux
```

---

## Step 2: Prepare Workspace

```bash
df -h /
mkdir -p ~/kernel-build
cd ~/kernel-build
```

---

## Step 3: Fetch Kernel Source

```bash
apt source linux
cd linux-*
pwd
ls -la
```

---

## Step 4: Configure Custom Version & Strip Debug Info

> [!NOTE]
> Stripping debug symbols avoids 30GB+ disk usage and reduces build time to ~30 minutes.

```bash
# Set custom kernel suffix
echo "-cpe-os-v1" > localversion

# Use running kernel config
cp /boot/config-$(uname -r) .config

# Disable heavy debug symbols
scripts/config --disable DEBUG_INFO
scripts/config --disable DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT
scripts/config --disable DEBUG_INFO_BTF
scripts/config --enable DEBUG_INFO_NONE

# Apply default config choices
make olddefconfig
```

---

## Step 5: Compile Kernel & Build .deb Packages

```bash
# Build using all CPU cores and log output
make -j$(nproc) bindeb-pkg 2>&1 | tee ~/kernel-build/build.log

# Verify generated packages
cd ~/kernel-build
ls -lh *.deb
```

---

## Step 6: Install Custom Kernel

```bash
cd ~/kernel-build
sudo dpkg -i linux-image-*.deb linux-headers-*.deb

# Check /boot files
ls -lh /boot | grep cpe-os-v1
```

---

## Step 7: Reboot and Select Kernel

```bash
sudo reboot
```

During reboot:
1. Hold `Shift` or press `Esc` to enter GRUB.
2. Go to **Advanced options for Ubuntu**.
3. Select `Ubuntu, with Linux 6.8.0-cpe-os-v1`.

---

## Step 8: Post-Boot Verification

```bash
uname -r
uname -a
dpkg -l | grep cpe-os-v1
```
