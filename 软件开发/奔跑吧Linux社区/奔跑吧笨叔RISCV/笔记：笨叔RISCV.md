[TOC]

# 第02章-搭建RISC-V实验环境

## 虚拟机环境

参考手册：
1. The RISC-V Instruction Set Manual Volume I: Unprivileged ISA, Version 20191213 
2. The RISC-V Instruction Set Manual Volume II: Privileged Architecture

- 01、使用笨叔提供的现成的实验环境：
  - 虚拟机压缩包: rlk_vmware_image_第二版_v1.4.2.rar
  - 主机：ubuntu20.04 （ 用户名：rlk ，密码：123 ）
  - QEMU：qemu-system-riscv64 4.2.1
  - GCC：riscv64-linux-gnu-gcc 9.3
  - gdb-multiarch：9.2
  - 百度网盘：奔跑吧Linux社区（笨叔）/
  - 视频教程平台: 微信小程序小鹅通
  - 开源代码：https://github.com/runninglinuxkernel/
  - 开源文章：https://github.com/runninglinuxkernel/riscv_programming_practice
  - The RISC-V Instruction Set Manual Volume I: Unprivileged ISA, Version 20191213 
  - The RISC-V Instruction Set Manual Volume II: Privileged Architecture


## QemuVirt地址空间

- The corresponding source code files for QEMU: **qemu/hw/riscv/virt.c**
- The hardware features supported by the platform are as follows:  
    - A maximum of 8 **RV32GC/RV64GC** general-purpose processor cores are supported.  
    - CLINT
    - Supports platform-level interrupt controllers.
    - Nor Flash
    - RTC
    - 8xVirtIO-MMIO
    - 1xPCIe Host Bridge Equipment  
    - fw_cfg, which for obtaining firmware configuration information from QEMU.  

---

<a id="20241020200910@InternalLink@QemuVirtAddressSpaceLayout"></a>
- The address space arrangement of the **QEMU Virt** development board. 
```cpp
- (base,size,name)
- 0x00000100, 0x0000F000, ROM
- 0x00101000, 0x00001000, RTC
- 0x02000000, 0x00010000, CLINT
- 0x02F00000, 0x00004000, ACLINT_SSWI
- 0x03000000, 0x00010000, PCIe PIO
- 0x0C000000, 0xXXXXXXXX, PLIC
- 0x10000000, 0x00000100, UART0
- 0x10001000, 0x00001000, VirtIO
- 0x10100000, 0x00000018, fw_cfg
- 0x20000000, 0x04000000, Flash
- 0x30000000, 0x10000000, PCIe ECAM
- 0x40000000, 0x40000000, PCIe MMIO
- 0x80000000, 0xXXXXXXXX, RAM (User-defined size)
```

---

- The allocation of interrupt numbers for the QEMU Virt development board.  
```cpp
VIRTIO_IRQ        ---> 1 ~ 8
UART0             ---> 10
RTC               ---> 11
PCIe              ---> 32 ~ 35
```

---



# 单步调试（QEMU+GDBServer+Eclipse）

## 通过终端单步调试

- 单步调试步骤：  
- 步骤1: 开两个终端，在终端A中执行GDBServer端 `make  debug` (note: `ctrl+a x` can terminal the emulator)，其实就是qemu命令的最后`-S -s`选项。
- 步骤2: 另一个终端运行: `gdb-multiarch  --tui  benos.elf`
- 步骤3: 在客户端这边，设置断点，并通过continue命令开始运行程序。

```bash
# in debugger
(gdb) target remote localhost:1234
(gdb) break src/kernel.c:kernel_main 
Breakpoint 1 at 0x80200444: file src/kernel.c, line 77.
(gdb) continue
(gdb) step  (or next)
```

![[image202502221150.png]]





## 通过Eclipse单步调试

