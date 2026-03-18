---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠== You can decompress Drawing data with the command palette: 'Decompress current Excalidraw file'. For more info check in plugin settings under 'Saving'


# Excalidraw Data

## Text Elements
Linux内核问题 ^qV4Q5Fxy

Level0:可观测内核实验系统
👉 你要做到：任何现象 → 能设计“观测方案” ^5AYS4XSc

编译环境：docker ^QJZLvNFd

运行环境：qemu ^GkYaHGLX

内核问题模拟器（训练题库） ^ClPiDt2T

工具清单2:perf,ftrace,eBPF,crash,vmstat/iostat/pidstat, sar ^6gjI9T57

Level1:基础操作入门级（单点问题/线性因果） ^xZQjot0G

Level2:机制级问题（工具不能直接给答案） ^CHTyOlMW

Level3:资源竞争（多因素） ^9xkT0taq

Level4:架构级问题（高级） ^AP9k4ze3

Level6:
Linux 内核工程师的本质职责 ^oBBt75vX

故障排查（最核心，占比最高） ^joflQERI

性能优化（第二核心） ^nAOBlCaj

内核机制理解与改造 ^KVlxZiTT

工具使用与构建（很重要） ^mkKTbW5G

系统建模与分析（高手分水岭） ^zhwCFXqg

驱动开发（驱动分两类：设备驱动、内核子系统） ^gDhX81II

Level5:地狱级（现实技术难题） ^2Uo32x5U

工具清单1:proc,sys,debugfs ^F9gBojd8

能力模型 ^6Wuk0GGf

① 现象层（Symptoms） ^Oy0HNRTf

② 观测层（Observability）：精通那几个工具来观测 ^s2LlEjQl

③ 内核机制层（Kernel Mechanics） ^GMg5u7VG

④ 根因分析层（Root Cause）：能复现、能解释链路 ^pbx2nGEt

crash（内核挂死核心技能） ^YMArQ3o6

1. 模拟：kernel panic、死锁 ^aO1NhSUv

2. crash分析vmcore ^ZtLxbWCP

eBPF ^dgn4PEU4

1. 能写：kprobe、tracepoint ^pt3hXl2L

2. 能做：latency分析、syscall追踪 ^A83SWL7O

3. 推荐项目：做一个系统慢请求分析工具 ^zyqNXjrv

调度问题 ^lDMH23UV

内存问题 ^dQxYesHK

IO问题 ^nU6ICCr3

锁问题 ^kOIOcENO

内核机制层（Kernel Mechanics） ^Sg9jcidk

调度器（CFS） ^4OyJy5sZ

内存（页表 / reclaim / slab） ^amymTsgZ

IO path（bio → request → driver） ^JbvpXTD8

锁（spinlock / mutex / RCU） ^ZpA4KCOE

01、构建qemu环境（docker里编译,再安装到宿主机上） ^gCm00scw

帮我写一个驱动模块，专门用来导致内核崩溃并转储 vmcore ，并且设置系统能够转储vmcore。
相当于指导我搭建一个 crash + vmcore 的调试环境，并刻意制造一个崩溃的场景，然后带着我一步一步定位问题。 ^Tl0SfhgC

# 第一步：准备环境和工具 ^DCb8DtKn

📦 整体架构: [恶意驱动] → 触发崩溃 → kdump捕获 → 生成vmcore → crash分析 ^UIs8Nk0h

1.1 安装必要软件包

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y crash kexec-tools build-essential
sudo apt-get install -y kdump-tools
sudo apt-get install -y gdb dwarves
sudo apt-get install -y linux-headers-$(uname -r)

# CentOS/RHEL/Rocky
sudo yum install -y kexec-tools crash kernel-devel-$(uname -r) gdb elfutils-libelf-devel ^bDjNi5JT

1.2 检查内核调试符号

# 确认内核是否带调试信息
ls /usr/lib/debug/lib/modules/$(uname -r)/vmlinux
# 如果没有，Ubuntu安装 linux-image-$(uname -r)-dbgsym ^aE1H0osk

第二步：配置系统支持 vmcore 转储 ^aUDq9jki

2.1 配置 kdump/kexec

# 编辑 /etc/default/kdump-tools (Ubuntu) 或 /etc/sysconfig/kdump (CentOS)
sudo vim /etc/default/kdump-tools

添加/修改以下内容：
    # 预留 512M 内存给 crashkernel
    CRASHKERNEL="crashkernel=512M-:256M"
    
    # 启用 kdump
    USE_KDUMP=1
    
    # vmcore 保存路径
    KDUMP_CORE_COLLECTOR="makedumpfile -c -d 31"  # 压缩并过滤不必要的页
    KDUMP_SAVE_PATH="/var/crash" ^mvv7D65Z

2.2 修改 GRUB 引导参数

# 添加 crashkernel 参数
sudo vim /etc/default/grub

# 找到 GRUB_CMDLINE_LINUX，添加：
GRUB_CMDLINE_LINUX="... crashkernel=512M-:256M"

# 更新 GRUB
sudo update-grub   # Ubuntu/Debian
sudo grub2-mkconfig -o /boot/grub2/grub.cfg  # CentOS/RHEL

# 重启系统
sudo reboot ^3qXnGonz

2.3 启动 kdump 服务

# Ubuntu
sudo systemctl enable kdump-tools
sudo systemctl start kdump-tools

# CentOS/RHEL
sudo systemctl enable kdump
sudo systemctl start kdump

# 验证是否成功
cat /proc/cmdline | grep crashkernel  # 应该有 crashkernel 参数
cat /sys/kernel/kexec_crash_loaded   # 应该输出 1 ^hB0Uxljp

第三步：编写故意崩溃的驱动模块 ^sCLj3zHh

3.1 模块源码 crash_driver.c
这个模块提供两种崩溃方式：内存越界 和 UAF ^uD1mKDOU

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/delay.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Debugger");
MODULE_DESCRIPTION("故意制造内核崩溃的演示模块");

static int crash_type = 0;
module_param(crash_type, int, 0644);
MODULE_PARM_DESC(crash_type, "0=越界写, 1=UAF, 2=空指针解引用");

static char *buffer = NULL;
static struct my_struct {
    int id;
    char data[128];
    void (*callback)(void);  // 函数指针，UAF时会被破坏
} *obj = NULL;

static void fake_callback(void)
{
    printk(KERN_INFO "fake_callback called\n");
}

static int __init crash_driver_init(void)
{
    printk(KERN_INFO "Crash driver loaded, type=%d\n", crash_type);

    switch(crash_type) {
        case 0:  /* 内存越界写 - OOB */
            printk(KERN_INFO "[Case0] 分配 64 字节，故意写越界\n");
            buffer = kmalloc(64, GFP_KERNEL);
            if (!buffer) return -ENOMEM;
            memset(buffer, 'A', 64);
            /* 越界写 - 写入第 128 字节（超出 64 字节） */
            buffer[128] = 'B';
            break;

        case 1:  /* UAF - 释放后使用 */
            printk(KERN_INFO "[Case1] 分配结构体，释放后再次使用\n");
            obj = kmalloc(sizeof(*obj), GFP_KERNEL);
            if (!obj) return -ENOMEM;
            obj->id = 123;
            strcpy(obj->data, "Hello UAF");
            obj->callback = fake_callback;
            
            /* 释放对象 */
            kfree(obj);
            printk(KERN_INFO "对象已释放，但即将伪造另一个对象占用这块内存\n");
            
            /* 模拟其他模块迅速重占这块内存（用不同类型的对象） */
            buffer = kmalloc(sizeof(*obj), GFP_KERNEL);
            if (buffer) {
                /* 用脏数据覆盖原来的结构体 */
                memset(buffer, 0xAA, sizeof(*obj));
            }
            
            /* UAF：再次访问已释放的结构体 */
            printk(KERN_INFO "即将访问已释放的对象...\n");
            msleep(100);  // 稍微延迟，让kmalloc有机会重用内存
            
            /* 这行会触发问题：obj 指向的内存可能已被 reuse */
            obj->callback();  /* CRASH HERE */
            break;

        case 2:  /* 空指针解引用 - 经典的 Oops */
            printk(KERN_INFO "[Case2] 空指针解引用\n");
            ((void (*)(void))NULL)();
            break;

        default:
            printk(KERN_INFO "Invalid crash_type\n");
            return -EINVAL;
    }
    return 0;
}

static void __exit crash_driver_exit(void)
{
    kfree(buffer);
    kfree(obj);
    printk(KERN_INFO "Crash driver unloaded\n");
}

module_init(crash_driver_init);
module_exit(crash_driver_exit); ^jXuu2Ugq

obj-m += crash_driver.o

