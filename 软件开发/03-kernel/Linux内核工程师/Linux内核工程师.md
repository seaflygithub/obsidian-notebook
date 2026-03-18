

我给你一个**真实行业视角拆解**，把 Linux 内核工程师分成几种“工作形态”，再讲清楚每天到底在干什么。

---

# 一、Linux 内核工程师的本质职责（一句话）

> **保障系统在复杂场景下：稳定、高性能、可解释**

换句话说：

系统出问题 → 你负责解释为什么 → 并解决

---

# 二、核心职责拆解（你未来工作的真实内容）

我按“重要性 + 真实占比”排序（不是按教材）

---

# 🔥 1️⃣ 故障排查（最核心，占比最高）

这是你JD里已经写得很清楚的部分：

### 你每天会干：

- 系统卡死（hang）
- CPU 异常
- 内存泄漏
- IO 卡顿
- 偶发崩溃（panic）

---

### 实际工作方式：

现象 → 指标 → 工具 → 内核路径 → 根因

---

### 举例（真实工作）：

> 用户反馈：系统偶发卡顿

你要做：

- 看 load / CPU / IO
- 用 perf / ftrace / bpf
- 判断：
    - 是调度问题？
    - 是锁？
    - 是 IO？
    - 是中断？

---

👉 这部分能力 = 你的“核心竞争力”

---

# 🔥 2️⃣ 性能优化（第二核心）

### 你会做：

- 降低延迟（latency）
- 提高吞吐（throughput）
- 减少抖动（jitter）

---

### 优化对象：

- 调度器（CFS）
- 内存分配（slab / page）
- IO 路径
- 网络栈

---

### 举例：

- 减少 context switch
- 优化锁竞争
- 调整 IO 调度策略

---

👉 这部分决定你能不能拿高薪

---

# 🔥 3️⃣ 内核机制理解与改造

### 你会：

- 阅读内核源码
- 修改或优化模块

---

### 常见模块：

- 调度（scheduler）
- 内存（mm）
- IO（block）
- 网络（net）

---

👉 注意：

> ❗大多数公司不是让你“从0写模块”，而是：  
> **改 + 优化 + 修bug**

---

# 🟡 4️⃣ 工具使用与构建（很重要）

你必须非常熟练：

- `perf`
- `ftrace`
- `eBPF`
- `crash`
- `sar / vmstat / iostat`

---

👉 高级一点：

- 自己写 bpf 工具
- 做观测系统

---

# 🟡 5️⃣ 系统建模与分析（高手分水岭）

这是很多人没有但你要具备的：

---

你要能回答：

- 为什么 load 高但 CPU 不高？
- 为什么内存够但 OOM？
- 为什么系统偶发抖动？

---

👉 本质：

> **把“现象”解释成“内核行为”**

---

# 🟢 6️⃣ 驱动开发（看岗位）

你说你不想碰硬件，这个可以理解：

---

### 驱动分两类：

| 类型        | 是否必须 |
| --------- | ---- |
| 设备驱动（硬件）  | ❌ 可选 |
| 内核子系统（逻辑） | ✅ 常见 |

---

👉 很多内核工程师：

- 不写硬件驱动
- 但会改内核模块

---

# 🟢 7️⃣ 内核调试环境搭建

你需要：

- 编译内核
- 配置调试选项
- 使用 QEMU / crash

---

---

# 三、工作内容差异（很重要）

---

## 🏢 1️⃣ 互联网公司

工作重点：

- 性能优化
- 故障排查
- 内核调优

👉 很少碰硬件

---

## 🏭 2️⃣ 嵌入式/芯片公司

工作重点：

- 驱动开发
- 硬件调试
- BSP

👉 硬件很多

---

## ☁️ 3️⃣ 云厂商

工作重点：

- 虚拟化
- 调度优化
- IO/网络优化

👉 高级内核玩法

---