- Step 01: Launch Eclipse, and the workspace is defaulted by Eclipse. 
- Step 02: [[#20241021151110@InternalLink@EclipseRISCVBenOSCCppImportExistingMakefileProject]]
- Step 03: [[#20241021154410@InternalLink@EclipseRISCVBenOSCCppDebugConfigure]]
- Step 04: Execute the `make debug` command in the terminal to enter the debugging wait state. 
- Step 05: [[#20241021154410@InternalLink@EclipseRISCVBenOSCCppDebugStart]]: Perform Debug in Eclipse and set breakpoints, then start debugging.

---

<center>
<a id="20241021151110@InternalLink@EclipseRISCVBenOSCCppImportExistingMakefileProject">
Eclipse Import Existing Makefile Project for BenOS of RISC-V
</a>
</center>

![[image_20241021151110.png]]

---

<center>
<a id="20241021154410@InternalLink@EclipseRISCVBenOSCCppDebugConfigure">
Eclipse Debug Configure for BenOS of RISC-V
</a>
</center>

![[image_20241021154410.png]]

```bash
gdb-multiarch  --tui  benos.elf
```


---

<center>
<a id="20241021154410@InternalLink@EclipseRISCVBenOSCCppDebugStart">
Eclipse Debug Start for BenOS of RISC-V
</a>
</center>

![[image_20241021161510.png]]











# 工程起步

## 工程编译链接树

![[image_20241021170810.png]]

---

![[image_20241021173010.png]]





## 实验02-02-单步调试BenOS和MySBI

- Using QEMU's gdbserver, open Terminal 1 and execute the `make debug` command directly to start the gdbserver.

```bash
# Terminal 1
cd  riscv_programming_practice/chapter_2/benos
export board=qemu
make clean
make 
make debug

# Terminal 2
cd  riscv_programming_practice/chapter_2/benos
export board=qemu
gdb-multiarch  --tui  benos.elf  # benos.elf or mysbi.elf
(gdb) target remote localhost:1234
(gdb) b _start
Breakpoint 1 at 0x80200000: file src/boot.S, line 6.
(gdb) c
```



## 16550串口控制器（tmp）

- reference materials
  - 16550 uart datasheet
  - benos/src/uart.c


---

01、通过 16550 这个串口控制器，我们学到了寄存器还有复用功能，即同一个地址在不同时刻对应的寄存器功能不同。顺便还直到了有 16550 这个串口控制器，以及笨叔提供的往串口写数据的功能。

```cpp
//riscv_programming_practice/chapter_2/benos/include/asm/uart.h
     4	#define UART        0x10000000
     5	
     6	/* THR:transmitter holding register */
     7	#define UART_DAT    (UART+0x00) /* 数据寄存器*/
     8	#define UART_IER    (UART+0x01) /* 中断使能寄存器*/
     9	#define UART_IIR    (UART+0x02) /* 中断标识寄存器 (read only)*/
    10	#define UART_FCR    (UART+0x02) /* FIFO控制寄存器 (write only)*/
    11	#define UART_LCR    (UART+0x03) /* 线路控制寄存器*/
    12	#define UART_MCR    (UART+0x04) /* MODEN控制寄存器*/
    13	#define UART_LSR    (UART+0x05) /* 线路状态寄存器*/
    14	#define UART_MSR    (UART+0x06) /* MODEN状态寄存器*/
    15	
    16	#define UART_DLL (UART+0x00)  /*预分频寄存器低8位*/
    17	#define UART_DLM (UART+0x01)  /*预分频寄存器高8位*/
    18	
    19	#define UART_LSR_ERROR   0x80  /* 出错 */
    20	#define UART_LSR_EMPTY    0x40  /* 传输FIFO和移位寄存器为空 */
    21	#define UART_LSR_TFE	    0x20  /* 传输FIFO为空 */
    22	#define UART_LSR_BI	    0x10  /* 传输被打断 */
    23	#define UART_LSR_FE	    0x08  /* 接收到没有停止位的帧 */
    24	#define UART_LSR_PE	    0x04  /* 奇偶校验错误位 */
    25	#define UART_LSR_OE	    0x02  /* 数据溢出 */
    26	#define UART_LSR_DR	    0x01  /* FIFO有数据 */
```


01、上述代码调用了串口打印了 Welcome RISC-V 语句。接下来实现简单的串口驱动代码，QEMU使用兼容 16550 规范的串口控制器。首先我们找到QEMU Virt地址空间中，串口的基地址为 0x10000000，大小为0x100，即256字节。然后在这256字节的范围内，继续划分了空间，比如寄存器空间，如上面头文件 asm/uart.h 所示，从寄存器地址排布看，每个寄存器只占用了1个字节的空间。而且还有复用寄存器，预分频寄存器。我们分析其代码需要结合16650相关的数据手册来分析，才能知其所以然。浏览器搜索: 16550 uart datasheet 即可搜到类似的数据手册。

02、复用寄存器通过某种方式进行切换，比如这里的串口，通过 UART_LCR 这个寄存器来进行切换，如下代码，直接往第7位即最高位写1，表示 0x00 和 0x01 此时是预分频寄存器，这时候再往 0x00,0x01 写入数据，就是在访问预分频相关的寄存器了。

参考笨叔的初始化代码，来间接理和梳理初始化流程。
```cpp
//riscv_programming_practice/chapter_2/benos/src/uart.c
    20	static unsigned int uart16550_clock = 1843200;   // a common base clock
    21	#define UART_DEFAULT_BAUD  115200
    22	
    23	void uart_init(void)
    24	{
    25		unsigned int divisor = uart16550_clock / (16 * UART_DEFAULT_BAUD);
    26	
    27		/* disable interrupt */
    28		writeb(0, UART_IER);
    29	
    30		/* Enable DLAB (set baud rate divisor)*/
    31		writeb(0x80, UART_LCR);
    32		writeb((unsigned char)divisor, UART_DLL);
    33		writeb((unsigned char)(divisor >> 8), UART_DLM);
    34	
    35		/*8 bits, no parity, one stop bit*/
    36		writeb(0x3, UART_LCR);
    37	
    38		/* 使能FIFO，清空FIFO，设置14字节threshold*/
    39		writeb(0xc7, UART_FCR);
    40	}
```


```cpp
//riscv_programming_practice/chapter_2/benos/src/uart.c
     4	void uart_send(char c)
     5	{
     6		while((readb(UART_LSR) & UART_LSR_EMPTY) == 0)
     7			;
     8	
     9		writeb(c, UART_DAT);
    10	}
    11	
    12	void uart_send_string(char *str)
    13	{
    14		int i;
    15	
    16		for (i = 0; str[i] != '\0'; i++)
    17			uart_send((char) str[i]);
    18	}
```


# Payload组成原理

- 不带Payload的文件，SBI和BenOS是分开的，即各自有各自的镜像文件（ELF、bin）。
- Payload的bin文件以及ELF文件，就相当于把SBI和BenOS做成一个镜像文件了。
- 下面是和Payload相关的源文件清单:
  - [[#20250227093300sbi_linker_payload_dot_ld]] —— 最主要的就是如何把SBI和OS两个系统合并成一个。
  - [[#20250227093300sbi_payload_dot_s]] —— 直接链接其bin文件，bin文件就是CPU直接可执行的文件。
  - [[#20250227093300MakefilePayload]] —— 可以得知如何利用链接器脚本最终构造出完整的合并文件。

---

<a id="20250227093300sbi_linker_payload_dot_ld"></a>

- 下面是完整源代码: sbi_linker_payload.ld

```cpp
OUTPUT_ARCH(riscv)
ENTRY(_start)

SECTIONS
{
	INCLUDE "sbi/sbi_base.ld"

	. = 0x80200000;
	
	.payload :
	{
		PROVIDE(_payload_start = .);
		*(.payload)
		. = ALIGN(8);
		PROVIDE(_payload_end = .);
	}

}
```

---

<a id="20250227093300sbi_payload_dot_s"></a>

- sbi_payload.S
```cpp
	.section .payload, "ax", %progbits
	.globl payload_bin
payload_bin:
	.incbin	"benos.bin"
```

---

<a id="20250227093300MakefilePayload"></a>

- Makefile局部
```makefile
benos_payload.bin: $(SBI_SRC_DIR)/sbi_linker_payload.ld $(SBI_OBJ_FILES) $(OBJ_FILES)
	$(CMD_PREFIX)$(GNU)-ld -T $(SBI_SRC_DIR)/sbi_linker_payload.ld -o $(SBI_BUILD_DIR)/benos_payload.elf  \
		$(SBI_OBJ_FILES) -Map benos_payload.map; \
		echo " LD $(SBI_BUILD_DIR)/benos_payload.elf"
	$(CMD_PREFIX)$(GNU)-objcopy $(SBI_BUILD_DIR)/benos_payload.elf -O binary benos_payload.bin; \
		echo " OBJCOPY benos_payload.bin"
	$(CMD_PREFIX)cp $(SBI_BUILD_DIR)/benos_payload.elf benos_payload.elf
```


# RISC-V GNU内嵌汇编

![[image20250221220900.png]]







# SBI学习笔记





# 大大大大大大大大大大大大分界线










# RISC-V架构基础


## 1、ISA与微架构

![[20230803102043.png]]

- 流水线性能指标：
  - 程序执行时间=总指令数 x 每个指令所需时钟周期 x 每个时钟周期所需时间.
  - CPI ：Cycles Per Instruction (单个指令执行所需周期数)
  - 指令提交：标志着该指令的整个执行生命周期结束.
- 处理器相关的概念
  - 流水线、超标量：苹果传递模型
  - 寄存器重命名、指令重排序ROB：商场购物模型
  - Cache高速缓存：统计表模型（高速缓存与一致性）
- RISC-V能够火起来的原因：
  - 1、开源和免费（BSD开源协议）
  - 2、设计简洁，集成了MIPS的优点和风格
  - 3、模块化设计（最小的指令集可以实现软件栈）
  - 4、丰富的软件生态


## 2、指令集支持


https://zhuanlan.zhihu.com/p/577987327

ISA(Instruction Set Architecture)

RISC-V指令集=<基本指令集> + [扩展指令集]  (注:尖括号表示必选, 方括号表示可选)

基础指令集：I、E
扩展指令集：A、B、C、D、F、...

指令编码：就是ISA设计者定义每条指令的每个位域.
```bash
root:~# cat /proc/cpuinfo
processor       : 0
hart            : 0
isa             : rv64imafdcsu  ---> (imafdcsu)
mmu             : sv48
```

根据上述cpuinfo查询到的信息，通过 isa 这个属性，即当前CPU支持的ISA详细信息：
```txt
- I：RV64I基础整型指令
- M：乘除法、取模求余指令
- F：单精度浮点指令
- D：双精度浮点指令
- Q：四倍浮点指令
- A：原子操作指令，例如常见的cas（compare and swap）指令
- C：压缩指令，主要用于改善程序大小
- G：= I+M+A+D+F，表示通用处理器所包含的指令集
- B：位操作指令集
- K：密码运算指令集
- H：虚拟化扩展指令
- 其他可参考：RISC-V官方手册
```

疑问：这些各种指令集，需要记住这些分类嘛？对于软件人员，有什么用？
解答：可以根据其支持的指令集所携带的功能，大致评估这款芯片的业务能力范围。


## 3、处理器模式

1、RV软件系统三个层次：SBI固件 —— 操作系统 —— 应用程序
2、处理器模式(没有使能虚拟化扩展)：M模式、S模式、U模式、HS模式、VS模式、VU模式.
2、处理器模式(使能了虚拟化扩展)：M模式、HS模式((VS模式、VU模式), U模式)
3、H(Hypervisor) Hypervisor 是一种**运行在物理服务器和操作系统之间的中间软件层**（可以是软件程序，也可以是固件程序），可允许多个操作系统和应用共享一套基础物理硬件
3、SBI —— Supervisor Binary Interface （ OpenSBI ）

在ARM中称为处理器模式，而在RV中称为特权架构。RISC-V总共有四种模式，分别是U、S、H和M模式。H模式是用作虚拟化，但是目前RISC-V对虚拟化还不太完善，基本不支持。因此，有人经常将RISC-V的模式说成三种U、S和M。以RISC-V Linux为例，Linux应用程序处于U模式，Linux内核/uboot处于S模式，M模式则是OpenSBI。M模式拥有最高访问权限，Linux内核如果要访问CSR寄存器，则必须由S模式切换到M模式，由OpenSBI读取CSR寄存器，然后将数据返回给内核。


## 4、通用寄存器

- 32bit/64bit RISC-V provides 32 general-purpose integer registers: ```x0 ~ x31```
- 32bit/64bit RISC-V provides 32 floating-point general purpose registers: ```f0 ~ f31```
- In RISC-V assembly, ABI names are employed to represent these registers (such as sp, ra, etc.). 

```txt
name ----------- ABI aliase --- Describe
x0               zero           A register with a constant value of 0
x1               ra             return address of function
x2               sp             stack pointer
x3               gp             global pointer
x4               tp             thread pointer
x10~x17          a0~a7          arguments of function
x8~x9,x18~x27    s0~s11         caller env save
x5~x7,x28~x31    t0~t6          temporary regs
```


## 5、系统寄存器

- **CSR** --- Control and Status Registers
- In RISC-V, CSR registers require specific instructions such as **csrr**, **csrw**, and **csrrw** to be accessed. RISC-V's CSR registers have their own registers in M mode and S mode, but they are mostly the same.
- In the encoding of CSR instructions, the encoding space of the **upper 12-bit field** is reserved for indexing system registers. The 12-bit CSR encoding space and its grouping are as follows:
  - **bit[11:10]** >>> The read-write attributes of the system registers are such that 0b11 represents read-only, while others denote read and write.
  - **bit[9:8]** >>> Processor modes, 0b00 = U mode, 0b01 = S mode, 0b11 = M mode, 0b10 = HS/VS mode.
- The following access operations will trigger an illegal instruction exception:
  - Accessing non-existent or unimplemented system registers.
  - Try modifying system registers that only have read-only attributes.
  - Accessing the system registers of high-level processor modes in low-level processor modes.  


## 6、处理器异常

mcause 寄存器异常码
用于保存发生中断或异常的情况. 中断和异常描述如下：1代表中断，0代表异常，每个异常/中断都有对应的编码值，通过mcause的值，可以很清楚的知道发生了什么中断或异常，特别在调试过程，`mcause`发挥了很大作用。
https://zhuanlan.zhihu.com/p/577987327

```txt
Intr? --- Exception Code --- Description
1 ------        1        --- Supervisor software interrupt
1 ------        3        --- Machine software interrupt
-----------------------------------------------------------
1 ------        5        --- Supervisor timer interrupt
1 ------        7        --- Machine timer interrupt
-----------------------------------------------------------
1 ------        9        --- Supervisor external interrupt
1 ------       11        --- Machine external interrupt
-----------------------------------------------------------
1 ------     >=16        --- Designated for platform use
-----------------------------------------------------------
0 ------        0        --- Instruction address misaligned
0 ------        1        --- Instruction access fault
0 ------        2        --- illegal instruction
0 ------        3        --- breakpoint
0 ------        4        --- load address misaligned
0 ------        5        --- load access fault
0 ------        6        --- store/AMO address misaligned
0 ------        7        --- store/AMO access fault
0 ------        8        --- environment call from u-mode
0 ------        9        --- environment call from s-mode
0 ------       11        --- environment call from m-mode
0 ------       12        --- instruction page fault
0 ------       13        --- load page fault
0 ------       15        --- store/AMO page fault
0 ------    24~31        --- Designated for custom use
0 ------    48~63        --- Designated for custom use
```




# RISC-V汇编基础

## 汇编：指令编码分类

为了方便RTL设计，指令编码还分类了，并且在指令编码中，即各个位域可能对于汇编器来说非常混乱，但是其能够更方便RTL设计，所以后面见到类似的奇怪位域布局，不要惊讶，这是正常的。

```txt
R-Type —— 寄存器与寄存器算术指令
I-Type —— 寄存器与立即数算术指令或加载指令.
S-Type —— 存储类指令
J-Type —— 无条件跳转类指令
B-Type —— 条件跳转类指令
U-Type —— 长立即数操作指令
```

疑问：这些分类对于软件人员来说，有什么作用？


## 汇编：立即数分类

下面是RISC-V架构中，指令编码里关于立即数参数的分类：
```txt
I-immediate ------ 12位有符号数
S-immediate ------ 12位有符号数
B-immediate ------ 13位有符号数
U-immediate ------ 32位有符号数
J-immediate ------ 21位有符号数
```

原码反码补码：正数的补码还是正数。
负数的计算机表达是：绝对值的原码(十六进制数)——取反——+1——乘以-1(十进制数)

汇编器解析立即数是按照处理器的位宽来解析的，比如在 RV64 中，你想表达 -2048 (0x800) ，则写立即数时你必须写成 -2048 或者 0xfffffffffffff800：
```cpp
// RV64 asm code:
li    t0, 0
addi  t1, t0, -2048
addi  t2, t0, 0xfffffffffffff800

//gdb debug info:
(gdb) n
(gdb) info registers t0 t1 t2
t0             0x0      0
t1             0xfffffffffffff800       -2048
t2             0xfffffffffffff800       -2048
```


## 汇编：伪指令

伪指令是汇编器提供的指令，而不是CPU指令集提供的指令。伪指令可以简单理解基于ISA指令，把几条ISA指令进一步封装成一条更大的指令，以方便程序员使用。这种封装一般由汇编器开发者封装，不属于ISA指令，属于伪指令范围。


## 汇编：PC相对寻址AUIPC

RISC-V目前只提供PC相对寻址AUIPC指令，也就是说不提供PC寄存器(你无法直接访问PC寄存器).
AUIPC ( Add Upper Immediate to PC )

AUIPC能寻址的范围为基于当前PC值偏移[-2GB,  +2GB]：
```cpp
	auipc  a5, 0x2     //a5=pc + signed(0x2 << 12)==pc+0x2000
	auipc  a5, 0xFFFFF //a5=pc + signed(imm << 12)
```

下面是单步调试实验代码运行效果：
```cpp
.globl asm_debug
asm_debug:
	auipc	t0, 0x0 //pc=0x80200208,t0=x
	auipc	t1, 0x0 //pc=0x8020020c,t0=0x80200208
	auipc	t2, 0x0 //pc=0x80200210,t1=0x8020020c
	ret             //pc=0x80200214,t2=0x80200210
```

由上述实验现象得知，当PC指针指向t0语句时，此时PC值是 0x80200208，由于PC值是即将执行的位置，所以此时并没有执行t0语句，当PC指向下一条语句时，t0语句已经执行完了，此时t0寄存器存入的就是t0所在地址。因此可以直观看出，auipc就是它所在当前语句的PC值存入rd寄存器。


```cpp
.globl asm_debug
asm_debug:
	auipc   a0,0
	auipc   a1,0
	auipc   a2,0
	auipc   a3,0
	jr      ra

//(gdb) info registers a0 a1 a2 a3
//a0             0x802002fc       2149581564
//a1             0x80200300       2149581568
//a2             0x80200304       2149581572
//a3             0x80200308       2149581576
```


下面的调试记录可以看出，被调用函数 asm_debug 和代码段入口函数 start 在地址上没有必然的联系。
```cpp
.global _start
_start:
	call asm_debug

.global asm_debug
asm_debug:
	mv      t0, ra
	ret

(gdb) b asm_debug
Breakpoint 1 at 0x80200218: file src/asm_test.S, line 3.
(gdb) c
Breakpoint 1, asm_debug () at src/asm_test.S:3
(gdb) info registers pc ra
pc             0x80200218       0x80200218 <asm_debug>
ra             0x80200004       0x80200004 <_start+4>
```


## 实例：立即数加载指令

探究 li 指令和 lui 指令的区别：
```cpp
li   a0, 0x80200004 //a0=0x80200004
lui  a0, 0x80200004 //Error: lui expression not in range 0..1048575(20bits)
lui  a0, 0x80204    //a0=0xffffffff80204000 (t0 = 0x80204 << 12; sext.dw t0, t0)
lui  t0, 0xc0204    //t0=0xffffffffc0204000 (t0 = 0xc0204 << 12; sext.dw t0, t0)
```

如上实验结果所示，lui会根据目标立即数先移位，然后根据目标数的符号位进行符号扩展。比如上述 0x80204 ，lui 指令只取目标立即数 imm[19:0] 位，并且在第19位处的值是1，因此需要符号位扩展，即寄存器的剩余高位全部填充1。

下面是利用 https://godbolt.org/ 来探究立即数加载指令的：
```cpp
	//long data1 = -2048;
	li      a5,-2048
	sd      a5,-24(s0)

	//long data1 = 2048;
	li      a5,4096
	addi    a5,a5,-2048
	sd      a5,-32(s0)

(gdb) x/4xw 0x80003fa0 //0x80003fa0 is -32(s0)
0x80003fa0:     0x00000800      0x00000000      0xfffff800      0xffffffff
//               -32(s0)                         -24(s0)
```


## 汇编：内存访问指令

load指令格式： 
b —— (byte)单字节，h —— (half-word)两字节，w —— (word)4字节，d —— (dw)8字节
```cpp
l{d|w|h|b}{u}  rd, offset(rs1) //offset[11:0] (-2048 ~ 2047)
li  rd, imm  //rd = imm
lui rd, imm  //rd = ( (imm&0xFFFFF) << 12 )
```

下面是load指令的各种用法：
```cpp
li    t0, 0x80200000
lw    t1, 12(t0) //t1=0xffffffffff810113
lwu   t2, 12(t0) //t2=0xff810113
```

---

store指令格式： **```s{d|w|h|b}  rs2, offset(rs1)```**

不对齐访问：
（1）RV没有强制约定，选择权交给CPU设计者，要么RTL支持不对齐访问，要么抛出异常并由软件来处理.
（2）QEMU模拟器支持不对齐访问.

```cpp
li    t0, 0x80210000
li    t1, 0x1122 //half-word-positive
li    t2, 0x8765 //half-word-negative
sw    t1, 0(t0)  //word-store  (*0x80210000) == 0x00001122
sw    t2, 4(t0)  //word-store  (*0x80210004) == 0x00008765

li    t3, (0x8765 | 0xffff0000)
sw    t3, 8(t0)  //we need 0x8765 --> 0xffff8765

li    t4, 0xffff0000
or    t3, t3, t4
sw    t3, 8(t0)  //we need 0x8765 --> 0xffff8765
```

---

**符号位扩展**
如下实验结果所示，如果我们把内存里的单字节数据当成有符号数，那么一旦这个单字节有符号数是负数，在被加载到寄存器之后会进行符号扩展，即高位全为1。
```cpp
//在任意.S文件中编写代码
.global asm_debug
asm_debug:
li   a0, 0x80200004
lb   a1, -4(a0) // a1 == 0xffffffffffffffef (signed)
lbu  a2, -4(a0) // a2 == 0xef (unsigned)

//在 benos 内核源码目录中修改 boot.S 来调用目标程序：
.globl _start
_start:
	call asm_debug
```

下面是利用GDB单步调试的调试记录：
```cpp
(gdb) target remote localhost:1234
Remote debugging using localhost:1234
0x0000000000001000 in ?? ()
(gdb) b asm_debug
Breakpoint 1 at 0x802001a8: file src/asm_test.S, line 4.
(gdb) c
Breakpoint 1, asm_debug () at src/asm_test.S:4
(gdb) x/8xb 0x80200000  //8表示展示8个数,x表示以16进制,b表示每个数宽度为字节
0x80200000 <_start>:    0xef    0x00    0x80    0x1a    0x73    0x10    0x40    0x10
(gdb) s (sss...)
(gdb) info reg a0 a1 a2 a3 a4
a0             0x80200004       2149580804
a1             0xffffffffffffffef       -17 //单字节的0xEF是负数,所以高位全1.
a2             0xef     239 //由于当成无符号载入,所以无需高位全1.
a3             0x73     115 //单字节的0x73不是负数,所以无需高位全1.
a4             0x73     115 //单字节的0x73不是负数,所以无需高位全1.
(gdb) 
```


使用不同规格往内存里写入负数实验效果：
```cpp
	li     t0, 0x80210000
	li     t1, -2
	sh     t1, 0(t0)   //2Bytes
	sw     t1, 8(t0)   //4Bytes
	sd     t1, 16(t0)  //8Bytes

(gdb) info registers t0 t1
t0             0x80210000       2149646336
t1             0xfffffffffffffffe       -2
(gdb) x/8xw 0x80210000
0x80210000:     0x0000fffe      0x00000000      0xfffffffe      0x00000000
0x80210010:     0xfffffffe      0xffffffff      0x00000000      0x00000000
```


## 汇编：移位指令

```
sll --- shift left logic       逻辑左移，最高位被丢弃，最低位补0.
srl --- shift right logic      逻辑右移，最低位被丢弃，最高位补0.
sra --- shift right arithmetic 算术右移，最低位会被丢弃，最高位会按照符号进行扩展.
```

格式如下：```sll    rd, rs1, rs2 // rd=rs1 << rs2[5:0]``` 

下面是小于32位的左移C代码反汇编效果：
```cpp
//sll    rd, rs1, rs2 // rd=rs1 << rs2[5:0]
	int data = 0;
	int bits = 16;
	data = 1<<bits;

//上述代码的反汇编:
	int data = 0;
   8:	00012623          	sw	zero,12(sp)
	int bits = 16;
   c:	01000793          	li	a5,16
  10:	00f12423          	sw	a5,8(sp)
	data = 1<<bits;
  14:	00812783          	lw	a5,8(sp)
  18:	00100713          	li	a4,1
  1c:	00f717bb          	sllw	a5,a4,a5  //<------区别位置
  20:	00f12623          	sw	a5,12(sp)
```

---

下面是大于等于32位的左移C代码反汇编效果：
```cpp
	unsigned long data = 0;
	int bits = 32;
	data = 1UL<<bits; // UL is important

//上述代码的反汇编:
	unsigned long data = 0;
   8:	00013423          	sd	zero,8(sp)
	int bits = 32;
   c:	02000793          	li	a5,32
  10:	00f12223          	sw	a5,4(sp)
	data = 1UL<<bits;
  14:	00412783          	lw	a5,4(sp)
  18:	00100713          	li	a4,1
  1c:	00f717b3          	sll	a5,a4,a5  //<------区别位置
  20:	00f13423          	sd	a5,8(sp)
```

---

下面是逻辑右移和算术右移的实验(没有带w后缀，表示根据寄存器长度来处理)：
```cpp
	li      t0, 0x8000008a00000000 //t0=0x8000008a00000000
	srai    a1, t0, 1 //a1=0xc000004500000000
	srli    a2, t0, 1 //a2=0x4000004500000000
```

---

下面是逻辑右移和算术右移的实验(带w后缀，表示只处理低32位)：
```cpp
0x12      8000 008a
0001 0010 1000 .... 1000 1010

          1100 .... 0100 0101 (sraiw) (w:只取低32位)
          0100 .... 0100 0101 (srliw) (w:只取低32位)
.... .... 0000 0001 0001 0100 (slliw) (w:只取低32位)

	li      t0, 0x128000008a //t0=0x128000008a
	sraiw   a1, t0, 1 //a1=0xffffffffc0000045
	srliw   a2, t0, 1 //a2=0x40000045
	slliw   a3, t0, 1 //a3=0x114
```

如果第32位为0，则实验效果如下：
```cpp
0x12      4000 008a
0001 0010 0100 .... 1000 1010
0001 0010 0010 .... 0100 0101 (sraiw) 0x20000045
0001 0010 0010 .... 0100 0101 (srliw) 0x20000045
0001 0010 1000 .... 0001 0100 (slliw) 0xffffffff80000114

	li      t0, 0x124000008a //t0=0x124000008a
	sraiw   a1, t0, 1  //a1=0x20000045
	srliw   a2, t0, 1  //a2=0x20000045
	slliw   a3, t0, 1  //a3=0xffffffff80000114
```

如果第32位为1，则实验效果如下：
```cpp
//sll    rd, rs1, rs2 // rd=rs1 << rs2[5:0]

0x13      4000008a   (0x13位域冻结不变)
0001 0011 0100 .... 1000 1010
0001 0011 0010 .... 0100 0101 (sraiw) 0x20000045
0001 0011 0010 .... 0100 0101 (srliw) 0x20000045
0001 0011 1000 .... 0001 0100 (slliw) 0xffffffff80000114

	li      t0, 0x134000008a //t0=0x134000008a
	sraiw   a1, t0, 1  //a1=0x20000045
	srliw   a2, t0, 1  //a2=0x20000045
	slliw   a3, t0, 1  //a3=0xffffffff80000114
```

从上述多个实验结果中可看到，slliw带了w后缀，表示只处理rs1数据低32位，如下图所示：
![[20230804103312.png]]


## 汇编：位操作指令

基于寄存器的位操作指令：
```cpp
and  rd, rs1, rs2 // rd = rs1 & rs2
or   rd, rs1, rs2 // rd = rs1 | rs2
xor  rd, rs1, rs2 // rd = rs1 ^ rs2
```

下面是位操作实验演示：
```cpp
	li    t0, 0x8000000000000000
	li    t1, 0x4000000000000000
	or    t2, t1, t0 //t2=0xc000000000000000
	and   t3, t1, t0 //t3=0x0
	xor   t4, t1, t0 //t4=0xc000000000000000
```

---

基于立即数的位操作指令：
```cpp
xori  rd, rs1, imm // rd = rs1 ^ imm   ( signed(imm[11:0]) )
 ori  rd, rs1, imm // rd = rs1 | imm   ( signed(imm[11:0]) )
andi  rd, rs1, imm // rd = rs1 & imm   ( signed(imm[11:0]) )
```

下面是立即数的位操作：
```cpp
	li    t1, 0x4000000000000000
	ori   t2, t1, -2048
(gdb) info registers t1 t2
t1             0x4000000000000000       4611686018427387904
t2             0xfffffffffffff800       -2048

	li    t1, 0x4000000000000000
	ori   t2, t1, 0x7FF
t1             0x4000000000000000       4611686018427387904
t2             0x40000000000007ff       4611686018427389951
```

异或：相异为1，相同为0；以下是关于异或的妙用.
（1）交换两个数，a=0001, b=0110 —— a=a^b; b=b^a; a=a^b
（2）寄存器清零：xor  x1, x1
（3）判断两个数是否相等：```( (a^b) == 0 )```


## 汇编：算术运算指令

```cpp
add  rd, rs1, rs2 // rd = rs1 + rs2
sub  rd, rs1, rs2 // rd = rs1 - rs2

addi   rd, rs1, imm // rd = rs1 + imm
addiw  rd, rs1, imm // rd = rs1 + imm
addw   rd, rs1, rs2 // rd = rs1 + rs2
subw   rd, rs1, rs2 // rd = rs1 + rs2
```

例子：下面哪一条是非法指令？（答案是第一条）
```cpp
addi  a1, t0, 0x800
addi  a1, t0, 0xFFFFFFFFFFFFF800
//开发者其实想传递 2048 这个值
```


## 汇编：立即数范围(恶心)

addi，xori等指令这种立即数版本的指令，它的imm是**12位有符号数**：
```cpp
	add   t3, zero, zero
	ori   a0, t3, 0x7ff //a0=0x7ff    2047
	ori   t4, t3, 0x800 //illegal operands `ori t4,t3,0x800'
	ori   a2, t3, -32   //a2=0xffffffffffffffe0  -32
	ori   a3, t3, -64   //a3=0xffffffffffffffc0  -64
	ori   a4, t3, -128  //a4=0xffffffffffffff80  -128
	ori   a5, t3, -256  //a5=0xffffffffffffff00  -256
	ori   a6, t3, -512  //a6=0xfffffffffffffe00  -512
	ori   a7, t3, -1024 //a7=0xfffffffffffffc00  -1024
	ori   t5, t3, -2048 //t5=0xfffffffffffff800  -2048
```

下面是C代码编译成.o文件之后，接着反汇编得到的汇编代码：
```cpp
//C代码
int data1 = 0x10000000;
int data2 = 0x80101016;
int data3 = data1 | data2;

//反汇编代码
lui     a5,0x10000 //a5= (0x10000<<12) == 0x10000000
sw      a5,12(sp)

lui     a5,0x80101 //a5= (0x80101<<12) == 0x80101000
addiw   a5,a5,22   //a5=a5+22=0x80101016
sw      a5,8(sp)

lw  a4,12(sp)
lw  a5,8(sp)
or  a5,a4,a5       //data1 | data2
sw  a5,4(sp)
```



## 汇编：比较指令(恶心)

```cpp
slt   rd, rs1, rs2 //rd=(rs1 < rs2)? 1:0;//rs1,rs2为有符号
sltu  rd, rs1, rs2 //rd=(rs1 < rs2)? 1:0;//rs1,rs2为无符号
slti  rd, rs1, imm //rd=(rs1 < imm)? 1:0;//rs1为有符号,imm为12位有符号数
sltiu rd, rs1, imm //rd=(rs1 < imm)? 1:0;//rs1为无符号,imm为12位有符号数

//比较伪指令
sltz   rd, rs1 //rd=(rs1<0)? 1:0;
snez   rd, rs1 //rd=(rs1 != 0)? 1:0;
seqz   rd, rs1 //rd=(rs1 == 0)? 1:0;
sgtz   rd, rs1 //rd=(rs1 > 0)? 1:0;
```

下面是与零值比较：
```cpp
seq   a0, t0, zero //rd= (t0 == zero?) 1:0;
seqz  a1, t0
```



## 实例：定义全局变量

下面是在 https://godbolt.org/ 函数外面定义了全局变量，然后转换成 RV64 汇编代码如下：
```cpp
//code of language C
long data1 = -2048;
long data2 = 2048;

//code of language RV64 asm
data1:
	.dword  -2048
data2:
	.dword  2048
```


## 实例：函数调用汇编

C语言转换成汇编代码（在线）：https://godbolt.org/

通过上述网站，可以编写如下一段C代码，并转换成右边窗口的汇编，经过实验验证，这段汇编是可以直接贴到.S文件里编译运行的。从这段汇编代码可以学到函数栈帧的知识，以及汇编级函数跳转和函数返回的知识。并且这些都没有用到AUIPC这种相对寻址，都是用到比较通用的简单的汇编指令达到函数层层调用和返回的功能。

```cpp
int mult(int a, int b)
{
    return (a*b);
}

int sum(int a, int b)
{
    return mult(a, b) + b;
}

int main(int argc, const char *argv[])
{
    int a = 0;
    a = sum(10, 20);//220
    return 0;
}
```

下面的代码是上面C代码转换后的汇编代码：从mult开始分析，从上至下分析代码，并且结合注释分析代码，从中能学到函数栈帧的构造，以及函数的调用和返回机制，并对栈帧相关寄存器进一步了解。
```cpp
//int mult(int a, int b);
mult:
		//push (s0 is frame pointer)
        addi    sp,sp,-32
        sd      fp,24(sp)  //sp(24)=s0 (save prev fp)
        addi    s0,sp,32   //s0=sp(32) (set cur fp)
        sw      a0,-20(s0) //s0(-20) = a0 (save args)
        sw      a1,-24(s0) //s0(-24) = a1 (save args)

		//return (a*b);
        lw      a4,-20(s0) //a4 = fp(-20)
        lw      a5,-24(s0) //a5 = fp(-24)
        mulw    a5,a4,a5   //a5 = a4 * a5
        sext.w  a5,a5      //a5 = (int)a5

		//pop
        mv      a0,a5      //a0 = a5 (return value)
        ld      s0,24(sp)  //s0 = sp(24) (restore fp)
        addi    sp,sp,32   //sp = sp + 32
        jr      ra         //ra is return address register

//int sum(int a, int b);
sum:
		//push
        addi    sp,sp,-32
        sd      ra,24(sp)  //sp(24) = ra (save prev ra)
        sd      s0,16(sp)  //sp(16) = s0 (save prev fp)
        addi    s0,sp,32   //fp = sp+32  (set cur fp)
        sw      a0,-20(s0) //fp(-20) = a0
        sw      a1,-24(s0) //fp(-24) = a1

		//return mult(a, b) + b;
        lw      a4,-24(s0)
        lw      a5,-20(s0)
        mv      a1,a4
        mv      a0,a5
        call    mult
        mv      a5,a0      //get return value of mult(a,b)
        mv      a4,a5
        lw      a5,-24(s0)
        addw    a5,a5,a4   //a5 = a5 + a4
        sext.w  a5,a5      //a5 = (int)a5

		//pop
        mv      a0,a5      //a0 is return value
        ld      ra,24(sp)  //restore prev ra
        ld      s0,16(sp)  //restore prev fp
        addi    sp,sp,32   //restore prev sp
        jr      ra         //jump to [ra] (function caller)

.globl asm_debug
asm_debug:
		//push
        addi    sp,sp,-48
        sd      ra,40(sp)
        sd      s0,32(sp)
        addi    s0,sp,48
        mv      a5,a0
        sd      a1,-48(s0)
        sw      a5,-36(s0)

		//int a = 0;
        sw      zero,-20(s0)

		//a = sum(10, 20);//220
        li      a1,20
        li      a0,10
        call    sum
        mv      a5,a0
        sw      a5,-20(s0)

		//return 0;
        li      a5,0
        mv      a0,a5
        ld      ra,40(sp)
        ld      s0,32(sp)
        addi    sp,sp,48
        jr      ra
```


## 实例：分支跳转汇编

C语言转换成汇编代码（在线）：https://godbolt.org/

C代码范例：
```cpp
int num_add(int a, int b) { return (a+b); }
int num_sub(int a, int b) { return (a-b); }

int num_op(int op, int a, int b)
{
    int ret = -1;
    switch(op)
    {
        case 0:
            ret = num_add(a, b);
            break;
        case 1:
            ret = num_sub(a, b);
            break;
        default:
            ret = -1;
            break;
    }
}
```

上述C代码转换的汇编代码如下：
```cpp
num_add:
        addi    sp,sp,-32  //set cur sp
        sd      s0,24(sp)  //save prev fp
        addi    s0,sp,32   //set cur fp
        sw      a0,-20(s0) //save arg 0
        sw      a1,-24(s0) //save arg 1
        lw      a4,-20(s0)
        lw      a5,-24(s0)
        addw    a5,a4,a5   //a5 = a4 + a5
        sext.w  a5,a5      //a5 = (int)a5
        mv      a0,a5      //set ret value
        ld      s0,24(sp)  //restore prev fp
        addi    sp,sp,32   //restore prev sp
        jr      ra         //jump to [ra]
num_sub:
        addi    sp,sp,-32
        sd      s0,24(sp)
        addi    s0,sp,32
        mv      a5,a0
        mv      a4,a1
        sw      a5,-20(s0)
        mv      a5,a4
        sw      a5,-24(s0)
        lw      a4,-20(s0)
        lw      a5,-24(s0)
        subw    a5,a4,a5
        sext.w  a5,a5
        mv      a0,a5
        ld      s0,24(sp)
        addi    sp,sp,32
        jr      ra
num_op:
        addi    sp,sp,-48  //set cur sp
        sd      ra,40(sp)  //save prev ra
        sd      s0,32(sp)  //save prev fp
        addi    s0,sp,48   //set cur fp
        sw      a0,-36(s0) //save arg 0
        sw      a1,-40(s0) //save arg 1
        sw      a2,-44(s0) //save arg 2
        li      a5,-1
        sw      a5,-20(s0) //int ret = -1;
        lw      a5,-36(s0)
        sext.w  a5,a5
        beq     a5,zero,.L6 //case arg0==0, b to .L6
        lw      a5,-36(s0)
        sext.w  a4,a5
        li      a5,1
        beq     a4,a5,.L7   //case arg0==1, b to .L7
        j       .L10        //default
.L6:
        lw      a1,-44(s0)
        lw      a0,-40(s0)
        call    num_add
        mv      a5,a0
        sw      a5,-20(s0)
        j       .L9
.L7:
        lw      a4,-44(s0)
        lw      a5,-40(s0)
        mv      a1,a4
        mv      a0,a5
        call    num_sub
        mv      a5,a0
        sw      a5,-20(s0)
        j       .L9
.L10:
        li      a5,-1
        sw      a5,-20(s0)
        nop
.L9:
        nop
        mv      a0,a5
        ld      ra,40(sp)
        ld      s0,32(sp)
        addi    sp,sp,48
        jr      ra

.globl asm_debug
asm_debug:
		//push
        addi    sp,sp,-48
        sd      ra,40(sp)
        sd      s0,32(sp)
        addi    s0,sp,48
        mv      a5,a0
        sd      a1,-48(s0)
        sw      a5,-36(s0)

		//int a = 0;
        sw      zero,-20(s0)

		//a = sum(10, 20);//220
        li      a1,20
        li      a0,10
        call    sum
        mv      a5,a0
        sw      a5,-20(s0)

		//return 0;
        li      a5,0
        mv      a0,a5
        ld      ra,40(sp)
        ld      s0,32(sp)
        addi    sp,sp,48
        jr      ra
```

从上述汇编指令范例我们可以学到，关于跳转，这几个指令都是跳转的意思。比如什么时候用 j ，什么时候用 jr ，什么时候用 call ，什么时候用bxx ，等等。通过上述汇编代码，我们能知道这几个跳转指令的具体用途。


## 实例：CSR寄存器读写

课程位置：第4季5 RISC-V指令集 par8
指令全称：CSR (Current Status Register 存放处理器当前状态的寄存器)
指令清单：csrrw 、csrrs 、csrrc、csrrwi 、csrrsi 、csrrci 
指令格式：
```cpp
csrrw    rd, csr, rs1 //rd=csr; csr  = rs1   (write value)
csrrs    rd, csr, rs1 //rd=csr; csr |= rs1   (set bits)
csrrc    rd, csr, rs1 //rd=csr; csr &= ~rs1  (clear bits)

csrrwi   rd, csr, imm[4:0]
csrrsi   rd, csr, imm[4:0]
csrrci   rd, csr, imm[4:0]
```

下面我们通过实例来获取处理器当前所在模式：
```cpp
// RV64 asm code:
.global asm_debug
asm_debug:
	csrrsi   a0, sscratch, 2
    csrrsi   a1, sscratch, 0
	jr       ra  //func returns

.globl _start
_start:
	call asm_debug

// GDB step debug info:
(gdb) info registers a0 a1
a0             0x0      0
a1             0x2      2
```

需要注意的是，如果是在S模式下访问mstatus，则当gdb单步正式执行到该语句时，即PC指向下一条语句时，会出现卡死现象. 因此得知S模式无法访问M模式的寄存器。


## 实例：ret指令陷阱

执行call指令后，CPU会修改ra指令来保存当前+4位置的地址；执行 ret 指令之后，CPU会读取 ra 寄存器，ra 寄存器等同于 LR 寄存器，保存着调用点下一个指令的地址。但是如果函数层层调用，则 ra 寄存器的值会被覆盖，上上层的地址位置信息会被丢失。为了解决这个问题，需要用栈来临时保存 ra 寄存器的值。

验证方法：
（1）执行 call 之前，查看 ra 寄存器的值
（2）执行 call 之后，即进入子函数之后，查看 ra 寄存器的值，看是否变化了.
（3）结论是，一旦进入子函数，ra 寄存器的值就变了

下面是函数调用和返回方式：
```cpp
.text

func_aaa:
	mv    s1, ra //save ra
	//...
	mv    ra, s1 //restore ra
	ret
func_bbb:
	mv    s1, ra //save ra
	//...
	mv    ra, s1 //restore ra
	jr    ra

func_main:
	mv    s0, ra
	call  func_aaa
	call  func_bbb
	mv    ra, s0
	ret
```


## 实例：汇编实现串口打印

理论依据：
（1）串口控制器工作原理
（2）汇编基础

<font color=blue>XXX的工作原理</font>：指XXX。

通过现成的汇编代码来反向分析该串口工作流程。但是能够首先把现成的用起来，学会使用了，再来探究其内在原理。这样有助于摸清楚细节。

下面是通过笨方法，把字符一个一个打在某内存地址，然后再把地址传递给打印函数。
```cpp
//asm code:
        call    __init_uart
        li      a0, 0x80210000 //string ptr
        li      t0, 'h'
        li      t1, 'e'
        li      t2, 'l'
        li      t3, 'l'
        li      t4, 'o'
        li      t5, 0
        sb      t0, 0(a0)
        sb      t1, 1(a0)
        sb      t2, 2(a0)
        sb      t3, 3(a0)
        sb      t4, 4(a0)
        sb      t5, 5(a0)
        call    put_string_uart
```

下面的版本稍微先进一点了，可以很方便定义一个字符串常量，然后把常量所在地址传递给打印函数：
```cpp
.data    //data section
str_hello:
    .asciz "hello world!"

.text    //text section
.global asm_debug
asm_debug:
	//other code ...
	
    call    __init_uart
    la      a0, str_hello  //load label address into a0
    call    put_string_uart

	//other code ...
```


la指令是pseudo-instruction，是 Load Address 的缩写，语法如下：
```cpp
la  rd, label   //把label所在地址载入rd
```


串口发送字符、字符串的流程核心代码：
```cpp

.global put_uart
put_uart:
.loop:
	la t0, UART_LSR /* 线路状态寄存器*/
	lbu t1, (t0)

	andi	t1,t1, 0x40
	beqz t1, .loop  //如果未就绪,就一直轮询该寄存器

	la t0, UART_DAT /* 数据寄存器*/
	sb a0, (t0)     //直接把目标字符写入数据寄存器

	ret

.global put_string_uart
put_string_uart:
	/*此时SP栈空间还没分配，把返回地址ra保存到临时寄存器中*/
	mv s8, ra
	mv a5, a0

.loop1:
	lbu a0,(a5)
	beqz  a0, .L2 
	call put_uart
	addi a5,a5,1
	j .loop1
.L2:
	/*恢复返回地址ra*/
	mv ra, s8
	ret
```



## 实例：汇编与宏定义

```cpp
#define UART_IER (0x10000000 + 1)
la t0, UART_IER //load macro value into t0
```


## 指令集结尾

（1）重新设计的指令集: 简洁，干净，没有历史包袱，与微架构设计解耦
（2）指令集开源，采用BSD开源协议
（3）可扩展性: 允许用户自定义添加指令 (可变长指令编码、预留了足够扩展空间)
（4）模块化设计: 最小整数指令集集合 + 模块化扩展
（5）基金会负责规范review和发布


# RISC-V 函数调用规范


函数调用规范可以总结出如下规则：
（1）函数的前8个参数使用a0~a7寄存器来传递，如果函数参数大于8个，后面的参数使用栈来传递。
（2）如果传递的参数小于寄存器宽度 (64位) ，那么符号扩展到64位。
（3）如果传递的参数为2倍的寄存器宽度 (128位)，那么将使用一对寄存器来传递该参数。
（4）函数的返回参数保存到a0~a1寄存器中（return 6; //a0=6）。
（5）函数的返回地址保存在ra寄存器中（PC=fn_call_pos + 4）。
（6）如果子函数里使用s0~s11寄存器，那么子函数在使用前需要把这些寄存器的内容保存到栈中，使用完成之后再从栈中恢复内容到这些寄存器里。
（7）栈向下增长(向较低的地址)，栈指针寄存器SP在程序进入时要对齐到16字节边界上。
（8）传递给栈的第一个参数位于栈指针寄存器的偏移量0处，通过反汇编可以快速获知。
（9）如果GCC使用了 <font color=green>-fno-omit-frame-pointer</font> 编译选项，那么编译器使用s0作为栈顿指针FP。
（10）结构体位域 (bitfield) 按照小端来排布。它会填充到下一个整型类型(int32)对齐的地方。

```cpp
struct {
	int x:10; // x is bitfield[9:0]
	int y:12; // y is bitfield[21:10]
};

struct {
	short x:10; // x is bitfield[9:0]
	short y:12; // y is bitfield[27:16]
};
```

---

升栈/降栈、满栈/空栈

---

函数栈帧，RISC-V采用 <font color=red>"降栈 + 空栈"</font> ，关于采用空栈还是满栈的判断，还可以根据具体编译器编译之后，再经过反汇编，并通过反汇编代码中查看函数的调用代码，也能看出是采用满栈还是空栈。

```cpp
.globl asm_debug
asm_debug:
	addi  sp, sp, -32
	li    a5, 1
	sd    a5, 0(sp)
	li    a5, 2
	sd    a5, 8(sp)

	ld    a1, 0(sp)
	ld    a2, 8(sp)
```

这里还涉及到是否使用 FP ，其中不使用 FP 的优点是压栈或者出栈的时候，减少对内存的访问。GCC编译命令通过参数 -fomit-frame-pointer 来达到不使用FP的效果。如果使用 FP ，也是为了方便获知每个函数栈帧大小，以及方便调试的时候回溯栈帧。Part3

---

Part4
栈的回溯：操作系统常用的输出栈信息等技术手段底层都是通过栈帧指针FP来回溯整个栈。


## 是否使用FP

1、不使用FP，GCC使用 "-fomit-frame-pointer" 编译选项，这样在函数入栈出栈时减少访问内存的指令，从而提高程序的性能。
2、使用FP，GCC使用 "-fno-omit-frame-pointer" 编译选项，这样在调试过程中方便计算每个栈帧大小以便回溯。


## 栈回溯

1、OS常用的输出栈信息等技术手段就是通过FP完成的，通过栈的回溯技术输出函数调用关系.

```txt
Call Trace:
[<0x0000000080202edc>] test_access_unmap_address+0x1c/0x42
[<0x0000000080202f12>] test_mmu+0x10/0xla
[<0x000000008020329a>] kernel_main+0xb4/0xb6
```

2、下面通过一个示例分析如何通过 FP 回溯整个栈。
[例4-4]在例4-3 的基础上，输出每个栈的范围，以及调用该函数时的PC值，如下面的日志信息所示。
```txt
Call Frame:
[0x0000000080202fa0-0x0000000080202fb0] pc 0x0000000080200f32
[0x0000000080202fb0-0x0000000080202fd0] pc 0x000000008020114a
[0x0000000080202fd0-0x0000000080202ff0] pc 0x0000000080201184
[0x0000000080202ff0-0x0000000080203000] pc 0x00000000802011a4
```

3、如果想把 PC 值对应的符号名称(函数名称)显示出来，需要建立一个符号名称与地址的对应表，然后查表，本示例中，我们没有满足这个需求。不过，读者可以通过查看 benos.map 文件的符号表信息确定PC 值对应的函数名称。下面是实现栈回溯的示例代码。

![[20230831174543.png]]


## 实验：GDB观察栈布局


1、实验目的：熟悉RISC-V的栈布局.
2、实验要求：
（1）首先使能FP，即通过gcc编译选项 "fno-omit-frame-pointer"
（2）在benos里实现函数调用 kernel_main() >> func1() >> func2()，然后使用GDB观察栈的变化情况.


```cpp
int func2(int a, int b)
{
    return a+b;
}

int func1(void)
{
    int a = 1;
    int b = 2;
    return func2(a, b);
}

void kernel_main(void)
{
    int ret = 0;
    ret = func1();
}
```

根据GDB调试记录分析出，只要PC指针还在某函数内，对应的FP,SP值就固定不变，一旦函数跳转或者返回，跑到其他函数里了，则对应的FP,SP值就会跟着改变。下面是PC指针从函数main->func1->func2时的FP,SP值变化：
```cpp
//当PC指针在main函数内部时:
fp = 0x80202000
sp = 0x80201fe0

//当PC指针在func1内部时:
ra = 0x80200394
fp = 0x80201fe0
sp = 0x80201fc0

//此时fp-16处,就是对应的寄存器值
//fp-8 --> 0x00000000_80200394 --> curr_ra
//fp-16--> 0x00000000_80202000 --> prev_fp
//其中 prev_fp 就是上一个栈帧的FP值，curr_ra 则表示PC指针所在当前函数的ra值.
(gdb) info registers ra sp fp
ra             0x80200394       0x80200394 <kernel_main+24>
sp             0x80201fc0       0x80201fc0
fp             0x80201fe0       0x80201fe0
(gdb) x/8xw 0x80201fd0
0x80201fd0:     0x80202000      0x00000000      0x80200394      0x00000000
0x80201fe0:     0x00000000      0x00000000      0x00000000      0x00000000
```

实验总结：FP,SP寄存器只会存储当前栈帧信息. PREV栈帧信息会存放在当前栈帧内. 关于RV中函数栈布局的关键点如下：（1）降栈/升栈，采用了降栈；（2）空栈，即SP指向的位置可以直接写入新数据；（3）栈大小为16字节的倍数，因为栈至少要保存8(curr_ra) + 8(prev_fp) 字节的内容；（4）当前栈帧对应的函数返回时，需要从 curr_ra 处把值写入 ra 寄存器，然后调用 ret 指令，或者调用 jr ra指令。

## 实验：如何实现栈回溯

1、实验目的：熟悉RV的栈回溯
2、在benos里实现函数调用 kernel_main >> func1 >> func2，并实现一个栈回溯功能，输出栈的地址范围和大小，并通过 GDB 观察栈是如何回溯的。


```cpp
static void walk_stackframe(void)
{
	unsigned long pc,sp,fp,low;
	unsigned long curr_sp __asm__ ("sp");
	sp = curr_sp;
	fp = (unsigned long)__buildin_frame_address(0);
	pc = (unsigned long)walk_stackframe;

	while (1) {
		if (!kernel_text(curr_pc))
			break;

		//check fp's valid
		low = sp + 8 + 8;
		if ( (fp < low) || (fp & 0xf) ) {
			//如果fp还低于low了,或者 fp 不被8整除
			break;
		}

		if (kernel_text(pc))
			printk("sp:0x%016lx, fp:0x%016lx, pc:0x%016lx\n",sp,fp,pc);
		
		ra = *(fp-8); //伪代码:获取 curr_ra
		sp = fp; //sp = curr_fp
		fp = *(fp-16);//fp = prev_fp
		pc = (ulong)ra - 4;//获取调用点地址
	}
}

void dump_stack(void)
{
	printk("Call Frame:\n");
	walk_stackframe();
}
```










# RISC-V GNU AS汇编器

GCC AS 汇编器采用 AT&T 语法格式。

（1）预处理：<font color=green>gcc  -E  test.c -o test.i</font>
（2）编译： <font color=green>gcc  -S  test.i -o test.S</font>
（3）汇编： <font color=green>as test.S -o test.o</font>
（4）链接： <font color=green>ld -o test.elf test.o -lc</font>

ELF文件常见的各个段：
（ .symtab ）用来存放函数、全局变量的符号表信息.
（ .debug ）存放调试使用的符号表信息.


## 数字标签跳转

1、符号可以代表它所在的地址，也可以当作变量或者函数来使用.

下面是数字标签跳转代码的同等功能代码对比：
![[20230902225221.png]]


## 数据定义伪指令

```cpp
.byte, .hword or .short, .long or .int, .word, .quad, .float, .asciz, .rept and .endr, .equ
.equ: 给符号赋值
.asciz: 在字符串末尾自动插入'\0'字符.
```

rept and endr指令：
```cpp
.rept 3
.long 0
.endr

//等同于
.long 0
.long 0
.long 0
```


equ伪指令用例：
```cpp
.equ my_data1, 100
.equ my_data2, 200

.text
main:
	...
	li x1, =my_data1
	li x2, =my_data2
	add x3, x1, x2
```


## 实验：把某局部代码链接到指定段


```cpp
.pushsection ".my.text", "awx"
...
.popsection
```


## 实验：C语言调用汇编函数


汇编函数只要通过 .global 声明一下，C语言那边也extern声明一下，C语言就可以调用汇编函数.


## 实验：汇编调用C语言函数


C语言这边需要 extern 声明一下，汇编这边就可以直接调用，就是注意一下栈帧以及参数即可.


## 实验：几种汇编跳转指令


无条件跳转指令例子：
```cpp
//无条件跳转到目标地址,并将下一条指令的地址保存到x1寄存器
jal   x1, target_addr 

//跳转到x2寄存器的地址,并将返回地址保存在x1中
jalr  x1, x2, 0 

//如果两个寄存器值相等,则跳转到目标地址
beq   x1, x2, label_aaa 
bne   x1, x2, label_aaa 
blt   x1, x2, label_aaa //if x1 < x2, goto label_aaa
ble   x1, x2, label_aaa
bge   x1, x2, label_aaa
bgt   x1, x2, label_aaa
```


跳转伪指令例子：
```cpp
//等同于 jal x0, target_label
j    target_label

//等同于 jalr x0, x2, 0
jr   x2

//等同于 jr ra
ret
```















# 内存相关章节内存相关章节内存相关章节内存相关章节内存相关章节内存相关章节


# RISC-V 内存管理


## 内存管理发展史

固定分区法和动态分区法

![[20230806181816.png]]


## 直接使用物理内存的缺点


1、进程地址空间保护问题：所有的用户进程都可以访问全部的物理内存，所以恶意的程序可以修改其他程序的内存数据。
2、内存使用效率低：如果即将要运行的进程所需要的内存空间不足，就需要选择一个进程进行整体换出，这种机制导致有大量的数据需要换出和换入，效率非常低下。
3、程序运行地址重定位问题。

![[20230806182316.png]]


## 分页机制的基本概念

1、虚拟内存
2、虚拟地址
3、物理内存
4、页帧（ Page Frame ）
5、虚拟页帧号 VPN （ Virtual Page Frame Number ）
6、物理页帧号 PFN （Physical Frame Number ）
7、页表（ Page Table ）
8、页表项 （ Page Table Entry ，PTE ）


## VA到PA映射过程


1、CPU拿到VA，即虚拟地址，交给MMU.
2、MMU拿到VA，分解成 index 和 offset 两个字段.
3、index 能够指引找到对应的页表项，把页表项里的内容，作为 PFNs 的索引.
4、offset 就是对应 PFN 里面的具体位置，即可 PA 中的黄色位置.

![[20230806184103.png]]


## 一级页表示意图


![[20230806185406.png]]

采用一级页表的缺点：
- 1、处理器采用一级页表，虚拟地址空间位宽是32位，寻址范围是4GB大小，物理地址位宽也是32位，最大支持4GB物理内存，另外页面的大小是4KB。为了能映射整个4GB地址空间，那么需要4GB/4KB=1MB个页表项，每个页表项占用4字节，则需要4MB大小的物理内存来存放这张页表。
- 2、每个进程拥有了一套属于自己的页表，在进程切换时，需要切换页表基地址。如上述的一级页表，每个进程需要为其分配4MB的连续物理内存来存储页表，这是不能接受的，因为这样太浪费内存了。
- 3、多级页表：按需一级一级映射，不用一次全部映射所有地址空间。


## 二级页表示意图


![[20230806190204.png]]


## RISC-V内存管理


1、MMU内包括：TLB 、页表遍历单元
2、在 SMP 中，每个CPU核内置了 MMU 和 TLB 硬件单元.
3、进程地址空间映射到物理地址空间.

![[20230806190549.png]]

## RISC-V页表机制

1、SV32仅支持32位 RV 处理器，二级页表，支持32位虚拟地址转换
2、SV39支持64位RV处理器，三级页表，支持39位虚拟地址转换.
3、SV48支持64位RV处理器，四级页表，支持48位虚拟地址转换.

支持4KB大小的页面粒度，也支持2MB、1GB大小的块粒度，也称为大页(huge page).


## SV39页表

1、39位虚拟地址 >> 56位物理地址.
2、64位的虚拟地址中只有低39位用于页表索引，剩余的高位必须和第38位相等.
- 1、底部256GB (bit[63:38]全为0) ，用于用户空间.
- 2、高端256GB (bit[63:38]全为1) ，用于内核空间.
- 3、中间部分为非映射区域，即 bit[63:30] 不全为0或不全为1，处理器访问该区域会触发缺页异常.

![[20230806191652.png]]

## 虚拟地址划分


![[20230806191847.png]]

![[20230806191950.png]]


![[20230806192058.png]]


## MMU查询页表的过程

MMU查询页表的过程（理想状态）
- 1、从 satp 获取L0页表基地址
- 2、查找L0页表项，得到页表项，即L1页表基地址
- 3、查找L1页表项，得到页表项，即L2页表基地址
- 4、查找L2页表项，得到页表项，里面存放着物理页帧号PFN
- 5、PFN就是PA基地址，然后加上VA的低12位偏移，构成新的精确的物理地址.


## MMU查询页表异常

1、PMA或者PMP机制做内存属性相关的检查，触发内存访问异常（ access-fault exception ）
2、页表项有效性检查，如发现页表项是无效的，比如V=0或者保留的访问权限（如R=0且W=1），那么处理器会触发缺页异常。
3、子叶页表项描述符的权限检查，触发缺页异常.
4、假设处理器采用软件方式处理A和D标志位，当处理器访问页面时，如果该页面对应的子叶页表项描述符中的访问标志位为0（A=0）或者该访问是存储操作并且脏位为0（D=0），则会触发缺页异常.


## SV48页表映射

![[20230806212747.png]]


1、页表项：各级页表中的表项.
2、使用页表描述符来描述页表项中的内容.
3、SV39模式以及SV48模式，页表项描述符占8字节，格式一样，但内容完全不一样.

1、无效类型：bit[0] = 0
2、非子叶类型：bit[3:1] = 0
- 非子叶页表项（ non-leaf page table ）
- 页表项描述符包含指向下一级页表基地址的页帧号.
- 页表项描述符中的 bit[3:1] 都为0.
3、子叶页表类型：bit[3:1] != 0
- 子叶页表项（ leaf page table ）
- 页表项描述符包含指向最终物理地址的字段.
- 页表项描述符中的 bit[3:1] 不为0.
4、子叶页表的属性
- 低位属性：由 bit[9:0] 组成的低位属性.
- 高位属性：由 bit[63:54] 组成的高位属性.


## 页表项描述符中的低位属性


![[20230806213927.png]]


## svpbmt扩展


SVPBMT扩展将来用于替代物理内存属性（ Physical Memory Attribute ，PMA ）机制.

![[20230806214140.png]]


## 页表属性：访问权限

1、在没有相应权限的页面中进行读、写或者执行代码等操作会触发缺页异常.
- （1）如果在没有可执行权限的页面中预取指令，会触发预取缺页异常 ( fetch page fault )
- （2）如果在没有读权限的页面加载数据，会触发加载缺页异常 ( load page fault )
- （3）如果在没有写权限的页面加载数据，会触发存储缺页异常 ( store page fault )

![[20230806214556.png]]


## 访问标志位与脏标志位

1、页表项属性中有一个访问字段A(Access)，用来指示页面是否被访问过.
- 如果A字段为1，表示页面已经被CPU访问过.
- 如果A字段为0，表示页面还没有被CPU访问.

2、页表项属性中的脏标志位(Dirty) 表示页面内容被写入或者修改过.

3、软件方式更新A和D标志位的方式如下：
- 当CPU尝试访问页面并且A=0时，会触发缺页异常，然后软件就可以设置A=1.
- 当CPU尝试修改或者写入页面并且D=0时，会触发缺页异常，然后软件就可以设置D=1.

4、硬件方式更新A和D标志位的方式如下：
- 当CPU尝试访问页面并且该A=0时，CPU自动设置A=1.
- 当CPU尝试修改或者写入页面且D=0时，CPU自动设置D=1.

5、当采用硬件方式时，页表项(PTE) 的更新必须是原子的，即CPU原子地更新整个页表项，而不是仅仅更新某个标志位。

6、为什么需要A和D位？
- 因为操作系统的页面回收机制需要A和D来辅助.

7、操作系统使用访问标志位有如下好处：
- 用来判断某个已经分配的页面是否被操作系统访问过，如果A=0，说明这个页面没有人访问过.
- 用于操作系统中的页面回收机制.

8、连续页块
- 子叶页表项描述符中的N字段就是用来实现TLB优化功能的.
- 使用连续块页表项位的条件如下：
	- 连续的页面必须有相同的内存属性，即子叶页表项描述符中 bit[5:0] 必须相同.
	- 必须有2N个连续的页面.


## 地址转换寄存器satp


1、PPN字段：存储了L0页表基地址的页帧号.
2、ASID字段：进程地址空间标识符 ( Address Space Identifier )
3、MODE字段：用来选择地址转换的模式.

![[20230806220204.png]]

![[20230806220230.png]]


## 物理内存属性PMA

1、PMA —— Physical Memory Attribute
2、PMA描述内存映射中的每个地址区域访问的属性.
3、通常 RV 处理器内置一个 PMA，当 ITLB、DTLB 以及页表遍历单元获得物理地址之后，PMA检测器会做物理地址权限和属性检查.
4、PMA一般是在芯片设计阶段就固定下来，不能修改.

![[20230806220600.png]]


## 物理内存保护PMP

1、M模式具有最高特权，拥有访问系统全部资源的权限.
2、S/U模式默认对任何内存区域都没有访问权限，需要配置PMP.
3、什么时候PMP会做检查呢？
- M模式下只有当PMP表项中的L字段置位才会去检查PMP.
- S/U模式每次访问都会去检查PMP
	- 当 MPRV=1 并且 MPP为S/U模式时，在任意处理器模式下数据访问都需要做PMP检查.
	- 当 MPRV=0 并且 MPP为S/U模式的指令预取和数据访问.
- 在MMU遍历页表的过程中也会做PMP检查.

4、64个PMP表项：8位宽的字段，用 pmpNcfg 表示，N表示表项数.



基于硬件TEE的技术方案：
（1）TEE: Trust Exe Env ，受信任的执行环境
（2）在TEE中，即使是使用调试器，也无法从外部查看数据或者执行操作。TEE确保只有经过授权的代码才能访问数据，如果代码被篡改，TEE将阻止其继续进行操作。



## PMP表项

1、64个PMP表项：8位宽的字段，用 pmpNcfg 表示，N表示表项数.

![[20230806221507.png]]


![[20230806221602.png]]


## PMP地址表示方法：TOR

1、TOR表示法：由前一个PMP表项的地址寄存器代表的起始地址 ( 假设为 pmpaddr(i-1) ) 和当前PMP表项的地址寄存器代表的起始地址共同决定.  

$$
pmpaddr(i-1) \le y \lt pmpaddr(i)
$$

2、如果当前PMP表项是第0个表项并且A字段为TOR，那么地址空间的下界被认为是0，此时，当前PMP表项代表的地址范围为：0 <= y < pmpaddr(i)


## PMP地址表示方法：NAPOT

1、NAPOT表示法：采用 2n 自然对齐的方式，其地址范围计算方式是从PMP地址寄存器第0位开始计算连续为1的个数n，地址的长度为 2^n+3 。
- 如果PMP地址寄存器的值为 yyyy...yyy0 ，即 LSZB 个数为0，则地址空间为从 yyyy...yyy0 开始的 2^3 ，即8字节.
- 如果PMP地址寄存器的值为 yyyy...yy01 ，即 LSZB 个数为1，则地址空间为从 yyyy...yy00 开始的 2^(1+3) ，即16字节.
- 如果PMP地址寄存器的值为 yy01...1111 ，即 LSZB 个数为n，则地址空间为从 yy00...0000 开始的 2^(n+3) .

2、例子：假设一个地址区间的起始地址为 0x4000_0000 ，大小为 1MB，这个地址区间的PMP属性为可读、可写、可执行，请计算 pmpaddr0 寄存器的值以及 pmpcfg0 寄存器的值（假设目前只有一个PMP表项）.

- （1）由于PMP地址寄存器记录的是地址的 bit[55:2]，因此地址需要右移动2位，即 0x4000_0000 >> 2 = 0x1000_0000。
- （2）地址区间的大小为1MB，即 0x10_0000，它为220，因此 LSZB 为20.
- （3）由于PMP地址空间大小的计算公式为 2n+3 字节，因此 LSZB 要减去3，即17.
- （4）pmpaddr0 = 0x1000_0000 | 0b01_1111_1111_1111_1111 = 0x1001_FFFF.
- （5）由于PMP属性为可读、可写、可执行，并且采用NAPOT模式，因此 pmpcfg0 寄存器的值为 0x1F.


## NAPOT例子

1、例子：以 0x4000_0000 为基地址，不同PMP地址大小对应的PMP地址寄存器的值的计算过程.

![[20230806225017.png]]

## PMP使用例子


1、假设同一个地址 0x8000_0000 在pmp0cfg 和 pmp1cfg 表项中有重叠.

![[20230806225225.png]]

注意事项：
- 1、如果同一个地址对应多个PMP表项，那么PMP表项编号最小的表项优先级最高.
- 2、PMP只能在M模式下配置.
- 3、PMP检查是基于地址范围的.


## 案例分析1：在benos里实现恒等映射


![[20230806225529.png]]

## 为什么要恒等映射

为了打开MMU不会出问题：
1、在关闭MMU情况下，处理器访问的地址都是物理地址；当MMU打开时，处理器访问的地址变成了虚拟地址.
2、现代处理器都是多级流水线架构，处理器会提前预取多条指令到流水线中。当打开MMU时，处理器已经提前预取了多条指令，并且这些指令是以物理地址来进行预取的。当打开MMU指令执行完成，处理器的MMU功能生效，那么之前提前预取的指令以虚拟地址来访问，到MMU单元去查找对应的物理地址。因此，这里是为了保证处理器在开启MMU前后可以连续取指令.


## 页表


采用以Linux内核类似的页表定义方式，采用以下三级分页模型：
- 1、页全局目录PGD >>> L0页表
- 2、页中间目录PMD >>> L1页表
- 3、页表PT >>> L2页表

![[20230806230303.png]]


## 页表相关的宏


![[20230806230629.png]]


```cpp
/* PGD */
#define PGDIR_SHIFT     30
#define PGDIR_SIZE      (1UL << PGDIR_SHIFT)
#define PGDIR_MASK      (~(PGDIR_SIZE - 1))

/* PMD */
#define PMD_SHIFT       21
#define PMD_SIZE        (1UL << PMD_SHIFT)
#define PMD_MASK        (~(PMD_SIZE - 1))

/* PTE */
#define PTE_SHIFT 12
#define PTE_SIZE (1UL << PTE_SHIFT)
#define PTE_MASK (~(PTE_SIZE-1))

/* Number of entries in the page global directory */
#define PTRS_PER_PGD    (PAGE_SIZE / sizeof(pgd_t))
/* Number of entries in the page table */
#define PTRS_PER_PTE    (PAGE_SIZE / sizeof(pte_t))
#define PTRS_PER_PMD    (PAGE_SIZE / sizeof(pmd_t))
```


## 页表属性


```cpp
#define _PAGE_PRESENT   (1 << 0)
#define _PAGE_READ      (1 << 1)    /* Readable */
#define _PAGE_WRITE     (1 << 2)    /* Writable */
#define _PAGE_EXEC      (1 << 3)    /* Executable */
#define _PAGE_USER      (1 << 4)    /* User */
#define _PAGE_GLOBAL    (1 << 5)    /* Global */
#define _PAGE_ACCESSED  (1 << 6)    /* Set by hardware on any access */
#define _PAGE_DIRTY     (1 << 7)    /* Set by hardware on any write */
#define _PAGE_SOFT      (1 << 8)    /* Reserved for software */
```

在benos里根据内存属性划分不同类型的页面：
- PAGE_KERNEL ：操作系统内核中的普通内存页面.
- PAGE_KERNEL_READ ：操作系统内核中只读的普通内存页面.
- PAGE_KERNEL_READ_EXEC ：操作系统内核中只读的、可执行的普通页面.
- PAGE_KERNEL_EXEC ：操作系统内核中可执行的普通页面.

![[20230806231345.png]]


## 页表项描述符


1、页表项都是64位宽.
2、pgd_t 表示一个 PGD 页表项.
3、pmd_t 表示一个 PMD 页表项.
4、pte_t 表示一个页表项.

```cpp
typedef u64 pteval_t;
typedef u64 pmdval_t;
typedef u64 pudval_t;
typedef u64 pgdval_t;

typedef struct {
	pteval_t pte;
} pte_t;
#define pte_val(x) ((x).pte)
#define __pte(x) ((pte_t) { (x) })

typedef struct {
	pmdval_t pmd;
} pmd_t;
#define pmd_val(x) ((x).pmd)
#define __pmd(x) ((pmd_t) { (x) })

typedef struct {
	pudval_t pud;
} pud_t;
#define pud_val(x) ((x).pud)
#define __pud(x) ((pud_t) { (x) })

typedef struct {
	pgdval_t pgd;
} pgd_t;
#define pgd_val(x) ((x).pgd)
#define __pgd(x) ((pgd_t) { (x) })

typedef struct {
	unsigned long pgprot;
} pgprot_t;
```


## PGD页表

1、在链接脚本的数据段中预留4KB大小给PGD.
```cpp
SECTIONS
{
	/*
        * 设置benos的加载入口地址为0x80200000
        */
	. = 0x80200000,

	...

	/*
        * 数据段
        */
	_data = .;
	.data : { *(.data) }
	. = ALIGN(4096);
       idmap_pg_dir = .;
       . += 4096;
	_edata = .;

	...
}
```


2、创建页表
```cpp
/*
 * __create_pgd_mapping: 创建页表
 *
 * pgdir: PGD页表的基地址
 * phys: 物理地址PA
 * virt: 虚拟地址VA
 * size: 映射的大小
 * prot: 页表项PTE的属性,目标内存的属性
 * alloc_pgtable: 分配各级页表的分配函数,
		 * 用来分配下一级页表的内存分配函数
 * flags: 标志位,传递给页表创建过程中的标志位
 */
static void __create_pgd_mapping(pgd_t *pgdir, unsigned long phys,
		unsigned long virt, unsigned long size,
		pgprot_t prot,
		unsigned long (*alloc_pgtable)(void),
		unsigned long flags);
```


## 创建PGD页表项的过程


![[20230807090718.png]]
## 打开和测试MMU


1、设置 satp 寄存器打开MMU
```cpp
.global enable_mmu_relocate
enable_mmu_relocate:
	la a2, idmap_pg_dir
	srl a2, a2, PAGE_SHIFT
	li a1, SATP_MODE_39
	or a2, a2, a1
	sfence.vma
	csrw sptbr, a2
	ret
```

2、分别访问一个经过恒等映射和没有经过恒等映射的内存地址.
```cpp
static void test_mmu(void)
{
	test_access_map_address();
	test_access_unmap_address();
}
```

3、最终运行结果
![[20230807091104.png]]

## 案例分析2：图解页表创建过程


1、假设 PA=0x8020_0000 ，VA=0x8020_0000 ，映射大小为4KB，PGD页表的基地址 idmap_pg_dir = 0x8020_8000 ，如下所示。
![[20230807091315.png]]

2、填充和创建PGD页表项，虚拟地址 0x8020_0000 对应的PGD索引为2，即PGD页表项2.
![[20230807092500.png]]

3、由于 PGD页表项2是空的，为 PMD 页表分配一个 4KB 页面，假设这个页面的物理地址 pmd_phys 为 0x8022_C000 。
![[20230807092809.png]]

4、由 PMD 页表基地址来构造PGD页表项描述符。
![[20230807092953.png]]


5、对 PGD 页表项2的填充。
![[20230807093045.png]]


6、填充和创建PMD页表项，虚拟地址为 0x8020_0000，对应的PMD索引为1，在PMD页表中找到页表项，即 PMD页表项1.

![[20230807100535.png]]

7、由于 "PMD页表项1" 为空，新创建一个下一级页表PT，为页表分配一个4KB页面，假设这个页面的物理地址 pte_phys 为 0x8022_D000 。

![[20230807100848.png]]


8、由 PTE 页表基地址来构造 PMD 页表项描述符的内容.
![[20230807100951.png]]


9、对PMD页表项1的填充.
![[20230807101313.png]]


10、填充和创建PT页表项，虚拟地址 0x8020_0000 对应的PT索引为0，在PTE页表中找到页表项，即【PTE页表项0】.
![[20230807101457.png]]

11、根据物理地址 ( 0x8020_0000 ) 来创建一个页表项描述符的内容.
![[20230807101611.png]]


12、把这个页表项内容写入到【页表项0】中，完成对页表的填充.
![[20230807101855.png]]


13、最终效果图
![[20230807102823.png]]


## 实验1：建立恒等映射

1、实验目的：熟悉RV处理器中MMU的工作流程.
2、实验要求：
- （1）在QEMU上完成案例分析1的代码
- （2）使用GDB单步调试页表建立过程


## 实验2：为什么MMU无法运行

1、实验目的
- （1）熟悉RV处理器中MMU的工作流程.
- （2）培养调试和解决问题的能力
2、实验要求：小明把实验1中的 create_identical_mapping() 函数写成如下内容。

```cpp
static void create_identical_mapping(void)
{
	unsigned long start;
	unsigned long end;

	/*map memory*/
	start = (unsigned long)_etext;
	end = DDR_END;
	__create_pgd_mapping((pgd_t *)idmap_pg_dir, start, start,
			end - start, PAGE_KERNEL,
			early_pgtable_alloc,
			0);
	printk("map memory done\n");
}
```

他发现系统无法运行，这是什么原因导致的？请使用QEMU与GDB单步调试代码并找出是哪条语句发生了问题。为什么MMU无法运行？

## 实验3：实现一个MMU页表的转储功能


1、实验目的
- （1）熟悉RV处理器中MMU的工作流程.
- （2）培养调试和解决问题的能力.
2、实验要求
在实验1的基础上实现一个MMU页表的转储(dump)功能，输出页表的虚拟地址、页表属性等等信息，以方便调试和定位问题。页表属性包括DAGRWXV等属性.


## 实验4：修改页面属性

1、实验目的
- （1）熟悉RV处理器中MMU的工作流程.
- （2）培养调试和解决问题的能力.
2、实验要求
在系统中找出一个只读属性的页面，然后把这个页面的属性设置为可读可写，使用 memset() 函数往这个页面写入内容。

3、本实验的步骤如下：
- （1）从系统中找出一个4KB的只读页面，其虚拟地址为 vaddr
- （2）遍历页表，找到 vaddr 对应的页表项
- （3）修改页表项，为它设置可读、可写属性
- （4）使用 memset() 函数修改页面内容.


## 实验5：使用汇编来建立恒等映射


1、实验目的
- （1）熟悉RV处理器中MMU的工作流程
- （2）熟悉页表建立过程
- （3）熟悉汇编的使用

2、使用要求
- （1）在实验1的基础上，在汇编阶段使用汇编来创建恒等映射，即大小为2MB的块映射，并且打开MMU.
- （2）写一个测试例子来验证MMU是否开启.


## 实验6：在mysbi中实验和验证PMP机制


1、实验目的：熟悉RV处理器的PMP机制

2、实验要求
- （1）在mysbi中实现PMP配置功能，配置页表的属性为可读、可写、可执行.
```cpp
pmp0cfg: 0x0-0xffff ffff ffff ffff
```

- （2）在mysbi中实现如下PMP配置功能，分别配置页表的属性为不可读、不可写、不可执行，页表的属性为可读、可写、可执行。
```cpp
pmp0cfg: 0x8000 0000-0x8004 0000
pmp1cfg: 0x0000 0000-0xffff ffff ffff ffff
```

- （3）在benos中访问地址 0x8000_0000，请观察现象.


# RISC-V Cache基础知识


1、为什么需要Cache？
为了解决CPU访问速度与内存访问速度的不匹配问题。

![[20230809152027.png]]


## 经典处理器的Cache架构


![[20230809152153.png]]


## UMA和NUMA


![[20230809162659.png]]

## Cache的访问延时

![[20230809162953.png]]


## 经典的Cache架构


![[20230809163100.png]]


## Cache内部架构图


![[20230810075705.png]]

1、高速缓存行(cache line)：高速缓存中最小的单元.
2、索引(index)：用于索引和查找在哪一行，which cache line.
3、标记(tag)：高速缓存地址编码的一部分，通常是cache line的高位部分，用来判断cache line里cache data的地址是否和处理器要对比的地址一致。
4、偏移(offset)：cache line中的偏移，处理器可以按照字或者字节来寻址cache line的内容.
5、组(set)：相同索引，也就是相同层的所有cache line组成一组，打个比方，例如小区里通告所有二层楼住户到小区门口集合。所有二层楼就构成一个组，同理所有三层楼构成另一个组，其他楼层同理。
6、路(way)：每张表统计一栋楼的住户信息，一张表就是一路，两张表就是两路，有几张表就表示几路。


1、下面是一个2路组相联的Cache，它由两路组成(两张表)，每一路都有256 cache lines。两张表格的同一行组成一个组。

![[20230810103102.png]]


## Cache映射方式-直接映射


1、你可以理解为只有一张表，而且这张表容量有限，但是楼层很多远远大于你的统计表容量。


## Cache映射方式-组相联

1、比如说4路组相联，表示有4张统计表，当输入详细地址时，可以一次性查询4张表，这样能提高查找效率，降低颠簸问题。





## 高速缓存分类

VIVT、PIPT、VIPT

别名问题：**不同的VA**可能映射相同的PA.
同名问题：**相同的VA**可能对应不同的PA.

## PIPT

1、物理高速缓存：当处理器查询MMU和TLB得到物理地址后，使用物理地址去查询高速缓存(PIPT)
2、缺点：处理器在查询MMU和TLB之后才能访问高速缓存，增加了流水线的延迟.


## VIPT工作流程

![[20230810113503.png]]


## VIPT别名问题

![[20230810114016.png]]


## Cache层级

L1, L2, L3


## Cache策略

read-allocate
write-through 、write-back
shareability

1、Cache分配策略
- write-allocation: 当 write miss 的时候才会分配一个新的 cache line.
- read-allocation: 当 read miss 的时候才会分配一个新的 cache line.
2、Cache回写策略
- write-through: 回写操作会直接更新 cache 和内存.
- write-back: 回写操作仅仅更新到cache，并不会马上更新到内存，但会标记D=1(Dirty).


## CMO维护指令

1、RV中的CMO(Cache Management Operation) 扩展指令集提供了对高速缓存进行管理的指令。
2、高速缓存的管理行为清单：
- clean: 把D=1的某个cache line内的数据写回内存，然后D=0.
- invalidate: 使某个cache line失效，并丢弃其数据.
- flush: 先执行clean，后执行invalidate.
- zero: 对 cache 进行清零操作.

3、指令清单
- CBO.CLEAN 指令：对一个指定地址的cache line执行清理操作.
	- ```cbo.clean  rs1```
- CBO.FLUSH 、CBO.INVAL 、CBO.ZERO

4、预取Cache指令清单
- ```PREFETCH.I  offset(base)```   //预取icache里的数据
- ```PREFETCH.R  offset(base)```   //用于在读操作中预取dcache的数据
- ```PREFETCH.W  offset(base)```  //用于在写操作中预取dcache的数据


## RISC-V架构与Cache相关


1、RV处理器中的【内存区域属性】与【cache实现】
2、平头哥C910处理器支持cachable、bufferable、shareable的页面，在PTE页表项中设置.
3、U74通过PMA来设定内存区域是否需要cacheable
4、RV体系结构规范约定处理器不允许出现类似于cache别名的cache一致性问题.
5、香山处理器在RTL里面解决了VIPT别名问题.

![[20230810155523.png]]


# RISC-V 缓存一致性



## 为什么要cache一致性

cache coherency

1、cache一致性关注的是同一个数据在多个高速缓存和内存中的一致性问题，解决cache一致性的方法主要是总线监听协议，例如MESI协议等。

2、需要关注cache一致性的例子：
（1）驱动中使用DMA（ dcache和内存不一致 ）
（2）self-modifying code (dcache的数据可能比icache新)
（3）修改了页表（ TLB里保存的数据可能过时 ）

3、大多数情况由硬件来保证一致性，不过有些场景需要软件来手动保证cache一致性。


## ARM的cache一致性

4、单核处理器（ cortex-a8 ）
（1）单核，没有cache一致性问题
（2）cache管理指令仅仅作用于单核

5、多核处理器（ cortex-a9 MP以及之后的处理器 ）
（1）硬件上支持cache一致性
（2）cache管理指令会广播到其他CPU核心

![[20230810173828.png]]

![[20230810174013.png]]


## 系统级cache一致性


1、系统cache一致性需要cache一致性内部总线，可以理解为通过统一的一根总线来管理一致性.

![[20230810174541.png]]

## cache一致性解决方案

1、关闭cache
2、软件维护cache一致性：手动clean , invalidate 等操作.
3、硬件维护cache一致性：MESI来维护多核cache一致性，ACE来实现系统级cache一致性.



## 多核之间的cache一致性

1、多核CPU产生cache一致性的原因：同一个内存数据在多个CPU核心上的L1 Cache中存在多个不同的副本，导致数据不一致。
2、维护cache一致性的关键是跟踪每一个cache line的状态，并根据处理器的读写操作和总线上的相应传输来更新cache line在不同CPU内核上的cache状态，从而维护cache一致性。
3、cache一致性协议：snooping protocol 、directory protocol

4、MESI协议

![[20230810175702.png]]

5、状态切换原理：首先假设CPU有A,B双核,且cache更新策略为write-back策略
```txt
(1) ------> [A=I, B=I]
(2) ------> [A=E, B=I]
(3) ------> [A=M, B=I]

(1) ------> [B=I, A=M]
(2) ------> [B=I, A=E]
(3) ------> [B=S, A=S]
```

本地读写：本地CPU读写自己私有的cache line，这是一个私有的操作.
总线读写：读写远端CPU的cache line，发送请求到总线上，所有其他CPU都可以收到该请求.

![[20230811074808.png]]


![[20230811075923.png]]


## MESI状态图推演


![[20230811175615.png]]


1、MESI协议分析的一个例子

2、假设系统中有4个cpu，每个cpu都有各自的一级缓存，它们都想访问相同地址的数据A，大小为一个cache line.
- （1）T0时刻：4个cpu相应cache line都没有缓存数据A，因此对应cache line状态为I.
- （2）T1时刻：CPU0率先发起访问数据A的操作.
- （3）T2时刻：CPU1也发起读数据操作.
- （4）T3时刻：CPU2的程序想修改数据A中的数据.

![[gif202308120116.gif]]


## Cache伪共享

1、伪共享(false sharing)：比如两个不相干的变量A和B，但它俩被缓存到同一个cache line中.

2、一些常用的数据结构在定义时，就约定数据结构以L1 Cache Line对齐，
```cpp
//linux-kernel/arch/riscv/include/asm/cache.h
#define L1_CACHE_SHIFT          6
#define L1_CACHE_BYTES          (1 << L1_CACHE_SHIFT)
```

3、数据结构(如结构体)中频繁访问的成员可以单独占用一个Cache Line，或者相关的成员在Cache Line中彼此错开，以提高访问效率。例如Linux内核中的数据结构zone通过 ZONE_PADDING 技术(填充字节的方式)来让频繁访问的成员在不同的Cache Line中。





## 系统间的Cache一致性




## 案例2：DMA的Cache一致性


1、DMA直接访问内存，它在传输过程中无需CPU干预，可以直接从内存中读取数据.

2、DMA产生Cache一致性问题的原因：
- （1）DMA直接操作系统总线来读写内存地址，而CPU并不感知.
- （2）如果DMA修改的内存地址，在CPU的Cache中有缓存，那么CPU并不知道内存被修改了，CPU依然去访问cache的旧数据，导致cache一致性问题。

![[20230812093920.png]]


3、解决方案：
- （1）硬件来解决，需要SoC支持
- （2）使用 non-cache 的内存来进行DMA传输.
- （3）根据DMA传输方向，软件来维护Cache一致性


## 案例3：self-modifying-code

1、icache和dcache是分开的，icache一般只读.

2、icache和dcache的一致性问题，指令通常不能修改，但特殊情况存在被修改.

2、self-modifying-code，在执行过程中修改自己的指令，过程如下：
- （1）把要修改的指令，加载到dcache里.
- （2）程序修改这个dcache里的指令，因此此时dcache里这指令被更新了.
- （3）但icache里依然是老指令，新指令还在dcache里.

3、解决思路：使用cache管理指令和内存屏障指令来保证dcache和icache的一致性.

4、例子：假设寄存器t0存储了代码段的地址，通过sd指令把新的指令t1写入t0寄存器值所在地址中.
```cpp
sd         t1, (t0)
cbo.flush  t0
fence      rw, rw
fence.i
```


# RISC-V TLB管理

## 为什么需要TLB？

1、MMU查询页表很慢，多级页表需要多次访问内存.
2、把MMU的地址转换结果缓存到一个特定cache中，这个Cache就叫TLB.

![[20230812112416.png]]

![[20230812112929.png]]


## RISC-V架构中的TLB表项结构

1、RISC-V体系结构手册中没有约定TLB项的结构.

![[20230812114338.png]]

2、各大厂商TLB采用X路组相联结构，也分L1, L2等等.

![[20230812115213.png]]


![[20230812132429.png]]


## TLB别名问题


![[20230812161539.png]]

## TLB同名问题

![[20230812161637.png]]


## ASID

1、ASID —— Address Space Identifier

2、全局类型的TLB：内核空间是所有进程共享的空间（我没理解这句话）。
3、进程独有类型的TLB：用户地址空间是每个进程独立的地址空间.

4、ASID机制用来实现进程独有类型的TLB.
5、RV的ASID存储在 satp 寄存器中，一共16位宽，最多支持65536个ASID。

![[20230812162050.png]]
## ASID怎么用？

![[20230812162634.png]]


## TLB维护指令

1、RV架构提供了一条TLB维护指令 SFENCE.VMA ，融合了内存屏障与刷新TLB的指令.
- （1）内存屏障：保证在屏障之前的存储操作与屏障之后的读写操作执行次序。这里主要指的是对虚拟内存管理中的相关数据的读写操作，例如，对页表的读写操作等。
- （2）刷新TLB：刷新本地处理器上与地址转换相关的Cache，如TLB等.

2、SFENCE.VMA 指令的作用范围仅限于本地处理器：```sfence.vma   rs1, rs2```
- （1）rs1用来指定虚拟地址，rs2用来指定ASID.

![[20230812163411.png]]

![[20230812163450.png]]

## TLB例子

![[20230812163601.png]]

![[20230812163715.png]]


## TLB广播

1、TLB shootdown —— TLB广播
2、SFENCE.VMA 指令仅作用于本地处理器，如果刷新多处理器中的TLB，则需要使用TLB广播.
3、TLB shootdown：A request to another processor to remove a newly invalid TLB entry.
4、有些处理器体系结构在芯片内部实现TLB广播协议，如ARM的DVM事务协议.
5、RV架构需要使用软件触发IPI才能完成TLB广播.
6、opensbi提供了两个刷新进程TLB的接口
- （1）SBI_EXT_RFENCE_REMOTE_SFENCE_VMA ：用来刷新全部进程的TLB.
- （2）SBI_EXT_RFENCE_REMOTE_SFENCE_VMA_ASID ：用来刷新指定进程的TLB.

7、在RV体系结构中实现TLB广播的步骤如下：
- （1）在本地处理器中执行 SFENCE.VMA 指令.
- （2）依次向系统中其他处理器触发IPI.
- （3）其他处理器在IPI处理函数中执行 SFENCE.VMA 指令.
- （4）其他处理器发送信号给本地处理器，告知IPI处理已经完成.

![[20230812164613.png]]

## 案例1：TLB在Linux内核中的应用


![[20230812164724.png]]

## 案例2：ASID在Linux内核中的应用

1、硬件ASID通过位图来分配和管理.
2、新创建的进程，使用位图机制来分配一个空闲的ASID，把这个ASID填充到satp寄存器里.
3、当系统中ASID加起来超过硬件最大值时，会发生溢出，需要冲刷全部TLB，重新分配ASID.
4、当切换进程的时候，需要把进程持有的硬件ASID写入satp寄存器里.
5、在Linux内核里，进程切换出去之后会把ASID存储在mm数据结构的context字段里面。当进程再切换回来的时候，把ASID设置到satp寄存器里。

![[20230812165149.png]]


## 案例3：Linux内核中的TLB维护操作

![[20230812165335.png]]

## 案例4：BBM机制

1、在多核系统中，多个虚拟地址可以同时映射到同一个物理地址，出现为同一个物理地址创建了多个TLB项的情况，而更改其中一个页表项会破坏缓存一致性以及内存访问的时序等，从而导致系统出问题。

2、BBM机制，Break-Before-Make，先断开后更新。

3、BBM机制工作流程：
- （1）使用一个失效的页表项来替换旧的页表项，执行一条内存屏障指令.
- （2）执行 SFENCE.VMA 指令来刷新对应的TLB，发送IPI中断到其他CPU上，让其他CPU也刷新TLB.
- （3）写入新的页表项，执行内存屏障指令，保证写入操作被其他CPU观察者看到.

4、假设主进程有两个线程：线程0和线程1，分别运行在CPU0和CPU1上，它们共同访问一个虚拟地址，这个VMA映射到Page0上。

![[20230812170134.png]]
解决方案：根据BBM机制，C对应的步骤需要分解成如下几个步骤。
- （1）在切换页表项之前，CPU1把旧的页表项内容清除掉.
- （2）刷新对应的TLB，发送广播到其他CPU上.
- （3）设置新的页表项（ PTE2 ）.
- （4）对于线程1来说，VMA的虚拟地址映射到Page_new之后才能往Page_new中写入新代码.


## 小结：RV架构规范与TLB

1、RV架构没有约定TLB表项的内容.
2、RV架构没有约定TLB映射方式：直接映射、全相联、组相联、多级TLB等.
3、RV架构没有约定TLB refill 是硬件实现还是软件实现.
4、RV架构约定了刷新TLB的指令：SFENCE.VMA
5、RV架构的ASID机制：16位的ASID，并存储在 satp 寄存器.


# RISC-V 原子操作


## 为什么需要原子操作


## 什么是原子操作

1、原子操作：保证某一组相关的操作不被打断.
2、要保证操作的完整性和原子性，完成读改写，中间不能被打断.
3、处理器需提供原子操作的指令
- （1）RV提供保留加载 Load-Reserved，简称LR；以及条件存储 Store-Conditional，简称SC指令.
- （2）原子内存访问指令.

3、LL指令：从指定内存地址读取一个值，处理器会监控这个内存地址.
4、SC指令：如果这段时间内其他处理器没有修改该内存地址，则把新值写入该地址.

5、LL/SC指令常常用于实现无锁算法与读改写原子操作.

如下代码所示，LR指令会注册一个保留集，SC指令有条件地把rs2寄存器的值存储到rs1地址中，执行结果反馈到rd寄存器，rd=0表示成功，rd!=0表示执行失败。SC执行不管成功还是失败，保留集都会失效。
```cpp
lr.w    rd, (rs1)
//lr.d    rd, (rs1)

sc.w    rd, rs2, (rs1)
//sc.d    rd, rs2, (rs1)
```



## 例子：atomic_add


```cpp
static inline void atomic_add(int i, unsigned long *p)
{
	unsigned long tmp;
	int result;

	asm volatile("# atomic_add\n"
"1:	lr.d	%[tmp], (%[p])\n"
"	add	%[tmp], %[i], %[tmp]\n"
"	sc.d	%[result], %[tmp], (%[p])\n"
"	bnez	%[result], 1b\n"
	: [result]"=&r" (result), [tmp]"=&r" (tmp), [p]"+r" (p)
	: [i]"r" (i)
	: "memory");
}

int main(void)
{
	unsigned long p = 0;
	atomic_add(5, &p);
	printf("atomic add: %ld\n", p);
}
```


## LRSC指令需要注意的地方


1、LR/SC指令是配对使用的.
2、SC指令执行成功的条件：当前保留集有效，保留集中包含的数据被成功更新或者写入.
3、无论SC指令执行成功与否，当前CPU包含的保留集都被无效掉.
4、SC指令可能失败的情况：
- （1）如果SC写入的地址，不在与之配对的LR指令组成的保留集范围内.
- （2）在LR/SC指令范围内，执行了另外一条SC指令（这条SC指令写任何地址）
- （3）在LR/SC指令范围内，执行了另外一条store指令并且是对LR的加载地址进行store的.
- （4）另外一个CPU对当前LR/SC的保留集地址进行写入操作.
- （5）另外一个外设对LR/SC加载的数据进行写入.


## LRSC指令的约束规范

1、RV架构对LR/SC序列做了一些约束，不符合这些约束的LR/SC序列不能保证在所有RV处理器中都能成功。

（1）LR/SC的循环Loop中最多包含16条指令.
（2）LR/SC序列包括RV64I指令或压缩指令，但是不包括加载、存储、向后跳转、向后分支、JALR、FENCE、以及 SYSTEM 指令。
（3）LR/SC序列可以包含向后跳转的retry重试.
（4）SC指令的地址必须与同一个CPU执行的最新LR的有效地址和数据大小相同.


## LRSC错误案例1

![[20230812211843.png]]

## LRSC错误案例2

![[20230812211938.png]]


## LRSC错误案例3

![[20230812212041.png]]


## 独占访问工作原理

1、RV指令手册中并没有约定LS/SC指令如何实现.
2、本课程是基于一种独占监视器，来监控内存访问的方法.
3、独占监视器一共有两个状态：开放访问状态、独占访问状态.
4、LR指令从内存加载数据时，CPU会把这个内存地址标记为独占访问状态.
5、当CPU执行SC指令到时候，需要根据独占监视器的状态来做决定
- （1）如果为独占访问状态，那么SC指令存储成功，SC指令返回0，紧接着监视器变成开放访问状态.
- （2）如果为开放访问状态，那么SC指令存储失败，stxr指令返回1.


## 独占监视器注意事项

1、独占监视器本身不是用来阻止CPU核心来访问被标记的内存，不会lock总线.
2、独占监视器仅仅起到监视的作用，监视状态的变化.
3、不能把独占监视器看成是一个硬件锁.


## 独占监视器组成架构

1、通常一个系统由多级独占监视器组成，分别是本地独占监视器、缓存一致性的全局独占监视器、外部的全局独占监视器。

![[20230812221359.png]]


## 独占监视器与缓存一致性

1、假设CPU0和CPU1同时访问一个锁，这个锁的地址为a0寄存器的值。

![[20230812222007.png]]




## 原子内存操作

1、原子内存操作指令，它允许在靠近数据的地方原子地实现读改写操作.
- （1）近端原子操作(near atomic)
- （2）远端原子操作(far atomic)：需要CHI总线或者TiLink总线支持.

2、AMBA 5总线引入了原子事务(atomic transaction)，近端和远端都支持.


## 原子内存访问与LRSC效率对比

1、在独占内存访问体系结构下，ALU位于每个CPU核内部，如果多个CPU同时用一个内存数据，则会导致cache颠簸.
2、原子内存操作指令在互连总线中的HN-F节点中对所有发起访问的CPU请求进行全局仲裁，并且在HN-F节点内部完成算术运算，从而避免cache颠簸消耗总线带宽.

![[20230812223606.png]]

## RV中的原子内存访问指令

1、原子内存访问指令格式：
![[20230812223722.png]]


## 例子：用AMOADD指令实现atomic_add


```cpp
static inline void atomic_add(int i, unsigned long *p)
{
	unsigned long result;

	asm volatile("# atomic_add\n"
"	amoadd.d %[result], %[i], %[p]\n"
	: [result]"=&r"(result) , [p]"+A" (*p)
	: [i]"r" (i)
	: "memory");
}

int main(void)
{
	unsigned long p = 0x1;
	atomic_add(0x3, &p);
	printf("atomic add: 0x%lx\n", p);
}
```


## 例子：使用AMOMAX实现自旋锁


```cpp
/*
   get_lock(lock)
*/
.global get_lock
get_lock:
	li a2, 1
retry:
	amomax.w a1, a2, (a0)  
	bnez a1, retry
	ret

/*
   free_lock(lock)
*/
.global free_lock
free_lock:
	sw x0, (a0)
```


## 例子：比较并交换

1、CAS操作：比较ptr指向的值与expected是否相等，若相等则把new赋值给ptr，否则什么也不做.

2、ARMv8和x86体系结构提供了专用的CAS指令，但是RV中并没有，而推荐使用LR/SC来实现.
- （1）CAS会存在ABA问题，但是SL/SC指令可以避免这个问题.
- （2）CAS还需要一种新的整数指令格式来支持3种源操作数（地址、比较值、交换值）以及一种不同的内存系统消息格式，这将使处理器设计变得复杂化.


## 例子：用LRSC实现cmpxchg函数


```cpp
static inline unsigned long cmpxchg(volatile void *ptr, unsigned long old, unsigned long new)
{
	unsigned long tmp;
	unsigned long result;

	asm volatile(
"1:	lr.d	%[result], (%[ptr])\n"
"       bne  %[result], %[old], 2f\n"
"	sc.d  %[tmp], %[new], (%[ptr])\n"
"	bnez	%[tmp], 1b\n"
"       2:\n"
	: [result]"+r" (result), [tmp]"+r" (tmp), [ptr]"+r" (ptr)
	: [new]"r" (new), [old]"r"(old)
	: "memory");

	return result;
}

int main(void)
{
	unsigned long p = 0x1234;
	unsigned long old;

	old = cmpxchg(&p, 0x1, 0x5);
	printf("old 0x%lx, p 0x%lx\n", old, p);

	old = cmpxchg(&p, 0x1234, 0x5);
	printf("old 0x%lx, p 0x%lx\n", old, p);
}
```



## 例子：用LRSC实现xchg函数


```cpp
static inline unsigned long xchg(volatile void *ptr, unsigned long new)
{
	unsigned long tmp;
	unsigned long result;

	asm volatile(
"1:	lr.d	%[result], (%[ptr])\n"
"	sc.d  %[tmp], %[new], (%[ptr])\n"
"	bnez	%[tmp], 1b\n"
	: [result]"+r" (result), [tmp]"+r" (tmp), [ptr]"+r" (ptr)
	: [new]"r" (new)
	: "memory");
	return result;
}

int main(void)
{
	unsigned long p = 0x1234;
	unsigned long old;
	old = xchg(&p, 0x1);
	printf("old 0x%lx, p 0x%lx\n", old, p);
}
```

## lock-free操作

1、无锁操作，即lock-free操作，
2、在链表并发操作过程种，不需要额外使用OS提供的锁机制，使用CAS指令来实现.
3、Linux内核的MCS锁，qspinlock锁的实现使用了无锁操作.


## 思考题：LRSC与进程切换

1、如果在LR/SC序列中发生了进程切换，那么LR/SC还能成功吗？

![[20230812225403.png]]


## 总结

1、RV架构的原子操作通过A扩展指令集来支持.
2、RV架构中的LR/SC指令采用LL/SC机制。
3、RV架构手册中没有约定LR/SC在微架构中如何实现.
4、LR/SC会注册保留集，手册中约定了几种情况会导致SC指令执行失败.
5、RV架构手册对LR/SC指令序列做了约束.
6、RV架构支持原子内存操作指令.
7、RV架构没有单独的CAS指令.


# RISC-V 内存屏障


## 为什么会有内存乱序？

1、内存乱序：程序在执行过程中，实际内存访问的顺序MO，与程序代码约定的访问顺序PO不一致.
2、MO就是从内存角度看到的内存访问顺序.

3、内存乱序产生的两个最基本原因：
- （1）编译优化导致内存乱序访问.
- （2）执行阶段：单核、多核，等不同访存部件的交互，导致内存乱序.

![[20230813102328.png]]



## 编译器优化导致的乱序

1、编译器会在翻译成汇编指令时对其进行优化，如内存访问指令的重排序可以提高指令级并行效率.
2、这些优化可能会与原始代码逻辑不符，导致一些错误发生.

```cpp
#define barrier() __asm__ __volatile__ ("" ::: "memory")
```

3、barrier 函数告诉编译器，不要为了性能优化而对这些代码重排序.




## CPU体系结构1：顺序执行处理器


![[20230813120244.png]]


## CPU体系结构2：超标量单核

![[20230813120326.png]]


## 内存一致性模型

1、在处理器系统中，内存一致性用来保证单核处理器，或者多核处理器的各个处理器，对存储子系统访问的正确性.













# RISC-V 常见C语言陷阱

![[20230814102134.png]]


## 数据模型

1、32位处理器通常采用 IL32 数据模型，而64位处理器可以采用 LP64 和 ILP64 数据模型.
2、Linux系统采用 LP64 数据模型.

![[20230814110650.png]]

## 数据类型转换

1、在赋值表达式中，右边表达式的值自动隐式转换为左边变量的类型.
```cpp
a = b;
```

2、在算术表达式中，占用字节少的数据类型，向占用字节多的数据类型转换.
```cpp
(int)a + (long)b;
```

3、在算术表达式中，当对有符号数据类型与无符号数据类型进行运算时，需要把有符号数据类型转换为无符号数据类型。
```cpp
(int)a + (unsigned int)b;
```

4、整数常量通常属于int类型.

![[20230814111953.png]]

## 整型提升

1、整型提升(integral promotion)：在表达式中，当使用符号或者无符号的char 、short 、位域 以及枚举类型时，它们都应该提升到int类型。


## 符号扩展

1、当要把一个带符号的整数提升为同一类型或更长类型的无符号整数时，它首先被提升为更长类型的带符号等价数值，然后转换为无符号值.


## 移位操作

1、整数常量通常被看成int类型，如果移位的范围超过int类型，就会出错；正常情况应该用UL修饰.
```cpp
unsigned long data = 1UL << 33;
```


# BenOS 进程创建


1、进程是OS分配内存、CPU时间片等资源的基本单位.
2、进程控制块（ task_struct ）
3、cpu_context 用来表示进程切换时的硬件上下文.


## do_fork实现

do_fork函数创建一个进程，其流程如下：
1、新建一个 task_struct 数据结构，设置好内核栈
2、为新进程分配PID
3、设置进程的上下文


## 进程上下文切换

1、cpu_switch_to 函数，它用于保存 prev 进程的上下文，并且恢复 next 进程的上下文.
```cpp
void cpu_switch_to(struct task_struct *prev, struct task_struct *next);
```

2、保存的上下文包括 s0~s11 寄存器、sp寄存器以及ra寄存器的值，保存在 prev->cpu_context 中.
3、从 next->cpu_context 中恢复处理器中这些寄存器的值.
```cpp
/* 进程切换时候需要保存的上下文 */
struct cpu_context {
	unsigned long ra;
	unsigned long sp;	/* 栈指针 */

	/* 函数调用必须要保存的通用寄存器 */
	unsigned long s[12];	/* s[0] 是FP */
};
```

![[20230814154439.png]]


## 新进程的第一次执行


![[20230814154633.png]]


## 实验：实现一个简单的调度器

任务：创建两个内核线程，这两个内核线程只能在内核空间中运行，线程A输出 "12345"，线程B输出 "abcde"，要求调度器能够合理调度这两个内核线程，二者交替运行，而系统的0号进程不参与调度.

实验目的：
1、了解进程调度的概念，发展历史.
2、了解进程调度的本质
- （1）调度的时机是什么？
- （2）如何合理和高效地选择下一个进程？
- （3）如何切换到下一个进程？
- （4）当调度器切换到next进程时，next进程执行的第一条指令是什么？
- （5）下一个进程如何返回上一次暂停的地方？

3、通过实验和单步调试的方式，深入理解进程调度.


## 调度器基本概念

1、就绪队列：存储即将要参与调度的候选进程.
2、就绪队列可以是链表也可以是红黑树.
3、调度策略：O(n)调度器、经典多级调度算法Multi-level feedback queue、Linux 2.6内核的O(1)调度算法、CFS调度器。
4、调度类：OS为了支持多种不同的调度策略，实现一个统一的抽象框架.


## 自愿调度与抢占调度

1、自愿调度就是进程主动调用 schedule 函数来放弃CPU的控制权.
2、抢占调度是指在中断处理返回后，检查是否可以抢占当前进程的运行权.


## 让进程运行在用户模式

1、RV体系结构中，所有的处理器模式共用一个SP，需要妥善处理SP问题.

2、benos中 task_struct 结构体中新增了2个字段，用来保存内核模式的SP和用户模式的SP.

```cpp
struct task_struct {
	...
	unsigned long kernel_sp;
	unsigned long user_sp;
	...
};
```













# BenOS 进程调度


# BenOS 系统调用


# RVV可伸缩矢量指令




# RVV虚拟化扩展






# RISC-V体系结构群技术交流

参考资料：《 RISC-V非特权级ISA精读（WPS文字批注）.pdf 》


**RISC-V体系结构读者群0——光影却流年**：请教大家一个问题，RISCV的opensbi的地址空间是怎么划分的？有没有什么安全机制让此地址空间不被其他程序踩内存？
**RISC-V体系结构读者群0——我**：常规情况从os kernel层在初始化mmu时，对sbi的地址空间进行了特殊保护
**RISC-V体系结构读者群0——光影却流年**：能详细说说吗？
**RISC-V体系结构读者群0——我**：这是本人常规猜测，毕竟sbi工作在M模式直接访问的是物理内存。那么对内存提供保护机制的成熟方案都在os kernel中实现了。在kernel对mmu初始化期间，可以通过补丁的方式对某特定的物理内存区域进行保护，不知道目前kernel那边是否已经考虑到你说的sbi空间保护问题，如果还没有，那么只能破费你自己去修改mmu初始化相关的位置，对特定物理内存区域进行权限等限制，并对缺页等相关的异常位置进行修改，来支持你所谓的踩内存。

ChatGPT(Q): 常规情况从os kerel层在初始化mmu时，对sbi的地址空间进行了特殊保护.
ChatGPT(A): 是的，通常在操作系统内核初始化内存管理单元 (MMU) 时会对SBI (Supervisor Binary Interface) 的地址空间进行特殊保护。SBI是用于操作系统和硬件交互的接口，它允许操作系统内核在特权模式下执行特权指令，从而对硬件资源进行管理和访问。在初始化MMU时，操作系统内核会设置专门的页表，将SBI的地址空间映射为只能以特权模式访问的内存区域。这样做的目的是确保只有操作系统内核才能执行SBI指令，防止恶意代码或用户态应用程序对SBI接口进行滥用。通过特殊保护SBI的地址空间，操作系统可以更好地控制和管理操作系统与硬件之间的交互，提高系统的安全性和稳定性。

**RISC-V体系结构读者群0——我**：ChatGPT补充了我前面的详细猜测~

---

陈康：处理器的内存模型跟处理器的乱序基本上没有直接的联系。有一个原则是在一个核的内部指令肯定是按照顺序提交的，这里的提交其实可以相当于按照顺序执行。提交是术语，简单理解为执行完成没有问题。也就是说，不管怎么样，从一个单核来看，执行顺序肯定是要按照程序的顺序来的，不会乱来的，哪怕是乱序执行的处理器。乱序执行为了速度，但是不能牺牲正确性。要是没有这个原则的话，那么处理器设计的底线就没有了。所以，在考虑内存模型的时候不需要担心处理器乱序的问题。

陈康：在这个前提下，为啥有fence指令这种东西呢，或者说，存储指令的乱序是怎么来的呢。这个就涉及到不同的核（严格的说是不同的部件）看到的从一个核c1中发出的存储指令的顺序可能是不同的。例如，从执行的核本身来看，可能看到的顺序是先有一个写W，再有一个读R，即先写后读。但是，从内存m的角度来看，c1发出的内存指令的顺序却是先读后写。因为这个写W会被缓存到处理器核c内部的写缓存write buffer。写缓存使用寄存器就可以实现，但是读不行，因为读是需要携带结果回来的，只能从内存里面拿。这样的话，从c1的角度看，W完成了，因为已经写到write buffer，之后R携带着数据从内存回来。而从内存m的角度来看，一个R是先来的，然后W后面才来。这样，c1和m看到的是同一个程序的内存执行顺序是不同的。c1感觉很对，并且速度快，因为W都不需要去触碰内存。m不管，因为m只提供内存服务。到现在为止，其实也没啥事，因为从c1的角度来看，我执行程序是一个正确的执行的流程。m自己本身不执行程序，只提供服务。

陈康：问题是在于有另外一个核，比如c2。从c2怎么看c1的读写顺序呢。显然c1在执行的过程中不会告诉c2我的执行顺序是怎么样的，因为这个本来跟c2也没关系。但是，c1和c2是共享内存的，c2在看顺序的时候只能从m的观点来看，它就看到和c1不一样的顺序。这样就会产生问题，原因是现在c2也执行程序，并且c2程序执行的结果非常有可能依赖于上面的R和W的执行顺序。这个时候就出问题了，c1必须要明确的告知c2执行顺序是怎么样的。c1就会在W之后插入fence，形成W, fence, R这样的指令执行序列。这样，c2看到的指令顺序和c1是一样的。

陈康：所以，所谓的fence就是，某一个核，就是上面的c1，会发现我自己看到的顺序和别人看到我的顺序可能不一样，这个时候就需要插入fence。如果这个顺序不重要，那就不需要插入fence。

陈康：上面是针对写可能存在的优化，就是使用write buffer，但是会造成内存看到的顺序和核看到的顺序不一样。在实际的处理器中，也有可能别的优化造成的顺序问题，比如预取什么的。speculative的load。都有可能造成乱序。例如，有些处理器的优化感觉将来可能用到什么内存 ，那就预先把数据从内存读进来。如果这个读最终是可见的，那也会出问题。有的处理器不这么做。这样，根据处理器的不同，会有不同的fence指令。这就造成了fence的参数不同。

陈康：然后，这个顺序在不同的范围内可能有不同的效果。我们当然希望顺序暴露给更小的范围更好，因为速度会更快，例如只需要在核心之间暴露就行。这样，fence又有了范围的参数（arm下面）。

陈康：最后，这些顺序并不是只局限在多核，在单核中也同样存在，有的时候还跟顺序无关，更合适的说法是什么时候可见。只要有不同的部件都涉及到内存就会出现这个问题。在单核中，有取指部件从内存中获得指令并放在L1指令缓存中。如果程序修改了指令，缓存中就不对了（注意L1缓存是哈佛结构的），这时候需要一个fence.i指令。然后tlb是用来缓存虚拟地址到物理地址转换的，修改了之后需要fence.vma。

笨叔@陈康 兄弟，总结精辟，理解深刻





