

# xdma-linux驱动剖析


## 数据读写原理


1、对应的设备节点：
```bash
root@mr50:/usr/src/xdma_binge_debug/xdma# ls -l /dev/xdma0_*
crw------- 1 root root 508, 36 12月 20 18:21 /dev/xdma0_c2h_0  (板卡到主机)
crw------- 1 root root 508, 32 12月 20 18:21 /dev/xdma0_h2c_0  (主机到板卡)
...
root@mr50:/usr/src/xdma_binge_debug/xdma#
```


**char_sgdma_read_write(数据流-->内存对象)**

1、完整执行流骨架(看草稿图建立一个基本图景印象)：[[pcie-xdma-dataio.excalidraw]]
- (1)、用户空间写入数据: write(h2c, 12KB, ...);
- (2)、内核空间: char_sgdma_read_write(...);
	- [[...]];
	- [[...]];
		- nents = [[...,sg, sgt->orig_nents,...]];
		- 创建req实例、req->sdesc数组: req = [[sgt, ep_addr]];
			- 创建sdesc数组: [[sdesc节点个数]];
			- 遍历每个sdesc节点，初始化每个sdesc节点:
				- req->sdesc[j].addr = sg_dma_address(sg);
				- req->sdesc[j].len = sg_dma_len(sg);
				- 特殊情况: req->sdesc[j].len = [[desc_blen_max]];
		- while (nents) {
			- 构建单个传输实例: [[transfer_init]]
				- [[...]];
				- [[...]];
				- [[...]];
			- 交给引擎: [[engine, xfer]];
			- 阻塞等待: [[xfer->wq, ...]]
			- 其他哪个位置的代码会主动唤醒它？
			- 结束本轮循环: transfer_destroy
		- }
		- pci_unmap_sg(...,sg, sgt->orig_nents,...);
		- xdma_request_free(...);
	- char_sgdma_unmap_user_buf(...);


3、经过详细分析简化后的结构图：
![[Pasted image 20251220072810.png]]



## 中断向量原理


1、用户空间设备节点，默认共有16个节点，也就是16个中断向量。
```bash
root@mr50:/usr/src/xdma_binge_debug/xdma# ls -l /dev/xdma0_*
crw------- 1 root root 508, 10 12月 20 18:21 /dev/xdma0_events_0
crw------- 1 root root 508, 11 12月 20 18:21 /dev/xdma0_events_1
crw------- 1 root root 508, 12 12月 20 18:21 /dev/xdma0_events_2
...
crw------- 1 root root 508, 25 12月 20 18:21 /dev/xdma0_events_15
root@mr50:/usr/src/xdma_binge_debug/xdma#
```


2、下面是用户中断的函数调用关系图：[[xdma_events_io]]
![[Pasted image 20251221014406.png]]

如上图所示，PCIe 设备可以同时支持 MSI 与 MSI-X 两种中断能力，但同一时刻只能启用其中一种，二者在使能层面互斥，这是 PCIe 规范的明确要求。也就是上图最上面不是(1)就是(2)，不是(2)就是(3)。规范强制要求同一 PCIe Function 的 MSI Enable 与 MSI-X Enable 位不能同时置 1，必须互斥使能。规范原文要点：PCIe 规范（及 PCI 3.0+）规定，系统软件初始化中断时，对同一 Function 只能激活 MSI、MSI-X 或 INTx 中的一种，且 MSI 与 MSI-X 不可同时激活。<font color=blue>为什么只能使能其中一种？</font> 因为二者的中断投递机制本身不兼容，无法在同一套硬件逻辑中共存。二者的硬件通路、中断路由逻辑完全不兼容，共享同一套物理资源且无法区分。