# 四、你未来每天实际在干什么（真实还原）

一个典型一天：

---

### 上午：

- 看报警（CPU / IO / latency）
- 分析问题机器

---

### 中午：

- 用 perf / bpf 抓数据
- 定位问题路径

---

### 下午：

- 看源码
- 验证假设

---

### 晚上（有时）：

- 写 patch / 优化方案

---

👉 本质：

> **不是写代码，是“破案”**

---

# 五、岗位能力结构（你要对标的）

---

## 初级（1~3年）

- 会用工具
- 能定位简单问题

---

## 中级（3~5年）⭐你的目标

- 能独立排查复杂问题
- 理解内核机制
- 能优化系统

---

## 高级（5年以上）

- 能设计系统
- 能解释复杂现象
- 能构建工具

---

# 六、你现在的路线是对的（但要注意）

你说你想：

> 专注“内核行为 + 系统现象”

👉 这是**最正确、最稀缺的路线**

---

但我要提醒你一点：

> ❗不要完全逃避“底层机制”

因为：

- 不懂机制 → 无法解释现象

---

# 七、给你一个现实建议（非常重要）

你要把自己定位成：

> ❗**“内核侦探（Kernel Detective）”**

而不是：

> ❌ 写代码的人  
> ❌ 配环境的人

---

# 八、如果你要对标JD（你最开始贴的）

你需要达到：

- 能排查：
    - hang
    - OOM
    - deadlock
    - IO异常
- 熟悉：
    - mm
    - scheduler
    - block
    - fs
- 熟练：
    - perf / ftrace / bpf / crash

---

# 九、下一步我建议你这样做

我可以帮你做一个非常实战的东西：

👉 **模拟你未来工作**

比如：

> “线上机器 load 高但 CPU 不高”

你来排查：

- 我给你现象
- 你一步步分析
- 我帮你纠正思路

---

或者：

👉 给你一套：

**“3~5年内核工程师训练路径（按周拆解）”**

---

如果用一句话总结这个岗位：

> **用工具 + 理解内核机制，解释并解决复杂系统问题**

---

如果你愿意，下一步我可以直接带你做：

👉 第一题“真实线上故障排查演练”（难度=面试级）





# DDDDDDDDDDDDDDDDDDDDDDDDDDDDD

# DDDDDDDDDDDDDDDDDDDDDDDDDDDDD

# DDDDDDDDDDDDDDDDDDDDDDDDDDDDD


👉 内核工程师的门槛不是“高学历”，而是：
> **你是否愿意长期做困难、枯燥、没有即时反馈的事情**

比如：
- 看几千行代码找一个 bug
- 为了一个竞态问题 debug 3 天
- 理解一个 obscure 的调度行为


