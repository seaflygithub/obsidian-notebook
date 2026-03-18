


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




# 内核问题排查

## 一、先定结论

**你的思路完全正确：主动找问题→提问拆解→动手验证→复盘沉淀，是成为内核问题定位高手最快路径，远超死读源码、死背理论**

内核架构师**核心立身本事只有一个：自上而下快速定位根因**，不是写代码，是**抓异常、追链路、定瓶颈、稳内核**。

## 二、内核架构师必备全套核心技能（按优先级）

### 1. 底层硬件基础（排障根基）

- x86_64/ARM64 寄存器、异常、中断、页表、MMU、缓存一致性、SMP 多核调度
- 总线时序、IO 拓扑、PCIe、DMA、中断路由、硬件寄存器读写
- 时钟源、TSC、HPET、本地 APIC、IOAPIC、电源管理底层逻辑

### 2. 内核核心子系统精通（问题全覆盖）

1. **进程 / 线程调度**：调度队列、CFS、实时调度、优先级、抢占、软硬中断阻塞
2. **内存管理**：SLUB/SLOB、页分配、OOM、内存泄漏、野指针、栈溢出、内存踩踏、缺页异常
3. **中断与下半部**：irq、tasklet、workqueue、中断风暴、中断耗时过长
4. **文件系统**：页缓存、块层、IO 调度、磁盘瓶颈、死锁、缓存脏页阻塞
5. **网络协议栈**：收发包流程、软中断、网卡队列、拥塞、丢包、内核协议栈卡顿
6. **驱动架构**：字符 / 块 / 网卡驱动、设备树、平台驱动、probe 流程、驱动死锁
7. **同步机制**：自旋锁、互斥锁、信号量、RCU、读写锁、**内核死锁全场景排查**
8. **调试子系统**：kprobe、ftrace、perf、tracepoint、panic/oops/BUG 栈回溯

### 3. 四大问题专属定位能力（你最需要的）

1. **功能性问题**：接口异常、流程走偏、硬件适配失败、配置解析错误、状态机错乱
2. **稳定性问题**：随机死机、oops、panic、软死锁、内存 corruption、随机崩溃、死机复现
3. **性能问题**：CPU 打满、IO 卡顿、内存飙升、调度延迟、上下文切换过高、网卡吞吐瓶颈、时延抖动
4. **疑难隐现问题**：偶现必现切换、高负载才出问题、多核竞态、时序敏感 BUG、环境依赖 BUG

### 4. 实战工具链（架构师标配）

- 源码：Linux 内核源码通读 + 定向精读
- 调试：gdb+kgdb、windbg、crash 工具、livepatch
- 性能：perf、bpftrace、systemtap、sar、vmstat、iostat、netstat
- 日志：dmesg、printk、内核动态打印、ringbuffer
- 崩溃分析：vmcore 离线分析、栈帧还原、内存镜像排查

### 5. 工程实战能力

- 内核编译、裁剪、定制、补丁移植、版本差异兼容
- 内核参数调优、系统全局瓶颈调优
- 线上内核故障应急排障、风险评估、修复方案设计
- 驱动与内核耦合问题拆解、跨版本 BUG 溯源

## 三、最优学习方法（提问解决法，标准化落地）

### 核心学习模式：**问题驱动学习法（唯一最快成型路线）**

1. **批量收集内核真实问题（问题来源）**
    
    - 内核社区 bugzilla、LKML 邮件列表
    - 大厂内核故障复盘、云服务器内核崩溃案例
    - 开源社区疑难内核报错、驱动异常、性能劣化案例
    - 嵌入式 Linux、服务器 Linux、安卓内核线上真实事故
    - 知乎、掘金、内核专题论坛、行业故障实录
    
2. **拿到问题先 3 步自问（主动思考，不直接看答案）**
    
    - 现象是什么？（死机 / 卡顿 / 丢包 / OOM / 死锁 / 崩溃）
    - 大概率落在哪个内核子系统？
    - 我能用什么工具先初步定位嫌疑点？
    
3. **主动拆解 + 假设验证（最关键）**
    
    建立**怀疑链**：现象 → 推测原因 → 设计验证方法 → 上机复现 / 抓日志 / 看栈帧 → 证实 / 推翻 → 锁定根因
    
    全程**自己先推导，卡住再查资料、提问求证**，严禁直接看答案。
    
4. **动手复现 + 动手调试**
    
    能本地复现就搭环境复现，不能复现就**离线分析崩溃日志、vmcore、oops 栈**，模拟现场排障。
    
5. **分类归纳沉淀**
    
    把问题按：内存类、调度类、中断类、IO 类、网络类、驱动类、死锁类、性能类归档，形成**自己的内核故障排查手册**。



## 五、分阶段执行路线（极简落地）

### 阶段 1：打底（1-2 个月）