```cpp
static ssize_t char_events_read(struct file *file, 
		char __user *buf, size_t count, loff_t *pos)
{
	struct xdma_cdev *xcdev = (struct xdma_cdev *)file->private_data;
	user_irq = xcdev->user_irq;
	
	// 阻塞方式等待(events_wq:等待队列)
	rv = wait_event_interruptible(user_irq->events_wq,
			user_irq->events_irq != 0);
	
	/* wait_event_interruptible() was interrupted by a signal */
	// 比如用户等待过程中按 Ctrl+C 终止了，或者强制kill该进程了
	// **不可捕获、不可忽略**的信号，进程会直接终止/暂停，不会走到这里if位置
	if (rv == -ERESTARTSYS)
		return -ERESTARTSYS;
	
	/* atomically decide which events are passed to the user */
	spin_lock_irqsave(&user_irq->events_lock, flags);
	events_user = user_irq->events_irq;
	user_irq->events_irq = 0;
	spin_unlock_irqrestore(&user_irq->events_lock, flags);

	// 把目标值拷贝到用户空间
	rv = copy_to_user(buf, &events_user, 4);
	return 4;
}
```

<font color=blue>MSI 和 MSI 支持的中断向量分别是多少？中断向量 这个词是什么意思？他和传统的中断irq的区别和关联。
</font>

MSI 最多支持 32 个中断向量，MSI - X 最多支持 2048 个中断向量；中断向量本质是中断服务程序入口地址的标识（x86 体系为 0-255 的向量号），你可以理解为ISR数组，用于 CPU 快速定位中断处理程序，你可以理解为通过下标快速定位数组元素；传统 IRQ 是中断请求信号线 / 请求编号，与中断向量通过中断控制器映射关联，是不同层面的中断标识。MSI-X 作为 MSI 的扩展，它最多支持 2048 个中断向量，且**向量无需连续，每个向量可独立配置地址与数据**，更灵活高效。

进阶：
GICv2 —— struct irq_domain
GIC驱动 —— struct irq_chip
驱动ISR —— struct irq_desc

## 主板BIOS与PCIe配置

<font color=blue>主板BIOS与PCIe设备相关的配置信息有哪些？
</font>

或者说是PCIe哪些配置信息需要依赖主板BIOS配置？UEFI配置？

主板 BIOS 中与 PCIe 设备相关的配置，核心围绕**链路与通道、资源分配、高级特性、电源管理、兼容性与虚拟化**五大模块，多在 Advanced/Chipset/PCIe Configuration 菜单下，不同厂商（如 Intel/AMD）与主板型号会有菜单项差异。

- **一、PCIe 链路与通道基础配置**
	- <font color=green>PCIe Generation</font>（链路版本），Auto（默认）、Gen1~Gen5，性能优先时选 Auto / 最高代际。
	- <font color=green>Link Width</font>，Auto、x1/x4/x8/x16，多设备共存时拆分通道（如 x16 拆 x8/x8），单卡时拉满带宽。
	- <font color=green>PCIe Bifurcation</font>（通道拆分），Disabled、x8x8、x8x4x4，将 CPU 直连 x16 通道拆分为多组（如 x8/x8、x8/x4/x4），多 GPU / 多 NVMe 卡并行场景；需 CPU / 主板 / BIOS 共同支持。
	- <font color=green>Link Speed/Training</font>， Auto、GenX、Retrain Link，控制链路协商速率，可强制训练，链路不稳时强制重训；用于规避高代际兼容性问题。