- [[#内核-环境和工具准备]]
    - 内核运行环境：笔记本+qemu
    - 内核编译环境：笔记本+docker
    - 内核问题模拟器（训练题库）
    - 必须非常熟练工具:perf,ftrace,eBPF,crash,sar/vmstat/iostat
- Level1:基础操作入门级（单点问题/线性因果）
    - 调度问题——实验:死循环CPU飙高
    - 内存问题——实验:内存泄露 
    - IO问题——实验:fio随机写（IO卡顿）
    - 锁问题——实验:mutex死锁
- Level2:机制级问题（内核味）
    - 中断/软中断——实验:软中断风暴
    - 网络栈问题——实验:高并发socket
    - NUMA/Cache/CPU架构相关
    - 系统时钟/定时器/延迟
    - 系统抖动/尾延迟
- Level3:资源竞争（多因素）
    - 调度 + 锁
    - 内存 + IO
    - 中断 + 调度
- Level4:架构级问题（高级）
    - NUMA问题
    - Cache / false sharing
    - RCU 问题（高级）
- Level5:地狱级（真实面试杀手）
    - Load高但CPU低
    - 系统偶发卡顿
    - 内存充足但OOM
    - CPU不高但系统慢
- Linux 内核工程师的本质职责
    - 故障排查（最核心，占比最高）
    - 性能优化（第二核心）
    - 内核机制理解与改造
    - 工具使用与构建（很重要）
    - 系统建模与分析（高手分水岭）
    - 驱动开发（驱动分两类：设备驱动、内核子系统）



# 内核-环境和工具准备


## 编译环境

为了方便环境迁移以及不污染宿主机系统，采用在 docker 中编译源代码。

docker环境可以参考下面笔记里的 qemu-8.2.0 这个章节：
[[docker-qemu虚拟环境]]

相当于基于 qemu-8.2.0 来运行Linux内核，所以这里qemu版本要留意。


## 运行环境

🐳 Docker → “干净、可重复的构建环境”
你用它做：
- 编译 Linux kernel
- 编译 rootfs（busybox）
- 构建交叉编译工具链
👉 优点：
- 环境不会污染宿主机
- 可以版本固化（非常重要）


宿主机运行 QEMU：
```bash
qemu-system-x86_64 \
	-kernel bzImage \
	-append "root=/dev/sda console=ttyS0" \
	-drive file=rootfs.img,format=raw \
	-nographic

# 进阶玩法
#     gdb 调试内核（-s -S）
#     virtio 驱动测试
#     eBPF tracing
#     多核调度实验（-smp）
```


## 内核版本

Linux内核版本：我直接给你结论（2026年的现实建议）
👉 **主力学习版本：6.6 LTS**
- ✅ 长期支持（LTS）
- ✅ 企业大量使用（服务器 / 嵌入式）
- ✅ 文档、资料、issue 都多
- ✅ bug 相对稳定（适合学习和调试）
https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.6.134.tar.xz



工程级用法，👉 用“双内核策略”：
```txt
kernel/
├── linux-6.6/    # 主力学习 + 实验
└── linux-6.13/   # 新特性对比
```

**一个关键认知（很多人没有）**
👉 内核工程师不是“用某个版本的人”
而是：理解“**版本演进**”的人
你要能回答：
- 为什么调度器变了？
- 为什么 mm 改了？
- 为什么某个 bug 在新版本消失了？

---

<font color=blue>内核源码目录：/workdir/linux-6.6.134，帮我写一个一键编译配置编译的脚本 build_kernel.sh，能够支持内核调试的那些配置项也自动给我配置上。
</font>

给你一份**工程可用的一键内核配置+编译脚本**，专门针对你现在的实验平台（QEMU + 可观测性），会自动：
- 生成 `.config`
- 打开调试 / ftrace / eBPF / lockdep 等关键选项
- 编译 `bzImage + vmlinux`

内核编译脚本: build_kernel.sh

---

## 根文件系统

👉 **主力：BusyBox（静态版）**  内核开发/调试，越简单越好
👉 **进阶：Debian rootfs（bookworm）** 系统行为分析，越真实越好

👉 BusyBox 1.36.x（2026 仍然主流稳定）
👉 Debian 12（bookworm）：glibc 新（适配 6.x 内核）、稳定




BusyBox（**验证机制**） + Debian（**验证现实**）
👉 rootfs 会直接影响你对内核的理解，比如：
- BusyBox：
    - 系统很“干净”
    - 你看到的是**纯内核行为**
- Debian：
    - systemd / udev / service 很多
    - 你看到的是**系统交互行为**
👉 两者必须结合


👉 带你做一个：“**可观测内核实验系统**”（你之前提到的 tracing 思路）
这个项目是可以直接写进简历的，而且含金量很高

---

### Debian12-镜像下载

浏览器直接搜: debian rootfs x86_64
https://github.com/kbaraniak/debian-rootfs/releases

以下为常见其他架构及其Debian支持情况：
ARM(armhf): http://ftp.debian.org/debian/dists/stable/main/installer-armhf
ARM64 (aarch64): http://ftp.debian.org/debian/dists/stable/main/installer-arm64
MIPS: http://ftp.ports.debian.org/debian-ports/dists/stable/main/installer-mips
RISC-V (riscv64): http://ftp.ports.debian.org/debian-ports/dists/stable/main/installer-riscv64


### Debian12-制作镜像

百度网盘目录: docker-qemu-8.2.0-kernel

```txt
build_rootfs2img.sh
	负责把官方 debian 的镜像解压到指定目录，
	解压后，目录里就是rootfs目录树内容，
	然后该脚本就是利用该目录树生成镜像文件 debian.img。

build_img2qcow.sh
	格式转换: debian.img --> debian.qcow2
	
build_qcow2img.sh
	格式转换: debian.qcow2 --> debian.img

build_qcow2_ops.sh
	根据需要手动查看并执行里面的命令
```


### Debian12-启动qemu

```bash
# QEMU 启动参数（核心）
qemu-system-x86_64 \
  -kernel bzImage \
  -drive file=debian.img,format=raw \
  -m 2G \
  -smp 2 \
  -nographic \
  -append "root=/dev/vda console=ttyS0 rw nokaslr"
```


一键启动qemu脚本: run_qemu_debian.sh
```bash
kernel=linux-6.6.134/build/arch/x86_64/boot/bzImage
fsimage_qcow2=debian-rootfs-main/debian.qcow2
# quit internel qemu: Ctrl+A X


qemu-system-x86_64 \
  -kernel ${kernel} \
  -drive file=${fsimage_qcow2},format=qcow2,if=virtio \
  -m 2G \
  -smp 2 \
  -nographic \
  -append "root=/dev/vda console=ttyS0 rw nokaslr"
```


qemu系统内的网络配置（另一种手动方法）：
```bash
# (进入qemu系统后可选)一个更“硬核”的方式（不依赖 ifup）
# 你也可以完全绕过 networking.service：
ip link
ip link set enp0s3 up
ip addr add 10.0.2.15/24 dev enp0s3
ip route add default via 10.0.2.2
echo "nameserver 8.8.8.8" > /etc/resolv.conf
# 上面这个方式非常适合你做：内核 + 网络路径 + 性能实验
```



---


### Debian12-快照管理


**1️⃣ 创建 qcow2 镜像**（如果你还没）
```bash
# 创建一个全新镜像
qemu-img create -f qcow2 debian.qcow2 4G

# 把已有镜像转换成qcow2镜像
qemu-img convert -f raw -O qcow2 debian.img debian.qcow2
```

**2️⃣ QEMU 启动参数**
```bash
-drive file=debian.qcow2,format=qcow2,if=virtio
```

**1️⃣ 创建快照**
在 QEMU 运行中或关闭状态都可以：
```bash
# snap1 = 快照名字
# 需要qemu内poweroff之后,再拍摄快照,否则该文件会被qemu占用着操作不了
qemu-img snapshot -c snap1 debian.qcow2
```

**2️⃣ 查看快照**
```bash
qemu-img snapshot -l debian.qcow2
```

**3️⃣ 删除快照**
```bash
qemu-img snapshot -d snap1 debian.qcow2
```

**🔁 快照回滚（rollback）**
回到某个快照：
```bash
# 注意:回滚必须在 QEMU 关闭状态下操作（推荐）
qemu-img snapshot -a snap1 debian.qcow2
```

✅ 备份方法1（推荐）：直接复制 qcow2
```bash
cp debian.qcow2 debian-bak.qcow2
```

✅ 方法2：转成 raw 镜像（你说的 img）
```bash
qemu-img convert -O raw debian.qcow2 debian-bak.img
```

---

🧩 九、**推荐你的实验流程**（最佳实践）

🧪 Step 1：干净系统
```bash
debian.qcow2
```

🧪 Step 2：做一个快照 baseline
```bash
qemu-img snapshot -c clean debian.qcow2
```

🧪 Step 3：进入实验

🧪 Step 4：出问题了？一秒回到干净状态
```bash
qemu-img snapshot -a clean debian.qcow2
```

扩容 qcow2:
```bash
# 原先从 debian.img 转换成 debian.qcow2 受到4GB限制,所以以这种方式扩容
qemu-img resize debian.qcow2 20G
```



### Debian12-qemu共享目录

最推荐：virtio-fs（现代方案，性能最好）
适合：Linux guest（你现在 Debian / BusyBox 都可以）

✅ QEMU 启动参数（宿主机）
```bash
-fsdev local,id=fsdev0,path=/home/linux/workdir,security_model=none \
-device virtio-9p-pci,fsdev=fsdev0,mount_tag=hostshare
```

✅ 虚拟机里挂载：
```bash
mkdir -p /mnt/workdir
mount -t 9p -o trans=virtio hostshare /mnt/workdir
```

✔ 效果：
```txt
Host  /home/linux/workdir
            ↓
VM    /mnt/workdir
```

---

scp / ssh（最简单但不是挂载）
如果 VM 有网络，在VM里执行：
比如把宿主机里面的 setup_tools_indebian.sh 文件拷贝到VM里面的 /mnt/workdir 目录：
```bash
# scp source target
scp linux@192.168.76.136:/home/linux/workdir/setup_tools_indebian.sh root@10.0.2.15:/mnt/workdir
```


### Debian12-安装调试软件

工具清单：
```bash
✔ eBPF 工具链
✔ perf / trace-cmd / ftrace 工具
✔ bcc / bpftrace
✔ strace / ltrace
✔ sysstat / iostat
✔ tcpdump / ethtool
✔ debugfs / tracefs 工具支持
```


一键构建脚本: setup_tools_indebian.sh
进入 qemu debian 系统后，执行工具安装脚本，一次性安装所有必备工具。

**🧩 1️⃣ 内核观测能力**
ftrace  
trace-cmd  
tracefs

**🧩 2️⃣ eBPF 全栈能力**
bcc tools  
bpftrace  
bpftool  
libbpf

**🧩 3️⃣ 性能分析**
perf  
sysstat  
iostat  
top/htop

**🧩 4️⃣ 网络分析**
tcpdump  
ethtool  
iproute2

**🧩 5️⃣ 调试能力**
gdb  
strace  
ltrace

❗ 1. QEMU 内核必须打开 debug config
```txt
CONFIG_DEBUG_INFO=y
CONFIG_FTRACE=y
CONFIG_BPF=y
CONFIG_KPROBES=y
```

❗ 2. tracefs 必须存在
```bash
mount -t tracefs nodev /sys/kernel/tracing
```

❗ 3. perf 版本必须匹配 kernel（6.6 OK）

你现在的系统已经升级成 ✔ 内核观测实验室（Kernel Observability Lab）

安装完成后，记得拍个快照备份一下。


---

### Busybox-制作镜像

build_busybox_rootfs.sh

编译环境在docker中，
在docker(root权限)中运行上述脚本自动执行源码配置和编译以及导出，
脚本执行完之后，最终在源码顶层目录的上一层生成 busybox_rootfs/ 目录：
```txt
busybox_rootfs/
├── bin/
├── sbin/
├── etc/
├── proc/
├── sys/
├── dev/
└── init   ← 关键入口
```

QEMU 启动方式（非常关键）
方法1：initramfs（推荐）
```bash
cd busybox_rootfs
find . | cpio -o -H newc | gzip > ../rootfs_busybox.cpio.gz

qemu-system-x86_64 \
  -kernel bzImage \
  -initrd rootfs_busybox.cpio.gz \
  -append "console=ttyS0 rdinit=/init" \
  -nographic
```


### Busybox-启动qemu


一键运行qemu系统: run_qemu_busybox.sh
```bash
kernel=linux-6.6.134/build/arch/x86_64/boot/bzImage
fsimage_busybox=rootfs_busybox.cpio.gz

cd busybox_rootfs
find . | cpio -o -H newc | gzip > ../rootfs_busybox.cpio.gz
cd ..

qemu-system-x86_64 \
  -kernel ${kernel} \
  -initrd ${fsimage_busybox} \
  -append "console=ttyS0 rdinit=/init" \
  -nographic
```



### 运行实验环境


一、Debian虚拟机实验系统

```bash
# 宿主机切换权限
sudo su

# qemu是docker虚拟环境编译安装的,所以宿主机需要初始化
source setup_qemu_runtime.sh

# 运行qemu虚拟机
bash run_qemu_debian.sh
```

二、Busybox虚拟机实验系统

```bash
# 宿主机切换权限
sudo su

# qemu是docker虚拟环境编译安装的,所以宿主机需要初始化
source setup_qemu_runtime.sh

# 运行qemu虚拟机
bash run_qemu_busybox.sh
```



### Buildroot

<font color=blue>Linux 6.6 内核，rootfs，我要用 buildroot，buildroot源码包选择哪个版本合适？
</font>

👉 **Linux 6.6 LTS + Buildroot 2024.02.x（LTS）**
👉 对齐策略：Kernel LTS ↔ Buildroot LTS

https://buildroot.org/downloads/buildroot-2024.02.13.tar.xz








## 可观测内核实验系统


👉 给你一套“6.6 LTS 内核实验路线”（从入门到进阶）  包括：
- 必改的 10 个内核点
- 必做的 5 个实验
- 如何写出能写进简历的项目

这个会直接决定你能不能进内核岗（不是开玩笑）


在构建具体版本内核的时候，需要确保整个链路大节点版本关系，可以通过询问AI来帮助版本搭配：

<font color=blue>给我列出不同内核版本需要的其他环境及其版本(u-boot、firmware、rootfs发行版、rootfs busybox)，以及与上一个版本最重要的更新差异。内核从 2.6 到 3.x 到 4.x 一直到最新的 7.x。
</font>

工程师必须理解的4条主线：

**1️⃣ 启动链变化**

```txt
2.6: bootloader → kernel (hardcode)
3.x: + Device Tree
5.x+: + ACPI (ARM也支持)
```
👉 重点：**DT → ACPI → firmware依赖增强**


**2️⃣ 用户态依赖增强**

```txt
2.6        BusyBox + uClibc
3.x        glibc 开始绑定
4.x+       systemd 强绑定
5.x+       容器 runtime
```
👉 重点：**kernel 已经不再是“独立层”**


**3️⃣ 驱动模型变化**

```txt
2.6: platform device
3.x: device tree
4.x: subsystems（DRM/NVMe）
5.x+: BPF 可扩展
6.x+: Rust 驱动
```

👉 重点：**驱动从“写死” → “描述” → “动态扩展”**

**4️⃣ 内存 & 并发**

这是你做内核工程最关键的👇

```txt
版本      核心变化
2.6       slab / zone
3.x       NUMA
4.x       THP
5.x       PSI
6.x       Maple Tree + MGLRU
```

👉 重点：  你说的“锁拆分”，正是这个主线的一部分。



# 入门单点问题


## 调度问题


### 用户态实验-恶霸进程


场景：CPU 被“恶霸进程”抢占

```cpp
// hog.c
int main() {
    while (1) {
        // busy loop
    }
}
```

```cpp
// latency.c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void delay_ms(unsigned long ms)
{
    struct timespec start, now;
    clock_gettime(CLOCK_MONOTONIC, &start);
    // 忙等 100ms，全程占用 CPU
    while (1)
    {
        clock_gettime(CLOCK_MONOTONIC, &now);
        long diff = (now.tv_sec - start.tv_sec) * 1000000000 + (now.tv_nsec - start.tv_nsec);
        if (diff >= ms * 1000000UL) // 100ms
            break;
    }
}

int main(int argc, const char *argv[])
{
    struct timespec a, b;
	int loop_count = 32;

	printf("\nusage: %s [loop_count]\n\n", argv[0]);
	if (argc == 2)
		loop_count = atoi(argv[1]);

	for (int i=0; i<loop_count; i++)
    {
        clock_gettime(CLOCK_MONOTONIC, &a);
        delay_ms(100); // 忙等，不是sleep！
        clock_gettime(CLOCK_MONOTONIC, &b);
        long ms = (b.tv_sec - a.tv_sec) * 1000 + (b.tv_nsec - a.tv_nsec) / 1000000;
        printf("[%4d/%-4d] cost: %ld ms\n", i+1, loop_count, ms);
    }
    return 0;
}
```


**▶️ 操作步骤**

```bash
if [[ "$1" = "clean" ]];then
	rm -rf hog latency
	rm -rf *.elf
elif [[ "$1" = "busybox" ]];then
	echo "build for busybox"
	gcc -static hog.c -o hog.elf
	gcc -static latency.c -O2 -lrt -o latency.elf
else
	echo "build for debian"
	gcc hog.c -o hog.elf
	gcc latency.c -O2 -lrt -o latency.elf
fi

# 多开几个
# in debian:
# for ((i=0; i<16; i++)); do ./hog.elf & done
# ./latency.elf
# After test: pkill -x hog.elf

# in busybox:
# i=0; while [ $i -lt 16 ]; do ./hog.elf & i=$((i+1)); done
# ./latency.elf
# ps | grep hog.elf | grep -v grep | awk '{print $1}' | xargs kill
```


**👀 现象**
- `latency` 输出时间会**抖动严重**
- 本该 100~101ms，可能变成 300ms+s


下面实际现象记录:

```bash
# 这是没有恶霸进程抢占cpu的延时,基本稳定在100~101ms之间
/workdir/project # ./latency.elf 16
usage: ./latency.elf [loop_count]
[   1/16  ] cost: 100 ms
[   2/16  ] cost: 100 ms
[   3/16  ] cost: 100 ms
[   4/16  ] cost: 101 ms
[   5/16  ] cost: 100 ms
[   6/16  ] cost: 100 ms
[   7/16  ] cost: 100 ms
[   8/16  ] cost: 100 ms
[   9/16  ] cost: 100 ms
[  10/16  ] cost: 100 ms
[  11/16  ] cost: 100 ms
[  12/16  ] cost: 100 ms
[  13/16  ] cost: 100 ms
[  14/16  ] cost: 101 ms
[  15/16  ] cost: 100 ms
[  16/16  ] cost: 100 ms
```


```bash
# 运行恶霸进程(多运行几个,疯狂抢占cpu调度)
i=0; while [ $i -lt 16 ]; do ./hog.elf & i=$((i+1)); done

# 观测进程: 耗时波动甚至相差20ms
./latency.elf 16
usage: ./latency.elf [loop_count]
[   1/16  ] cost: 106 ms
[   2/16  ] cost: 104 ms
[   3/16  ] cost: 100 ms
[   4/16  ] cost: 124 ms
[   5/16  ] cost: 103 ms
[   6/16  ] cost: 104 ms
[   7/16  ] cost: 117 ms
[   8/16  ] cost: 100 ms
[   9/16  ] cost: 121 ms
[  10/16  ] cost: 129 ms
[  11/16  ] cost: 117 ms
[  12/16  ] cost: 113 ms
[  13/16  ] cost: 107 ms
[  14/16  ] cost: 112 ms
[  15/16  ] cost: 105 ms
[  16/16  ] cost: 100 ms

# 实验结束, 批量结束所有恶霸进程(也可以通过 Ctrl+A+X 强行退出qemu虚拟机)
/workdir/project # ps | grep hog.elf | grep -v grep | awk '{print $1}' | xargs kill
```

你观察到：
- 100ms → 120ms 波动
- 抖动随 hog 增加而变大

👉 本质不是“计时不准”，而是：
> **调度延迟（scheduling latency）**



🔍 深入（内核态）

观察调度：

```bash
cat /proc/sched_debug

# 或者
perf sched record
perf sched latency
```


**🧠 本质**
- CFS 调度器时间片被 hog 占满
- latency 进程得不到 CPU


**✅ 进阶验证**
```bash
nice -n -20 ./latency
```

👉 延迟明显改善




## 内存问题


**🎯 实验目标**

理解：

- 缺页异常（page fault）
- 内存回收（reclaim）
- swap / OOM

---

**🧪 实验设计**

**场景：制造“内存抖动”**

```cpp
// mem.c
#include <stdlib.h>
#include <string.h>

#define SIZE (1024 * 1024 * 1024) // 1GB

int main() {
    char *p = malloc(SIZE);
    while (1) {
        for (size_t i = 0; i < SIZE; i += 4096) {
            p[i] = 1;  // 每页触发
        }
    }
}
```


---


**▶️ 操作**

```bash
./mem &
./mem &
./mem &
```

---

**👀 现象**

top

- CPU system 飙高
- 系统卡顿
- 可能触发 OOM

---

**🔍 内核观察**

```bash
vmstat 1
```

关注：
- `si/so`（swap）
- `pgfault`
- `pgmajfault`

---

**🧠 本质**
- 每 4KB 触发 page fault
- LRU 回收频繁
- 进入 direct reclaim


---

**✅ 进阶（内核态）**

```bash
cat /proc/zoneinfo
cat /proc/meminfo
```



## IO问题


**🎯 实验目标**

理解：
- 阻塞 IO
- IO 队列
- IO 延迟

---

**🧪 实验设计**
场景：磁盘被打满

```bash
dd if=/dev/zero of=test.img bs=1M count=10240
```

同时运行：
```cpp
// read_latency.c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

int main() {
    char buf[4096];
    int fd = open("test.img", O_RDONLY);

    while (1) {
        read(fd, buf, sizeof(buf));
    }
}
```

---

**👀 现象**

- read 变慢
- 系统 load 升高

---

**🔍 观察**

```bash
iostat -x 1
```

关注：
- `await`
- `svctm`
- `%util`

---

**🧠 本质**
- IO 队列排队
- block layer 调度（CFQ / mq-deadline）


---

**✅ 进阶（内核）**

```bash
cat /sys/block/sda/queue/scheduler
```

切换调度器：
```bash
echo mq-deadline > /sys/block/sda/queue/scheduler
```



## 锁问题


**🎯 实验目标**

理解：
- 锁竞争
- 自旋锁 vs 睡眠锁
- cache line 争用

---

**🧪 实验设计（用户态模拟）**

```cpp
// lock.c
#include <pthread.h>
#include <stdio.h>

pthread_mutex_t lock;
long counter = 0;

void* worker(void* arg) {
    while (1) {
        pthread_mutex_lock(&lock);
        counter++;
        pthread_mutex_unlock(&lock);
    }
}

int main() {
    pthread_t t[8];
    pthread_mutex_init(&lock, NULL);

    for (int i = 0; i < 8; i++)
        pthread_create(&t[i], NULL, worker, NULL);

    for (int i = 0; i < 8; i++)
        pthread_join(t[i], NULL);
}
```

---


**👀 现象**

```bash
top
```

- CPU 利用率高
- 但吞吐很低

---

🔍 分析

```bash
perf top
```

看到：
- `pthread_mutex_lock`
- futex


---

🧠 本质

- 锁竞争严重
- 线程在 futex 等待


---

✅ 内核态观察

```bash
perf lock record
perf lock report
```




# Bottom