吃透内核四大基石：内存、调度、中断、锁机制，看懂基础 oops 栈信息，会用 crash/perf 基础命令。

### 阶段 2：专项破局（2-3 个月）

专攻四类问题：

- 稳定性：panic、死锁、内存泄漏、野指针排查
- 性能：CPU/IO/ 内存 / 网络内核瓶颈定位
- 功能：驱动适配、内核接口异常、子系统流程异常
- 偶现问题：时序竞态、多核 BUG、高负载隐性故障

### 阶段 3：实战拔高（长期）

跟进线上真实内核事故、参与内核社区问题讨论、独立完成内核故障根因分析 + 修复思路，具备**独立主导内核架构优化与故障治理**能力。

## 六、核心心法（架构师排障思维）

1. **先分域，再深挖**：先锁定子系统，再往下追调用栈，不盲目乱查
2. **先现象，再日志，最后源码**：日志栈帧 > 现场数据 > 源码逻辑
3. **优先怀疑并发、时序、资源竞争**：90% 内核疑难 BUG 全是竞态与资源争抢
4. **性能问题优先抓瓶颈链路**：定位热点函数、阻塞点、等待队列、IO 阻塞

## 最终总结

**你的学习思路完全正确：以全网真实内核问题为题库，主动思考假设→动手验证→卡点提问求证→复盘固化，是从内核学习者蜕变为内核问题定位专家、最终达到内核架构师水平的唯一高效路径。**




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



# 练手案例清单


性能瓶颈90%就是: 锁竞争、等待队列阻塞、IO阻塞、调度饥饿、内存缺页

偶现崩、死锁、数据错乱: 10个里9个是竞态导致

这类BUG典型特征：
- 偶现、压力越大越容易出
- 加日志、加打印、加sleep、加调试核就消失（Heisenbug）
- 不同机器、不同内核版本表现不一样
- 抓不到必现栈，只能靠日志、core、perf、ftrace 回溯时序



**时序问题**: 太早or太晚，比如 硬件还没上电就绪，软件直接发指令；比如 多核下**一个核改数据，另一个核读数据时机错位**，读到脏数据。


竞态条件、时序问题(太早or太晚)、锁顺序死锁、抢占调度时机、中断上下文冲突、资源多路径路径争抢；

内存越界、野指针、use-after-free、栈溢出；

硬件兼容性、寄存器时序、DMA时序、中断异常

逻辑设计错误（比如状态机写错）



---



<font color=blue>帮我搜索罗列出网络上现有的内核相关的疑难杂症以及其解决方案，包括开源社区以及社区邮件的。我要用这些实际案例从简单到专家级排序后，进行故意制造复现这类问题，并尝试解决这类问题，简单阶段，主要熟悉各种架构师常用排查问题的工具和环境。
</font>


下面我直接给你一份**可直接拿来练手的「内核疑难杂症清单」**，覆盖 **LKML / 社区邮件、Bugzilla、GitHub Issues、厂商案例**，并按**简单→中级→专家级**排序，每个都写：现象、根因、复现方法、排查工具、解决方案。你可以按这个顺序**故意制造问题→排查→解决**，把工具链练熟。

## 0. 整体分级说明（你要的训练路线）

- **Lv1 入门（简单）**：Oops、空指针、小内存泄漏、简单死锁、驱动初始化时序错。目标：**熟练工具（dmesg、crash、perf、ftrace、KASAN）**。
- **Lv2 中级**：软死锁、Slab 泄漏、RCUstall、中断风暴、调度延迟、网络丢包 / 软中断瓶颈。目标：**看懂调用栈、定位子系统、会写简单 kprobe**。
- **Lv3 专家级**：Use-after-free、内存踩踏、多核竞态、缓存一致性问题、时序偶现崩溃、IRQ/SoftIRQ 嵌套死锁、内核栈溢出、cgroup/oom 死锁。目标：**能复现偶现问题、读懂汇编、会改内核补丁**。


---


## Lv1 入门级（先把工具用熟）

### 1）空指针解引用（最经典 Oops）

- 现象：`BUG: kernel NULL pointer dereference`，Oops + 调用栈，直接崩溃。
- 根因：函数里用了未初始化 / 为 NULL 的指针，直接解引用。
- 复现：写个内核模块：

```cpp
int *p=NULL; 
*p=1; // 触发Oops
```

- 排查工具：**dmesg、objdump、gdb+kgdb、KASAN**。
- 解决：判空后再用。


### 2）简单内存泄漏（kmalloc 不 free）

- 现象：`meminfo`中 Slab/Used 持续涨，不释放，久了 OOM。
- 根因：`kmalloc/kzalloc`后没`kfree`；模块卸载没清理。
- 复现：模块里循环`kmalloc(1024, GFP_KERNEL)`，不释放。
- 排查工具：**slabtop、cat /proc/slabinfo、valgrind（用户态）、KASAN**。
- 解决：匹配`kfree`；退出 / 卸载时释放。


