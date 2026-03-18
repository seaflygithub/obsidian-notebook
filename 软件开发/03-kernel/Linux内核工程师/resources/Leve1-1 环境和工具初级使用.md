

# 第一阶段（0~1个月）：打基础 + 环境搭建

目标：建立“可观测系统”

### 1️⃣ 环境（你现在就可以做）

- 主力用 **QEMU + Linux（建议 Ubuntu + 自编译内核）**
- 打开内核选项：
    - `CONFIG_FTRACE`
    - `CONFIG_BPF`
    - `CONFIG_KPROBES`
    - `CONFIG_KALLSYMS`
    - `CONFIG_DEBUG_INFO`

👉 不要用发行版默认内核（太黑盒）

---

### 2️⃣ 必须掌握的工具（基础操作级）

每天练：
- `perf top`
- `perf record`
- `trace-cmd`
- `ftrace function_graph`
- `bpftool`

---

## 🔵 **单点问题（线性因果）**

特点：
- 单一瓶颈
- 易复现
- 工具直接定位


---

## 1️⃣ 调度问题

实验1：CPU 100% 写个死循环程序
👉 用 `perf` 找热点函数
工具: top、perf top

提升点：
- run queue
- context switch


---

实验：
- 创建 1000 个线程竞争 CPU
观察：
- load average
- run queue
- context switch
工具：
- `perf sched`
- `ftrace:sched_switch`

👉 目标：  
理解 CFS 行为

---







## 2️⃣ 内存问题


写 malloc 不 free

👉 用：
- `/proc/meminfo`
- `slabtop`

工具: vmstat、slabtop

---

实验：
- 制造：
    - 内存泄漏
    - page cache 占满
    - OOM
工具：
- `vmstat`
- `sar`
- `perf mem`
- `cgroup`

👉 重点理解：
- reclaim
- LRU
- OOM killer



## 3️⃣ IO问题

1. 实验：随机 IO vs 顺序 IO
1. 实验：多线程写盘
2. 工具：blktrace、iostat、fio
3. 重点理解：request queue、IO scheduler


实验3：IO 卡顿

实验：fio 随机写

用 `dd` 或 `fio`

👉 用：

- `iostat`
- `blktrace`





## 4️⃣ 锁问题

### 实验：mutex 死锁

1. 自己写程序制造死锁（这是面试高频）
2. 工具：perf lock、lockdep、ftrace












