


# busybox

busybox下载地址：[[downloads]]

```bash
wget <https://busybox.net/downloads/busybox-1.31.0.tar.bz2>

tar -jxvf busybox-1.31.0.tar.bz2
cd busybox-1.31.0
make menuconfig
#-> Settings
#[*] Build static binary (no shared libs)
#(aarch64-linux-gnu-) Cross compiler prefix

make && make install

cd _install
mkdir dev
cd dev
sudo mknod console c 5 1
sudo mknod null c 1 3

#压缩成cpio.gz文件系统
find . | cpio -o -H newc |gzip > ../rootfs.cpio.gz

#启动arm64内核
qemu-system-aarch64 \\
        -machine virt,virtualization=true,gic-version=3 \\
        -nographic \\
        -m size=1024M \\
        -cpu cortex-a57 \\
        -smp 2 \\
        -kernel Image \\
        -initrd rootfs.cpio.gz \\
        --append "console=ttyAMA0 rdinit=/linuxrc"

```

---

<font color=blue>busybox rootfs 里，如何不输入用户名密码，系统开机就能直接进入命令行？</font>

busybox 的 init 进程通过 `/etc/inittab` 控制开机流程，默认可能会触发 login 程序要求输入账号密码。要跳过认证，核心是让 init 直接启动 shell（而非 login 程序），并通过配置确保 shell 无交互直接运行。

1、**编写 / 修改 `/etc/inittab` 配置**
```bash
# 写入核心配置
cat > /etc/inittab << EOF
# 系统初始化：执行 rcS 脚本（可选，用于挂载文件系统、启动基础服务）
::sysinit:/etc/init.d/rcS

# 核心配置：在控制台(tty1)直接启动shell，退出后自动重启（respawn）
tty1::respawn:-/bin/sh

# 可选：关闭其他tty（避免多控制台干扰）
tty2::off
tty3::off
tty4::off
tty5::off
tty6::off

# 系统关机/重启时执行的清理脚本（可选）
::shutdown:/etc/init.d/rcK
```


**2、确保 `/etc/init.d/rcS` 无认证逻辑（关键）**

检查rcS脚本并确保其中**没有调用 login、getty 等需要认证的程序**。


**3、禁用可能的认证配置（兜底）**

部分 busybox 版本可能会读取 `/etc/passwd`/`/etc/shadow` 强制认证，需确保这些文件不影响：

```bash
# 确保 root 用户无密码（即使存在 passwd 文件）
echo "root::0:0:root:/root:/bin/sh" > /etc/passwd
# 清空 shadow 文件（避免密码校验）
> /etc/shadow
```


---

1、其他参考制作脚本
```bash
#!/bin/bash

MOUNT_DIR=mnt
CURR_DIR=`pwd`

rm initrd.ext4
dd if=/dev/zero of=initrd.ext4 bs=1M count=64
mkfs.ext4 initrd.ext4

mkdir -p $MOUNT_DIR
mount initrd.ext4 $MOUNT_DIR
cp -arf busybox-1.35.0/_install/* $MOUNT_DIR

cd $MOUNT_DIR
mkdir -p etc dev mnt proc sys tmp mnt etc/init.d/

echo "proc /proc proc defaults 0 0" > etc/fstab
echo "tmpfs /tmp tmpfs defaults 0 0" >> etc/fstab
echo "sysfs /sys sysfs defaults 0 0" >> etc/fstab

echo "#!/bin/sh" > etc/init.d/rcS
echo "mount -a" >> etc/init.d/rcS
echo "mount -o remount,rw /" >> etc/init.d/rcS
echo "echo -e \\"Welcome to ARM64 Linux\\"" >> etc/init.d/rcS
chmod 755 etc/init.d/rcS

echo "::sysinit:/etc/init.d/rcS" > etc/inittab
echo "::respawn:-/bin/sh" >> etc/inittab
echo "::askfirst:-/bin/sh" >> etc/inittab
chmod 755 etc/inittab

cd dev
mknod console c 5 1
mknod null c 1 3
mknod tty1 c 4 1

cd $CURR_DIR
umount $MOUNT_DIR
echo "make initrd ok!"
```





# bottom