### 3）自旋锁死锁（最简单锁问题）

- 现象：`BUG: soft lockup - CPU#X stuck for XXs`，CPU100%，系统卡死。
- 根因：同一 CPU 重复拿自旋锁；或自旋锁嵌套。
- 复现：

```cpp
spin_lock(&lock); 
spin_lock(&lock); // 二次拿锁，死锁
```

- 排查工具：**dmesg（soft lockup）、watchdog、ftrace、perf lock**。
- 解决：保证同一锁不重复拿；自旋锁不可嵌套。


### 4）驱动初始化时序错误（A 没做完就做 B）

- 现象：模块加载报错`-ENODEV`、`-EIO`；设备寄存器读写失败。
- 根因：**时序**：先写寄存器→再初始化时钟 / 复位；或中断没关就操作。
- 复现：模拟驱动：先访问设备寄存器，再使能时钟。
- 排查工具：**dmesg、printk、ftrace、逻辑分析仪（硬件）**。
- 解决：严格按芯片手册：**上电→复位→时钟→初始化→操作**。


---

## Lv2 中级（子系统级，要懂流程）

### 5）Slab 内存泄漏（内核态隐藏泄漏，top 看不到）

- 现象：`free -h`看 used 很高，但`top`无进程异常；`cat /proc/meminfo`中**Slab 持续涨**，`SReclaimable`不释放。
- 根因：内核对象（inode、dentry、socket、task_struct）没释放；驱动 / 模块频繁创建不销毁。
- 典型案例：SGX 驱动`sgx_encl_mm_release_deferred`引用计数不递减，EPC 内存泄漏。
- 复现：写模块频繁创建`struct file`或`socket`，不关闭 / 释放。
- 排查工具：**slabtop、cat /proc/slabinfo、kmemleak、ftrace**。
- 解决：补全`put`/`free`；修复引用计数。

### 6）RCU Stall（RCU 读侧卡住，系统变慢）

- 现象：`dmesg`报`RCU: INFO: Stall detected on CPU X`；系统响应慢、卡顿。
- 根因：RCU 读临界区太长（循环 / 大计算）；或写侧`rcu_synchronize`阻塞。
- 复现：RCU 保护下写大循环（1e8 次）。
- 排查工具：**dmesg、perf、ftrace（rcu:*）、rcutorture**。
- 解决：读侧拆分；用`cond_resched()`；写侧优化。

### 7）中断风暴（IRQ 暴增，CPU 打满）

- 现象：`top`中`%sys`接近 100%；`cat /proc/interrupts`某 IRQ 计数疯涨。
- 根因：设备反复触发中断（网卡 / 磁盘 / 驱动 bug）；中断标志没清。
- 复现：模拟驱动中断服务程序（ISR）不清中断标志，导致反复进 ISR。
- 排查工具：`cat /proc/interrupts、perf top -e irq:*、ftrace（irq_handler）`。
- 解决：ISR 里正确清中断标志；加限流 / 阈值。

### 8）调度延迟大（实时任务抖动，`cyclictest`差）

- 现象：实时应用（工控 / 音视频）卡顿；`cyclictest`抖动 > 10ms。
- 根因：软中断（`ksoftirqd`）抢占；CFS 调度不公平；`HZ`太低；没开`PREEMPT`。
- 复现：高负载下（`dd`+`ping -f`）跑`cyclictest`。
- 排查工具：**cyclictest、perf sched、ftrace（sched:*）、trace-cmd**。
- 解决：开`PREEMPT`；`isolcpus`隔离；`rt_mutex`；调整`HZ=1000`。

### 9）网络软中断瓶颈（网卡收包 CPU100%，吞吐上不去）

- 现象：`top`中`ksoftirqd`占满；`sar -n DEV`网卡吞吐低；丢包。
- 根因：网卡队列太少；软中断绑定到单个 CPU；`napi`没聚合。
- 复现：单队列网卡，高并发`ping -f`或`iperf`。
- 排查工具：**perf top -e softirq、ss -s、netstat -s、ftrace（napi:*）**。
- 解决：多队列 RSS；调整`net.core.netdev_budget`；`napi`聚合。


---

## Lv3 专家级（偶现、时序、多核、内存踩踏）

### 10）Use-after-free（释放后再用，最危险偶现崩溃）

- 现象：随机 Oops/panic；`KASAN`报`BUG: KASAN: use-after-free`；栈回溯指向已释放内存。
- 根因：`kfree`后没置 NULL，后续分支又访问；竞态：A 释放、B 还在用。
- 典型案例：ECS 实例`cdev_put`后再访问，触发`use-after-free`崩溃。
- 复现：