- **二、地址与资源分配配置**
	- <font color=green>Above 4G Decoding</font>，Enabled/Disabled，启用 4GB 以上内存地址空间解码，大 BAR 设备（如显卡 / PCIe SSD）需要开启来提供支持。
	- <font color=green>Resizable BAR (ReBAR/SAM)</font>，Enabled/Disabled/Auto，允许 OS 动态调整 PCIe BAR 空间大小，提升显卡 / 加速卡显存访问效率，需 CPU / 设备 / BIOS 协同支持。
	- <font color=green>PCIe Resource Allocation</font> 为 PCIe 设备预分配资源， Auto、Manual、Expand，多设备时避免资源冲突；PCIe 热插拔 / 热添加需 Expand 模式。
	- <font color=green>PCIe Slot</font> Enable/Disable 启用 / 禁用指定 PCIe 插槽，屏蔽不用的插槽以释放资源，减少枚举耗时。
	- <font color=green>Option ROM</font>（扩展 ROM），控制 PCIe 设备的启动 ROM 加载，Enabled/Disabled/Auto，传统设备（如 RAID 卡）需启用；UEFI 启动时可按需关闭。“启动 ROM 加载” 本质是主板 BIOS 在 POST 阶段，将 PCIe 设备自带 Option ROM（扩展 ROM）中的固件代码映射到内存并执行，核心是让设备在 OS 启动前完成初始化与特定引导服务，并非让设备 “独立运行自己 ROM 程序”，而是 BIOS 主导下的协作执行。加载流程：BIOS POST→枚举 PCIe→查配置空间 0x30 偏移的 ROM 基址寄存器→验证 ROM 签名（0xAA55）→映射 ROM 到内存→调用入口执行→执行完交还控制权。典型使用场景: - RAID 卡（加载阵列配置、初始化逻辑卷，支持从阵列盘启动），PXE 网卡（提供网络引导服务，支持无盘启动或远程装机），NVMe/PCIe SSD（在 UEFI 环境提供早期识别，支持从 NVMe 盘启动）。
- **三、高级特性与虚拟化配置**
	- <font color=green>SR-IOV Support</font> Enabled/Disabled，启用单根 I/O 虚拟化，允许设备虚拟为多 VF，需 CPU / 芯片组 / 设备驱动均支持；虚拟化场景（如 KVM）必备。
	- <font color=green>ACS(Access Control Services)</font> Enabled/Disabled，隔离 PCIe 设备间的 DMA 与事务访问，虚拟化环境中防止设备越权访问，提升安全性。
	- <font color=green>ATS(Address Translation Services)</font> Enabled/Disabled，支持 IOMMU 地址翻译，优化 DMA 性能，配合 VT-d/AMD-Vi 使用，适合高速 I/O 设备（如 XDMA 加速卡）。
	- <font color=green>Hot Plug/Hot Add</font> Enabled/Disabled，支持 PCIe 设备热插拔 / 热添加，服务器场景；需主板插槽 / 电源 / OS 驱动支持。
- **四、电源管理配置**
	- <font color=green>ASPM（Active State Power Management）</font>,链路低功耗状态（L0s/L1/L1.2/L1.1）, Auto、Disabled、L0s/L1, 节能优先时选 Auto；高负载 / 低延迟场景（如 XDMA 实时传输）建议禁用，避免链路波动。
	- L1 Substates 启用 L1.1/L1.2 深度节能，Enabled/Disabled，延长待机续航；可能影响高实时性设备（如高速采集卡）。
	- PCIe ASPM L1 PM Substates，Auto、Enabled/Disabled，控制 L1 子状态参数，平衡功耗与延迟，按设备手册调整。
- **五、兼容性与错误处理配置**
	- <font color=green>PCIe Error Reporting</font> Enabled/Disabled, 启用 PCIe 事务层错误上报（如 Correctable/Uncorrectable Error）, 调试链路错误时启用；生产环境可按需关闭以避免误触发宕机。
	- <font color=green>PCIe Compliance Mode</font> Enabled/Disabled, 硬件调试时使用，非普通用户场景。
	- <font color=green>Legacy PCIe Support</font> Enabled/Disabled, 老旧设备（如早期 PCIe 网卡）适配；纯 UEFI 环境可关闭。
- **六、中断与 DMA 相关配置**
	- <font color=green>PCIe Interrupt Routing</font> 控制 PCIe 中断的路由方式（如 MSI/MSI-X/INTx），Auto、MSI-X Preferred，优先启用 MSI-X 以提升中断并行性，适合高吞吐设备（如 NVMe/XDMA）。
	- <font color=green>VT-d/AMD-Vi</font>，启用 IOMMU，隔离设备 DMA 地址空间，Enabled/Disabled，虚拟化 / 安全场景必备；防止 DMA 攻击，支持 SG DMA 地址翻译。
