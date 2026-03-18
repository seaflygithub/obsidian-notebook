

草稿: [[笨叔RISC-V体系结构.excalidraw]]

# 第02章-搭建RISC-V实验环境

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


---

**QemuVirt地址空间**

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




## 单步调试（QEMU+GDBServer+Eclipse）

**通过终端单步调试**

- 单步调试步骤：
- 步骤1: 开两个终端，在终端A中执行GDBServer端 `make debug` (note: `ctrl+a x` can terminal the emulator)，其实就是qemu命令的最后`S -s`选项。
- 步骤2: 另一个终端运行: `gdb-multiarch --tui benos.elf`
- 步骤3: 在客户端这边，设置断点，并通过continue命令开始运行程序。

```bash
# in debugger
(gdb) target remote localhost:1234
(gdb) break src/kernel.c:kernel_main
Breakpoint 1 at 0x80200444: file src/kernel.c, line 77.
(gdb) continue
(gdb) step  (or next)
```

![[Pasted image 20251222150011.png]]

---

**通过Eclipse单步调试**

- Step 01: Launch Eclipse, and the workspace is defaulted by Eclipse.
- Step 02: [[RISC-V-1e629537878080be85e2f9cc5f06cdd9?pvs=21]]
- Step 03: [[RISC-V-1e629537878080be85e2f9cc5f06cdd9?pvs=21]]
- Step 04: Execute the `make debug` command in the terminal to enter the debugging wait state.
- Step 05: [[RISC-V-1e629537878080be85e2f9cc5f06cdd9?pvs=21]]: Perform Debug in Eclipse and set breakpoints, then start debugging.


![[Pasted image 20251222150047.png]]


![[Pasted image 20251222150059.png]]


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

riscv_programming_practice/chapter_2/benos/include/asm/uart.h

01、上述代码调用了串口打印了 Welcome RISC-V 语句。接下来实现简单的串口驱动代码，QEMU使用兼容 16550 规范的串口控制器。首先我们找到QEMU Virt地址空间中，串口的基地址为 0x10000000，大小为0x100，即256字节。然后在这256字节的范围内，继续划分了空间，比如寄存器空间，如上面头文件 asm/uart.h 所示，从寄存器地址排布看，每个寄存器只占用了1个字节的空间。而且还有复用寄存器，预分频寄存器。我们分析其代码需要结合16650相关的数据手册来分析，才能知其所以然。浏览器搜索: 16550 uart datasheet 即可搜到类似的数据手册。

02、复用寄存器通过某种方式进行切换，比如这里的串口，通过 UART_LCR 这个寄存器来进行切换，如下代码，直接往第7位即最高位写1，表示 0x00 和 0x01 此时是预分频寄存器，这时候再往 0x00,0x01 写入数据，就是在访问预分频相关的寄存器了。



## payload

不带payload后缀文件名的文件，表示 sbi 和 benos 是分开的，即各自编译制作出独立的镜像文件；

带 payload 后缀文件名的文件，表示 sbi 和 benos 被链接到一个输出镜像里。

sbi_linker_payload.ld

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

sbi_payload.S

```cpp
	.section .payload, "ax", %progbits
	.globl payload_bin
payload_bin:
	.incbin	"benos.bin"
```

Makefile里payload部分

```cpp
$(CMD_PREFIX)$(GNU)-ld -T $(SBI_SRC_DIR)/sbi_linker_payload.ld -o $(SBI_BUILD_DIR)/benos_payload.elf
```




# 内嵌汇编

ISA(Instruction Set Architecture)

```markdown
root:~# cat /proc/cpuinfo
processor       : 0
hart            : 0
isa             : rv64imafdcsu  ---> (imafdcsu)
mmu             : sv48
```

```markdown
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

```markdown
疑问：这些各种指令集，需要记住这些分类嘛？对于软件人员，有什么用？
解答：可以根据其支持的指令集所携带的功能，大致评估这款芯片的业务能力范围。
```


![[Pasted image 20251222150231.png]]




# 汇编基础

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

```nasm
.globl asm_debug
asm_debug:
	auipc	t0, 0x0 //pc=0x80200208,t0=x
	auipc	t1, 0x0 //pc=0x8020020c,t0=0x80200208
	auipc	t2, 0x0 //pc=0x80200210,t1=0x8020020c
	ret             //pc=0x80200214,t2=0x80200210