```cpp
char *p=kmalloc(1024, GFP_KERNEL);
kfree(p);
// 时序/分支导致再次访问
if (x) *p=1;
```

- 排查工具：**KASAN（必开）、crash、gdb、objdump、kprobe**。
- 解决：释放后置 NULL；加锁 / RCU 保护生命周期。


### 11）内存踩踏（野指针 / 越界写，随机数据错乱 / 崩溃）

- 现象：随机 panic、数据 corruption、文件系统报错；无固定栈。
- 根因：数组越界、野指针、栈溢出、驱动 DMA 写越界。
- 复现：模块里`char buf[10]; buf[10]=1;`（越界）。
- 排查工具：**KASAN、KMSAN、crash、vmcore、objdump**。
- 解决：边界检查；用`kmemdup`；DMA 做地址校验。

### 12）多核竞态（SMP 下时序，偶现死锁 / 数据错）

- 现象：高负载 / 多核下偶现崩溃、死锁、数据不一致；单 CPU 正常。
- 根因：**时序 + 并行**：CPU0 写、CPU1 读，无锁 / 无内存屏障，读到中间态。
- 复现：多核模块：

```cpp
int x=0;
// CPU0
x=1;
// CPU1
if (x==1) ... // 无屏障，可能读到0
```

- 排查工具：**ftrace、perf lock、kprobe、memory barrier、lockdep**。
- 解决：加锁 / RCU；`smp_wmb()`/`smp_rmb()`；`lockdep`检查。


### 13）内核栈溢出（深递归 / 大栈帧，直接 panic）

- 现象：`BUG: stack overflow`；panic 在深递归函数；栈回溯很长。
- 根因：递归过深；函数内大数组（>1KB）；中断嵌套深。
- 复现：模块递归调用 1000 次；栈内`char buf[4096]`。
- 排查工具：**dmesg、objdump（看栈帧）、KASAN、crash**。
- 解决：改迭代；大数组改`kmalloc`；减少递归深度。

### 14）Cgroup/oom 死锁（OOM 时 cgroup 递归锁，系统卡死）

- 现象：频繁 OOM 后 panic；栈回溯`cgroup_is_descendant`；系统无响应。
- 根因：OOM 流程与 cgroup 嵌套锁竞争，形成死锁。
- 典型案例：RHEL7 频繁 OOM 后`cgroup_is_descendant+0x1d` panic。
- 复现：`dd`吃满内存触发 OOM，同时 cgroup 嵌套。
- 排查工具：**crash、vmcore、dmesg、ftrace（cgroup:_、oom:_）**。
- 解决：内核补丁；调整`oom_score_adj`；避免 cgroup 嵌套过深。


## 附：你训练用的「工具链清单」（Lv1 必须练熟）

- 日志 / 基础：**dmesg、printk、/proc/interrupts、/proc/meminfo、slabtop**
- 崩溃分析：**crash、vmcore、objdump、gdb+kgdb**
- 性能：**perf（top/sched/lock）、ftrace、trace-cmd、cyclictest**
- 内存错误：**KASAN、KMSAN、kmemleak**
- 锁 / 竞态：**lockdep、smp_barrier、kprobe**




# 练手案例实验设计



## LV1-空指针解引用



<font color=blue>帮我写个内核模块和Makefile，用来复现 空指针解引用（最经典 Oops）问题，并教我怎么用 dmesg、objdump、gdb+kgdb、KASAN 来排查问题所在。
</font>


```cpp
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

static int __init null_bug_init(void)
{
    int *bad_ptr = NULL;

    // 强制空指针写，触发内核Oops
    *bad_ptr = 0x1234;
    pr_info("call %s\n", __func__);
    return 0;
}

static void __exit null_bug_exit(void)
{
    pr_info("call %s\n", __func__);
}

module_init(null_bug_init);
module_exit(null_bug_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Test NULL Pointer Dereference Oops");
MODULE_AUTHOR("Train Kernel Debug");
```


```makefile
obj-m += null_ptr_bug.o
KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```


---


**二、编译 + 加载复现问题**

```bash
# 编译
make

# 加载模块 立刻触发Oops
sudo insmod null_ptr_bug.ko

# 查看内核报错日志
dmesg -T
```


报错特征

```log
BUG: kernel NULL pointer dereference, address: 0000000000000000
#PF: error_code(0x0002) - write access
RIP: 0010:null_bug_init+0xXX/0xXX
Call Trace:
 ...
```


---



**三、四种工具逐级排查（从简单到专业）**

**方式 1：dmesg 快速定位（入门必用）**

1. `dmesg -T` 找到报错行
2. 抓取关键信息：
```txt
- address: 0000000000000000 → 明确**空指针访问**
- RIP: 0010:null_bug_init+0x17/0xff0 [drv_myptr] → 出错函数 + 函数内偏移地址 [模块名称]
- error_code 0x0002 = **写空指针**，0x0001 是读空指针
```