KERNEL_DIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
        $(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules

clean:
        $(MAKE) -C $(KERNEL_DIR) M=$(PWD) clean

install:
        sudo insmod crash_driver.ko crash_type=1 ^gkgWaTxY

第四步：编译并安装驱动 ^txNT0kr3

# 编译模块
make

# 安装内核头文件（如果还没有）
sudo apt-get install linux-headers-$(uname -r)  # Ubuntu

# 加载驱动（先试 case 0 越界，再试 case 1 UAF）
sudo insmod crash_driver.ko crash_type=1

# 加载后应该立即 panic，系统会重启 ^ijUPciwX

第五步：配置自动重启和 vmcore 收集 ^DfKLQXmR

5.1 设置 panic 后自动重启并捕获 vmcore ^2FGhtNQi

# 设置 panic 后 5 秒自动重启
sudo sysctl -w kernel.panic=5
sudo sysctl -w kernel.panic_on_oops=1

# 永久生效
echo "kernel.panic=5" | sudo tee -a /etc/sysctl.conf
echo "kernel.panic_on_oops=1" | sudo tee -a /etc/sysctl.conf ^jx8tAqZW

5.2 验证 vmcore 生成
加载驱动触发 panic 后，系统重启。重启后检查： ^fgpjPV1R

ls -lh /var/crash/
# 应该看到类似 vmcore.20250601.123456 的文件

# 如果没生成，检查 kdump 状态
sudo systemctl status kdump-tools
sudo dmesg | grep -i crash ^HJt2mg4G

第六步：用 Crash 工具分析 vmcore ^5s3pkmJU

6.1 启动 crash 分析 ^LYXPEUfA

# 找到最新的 vmcore 和对应的 vmlinux
sudo crash /usr/lib/debug/lib/modules/$(uname -r)/vmlinux /var/crash/20250601123456/vmcore ^ArD87X43

6.2 实战分析 Case 1 (UAF) ^lWqU6Ivu

进入 crash 后，按以下步骤操作：

# 1. 查看 panic 的栈回溯
crash> bt -a

# 预期看到类似：
# PID: 1234   TASK: ffff88807a5a8000  CPU: 2   COMMAND: "insmod"
# #0 [ffffc90001213c80] crash_kexec at ffffffff810c1b5f
# #1 [ffffc90001213cd8] oops_end at ffffffff81493e18
# #2 [ffffc90001213d00] no_context at ffffffff81063c7f
# #3 [ffffc90001213d58] __bad_area_nosemaphore at ffffffff81063f18
# #4 [ffffc90001213da0] bad_area_nosemaphore at ffffffff81063fe6
# #5 [ffffc90001213db0] do_user_addr_fault at ffffffff810b316e
# #6 [ffffc90001213e30] exc_page_fault at ffffffff81a00d3e
# #7 [ffffc90001213e50] asm_exc_page_fault at ffffffff81a0120a
#     [exception RIP: crash_driver_init+0x1f0]  # 注意这里就是我们模块的地址


# 2. 查看具体导致崩溃的指令
crash> dis -l crash_driver_init+0x1f0

# 应该看到类似：
# 0xffffffffc0005000 <crash_driver_init>: mov    %gs:0x1b244(%rip),%rax
# ...
# 0xffffffffc00051f0: callq  *0x0(%rax)   # 这里调用了一个函数指针，但 RAX 指向的是无效内存


# 3. 检查出错的寄存器
crash> rd -a

# 重点看 RIP（指令指针）和 RAX（被调用的函数指针地址）


# 4. 查看 obj 这个变量的状态
crash> p crash_driver_init
crash> sym crash_driver_init  # 找到模块的地址范围

# 检查 obj 指针（在模块的 .data 段）
crash> sym crash_driver_init+0x200  # 估算 obj 的位置，或者直接搜索

# 更简单的方法：查看模块的符号表
crash> module crash_driver
crash> mod -s crash_driver  # 列出模块的符号


# 5. 关键：查看 obj 指向的内存被什么数据覆盖
crash> struct my_struct <obj的地址>

# 如果这块内存已被覆盖，你会发现：
# id 可能变成 0xAAAAAAAA
# data 全是 0xAA
# callback 指向了无效地址 0xAAAAAAAAAAAAAAAA


# 6. 追踪这块内存的分配历史
crash> kmem -s <obj的地址>
# 查看 slab 信息，可以看到这块内存当前属于哪个 slab cache
# 可能显示是 "kmalloc-128" 并且状态是 inuse 还是 free


# 7. 查看内核日志，还原时序
crash> log | grep -i "crash driver"

# 应该看到：
# [  123.456] Crash driver loaded, type=1
# [  123.457] 对象已释放，但即将伪造另一个对象占用这块内存
# [  123.458] 即将访问已释放的对象... ^UaFIh8dz

学习路线图
做完这个实验，你可以继续挑战：

修改驱动：增加并发场景，多 CPU 同时触发 UAF

使用 eBPF 动态追踪：在 vmcore 分析的同时，用 bpftrace 实时追踪内存分配

模拟真实驱动漏洞：比如网卡驱动中的 UAF（释放后未同步 RCU）

编写 crash 扩展命令：定制化分析你的模块 ^0oTLoasq

qemu-debian中新建 /etc/default/grub, 内容如下:

# 默认启动项，0 表示第一个
GRUB_DEFAULT=0
# 选择操作系统前的等待时间，单位秒
GRUB_TIMEOUT=5
# 默认的内核启动参数，此处添加 crashkernel 参数
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash crashkernel=256M"
# 非默认内核启动参数，通常留空
GRUB_CMDLINE_LINUX=""


# 2. 更新 GRUB 配置以使修改生效, 然后重启
sudo update-grub

# 3. 重启后查看cmdline
cat /proc/cmdline | grep crashkernel

# 4. 查看预留内存
应该能看到类似 d0000000-d1ffffff : Crash kernel 的行，这表示内存已成功预留
cat /proc/iomem | grep Crash ^7v1Psmv2

# 检查是否为 UEFI 启动
ls /sys/firmware/efi/efivars/
# 如果有输出，说明是 UEFI 模式；如果没有输出，说明是传统 BIOS 模式



# 安装完整的 GRUB 包
apt install --reinstall grub-pc grub-pc-bin grub-common
# 如果是 UEFI 系统，安装这个包
apt install --reinstall grub-efi-amd64 grub-efi-amd64-bin



方案 A：传统 BIOS 模式（最常见）
    # 1. 创建 grub 目录
    mkdir -p /boot/grub
    
    # 2. 重新安装 GRUB 到磁盘（假设系统盘是 /dev/sda，请根据实际情况调整）
    grub-install /dev/sda
    
    # 3. 生成 GRUB 配置文件
    update-grub
    
    # 4. 验证配置文件是否生成
    ls -la /boot/grub/grub.cfg


方案 B：UEFI 模式
    # 1. 检查 UEFI 分区挂载点
    ls /boot/efi/
    
    # 2. 创建必要的目录
    mkdir -p /boot/grub
    mkdir -p /boot/efi/EFI/debian
    
    # 3. 重新安装 GRUB（UEFI 模式）
    grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=debian
    
    # 4. 生成配置文件
    update-grub
    
    # 5. 验证
    ls -la /boot/grub/grub.cfg ^CyY9KOAH

#!/bin/bash
# 修复 GRUB 配置问题

echo "=== 修复 GRUB 配置 ==="

# 1. 创建缺失的目录
echo "创建 /boot/grub 目录..."
mkdir -p /boot/grub

# 2. 检查启动模式并安装 GRUB
if [ -d /sys/firmware/efi ]; then
    echo "检测到 UEFI 模式"
    echo "安装 GRUB for UEFI..."
    mkdir -p /boot/efi/EFI/debian
    grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=debian --recheck
else
    echo "检测到传统 BIOS 模式"
    echo "安装 GRUB for BIOS..."
    # 假设系统盘是第一个磁盘，请根据实际情况修改
    DISK=$(lsblk -no pkname $(df /boot | tail -1 | awk '{print $1}') | head -1)
    if [ -z "$DISK" ]; then
        DISK="sda"
    fi
    echo "安装 GRUB 到 /dev/$DISK"
    grub-install /dev/$DISK
fi

# 3. 生成配置文件
echo "生成 GRUB 配置文件..."
update-grub

# 4. 验证
if [ -f /boot/grub/grub.cfg ]; then
    echo "✓ GRUB 配置修复成功"
    echo "配置文件大小: $(du -h /boot/grub/grub.cfg | cut -f1)"
else
    echo "✗ GRUB 配置修复失败"
    exit 1
fi

echo "=== 修复完成 ==="
echo "请重启系统: reboot" ^LBv6j9B4

第一步：修改 run_qemu_debian.sh

#!/bin/bash
kernel=linux-6.6.134/build/arch/x86_64/boot/bzImage
fsimage_qcow2=debian-rootfs-main/debian.qcow2
dir_share=/home/linux/workdir
# quit internel qemu: Ctrl+A X

qemu-system-x86_64 \
  -kernel ${kernel} \
  -drive file=${fsimage_qcow2},format=qcow2,if=virtio \
  -virtfs local,path=${dir_share},mount_tag=hostshare,security_model=passthrough,id=hostshare \
  -m 2G \
  -smp 2 \
  -nographic \
  -append "root=/dev/vda console=ttyS0 rw nokaslr crashkernel=256M"


第二步：启动虚拟机并验证

    # 1. 重新启动虚拟机
    ./run_qemu_debian.sh
    
    # 2. 在虚拟机内验证 crashkernel 参数
    cat /proc/cmdline | grep crashkernel
    # 预期输出应该包含 crashkernel=256M
    
    # 3. 检查内存预留
    cat /proc/iomem | grep Crash
    # 应该能看到 Crash kernel 区域 ^K9fbHlke

第一步：挂载共享目录并复制内核
cp /workdir/linux-6.6.134/build/arch/x86_64/boot/bzImage /boot/vmlinuz-$(uname -r)


第二步：生成 initrd 文件
apt install -y initramfs-tools
mkinitramfs -o /boot/initrd.img-$(uname -r) $(uname -r)


第三步：配置 kdump-tools  —— vi /etc/default/kdump-tools
# 确保以下行没有被注释，并且路径正确：
USE_KDUMP=1
KDUMP_KERNEL="/boot/vmlinuz-$(uname -r)"
KDUMP_INITRD="/boot/initrd.img-$(uname -r)"
KDUMP_COREDIR="/var/crash"

# 2. 重启 kdump 服务
sudo systemctl restart kdump-tools

# 3. 检查是否加载成功
cat /sys/kernel/kexec_crash_loaded
# 应该输出 1

# 4. 查看服务状态
sudo systemctl status kdump-tools ^rV80uNYy

Linux内核里，你在用户态新建一个对象，内核很可能会把它丢到磁盘上养老，除非你不停访问它。
内核是怎么知道哪些对象被频繁访问哪些很少访问甚至几乎不访问？ ^MWYgW98R

LRU（最近最少使用）链表管理在起作用


1. 核心数据结构：活跃链表与非活跃链表
内核为每个内存区域维护两组 LRU 链表：
    活跃链表：存放最近被访问过的页面（热数据）
    非活跃链表：存放相对冷的数据
判断“热”与“冷”的核心指标是：页面是否被标记为“最近被访问过”。


2. 硬件辅助：页表项中的 ACCESSED 位
当 CPU 读写某个用户态虚拟地址时，MMU（内存管理单元）会自动在页表项中设置一个 _PAGE_ACCESSED 位
只要访问过该页面，硬件就自动将这个位置 1,
内核相关线程会检测这个位, 并清空这个位, 方便下次检测。


3. 内核的扫描与判断：kswapd 线程 和 refault distance 更精细机制
kswapd 线程会周期性地做：
    (1) linux 5.x 之前: 维护活跃和非活跃两个链表: 每次检测, 把访问过的往活跃链表挪，把没访问的往非活跃链表挪;
    (2) Refault Distance 算法: 比如通过 内核 jiffies 记录一个页面被踢出内存的时间点, 
          如果该页面在短时间内（可配置阈值）再次被缺页调入，说明它其实很热，只是被误判了 ^2ickEV9e

为什么不能简单拉长扫描间隔？ ^ccYiLJ1w

1. “10秒才扫描一次”会严重误判内存压力
内核的扫描频率是动态的，由内存压力驱动：扫描间隔 ∝ 1 / (内存紧缺程度)
Refault Distance 的核心洞察就是：
用“扫描间隔”判断冷热有天然的采样缺陷，必须用页面被换出后到再次缺页的时间差来反推其真实热度。
换句话说：它不是判断“当前是否冷”，而是预测“未来会不会很快再热”。

假设你是图书馆管理员，需要决定哪些书下架（回收）：
你的方案（长间隔扫描）：每 10 小时来看一次，没被翻动过的书就下架 → 结果有人 11 小时来一次，书老被误下架;
Refault Distance：给每本书贴一个“上次下架时间戳”，如果一本书刚下架 5 分钟又被借出 → 给它贴个“热门保护”标签，下次优先保留。
Linux 最终选择两者结合：短间隔动态扫描（处理紧急内存压力）、Refault Distance（纠正假冷页面的误判）


固定间隔扫描：内存压力大时响应慢，可能 OOM，仅适合负载非常平稳的系统，不适合通用服务器和高吞吐量场景。 ^y4UZDL3c

为什么不能专门用一个线程固定轮询？ ^VUkn1VUG

如果它轮询太频繁（如 1ms）→ 系统开销巨大（每次要遍历大量页表）
如果它轮询太慢（如 10 秒）→ 内存压力时来不及回收

所以 Linux 采用事件驱动 + 周期性后台的混合模式：
kswapd 周期性睡眠/唤醒，但唤醒频率由内存水位决定，
直接回收路径（__alloc_pages_direct_reclaim）在分配失败时同步扫描，Refault Distance 不取代扫描，而是让扫描结果更准确 ^Udtf7aHm

软件发生 OOM 错误时，在行业内标准做法或者稳妥做法是什么？ ^h0n5zfpd

在 Linux 系统中，处理 OOM（Out Of Memory，内存溢出）错误的行业标准做法，
其核心思路并非试图“处理”这个错误本身，而是通过“预防”和“隔离”来优雅地应对。

Linux 内核的 OOM Killer 是一个“最后的守门员”，它的行为是系统性的，直接依赖它来处理错误是一种不稳定的方案。
因此，现代高可靠系统的标准做法是分层防御，从代码、配置、部署到监控，建立一个完整的闭环。




💻 应用层：从源头控制
处理 OOM 最有效的方式，是让它在应用层面根本不要发生。
主动防御：
    (1) 设置 cgroup 内存 limits;
    (2) 调整 OOM Score 保护核心进程;
同时，应养成处理内存分配失败（如 C++ 中的 std::bad_alloc）的好习惯，而不是让程序直接崩溃

使用 choom 调整进程评分：调整值的范围是 -1000 到 1000。
(1) 将核心进程（如数据库、业务网关）设置为 -1000，意味着它永远不会被 OOM Killer 选中；
(2) 将非核心、高内存占用的进程（如离线分析任务）设置为较高的正数，会让它在内存紧张时成为“优先牺牲品”，从而保护核心业务。




⛑️ 系统与容器层：设置最后防线
在系统层面，利用内核的 cgroup v2 机制为进程设置“硬性边界”是现代服务部署（如 Kubernetes）的标准实践。

三大水位线：cgroup v2 定义了三个关键的水位线来控制内存使用：
    (1) memory.low (软限制)：当系统内存紧张时，内核会尽量不回收低于此线 cgroup 的内存。这就像给你的服务划了一块“保护区”。
    (2) memory.high (节流阀)：当内存使用超过此线，内核会开始积极回收内存并限制进程的执行。此时你的服务不会死，但会变得很慢。这是一个重要的“变慢而非崩溃”的预警阶段。
    (3) memory.max (最后防线)：这是绝对不能逾越的红线。一旦触及，内核会立即对该 cgroup 内的进程执行 OOM Kill，以强制释放内存。




🩺 运维层：排查、监控与复盘
当 OOM 不可避免地发生后，专业的运维流程能帮你快速定位并解决问题。
1、排查根因（事后分析）：OOM 发生后，第一步不是简单地重启，而是找到“元凶”。
    （1）通过 dmesg 查看日志或查看 /var/log/messages 文件
    （2）关键信息：在内核日志中，你需要找到这几类关键输出：
            （1）Out of memory: Killed process <PID> (<进程名>)：确认哪个进程被杀。
            （2）oom_score_adj：查看该进程的调整值，判断它是否是被“故意”牺牲的。
            （1）Mem-Info：查看当时的系统内存快照，包括空闲内存、页缓存等，判断是整体内存不足还是单一进程泄漏。

2、建立监控与告警（主动防御）：不要等到 OOM 发生了再手忙脚乱，应当建立主动的监控体系。
(1) cgroup events：对于容器化环境，重点监控 memory.events 文件中的 high（节流事件）和 oom 计数器。如果 high 计数在持续增长，说明你的服务在持续“变慢”，这是一个极强的OOM前兆信号。
(2) PSI (Pressure Stall Information)：这是更先进的监控指标。查看 /proc/pressure/memory，如果 some 或 full 字段出现非零值，说明进程正在因等待内存而被“卡住”。

3、复盘与归档（持续改进）
将每一次 OOM 事件都记录在案。分析是突发的流量高峰、代码的内存泄漏，还是配置的不合理。
通过长期的统计，可以清晰地看到哪些组件是内存消耗的“常客”，从而针对性地进行优化或扩容。

 ^giK0z9kB

cgroup 是个什么东西？为了解决什么问题而生？优点和缺陷是什么？ ^kyJnllc2

cgroup（Control Groups）是 Linux 内核的一个核心功能，它允许将进程组织成层级化的分组，并对这些分组可以使用的系统资源（如 CPU 时间、内存、磁盘 I/O 等）进行限制、记录和隔离。

可以把 cgroup 想象成在 Linux 系统中安装了一整套"资源阀门"
——你可以精确控制一组进程能用多少 CPU、能占多少内存、能写多快的磁盘，还能随时查看它们用了多少。

cgroup 的接口通过一个名为 cgroupfs 的伪文件系统提供，通常挂载在 /sys/fs/cgroup/ 目录下。这意味着你可以像操作普通文件一样（echo、cat）来配置资源限制。
cgroup v2：统一层级结构，简化了管理，提供了更精细的内存控制（如三级水位线），是目前的主流方案。



cgroup 的诞生，是为了解决防止一组进程"霸占"所有资源，导致其他进程"饿死"或系统崩溃。
在未实施 cgroup 隔离的环境中，以下问题频繁发生：
(1) 多线程任务抢占全部 CPU 核心，导致延迟敏感型任务超时;
(2) 单个进程内存泄漏逐渐消耗整台服务器的内存，触发系统级 OOM Killer 随机终止进程（可能杀掉关键进程）;
(3) 高并发写入操作导致磁盘队列深度激增，延长所有业务的 I/O 响应时间;
(4) 大流量服务独占网络带宽，同服务器其他业务无法保证最低传输速率.
cgroup 的出现，使得系统管理员可以将进程分组，并对每组使用的 CPU、内存、磁盘 I/O、网络带宽等资源进行精细化控制。



cgroup 的核心能力可以概括为五个方面：
资源限制：为进程组设定资源使用上限。例如，限制某容器最多使用 512MB 内存，超限将触发 OOM。
优先级控制：为不同进程组分配不同的 CPU 时间份额。例如，核心业务获得更高权重，确保其在资源紧张时优先获得 CPU。
资源统计：记录进程组实际使用的资源数量，用于监控和计费。
进程隔离：结合 namespace，为不同进程组提供独立的资源视图（如进程空间、网络栈）。
进程控制：支持将一组进程统一挂起或恢复。



目前 Linux 内核支持 12 种子系统，常用的包括：
pids        进程数量        pids.max（限制可创建的进程总数）
cpuset        CPU 核心绑定        cpuset.cpus（指定可用核心）
blkio        块设备 I/O        blkio.throttle.read_bps_device（读带宽限制）
memory        内存使用量        memory.limit_in_bytes（硬限制）、memory.high（节流阀）
cpu        CPU 时间分配        cpu.shares（权重）、cpu.cfs_quota_us（配额）




一个典型的层级结构示例：
/sys/fs/cgroup/cpu/          # CPU 子系统的根层级
├── system.slice/            # systemd 管理的系统服务
├── user.slice/              # 用户会话
└── myapp/                   # 自定义控制组
    ├── cpu.shares           # 权重配置
    └── tasks                # 属于该组的进程 PID 列表
所有进程在系统启动时都位于根控制组（root cgroup），子进程默认继承父进程所在的 cgroup。



四、cgroup 的主要优点
(1) 精细化资源控制：可以对 CPU、内存、I/O 等资源进行精确到毫秒级、字节级的限制，粒度远超传统的 ulimit。
(2) 层级化管理：树形结构支持嵌套分组，子组自动继承父组限制，适合复杂的资源分配场景。
(3) 动态调整：限制参数可以在运行时修改并立即生效，无需重启进程，非常适合弹性伸缩场景。
(4) 完善的监控能力：memory.stat、cpuacct.usage 等文件提供了详尽的资源使用统计，是容器监控系统的基础数据来源。
(5) 硬隔离保障：当进程超出限制时，内核强制执行限制（如直接终止进程），防止单点故障扩散。
(6) 容器技术基石：Docker、Kubernetes 等容器平台都依赖 cgroup 来实现资源限制，可以说"没有 cgroup 就没有容器"。



五、cgroup 的主要缺陷与挑战
(1) 性能开销：启用 cgroup 会引入一定的内核调度开销。测试显示，在 40 核服务器上运行 100 个 cgroup 时，系统吞吐量下降约 3%~5%。
      对于大多数场景这是可接受的代价，但对极致性能敏感的业务需要评估。
(2) 应用兼容性问题：早期版本的 Java、Node.js 等语言运行时不能自动感知 cgroup 限制，
      会错误地读取宿主机总资源来计算自己的默认配置（如 JVM 堆大小），导致容器内应用超出限制而被 OOM Kill。
      从 OpenJDK 8u372、11.0.16 及 Node.js 22 开始已支持 cgroup v2 自动检测。
(3) 难以完美预测资源需求：虽然可以设置资源限制，但设置过低会导致应用性能不足，设置过高又浪费资源。最优配置往往需要反复压测和调优。
在实际容器化部署中，两者通常配合使用：cgroup 负责资源限制，namespace 负责环境隔离，共同构成容器技术的底层支撑。
 ^GM3uzdUS

Q: 内存swap ^84WGHIVx

活跃

非活跃 ^of8KxZO1

时间戳 ^0tN172Ix

t ^MCpLsB0P

Refault Distance 算法 ^NlOO6rex

🎯 如何在调试中结合使用？perf、ftrace、eBPF
你的程序为什么这么慢？ ^pHyikQgL

第一步：使用 perf 进行“宏观定位”
当怀疑驱动导致性能下降时，先执行 perf top 或 perf record -ag 生成火焰图。
如果发现你的驱动模块中的某个函数（例如 my_driver_read）CPU占用率异常高，那么问题范围就缩小到了这个函数。



第二步：使用 ftrace 进行“微观分析”
锁定了可疑函数后，用 ftrace 来细致分析它的执行过程。

# 示例：追踪特定内核函数的调用流程
cd /sys/kernel/debug/tracing
echo function_graph > current_tracer          # 选择函数流图模式
echo my_driver_read > set_graph_function      # 指定要追踪的函数
echo 1 > tracing_on                           # 开启追踪
# ... 执行触发问题的操作 ...
echo 0 > tracing_on                           # 关闭追踪
cat trace                                     # 查看结果，分析函数调用路径和返回值[citation:10]




第三步：使用 eBPF 进行“自定义深度观测”
如果 ftrace 的信息还不够，比如你想在特定参数满足某个条件（如 size > 1024）时才记录，
或者想在内核态就计算出平均延迟，eBPF 就是最佳选择。
具体实现方式：可以使用 bpftrace 编写几行脚本，挂载到驱动的 kprobe 或 tracepoint 上，来动态输出你关心的信息。
# 示例：bpftrace 一行式，打印当 open 系统调用打开的目标文件路径
bpftrace -e 'tracepoint:syscalls:sys_enter_open { printf("%s opened: %s\n", comm, str(args->filename)); }'[citation:4]
 ^8I3ApNc9

1、执行采样: 在终端运行命令，让系统在你关心的负载下运行 60 秒。
sudo perf record --call-graph dwarf -F 99 -a -g -- sleep 60
    --call-graph dwarf (推荐), 指定记录调用栈的方式。
                                      dwarf 是目前最通用的方法，它通过调试信息来还原调用栈，不要求编译时保留 frame pointer，因此兼容性最好。
    
    -F 99 表示每秒采样 99 次，大约是每 10 毫秒一次。
    
    sleep 60 这只是为了控制采样时长，让 perf 在 60 秒后自动停止。也可以不写，按 Ctrl+C 手动停止。
                    采样结束后，会在当前目录生成一个 perf.data 文件。


2、查看报告: 运行 perf report 来交互式地分析结果。
    perf report -g graph



3、生成火焰图 (进阶用法)
# 生成折叠的堆栈文件
sudo perf script > out.perf
# 使用 FlameGraph 工具处理: https://github.com/brendangregg/FlameGraph
./stackcollapse-perf.pl out.perf > out.folded
./flamegraph.pl out.folded > flamegraph.svg
最后用浏览器打开 flamegraph.svg，就能看到经典的性能火焰图了。



(1) 用 perf record 抓数据;
(2) 用 perf script 导出数据;
(3) 用 脚本 把重复的调用栈折叠起来, 算一下它们的调用次数;
(4) 生成 svg 火焰图。



如何看懂火焰图？
宽度(X轴) —— 代表时间占比 —— 哪个方块越宽,代表哪个函数占用cpu时间越多
高度(Y轴) —— 调用栈深度 —— 即下面是caller,上面是callee
颜色深度 —— 用来区分不同函数，随机颜色，和性能无关。


火焰图关键观察点：
(1) 最宽的方块: 性能热点
(2) 平坦的顶部: 函数
(3) 陡峭的堆栈: 深层调用链
(4) 重复的模式: 循环或递归



perf + 标准火焰图只能捕捉 CPU 繁忙（On-CPU）的时间，看不见线程在“等”——等 I/O、等锁、等网络、等换页。
分析 I/O 阻塞这类 Off-CPU 问题，需要用另一种思路：抓住线程“主动让出 CPU”的那个瞬间，并把被阻塞的时间累积到调用栈上。
简单来说：On-CPU 图看的是“谁在干活”，Off-CPU 图看的是“谁在等活儿干”。



🧭 方案一：使用 offcputime (推荐，最为直观)
1. 安装 BCC 工具集
apt install bpfcc-tools linux-headers-$(uname -r)

2. 采集 Off-CPU 数据并生成火焰图
这里假设你想要分析一个正在运行的、PID 为 12345 的进程：

# -K: 追踪内核调用栈 (看 I/O 等系统调用)
# -U: 追踪用户态调用栈 (看应用逻辑)
# -f: 输出折叠格式 (folded)，直接供 flamegraph.pl 使用
# -d 秒数: 采样时长
sudo /usr/share/bcc/tools/offcputime -K -U -f -p 12345 30 > out.stacks

# 生成 SVG 火焰图
git clone https://github.com/brendangregg/FlameGraph
cd FlameGraph
./flamegraph.pl --color=io --title="Off-CPU Time Flame Graph" < ../out.stacks > offcpu.svg

效果解读：生成的火焰图里，每一个方块代表一段阻塞时间。
很宽的方块就意味着你的进程在这里等了很久，可能是磁盘 I/O 慢，也可能是锁没争到。



find /workdir/linux-6.6.134 -name "kheaders*"
/workdir/linux-6.6.134/kernel/kheaders.c


专门为 offcputime-bpfcc 工具重定向内核指向：

# 1. 创建必要的目录结构
mkdir -p /lib/modules/6.6.134/kernel
mkdir -p /lib/modules/6.6.134/kernel/drivers

# 2. 创建内核构建链接
ln -sf /workdir/linux-6.6.134/build /lib/modules/6.6.134/build
ln -sf /workdir/linux-6.6.134 /lib/modules/6.6.134/source

# 3. 创建 Module.symvers 文件（如果存在）
if [ -f /workdir/linux-6.6.134/Module.symvers ]; then
    cp /workdir/linux-6.6.134/Module.symvers /lib/modules/6.6.134/
fi

# 4. 创建空的 modules.dep 文件（避免 modprobe 报错）
touch /lib/modules/6.6.134/modules.dep
touch /lib/modules/6.6.134/modules.builtin

# 5. 设置环境变量
export KERNEL_HEADERS=/workdir/linux-6.6.134/build

# 6. 测试运行
offcputime-bpfcc









重新编译内核并启用 BTF：
cd /workdir/linux-6.6.134

# 1. 启用 BTF 配置
scripts/config --enable CONFIG_DEBUG_INFO_BTF
# 也可以启用更多调试信息
scripts/config --enable CONFIG_DEBUG_INFO
scripts/config --enable CONFIG_DEBUG_INFO_DWARF4

# 2. 安装 pahole（BTF 生成工具）
apt-get install dwarves pahole

# 3. 重新编译内核（只需要重新链接 vmlinux）
make -j$(nproc) vmlinux

# 4. 复制新的 vmlinux
cp vmlinux /lib/modules/6.6.134/build/



生成目标进程信息：
offcputime-bpfcc  -K -f -p 12345 30 > out.stacks
./flamegraph.pl --color=io --title="Off-CPU Time Flame Graph" < ./out.stacks > offcpu.svg ^yDT6DHzE

采样分析(perf)、插桩分析(eBPF) ^Bag4BMFC

一个完整的 libbpf + tp_btf 方案，提供两套例程，分别用来抓取特定进程的 off-cpu 火焰图，另一套例程用来抓取 on-cpu 火焰图。

Q：tp_btf 和 kprobe 有什么区别
tp_btf 直接挂载到 tracepoint，性能更好且不依赖 BTF 信息，是内核 5.8+ 推荐的方式。

Q：为什么 off-CPU 工具能捕获 sleep？
因为 sched_switch tracepoint 会在每次 CPU 切换时触发，记录进程何时让出 CPU、何时重新获得 CPU，差值就是 off-CPU 时间。
让出cpu时记录一下, 再次获得cpu时又记录一下, 差值就是 off-cpu 时间。

Q：sampling frequency 设置多少合适？
on-CPU 推荐 99Hz（避免与 100Hz 定时器产生谐振），off-CPU 使用 tracepoint 无频率概念，只记录实际切换事件。
on-cpu 时间是不是也可以摒弃采样机制，用 off-cpu 相似的机制，
比如 当获得cpu时记录一下时间戳，然后离开cpu时又记录一下时间戳，差值就是 on-cpu 的近似时长。
完全可以，而且这是比采样更精准、零估算误差的方式，业界称为基于调度事件的精准计时。
时间戳来源：优先硬件计数器，硬件自增、纳秒 / 周期级精度、读取开销极小，每次切换读一次几乎无损耗。

还得了解它的缺点，因为你得在实际应用场景，要决策权衡优缺点来使用哪种机制，
时间戳来源：优先硬件计数器
 ^A2ukCBOb

环境准备 ^pJDX1w4n

在开始之前，请确认你的系统已安装必要的编译工具：
apt-get install -y clang llvm 
apt-get install -y libelf-dev  libbpf-dev bpftool
apt-get install -y zlib1g-dev linux-tools-common linux-tools-$(uname -r) linux-perf

# 创建项目目录
mkdir -p /workdir/ebpf-offcpu && cd /workdir/ebpf-offcpu ^mTCh9iEP

第一套：off-CPU 火焰图（捕获睡眠/阻塞时间） ^cNFLeEF8

步骤 1：创建内核态 BPF 程序 —— offcpu.bpf.c ^ydKUCBMv

// SPDX-License-Identifier: GPL-2.0
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>
#include <bpf/bpf_tracing.h>

char LICENSE[] SEC("license") = "GPL";

#define MAX_ENTRIES 10240
#define TASK_COMM_LEN 16

// 存储 off-CPU 统计信息
struct key_t {
    u32 pid;
    u32 tgid;
    u32 kern_stack_id;
    u32 user_stack_id;
    char comm[TASK_COMM_LEN];
};

struct val_t {
    u64 total_ns;
};

// 存储任务切换出去的时间戳
struct start_t {
    u64 start_ns;
    struct key_t key;
};

// BPF 映射定义
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_ENTRIES);
    __type(key, u32);
    __type(value, struct start_t);
} start SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_STACK_TRACE);
    __uint(key_size, sizeof(u32));
    __uint(value_size, sizeof(u64) * 127);
    __uint(max_entries, 1024);
} stackmap SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_ENTRIES);
    __type(key, struct key_t);
    __type(value, struct val_t);
} counts SEC(".maps");

