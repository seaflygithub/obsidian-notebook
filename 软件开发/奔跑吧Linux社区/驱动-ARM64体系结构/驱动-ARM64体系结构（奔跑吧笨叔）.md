
草稿: [[笨叔ARM64体系结构.excalidraw]]

# 裸机实验环境

笨叔虚拟机里，arm64_programming_practice.zip

Ubuntu 20.04 环境里，裸跑笨叔的 BenOS 系统，需要安装如下环境：

```bash
sudo apt-get install -y qemu-system-arm
sudo apt-get install -y libncurses5-dev
sudo apt-get install -y gcc-aarch64-linux-gnu
sudo apt-get install -y build-essential
sudo apt-get install -y git
sudo apt-get install -y bison
sudo apt-get install -y flex
sudo apt-get install -y libssl-dev
```

编译和运行笨叔的 BenOS：

```bash
# cd到对应裸机Makefile所在目录

# 编译裸机代码
make

# 运行裸机代码
make run
```

使用 GDB 与 QEMU 虚拟机调试BenOS：

1、首先在 qemu-system-aarch64 命令的参数末尾添加参数( -S -s)；

2、在另一个终端启动GDB：`gdb-multiarch —tui build/benos.elf`

3、在GDB命令行中，输入如下连接 qemu 的服务端:

```bash
target remote localhost:1234
b  _start
continue
```

# 裸机汇编实验

内存访问指令

```cpp
// 前变基模式
ldr    x1, [x2, #4]!    //等同于 x1 = [x2+4]; x2 = x2 + 4;

// 后变基模式
ldr    x1, [x2], #4     //等同于 x1 = [x2]; x2 = x2 + 4;
```

相对寻址与LDR伪指令

```cpp
// 相对寻址
ldr    <Xt>, <label>   //注意,标签地址必须在 PC ± 1MB 范围内

my_data:
	.word  0x40
ldr  x0, my_data  // x0 == 0x40

#define MACRO_AAA 0x20
ldr  x0, MACRO_AAA // x0 == PC + 0x20
```

LDR伪指令

```cpp
// ldr 伪指令
#define MY_LABEL 0x20
ldr  x0, =MY_LABEL  // 等同于 x0 = 20

my_data1:
	.quad  0x8
ldr  x1, =my_data1
ldr  x2, [x1]   // x2 = 0x8
```

## LDR伪指令与重定位

```cpp
// linux-5.0/arch/arm64/kernel/head.S
PROC(__primary_switch)
__primary_switch:
    adrp    x1, init_pg_dir
    bl        __enable_mmu

    ldr      x8, =__primary_switch
    adrp   x0, __PHYS_OFFSET
    br       x8
ENDPROC(__primary_switch)
```

上面是一段arm64的汇编代码，利用ldr伪指令达到地址重定位的目的，

请问使能 mmu 之前的 __primary_switch 和 使能 mmu 之后的 __primary_switch 地址是否相同？它们的地址分别来源于哪里？

总结 MMU 使能前：__primary_switch地址是物理地址（例如 0x0000000000080000）。 MMU 使能后：__primary_switch地址是虚拟地址（例如 0xFFFF000000080000）。 地址差异来源：物理地址到虚拟地址的偏移量（__PHYS_OFFSET）。

这种设计确保了内核可以在 MMU 使能前后无缝切换地址空间，是 ARM64 架构下启动流程的典型实现方式。

## RET指令之后崩溃

函数在执行bl func1之后，再执行ret就崩了，

解决办法是在遇到嵌套调用函数时在父函数里把LR的值保存到一个临时寄存器里或者栈里，

在父函数真正执行ret指令之前，恢复一下LR寄存器，再执行ret指令。