结论：直接确定 **在`null_bug_init`函数内发生空指针写操作**。

**方式 2：objdump 反汇编定位精确代码行**

```bash
# 反汇编内核模块
objdump -S null_ptr_bug.o > disasm.txt
```

- 打开`disasm.txt`找到 `null_bug_init`
- 对照 dmesg 里的**函数内偏移**，直接对应汇编指令
- 一眼看到：`mov $0x1234,(%rax)` 就是向 NULL 地址赋值
    精准锁定**出错源码行**。


**方式 3：开启 KASAN 最强内存错误检测（最推荐）**

1）确认内核是否开启 KASAN

```bash
# 确认内核是否开启 KASAN
zcat /proc/config.gz | grep KASAN


# 内核配置
CONFIG_KASAN=y
CONFIG_KASAN_GENERIC=y

# 重新编译带 KASAN 内核后加载模块
```

再次`insmod`，**KASAN 会打印超级详细日志**：
- 明确指出：`NULL pointer dereference`
- 完整调用栈、内存类型、读写类型、上下文
- 直接标注源码文件 + 行号，无需手动猜

**实战内核排错首选 KASAN，90% 内存问题直接秒定位**

---

<font color=blue>现实生产环境中，无效指针引用或者野指针引用的问题，用kasan多吗？毕竟有些内存问题并不是马上能暴露出来，可能在生产环境中运行几天后突然发生了，毕竟使用了kasan，性能问题可能会大打折扣
</font>

**在生产环境几乎不用，在开发/测试环境是必备神器。**
针对你提到的“运行几天才暴露”和“性能损耗”这两个关键问题，下面是业界的真实做法：

你担心的“内存污染后延迟崩溃”是典型的内存安全问题。KASAN 的理念不是一直开着等它崩，而是**主动复现**。生产环境定位这类问题通常遵循下面这个流程：

**阶段一：生产环境（只收集线索，不开 KASAN）**
- **开启 `CONFIG_DEBUG_PAGEALLOC`**：性能损耗 10%-20%，比 KASAN 轻量，能捕获 UAF（Use After Free）。
- **开启 `CONFIG_SLUB_DEBUG`**：几乎无性能损耗，在 `sysfs` 中记录分配/释放的调用栈。
- **利用 `pstore`**：崩溃时自动保存 `dmesg`，即使没 KASAN，`RIP` + `Call Trace` 也能提供线索。

**阶段二：开发/测试环境（开启 KASAN 复现）**
- 拿到生产环境的崩溃日志后，确定操作序列（比如：执行某个 ioctl 后 sleep 3 秒再写入）。
- 在测试服务器上，**加载开启 KASAN 的内核**，运行相同的操作。
- 通常 **几秒或几分钟** 内，KASAN 就会精准报告：

```txt
BUG: KASAN: use-after-free in my_driver_write+0x123/0x200
Read of size 4 at addr ffff88807a5a4000 by task app/1234
Freed by task 1233:
    kfree+0xabc/0xb00
    my_driver_release+0x45/0x80
Previously allocated by task 1232:
    kmalloc+0x123/0x300
    my_driver_open+0x67/0x90
```

这直接告诉你：在第 123 行释放后，又在第 456 行被访问。


对于必须**长期运行但内存问题频发**的场景，业界有两个替代品：

| 工具                                       | 性能损耗        | 检测能力                                         | 适用场景      |
| ---------------------------------------- | ----------- | -------------------------------------------- | --------- |
| **KASAN**                                | 2-3 倍       | **最全面** (OOB, UAF, 野指针)                      | 开发/测试环境   |
| **KFENCE** (Kernel Electric Fence)内核电子围栏 | **1% - 5%** | 只能测 UAF 和 OOB（采样模式）。一旦捕获到错误，日志精度和 KASAN 一样高。 | **生产环境！** |
| **Kmemleak**                             | 忽略不计        | 只测内存泄漏                                       | 长期运行的后台任务 |


**Electric Fence**：电子围栏（一种安全防护系统，用于检测越界访问）
```txt
这个名字借鉴了一个经典的用户态内存调试工具 **Electric Fence**（libefence），它的工作原理是：
- 在分配的内存块前后放置"不可访问"的保护页（如同电子围栏）
- 当程序越界访问时，立即触发段错误，精准定位问题
**KFENCE** 把同样的思想移植到了内核态，因此得名"内核电子围栏"。

KFENCE 就是给内核内存分配套上了一层"电子围栏"，专门用来抓：
- **Use-After-Free**（释放后使用）
- **Out-of-Bounds**（越界访问）
- **Invalid-free**（无效释放）
```


---


**生产环境遇到内存问题的真实调试手段**

实际靠的是下面这些**低开销、可在线开启**的工具：