// 目标 PID 过滤（0 = 所有进程）
const volatile u32 target_pid = 0;

// 使用 tp_btf 附加到 sched_switch 跟踪点
SEC("tp_btf/sched_switch")
int BPF_PROG(sched_switch, bool preempt, struct task_struct *prev, struct task_struct *next)
{
    u32 prev_pid = BPF_CORE_READ(prev, pid);
    u32 next_pid = BPF_CORE_READ(next, pid);
    u32 prev_tgid = BPF_CORE_READ(prev, tgid);
    u64 ts = bpf_ktime_get_ns();
    
    // 过滤目标进程（仅当 target_pid > 0 时）
    if (target_pid > 0 && prev_pid != target_pid && next_pid != target_pid)
        return 0;
    
    // 处理被切换出去的任务（开始 off-CPU）
    struct start_t start_val = {};
    start_val.start_ns = ts;
    start_val.key.pid = prev_pid;
    start_val.key.tgid = prev_tgid;
    
    // 获取用户态和内核态堆栈 ID
    start_val.key.user_stack_id = bpf_get_stackid(ctx, &stackmap, BPF_F_USER_STACK);
    start_val.key.kern_stack_id = bpf_get_stackid(ctx, &stackmap, 0);
    
    BPF_CORE_READ_STR_INTO(&start_val.key.comm, prev, comm);
    
    bpf_map_update_elem(&start, &prev_pid, &start_val, BPF_ANY);
    
    // 处理被切换进来的任务（结束 off-CPU）
    struct start_t *existing = bpf_map_lookup_elem(&start, &next_pid);
    if (existing) {
        u64 delta_ns = ts - existing->start_ns;
        if (delta_ns > 0) {
            struct val_t *val = bpf_map_lookup_elem(&counts, &existing->key);
            if (!val) {
                struct val_t new_val = {.total_ns = delta_ns};
                bpf_map_update_elem(&counts, &existing->key, &new_val, BPF_NOEXIST);
            } else {
                __sync_fetch_and_add(&val->total_ns, delta_ns);
            }
        }
        bpf_map_delete_elem(&start, &next_pid);
    }
    return 0;
} ^fwyJcz3V

