
核心目标：搞清楚并能构建 initramfs、发行版、图形桌面环境。



# Rootfs Ubuntu

1、有现成的适用于 arm、arm64、riscv32、riscv64 架构的 Ubuntu 根文件系统镜像。

**Ubuntu 官方网站**：

最新版本列表: https://cdimage.ubuntu.com/ubuntu-base/daily/current/

各个版本列表: https://cdimage.ubuntu.com/ubuntu-base/releases/

比如: https://cdimage.ubuntu.com/ubuntu-base/releases/20.04/release/ubuntu-base-20.04.1-base-arm64.tar.gz

---

1、下面是完整脚本，qemu切换到指定根文件系统：
```bash
#!/bin/bash 

ROOTFS_DIR=ubuntu-22.04-rootfs

if [ $# -eq 1 ]
then
        ROOTFS_DIR=$1
fi

if [ ! -d $ROOTFS_DIR ]
then
        echo "$ROOTFS_DIR not exist"
        echo "Usage: $0 DIR"
        exit 1
fi

echo "Mounting file system"
sudo mount -t proc      /proc    $ROOTFS_DIR/proc
sudo mount -t sysfs     /sys     $ROOTFS_DIR/sys
sudo mount -o bind      /dev     $ROOTFS_DIR/dev
sudo mount -o bind      /dev/pts $ROOTFS_DIR/dev/pts
echo "Change root"
sudo cp /usr/bin/qemu-riscv64-static $ROOTFS_DIR/usr/bin
sudo chroot $ROOTFS_DIR /bin/bash -i
```


2、下面是相反操作，即卸载根文件系统脚本：
```bash
#!/bin/bash

ROOTFS_DIR=ubuntu-22.04-rootfs

if [ $# -eq 1 ]
then
        ROOTFS_DIR=$1
fi

if [ ! -d $ROOTFS_DIR ]
then
        echo "$ROOTFS_DIR not exist"
        echo "Usage: $0 DIR"
        exit 1
fi

echo "Umounting file system"
sudo umount $ROOTFS_DIR/proc
sudo umount $ROOTFS_DIR/sys
sudo umount $ROOTFS_DIR/dev/pts
sudo umount $ROOTFS_DIR/dev
sudo rm $ROOTFS_DIR/usr/bin/qemu-riscv64-static
```




<font color=blue>我现在板子成功进入了 ubuntu-base-20.04.1-base-arm64.tar.gz 对应的根文件系统，但是只有控制台界面，没有图形界面，如果想要在其基础上运行图形桌面环境，硬件上和驱动上以及软件上需要做哪些事？</font>


# zynq ubuntu to uramdisk


你想解决的核心问题是：将官方下载的 `ubuntu-base-20.04.5-base-armhf.tar.gz` 基础镜像包，制作成可在 Zynq 等 ARM 平台上使用的 `uramdisk.image.gz` 格式内存根文件系统镜像。


**环境要求（PC 端，建议 Ubuntu 20.04/22.04 x86_64）**

1、初始化编译环境：
```bash
# 安装必要工具：
sudo apt update && sudo apt install -y \
  qemu-user-static \
  debootstrap \
  binfmt-support \
  dosfstools \
  mtools \
  cpio \
  gzip \
  sudo \
  vim

# 确认交叉编译环境（若需适配 Zynq，需确保工具链匹配 armhf）。
source /home/settings64-xsdk-2018.3.sh
```


2、目录规划（避免权限问题，建议在用户目录操作）：
```bash
# 创建工作目录
mkdir -p  ubuntu_rootfs
# 解压ubuntu-base包到临时根文件系统目录
tar -xf ubuntu-base-20.04.5-base-armhf.tar.gz -C ubuntu_rootfs/
```


3、挂载必要系统目录 + 配置 qemu 模拟 ARM 环境：
```bash
# 挂载必要目录（chroot必备）
sudo mount --bind /dev ubuntu_rootfs/dev
sudo mount --bind /dev/pts ubuntu_rootfs/dev/pts
sudo mount --bind /proc ubuntu_rootfs/proc
sudo mount --bind /sys ubuntu_rootfs/sys
# 关键：挂载宿主机的resolv.conf，解决DNS解析
sudo mount --bind /etc/resolv.conf ubuntu_rootfs/etc/resolv.conf
# 挂载tmpfs到/tmp，解决临时文件创建问题
sudo mount -t tmpfs tmpfs ubuntu_rootfs/tmp

# 复制qemu-arm-static
sudo cp /usr/bin/qemu-arm-static ubuntu_rootfs/usr/bin/

# 进入chroot
sudo chroot ubuntu_rootfs/












# 先卸载已挂载的目录（重点卸载/etc/resolv.conf）
sudo umount ubuntu_rootfs/etc/resolv.conf
sudo umount ubuntu_rootfs/dev/pts
sudo umount ubuntu_rootfs/dev
sudo umount ubuntu_rootfs/proc
sudo umount ubuntu_rootfs/sys
sudo umount ubuntu_rootfs/tmp

# 重新正确挂载（重点：先挂载dev，再挂载dev/pts，且不挂载/etc/resolv.conf）
sudo mount --bind /dev ubuntu_rootfs/dev
sudo mount -t devpts devpts ubuntu_rootfs/dev/pts
sudo mount --bind /proc ubuntu_rootfs/proc
sudo mount --bind /sys ubuntu_rootfs/sys
sudo mount -t tmpfs tmpfs ubuntu_rootfs/tmp

# 重新复制qemu-arm-static
sudo cp /usr/bin/qemu-arm-static ubuntu_rootfs/usr/bin/

# 重新进入chroot
sudo chroot ubuntu_rootfs/
```


