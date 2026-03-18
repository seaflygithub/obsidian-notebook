



# 🔴 Level 4：架构级问题（高级）

特点：

- 难复现
- 需要模型思维

---

## 1️⃣ NUMA 问题

### 实验：

numactl --cpunodebind=0 --membind=1

---

### 现象：

- 延迟增加
- 带宽下降

---

👉 本质：

> 远程内存访问

---

---

## 2️⃣ Cache / false sharing

### 实验：

- 多线程写同一 cache line

---

### 现象：

- CPU 高
- 但性能低

---

👉 本质：

> cache line bouncing

---

---

## 3️⃣ RCU 问题（高级）

### 实验：

- 制造长时间不 quiescent state

---

### 现象：

- `rcu_sched detected stalls`