步骤 2：创建用户态加载程序 —— offcpu.c ^k1jnJZPL

// SPDX-License-Identifier: GPL-2.0
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <errno.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include "offcpu.skel.h"

static volatile bool exiting = false;

static void sig_handler(int sig) {
    exiting = true;
}

static int bump_memlock_rlimit(void) {
    struct rlimit rlim_new = {
        .rlim_cur = RLIM_INFINITY,
        .rlim_max = RLIM_INFINITY,
    };
    return setrlimit(RLIMIT_MEMLOCK, &rlim_new);
}

static void print_folded(struct offcpu *skel) {
    struct key_t key;
    struct val_t *val;
    struct bpf_map *map = skel->maps.counts;
    int fd = bpf_map__fd(map);
    u64 *stack_trace;
    char stack_str[8192] = {0};
    char *p;
    size_t left;
    int err, stackid;
    
    // 遍历所有统计条目
    while (!bpf_map_get_next_key(fd, &key, &key)) {
        val = bpf_map_lookup_elem(fd, &key);
        if (!val || val->total_ns == 0)
            continue;
        
        stack_str[0] = '\0';
        p = stack_str;
        left = sizeof(stack_str);
        
        // 获取用户态堆栈（如果存在）
        if (key.user_stack_id >= 0) {
            stack_trace = calloc(127, sizeof(u64));
            err = bpf_map_lookup_elem(bpf_map__fd(skel->maps.stackmap), 
                                       &key.user_stack_id, stack_trace);
            if (err == 0) {
                for (int i = 0; i < 127 && stack_trace[i] != 0; i++) {
                    char sym[256];
                    // 这里简化处理，实际可以使用 addr2line 获取符号
                    int n = snprintf(p, left, "%s;", "user_func");
                    p += n;
                    left -= n;
                    if (left <= 1) break;
                }
            }
            free(stack_trace);
        }
        
        // 获取内核态堆栈
        if (key.kern_stack_id >= 0) {
            stack_trace = calloc(127, sizeof(u64));
            err = bpf_map_lookup_elem(bpf_map__fd(skel->maps.stackmap),
                                       &key.kern_stack_id, stack_trace);
            if (err == 0) {
                for (int i = 0; i <127 && stack_trace[i] != 0; i++) {
                    // 简化输出
                    int n = snprintf(p, left, "kernel_func_%llx;", stack_trace[i]);
                    p += n;
                    left -= n;
                    if (left <= 1) break;
                }
            }
            free(stack_trace);
        }
        
        // 输出 folded 格式：堆栈 时间（微秒）
        if (strlen(stack_str) > 0) {
            printf("%s %llu\n", stack_str, val->total_ns / 1000);
        }
    }
}