| 工具                     | 性能开销     | 可在线开启     | 定位能力          | 生产环境可用性    |
| ---------------------- | -------- | --------- | ------------- | ---------- |
| **KFENCE**             | 1-5%     | ✅ 是（动态采样） | UAF/OOB 精确到行号 | ✅ **强烈推荐** |
| **Lockdep**            | 5-10%    | ✅ 是       | 锁竞争/死锁        | ✅ 常用       |
| **pstore + panic log** | 0%       | ✅ 自动      | 崩溃时的调用栈       | ✅ **自动收集** |

**3.1 实战流程（你刚才遇到的 NULL 指针问题）**

```bash
# 生产环境：系统 panic 后自动保存日志
# 1. 配置 pstore
mount -t pstore pstore /sys/fs/pstore
echo 1 > /sys/module/kernel/parameters/panic_on_oops
echo 1 > /proc/sys/kernel/panic

# 2. 崩溃后，在 /sys/fs/pstore/ 下找到日志
ls /sys/fs/pstore/
# console-ramoops-0  包含完整的 oops 信息（RIP、Call Trace）

# 3. 即使有 KASLR，RIP 是相对偏移，仍可定位
# 你的日志：RIP: 0010:init_module+0x17/0xff0
# 配合 objdump（即使模块无符号），也能找到具体指令
```


**3.2 没有 KGDB，如何分析"运行几天才崩溃"？**

**方案：KFENCE 采样 + 持续监控**