```cpp
// 用现成的启动代码来运行看效果
.globl _start
_start:
	mrs	x0, mpidr_el1		
	and	x0, x0,#0xFF		// 检查处理器核心ID
	//cbz	x0, master		// 除了CPU0，其他CPU都会在这里死循环等待

	// 初始化栈指针,我们用栈来保存LR
	mov	sp, #0x800000

	// 调用子函数之前,保存lr: [sp]=lr; sp=sp-8
	str  lr, [sp],#-0x08

	// 调用子函数
	bl test_func1
	
	// 调用子函数之后,恢复lr: lr=[sp]; sp=sp+8
	ldr  lr, [sp],#0x08

	// 调用ret能访问到正常的lr值
	ret
	//b	proc_hang

.globl test_func1
test_func1:
	mov  x2, x0

	// 调用子函数之前,保存lr: [sp]=lr; sp=sp-8
	str  lr, [sp],#-0x08

	// calling subfunc
	bl   test_func2

	// 调用子函数之后,恢复lr: lr=[sp]; sp=sp+8
	ldr  lr, [sp],#0x08

	// ret
	ret

.globl test_func2
test_func2:
	mov  x2, x0

	// 调用子函数之前,保存lr: [sp]=lr; sp=sp-8
	str  lr, [sp],#-0x08

	bl test_func3

	// 调用子函数之后,恢复lr: lr=[sp]; sp=sp+8
	ldr  lr, [sp],#0x08

	ret

.globl test_func3
test_func3:
	mov x2, x0

	// 调用子函数之前,保存lr: [sp]=lr; sp=sp-8
	str  lr, [sp],#-0x08

	bl test_func4

	// 调用子函数之后,恢复lr: lr=[sp]; sp=sp+8
	ldr  lr, [sp],#0x08

	ret

.globl test_func4
test_func4:
	mov  x2, x2
	mov  x2, x3
	ret
```

## CPU多核心闲置

```cpp
.section ".text.boot"

// BenOS启动代码
// arm64_programming_practice/chapter_2/lab01_hello_benos/BenOS/src/boot.S
.globl _start
_start:
	mrs	x0, mpidr_el1  // 读取多核id寄存器
	and	x0, x0,#0xFF	 // 检查处理器核心ID
	cbz	x0, master     // 如果是CPU0,则跳转到master函数,其他CPU会跳转到proc_hang函数
	b	proc_hang
	
proc_hang: 
	b 	proc_hang
	
master:
	adr	x0, bss_begin
	adr	x1, bss_end
	sub	x1, x1, x0
	bl 	memzero

	mov	sp, #LOW_MEMORY 
	bl	kernel_main
	b 	proc_hang
```

## LDR和ADRP指令区别

比如，当前程序的运行地址是 0x80000，而程序编译时的链接地址为 0xFFFF000000080000，

此时我们应该使用 adrp x0, init_pg_dir 来加载该标签地址，此时 x0 的地址是在 0x80000 附近的地址，

如果是用 ldr x0, =init_pg_dir 这条指令，由于链接地址是一个虚拟地址，此时CPU还没有建立虚拟地址到物理地址的映射，

因此程序就会出错，此时 x0 的值是在 0xFFFF000000080000 附近。

# 内核实验环境

```bash
cd ~/rlk/runninglinuxkernel_5.0
./run_debian_arm64.sh  build_kernel
./run_debian_arm64.sh  build_rootfs
./run_debian_arm64.sh  run

用户名: root  密码: 123
虚拟机内笨叔配置好了 VirtIO-Net 虚拟网卡，因此虚拟机内部可以和外部相互网络通信。

或者
./run_debian_arm64.sh  run debug
```

# 异常处理

## 异常等级

Exception Levels

可以粗略理解为：EL0=用户程序，EL1=系统程序，EL2=虚拟程序，EL3=安全程序。

当发生异常（如中断、系统调用）时，执行流程会从低特权级切换到高特权级。

高特权级可以访问低特权级的寄存器，但低特权级无法直接访问高特权级的寄存器。

EL3 能够隔离 EL2/EL1/EL0，EL2 可以隔离 EL1/EL0，这种分层隔离机制保障了系统的安全性。

EL2 在需要虚拟化的场景下，运行 Hypervisor 和多个客户机操作系统。

运行 TrustZone 等安全相关的代码，保障关键功能的安全性，能够隔离关键系统功能（如安全启动、加密操作、银行资金系统等）。

ARM中断模型：每个外设都有一根中断线连接到中断控制器(IC)，然后IC有两根线连到CPU，分别是IRQ、FIQ。

复位操作是优先级最高的一种异常处理，它通常让CPU复位引脚产生复位信号，进而让CPU进入复位状态并重新启动。