```

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

```cpp
li   a0, 0x80200004 //a0=0x80200004
lui  a0, 0x80200004 //Error: lui expression not in range 0..1048575(20bits)
lui  a0, 0x80204    //a0=0xffffffff80204000 (t0 = 0x80204 << 12; sext.dw t0, t0)
lui  t0, 0xc0204    //t0=0xffffffffc0204000 (t0 = 0xc0204 << 12; sext.dw t0, t0)
```

如上实验结果所示，lui会根据目标立即数先移位，然后根据目标数的符号位进行符号扩展。比如上述 0x80204 ，lui 指令只取目标立即数 imm[19:0] 位，并且在第19位处的值是1，因此需要符号位扩展，即寄存器的剩余高位全部填充1。

下面是利用 [[godbolt.org]] 来探究立即数加载指令的：

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

```markdown
l{d|w|h|b}{u}  rd, offset(rs1) //offset[11:0] (-2048 ~ 2047)
li  rd, imm  //rd = imm
lui rd, imm  //rd = ( (imm&0xFFFFF) << 12 )
```

```markdown
li    t0, 0x80200000
lw    t1, 12(t0) //t1=0xffffffffff810113
lwu   t2, 12(t0) //t2=0xff810113
```

```markdown
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

```markdown
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

```markdown
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

```markdown
sll --- shift left logic       逻辑左移，最高位被丢弃，最低位补0.
srl --- shift right logic      逻辑右移，最低位被丢弃，最高位补0.
sra --- shift right arithmetic 算术右移，最低位会被丢弃，最高位会按照符号进行扩展.
```

```markdown
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

下面是大于等于32位的左移C代码反汇编效果：

```markdown
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

下面是逻辑右移和算术右移的实验(没有带w后缀，表示根据寄存器长度来处理)：

```markdown
	li      t0, 0x8000008a00000000 //t0=0x8000008a00000000
	srai    a1, t0, 1 //a1=0xc000004500000000
	srli    a2, t0, 1 //a2=0x4000004500000000
```

下面是逻辑右移和算术右移的实验(带w后缀，表示只处理低32位)：

```markdown
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

```markdown
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

```markdown
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

![[Pasted image 20251222150311.png]]


基于寄存器的位操作指令：

```markdown
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

异或：相异为1，相同为0；以下是关于异或的妙用. （1）交换两个数，a=0001, b=0110 —— a=a^b; b=b^a; a=a^b （2）寄存器清零：xor x1, x1 （3）判断两个数是否相等：`( (a^b) == 0 )`

---

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

---

下面是在 [[godbolt.org]] 函数外面定义了全局变量，然后转换成 RV64 汇编代码如下：

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

---

C语言转换成汇编代码（在线）：[[godbolt.org]]

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

---

分支跳转

C语言转换成汇编代码（在线）：[[godbolt.org]]

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

---

**实例：CSR寄存器读写**

课程位置：第4季5 RISC-V指令集 par8 指令全称：CSR (Current Status Register 存放处理器当前状态的寄存器) 指令清单：csrrw 、csrrs 、csrrc、csrrwi 、csrrsi 、csrrci 指令格式：

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

---

**实例：ret指令陷阱**

执行call指令后，CPU会修改ra指令来保存当前+4位置的地址；执行 ret 指令之后，CPU会读取 ra 寄存器，ra 寄存器等同于 LR 寄存器，保存着调用点下一个指令的地址。但是如果函数层层调用，则 ra 寄存器的值会被覆盖，上上层的地址位置信息会被丢失。为了解决这个问题，需要用栈来临时保存 ra 寄存器的值。

验证方法： （1）执行 call 之前，查看 ra 寄存器的值 （2）执行 call 之后，即进入子函数之后，查看 ra 寄存器的值，看是否变化了. （3）结论是，一旦进入子函数，ra 寄存器的值就变了

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

---

**实例：汇编实现串口打印**

理论依据： （1）串口控制器工作原理 （2）汇编基础

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

---

**实例：汇编与宏定义**

```cpp
#define UART_IER (0x10000000 + 1)
la t0, UART_IER //load macro value into t0
```

---

**函数调用规范**

函数调用规范可以总结出如下规则： （1）函数的前8个参数使用a0~a7寄存器来传递，如果函数参数大于8个，后面的参数使用栈来传递。 （2）如果传递的参数小于寄存器宽度 (64位) ，那么符号扩展到64位。 （3）如果传递的参数为2倍的寄存器宽度 (128位)，那么将使用一对寄存器来传递该参数。 （4）函数的返回参数保存到a0~a1寄存器中（return 6; //a0=6）。 （5）函数的返回地址保存在ra寄存器中（PC=fn_call_pos + 4）。 （6）如果子函数里使用s0~s11寄存器，那么子函数在使用前需要把这些寄存器的内容保存到栈中，使用完成之后再从栈中恢复内容到这些寄存器里。 （7）栈向下增长(向较低的地址)，栈指针寄存器SP在程序进入时要对齐到16字节边界上。 （8）传递给栈的第一个参数位于栈指针寄存器的偏移量0处，通过反汇编可以快速获知。 （9）如果GCC使用了 `-fno-omit-frame-pointer` 编译选项，那么编译器使用s0作为栈顿指针FP。 （10）结构体位域 (bitfield) 按照小端来排布。它会填充到下一个整型类型(int32)对齐的地方。

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