KFENCE 的工作原理是在内核态捕获缺页异常（page fault）。当你的程序触发空指针或越界访问时，CPU 会陷入内核，KFENCE 的异常处理函数 `kfence_handle_page_fault` 会被调用[](https://git.uk.ideasonboard.com/epaul/linux/src/commit/8f6f76a6a29f36d2f3e4510d0bde5046672f6924/include/linux/kfence.h)。在这个函数里，KFENCE 会将格式化的错误报告直接写入内核缓冲区，最终通过 `printk` 输出，所以你需要在 `dmesg` 里查看。

```bash
# 生产环境开启 KFENCE（动态采样，无需重启）
echo 100 > /sys/module/kfence/parameters/sample_interval  # 每 100ms 采样一次

# KFENCE 捕获到错误后，自动记录到内核日志
# 日志会精确指出：哪个函数的第几行释放了内存，哪个函数的第几行再次访问
```



```txt
# 启用 KFENCE 主选项
set_config -e CONFIG_KFENCE
# 设置采样间隔为 100ms
set_config --set-val CONFIG_KFENCE_SAMPLE_INTERVAL 100
# 设置保护对象数量为 255
set_config --set-val CONFIG_KFENCE_NUM_OBJECTS 255
```


安装空指针访问模块，触发内核panic

KFENCE 主要用于检测对**已释放内存（UAF）** 或**缓冲区边界**的非法访问。**KFENCE 擅长的事**：它擅长于检测像 `p = kmalloc(size); kfree(p); ... p->data = x;` 这种（UAF）错误，或者 `p = kmalloc(16); p[16] = 0` 这种“踩着边界线”的越界访问。这些都是常规手段难以发现的内存破坏。

---



```cpp
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>

void myfunc1(void)
{
    // 强制空指针写，触发内核Oops
    //int *bad_ptr = NULL;
    //*bad_ptr = 0x1234;
	unsigned char *ptr_uaf = kmalloc(32, GFP_KERNEL);
	kfree(ptr_uaf);
	ptr_uaf[0] = 128;
}

static int __init null_bug_init(void)
{
	myfunc1();
    pr_info("call %s\n", __func__);
    return 0;
}

static void __exit null_bug_exit(void)
{
    pr_info("call %s\n", __func__);
}

module_init(null_bug_init);
module_exit(null_bug_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Test NULL Pointer Dereference Oops");
MODULE_AUTHOR("Train Kernel Debug");
```


```bash
echo 1 > /sys/module/kfence/parameters/sample_interval
```


实验总结: kfence 主要用于监测UAF，就是那种动态内存分配释放后，仍然访问的bug，或者越界bug，但是访问粒度必须是sizeof(size_t) 这样的粒度，并且 kfence 采样间隔即使设置到最小的1毫秒，也不一定能精确捕获UAF行为，这是我在实验中验证得到的结果。

```bash
root@amd64:/workdir/project/kernel_module# echo 1 > /sys//module/kfence/parameters/sample_interval 
root@amd64:/workdir/project/kernel_module# cat /sys/module/kfence/parameters/sample_interval 
1
root@amd64:/workdir/project/kernel_module# 
root@amd64:/workdir/project/kernel_module# insmod drv_myptr.ko 
[   74.177481] drv_myptr: loading out-of-tree module taints kernel.  这是没有捕获到的情况
[   74.194530] call null_bug_init
root@amd64:/workdir/project/kernel_module# 


# 下面是我反复多试几次才触发的kfence捕获
root@amd64:/workdir/project/kernel_module# insmod drv_myptr.ko ; rmmod drv_myptr
root@amd64:/workdir/project/kernel_module# insmod drv_myptr.ko ; rmmod drv_myptr
root@amd64:/workdir/project/kernel_module# insmod drv_myptr.ko ; rmmod drv_myptr
[  464.736627] ==================================================================
[  464.736627] BUG: KFENCE: use-after-free write in myfunc1+0x2b/0x50 [drv_myptr]
[  464.736627] 
[  464.736627] Use-after-free write at 0x000000001f1c18f3 (in kfence-#3):
[  464.736627]  myfunc1+0x2b/0x50 [drv_myptr]
[  464.736627]  null_bug_init+0xe/0xff0 [drv_myptr]
[  464.736627]  do_one_initcall+0x5f/0x280
[  464.736627]  do_init_module+0x64/0x230
[  464.736627]  load_module+0x1bfb/0x1e60
[  464.736627]  init_module_from_file+0x8b/0xd0
[  464.736627]  idempotent_init_module+0x189/0x290
[  464.736627]  __x64_sys_finit_module+0x59/0x90
[  464.736627]  do_syscall_64+0x37/0x90
[  464.736627]  entry_SYSCALL_64_after_hwframe+0x78/0xe2

# 从上述 kfence 信息得知:
BUG: KFENCE: use-after-free write in myfunc1+0x2b/0x50 [drv_myptr]
```


```bash
# 反汇编驱动模块
objdump -D -S drv_myptr.ko > drv_myptr.dump.S

0000000000000010 <myfunc1>:
  10:   f3 0f 1e fa             endbr64 
  14:   e8 00 00 00 00          callq  19 <myfunc1+0x9>
  19:   53                      push   %rbx
  1a:   ba 20 00 00 00          mov    $0x20,%edx
  1f:   be c0 0c 00 00          mov    $0xcc0,%esi
  24:   48 8b 3d 00 00 00 00    mov    0x0(%rip),%rdi        # 2b <myfunc1+0x1b>
  2b:   e8 00 00 00 00          callq  30 <myfunc1+0x20>
  30:   48 89 c3                mov    %rax,%rbx
  33:   48 89 c7                mov    %rax,%rdi
  36:   e8 00 00 00 00          callq  3b <myfunc1+0x2b>
  3b:   48 c7 03 00 00 00 00    movq   $0x0,(%rbx)         # 也就是这个位置触发的kfence惊觉
  42:   48 c7 43 08 00 00 00    movq   $0x0,0x8(%rbx)
  49:   00  
  4a:   48 c7 43 10 00 00 00    movq   $0x0,0x10(%rbx)
  51:   00  
  52:   48 c7 43 18 00 00 00    movq   $0x0,0x18(%rbx)
  59:   00  
  5a:   5b                      pop    %rbx
  5b:   e9 00 00 00 00          jmpq   60 <__UNIQUE_ID_license180+0x17>

```


我理解了，凡是越高频的操作，对其单次操作的改造或者干预，都会影响其整体性能。**完全正确。** 你精准地抓住了计算机体系结构和性能优化的核心原则。这个原则可以称之为 **“高频路径的敏感性”** (The Sensitivity of Hot Paths)。

你一旦理解了“高频操作极度敏感”这个原则，就能明白很多系统设计背后的道理：

| 操作频率            | 典型例子         | 允许的干预  | 代表工具/技术              |
| --------------- | ------------ | ------ | -------------------- |
| **极高** (纳秒级)    | 内存读写、整数运算    | 几乎为零   | 硬件 MTE (CPU 流水线并行处理) |
| **高** (十纳秒级)    | 分支预测、函数调用    | 极少量指令  | KFENCE (完全不干预内存访问)   |
| **中** (百纳秒/微秒级) | 系统调用、上下文切换   | 少量函数调用 | eBPF (在内核入口做过滤)      |
| **低** (毫秒级)     | 磁盘 I/O、网络包处理 | 复杂的逻辑  | 加密、压缩、校验和            |


<font color=blue>现实互联网大厂中，linux 内核or驱动因为内存越界或者UAF的情况多吗？他们主要在生产环境定位问题还是调试环境定位问题？如何定位的？主要用哪些手段和工具定位？
</font>

大厂会投入大量计算资源搭建测试集群，将开启KASAN的内核部署到测试集群，一旦发生越界或UAF，KASAN会立刻打印调用栈，指出哪行代码、访问了哪个已释放的内存地址。虽然这会让性能大幅下降，但为了在发布前消灭高危Bug，这是值得的。对于KASAN难以覆盖的场景（如多子系统间的内存踩踏），还会利用硬件特性（如**Firewall**）或内核编译选项（**SLUB_DEBUG**）进行辅助检测。

生产环境不能牺牲性能，但也不能完全没有“岗哨”。这就是 **KFENCE** 的价值所在。在生产内核中开启KFENCE（默认采样率很低，如每隔100ms采样一次）。KFENCE像哨兵一样，虽然不一定能抓到每一个Bug，但只要它捕获到一次UAF或越界，就会触发告警并记录现场。这种**极低开销**的特性让它在大规模服务器集群中得以应用。

危机处理：死后验尸，现场分析。当上述手段都没拦住，系统已经在线上崩溃（Kernel Panic）了，最后一道防线是 **Crash工具 + vmcore**。配置 **kdump** 机制，当内核崩溃时，自动将内存转储为 `vmcore` 文件。运维人员拿到 `vmcore` 后，配合 `vmlinux` 调试文件，使用 **Crash** 工具像侦探一样分析。查看崩溃时的调用栈（bt命令），查看寄存器和内存数据（rd、list命令），log命令能输出崩溃前内核环形缓冲区中的所有日志，包括之前的警告（WARN）、Oops 信息，帮助你还原问题发生前几秒的“时间线”。

**Crash工具 + vmcore 的组合，完全可以精准定位到问题的原因，但需要满足一个前提——你有足够的内核调试经验和上下文分析能力。** 如果把 KASAN 比作“现场直播”（直接在测试环境告诉你哪行代码出错了），那 Crash + vmcore 就是“事后最精细的刑侦分析”。它虽然没有 KASAN 那么“傻瓜式”的直观报错，但它能还原出崩溃那一瞬间系统的完整、静态、可交互的“犯罪现场”。简单来说，只要 vmcore 抓到了现场，你就能像分析一个暂停的程序一样，反推它在 crash 前都经历了什么。

---

【crash+vmcore】如何用它一步步定位“内存越界”和“UAF”？
我们按照大厂工程师的实际操作路径，来看看具体怎么分析这两种典型问题。

**第一步：启动 Crash，检查“第一现场”**

首先，你需要用带有调试符号的内核镜像（vmlinux）和 vmcore 文件启动 crash：
等进入 crash 提示符后，分析开始。

```bash
crash /usr/lib/debug/lib/modules/$(uname -r)/vmlinux /var/crash/.../vmcore
[citation:1][citation:6]
```


**第二步：定位“越界”问题**

1、查看 Panic 栈: 输入 bt -a 命令（显示所有CPU调用栈）。通常，触发 Panic 的那个CPU的栈顶就是案发现场。

log命令（内核日志）里通常会直接告诉你原因，比如 `BUG: unable to handle kernel paging request at 0000000000019600`[](https://juejin.cn/post/7117828450328510501)。看到 `paging request` 这种提示，基本就是访问了非法地址。

2、反汇编分析: 关键一步，对栈顶的指令指针（RIP）进行反汇编。你会看到导致崩溃的那条指令（比如 `mov` 指令），以及它试图访问的内存地址。

```bash
crash> dis -l ffffffff810fdfa0   # 用 bt 里看到的 RIP 地址
```

分析这条指令，通常就能发现它正在解引用一个**野指针**或已经被破坏的结构体成员。

3、**追溯源头**：知道了是哪个变量地址非法，就可以往上查看栈帧（`bt -f`），看看这个非法值是从哪个上层函数传下来的，或者是在哪个函数里被错误赋值的。


**第三步：定位“UAF”问题**

UAF 的定位更复杂一些，因为崩溃往往发生在一个看似正常的指针访问时，而其指向的内存早已被释放并可能被重新分配给了其他用途。

1、**检查内存状态**：使用 `kmem` 命令检查出错的内存地址。

```bash
crash> kmem -s <address>   # 查看这块内存所属的 slab 信息
```

如果这块内存已经被释放，你会发现其 slab 上的对象状态异常，比如毒化模式被破坏，或者 `invalid freepointer`。


2、**追踪生命周期**：这是最考验经验的一步。你需要：
- 通过 `struct` 命令查看该内存块作为某种结构体（如 `struct file`, `struct vm_area_struct`）时的成员值。
- 通过 `log` 日志，寻找此前该内存被释放的蛛丝马迹。

不过， Crash + vmcore 阶段的定位效果高度依赖工程师的经验。一个新手可能只能看到“访问了非法地址”，而一个资深的内核工程师能通过反汇编、分析栈帧、检查关键结构体，一步步逆推出导致指针失效的那次“释放”操作发生的场景，从而彻底解决 UAF 问题。


<font color=blue>帮我写一个驱动模块，专门用来导致内核崩溃并转储 vmcore ，并且设置系统能够转储vmcore。相当于指导我搭建一个 crash + vmcore 的调试环境，并刻意制造一个崩溃的场景，然后带着我一步一步定位问题。
</font>









# Bottom