- **七、NVMe / 存储专项配置**
	- <font color=green>NVMe PCIe Resource Padding</font>, 为 NVMe 热添加预分配资源, Normal/Medium/High, 服务器热插拔 NVMe 时选 Medium/High，避免资源不足。
	- <font color=green>NVMe Boot Priority</font>, 设置 NVMe 设备为启动项, Enabled/Disabled, 从 NVMe SSD 启动系统时需启用。





## (TODO)流模式与MM原理

流模式与内存映射模式，流模式的本质，以及应用场景。

<font color=blue>xdma中，与流模式(stream mode)对应的是什么模式？它们之间有什么区别？两者主要分别应用在哪种场合？
</font>

简单来说，AXI-ST模式应用于高频小数据量场景, AXI-MM模式应用于大数据量场景。

AXI-ST 和 AXI-MM，内存映射模式；AXI-ST模式无DDR缓存，依赖 FIFO 缓冲；AXI-MM模式突发传输，支持 Scatter-Gather（SG）管理非连续内存；AXI-ST模式极低延迟（无地址握手，数据直传 FPGA 逻辑），而 AXI-MM模式延迟相对较高（需地址解析、描述符调度，可配 SG 优化）；AXI-ST模式无描述符，靠流控信号与时序同步；AXI-MM模式依赖描述符链表或块描述符，支持中断 / 轮询完成通知；AXI-ST模式适配持续稳定的流式带宽，适合小数据包连续传输，适合实时流水线处理；AXI-MM模式追求链路饱和带宽，适合 GB 级大块批量数据传输。

---


<font color=blue>BIOS和ACPI是什么关系？</font>

BIOS（传统 BIOS）/UEFI（现代 BIOS 的替代者）与 ACPI 是**从属与承载的关系**：**ACPI 是一套硬件管理规范，而 BIOS/UEFI 是实现并承载这套规范的固件载体**，二者协同为操作系统提供统一的硬件配置、电源管理和资源调度能力。

简单来说：**BIOS/UEFI 是 “执行者”，ACPI 是 “执行标准”**。


---

<font color=blue>ACPI 为内核提供硬件信息，这里的硬件信息有没有标准的数据结构来存储描述？</font>

简单来说，ACPI 的硬件信息描述体系分为 **两层核心结构**：**系统描述表头 + 功能表数据**，所有信息最终都会被 Linux 内核的 ACPI 子系统解析，转化为驱动可识别的硬件资源。

**一、 顶层统一结构：系统描述表（SDT）的通用表头**

所有 ACPI 硬件信息表都共享一个 **标准化的 36 字节表头** (struct acpi_table_header)，OS内核通过表头识别表的类型、长度、校验和等关键信息。

```cpp
struct acpi_table_header {
    char        signature[4];      // 表签名，如"DSDT" "SSDT" "PCI"
    u32         length;            // 整个表的长度（含表头）
    u8          revision;          // ACPI 规范版本号
    u8          checksum;          // 校验和（整个表求和为0）
    char        oem_id[6];         // 厂商ID，如"DELL " "INTEL"
    char        oem_table_id[8];   // 厂商表ID，自定义标识
    u32         oem_revision;      // 厂商修订版本
    char        asl_compiler_id[4];// ASL编译器ID，如"ACPI"
    u32         asl_compiler_revision; // 编译器版本
};
```

**二、 与 PCIe 硬件信息强相关的标准功能表结构**

对于你关注的 **PCIe 设备**，有一个**MCFG 表（Memory Mapped Configuration Space Table）**，其作用是描述 PCIe 配置空间的内存映射地址范围，内核通过它找到 PCIe 设备的配置空间入口。


---

<font color=blue>比如XDMA需要16个irq vector支持，这时候就需要VT-d 支持，才能支持多个irq vector的申请和使用。那么Linux内核是如何获取到VT-d 相关的支持并知道是否支持多个vector？是通过ACPI信息获取的吗？</font>

核心靠 ACPI 的 DMAR 表与 CPUID/MSR 硬体检测，ACPI 是传递 VT-d 控制器与设备管辖范围的关键载体，多向量能力还需结合 IOMMU、PCIe MSI‑X 与中断子系统综合判断。