Part4 栈的回溯：操作系统常用的输出栈信息等技术手段底层都是通过栈帧指针FP来回溯整个栈。

1、不使用FP，GCC使用 "-fomit-frame-pointer" 编译选项，这样在函数入栈出栈时减少访问内存的指令，从而提高程序的性能。 2、使用FP，GCC使用 "-fno-omit-frame-pointer" 编译选项，这样在调试过程中方便计算每个栈帧大小以便回溯。

---

**栈回溯**

1、OS常用的输出栈信息等技术手段就是通过FP完成的，通过栈的回溯技术输出函数调用关系.

```
Call Trace:
[<0x0000000080202edc>] test_access_unmap_address+0x1c/0x42
[<0x0000000080202f12>] test_mmu+0x10/0xla
[<0x000000008020329a>] kernel_main+0xb4/0xb6
```

2、下面通过一个示例分析如何通过 FP 回溯整个栈。 [例4-4]在例4-3 的基础上，输出每个栈的范围，以及调用该函数时的PC值，如下面的日志信息所示。

```
Call Frame:
[0x0000000080202fa0-0x0000000080202fb0] pc 0x0000000080200f32
[0x0000000080202fb0-0x0000000080202fd0] pc 0x000000008020114a
[0x0000000080202fd0-0x0000000080202ff0] pc 0x0000000080201184
[0x0000000080202ff0-0x0000000080203000] pc 0x00000000802011a4
```

3、如果想把 PC 值对应的符号名称(函数名称)显示出来，需要建立一个符号名称与地址的对应表，然后查表，本示例中，我们没有满足这个需求。不过，读者可以通过查看 benos.map 文件的符号表信息确定PC 值对应的函数名称。下面是实现栈回溯的示例代码。

---

**实验：GDB观察栈布局**

1、实验目的：熟悉RISC-V的栈布局. 2、实验要求： （1）首先使能FP，即通过gcc编译选项 "fno-omit-frame-pointer" （2）在benos里实现函数调用 kernel_main() >> func1() >> func2()，然后使用GDB观察栈的变化情况.

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

---

**实验：如何实现栈回溯**

1、实验目的：熟悉RV的栈回溯 2、在benos里实现函数调用 kernel_main >> func1 >> func2，并实现一个栈回溯功能，输出栈的地址范围和大小，并通过 GDB 观察栈是如何回溯的。

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
			printk("sp:0x%016lx, fp:0x%016lx, pc:0x%016lx\\\\n",sp,fp,pc);

		ra = *(fp-8); //伪代码:获取 curr_ra
		sp = fp; //sp = curr_fp
		fp = *(fp-16);//fp = prev_fp
		pc = (ulong)ra - 4;//获取调用点地址
	}
}

void dump_stack(void)
{
	printk("Call Frame:\\\\n");
	walk_stackframe();
}
```

---

**RISC-V GNU AS汇编器**

GCC AS 汇编器采用 AT&T 语法格式。

（1）预处理：`gcc -E test.c -o test.i` （2）编译： `gcc -S test.i -o test.S` （3）汇编： `as test.S -o test.o` （4）链接： `ld -o test.elf test.o -lc`

ELF文件常见的各个段： （ .symtab ）用来存放函数、全局变量的符号表信息. （ .debug ）存放调试使用的符号表信息.

---

**数字标签跳转**

1、符号可以代表它所在的地址，也可以当作变量或者函数来使用.

下面是数字标签跳转代码的同等功能代码对比：

![[Pasted image 20251222150423.png]]

**数据定义伪指令**

```markdown
.equ: 给符号赋值
.asciz: 在字符串末尾自动插入'\\0'字符.
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

---

**实验：把某局部代码链接到指定段**

```cpp
.pushsection ".my.text", "awx"
...
.popsection
```

---

**实验：C语言调用汇编函数**

汇编函数只要通过 .global 声明一下，C语言那边也extern声明一下，C语言就可以调用汇编函数.

**实验：汇编调用C语言函数**

C语言这边需要 extern 声明一下，汇编这边就可以直接调用，就是注意一下栈帧以及参数即可.

---

**实验：几种汇编跳转指令**

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


# 异常

关于 mcause 寄存器中的值:
EC(Exception Code), Interrupt(1=中断, 0=异常)

```cpp
Interrupt --- Exception Code --- Description
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




