int main(int argc, char **argv) {
    struct offcpu *skel;
    int duration = 30;
    int pid = 0;
    int err;
    
    // 解析命令行参数
    if (argc > 1) duration = atoi(argv[1]);
    if (argc > 2) pid = atoi(argv[2]);
    
    // 设置信号处理
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);
    
    // 提升 memlock 限制
    bump_memlock_rlimit();
    
    // 打开并加载 BPF 程序
    skel = offcpu__open();
    if (!skel) {
        fprintf(stderr, "Failed to open BPF skeleton\n");
        return 1;
    }
    
    // 设置目标 PID 过滤
    if (pid > 0) {
        skel->rodata->target_pid = pid;
        printf("Tracing off-CPU for PID %d for %d seconds...\n", pid, duration);
    } else {
        printf("Tracing off-CPU for all processes for %d seconds...\n", duration);
    }
    
    // 加载并附加 BPF 程序
    err = offcpu__load(skel);
    if (err) {
        fprintf(stderr, "Failed to load BPF skeleton: %d\n", err);
        goto cleanup;
    }
    
    err = offcpu__attach(skel);
    if (err) {
        fprintf(stderr, "Failed to attach BPF skeleton: %d\n", err);
        goto cleanup;
    }
    
    // 等待指定时间
    sleep(duration);
    
    // 输出结果（folded 格式）
    print_folded(skel);
    
cleanup:
    offcpu__destroy(skel);
    return err;
} ^1HtFCkD9

步骤 3：编译和运行 ^leUPY3ne

CLANG ?= clang
LLVM_STRIP ?= llvm-strip
#ARCH := $(shell uname -m | sed 's/x86_64/x86/' | sed 's/aarch64/arm64/')
ARCH := $(shell uname -m)
INCLUDES := -I/usr/include/$(ARCH)-linux-gnu

.PHONY: all clean

all: offcpu

offcpu.bpf.o: offcpu.bpf.c
        $(CLANG) -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH) $(INCLUDES) -c $< -o $@
        $(LLVM_STRIP) -g $@

offcpu.skel.h: offcpu.bpf.o
        bpftool gen skeleton $< > $@

offcpu: offcpu.c offcpu.skel.h
        gcc -Wall -O2 -g $< -lbpf -lelf -lz -o $@

clean:
        rm -f offcpu offcpu.bpf.o offcpu.skel.h
 ^PIjdjSP2

编译并运行：

make

# 追踪特定进程的 off-CPU 时间
sudo ./offcpu 30 12345 > out.offcpu.stacks

# 生成火焰图
git clone https://github.com/brendangregg/FlameGraph
cd FlameGraph
./flamegraph.pl --color=io --title="Off-CPU Time Flame Graph" < ../out.offcpu.stacks > offcpu.svg ^fa6lIqLF

我实验的内核是 6.6.134，在qemu里运行的这个内核，fs发行版是debian12，帮我拟定一个完整的 libbpf + tp_btf 方案，提供两套例程，分别用来抓取特定进程的 off-cpu 火焰图，另一套例程用来抓取 on-cpu 火焰图。 ^Oqg61Sie

on-cpu 和 off-cpu
off-cpu 只知道某个外设慢，但不知道外设为什么慢(外设内部阻塞等原因);

1️⃣ 内存问题（不完整）
cache miss
TLB miss
NUMA locality

👉 on/off CPU 看不到“cache为什么慢”
因为无论 on 还是 off cpu, cache miss 都在随时发生着;


✔ on/off CPU 能回答：“时间花在哪里”
❌ 但不能回答：“为什么每条指令变慢”



PMU 性能计数器为什么能监测它们性能？一个计数器而已，原理是什么？
✔ 为什么 PMU 能看到 cache miss / TLB miss？
关键点：❗PMU不是“采样CPU行为”，而是“监听硬件事件发生次数”

👉 比如 cache miss 到从内存加载的这个过程中：
🧠 Cache controller 会“主动触发 PMU counter++”

NUMA 本质是：memory access distance
PMU/CPU 会记录：local node access、remote node access, 对应的计数器会累加

PMU 不是只计“执行次数”，而是计“哪些事件” 执行次数, 
相比于统计执行多少条指令这种底层语义，它统计事件次数，从语义上就更上一层。




🧠基于计数器的 "发生了多少" 这种底层语义，我能不能堆叠或者向上层组合出更高级的 "为什么发生" 的语义？
✔ 计数器本身不能直接给出“为什么”，但可以作为“因果推断的证据源”
✔ “为什么”不是一个直接观测值，而是一个推断结果（inference），它需要一个因果链过程。

能不能从“发生了多少（count）”堆出“为什么发生”，可以！
🧩 二、从 count 到 why 的三步升级
🟦 Step 1：计数（what happened）
🟨 Step 2：分解（where it happened）
🟥 Step 3：关联（why candidates）—— 比如A↑，同时B↓，导致C↑。
计数器不能直接表达“为什么”，但可以作为构建因果解释模型的基础信号，通过多维度关联分析推导出“可能的原因”。
 ^IOmBqOrk

perf+cpu热点火焰图 ^U9QG25Ka

❌ perf 不能很好解决的问题
1️⃣ 因果问题（why）
例如：
为什么慢？
是 cache miss 还是锁？
👉 perf 只能看到“函数热”，看不到“原因”


2️⃣ 短时瞬态事件
lock wait 很短
burst IO
👉 采样可能错过


3️⃣ 事件链路
IO → syscall → block → disk
👉 只能看到片段 ^qgK5xumB

🟨 三、eBPF（插桩 / tracing）能做什么
✔ 能解决的问题
1️⃣ 系统调用路径（强项）
open/read/write
socket send/recv

2️⃣ IO 延迟分析（非常强）
block_rq_issue
block_rq_complete
👉 可以看到：
IO latency 分布