系统调用允许软件主动地通过特殊指令请求更高级程序提供的服务，

可以类比为普通用户到银行取钱，普通用户并不是直接拿钱，而是需要通过银行工作人员才能拿到钱。

SVC指令：允许用户申请系统内核的服务；

HVC指令：允许客户OS请求 Hypervisor 的服务；

SMC指令：允许普通世界的程序请求安全监视器的服务；

下面这个示例展示了如何在 ARM64 汇编中使用 SVC 指令调用 Linux 系统服务：

```cpp
.global _start

_start:
    // 准备系统调用参数 - 写操作 (sys_write)
    mov x0, #1          // 文件描述符1 = 标准输出
    ldr x1, =message    // 消息地址
    mov x2, #13         // 消息长度
    mov x8, #64         // 系统调用号64 = sys_write
    svc #0              // 触发系统调用

    // 准备退出程序 (sys_exit)
    mov x0, #0          // 返回码0
    mov x8, #93         // 系统调用号93 = sys_exit
    svc #0              // 触发系统调用

message:
    .ascii "Hello World\\n"
```

ARM64中，常见的异步异常分为物理中断和虚拟中断两种，

而物理中断又细分为 SError、IRQ、FIQ，虚拟中断又细分为 vSError、IRQ、FIQ。

在 ARMv8 处理器里，

当一个异常发生时，CPU硬件层面就能感知到异常发生，而且会生成一个目标异常等级(Target EL)，

并且会硬件层面自动完成如下事情：

（1）PSTATE 寄存器的值保存到目标异常等级的SPSR寄存器（SPSR_ELx）；

（2）把返回地址保存到目标异常等级的ELR寄存器（ELR_ELx）；

（3）把PSTATE寄存器里的D、A、I、F标志位都置1，相当于把调试异常、SError、IRQ、FIQ都关闭（相当于关闭本地中断了）；

（4）对于同步异常，CPU硬件会分析异常的原因，并把具体原因写入到 ESR_ELx 寄存器，该寄存器用于存储**异常发生时的详细信息**，包括异常类型、系统调用编号、错误码等。当处理器进入异常处理流程（如中断、SVC 指令触发的异常）时，ESR_EL1 会被CPU硬件自动更新，以帮助软件识别异常原因。 （5）切换SP寄存器为目标等级的寄存器SP_ELx；

（6）从异常发生现场的异常等级，切换到目标异常等级，并跳转到异常向量表里，向量表里的每个项都会保存一条跳转指令，然后跳转到恰当的异常处理函数并处理异常。

当异常处理完成后，软件代码可通过 eret 指令从异常返回，该指令会自动完成如下工作：

（1）从 ELR_ELx 中恢复 PC 指针；

（2）从 SPSR_ELx 中恢复 PSTATE 寄存器的状态（相当于打开本地中断了）。

两个关于返回的寄存器，

x30 寄存器又称为LR，存放子函数的返回地址，在函数调用中起到作用，当执行ret指令时，硬件会从x30寄存器拿到返回地址并跳转过去。

ELR_ELx 寄存器，存放异常的返回地址，当异常处理代码执行完后，执行 eret 指令，硬件自动加载ELR_ELx就可以返回异常发生现场。

异常处理路由，指的是当异常发生时，应该在哪个异常等级处理，下面是规则：

（1）EL0不能用来处理异常，其一般用来运行用户态程序；

（2）比如缺页异常，会从EL1陷入到EL1，也就是不会改变异常等级；

（3）比如开启虚拟化时，虚拟机访问尚未映射的客户物理地址(GPA)，会发生二阶段页表缺页异常，此时会从EL1陷入到EL2，由 Hypervisor Monitor 处理该异常；

（4）对于中断，可以路由到 EL1、EL2甚至EL3并处理，但是需要配置 HCR_EL2 以及 SCR_EL3 相关寄存器；

**栈的选择**

在 ARMv8 体系结构里，每个异常等级都有对应的 SP 指针，例如 SP_EL0, SP_EL1, …

我们可以通过 SPSel 寄存器来配置 SP，

寄存器中的SP字段为0时表示所有 EL 都使用 SP_EL0 作为栈指针寄存器，