中断重映射是多 IRQ 向量的关键：VT‑d IR 支持将设备 MSI/MSI‑X 向量映射到不同 CPU 核，为 XDMA 的 16 个向量提供隔离与路由能力。内核 IOMMU 子系统（drivers/iommu/intel/iommu.c）基于 DMAR 表初始化 VT‑d 控制器，启用 DMA 重映射与中断重映射。

acpi_table_header
https://elixir.bootlin.com/linux/v5.15/source/arch/x86/kernel/acpi/boot.c#L123
https://elixir.bootlin.com/linux/v5.15/source/arch/arm64/kernel/acpi.c#L129
https://elixir.bootlin.com/linux/v5.15/source/drivers/iommu/intel/iommu.c





## (TODO)异步轮询模式原理




## (TODO)物理链路Root Port


1、我们想要让xdma尽量调高PCI MRRS (Memory Read Request Size) 数据量。核心思路是 **隔离 XDMA 设备的 PCIe 链路、避免总线资源竞争**。也就是让xdma独占一个物理链路(Root Port)。

2、PCIe 设备的总线归属由 CPU 的 PCIe 控制器（Root Complex）和主板布线决定。每个 **Root Port** 对应一条独立的物理总线，若多个设备共享同一个 Root Port，则会竞争总线带宽。
- 1、**选择独立的 PCIe 根端口（Root Port）**：查阅主板手册，找到**直连 CPU 的 PCIe 插槽**（而非通过芯片组扩展的插槽），这类插槽通常拥有独立的 Root Port 和更高的链路带宽（如 x16）。将 XDMA 卡插入该独立插槽。
- 2、**配置 PCIe 链路宽度和速率（锁定最大带宽）**：XDMA 的 MRR 吞吐量受 PCIe 链路宽度（x4/x8/x16）和速率（Gen3/Gen4/Gen5）限制，需锁定链路运行在**最大配置**，避免降速。
- **验证命令**：
- 若链路宽度 / 速率未达最大值，可在 BIOS 中关闭 **PCIe Power Management** 或 **Auto Negotiation**，强制设置为目标规格（如 Gen4 x8）。




2、可以通过拓扑关系，才能看出xdma与其他设备比如gpu是否共用一个root port，如下信息所示，显然和多个设备共用一个Root Port，若想让xdma独占一个物理链路，则把它插在主板上的空闲PCIe插槽上即可。这里信息表明xdma和gpu都插在交换芯片下游。


# (TODO)数据通路速度不匹配问题





# (TODO)解决内核PCIe热插拔问题


现实中遇到一个问题，BIOS启动太快，导致没有枚举到 PCIe 相关设备，导致设备无法正常被加载到系统。




# ax7015-PCIe基础实验


- [ ] ax7015-hdmi输出实验
- [ ] ax7015-hdmi直通ila调试实验
- [ ] ax7015-GTX收发器误码率测试IBERT实验
- [ ] ax7015-使用vdma驱动hdmi显示
- [ ] ax7015-PCIe基础测试
- [ ] ax7015-PCIe传输视频到HDMI显示
- [ ] ax7015-HDMI视频输入到PCIe捕捉显示
- [ ] 可观测性-日志与指标


日志是**离散的点**：记录单个事件的 “快照”，但无法反映全局趋势；

指标是**连续的线**：把无数个 “点” 串联成趋势，暴露系统的瓶颈和异常关联；

只有 “点 + 线” 结合，才能从 “知道发生了什么”，升级到 “明白为什么发生”。



1、下面是 Lane Width 这个参数探究（x1、x2、x4、x8、x16），实际连了几路就算几路。
![[Pasted image 20251219233842.png]]

```txt
IBUFDSGTE = I + BUF + DS + GT + E
          = Input + buffer + 差分信号 + GTX收发器 + Enable
就是专门为这个GTX收发器设计的
```



# ax7015-vdma-xdma

07A_基于 XDMA 的 PCIe 实时视频传输系统Vivado工程设计

[[BV1fd1pBGELq]]