3️⃣ 锁竞争分析
futex wait
mutex contention

4️⃣ off-CPU 分析（你已经做了）
thread 为什么 sleep
waiting stack

✔ eBPF 擅长回答：
“发生了什么 + 经过了哪里”


❌ eBPF 的限制

1️⃣ CPU 微架构不可见
cache miss
TLB miss
pipeline stall
👉 只能间接推断

2️⃣ 高频路径成本问题
热路径 trace 会有开销

3️⃣ 无法自动归因“时间占比”
需要自己聚合

 ^PnLn9KPe

🧠 七、为什么这个 pipeline 在工业界成立？

因为 CPU 性能问题本质是三层叠加：
🟦 1. 时间问题（perf）—— 哪慢
🟨 2. 路径问题（eBPF）—— 执行流程
🟥 3. 物理原因（PMU）—— 为什么慢 ^DUVZeXoE

## Element Links
xZQjot0G: [[Leve1-1 环境和工具初级使用]]

CHTyOlMW: [[Level2-1 机制级问题（工具不能直接给答案）]]

9xkT0taq: [[Level3-1 资源竞争（多因素）]]

AP9k4ze3: [[Level4-1 架构级问题（高级）]]

2Uo32x5U: [[Level5-1 地狱级难度]]

%%
## Drawing
```compressed-json
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

d4Lvhd6Lvxd85T9iNLvZd/LvFdylUG4crvVd+rutdzru9dwxHDd5igTd+bvLd5iBvd7bvSLPbvj5xO0nd0Rw+Ua7T3d57uIoPYffd/LvA98HvQ9+xTw91vikbHNhtADHu496gAE92Vuk9+VuU92nvUABnuM29nvc9wXv1t8XvS9+Xu891gfq92Hu6908HnD6gAm987u+UW3uO93Piu9z3u+90KBBYC+jh96Pu5txPup9+0dKLDPu594MKF989uV9

2vuN99vu99wfuj9yfuz9xfur9zfu794/vn9472wp7ebDuHD6WG5VzeVew33XZw2CMK/uEt0lvuZClv0t5luct3lvWMX/uAD0AfKt1gewD01uWt7WOOt91vet/1v4D+xTED+Nuft6geFt8tuBxatv7jzgedt3tuBxYduTt2duLt1dubt+Q57t49vnt69uPt19vHj/Qf9d3pgmD5Dvod7DvFJfDv2d0juud2jvg8zwe8d9WuCd9CGidyTuOjqIfqd7

TvWDzIfqBdfAWd0ieOD0oeed3zu/t4vuhdyOiRd5bExdwYetD1LuOAFigZd37v9D4YfUACru1dwYfqQKYfM99CeOAJYfrDxbujt1busMT7u7d1FyHd7MHXDy3uPDx7vklF7vpTw4eA90HuQ90NubScEfI9+EfUALHv49+1vE98nvU98J9095nuUj39v890XuS92XvsUBXui9zXv8jw3vZg8Ue3D63v296gBO993usUL3v+97Ueh9yPuUqmPvJ99P

vGC7PuUm3kLOj0vvV94wX195vurYbvv999CLD98fvT91RXz95fvr97fuH90/vlV6hzJnVLPNCez6rMxrrfotgBGgIQBCoODNiocBtG9oN1TV+1hzV44EiklYSxXkT8RTMkIPdv3sA2usit866g+CoPmzNziMKvRccghxa5QiQ+WJOav6ISRfnXy5lmboQL7i0bv77gYHRV6NsYiPq38YrLmkxCBVns11Vnc19tQIt0hQot0Wv0AAhX/w9kpVw4AB

Jo0AA/qlm7xguAAFLS+N/53jmFee/wzeeuBA+enz6+f4N1uCbzfU6Xe5FO3e9MuSk7Mv3PZ+fvz7+fTdy+e3zyoPC3XC2VieqvLM53nSbTAARgE7A+IJrTeAzJuNbXJvWz2vRB3o+DmTTzNQUtDQ6Br+XLDsth4gLHQE8UpuOPU1tzy94OTN/c6/V486BPcEP2W4F9PZx868julndjVcjjhoK3/nTXpnCIf1yFm7qJWxnqDnVpYk8ZkOQt/iSwtz

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

cgB85KoARgBWAG4AfgBRAEkAWQBrGIUAZqBEIE0Aa3yr4HfbowBLAFsAZQ4HAH4MFwBPAF8AXkoQgEiAWIB9+4SAVIBMgFhYPIBigHKAaoBGgFaYM6Bzv66AQYBxgGmAeYBVsJWAbYBjgHOAa4BKVQeAV4Brlb74P4BaQFBASEBYQERAVEBMSAxAXEBCQFJAdSBqQHpAZkB2QG5AXpgUMH6AfGBwR4vWmTB1YAVAUQAVQE1AdsBEKL1AUPCvIEtA

W0BieYdAV0B9Pg9AWZ2fQEDAagAQwFQACMBYwHwphMB0wFzAQsBvX7LAasBmsLrAazKfME7AaRY+wGHARCixwGnAcB2c0aXATGgJMGIgXcBDwEDik8BLwFvAYSBXwGa2r8BAIFAgaCBz/J0QVCBmpawgfCB+R5IgSiBaIHtHBiBWIFz4jiBeIEEgZ8BpIHkgZSBKiEFgYyBAWAsgRyBJ8G8gfyBYiEcACKBYoESgVKB7sRWwnBBCoFKgSqB6oGUA

QYhkpI6gXqBBoFWwkaBpoHmgZaBxn7WgdYBtoH2gR40joGTAdb+boEegV6BDcI+gTMhAYGoAMGBoYHhga+GkYFHIdGBBc7tHHGBYe6Jgd/BgvKpgVySmYHZgbmB+YHtHEFe9IErgaWB5YEBWlWBNYEUQYYhDYFNga2Bl4FdgWZsPYF9gV5BRyr5HkmB5NYk8mLBZICTgTOBuYHzgYuBy4FFgeuB24G7ge0c+4HJKIeBJ4FngReBlFhFMteBt4EPg

U+BL4EWbO+BSsE/gX+BlFiAQSBBq0FckhBBTMHaADBBZIBwQfbBKEHoQZhBOEF4QYRBxEFFgaRB5EEnIeig1EG0QZghkoAMQcxBrEHtHOxBHADcQbxB/EE2YIJBwkGiQeJB8iGSQbJB8kFEoopBykGqQepBmkHaQbpB+kGGQYNsJkGEOGZBFkFWQTZgCMFDOvZBdeKOQc5BC16uQR5BcKGoAAVB/kHmuoFBOLrBQaFBkrrhQea6ugg7otFBRDbeQ

fFBiUFt4slBHGZuRqlB6UGqJllBOUG/MnlBsQoFQe/B0oqFCoihMADlQTQBo5J0sjVBuPJ1QVySjUGkWC1BbUHV4h1BpFjdQWyh+UHxQYNBE/IbjKNB40GTQVEhT0GzQQ3i80GLQctBDaGZob5BG0HWwTtBe0FfIUdBJ0HnQVdB7Rw3QfdBj0HHbi9BUKJvQZ9BdeLfQX9BAMFA7sDBVZpgwRDB2iEwwWZgcMGG/vr+SMGowZjB2MG4wVWa+MGEw

cTB8IGkweUBLMHMAFTBNMG8cHTB68IMwQ4BnKEPoWzBI6Icwf1A/HDcwSOivMFbAQLBQsEiwZzB4sEKwTLBcsHkoYUyCsFKwSrBr4HqwZrBMSA6wXrBBsFaYkbBqFZv6mbB2WR3QIji1sHXQGlKnAD2wY7BzsGOAW7BHsEbMl7BAYA+wXmhAcGCABpiApL6YheigQrhwZHBMcFxwaRYCcFJwXQWKcFpwZnB2cGinnnBBVaFwSXBZcEVwXpgVcE1w

dEB9cGNwc3BEERtwR3BXcG9wf3B1nKDwe9mw8GjwePBk8F6YNPBs8HzwYvBK8FrwcuuG8Fbwe0ce8EHwcfBxgGnwefBqySXwdfBt8H3wcyqkJojflH+v9LjfnyWcf7VfGUmj8EA+s/BciHtQPf+H8FfwX7Bb/5/wT/+Fv5AIXpgQAHkOKAB4AGQAdAB9PiwASlU8AFIAQteKAHoAZgB2AF4AQQBxAGkAeQBoR6UAbKhwQDYIfQBeCGsAewBnAHcA

VpgvAGUOAIBwgGiAfT44gFmbJIB0gGyAQwhSgEqAeoBmgHaARwhhgEmAWYBFgE2AfYBTgEuAW4BIlaeAcqhfgEBAVIhoQHhAXpgAWEKIfEBgXLKISkBkiEZAVkBOQFEonkBBQE6IY8hWmL6IeUBHRyVAWoA1QF5HrUB5iHRAQ0BJsJWIa0BemDtAZ0B3QEZ5hD+TiEhfv0BgwGKSsMBowHjAd3gkwEzAfMBc16LAQEheShrAVzmISFbAWEhESFHA

ScBZYZnAZraOHY7sIkAiSGoALcB5Dg1IY8BzwGvAe8BnwGxIdGgOSGAgSCBYIGFISVhxSFwgRwAQ4HlIeQ4qIHogcWmNSF1IRBE+IGZIU0hFIGUOFSBNIHfIfSB7SGdIZyB1mE9IYUyyqEDIdpgQyHSgaMhxcJygeMhWmDKgWqBGoGKSichcyHJKPqBpFiGgcaBZoEWgVaBhTI2gSF+doFSLNsh4QC7IS6B7oGsYp6B3oG+gdqBgYEhgWGBEYFRg

TGB9yHcyLohTyF+wSmBbEBvIVmBs4FfIT8hhYGYoCWBZYGVgdWBtYEnIWChLYFtgTBhUKEwoe1u/YFsoUOBeaHIoWOBqKHTgbOBmKFLgfpIK4G4oTuBAVp7gQeBpFjHgaeB54GXgZShjop3gY+Bz4GqwW+Bm1IMob+BmsL/gcBBoEFh7hyh0eHcobyhNmCIQfyhXmAYQdhBuEEEQURBJEHOimRBIKGSklKhLQEyofIhFUHyoSxBTwpsQX0hqqF8Q

QJBhDhCQQ4BIkFiQRwAaO4SQdJBckG2QUpBKkGtbmpBGkFaQTpBDcJ6QQZBJ8JGQTahdqGWQRBE1kHyIbZBLqFuoemSLkFWYG5BnkFsob6h3e4BQU5GQaFABmFBziYRQQGAUUHfobmS/UGxofGh7kZJoWZgGUGpoa+GuUHhilmhxUG5oc8hBaFuykWh1UEBgLVBuCD1QRWhVaE2YO1BKVSdQT1BUBFNoQYALaEjQc8QY0GABhNBWeFTQTNBc0Fpw

X2hrIErQVARQ6HpAJtBEVJsAKOh+0HtHBOhZ0GXQddBd0EPQU9Bi6HLoV9BP0GkWP9BgMFboTuhkMG7Yfuhh6EIwSeh6MFYwTjBeMGWxC7BRMHI4SchD6FPobTB9MHaSIzB0eFfoezBikqcwf+hE4E8wVFyfMEgYcLBpkiiwWOBAsGQYbLBVFbywVLB8GEVFohhGsFawbrB+sGlIRhhxsHYYd7BFsH4YcwRhGG2wSRhTsEuwRRhH+GewThhuFZ0Y

SLBDGF8okxhocGsYRHB0cGxwVRW8cGJwcnB7RypwenBWcH67rnB+cHFwaXBg2blwZXB1cHQirXBI6INwTFWTcHOwi3B7cGdwd3BfcEDwR0cQ8E2RlphE8FTwfOSM8FzwQvB0kbLwavBVmDrwZvBO8H7wQFgR8EnwWfBF8FXwW24N8F3waxi7L5oeqqubeaoXh3mZf7arqKKXkB9kk7ATqCPvBP8tX5Z0Caul2DA4ILwXMy/ALqYiUiU/CtybbBFt

Hsomm5IxEsovLg1GNqIiJD+gvRUolpbloLUkFCzSFp0g56mblq+0pq8/lP+/P6z/qta8tpScguepr7B4tCARlrHGnGuidBT1AmkutoMwnoM1aKHspHQrtD1ZOe+qXyuvoeeqTLrYC2AjiyV3LLOKvw96KWeXYLWZhIAVOIWQDCC+AC+ri2+67gN/pbqPjrC8GpYcuw/UM8SgxoFMLrOwNI+bt0QZ77wUAsULRgqvu7q9s62WNz+HF78ekta7s7Ak

SJ6SYLezteEi56bvuPozYDQkZb6z3QXANSwSa5quG4irESpMN4CLr5KXjmubaIn/t6+mTLHMCchdeIpVP+GgAA4coAA/pFXrghW6ob6Qf+GeKBzXkSiV64tuNpIzMglXrn+bv6l0vhg5pGWkX+GtpH2kY6Rd17OkbigrpHukZ6R3pFh/na60x7AXtH+oF6x/mw2U3725h66AZHWkXaRDpFOkX+GLpFukR6RXpHFXj6R8xEUWvjaGhKjcloOpNrnI

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

fEm0S9JILFW0W7uNtHJKHbRQ/HkOI7RhpIu0W7RHtFe0R/xU/F+0SBRs/ENaCHRYdGR0UvxK/Fr8VmSSdFuktvxGdEc5lnRemA50XnR29GZioXR5RLF0bxJjBaX8aTJ1/G38c3RrdHt0Z3RDWjd0UmavdHUBv3RDWiD0cPRu9Gj0cWm49GT0dzI09EOAbPRC9F6YEvROAEr0cbea9HmupAJ0AksybvRsAkcsafR59GkWJfR19GoCarJD9G+0U/RL

9HYCV/RP9GuVn/R6CFECSAxYDFkCRQJHABUCTEKNAkIMbOASDGYAIwJzAmsCQYxi4p2CazmxDGkMWYxvAl2MVYxAgm0MfQxHADSCXkKLDEexAJJUgmiCbIJGIDyCfwxignCMWUOZgBiAGoJkjHJKNIx2gmxCnIxCjEGCQ8JKjFqMRoxWjHFyToxBgl6MdOBBjGhyagATBYOCW9qfTEbDlYxNjEmsfYxngkQjt4JUQC+CW4xHjF9IUEJlFh+MQExQ

TEY8d5Jk4BhMfOigzHB5vEJ8TEcAD0xKQkFCWkJzQl5MagABTHaYEUxjTH5CZkx6tZFCT2KJQm1MRwAHQkVCXAAcADRCc4qbTEdMckoXTHsUj0xjQndyc0JwzFWwqMxjTETMd0Jp8l9CQsxSzErMXpgazGkWBsxEwm7MfsxT8mHMeO0xzGUOKcxpFjnMdcxSwkPMafQqwkB4W8xHzHk4SUBOwl7CQcJC0abcUCx8Ml98eCxULEwsXCxCLF/CTcJ6

LGsIfcJRglPCVBRLwlksZ4YlLHUsbBRtLH0sdcxvwn/CcbebLEcscCJ1wG8scy6/LGCsYLSwrGiseKxkrEJ2tKxsrHpkvKxirHG3iqx6rGasWSA2rF6sY4BBrFGsUiIfclkiRSJVrHUiSOidrEOsXPxjIm8cG6xrCEesQOKXrE+sX6xAbFBsR7CIbFjickogonCidGxeShbSRKJbVGJsbg4KbFpsRmxvHBZsbmx+bFVUIWxWyE2gI6BwLHqiZWxg

gHVsbWx9bHSRo2xEADNsYaJbbGOhqaJrlZdsRgpZmB9sQOx2ClaYnaJDom0Uc6J07GCFtns87GLscuxh2a+ieuxTL6bsfgw27G7seUBIYlhiWex5wCXsdext7Fewvexj7F5ws+xb7Efsd+xjoq/sf+xXmCAccBxZmCgceBx3Mi5iXBxiHHIcagAqHHoceuJunEViURxcIkkcZbEZHEUcX8JVHE0cXRxDHFMcSxx7HGccdXi3HEhfrxxAnFCcZVJI

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

mVYxbjF+MUQRITFtsrV5STFY4hkxSalFh7exFTFNMV0xQzFjmIsxezFnMXcxTzlvMUVZcZWDsXkiaCIosVZkkalBsU3ojLF9PhyxTIASqVKxaqlOgAaVurF3vBapYnFOqUJxbPlsOUipWbFKsCZaVbFAgjexXbFYAXj5U7F+ICQwLDlgcWJxSSllqVCxTil9gVEpUHFJKVhpRwA4cXRxbHF1sSv5fflCOUhxanF6cWZxV5g2cW5xSUBFcWFChgFo

5IlxQOKZcU9ilHldIij5TXFdcVwFQ3FqABNxS3FbcUlRZ3F3cWt7n3FA8VqhkPFI8WjVuPFk8WuVtPFc8WVeQvFHABLxSvFT8WbxdvFjBa7xWCuB8VHxSfFZ8WqhZfFuDHXxbfFHAD3xWSAj8UbxfvOL8WKpG/FH8V14l/FpADUAD/FkhV/xXpgQCUgJfvOYCUQJZmKUCUwJYAlcCUIJUglDEYoJa+GaCUYJYOx2CW4JfglXmCEJdmJpCUUJVQlr

aqHSYwlzCWsJewl3MicJbiJ4RZtxYbWAiVCJaIl4iVgBZIlUSLSJbIlCiXB5kolKiUupeolzBaaJdolYCl6JQYlO85GJSbRJiVmJRYlNBZWJTYlv7r2JU4lLiWY5ctmHiW3Xl4lLWG+Jf4lgSXBJaElC0bhJVElMSVxJQklTBbJJaklgKXpJXpgmSXZJbklrOb5JYUlJSXlJZUlQoAupagArRV1JSUljSUtJW0lt+KdJd0lvSX9Jf9l7qWK5eMlk

yXTJUZBE2XV1vMlqACLJcslYdYLpcziE5pvNnslDi5A7kclJyVZFazmFyVXJalyNyU+YA759yUQRI8lsIkvJW8lw0bgOtRBG6W/JWgA/yWwpWSAIKU7cWClyKVQpeSsMKWApXCl3MiIpcilAoCopb8yGKVYpWSAz+V4pfkohKV35RalX9RkpT8lo5KUpdSl4eW0pa9i9KXITkylzJKjYmylFOVzpSDlkKWEDslWEOVCpQGlJOWipdQy4qWSpUKFM

qU5SgSAkbKKpYrFKqUqxWvlasUapZrF0bI6xTPlJqX2hVyV3qWmpTCVD+WmVtalpAAo5YTWL0Do5U6lXRVY5e6luOV75QTlfqXE5XdgZOUuZZTlocW34hGlUaUxpXGllXkJpRZsh8UppWmlDiUZpXpgWaW4JbmlAIH45usxhaXFpaWlNErlpTDJ7DFVpXaVdaUNpU2luRCbLuBl36X0Zd2ljGK9pZOazAD9pQsmIWUP1l6VOU40LtSS46U3kg7GU

6Xk5bOlnKWA5eslSxVsCMulq6WYoOulkWXhVlulqXa7pWelr9aJNjJlEQBAZaeluXavZYelRZW3pQHK96WOxgs2T6UFBC+lIGXnhgRlIZU2Zb+lQMCllXt6QGV2ZTCC76VNlURlHaXelQelHZVyZfBlogAbZbUuCzbf1L6qaGXbEixlfZoL4thluGVc9h6VoWWhlf2OjGX8McxlLAA8dv/2KbY8isuVzZV0ZWGV65XTlRhlg5WXpRxlyA54ltxlv

GWoGoplmGVCZTLQImViZRJlKmXSZQBlZZUaZbeV3UBKZZJlqmVnlbJlYZWaZf3q2mWPhgEMemXjkAZlNoBGZS3lpmU1ADAgPUCWZcGVfZWQZe9l0i72ZQEMjmX4MH9luJXxlQulXmWBNnpgW2V+ZdFlQWWqBfuVyFXhZTlOGZUkVV4WrWWVZceSSWWdZfiy3WW9ZdD0zWW5ZYFlBWXSRsVlpWV0Ei/i8WXZAAxV1WXJZV1lDWU9ZU1lA2WnWHRVC

WVCVR1lrgB1ZSxVElV1ykNlI2VjZcCW8xVrZVDOs2UxZfNlbAiLZTliYdYrZYPuU2VQzmEWRFWYoLtl+2Xu0odlN2UnZdiAZ2UXZXSy12XKLrdl7Pb3Zckoj2UuVc9lLlXtleeVqFVAwGsKDEZfZXduP2VxodhVcZVuZQul7w6g5fylFLou6JDlipWk5bfl5qWClValyOV2pY+iDqU4WpKV1SWupTKVnqVylXjyjYb+pdDlZJXKlSGlFQ5U5Rm5R

IWIbuMupIUeYahuFIUTEqIsNOV05S5F7kX4MJ5FCEreRb5F7OX1KVdF3OXrorzlmaYy5RziguVVRU7lSUWsOilF6NZpRYcyUuXsUvzlsuXjVZBA+UVK5dSARUUxViVF6uUZhTWFWuWVUTrlDUWtrk1FfFUtRWOKbUXZAabl5uW9RRpi/UWkAINFohbDRaNF/daTVS7l00WzRQVezuWoAItFy0WrRagAvuX+5XeqgeW7RSHlYeUR5adFEXkx5S7ac

eUPRU9FL0Vv+m9F1w6p5T9FGeUxClnlwMW55fnlheWn5cXlI6Kl5eXlKMVV5edFVrot5elUOMV4xQTFpkhExc3lGMUpReTFgTaUxYKFlXnd5fTFEKX95cwlQ+VDVSPl/MUklRPlIsV34mLFu+WsTkmVssXQ9kvljJXKxRoALJXqpRrFW+WclULVfJXGxWSVh+UWxXviUMWP5Y7F9sVQ5VflLsVyCvyVKVUI5RrV5InP5ej5ApUAFcnFYcXFwpHFM

cVxxWbVdQCVVSnFacV4uiAVYBWuVnnFiBXQFagAsBXwFZAVSBU81bXF9cW0JQgVmBU8JTgVrMVdxT3FBBVghoPFw8VcJaPFdIjJxVKlwoWBNpQV88WLxcvFa8XCFagAW8U7xbQ4e8VsFcfFp8XCfOfFgtLcFUIAvBV3xQ/FDBUiFYClShWoAO/Fv8VQgTIVjdWASgoVwCViFaAl6VTgJZAllhYaFVoVXmCIJcgllXmoJeglmCUxAdmleCVDsWYVR

CVaYpYVlCXUJbXSh4n0JUwlnMUOFRwlcdU8Je4VqACCJSIlYiWBNhIlqABSJZV5MiXyJYolyiU5JaEVzV6UOBEVOiXRFYYlxiWmJeYlXNGWJdYlemC2JewxjiXOJacl7iW4oJ4l3iUFFQElpFhBJZbEISUs5mUV0SVmwpUVDiVJJSklaSUZJVwIWSWOoc0VPRW1JfUlHRWUOPsVKDVtFQ0lzSWtJQKBIxVhYGMVWZIqlXiVUxUTJVMlMyUaVYsVy

xVbMHouFWJrFZySGxW7JVkut+LqjMcl39XnJQOKlyVM1aTmgIa3JecVlxXPJa8lQwnvJXFV9xV3Yo8VzEYS5gClQKWvFQJJNBYfFY5iPKVPFd8V1a4vFTi6CKVIpUo1QJWoAGilrMWYpdil1+W4pfil0JUG1fbVlqXwlYtSSJWoADSldKVMEhiVmgDMpdiVJDXupb8lBJV8pUSVcVWCpZflMOUUlVhGEqWCjtSVfQC0lfKlYtUKxcqlktVqpRvlm

qVaxdvlusUK1YbFZFW8lYk17sVmNZIAiOXe1ulVqOWZVRKVEACYNdjlfKKylfql8pU20iVVFQ5lVUKlFVUf5XpgGpXRpaSi2pWtZrqVSaUGlemljBaZpRPV5pW+Ufml1pUlpWWlFaWoAE6VNaUulY2lrlbNpZV21mWHlWZ4PpUaYn6VmxWBleEJEzX9lWGVY6X+lROlt+IxlS41kVUeZYulyZUrpWul5EobpdE2SzY5lSWV/5WFlXJlxZXnpe+VQ

5XLNRWV2YDjZZmVtZX1ld2VoGXkVbRlSzVSLm2VZzVXpWGVXZX4AD2VbzVhZbsuOU6+VQBV/Y4jlYhlmZbIZVOVm5WRoVhlOGWZ9vhlgLWrlfsux5WwtduVfHZUZci1LZUKAGi16GUsZd81F5W2dm5VmZU8ZSAmABJ3lYJlMkHCZQ+Fz5V6YL+Vb5UwZW9lgFVflWos9LWvlaC15zUstfYa2gBaZQE2jmK6ZVbC+mWJhoZlNeWwVeZlCFVWZZ6VO

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

VmSTw2Nrc2tpI1trXOtqADdrb2tLh0Dra2tzA0draOtjjTlqhOtwcDTrZkdw63cwNSAidLQDOVKK60xrZ0JkzEbrWStW60PrbYd+60EJoetR4AlSpPttG3vrVet4G1frXVt962SYP+td23tHbdtl62zbRBtd61HrQMds+ovrQ0tNm3j7SMdNW1dwL0d0G0tLYMdk1bwbfltVi3IbZylqG3oTuhtC23qiuJ8OG0hVXhtBG3hHe+tVG1tyWRt9ipMb

cRt1M0TbaOS7G03HSxtLu1sbYxtZx3cbXOKHu05ji2qy23n7ZRYom3ibQHNkm0EJjft021f1DTtbO2+kmCdam0UrV9tjG1A7X/qbW16bQZtxmr3HdptZm26bRZtcx098sBtdm391ufyTm0ubW5tQKW4IF5t6E6ZbX5trU6L7YFtVi3BbUVtxADhbaVtrW13YLFts20JbUltG8C8rWlt6J3ebZidvm3T7dSdIx0FbehO9J2MnVNtZJWsnRDt9m02k

gsd3631bZggLgrNbcydvJ3tbb5tnW3LHT7W+x0c7cdtXO1DbWjtyp1QAONtNm0oiOKdGJ1S7cCt08CNAFqdPx30+EJt1V6rbf8dhTL8cBttQJ1bbWStN+17bULtT20bHQjtJ22StJiA5236nWNtJU3DHWaKzYrY7X0AxO0xCm9tZu1wnW1QP20RnUvOpPL37YyKIO0fbSzt4O1RnY0KpO0M7bttcO05+Yjtm3WnbQGdqO0jbXztaE76rcVNiZ2i7

fpt+O3FCkTtg+1Q7QQmMO0S7fmdtO377Yzt722qkhmdkJ3lajbtg206UA7t5Z1JrYLtf20i7bjtKB0hnQ9Mku1xbRytMu1y7XlACu184tcKKu1SimrtMAAa7WUKGgohBpyATMYMncVNBu2k8h2dJu1dnWDtFu1zilbt9Go6nbbtx6BDncGd4u0vHasdNpLu7fjqUR1kCphJNVWuYWhNUc3cqnm5vLkFuThNxzDe7b7tKi2ZAGotQe0vQCHtHNJh7

UkA+i1mLQTyxi0iRpHtae1J7SwAWe2OLZdmMe3p7W4t9i3yqhhdAoBYXbntJCZL8oXtgS3IoiXtYS36dpEtle16wIaqNe2WVpGyBh2YIBitaS3N7QxdfKJr7SnyxCCd7TWtJ+0lLS4Nve1X7RYdT+0/Le0dJm3tHXMd0x2dLTPtUl0L7d0tE+2L8ivtUrBjLf0mOS1cXTwgm+0UCnMt9h237Sst9O3rLa/tXe3ifKfthTLCbUctQl3krehOol1rH

QEKKZ0Zyv3tIl1SYjAAhl28Xa8tHy1BgRZdtq1kHQAdnK3AHZodoB2kHdqtkB26rfodsB3MXf6t6B2BrcGt+K2RXSYdNh1VHdJtuB1TMnIdbh0KHQQmXl1wrT5dVB3crZydqW30HUKtTB1wrSwdvB1sHaqt0q0iHdwd4q2lXfwd/Qrt8lMK1wA6HcFdXq0SHf75SV0snZ8wpq2praldxB3pXYFd9q2IALOdah3Orf5dbq2FXR6tTV16HRIdTF3wH

VYdph22HZYdsV3WHZgdth1xrYatTh2dXQQdFsXuHdFWnh1LMT4dPfL+HVzAgR1b8sEdZa0dLTcdfvLVrTYAta2xHfWtTa0trbOtFI0pHT2temAl7Rkdj13ZHSQKY62zbZOthR0fXRoKpR2LrV7B6QCUlI0dXQm1HaPy9R39HVUdTR2brUetbR1z7R0dkR2ynUsdDR1PrVMdo+1BgI+d8x3dHbVt4x1/rejdgG1nrbMdVm2jHT0dd63LHXMdcG177

QhtBZ1bHRkAOx3rLRht+J2HHYuSuG38cPhtHG3BbURtFx2kbfdtgK3vHZRtyIB3HcadbIqPHYLdzG1lTcMdqADi3ZxtER3sCp8dr52gqoC2Am22nWZdAJ1rgZtt9l3bbeptMm1mnQptvZ13qkidgO3fbTyd5J18nSidIx1onWSdku3InZZtqJ0k3QpdNTZqyqgAhJ3Vrq5tkwXubaSd9l1mnXbdcl0sgHlt8O2M3aKdJW2mncatFW1snYlt4yDJb

Vyd6W1InRZtAp3yXUKdtJ2FbWSVxW0RbWHdMh2VbdKd1pIo3XBVnJ2NbUUgtECO7Sqddt3qnWjdmp053QWdA23c7UGd120lTfcdpp0qnYNdc21WnVXdqt12nQ6d620AxVrdUJ0gnTtt7fKJnT6dhZ3I7SWdd5313Q+dlMCu7UcK4Z1enVrAWZ02XaedGZ3fbeYK1Z3JnbJth+1zimmd3Z0abVRtC91cis2dOl1t8vmd/Z3FnYGdZZ1OHaOdwu1Jn

XjtxWoE7Q2dq52DCjmd5O3TnW2ddO1rLXGdsZ3MAIbdzir9nbXdF90VnVfdT201nWYdU52U7YFKLd3znR0gi53hKsudyu2o1ZlK6u1Cslud3MA7nbrtoqD67QQAhu36XSedX93nnXkKl53anb6dSO127fWA491O7VOdU90AbbFKuZJfHS+A+E1o/sX++nV7tVX6mIBTAEBAHAAXkB7AknkimBUYTTQymDtozNp7ABRkjc1Q0NpY75AaejdoYyx92

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
```
%%