寄存器中的SP字段为1时表示使用 SP_ELx 作为栈指针寄存器。

SP_EL0t 后面跟了一个t符号，表示 trapped，

SP_EL1h、SP_EL2h 后面的h符号，表示 Hypervisor/Hyp，这种命名约定体现了 ARMv8 架构对安全隔离和虚拟化的设计考虑。

栈必须16字节对齐，

我们可以通过配置寄存器来让CPU自动检测栈指针是否对齐，

如果没有对齐，则会触发一个 SP alignment fault 异常。

当异常发生时，CPU会自动相应等级的 SP_ELx，

例如，CPU正在EL0中运行用户空间进程，突然触发了一个中断，

CPU就会跳转到 EL1 来处理这个中断，因此CPU会自动选择 SP_EL1 指向的栈空间。

操作系统负责保障异常等级对应的栈空间是可用的，

以 BenOS 的实验代码为例，在汇编代码准备跳转到 C 语言的 main 函数之前，

我们需要分配栈的空间，比如 4KB 或者 8KB，然后设置SP，跳转到C语言的main函数。

**异常返回的执行状态**

当异常处理结束后，执行 eret 时要不要切换执行模式？这里得看 SPSR 寄存器，

SPSR.M[3:0] 记录了返回哪个异常等级，SPSR.M[4] 记录了返回哪个执行状态(0=aarch64,1=aarch32)，

**异常向量表**

在 ARMv8 体系结构中，每个异常级别都有自己的向量表，

在 ARMv7 体系结构的异常向量表比较简单，每个表项是4字节，每个表项存放了一条跳转指令。

在 ARMv8 体系结构的异常向量表中，每个表项是128字节，注意每条指令还是32位，这个可以通过反汇编看，

```cpp
+0x000  ————  同步(以下是 EL0)
+0x080  ————  IRQ/vIRQ
+0x100  ————  FIQ/vFIQ
+0x180  ————  SError/vSError

+0x200  ————  同步(以下是 ELx)
+0x280  ————  IRQ/vIRQ
+0x300  ————  FIQ/vFIQ
+0x380  ————  SError/vSError

+0x400  ————  同步(以下是 aarch64)
+0x480  ————  IRQ/vIRQ
+0x500  ————  FIQ/vFIQ
+0x580  ————  SError/vSError

+0x600  ————  同步(以下是 aarch64)
+0x680  ————  IRQ/vIRQ
+0x700  ————  FIQ/vFIQ
+0x780  ————  SError/vSError
```

异常向量表存放的基地址可以通过向量基地址寄存器(VBAR——Vector Base Address Register)来设置，

Linux 5.0 内核中，异常向量表的描述在 arch/arm64/kernel/entry.S 文件中：

```cpp
/*
 * Exception vectors.
 */
	.pushsection ".entry.text", "ax"

	.align	11
SYM_CODE_START(vectors)
	kernel_ventry	1, t, 64, sync		// Synchronous EL1t
	kernel_ventry	1, t, 64, irq		// IRQ EL1t
	kernel_ventry	1, t, 64, fiq		// FIQ EL1h
	kernel_ventry	1, t, 64, error		// Error EL1t

	kernel_ventry	1, h, 64, sync		// Synchronous EL1h
	kernel_ventry	1, h, 64, irq		// IRQ EL1h
	kernel_ventry	1, h, 64, fiq		// FIQ EL1h
	kernel_ventry	1, h, 64, error		// Error EL1h

	kernel_ventry	0, t, 64, sync		// Synchronous 64-bit EL0
	kernel_ventry	0, t, 64, irq		// IRQ 64-bit EL0
	kernel_ventry	0, t, 64, fiq		// FIQ 64-bit EL0
	kernel_ventry	0, t, 64, error		// Error 64-bit EL0

	kernel_ventry	0, t, 32, sync		// Synchronous 32-bit EL0
	kernel_ventry	0, t, 32, irq		// IRQ 32-bit EL0
	kernel_ventry	0, t, 32, fiq		// FIQ 32-bit EL0
	kernel_ventry	0, t, 32, error		// Error 32-bit EL0
SYM_CODE_END(vectors)
```

ESR_ELx寄存器

# 中断处理

# GICv2、GICv3

# 内存管理







