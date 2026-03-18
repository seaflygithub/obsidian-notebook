


# 🟡 Level 2：机制级问题（开始有“内核味”）

特点：

- 需要理解内核机制
- 工具不能直接给答案

---

## 5️⃣ 中断 / SoftIRQ（非常关键）

### 本质：

> CPU 时间被“偷走”

---

### 实验1：软中断风暴

ping -f 127.0.0.1

或：

iperf3 -u

---

### 观察：

- `/proc/softirqs`
- `top` 看 ksoftirqd
- `perf top`

---

### 现象：

- CPU 高，但用户态不高
- 系统卡顿

---

### 提升：

👉 理解：

- softirq
- ksoftirqd
- NAPI

---

## 6️⃣ 网络栈问题

### 实验：高并发 socket

wrk / ab 压测

---

### 观察：

- `ss -s`
- `netstat -s`
- `sar -n DEV`

---

### 进阶：

- backlog 队列满
- 丢包

---

## 7️⃣ 定时器 / 时钟问题

### 实验：

- 大量 timerfd / sleep

---

### 现象：

- 延迟抖动
- 定时不准