4、在 chroot 环境内配置基础系统：
```bash
echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal main restricted universe multiverse
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal-updates main restricted universe multiverse
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal-backports main restricted universe multiverse
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ focal-security main restricted universe multiverse" > /etc/apt/sources.list


# 2. 修复/tmp权限（必做）
mkdir -p /tmp
chmod 1777 /tmp

# 3. 配置本地化（避免乱码）
locale-gen en_US.UTF-8
update-locale LANG=en_US.UTF-8

# 4. 临时跳过签名验证更新源（先解决基础依赖）
apt update --allow-unauthenticated


# 4. 临时跳过签名验证更新源（先解决基础依赖）
apt update --allow-unauthenticated

# 5. 安装核心依赖（包括GPG签名所需组件）
apt install -y ubuntu-keyring resolvconf net-tools ifupdown passwd sudo --allow-unauthenticated

# 6. 正常更新源（此时签名验证会通过）
apt update

# 7. 设置root密码（必做）
passwd root




# 清理apt缓存（减小根文件系统体积）
apt clean && apt autoremove -y

# 退出chroot
exit

```


5、安装基础工具:
```bash
# 2. 更新并安装基础工具（适配嵌入式ARM平台）
apt update && apt install -y \
  locales \
  net-tools \
  ifupdown \
  iproute2 \
  resolvconf \
  passwd \
  sudo \
  bash-completion \
  initramfs-tools

# 3. 配置本地化（避免乱码）
locale-gen en_US.UTF-8
update-locale LANG=en_US.UTF-8

# 4. 设置root密码（必做，否则登录不了）
passwd root  # 输入你想要的密码，如root123

# 5. 配置回环接口（确保启动后有lo接口）
echo "auto lo
iface lo inet loopback" > /etc/network/interfaces

# 6. 配置DNS（确保能联网）
echo "nameserver 8.8.8.8
nameserver 114.114.114.114" > /etc/resolv.conf

# 7. 清理apt缓存（减小根文件系统体积）
apt clean && apt autoremove -y

# 8. 退出chroot环境
exit
```


6、卸载挂载的伪文件系统:
```bash
sudo umount ubuntu_rootfs/tmp
sudo umount ubuntu_rootfs/etc/resolv.conf
sudo umount ubuntu_rootfs/dev/pts
sudo umount ubuntu_rootfs/dev
sudo umount ubuntu_rootfs/proc
sudo umount ubuntu_rootfs/sys


# 删除qemu-arm-static（可选，减小体积）
sudo rm ubuntu_rootfs/usr/bin/qemu-arm-static
```

---

三、**制作 uramdisk.image.gz**（核心步骤）

1、进入根文件系统目录，打包为 cpio 格式：
```bash
cd ubuntu_rootfs
# 注意：必须用sudo，否则会丢失权限文件；find . 表示打包当前目录所有文件
# newc 表示使用新的 cpio 格式，兼容 Linux 内核
sudo find . -print0 | sudo cpio --null -ov --format=newc > ../uramdisk.image

cd ..
sudo gzip -9 uramdisk.image
```


2、验证镜像完整性（可选）：
```bash
# 解压验证（测试cpio包是否正常）
mkdir test && cd test
zcat ../uramdisk.image.gz | cpio -idmv
# 若能正常解压出根文件系统的所有文件（如bin、etc、usr等），说明打包成功
cd .. && rm -rf test
```


---

四、**添加 Zynq 设备树 / 驱动相关文件**：

如果你的 uramdisk 要在 Zynq 平台使用，需补充以下配置：

- **添加 Zynq 设备树 / 驱动相关文件**：
    
    - 将 Zynq 的设备树兼容文件放到 `rootfs/lib/firmware/` 或 `rootfs/lib/modules/`；
    - 若需自定义驱动，编译后复制到 `rootfs/lib/modules/$(uname -r)/kernel/`。
    
- **配置启动脚本**：
    
    - 若 Zynq 启动时需要自动执行命令，可在 `rootfs/etc/rc.local` 中添加（需赋予执行权限）：

```bash
sudo chmod +x rootfs/etc/rc.local
echo "#!/bin/bash
ifconfig eth0 192.168.1.10 netmask 255.255.255.0 up  # 示例：配置网口
exit 0" > rootfs/etc/rc.local
```

- **精简根文件系统（可选）**：

Ubuntu-base 默认包含较多冗余文件，可删除 `rootfs/usr/share/doc`、`rootfs/usr/share/man` 等目录减小体积。






# bottom





