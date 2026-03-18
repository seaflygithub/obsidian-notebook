

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
https://www.kernel.org/pub/linux/kernel/v6.x/linux-6.6.134.tar.xz


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

## 根文件系统

👉 **主力：BusyBox（静态版）**  内核开发/调试，越简单越好
👉 **进阶：Debian rootfs（bookworm）** 系统行为分析，越真实越好

👉 BusyBox 1.36.x（2026 仍然主流稳定）
👉 Debian 12（bookworm）：glibc 新（适配 6.x 内核）、稳定
https://www.debian.org/releases/bookworm/debian-installer/


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


## 可观测内核实验系统


👉 给你一套“6.6 LTS 内核实验路线”（从入门到进阶）  包括：
- 必改的 10 个内核点
- 必做的 5 个实验
- 如何写出能写进简历的项目

这个会直接决定你能不能进内核岗（不是开玩笑）