1、如下图所示，首先摄像头图像数据沿着红色箭头最终写入到DDR里。
![[Pasted image 20251219232627.png]]


2、如下图所示，前面存入DDR的数据，可以通过VDMA，从DDR把数据搬运到HDMI显示。
![[Pasted image 20251219232717.png]]


3、如下图所示，同样也能把DDR里的数据，通过XDMA搬运给上位机显示。
![[Pasted image 20251219232758.png]]


累加数验证数据正确性




# RDMA技术原理


<font color="blue">
1、XDMA是直接将用户内存的物理页交给dma引擎，让引擎直接访问该物理页。那RDMA的RNIC也是这样吗？相当于RNIC左边是服务器A的应用内存，右边是服务器B的应用内存，把两边应用内存的物理页交给RNIC，然后让RNIC内置dma引擎实现双方数据搬运？
</font>

- 两者相似点：都要**pin 住用户内存物理页**（防止换出），并把物理地址 / IOVA 交给 DMA 引擎，实现内核旁路、无 CPU 拷贝。
- RDMA 的关键差异（核心区别）: 远端访问时用虚拟地址查 MTT 找物理页，不是直接暴露物理地址。通过**队列对 QP**下发 RDMA_READ/RDMA_WRITE/SEND 等指令；RNIC 负责网络层可靠传输（如 InfiniBand/RoCE/TCP），确保跨机数据正确送达目标物理页。传输完成后，RNIC 通过**完成队列 CQ**异步通知应用，不阻塞 CPU。
- 关键差异: 在DMA搬运之前，多了一些权限相关操作。全程CPU 只发指令和收通知。

---

<font color="blue">
2、RNIC 里的DMA引擎是如何访问服务器的物理内存？物理内存不是在各自服务器里吗？又不是在RNIC里。
</font>

- 核心结论：RNIC 的 DMA 引擎只直接访问**本地服务器物理内存**，远程内存是通过**网络传输 + 远端 RNIC 本地 DMA**接力完成，并非跨机直接 “碰” 对方物理内存。

---

<font color="blue">
3、那等同于本地RNIC的面向本地服务侧是有物理内存的，外侧是直连网络的，那RNIC 里的DMA引擎只有一侧有物理内存呀，另一侧的数据怎么访问？
</font>

本地 RNIC 面向本地服务侧有物理内存。**“另一侧数据” 的访问逻辑：两端 DMA + 网络的接力传输**。以常用的 RDMA_WRITE 操作为例，完整流程如下：

1. **本地 DMA 读取数据**：服务器 A 的应用发起传输请求后，A 的 RNIC 从 SQ（发送队列）获取指令，DMA 引擎通过 PCIe 总线查本地 MTT 拿到物理地址，直接读取本地服务器 A 的物理内存数据。
2. **网络传递数据报文**：A 的 RNIC 把读取到的数据，加上服务器 B 的目标内存地址、R_Key（远程访问密钥）等信息封装成 RDMA 报文，通过 InfiniBand、RoCE 等网络链路发送给服务器 B 的 RNIC。
3. **远端校验与地址转换**：服务器 B 的 RNIC 收到报文后，先通过 MPT 校验 A 发来的 R_Key，确认访问权限合法后，再查自己本地的 MTT，把报文中的目标虚拟地址转换成 B 服务器本地的物理地址。
4. **远端 DMA 写入数据**：B 的 RNIC 内置 DMA 引擎同样通过 PCIe 总线，把收到的数据直接写入 B 服务器对应的物理内存中。最后 B 的 RNIC 通过完成队列（CQ）异步通知本地应用，数据已成功写入。

简单来说，RNIC 的 DMA 引擎始终只 “负责自己身边的事”—— 仅访问本地物理内存，远程物理内存的数据是靠两端 RNIC 的 DMA 引擎各自完成本地读写，再通过网络传递数据实现的 “接力搬运”。这也正是 RDMA 能做到零拷贝、低 CPU 占用的核心，既解决了跨服务器数据传输的效率问题，又通过 R_Key、MTT 等机制保障了内存访问的安全性。



