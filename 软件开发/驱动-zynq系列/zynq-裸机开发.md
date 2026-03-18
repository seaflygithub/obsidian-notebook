

草稿: [[zynq-boot.bin.excalidraw]]

# ARM汇编学习起点

**ZYNQ开发板黑金AX7020裸机实验**

## XSDK汇编单步调试

1、实验平台

- 硬件平台：笔记本电脑、ZYNQ开发板（黑金AX7020）
- 软件平台：Win10 + Vivado SDK 2018.3 、串口软件、Vscode等等。
- 源代码：rt-thread v4.x+、xsdk bsp 2018.3+、Linux kernel 4.x+
- 作者邮箱：<font color=blue>[[mailto:seafly0616@qq.com]]</font>

**一、实验目的描述**

（1）实验基于 ZYNQ 7000 开发板（AX7020） （2）主要用于建立汇编单步运行环境，来学习和探究汇编指令的具体行为。

**二、工程结构描述**

工程搭建： （1）新建 XSDK 工程，使用 Standalone + Helloworld 模板。 （2）修改源文件清单：（后续将是完整源文件内容）

```cpp
xxx.sdk/hello/src/helloworld.c         //调度器实现和调用
xxx.sdk/hello/src/asm_debug.S          //汇编源文件
```

汇编源文件模板：

```cpp
.section .text, "ax"

.global assembly_step_debug
assembly_step_debug:
    mov        r0, #6
    mov        r1, #16
    bx         lr  /* function returns */
```

main函数调用汇编函数：

```cpp
int main()
{
    init_platform();

    extern void assembly_step_debug(void);
    assembly_step_debug();
    xil_printf("hello world!\\\\r\\\\n");

    cleanup_platform();
    return 0;
}
```

![[Pasted image 20251225164831.png]]


**三、核心原理描述**

（1）直接利用完备的XSDK环境，新建汇编函数，双击建立断点，即可汇编调试。

**四、运行效果描述**

通过 Debug As 方式下载到板卡运行后，可以通过寄存器窗口查看各个寄存器值的变化，以及内存的变化。

操作演示动态图GIF：

![[gif202307141010.gif]]



## ARM寄存器基础

常见寄存器的功能:

- LR(r14)用于保存子程序的返回地址，也用于保存中断的返回地址.
- PC(r15)由于 ARM 采用了流水线机制，当正确读取了 PC 的值后，该值为当前指令地址加 8 个字节，即 PC 指向当前指令的下两条指令地址。CPSR(current), SPSR(Saved).
- CPSR和SPSR都是程序状态寄存器，其中SPSR是用来保存中断前的CPSR中的值，以便在中断返回之后恢复处理器程序状态。

## arm-asm：CPSR和SPSR访问

参考资料：《 ARM Architecture Reference Manual.pdf 》

**一、获取处理器模式**

（1）CPSR：用来表示处理器**当前状态**的寄存器. （2）SPSR：用来保存处理器**上一个状态**的寄存器(Save).

```cpp
// Following asm code must write into xxx.S file
.globl get_cpu_cpsr
get_cpu_cpsr:
	MRS r0, CPSR //r0=CPSR
	bx  lr       //return

.globl get_cpu_spsr
get_cpu_spsr:
	MRS r0, SPSR //r0=SPSR
	bx  lr       //return

int main(void)
{
	...
    extern uint32_t get_cpu_cpsr(void);
    extern uint32_t get_cpu_spsr(void);
    xil_printf("spsr cpu mode is 0x%02x\\\\r\\\\n", get_cpu_spsr() & 0x1F);
    xil_printf("cpsr cpu mode is 0x%02x\\\\r\\\\n", get_cpu_cpsr() & 0x1F);
	    //0x10:usr mode
	    //0x11:fiq mode
	    //0x12:irq mode
	    //0x13:svc mode
	    //0x17:abt mode
	    //0x1B:und mode
	    //0x1F:sys mode
    ...
}

```

---

**二、全局中断开关**

```cpp
//rt_base_t rt_hw_interrupt_disable();
.globl rt_hw_interrupt_disable
rt_hw_interrupt_disable:
    mrs r0, cpsr
	//cpsr intr bit field diable (set 1 to disable)
    cpsid i
    bx  lr

//void rt_hw_interrupt_enable(rt_base_t level);
.globl rt_hw_interrupt_enable
rt_hw_interrupt_enable:
    msr cpsr, r0  //set cpsr, cpsr=r0
    bx  lr

```

---

**对处理器模式的判断对我们来说有什么作用呢？** 为了方便我们知道我们当前所处在的处理器模式，根据模式来压栈备份栈帧。

---

## arm-asm：R0寄存器

R0寄存器可以用来存储函数的返回值，比如下列同一函数的两个实现，都能返回数值16.

```cpp
.globl get_fn_number
get_fn_number:
	mov  r0, #16
	bx   lr

int get_fn_number(void) { return 16; }

```

## arm-asm：LR寄存器

栈帧切换，即当AAA函数调用BBB函数时，栈帧从AAA切换到BBB的过程，这个过程我们需要熟悉一下。

如下图所示，运行时，单步调试的情况下，当PC指针指向调用BBB的语句时，此时PC指针为【 addr+0 】；当单步运行到函数BBB内部，此时PC指针的值为函数BBB的首地址，LR寄存器的值为【 addr+4 】，当运行完BBB函数后，返回时，PC指针被赋值为【 addr+4 】，即表示CPU即将要运行下一条指令。

![[Pasted image 20251225165101.png]]

## arm-asm：内存访问

**一、直接访问某地址**

```cpp
.section .text, "ax"
.globl access_memory
access_memory:
	ldr r3, =0x200000
	ldr r0, =0x12345678

	str r0, [r3] //wr_mem (store, write mem)
	ldr r1, [r3] //rd_mem (load, read mem)

```

```cpp
//两点注意: 取地址, 取数据
.globl seafly_code_debug
seafly_code_debug:
    ldr r0, =temp_data  //& = 0x10E0A8  r0=0x10E0B8
    ldr r1, temp_data   //& = 0x10E0AC  r1=0x12345678
    ldr r2, =0x12345678 //& = 0x10E0B0  r2=0x12345678
    ldr r3, =array_data //& = 0x10E0B4  r3=0x10E0CC
    ldr r4, array_data  //& = 0x10E0B8  r4=0x11111111
    ldr r5, [r3, #4]    //& = 0x10E0BC  r5=0x22222222
    ldr r6, [r4, #4]    //& = 0x10E0C0  r6=0xFFFEF5FF
    bx  lr

temp_data:
	.word 0x12345678 //&temp_data = 0x10E0C8

array_data:          //&array_data    = 0x10E0CC
	.word 0x11111111 //&array_data[0] = 0x10E0CC
	.word 0x22222222 //&array_data[1] = 0x10E0D0
	.word 0x33333333 //&array_data[2] = 0x10E0D4

```

---

**二、访问变量地址**

（1）汇编声明该变量，并修改该变量值：

```cpp
.globl g_ldr_var111
.globl asm_modify_gvariable
asm_modify_gvariable:
	LDR		r1, =0x66666666
	LDR		r3, =g_ldr_var111
	STR		r1, [r3]
	ADD		r4, r1, #1
	BX		lr

```

（2）C语言定义该全局变量，调用汇编之后，读取该变量值：

```cpp
int g_ldr_var111 = 0x1111;
int main()
{
	...
    extern void asm_modify_gvariable(void);
    asm_modify_gvariable();
    xil_printf("g_ldr_var111 is 0x%x\\\\r\\\\n", g_ldr_var111);
    ...
}

```

---

（1）汇编语言声明并修改该变量值：

```cpp
.extern g_var_nest
g_var_nest_asm: .word g_var_nest

.globl asm_write_var
asm_write_var:
    ldr    r0, =0x1234
	ldr    r3, g_var_nest_asm
	str    r0, [r3]
	bx     lr

```

（2）C语言定义并读取该变量值：

```cpp
int g_var_nest = 0;
int main()
{
	...
    extern void asm_write_var(void);
    asm_write_var();
    xil_printf("g_var_nest is 0x%x\\\\r\\\\n", g_var_nest);
    ...
}

```

## arm-asm：压栈出栈

```cpp
.globl arm_asm_debug
arm_asm_debug:
	ldr r0, =0x00000000
	ldr r1, =0x11111111
	ldr r2, =0x22222222
	ldr r3, =0x33333333
	ldr r12,=0x12121212
	ldr lr, =0x14141414
	stmdb	sp!,{r0-r3,r12,lr}  //push into stack(memory)
	// ldmia sp!,{r0-r3,r12,lr} //pop

	// The above stack push instruction is equivalent to:
	// sp = sp-4; [sp] = lr
	// sp = sp-4; [sp] = r12
	// sp = sp-4; [sp] = r3
	// sp = sp-4; [sp] = r2
	// sp = sp-4; [sp] = r1
	// sp = sp-4; [sp] = r0

```

![[Pasted image 20251225165123.png]]

## arm-asm：函数传参（一）

搜索关键字：arm 汇编 函数 传参

（$）子程序通过寄存器R0~R3来传递参数，子程序在返回前无需恢复寄存器R0~R3的内容. （$）子程序进入时必须保存这些寄存器的值,在返回前必须恢复这些寄存器的值. （$）寄存器R13用作数据栈指针,寄存器SP在进入子程序时的值和退出子程序时的值必须相等. （$）寄存器R14用作连接寄存器,它用于保存子程序的返回地址. （$）函数如果有返回值，则返回值存放在R0寄存器.

**一、不超过四个参数**

（1）C语言实现并调用：

```cpp
int func_le4(int a, int b, int c, int d)
{
	int sum = 0;
	sum = a + b + c + d;
	return sum;
}

int func_gt4(int a, int b, int c, int d, int e, int f, int g)
{
	int sum = 0;
	sum = a + b + c + d + e + f + g;
	return sum;
}

int main()
{
    int data = 0;
    data = func_le4(1, 2, 3, 4);
    xil_printf("data is %d\\\\r\\\\n", data);//10

    data = func_gt4(1, 2, 3, 4, 5, 6, 7);
    xil_printf("data is %d\\\\r\\\\n", data);//28
}

```

执行类似如下命令，编译生成反汇编文件：

```bash
arm-none-eabi-gcc -g -c func.c
arm-none-eabi-objdump -S -D func.o > func.S

```

```cpp
00000000 <func_le4>:
   0:  push	{fp}		; (str fp, [sp, #-4]!)
   4:  add	fp, sp, #0
   8:  sub	sp, sp, #28
   c:  str	r0, [fp, #-16]
  10:  str	r1, [fp, #-20]
  14:  str	r2, [fp, #-24]
  18:  str	r3, [fp, #-28]

```

如图所示，在PC指针指向函数后，r0~r3自动就载入了前四个参数。

![[Pasted image 20251225165138.png]]


## arm-asm：函数传参（二）

**二、超过四个参数**

总结：当函数参数大于4个的时候，前面4个参数仍然会通过r0~r3传递，而后续的参数则通过压栈的方式传递，压栈由调用者来完成。具体细节后续探究。

![[Pasted image 20251225165157.png]]

如上图所示，可以了解到SP和FP之间的关系，以及知道了局部变量存放在当前栈帧内，a,b,c,d前四个参数分别存放在r0,r1,r2,r3，多余四个参数的情况下，这些多出来的参数存放在调用者的栈帧内。

![[Pasted image 20251225165210.png]]

如上图所示，上图是根据 func_temp 的C代码反汇编代码构造出的栈帧布局图，能够学到caller和called的栈帧构造流程。在单步调试运行的环境下，下面用汇编实现的函数 func_temp，没有保存栈帧和更新栈帧的行为，所以即使进入函数后，SP和FP还是上一个栈帧的信息，通过如下运行代码得以验证。

![[Pasted image 20251225165224.png]]



下面是手动保存栈帧的汇编代码：

```cpp
//func_temp(a,b,c,d,e,f,g);
.globl func_temp
func_temp:
	//save prev stack frame
	str fp, [sp, #-4]

	//set cur stack frame
	sub sp, sp, #4
	sub sp, sp, #4
	add fp, sp, #0  // fp=sp

	//function code
	bx	lr

```

## arm-asm：栈帧探究

**一、什么是栈帧**

如下图所示，栈帧就是框起来的部分，FP标记栈帧的起始，SP标志栈帧的顶点. 该图的绘制是根据前面的反汇编代码绘制出来，从图中看出，上一个SP和下一个FP紧挨着，事实上从反汇编代码也能看出. 不同处理器架构栈帧的结构可能有所差异，主要差异表现在是满栈还是空栈，升栈还是降栈。ARM体系结构，采用【满栈+降栈】，即满栈表示SP指向的地址有数据，如果需要往SP压入数据，则需要移动SP指针到下一格，才能往SP所在地址写入数据；降栈表示SP生长方向在内存地址上表现为从高地址往低地址生长.

![[Pasted image 20251225165244.png]]


**二、栈帧探究实验**

我们通过实验来验证push栈帧寄存器，以及push通用寄存器来探究push指令的功能.

```cpp
.globl get_fn_number
get_fn_number:
	//get prev fp,sp
	mov  r0, fp
	mov  r1, sp

	//fp: only backup prev fp
	//sp: sp = sp-4
	push {fp}

	//fp: set current fp (fp = sp)
	add fp, sp, #0

	//fp: restore prev fp
	//sp: restore prev sp
	pop  {fp}

	bx   lr

```

通过上述实验代码的单步调试和现象观察，得知了上述的 push 语句分别做了两个动作： （1）把 prev fp 备份到内存，这里的内存指 sp-4 所在的内存. （2）修改 sp 指针，sp=sp-4 同理，上面pop语句的作用是恢复 prev fp 和 prev sp，总之 push/pop 是专为FP/SP服务的指令.

上述的push语句等同于(已通过实验验证)：

```cpp
	sub  sp, sp, #4
	str  fp, [sp]
	mov  fp, sp

```

## arm-asm：从VA到PA

【一分钟讲逻辑转换从虚拟内存到物理内存-动画版】 [[?share_source=copy_web&vd_source=68693d83d0a1db19f6c27c633ba93f95]]

![[Pasted image 20251225165300.png]]



## ARM内联汇编

[[13169391]]

在 C 代码中嵌入汇编需要使用 asm 关键字，用法asm volatile();

```cpp
asm volatile(
	"  \\\\n\\\\t"      引号内部包含的部分是指令部分
	: 输出运算符列表(参数输出部分  函数的返回值)
	: 输入运算符列表(参数输入部分  函数的形参)
	: 被更改资源列表(内联汇编的声明部分，要被更改的资源)
);

```

## 上下文保存与切换

1、源代码可参考现成的 rt-thread arm部分的代码，其中相关的函数有 `rt_hw_context_switch_to`、`rt_hw_context_switch`、`rt_hw_context_switch_interrupt` 这几个跟上下文切换相关的函数，不同处理器的实现代码不同，参考rt-thread源码目录下的libcpu目录。

启动之初，即设置异常向量表之后，下一步就是设置处理器模式，需要确保设置成SVC模式，否则到后面有些寄存器你程序无权修改，也就是你的修改并不会生效到对应寄存器。

2、下面是 `rt-thread-v5.0.0/libcpu/arm/cortex-a/context_gcc.S` 相关的实现代码以及注释:

```cpp
/*
 * void rt_hw_context_switch_to(rt_uint32 to, struct rt_thread *to_thread);
 * r0 --> to (thread stack)
 * r1 --> to_thread
 */
.globl rt_hw_context_switch_to
rt_hw_context_switch_to:
    ldr sp, [r0]            @ get new task stack pointer

#ifdef RT_USING_SMP
    mov     r0, r1
    bl      rt_cpus_lock_status_restore
#ifdef RT_USING_SMART
    bl      rt_thread_self
    bl      lwp_user_setting_restore
#endif
#else
#ifdef RT_USING_SMART
    bl      rt_thread_self
    mov     r4, r0
    bl      lwp_aspace_switch
    mov     r0, r4
    bl      lwp_user_setting_restore
#endif
#endif /*RT_USING_SMP*/

    b       rt_hw_context_switch_exit

```

chat: 请问 ldmfd sp!, {r0-r12,lr,pc}^ 和 ldmfd sp!, {r0-r12,lr,pc} 有什么区别？

在 ARM 汇编语言中，`ldmfd` 指令用于从栈中加载多个寄存器的值，并同时恢复堆栈指针 (SP)。这两个指令 `ldmfd sp!, {r0-r12,lr,pc}^` 和 `ldmfd sp!, {r0-r12,lr,pc}` 在使用时有一个重要的区别：

1. **`ldmfd sp!, {r0-r12,lr,pc}^`：** 在这个指令中，`^` 符号表示载入完整的寄存器列表后，还会回到上一个模式的状态，即将 CPU 恢复到之前的状态。这通常用于 ARM 中的子程序调用，从子程序返回时，会使用 `ldmfd sp!, {r0-r12,lr,pc}^` 指令来从堆栈中恢复所有寄存器的值，并返回到调用该子程序之前的指令执行状态。
2. **`ldmfd sp!, {r0-r12,lr,pc}`：** 在这个指令中，没有使用 `^` 符号，因此在载入完整的寄存器列表后，并不会回到上一个模式的状态。这意味着执行这个指令后，CPU 的模式将保持不变。通常情况下，这个指令用于从堆栈中恢复寄存器的值，并跳转到一个新的地址，而不需要返回到之前的状态。

综上所述，这两个指令的主要区别在于是否使用 `^` 符号，以及它们在使用时的场景和目的。 `ldmfd sp!, {r0-r12,lr,pc}^` 用于子程序调用返回，而 `ldmfd sp!, {r0-r12,lr,pc}` 则用于从堆栈中恢复寄存器的值并跳转到一个新的地址。

**STMFD和LDMFD**: store, Multiple, Full, Descending，M表示会操作多个寄存器，即可能会把多个寄存器压栈或出栈；F表示满栈，即SP指针指向的当前格子是满的有数据的，如果需要往栈里push东西，就需要先把sp-4之后，才能往里面push新的数据；D表示降栈，即随着压栈的行为发生，栈的生长方向是递减，即从高地址往低地址生长，比如32位平台，每压栈一次，SP指针就减4。

chat: rt_hw_stack_init()函数的实现依据是什么? 用于初始化线程的栈空间。在RTT中，每个线程都需要有自己的栈空间，用于存储函数调用过程中的局部变量、函数返回地址等信息。栈空间是线程运行时的临时工作区域。

Computer Architecture —— ISA 指令集架构介绍 （一）：为什么需要 ISA\ [[345307861]]

ARM指令STMFD和LDMFD、PUSH和POP区别深入详解\ [[90449502]]







# fpga基础：verilog基础

参考资料：

- 《1_ZYNQ小系统板之FPGA开发指南_V1.0.pdf》
- 《course_s1_ZYNQ那些事儿-FPGA实验篇V1.06.pdf》

1、笔记目的：需要知道如何用起来现有例程，根据现有例程进行扩展或者优化。作为ZYNQPS软件开发人员，硬件资源对于软件这边来说就是各种寄存器，寄存器，寄存器，还是寄存器；而对于逻辑开发人员，听到最多的就是时序，信号，时序，信号，时序，信号。所以这里作为 ZYNQPS 人员，有必要掌握 ZYNQPL 相关的基础知识，以便能够更好地配合逻辑人员调试目标设备。

学习路线参考：【入行十年，我总结了这份FPGA学习路线：搞定这四点，你也能轻松进阶】 [[BV1aK4y1E7nc]]

**FPGA编程语言** 对于verilog学习，强烈推荐[[Main_Page]]

**FPGA基础知识** 主要两部分：专业基础课（电路、数电、计算机体系结构、接口、数字信号处理等等），另一部分是FPGA芯片的结构。 FPGA芯片结构：基本组成单元结构（查找表、逻辑单元、逻辑块、DSP、存储器等） FPGA开发流程：RTL设计、仿真验证、逻辑综合、布局布线、时序收敛、下载硬件调试。

**FPGA开发工具**：入门阶段建议坚持使用一个平台（vivado或者quartus）。

**FPGA动手实验**：强烈建议需要用开发板。

## ZYNQPL-最简单的纯仿真

1、万事开头难，首先vivado仿真不依赖开发板，也就是不需要连接硬件。这里所说的纯仿真，就是只有仿真代码，没有模块代码。

2、随便新建一个vivado工程（本人用的vivado 2018.3 版本）。

3、选择仿真器(默认选择vivado自带仿真器)：

![[Pasted image 20251225164000.png]]


4、编写仿真代码(仿真激励文件代码)：

![[Pasted image 20251225164022.png]]


```verilog
`timescale 1ns/1ns

module testbench_hello();
reg sys_clk;
reg sys_rst_n;

//每10ns翻转一次，那么就能产生周期为20ns的时钟信号，换算成频率为50MHz
always begin
    #10
    sys_clk = ~sys_clk;
end

//下面这个代码和上面是一样的效果
//always #10 sys_clk = ~sys_clk;

initial begin
	sys_clk = 0;
	sys_rst_n = 1;
	#20
	sys_rst_n = 0;
end //initial

endmodule

```

5、开始仿真：vivado主界面最左边 >> Run Simulation >> Run Behavioral Simulation，此时就会弹出仿真时序界面。

![[Pasted image 20251225164038.png]]



6、工程窗口切换

![[Pasted image 20251225164051.png]]


7、查看仿真全局效果

![[Pasted image 20251225164104.png]]


8、每次修改代码，如果要立即生效，就再次点击vivado主界面最左边 >> Run Simulation >> Run Behavioral Simulation。

## ZYNQPL-最简单的代码仿真

1、比如我们实现了一个与门模块，我们要验证其正确性，于是为其写了testbench，这在模块调试时候非常有用，无需依赖实际硬件。

2、基于前面新建的vivado工程，新增verilog源文件，把下面的与门模块代码放到文件里。

```verilog
`timescale 1ns / 1ns

module mygate_and(a,b,c);
input    a;
input    b;
output   c;

assign c = a & b;

endmodule

```

3、修改 testbench 文件，内容如下：

```verilog
`timescale 1ns/1ns

module mygate_and_tb();
    reg  a;
    reg  b;
    wire c;

    initial begin
        a = 0;
        b = 0;
        forever begin
            #({$random}%100) //range is 0:(100-1)
            a = ~a;
            #({$random}%100) //if $random % 100, the range is -(100-1):(100-1)
            b = ~b;
        end
    end

    mygate_and u_mygate_and(
        .a    (a),
        .b    (b),
        .c    (c)
    );
endmodule

```

4、模块文件和仿真文件修改完成后，直接点击vivado主界面最左边 >> Run Simulation >> Run Behavioral Simulation。
![[Pasted image 20251225164124.png]]



关于FPGA设计仿真和硬件实测不一致问题的讨论 [[51896958]]

- 一个良好的习惯就是每个寄存器变量都要在reset里面预先定义初值.
- 阻塞和非阻塞赋值在always里面混用是RTL设计的大忌.
- 时序收敛问题: 虽然时序是个大问题,不过一定要首先在确定功能正确后再着手动时序这块,你会发现绝大部分仿真通过但是实测不过的原因还是代码的功能有问题,而由于一些原因没有仿真到.
- 记住一句话,复杂设计的仿真绝对不能局限在肉眼一点一点看波形,绝大多数的bug是要编程靠程序自动发现的!

## ZYNQPL-Verilog基础

1、Verilog的数据类型：在Verilog语法中，主要有三大类数据类型，即寄存器型、线网类型和参数类型。其中真正在数字电路中起作用的是寄存器类型和线网类型。其中，寄存器类型只能在always和initial语句中被赋值。如果always语句块是组合逻辑，那么该寄存器变量就变为硬件连线；寄存器类型的缺省值是X（未知状态）。线网类型就是元件之间的物理连线，缺省值为Z（高阻态）。参数类型，其实就是常量，常用于定义状态、数据位宽、延迟大小等等。由于它可以在编译时修改参数的值，因此它又被常用于一些参数可调的模块中，让用户在实例化模块时，可以根据需要修改参数值。我们需要注意的是参数的定义是局部的，只在当前模块中有效。

![[Pasted image 20251225164141.png]]


2、Verilog的拼接运算符：其他运算符和C语言类似，这里就不探究了，唯独这个拼接运算符比较特殊。这里就是指【位拼接运算符】，拼接运算符可以把两个或者多个信号的某些位拼接起来进行运算操作。

```verilog
wire a[3:0], b[3:0];
wire c[7:0];
assign c = {a, b}; //比如a=4'b1101, b=4'b1100, 那么c=8'b1101_1100

wire w[7:0];
assign w = {8{1'b1}}; //把w初始化为8‘b1111_1111, 错误的写法为: assign w = {8{1}};

```

3、assign和always区别：assign语句使用时不能带时钟，always语句可以带时钟也可以不带时钟。在always不带时钟时，逻辑功能和assign完全一致，都是只产生组合逻辑。比较简单的组合逻辑用assign，比较复杂的组合逻辑推荐使用always语句。

```verilog
wire [1:0] a;
assign a = x & y;       // Explicit assignment(显式赋值)

wire [1:0] a = x & y;   // Implicit assignment(隐式赋值)

```

4、模块的输入输出端口类型都默认为wire型，wire相当于物理连线，默认初始值是z（高组态）。reg相当于存储单元，默认初始值是x（未知状态）。在设计中，输入信号一般来说你是不知道上一级是寄存器输出还是组合逻辑输出，那么对于本级来说就是一根导线，也就是wire型。而输出信号则由你自己来决定是组合逻辑输出还是寄存器输出，wire型、reg型都可以。但一般的，整个设计的外部输出（即最顶层模块的输出），要求是寄存器输出，较稳定、扇出能力也较好。【原文链接：[[104228223%E3%80%91%E3%80%82%E6%89%87%E5%87%BA%E6%98%AF%E4%BB%80%E4%B9%88%E6%84%8F%E6%80%9D]][[104228223%E3%80%91%E3%80%82%E6%89%87%E5%87%BA%E6%98%AF%E4%BB%80%E4%B9%88%E6%84%8F%E6%80%9D]]? 是指该模块直接调用的下级模块的个数。wire可以理解为一捆线，这一捆可以只有一根导线(默认1个bit)，也可以有多根导线(多个bit)。

5、**阻塞赋值与非阻塞赋值**：

阻塞赋值，顾名思义，即在一个 always 块中，后面的语句会受到前语句的影响，具体来说，在同一个 always 中，一条阻塞赋值语句如果没有执行结束，那么该语句后面的语句就不能被执行，即被 "阻塞"。下面就是阻塞语句，0会按顺序直接透传给a,b,c器件。这里的透传没有时序概念，即没有过去和未来，当满足触发条件，则0直接透传给a,b,c器件。

```verilog
always @(posedge clk or negedge rst_n) begin
	if (!rst_n) begin
		a = 1;
		b = 2;
		c = 3;
	end
	else begin
		a = 0;
		b = a;
		c = b;
	end
end
```


![[Pasted image 20251225164207.png]]

如上图所示，当t2时刻，(0)值传递给a时，里面就顺序透传给b和c了。因此a,b,c是相连的组合逻辑，前端给a一个数，a里面透传给b,b里面透传给c，没有时间概念，也就是没有先后概念。通常阻塞赋值只需要触发一次always时钟就能完成一次透传赋值。

---

非阻塞赋值是由时钟节拍决定，在时钟上升到来时，执行赋值语句等于号的右边，然后将 begin-end 之间的所有赋值语句同时赋值到赋值语句的左边，注意：是 begin—end 之间的所有语句，一起执行，且一个时钟只执行一次，属于并行执行语句。非阻塞赋值的操作过程可以看作两个步骤：赋值开始的时候，计算RHS；赋值结束的时候，更新LHS。所谓的非阻塞的概念是指，在计算非阻塞赋值的 RHS 以及 LHS 期间，允许其它的非阻塞赋值语句同时计算 RHS 和更新 LHS。

```verilog
always @(posedge clk or negedge rst_n) begin
	if (!rst_n) begin
		a <= 1;
		b <= 2;
		c <= 3;
	end
	else begin
		a <= 0;
		b <= a;
		c <= b;
	end
end

```


![[Pasted image 20251225164224.png]]


如上图所示，t0时刻，a,b,c的值都有一个初始值；t2时刻，(0)传递给a, a把手头上的(1)传递给b, b把手头上的(2)传递给c, c把手头上的(3)传递给下一个器件，由于语句中没有下一个器件，故c丢掉手头上的(3), 即t2时刻，a的值为(0), b的值为(1), c的值为(2); 后续的时刻也同理，时间每走一个时刻，a,b,c就做一次动作，这个动作就是各自往下一级传递值。也就是always语句里的每次非复位常规触发，都会做一次动作，每次动作，大家都会往后移动一下子。

1、如下图所示，跳变对应着

```
always@(posedge clk)
```

触发，探究触发机制的精确时机，跳变的速度(坡度)。

![[Pasted image 20251225164242.png]]


---

什么时候使用阻塞赋值，什么时候使用非阻塞赋值？

- （1）描述组合逻辑电路时，使用阻塞赋值，比如assign赋值语句，以及不带时钟的always语句，这种电路结构只与输入电平的持续高低有关系。比如：

```verilog
assign data = (data_en == 1'b1)? 8'd255:8'd0;

always @(*) begin
	if (en) begin
		a = a0;
		b = b0;
	end
	else begin
		a = a1;
		b = b1;
	end
end

```

- （2）在描述时序逻辑的时候，使用非阻塞赋值，比如带时钟的 always 语句，这种电路往往与触发沿有关系，只有在触发沿时才可能发生赋值的变化。换句话说，这种电路与电平的跳变有关系，就是在跳变的那一瞬间那个陡坡。

```verilog
always @ (posedge sys_clk or negedge sys_rst_n) begin
	if (!sys_rst_n) begin
		a <= 1'b0;
		b <= 1'b0;
	end
	else begin
		a <= c;
		b <= d;
	end
end

```

---

非阻塞赋值案例

1、模块代码

```verilog
module top(clk, rst_n, a, b, c);
input clk;
input rst_n;
output reg [1:0] a = 1;
output reg [1:0] b = 2;
output reg [1:0] c = 3;

always @(posedge clk or negedge rst_n) begin
	if (!rst_n) begin
		a <= 1;
		b <= 2;
		c <= 3;
	end
	else begin
		a <= 0;
		b <= a;
		c <= b;
	end
end

endmodule

```

2、激励文件

```verilog
`timescale 1ns/1ns
module top_tb();
reg   clk;
reg   rst_n;
wire [1:0] a;
wire [1:0] b;
wire [1:0] c;

initial begin
    clk = 0;
    forever begin
        #10; clk = ~clk;
    end
end

initial begin
    rst_n = 1;
    forever begin
        #100; rst_n = ~rst_n;
    end
end

top u_top(
    .rst_n  (rst_n),
    .clk    (clk),
    .a      (a),
    .b      (b),
    .c      (c)
);

endmodule

```

3、仿真效果

![[Pasted image 20251225164306.png]]


6、**latch锁存器与触发器** 锁存器和寄存器都是基本存储单元，锁存器是电平触发的存储器，寄存器是边沿触发的存储器。两者的基本功能是一样的，都可以存储数据。锁存器是组合逻辑产生的，而寄存器是在时序电路中使用，由时钟触发产生的。latch 的主要危害是会产生毛刺（glitch），这种毛刺对下一级电路是很危险的。并且其隐蔽性很强，不易查出。因此，在设计中，应尽量避免 latch 的使用。

代码里面出现 latch 的两个原因是在组合逻辑中，if 或者 case 语句不完整的描述，比如 if 缺少 else 分支，case 缺少 default 分支，导致代码在综合过程中出现了 latch。解决办法就是 if 必须带 else 分支，case 必须带default 分支。大家需要注意下，只有不带时钟的 always 语句 if 或者 case 语句不完整才会产生 latch，带时钟的语句 if 或者 case 语句不完整描述不会产生 latch。

锁存器是电平触发的，触发器是边沿触发的。如果是电平触发的，当使能的时候，如果输入信号不稳定，那么输出就会出现毛刺。而触发器就不会出现这种问题，他的变化只会在边沿的时候触发。在实际的数字系统中，通常把能够用来存储一组二进制代码的同步时序逻辑电路称为寄存器。

## ZYNQPL-阻塞赋值与非阻塞赋值

阻塞赋值操作符是"="，非阻塞赋值操作符是"<="。 阻塞赋值中阻塞的意思是要等一会儿，阻塞了，先让赋值变量得到一个新值，然后阻塞赋值得到的是赋值变量刚刚得到的新值；

非阻塞赋值中非阻塞的意思是要直接传输，不等，得到的是赋值变量的旧值。 非阻塞赋值只能对寄存器类型变量进行赋值，不能用于连续赋值（assign语句）。

```verilog
var    a = 0;
var    b = 1;
var    c = 2;

//代码1: 阻塞赋值
a = 10;
b = a;  //阻塞赋值: b要等a得到新值之后,再用a的新值给b赋值
c = b;  //阻塞赋值: c要等b得到新值之后,再用b的新值给c赋值

//代码2: 非阻塞赋值
a <= 10;
b <= a; //非阻塞赋值: 此时b立马得到a的值,但此时得到的是a的旧值
c <= b; //非阻塞赋值: 此时c立马得到b的值,但此时得到的是b的旧值

```

阻塞赋值的仿真效果表现为，最终大家都是同一个新值。
![[Pasted image 20251225164322.png]]
![[Pasted image 20251225164332.png]]

## ZYNQPL-门电路SR锁存器

1、SR锁存器仿真电路图文件: logisim_202404241050.circ

2、SR锁存器门电路图

![[Pasted image 20251225164348.png]]


3、SR锁存器门电路图实验现象

- 当R=0时，疯狂点击S，一旦S为1，Q也变成1，并且Q后续恒定为1；
- 当R=1时，Q立马变成0，并且即使疯狂点击S，Q恒定为0；

4、FPGA逻辑仿真代码

```verilog
`timescale 1ns/1ns
module hello_top(r, s, q);
input      r;
input      s;
output reg q = 0;

always@(*) begin
    if (r) begin
        q = 0;
    end
    else begin
        if (s == 1) begin
            q = 1;
        end
        else begin
            ; //do nothing
        end
    end
end

endmodule

```

```verilog
`timescale 1ns/1ns
module hello_top_tb();
reg   R;
reg   S;
wire  Q;

initial begin
    R = 0;
    forever begin
        #100; R = ~R;
    end
end

initial begin
    S = 0;
    forever begin
        #12; S = ~S;
    end
end

hello_top u_hello_top(.r(R), .s(S), .q(Q));

endmodule

```

5、仿真时序图如下
![[Pasted image 20251225164406.png]]


6、仿真时序图文字描述

- 上面的仿真时序图是根据本人操作 logisim 电路图中疯狂点击S观察的现象来模拟的时序图；
- 经过硬件仿真现象和逻辑仿真时序的反复对比，确认该时序图遵循 SR锁存器 的工作特性；
- 当R=0时，此时本人疯狂点击S，Q从0变成1之后，就恒定为1了；
- 当R=1时，Q立马变成0，并且恒定为0，无论之前S是高还是低。

7、总结

- always语句带有边沿触发条件,则只有在边沿触发时，相关的时序才有动作。比如对clk上升沿敏感，则只有在上升沿发生的位置，相关的逻辑才会更新，如果没有上升沿，即使前面数据准备就绪了，后面相关的逻辑也不会更新值。
- always语句没有边沿触发条件，即星号，表示当内部数据发生变化的时候(一般是输入的变化)，才会开始工作。
- Verilog初级教程（10）Verilog的always块: [[107052261]]

## ZYNQPL-门电路D型锁存器

1、硬件仿真工具: logisim，硬件仿真文件: logisim_202404240949.circ

2、硬件仿真简图

![[Pasted image 20251225164420.png]]

3、硬件仿真现象描述

- 当LOCK=1时，本人疯狂点击DIN，DOUT没动静；
- 一旦LOCK=0，DOUT立马跟随DIN变动，这也说明了容易受到输入DIN毛刺影响；
- 在LOCK=0期间，本人疯狂点击DIN，DOUT也疯狂跟着变化。

4、FPGA逻辑仿真代码

```verilog
`timescale 1ns/1ns
module hello_top(lock, din, dout);
input      lock;
input      din;
output reg dout;

always @(*) begin
    if (!lock) begin
        dout = din;
    end
    else begin
        ;//do nothing
    end
end

endmodule

```

```verilog
`timescale 1ns/1ns
module hello_top_tb();
reg   lock;
reg   din;
wire  dout;

initial begin
    lock = 0;
    forever begin
        #100; lock = ~lock;
    end
end

initial begin
    din = 0;
    forever begin
        #12; din = ~din;
    end
end

hello_top u_hello_top(.lock(lock), .din(din), .dout(dout));

endmodule

```

5、仿真时序图：根据硬件仿真现象，在草稿纸上绘制时序图，然后用verilog实现这个时序图。

![[Pasted image 20251225164439.png]]

6、仿真时序图文字描述

- 一旦LOCK=0，dout就立即跟随din输出;
- 在LOCK=0期间，本人疯狂点击DIN，DOUT也疯狂跟着变化；
- 一旦LOCK=1，DOUT就不再跟随变化；
- 在LOCK=1期间，本人疯狂点击DIN，DOUT保持不变。

## ZYNQPL-门电路D触发器

1、D触发器仿真文件: logisim_202404241004.circ

2、D触发器门电路图

![[Pasted image 20251225164452.png]]


3、D触发器硬件模拟实验现象

- 当LOCK=0期间，本人疯狂点击DIN，只有DOUT_1跟着疯狂变化；
- 一旦LOCK=1，这一瞬间，DOUT_1输出到DOUT_2；
- 当LOCK=1期间，本人疯狂点击DIN，DOUT_1和DOUT_2都不受影响；
- 一旦LOCK=0，这一瞬间，DIN此刻的值立马输出到DOUT_1。

4、D触发器工作时序描述

![[Pasted image 20251225164508.png]]

5、FPGA逻辑仿真代码

```verilog
`timescale 1ns/1ns
module hello_top(lock, din, dout_1, dout_2);
input      lock;
input      din;
output reg dout_1 = 0;
output reg dout_2 = 0;

always @(*) begin
    if (!lock) begin
        dout_1 = din;
    end
    else begin
        dout_2 = dout_1;
    end
end

endmodule

```

```verilog
`timescale 1ns/1ns
module hello_top_tb();
reg   lock;
reg   din;
wire  dout_1;
wire  dout_2;

initial begin
    lock = 0;
    forever begin
        #100; lock = ~lock;
    end
end

initial begin
    din = 0;
    forever begin
        #12; din = ~din;
    end
end

hello_top u_hello_top(.lock(lock), .din(din), .dout_1(dout_1), .dout_2(dout_2));

endmodule

```

6、FPGA仿真时序图

![[Pasted image 20251225164524.png]]


7、FPGA仿真时序图文字说明

- 当LOCK=0期间，DOUT_1跟随着DIN的疯狂变化而跟着疯狂变化；
- 一旦LOCK=1，一瞬间，DOUT_1此时定住不变，紧接着DOUT_1此时的信号传递给DOUT_2；
- 当LOCK=1期间，DOUT_2的信号恒定不变，因为此时DOUT_1已经被定住了；
- 一旦LOCK=0，一瞬间，DOUT_1的值随着DIN的疯狂变动，也在疯狂变动；
- 边沿触发器的状态改变仅出现在时钟脉冲的上升沿或者下降沿, 而在时钟稳定为0或者1期间, 输入信号都不能进入触发器。

## ZYNQPL-时钟节奏的理解

1、在一个时序系统中，假如该系统的时钟突然暂停(处在一直拉高或者一直拉低的状态)，那么这个系统整个都会像被点穴一样定住不动。只有时钟每跳变一次(上升沿)，整个依赖该时钟的时序逻辑系统就会动一下，跳变一次，动一下，跳变一次，动一下，如此往复。

2、模块代码和激励文件: 下面通过计数器来模拟逻辑系统动一下的场景，即时钟跳变一次，计数器加一下，时钟跳变一次，计数器加一下；另外再弄一个组合逻辑来作对比，看看同样的自增加代码块，一个在组合逻辑里，一个在时序逻辑里，看看它们的运行结果有什么异同。

```verilog
module hello_top(clk, rst_n, cnt1, cnt2);
input clk;
input rst_n;
output reg [3:0] cnt1 = 0;
output reg [3:0] cnt2 = 0;

always @(*) begin
	if (!rst_n) begin
		cnt1 = 0;
	end
	else begin
		cnt1 = (cnt1 + 6);
	end
end

always @(posedge clk or negedge rst_n) begin
	if (!rst_n) begin
		cnt2 <= 0;
	end
	else begin
		cnt2 <= (cnt2 + 1);
	end
end

endmodule

```

```verilog
`timescale 1ns/1ns
module hello_top_tb();
reg   clk;
reg   rst_n;
wire [3:0] cnt1;
wire [3:0] cnt2;

initial begin
    clk = 0;
    forever begin
        #10; clk = ~clk;
    end
end

initial begin
    rst_n = 1;
    forever begin
        #200; rst_n = ~rst_n;
    end
end

hello_top u_hello_top(
    .clk    (clk),
    .rst_n  (rst_n),
    .cnt1   (cnt1),
    .cnt2   (cnt2)
);

endmodule

```

3、仿真时序图: 如下图所示，其中cnt1是组合逻辑器件，cnt2是时序逻辑器件。对于cnt1，可以看出，组合逻辑下的器件一个很明显的特征是没有记忆功能，代码中直接+6是为了更明显体现出这个特性。对于cnt2，当时钟每跳变一次，计数器就加1，时钟每跳变一次，计数器就加1，直到遇到复位，如果时钟不跳变，那么计数器的值就一直不变，并且cnt2具有记忆功能，能记住上一次的值，因此它能自加一不断加上去。

![[Pasted image 20251225164543.png]]

4、时钟节奏总结：我们肉眼可见的时间尺度下，貌似电子世界的时序逻辑系统的工作是连续流畅丝滑的，但是我们深入微观时间尺度，可以看到每个时序逻辑系统都是跟着它们自己所属的时钟节奏一步一步走动的。这样的理解方式，对于我们后续的时序分析和深入学习有很大帮助。

## ZYNQPL-组合逻辑和时序逻辑

1、组合逻辑和时序逻辑的区分: 可以从三个方面(代码、电路图、波形图)来判断；

- 代码层方面: 如果没有上升沿或者带有星号的代码，就仅仅是组合逻辑；
- 电路图方面: 时序逻辑相当于在组合逻辑的基础上加一个D触发器；
- 波形方面: 组合逻辑的波形是时刻反应变化的，与时钟无关；但是时序逻辑的波形不会立刻反映出来，只有在时钟的上升沿才发生变化；
- 应用方面: 在具体的应用中，只要完成实现功能就好，不用细究它使用哪种逻辑，因为组合逻辑能完成的事情，时序逻辑只是晚一个时钟周期出来结果而已。
- 参考资源: 如何区分时序逻辑和组合逻辑？: [[BV17k4y1e71n]]

2、实验代码和激励文件代码

```verilog
module hello_top(clk, rst_n, din, dout1, dout2);
    input       clk;
    input       rst_n;
    input       din;
    output reg  dout1 = 0;
    output reg  dout2 = 0;

    always@(*) begin
        if(!rst_n)
            dout1 = 0;
        else
            dout1 = din;
    end

    always@(posedge clk or negedge rst_n) begin
        if(!rst_n)
            dout2 <= 0;
        else
            dout2 <= din;
    end

endmodule

```

```verilog
`timescale 1ns/1ns
module hello_top_tb();
    reg clk, rst_n, din;
    wire dout1, dout2;

    initial begin
        clk = 0;
        forever begin
            #10; clk = ~clk;
        end
    end

    initial begin
        din = 0;
        forever begin
            #16; din = ~din;
        end
    end

    initial begin
        rst_n = 1;
        forever begin
            #100; rst_n = ~rst_n;
        end
    end

    hello_top u_hello_top(
        .clk     (clk    ),
        .rst_n   (rst_n  ),
        .din     (din    ),
        .dout1   (dout1  ),
        .dout2   (dout2  )
    );

endmodule

```

3、仿真效果图

![[Pasted image 20251225164603.png]]


4、仿真效果图文字说明

- dout1为组合逻辑，不受时钟节奏影响，跟随din同步变化；
- dout2为时序逻辑，受到时钟上升沿影响，只有时钟上升沿才会变化；
- dout2在时钟上升沿之后，dout2数据会一直保持，直到下一个时钟上升沿到来为止；
- 在复位拉低后，所有输出信号都拉低了，由此可见复位信号的判断处理在各个always语句块中最先被执行；
- 代码中每一个独立的always语句块，各自都是并发执行；
- begin-end: 用于将多条语句组成顺序块。 顺序块具有以下特点: (1)顺序块中的语句是一条接一条按顺序执行的，只有前面的语句执行完成之后才能执行后面的语句 (除了带有内嵌延迟控制的非阻塞赋值语句)。 (2)如果语句包括延迟或事件控制,那么延迟总是相对于前面那条语句执行完成的仿真时间的，就像仿真激励文件里面的延时执行。

## ZYNQPL-组合逻辑探究

assign 组合逻辑和`always@(*)`组合逻辑

另外一个区别则是更细微的差别：举个例子:

```verilog
wire    a;
reg     b;
assign  a = 1'b0;

always@(*) begin
	b = 1'b0;
end

```

在这种情况下，做仿真时a将会正常为0， 但是b却是不定态X。这是为什么？verilog规定，`always@(*)` 中的星号是指该always块内的所有输入信号的变化为敏感列表，而且这些敏感列表的敏感条目之间是或的敏感关系，即任何一个敏感条目发生，也就是仿真时只有当 `always@(*)` 块内的输入信号产生变化，该块内描述的信号才会产生变化，而像 `always@(*) b = 1'b0;` 这种写法由于1'b0是常数一直没有变化，所以b的信号状态一直没有改变，由于b是组合逻辑输出，所以复位时没有明确的值（不定态），而又因为 `always@(*)` 块内没有敏感信号变化，因此b的信号状态一直保持为不定态。

verilog 里面，always，assign和`always@(*)`区别: [[101114439]]



# zynq-fsbl-boot.bin

草稿: 

**链接器脚本与地址空间**：

通过 lscript.ld 文件里的 MEMORY 可以获取其地址空间，并画出地址空间分布图。

```cpp
MEMORY
{
   ps7_ddr_0 : ORIGIN = 0x100000, LENGTH = 0x3FF00000
   ps7_qspi_linear_0 : ORIGIN = 0xFC000000, LENGTH = 0x1000000
   ps7_ram_0 : ORIGIN = 0x0, LENGTH = 0x30000
   ps7_ram_1 : ORIGIN = 0xFFFF0000, LENGTH = 0xFE00
}
```

![[Pasted image 20251225162006.png]]


**FSBL-RAM0**：经过实验结果验证，无论是在启动介质(比如SD卡)中，还是JTAG在线下载，FSBL必须在 ps7_ram_0 里，FSBL只能运行在RAM里，大部分运行在RAM0，因为RAM1空间可能不够。

```cpp
MEMORY
{
   ps7_ddr_0 : ORIGIN = 0x100000, LENGTH = 0x3FF00000
   ps7_qspi_linear_0 : ORIGIN = 0xFC000000, LENGTH = 0x1000000
   ps7_ram_0 : ORIGIN = 0x0, LENGTH = 0x30000
   ps7_ram_1 : ORIGIN = 0xFFFF0000, LENGTH = 0xFE00
}

/* Specify the default entry point to the program */
ENTRY(_vector_table)

/* Define the sections, and where they are mapped in memory */
SECTIONS
{
    .text : {
        KEEP (*(.vectors))
        *(.boot)
        *(.text) //The .text of all the files is put here.
        *(.text.*)
        *(.gnu.linkonce.t.*)
        *(.plt)
        *(.gnu_warning)
        *(.gcc_execpt_table)
        *(.glue_7)
        *(.glue_7t)
        *(.vfp11_veneer)
        *(.ARM.extab)
        *(.gnu.linkonce.armextab.*)
    } > ps7_ram_0

    .init : {
        KEEP (*(.init))
    } > ps7_ram_0

    ...
}
```

```cpp
#define log_print_debug(fmt,...) do {\\
    printf("%s:%s():%d:>> ", __FILE__, __func__, __LINE__);\\
    printf(fmt,##__VA_ARGS__);\\
    printf("\\r\\n");\\
}while(0)
```

**FSBL-主流程**：我们现在控制变量法，默认SD卡启动模式，然后FSBL主程序经过简化，可运行的核心代码如下：

```cpp
//This is the main function for the FSBL ROM code.
int main(void)
{
    u32 BootModeRegister = 0;
    u32 HandoffAddress = 0;
    u32 Status = XST_SUCCESS;
    
    //PCW initialization for MIO,PLL,CLK and DDR
    Status = ps7_init();
    if (Status != FSBL_PS7_INIT_SUCCESS) return -1;

    SlcrUnlock();

    Xil_DCacheFlush();
    Xil_DCacheDisable();

    //Register the Exception handlers
    RegisterHandlers();
    Status = InitPcap();

#if defined(XPAR_PS7_SD_0_S_AXI_BASEADDR) || defined(XPAR_XSDPS_0_BASEADDR)
    log_print_debug("Boot mode is SD");
    Status = InitSD("BOOT.BIN");
    MoveImage = SDAccess;
#endif

    HandoffAddress = LoadBootImage();
    log_print_debug("HandoffAddress = 0x%lx", HandoffAddress);
    FsblHandoff(HandoffAddress);//PC = HandoffAddress
    return Status;
}
```

在SD卡启动模式下，下面是一些关键信息：

```cpp
../src/main.c:main():258:>> Boot mode is SD
../src/image_mover.c:LoadBootImage():193:>> Silicon_Version = 3
../src/image_mover.c:LoadBootImage():229:>> Image Start Address: 0x00000000
../src/image_mover.c:PartitionMove():1170:>> //PL
    SourceAddr = 0x100000, Header->LoadAddr = 0x0, Header->ExecAddr = 0x0
../src/image_mover.c:PartitionMove():1170:>> //PS
    SourceAddr = 0x100000, Header->LoadAddr = 0x100000, Header->ExecAddr = 0x100000
../src/main.c:main():264:>> HandoffAddress = 0x100000
../src/helloworld.c:main():28:>> main address is 0x1005b8
```



## **探究BIT文件到BOOT.BIN**

**PcapLoadPartition**：这里我们简化改写了必要的函数，去掉了很多检查和不必要的条件判断。然后重新编译FSBL并下载到开发板，开发板是SD卡启动模式，然后看到必要的日志打印。这里我们探究的是，FSBL如何识别处BOOT.BIN中的比特流文件，并把比特流从BOOT.BIN中读取出来，最终加载到PL端运行。其中最核心的函数就是 PcapLoadPartition 这个函数，它负责把比特流怼到PL硬件里，让PL程序运行起来。

```cpp
u32 LoadBootImage(void)
{
    u32 RebootStatusRegister = 0;
    u32 MultiBootReg = 0;
    u32 ImageStartAddress = 0;
    u32 PartitionNum;
    u32 PartitionDataLength;
    u32 PartitionImageLength;
    u32 PartitionTotalSize;
    u32 PartitionExecAddr;
    u32 PartitionAttr;
    u32 ExecAddress = 0;
    u32 PartitionLoadAddr;
    u32 PartitionStartAddr;
    u32 PartitionChecksumOffset;
    u8 ExecAddrFlag = 0 ;
    u32 Status;
    PartHeader *HeaderPtr;
    u32 EfuseStatusRegValue;
    /*
     * Resetting the Flags
     */
    BitstreamFlag = 0;
    ApplicationFlag = 0;

    RebootStatusRegister = Xil_In32(REBOOT_STATUS_REG);

    //read the multiboot register
    MultiBootReg =  XDcfg_ReadReg(DcfgInstPtr->Config.BaseAddr, XDCFG_MULTIBOOT_ADDR_OFFSET);

    //Compute the image start address
    ImageStartAddress = (MultiBootReg & PCAP_MBOOT_REG_REBOOT_OFFSET_MASK) * GOLDEN_IMAGE_OFFSET;
    log_print_debug("Image Start Address: 0x%08lx\\r\\n",ImageStartAddress);

    //Get partitions header information
    Status = GetPartitionHeaderInfo(ImageStartAddress);

    //分区[0]是存放FSBL的分区,因此从分区[1]开始,而且在裸机SDK中总共只有3个分区(fsbl+bit+elf)
    for (size_t PartitionIdx = 1; PartitionIdx < 3; PartitionIdx++)
    {
        HeaderPtr = &PartitionHeader[PartitionIdx];
        HeaderDump(HeaderPtr);

        //Load partition header information in to local variables
        PartitionDataLength = HeaderPtr->DataWordLen;
        PartitionImageLength = HeaderPtr->ImageWordLen;
        PartitionExecAddr = HeaderPtr->ExecAddr;
        PartitionAttr = HeaderPtr->PartitionAttr;
        PartitionLoadAddr = HeaderPtr->LoadAddr;
        PartitionChecksumOffset = HeaderPtr->CheckSumOffset;
        PartitionStartAddr = HeaderPtr->PartitionStart;
        PartitionTotalSize = HeaderPtr->PartitionWordLen;

        if (PartitionAttr & ATTRIBUTE_PL_IMAGE_MASK)
        {
            log_print_debug("-------------------------- Now in PL Progress");
            PLPartitionFlag = 1;
            PSPartitionFlag = 0;
            BitstreamFlag = 1;
        }

        if (PartitionAttr & ATTRIBUTE_PS_IMAGE_MASK) {
            log_print_debug("-------------------------- Now in PS Progress");
            PSPartitionFlag = 1;
            PLPartitionFlag = 0;
            ApplicationFlag = 1;

            if (!ExecAddrFlag)
            {
                ExecAddrFlag++;
                //直接获取地址,后续这个内存地址会直接交给PC指针
                ExecAddress = PartitionExecAddr;
            }
        }

        //把BOOT.BIN内各个子文件内容从存储介质拷贝到内存中
        Status = PartitionMove(ImageStartAddress, HeaderPtr);
    }

    return ExecAddress;
}

//This function load the partition from boot device
u32 PartitionMove(u32 ImageBaseAddress, PartHeader *Header)
{
    ...
    ...
    
    /*
     * Load Bitstream partition in to fabric only
     * if checksum and authentication bits are not set
     */
    log_print_debug("SourceAddr = 0x%lx, Header->LoadAddr = 0x%lx, Header->ExecAddr = 0x%lx", 
        SourceAddr, Header->LoadAddr, Header->ExecAddr);
    if (PLPartitionFlag && (!(SignedPartitionFlag || PartitionChecksumFlag))) {
        log_print_debug("PcapLoadPartition execute here ");
        log_print_debug("srcaddr = 0x%lx", SourceAddr);
        log_print_debug("dstaddr = 0x%lx", Header->LoadAddr);
        log_print_debug("ImageWordLen = %d", Header->ImageWordLen);
        log_print_debug("DataWordLen  = %d", Header->DataWordLen);

        //PcapLoadPartition()函数是加载bit到FPGA器件的关键函数
        Status = PcapLoadPartition((u32*)SourceAddr,
                    (u32*)Header->LoadAddr,
                    Header->ImageWordLen,
                    Header->DataWordLen,
                    EncryptedPartitionFlag);
        if(Status != XST_SUCCESS) {
            fsbl_printf(DEBUG_GENERAL, "PCAP Bitstream Download Failed\\r\\n");
            return XST_FAILURE;
        }
    }
}
```

**比特流数据搬运和运行**：下面进一步探究，比特流在BOOT.BIN中的起始内容和大小，以及比特流在 system.bit 文件中的起始内容和大小，通过该方法，探究比特流哪些数据最终被打包进BOOT.BIN并且在板子上电时被加载到PL执行。下面的串口输出信息表示，分别dump了 BOOT.BIN 中比特流的开始位置和结束位置的数据内容，并对比 hardware.bit 文件中的内容。

```cpp
../src/main.c:main():258:>> Boot mode is SD
../src/image_mover.c:LoadBootImage():219:>> Image Start Address: 0x00000000
../src/image_mover.c:LoadBootImage():242:>> ------------ Now in PL Progress
../src/image_mover.c:PartitionMove():863:>> 
    SourceAddr = 0x100000, Header->LoadAddr = 0x0, Header->ExecAddr = 0x0
../src/image_mover.c:PartitionMove():865:>> PcapLoadPartition execute here 
../src/image_mover.c:PartitionMove():866:>> srcaddr = 0x100000
../src/image_mover.c:PartitionMove():867:>> dstaddr = 0x0
../src/image_mover.c:PartitionMove():868:>> ImageWordLen = 1011392
../src/image_mover.c:PartitionMove():869:>> DataWordLen  = 1011392
../src/image_mover.c:PartitionMove():870:>> start of SourceAddr data dump: 
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff |................
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff |................
bb 00 00 00 44 00 22 11 ff ff ff ff ff ff ff ff |....D.".........
66 55 99 aa 00 00 00 20 01 20 02 30 00 00 00 00 |fU..... . .0....
../src/image_mover.c:PartitionMove():873:>> end of SourceAddr data dump: 
00 00 00 20 00 00 00 20 00 00 00 20 00 00 00 20 |... ... ... ... 
00 00 00 20 00 00 00 20 00 00 00 20 00 00 00 20 |... ... ... ... 
00 00 00 20 00 00 00 20 00 00 00 20 00 00 00 20 |... ... ... ... 
00 00 00 20 00 00 00 20 00 00 00 20 00 00 00 20 |... ... ... ... 
```

从下图最终对比数据得知，比特流文件打包进BOOT.BIN文件，需要做**字节序转换**，并且以字为单位(4字节)做字节序转换。

![[Pasted image 20251225162100.png]]


## **探究ELF文件到BOOT.BIN**

问题清单：

- （1）ELF文件开始位置是哪里？
- （2）ELF拷贝到BOOT.BIN大小怎么确定？
- （3）ELF文件里哪些节需要加载到内存中以保证程序能够运行？

**开始执行PS程序**：FSBL加载到PS程序后，会把地址直接交给PC指针，之后PS就跳转到对应的地址，执行PS程序了。

```cpp
int buffer_print8(const void *buf, const uint32_t length, int bytesOneLine)
{
    const uint8_t *data_buffer = (const uint8_t *)buf;
    size_t i = 0, j = 0;
    uint8_t byte = 0;
    for (i = 0; i < length; i++)
    {
        byte = data_buffer[i];
        printf("%02x ", data_buffer[i]);
        if ((i % bytesOneLine == (bytesOneLine - 1)) || (i == length - 1))
        {
            for (j = 0; j < (bytesOneLine - 1) - (i % bytesOneLine); j++)
            {
                printf("   ");
            }
            printf("|");
            for (j = (i - (i % bytesOneLine)); j <= i; j++)
            {
                byte = data_buffer[j];
                if (byte > 31 && byte < 127)
                    printf("%c", byte);
                else
                    printf(".");
            }
            printf("\\n");
        }
    }
    return 0;
}

u32 LoadBootImage(void)
{
    ...
    ...
    if (PartitionAttr & ATTRIBUTE_PS_IMAGE_MASK) {
        ...
        //把BOOT.BIN内各个文件从存储介质拷贝到内存中
        log_print_debug("ImageWordLen   = %d", HeaderPtr->ImageWordLen);
        log_print_debug("PartitionStart = %d (words)", HeaderPtr->PartitionStart);
        log_print_debug("ImageStartAddress         = %d", ImageStartAddress);
        Status = PartitionMove(ImageStartAddress, HeaderPtr);
        log_print_debug("begin data:");
        buffer_print8(ExecAddress, 64, 16);
        log_print_debug("end   data:");
        buffer_print8(ExecAddress + HeaderPtr->ImageWordLen*4 - 64, 64, 16);
    }
}
```

```cpp
../src/image_mover.c:LoadBootImage():252:>> -------------------------- Now in PS Progress
../src/image_mover.c:LoadBootImage():261:>> ExecAddress    = 0x100000
../src/image_mover.c:LoadBootImage():265:>> ImageWordLen   = 20484
../src/image_mover.c:LoadBootImage():266:>> PartitionStart = 1049744 (words)
../src/image_mover.c:LoadBootImage():267:>> ImageStartAddress         = 0
../src/image_mover.c:PartitionMove():864:>> SourceAddr = 0x100000, LoadAddr = 0x100000, ExecAddr = 0x100000
../src/image_mover.c:LoadBootImage():269:>> begin data:
49 00 00 ea 25 00 00 ea 2b 00 00 ea 3b 00 00 ea |I...%...+...;...
32 00 00 ea 00 f0 20 e3 00 00 00 ea 0f 00 00 ea |2..... .........
0f 50 2d e9 10 0b 2d ed 20 0b 6d ed 10 1a f1 ee |.P-...-. .m.....
04 10 2d e5 10 1a f8 ee 04 10 2d e5 95 08 00 eb |..-.......-.....
../src/image_mover.c:LoadBootImage():271:>> end   data:
00 00 40 ff 00 00 50 ff 00 00 60 ff 00 00 70 ff |..@...P...`...p.
00 00 80 ff 00 00 90 ff 00 00 a0 ff 00 00 b0 ff |................
00 00 c0 ff 00 00 d0 ff 00 00 e0 ff 0e 4c f0 ff |.............L..
ac aa ff 7f 01 00 00 00 84 05 10 00 40 05 10 00 |............@...
../src/main.c:main():264:>> HandoffAddress = 0x100000
../src/helloworld.c:main():28:>> main address is 0x1005b8
[1] Now led_on == 1
[2] Now led_on == 0
```


![[Pasted image 20251225162125.png]]


由上下图得知，绿色字体红框截图，是 hello.elf 的section信息表，其中红框所在列Off，表示相对于 hello.elf 文件内的偏移量，通过 fseek 来定位。经过探究，最终把 hello.elf 打包到 BOOT.bin 里的，不是所有内容都打包进去，只把 hello.elf 上面红框范围内的内容打包进 BOOT.bin 即可。这结果是通过上面的实验验证得来。并在期间参考Linux内核模块加载相关的代码来进一步验证。

![[Pasted image 20251225162142.png]]


## **手搓ELF浅解析**

```bash
readelf -a hello.elf > hello.readelf

ELF Header:
  Magic:   7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF32
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           ARM
  Version:                           0x1
  Entry point address:               0x100000
  Start of program headers:          52 (bytes into file)
  Start of section headers:          348632 (bytes into file)
  Flags:                             0x5000400, Version5 EABI, hard-float ABI
  Size of this header:               52 (bytes)
  Size of program headers:           32 (bytes)
  Number of program headers:         2
  Size of section headers:           40 (bytes)
  Number of section headers:         28
  Section header string table index: 27

Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .text             PROGBITS        00100000 010000 00ebd0 00  AX  0   0 64
  [ 2] .init             PROGBITS        0010ebd0 01ebd0 000018 00  AX  0   0  4
  [ 3] .fini             PROGBITS        0010ebe8 01ebe8 000018 00  AX  0   0  4
  [ 4] .rodata           PROGBITS        0010ec00 01ec00 000524 00   A  0   0  8
  [ 5] .data             PROGBITS        0010f128 01f128 000a14 00  WA  0   0  8
  [ 6] .eh_frame         PROGBITS        0010fb3c 01fb3c 000004 00   A  0   0  4
  [ 7] .mmu_tbl          PROGBITS        00110000 020000 004000 00   A  0   0  1
  [ 8] .ARM.exidx        ARM_EXIDX       00114000 024000 000008 00  AL  1   0  4
  [ 9] .init_array       INIT_ARRAY      00114008 024008 000004 04  WA  0   0  4
  [10] .fini_array       FINI_ARRAY      0011400c 02400c 000004 04  WA  0   0  4
  [11] .ARM.attributes   ARM_ATTRIBUTES  00114010 024010 000033 00      0   0  1
  [12] .bss              NOBITS          00114010 024010 000328 00  WA  0   0  4
  [13] .heap             NOBITS          00114338 024010 002008 00  WA  0   0  1
  [14] .stack            NOBITS          00116340 024010 003800 00  WA  0   0  1
  [15] .comment          PROGBITS        00000000 024043 000031 01  MS  0   0  1
  [16] .debug_info       PROGBITS        00000000 024074 00dbf7 00      0   0  1
  [17] .debug_abbrev     PROGBITS        00000000 031c6b 002d96 00      0   0  1
  [18] .debug_aranges    PROGBITS        00000000 034a08 0003b8 00      0   0  8
  [19] .debug_macro      PROGBITS        00000000 034dc0 0036f8 00      0   0  1
  [20] .debug_line       PROGBITS        00000000 0384b8 00493d 00      0   0  1
  [21] .debug_str        PROGBITS        00000000 03cdf5 00ff5f 01  MS  0   0  1
  [22] .debug_frame      PROGBITS        00000000 04cd54 000ad4 00      0   0  4
  [23] .debug_loc        PROGBITS        00000000 04d828 002d99 00      0   0  1
  [24] .debug_ranges     PROGBITS        00000000 0505c1 000120 00      0   0  1
  [25] .symtab           SYMTAB          00000000 0506e4 002f80 10     26 428  4
  [26] .strtab           STRTAB          00000000 053664 001a65 00      0   0  1
  [27] .shstrtab         STRTAB          00000000 0550c9 00010f 00      0   0  1

Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings)
  I (info), L (link order), G (group), T (TLS), E (exclude), x (unknown)
  O (extra OS processing required) o (OS specific), p (processor specific)
```

下面是完整源代码，主要解析ELF文件的ehdr和shdr：

```cpp
//https://blog.csdn.net/u012787710/article/details/77613298

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>

int file_get_context(const char *file, long off, void *buffer, long rdlen)
{
    FILE *fp = fopen(file, "rb");
    uint8_t *buf = (uint8_t *)buffer;
    
    fseek(fp, off, SEEK_SET);
    fread(buf, 1, rdlen, fp);
    fclose(fp);
    
    return 0;
}

int buffer_print8(const void *buf, const uint32_t length, int bytesOneLine)
{
    const uint8_t *data_buffer = (const uint8_t *)buf;
    size_t i = 0, j = 0;
    uint8_t byte = 0;
    for (i = 0; i < length; i++)
    {
        byte = data_buffer[i];
        printf("%02x ", data_buffer[i]);
        if ((i % bytesOneLine == (bytesOneLine - 1)) || (i == length - 1))
        {
            for (j = 0; j < (bytesOneLine - 1) - (i % bytesOneLine); j++)
            {
                printf("   ");
            }
            printf("|");
            for (j = (i - (i % bytesOneLine)); j <= i; j++)
            {
                byte = data_buffer[j];
                if (byte > 31 && byte < 127)
                    printf("%c", byte);
                else
                    printf(".");
            }
            printf("\\n");
        }
    }
    return 0;
}

typedef uint16_t Elf32_Half;
typedef uint16_t Elf32_Half;
typedef uint32_t Elf32_Word;
typedef uint32_t Elf32_Addr;
typedef uint32_t Elf32_Off ;
typedef uint32_t Elf32_Off ;
typedef uint32_t Elf32_Word;
typedef uint16_t Elf32_Half;
typedef uint16_t Elf32_Half;
typedef uint16_t Elf32_Half;
typedef uint16_t Elf32_Half;
typedef uint16_t Elf32_Half;
typedef uint16_t Elf32_Half;
typedef int32_t  Elf32_Sword;

#define EI_NIDENT       16  
typedef struct elf32_hdr{  
    unsigned char e_ident[EI_NIDENT];   
    Elf32_Half    e_type;     /* file type */  
    Elf32_Half    e_machine;  /* architecture */  
    Elf32_Word       e_version;  
    Elf32_Addr    e_entry;    /* entry point */  
    Elf32_Off       e_phoff;        /* PH table offset */  
    Elf32_Off       e_shoff;        /* SH table offset */  
    Elf32_Word    e_flags;  
    Elf32_Half    e_ehsize;       /* ELF header size in bytes */  
    Elf32_Half    e_phentsize;    /* PH size */  
    Elf32_Half    e_phnum;        /* PH number */  
    Elf32_Half    e_shentsize;    /* SH size */  
    Elf32_Half    e_shnum;        /* SH number */  
    Elf32_Half    e_shstrndx; /* SH name string table index */  
} Elf32_Ehdr;
//sizeof(Elf32_Ehdr) == 52

/* Legal values for e_type (object file type).  */
#define ET_NONE     0       /* No file type */
#define ET_REL      1       /* Relocatable file */
#define ET_EXEC     2       /* Executable file */
#define ET_DYN      3       /* Shared object file */
#define ET_CORE     4       /* Core file */

typedef struct {  
    Elf32_Word    sh_name;    /* name of section, index */  
    Elf32_Word    sh_type;      
    Elf32_Word    sh_flags;  
    Elf32_Addr    sh_addr;       /* memory address, if any */  
    Elf32_Off     sh_offset;  
    Elf32_Word    sh_size;        /* section size in file */  
    Elf32_Word    sh_link;  
    Elf32_Word    sh_info;  
    Elf32_Word    sh_addralign;  
    Elf32_Word    sh_entsize;     /* fixed entry size, if have */  
} Elf32_Shdr;
//Section Header sizeof(Elf32_Shdr) == 40

/* Legal values for sh_flags (section flags).  */
#define SHF_WRITE        (1 << 0)   /* Writable */
#define SHF_ALLOC        (1 << 1)   /* Occupies memory during execution */
#define SHF_EXECINSTR        (1 << 2)   /* Executable */
#define SHF_MERGE        (1 << 4)   /* Might be merged */
#define SHF_STRINGS      (1 << 5)   /* Contains nul-terminated strings */

/* Legal values for sh_type (section type).  */
#define SHT_NULL      0     /* Section header table entry unused */
#define SHT_PROGBITS      1     /* Program data */
#define SHT_SYMTAB    2     /* Symbol table */
#define SHT_STRTAB    3     /* String table */
#define SHT_RELA      4     /* Relocation entries with addends */
#define SHT_HASH      5     /* Symbol hash table */
#define SHT_DYNAMIC   6     /* Dynamic linking information */
#define SHT_NOTE      7     /* Notes */
#define SHT_NOBITS    8     /* Program space with no data (bss) */
#define SHT_REL       9     /* Relocation entries, no addends */
#define SHT_SHLIB     10        /* Reserved */
#define SHT_DYNSYM    11        /* Dynamic linker symbol table */
#define SHT_INIT_ARRAY    14        /* Array of constructors */
#define SHT_FINI_ARRAY    15        /* Array of destructors */
#define SHT_PREINIT_ARRAY 16        /* Array of pre-constructors */
#define SHT_GROUP     17        /* Section group */
#define SHT_SYMTAB_SHNDX  18        /* Extended section indeces */
#define SHT_NUM       19        /* Number of defined types.  */

/* Find a module section: 0 means not found. */
// static unsigned int find_sec(const Elf32_Ehdr *ehdr, const char *name)
// {
    // unsigned int i;

    // for (i = 1; i < ehdr->e_shnum; i++) {
        // Elf_Shdr *shdr = &info->sechdrs[i];
        // /* Alloc bit cleared means "ignore it." */
        // if ((shdr->sh_flags & SHF_ALLOC)
            // && strcmp(info->secstrings + shdr->sh_name, name) == 0)
            // return i;
    // }
    // return 0;
// }

typedef struct elf32_phdr{  
    Elf32_Word    p_type;   
    Elf32_Off     p_offset;  
    Elf32_Addr    p_vaddr;        /* virtual address */  
    Elf32_Addr    p_paddr;        /* ignore */  
    Elf32_Word    p_filesz;       /* segment size in file */  
    Elf32_Word    p_memsz;        /* size in memory */  
    Elf32_Word    p_flags;  
    Elf32_Word    p_align;       
} Elf32_Phdr;  
//Program Header sizeof(Elf32_Phdr) == 32

typedef struct elf32_sym{  
    Elf32_Word    st_name;  
    Elf32_Addr    st_value;  
    Elf32_Word    st_size;  
    unsigned char st_info;  
    unsigned char st_other;  
    Elf32_Half    st_shndx;  
} Elf32_Sym;
//Symbol Table sizeof(Elf32_Phdr) == 16

/* Legal values for ST_BIND subfield of st_info (symbol binding).  */
#define STB_LOCAL   0       /* Local symbol 局部符号，对于目标文件的外部不可见*/
#define STB_GLOBAL  1       /* Global symbol 全局符号，外部可见*/
#define STB_WEAK    2       /* Weak symbol 弱引用*/
#define STB_NUM     3       /* Number of defined types.  */
#define STB_LOOS    10      /* Start of OS-specific */
#define STB_GNU_UNIQUE  10      /* Unique symbol.  */
#define STB_HIOS    12      /* End of OS-specific */
#define STB_LOPROC  13      /* Start of processor-specific */
#define STB_HIPROC  15      /* End of processor-specific */

/* Legal values for ST_TYPE subfield of st_info (symbol type).  */
#define STT_NOTYPE  0 /* Symbol type is unspecified */
#define STT_OBJECT  1  /* Symbol is a data object, such as var, array */
#define STT_FUNC    2 /* Symbol is a code object, such as func,or other execode */
#define STT_SECTION 3 /* Symbol associated with a section, must be STB_LOCAL */
#define STT_FILE    4 //file name
#define STT_COMMON  5       /* Symbol is a common data object */
#define STT_TLS     6       /* Symbol is thread-local data object*/
#define STT_NUM     7       /* Number of defined types.  */
#define STT_LOOS    10      /* Start of OS-specific */
#define STT_GNU_IFUNC   10      /* Symbol is indirect code object */
#define STT_HIOS    12      /* End of OS-specific */
#define STT_LOPROC  13      /* Start of processor-specific */
#define STT_HIPROC  15      /* End of processor-specific */

#define SHN_UNDEF   0 //Undefined section, but defined in other file   
#define SHN_ABS     0xfff1 //Associated symbol is absolute, such as filename
#define SHN_COMMON  0xfff2 //Associated symbol is common, uninited global vars

#define log_print_debug(fmt,...) do {\\
    printf("%s:%s():%d:>> ", __FILE__, __func__, __LINE__);\\
    printf(fmt,##__VA_ARGS__);\\
    printf("\\r\\n");\\
}while(0)

int main(int argc, const char *argv[])
{
    const char *file = argv[1];
    log_print_debug("%s", file);
    
    Elf32_Ehdr ehdr;
    file_get_context(file, 0, &ehdr, sizeof(ehdr));
    
    
    do {
        printf("e_ident        = ");
        for(int i=0; i<EI_NIDENT; i++)
        {
            //[0~4]             elf magic number
            //[5]               1=elf is 32bit, 2=elf is 64bit
            //[6]               1=elf is little-endian, 2=...big-endian
            //[7]               fixed=1, version of elf
            //[8~EI_NIDENT-1]   reserved
            printf("%02x ", ehdr.e_ident[i]);
        }
        printf("\\n");

        printf("e_type         = 0x%x (ET_REL=1 xxx.o, ET_EXEC=2, ET_DYN=3 xxx.so)\\n", ehdr.e_type);
        printf("e_machine      = 0x%x\\n", ehdr.e_machine);
        printf("e_version      = 0x%x\\n", ehdr.e_version);
        printf("e_entry        = 0x%x\\n", ehdr.e_entry);
        printf("e_phoff        = 0x%x\\n", ehdr.e_phoff);
        printf("e_shoff        = 0x%x\\n", ehdr.e_shoff);
        printf("e_flags        = 0x%x\\n", ehdr.e_flags);
        printf("e_ehsize       = 0x%x\\n", ehdr.e_ehsize);
        printf("e_phentsize    = 0x%x\\n", ehdr.e_phentsize);
        printf("e_phnum        = 0x%x\\n", ehdr.e_phnum);
        printf("e_shentsize    = 0x%x\\n", ehdr.e_shentsize);
        printf("e_shnum        = 0x%x\\n", ehdr.e_shnum);
        printf("e_shstrndx     = 0x%x\\n", ehdr.e_shstrndx);  
    }while(0);
    

    do {
        const Elf32_Shdr *shdr;
        const char *secname;
        
        Elf32_Shdr *shdrs = malloc(sizeof(Elf32_Shdr) * ehdr.e_shnum);
        file_get_context(file, ehdr.e_shoff, shdrs, sizeof(Elf32_Shdr) * ehdr.e_shnum);
        

        printf("%64s\\n", "----------------------------------------------------------------------");
        printf("%-4s  "  "%-16s  "  "%-12s  "  "%-8s  " "%-8s  "    "%-8s\\n", 
               "idx",   "sename",  "sectype", "secaddr", "secoffset", "secsize");
        printf("%64s\\n", "----------------------------------------------------------------------");
        for(int i=0; i<ehdr.e_shnum; i++)
        {
            shdr = &shdrs[i];
            
            //这是文件中存放字符串的位置,在文件中的偏移
            shdrs[ehdr.e_shstrndx].sh_offset;
            
            //这是字符串总大小
            shdrs[ehdr.e_shstrndx].sh_size;
            
            char *secstrs = malloc(shdrs[ehdr.e_shstrndx].sh_size);
            file_get_context(file, shdrs[ehdr.e_shstrndx].sh_offset, 
                secstrs, shdrs[ehdr.e_shstrndx].sh_size);
            
            secname = (const char *)&secstrs[shdr->sh_name];
            
            printf("%04d  "  "%-16s  "  "%-12d  "      "%08x  "     "%08x  "       "%08x\\n", 
                     i,     secname,    
                     shdr->sh_type, shdr->sh_addr, shdr->sh_offset, shdr->sh_size);
        }
    } while(0);

    
    return 0;
}
```

```cpp
elf-read.c:main():234:>> hello hello.elf
e_ident        = 7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00
e_type         = 0x2 (ET_REL=1 xxx.o, ET_EXEC=2, ET_DYN=3 xxx.so)
e_machine      = 0x28
e_version      = 0x1
e_entry        = 0x100000
e_phoff        = 0x34
e_shoff        = 0x551d8
e_flags        = 0x5000400
e_ehsize       = 0x34
e_phentsize    = 0x20
e_phnum        = 0x2
e_shentsize    = 0x28
e_shnum        = 0x1c
e_shstrndx     = 0x1b
----------------------------------------------------------------------
idx   sename            sectype       secaddr   secoffset  secsize
----------------------------------------------------------------------
0000                    0             00000000  00000000  00000000
0001  .text             1             00100000  00010000  0000ebd0
0002  .init             1             0010ebd0  0001ebd0  00000018
0003  .fini             1             0010ebe8  0001ebe8  00000018
0004  .rodata           1             0010ec00  0001ec00  00000524
0005  .data             1             0010f128  0001f128  00000a14
0006  .eh_frame         1             0010fb3c  0001fb3c  00000004
0007  .mmu_tbl          1             00110000  00020000  00004000
0008  .ARM.exidx        1879048193    00114000  00024000  00000008
0009  .init_array       14            00114008  00024008  00000004
0010  .fini_array       15            0011400c  0002400c  00000004
0011  .ARM.attributes   1879048195    00114010  00024010  00000033
0012  .bss              8             00114010  00024010  00000328
0013  .heap             8             00114338  00024010  00002008
0014  .stack            8             00116340  00024010  00003800
0015  .comment          1             00000000  00024043  00000031
0016  .debug_info       1             00000000  00024074  0000dbf7
0017  .debug_abbrev     1             00000000  00031c6b  00002d96
0018  .debug_aranges    1             00000000  00034a08  000003b8
0019  .debug_macro      1             00000000  00034dc0  000036f8
0020  .debug_line       1             00000000  000384b8  0000493d
0021  .debug_str        1             00000000  0003cdf5  0000ff5f
0022  .debug_frame      1             00000000  0004cd54  00000ad4
0023  .debug_loc        1             00000000  0004d828  00002d99
0024  .debug_ranges     1             00000000  000505c1  00000120
0025  .symtab           2             00000000  000506e4  00002f80
0026  .strtab           3             00000000  00053664  00001a65
0027  .shstrtab         3             00000000  000550c9  0000010f
```



## **探究LOAD地址**

下面是zynq制作BOOT.bin生成的 **output.bif** 文件。

```cpp
//arch = zynq; split = false; format = BIN
the_ROM_image:
{
    [bootloader]E:\\Xilinx_SDK\\BF_Zynq7010\\spiflash\\fsbl.elf
    E:\\Xilinx_SDK\\BF_Zynq7010\\spiflash\\bf_top.bit
    E:\\Xilinx_SDK\\BF_Zynq7010\\spiflash\\u-boot.elf
    [load = 0x1000000]E:\\Xilinx_SDK\\BF_Zynq7010\\spiflash\\devicetree.dtb
    [load = 0x800000]E:\\Xilinx_SDK\\BF_Zynq7010\\spiflash\\uramdisk.image.gz
    [load = 0x1200000]E:\\Xilinx_SDK\\BF_Zynq7010\\spiflash\\uImage
}
```

上面这个BOOT.BIN打包的文件列表，来源于某个项目，最后3个文件额外设置了load值。于是我直接把当时项目的BOOT.BIN拿到手，然后放到SD卡里，并修改FSBL重新编译后，下载运行FSBL程序，最终串口打印信息如下：

```cpp
../src/main.c:main():243:>> Boot mode is SD
LoadBootImage():296:>> [PL idx:1] LoadAddr = 0x0, ExecAddr = 0x0, imageWLen:0x7f2e8
LoadBootImage():296:>> [PS idx:2] LoadAddr = 0x4000000, ExecAddr = 0x4000000, imageWLen:0x386aa
LoadBootImage():296:>> [PS idx:3] LoadAddr = 0x1000000, ExecAddr = 0x0, imageWLen:0xb92
LoadBootImage():296:>> [PS idx:4] LoadAddr = 0x800000, ExecAddr = 0x0, imageWLen:0x163d10
LoadBootImage():296:>> [PS idx:5] LoadAddr = 0x1200000, ExecAddr = 0x0, imageWLen:0x112178
```

在项目中，板子上电之后FSBL只要把u-boot运行起来即可，但在启动u-boot之前，要确保把u-boot以下的其他文件（比如 uImage、设备树、ramdisk）存放到对应的内存地址。因为后续u-boot启动后，u-boot会访问这些地址。

u-boot的入口地址：**0x4000000**，即运行u-boot的第一个函数。

```cpp
elf-read.c:main():234:>> u-boot.elf
e_ident        = 7f 45 4c 46 01 01 01 61 00 00 00 00 00 00 00 00
e_type         = 0x2 (ET_REL=1 xxx.o, ET_EXEC=2, ET_DYN=3 xxx.so)
e_machine      = 0x28
e_version      = 0x1
e_entry        = 0x4000000
e_phoff        = 0x34
e_shoff        = 0xf1b88
e_flags        = 0x0
e_ehsize       = 0x34
e_phentsize    = 0x20
e_phnum        = 0x1
e_shentsize    = 0x28
e_shnum        = 0x5
e_shstrndx     = 0x4
----------------------------------------------------------------------
idx   sename            sectype       secaddr   secoffset  secsize
----------------------------------------------------------------------
0000                    0             00000000  00000000  00000000
0001  .data             1             04000000  00010000  000e1aa7
0002  .symtab           2             00000000  000f1aa8  00000070
0003  .strtab           3             00000000  000f1b18  0000004c
0004  .shstrtab         3             00000000  000f1b64  00000021

----------------------------------------------------------------------
$ readelf.exe -S u-boot.elf
There are 5 section headers, starting at offset 0xf1b88:

Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .data             PROGBITS        04000000 010000 0e1aa7 00  WA  0   0  1
  [ 2] .symtab           SYMTAB          00000000 0f1aa8 000070 10      3   3  4
  [ 3] .strtab           STRTAB          00000000 0f1b18 00004c 00      0   0  1
  [ 4] .shstrtab         STRTAB          00000000 0f1b64 000021 00      0   0  1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings)
  I (info), L (link order), G (group), T (TLS), E (exclude), x (unknown)
  O (extra OS processing required) o (OS specific), p (processor specific)
```


## **探究BOOT.BIN**

- zynq-standalone = fsbl.elf + hw.bit + hello.elf
    
- zynq-linux = (fsbl+bit) + u-boot.elf + uImage + uramdisk.image.gz + system-top.dtb
    
- Run PS: ps.cpu.pc = elf.entry.addr (PC pointer)
    
- Run PL: slcr
    
- excalidraw-url: [[excalidraw.com]]
    
- excalidraw-data: 在草稿文件有ZYNQ字样的草稿，里面有 BOOT.BIN 的构造图。
    
- excalidraw-uage: Copy the data from the json file and paste it on the page where the URL is loaded.


![[Pasted image 20251225162256.png]]


## **探究ELF哪些节需要加载到内存**

- 参考代码: [[module.c]]
- 参考函数: load_module

**Elf_Ehdr**：首先拷贝获取到ELF头信息。

```cpp
/* Sets info->hdr and info->len. */
static int copy_module_from_user(const void __user *umod, 
    unsigned long len, struct load_info *info)
{
    info->len = len;

    /* Suck in entire file: we'll want most of it. */
    info->hdr = __vmalloc(info->len, GFP_KERNEL | __GFP_NOWARN);
    copy_chunked_from_user(info->hdr, umod, info->len);
    return err;
}
```

如下代码所示，上面是从内核代码摘下来简化的核心伪代码，目的是探究内核模块需要把哪些sections弄到内核里，以方便后续使用。跟踪到最后，发现 move_module 函数是核心位置，它的实现基本描述了哪些sections需要弄到内核里。从上述代码中能看到，首先需要满足 **SHF_ALLOC**，然后排除 **SHT_NOBITS**，然后把这两个条件，代入到前面ELF探究的小节验证，果然是这样的，因此ELF文件需要拷贝哪些内容到内存，就是根据这两个条件来确定的。

```cpp
static int move_module(struct module *mod, struct load_info *info)
{
    void *ptr;

    /* Do the allocs. */
    ptr = module_alloc(mod->core_layout.size);

    memset(ptr, 0, mod->core_layout.size);
    mod->core_layout.base = ptr;

    /* Do the allocs. */
    ptr = vzalloc(mod->data_layout.size);
    mod->data_layout.base = ptr;
    
    /* Transfer each section which specifies SHF_ALLOC */
    pr_debug("final section addresses:\\n");
    for (i = 0; i < info->hdr->e_shnum; i++) {
        void *dest;
        Elf_Shdr *shdr = &info->sechdrs[i];

        if (!(shdr->sh_flags & SHF_ALLOC))
            continue;

        if (shdr->sh_entsize & INIT_OFFSET_MASK)
            dest = mod->init_layout.base
                + (shdr->sh_entsize & ~INIT_OFFSET_MASK);
        else if (!(shdr->sh_flags & SHF_EXECINSTR))
            dest = mod->data_layout.base + shdr->sh_entsize;
        else
            dest = mod->core_layout.base + shdr->sh_entsize;

        if (shdr->sh_type != SHT_NOBITS)
            memcpy(dest, (void *)shdr->sh_addr, shdr->sh_size);
        /* Update sh_addr to point to copy in image. */
        shdr->sh_addr = (unsigned long)dest;
        pr_debug("\\t0x%lx %s\\n",
             (long)shdr->sh_addr, info->secstrings + shdr->sh_name);
    }
}
```


```
- **sh_name**，4字节，是一个索引值，在shstrtable（section header string table，包含section name的字符串表，也是一个section）中的索引。第二讲介绍ELF文件头时，里面专门有一个字段e_shstrndx，其含义就是shstrtable对应的section header在section header table中的索引。
- **sh_type**，4字节，描述了section的类型，常见的取值如下：
    - SHT_NULL 0，表明section header无效，没有关联的section。
    - **SHT_PROGBITS** 1，section包含了程序需要的数据，格式和含义由程序解释。
    - **SHT_SYMTAB** 2， 包含了一个符号表。当前，一个ELF文件中只有一个符号表。SHT_SYMTAB提供了用于(link editor)链接编辑的符号，当然这些符号也可能用于动态链接。这是一个完全的符号表，它包含许多符号。
    - **SHT_STRTAB** 3，包含一个字符串表。一个对象文件包含多个字符串表，比如.strtab（包含符号的名字）和.shstrtab（包含section的名称）。
    - **SHT_RELA** 4，重定位节，包含relocation入口，参见Elf32_Rela。一个文件可能有多个Relocation Section。比如.rela.text，.rela.dyn。
    - SHT_HASH 5，这样的section包含一个符号hash表，参与动态连接的目标代码文件必须有一个hash表。目前一个ELF文件中只包含一个hash表。讲链接的时候再细讲。
    - **SHT_DYNAMIC** 6，包含动态链接的信息。目前一个ELF文件只有一个DYNAMIC section。
    - **SHT_NOBITS** 8，这种section不含字节，也不占用文件空间，section header中的sh_offset字段只是概念上的偏移。
    - **SHT_REL** 9， 重定位节，包含重定位条目。和SHT_RELA基本相同，两者的区别在后面讲重定位的时候再细讲。
    - SHT_DYNSYM 11， 用于动态连接的符号表，推测是symbol table的子集。
- **sh_flags**, 32位占4字节， 64位占8字节。包含位标志，用 readelf -S <elf> 可以看到很多标志。常用的有：
    - SHF_WRITE 0x1，进程执行的时候，section内的数据可写。
    - **SHF_ALLOC** 0x2，进程执行的时候，section需要占据内存。
    - **SHF_EXECINSTR** 0x4，节内包含可以执行的机器指令。
    - **SHF_STRINGS** 0x20，包含0结尾的字符串。
- **sh_addr**, 对32位来说是4字节，64位是8字节。如果section会出现在进程的内存映像中，给出了section第一字节的虚拟地址。
- **sh_offset**，在ELF文件中的偏移，可用 `lseek(fd, sh_offset, SEEK_SET)` 定位到。
```


## **探究symtab和strtab**

下面代码片段参考自Linux内核模块管理相关代码，它们是关于如何访问symtab和strtab的核心代码。

```cpp
mod->kallsyms->symtab = (void *)symsec->sh_addr;
mod->kallsyms->num_symtab = symsec->sh_size / sizeof(Elf_Sym);

/* Find internal symbols and strings. */
for (i = 1; i < info->hdr->e_shnum; i++) {
    if (info->sechdrs[i].sh_type == SHT_SYMTAB) {
        info->index.sym = i;
        info->index.str = info->sechdrs[i].sh_link;
        info->strtab = (char *)info->hdr
                + info->sechdrs[info->index.str].sh_offset;
        break;
    }
}

if (info->index.sym == 0) {
    pr_warn("%s: module has no symbols (stripped?)\\n",
            info->name ?: "(missing .modinfo section or name field)");
    return -ENOEXEC;
}

static const char *kallsyms_symbol_name(struct mod_kallsyms *kallsyms, unsigned int symnum)
{
    //strtab + symtab[symnum].st_name
    return kallsyms->strtab + kallsyms->symtab[symnum].st_name;
}
```

下面是section访问的接口代码，来自Linux内核模块管理，先搜藏起来以可以用在其他需要的地方。

```cpp
/* Find a module section: 0 means not found. */
static unsigned int find_sec(const struct load_info *info, const char *name)
{
    unsigned int i;

    for (i = 1; i < info->hdr->e_shnum; i++) {
            Elf_Shdr *shdr = &info->sechdrs[i];
            /* Alloc bit cleared means "ignore it." */
            if ((shdr->sh_flags & SHF_ALLOC)
                && strcmp(info->secstrings + shdr->sh_name, name) == 0)
                    return i;
    }
    return 0;
}

/* Find a module section, or NULL. */
static void *section_addr(const struct load_info *info, const char *name)
{
        /* Section 0 has sh_addr 0. */
        return (void *)info->sechdrs[find_sec(info, name)].sh_addr;
}

/* Find a module section, or NULL.  Fill in number of "objects" in section. */
static void *section_objs(const struct load_info *info,
                          const char *name,
                          size_t object_size,
                          unsigned int *num)
{
        unsigned int sec = find_sec(info, name);

        /* Section 0 has sh_addr 0 and sh_size 0. */
        *num = info->sechdrs[sec].sh_size / object_size;
        return (void *)info->sechdrs[sec].sh_addr;
}

/* Find a module section: 0 means not found. Ignores SHF_ALLOC flag. */
static unsigned int find_any_sec(const struct load_info *info, const char *name)
{
        unsigned int i;

        for (i = 1; i < info->hdr->e_shnum; i++) {
                Elf_Shdr *shdr = &info->sechdrs[i];
                if (strcmp(info->secstrings + shdr->sh_name, name) == 0)
                        return i;
        }
        return 0;
}
```



## **探究ELF入口函数和链接地址**

```cpp
int hello_mul(int a, int b)
{
    return (a*b);
}

int hello_add(int a, int b)
{
    return (a+b);
}

void hello_cal(void)
{
    int a = 10;
    int b = 20;
    int c = hello_add(a, b);
    int d = hello_mul(a, b);
}
```

Entrypoint function of executable program is **hello_cal**, and Address of ".text" is **0x40000000**.

```cpp
# Specify the entry point function as hello_cal, 
# and specify the first address of the code section as 0x40000000.
gcc -o hello.elf hello.c -nostdlib -e hello_cal -Ttext 0x40000000

readelf -S hello.elf
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .text             PROGBITS        40000000 008000 0000a4 00  AX  0   0  4

readelf -h hello.elf 
ELF Header:
  Magic:   7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF32
  Data:                              2's complement, little endian
  OS/ABI:                            UNIX - System V
  Type:                              EXEC (Executable file)
  Machine:                           ARM
  Version:                           0x1
  Entry point address:               0x40000060  <--------<hello_cal>
  Start of program headers:          52 (bytes into file)
  Start of section headers:          33104 (bytes into file)
  Flags:                             0x5000002, has entry point, Version5 EABI
  Number of section headers:         7
  Section header string table index: 4
```

By disassembling the code, you can see that the function ****hello_mul**** is ****0x40000000**** at the first address of the code section. And through the above ****ELF**** information, we can see that the size of the code section is 0xa4 (164) bytes, and we can directly count the number of instruction lines of each function of the disassembly code section, and we can verify that the code section size is indeed 164 bytes. And in the disassembly code, where the function is called, the jump instruction is directly to the determined address.

```cpp
objdump -D -S hello.elf > hello.dump.S
objdump -D -S --section=".text" hello.elf > hello.dump.S
```

Here's the full disassembly code for the code section:

```cpp
hello.elf:     file format elf32-littlearm

Disassembly of section .text:

40000000 <hello_mul>:
40000000:    e52db004     push    {fp}        ; (str fp, [sp, #-4]!)
40000004:    e28db000     add    fp, sp, #0
40000008:    e24dd00c     sub    sp, sp, #12
4000000c:    e50b0008     str    r0, [fp, #-8]
40000010:    e50b100c     str    r1, [fp, #-12]
40000014:    e51b3008     ldr    r3, [fp, #-8]
40000018:    e51b200c     ldr    r2, [fp, #-12]
4000001c:    e0030392     mul    r3, r2, r3
40000020:    e1a00003     mov    r0, r3
40000024:    e28bd000     add    sp, fp, #0
40000028:    e8bd0800     ldmfd    sp!, {fp}
4000002c:    e12fff1e     bx    lr

40000030 <hello_add>:
40000030:    e52db004     push    {fp}        ; (str fp, [sp, #-4]!)
40000034:    e28db000     add    fp, sp, #0
40000038:    e24dd00c     sub    sp, sp, #12
4000003c:    e50b0008     str    r0, [fp, #-8]
40000040:    e50b100c     str    r1, [fp, #-12]
40000044:    e51b2008     ldr    r2, [fp, #-8]
40000048:    e51b300c     ldr    r3, [fp, #-12]
4000004c:    e0823003     add    r3, r2, r3
40000050:    e1a00003     mov    r0, r3
40000054:    e28bd000     add    sp, fp, #0
40000058:    e8bd0800     ldmfd    sp!, {fp}
4000005c:    e12fff1e     bx    lr

40000060 <hello_cal>:
40000060:    e92d4800     push    {fp, lr}
40000064:    e28db004     add    fp, sp, #4
40000068:    e24dd010     sub    sp, sp, #16
4000006c:    e3a0300a     mov    r3, #10
40000070:    e50b3008     str    r3, [fp, #-8]
40000074:    e3a03014     mov    r3, #20
40000078:    e50b300c     str    r3, [fp, #-12]
4000007c:    e51b0008     ldr    r0, [fp, #-8]
40000080:    e51b100c     ldr    r1, [fp, #-12]
40000084:    ebffffe9     bl    40000030 <hello_add>
40000088:    e50b0010     str    r0, [fp, #-16]
4000008c:    e51b0008     ldr    r0, [fp, #-8]
40000090:    e51b100c     ldr    r1, [fp, #-12]
40000094:    ebffffd9     bl    40000000 <hello_mul>
40000098:    e50b0014     str    r0, [fp, #-20]
4000009c:    e24bd004     sub    sp, fp, #4
400000a0:    e8bd8800     pop    {fp, pc}
```


# zynqmp-fsbl-boot.bin

## 特征码定位（BOOT.bin）

思路：构造一个特定的BOOT.bin，把不同文件放到Flash确定的偏移位置，从而方便二进制分析。

一、把要探究的文件设置偏移：

```bash
//arch = zynqmp; split = false; format = BIN
the_ROM_image:
{
	[bootloader, destination_cpu = a53-0]D:\\loop_test.sdk\\bootimage/fsbl_origin.elf
	[destination_cpu = pmu]D:\\loop_test.sdk\\bootimage\\pmufw.elf
	[offset = 0x00080000, destination_device = pl]D:\\loop_test.sdk\\bootimage/LOOP_TEST.bit
	[offset = 0x04080000, destination_cpu = a53-0, exception_level = el-3, trustzone]D:\\loop_test.sdk\\bootimage\\bl31.elf
	[offset = 0x040A0000, load = 0x08000000, destination_cpu = a53-0, exception_level = el-2]D:\\loop_test.sdk\\bootimage\\u-boot.elf
	[offset = 0x042A0000, load = 0x08800000, destination_cpu = a53-0]D:\\loop_test.sdk\\bootimage\\system-top.dtb
	[offset = 0x043A0000, load = 0x10000000, destination_cpu = a53-0, exception_level = el-1]D:\\loop_test.sdk\\bootimage\\uImage
	[offset = 0x063A0000, load = 0x12000000, destination_cpu = a53-0, exception_level = el-1]D:\\loop_test.sdk\\bootimage\\uramdisk.image.gz
}
```

二、从BOOT.bin中获取到特征码如下：打上确定的偏移制作出BOOT.bin之后，就能分析出文件对应于BOOT.bin中的位置和数据组织。

```bash
[OK]设备树在BOOT.bin中的特征码:
D0 0D FE ED 00 00 6C A9

[OK]bitstream在BOOT.bin中的特征码(原bitstream四字节序反转-->BOOT.bin.bitstream):
FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 
FF FF FF FF FF FF FF FF FF FF FF FF BB 00 00 00 
44 00 22 11 FF FF FF FF FF FF FF

[OK]uramdisk在BOOT.bin中的特征码:
27 05 19 56 00 2A EF 25
```

三、各个文件

（1）u-boot.elf —— 并没有把elf文件完整存放到BOOT.bin里，只把里面带A(alloc)标志的Section存放到了BOOT.bin文件里。参考命令： `aarch64-linux-gnu-readelf -S u-boot.elf > u-boot.elf.Sections`。

（2）.bit文件 —— 并没有把.bit文件完整存放到 BOOT.bin 文件里，


## fsbl加载bitstream

![[Pasted image 20251225162603.png]]













# zynq裸机i2c温度传感器


## 一、硬件原理图拓扑

![[Pasted image 20251225165437.png]]

ZYNQ裸机环境下，通过 PS I2C 来读取LM75温度传感器。


## 二、交换芯片读写时序

![[Pasted image 20251225165456.png]]

## 三、温度传感器时序

![[Pasted image 20251225165510.png]]


四、参考源文件

```cpp
#include "xparameters.h"
#include "xiicps.h"
#include "xstatus.h""
#include "xil_printf.h"
#include "sleep.h"
#include "zynq_debug.h"

static XIicPs IicPs_Instance;

int IicPs_Init(uint32_t i2c_device_id)
{
    XIicPs_Config *IicPs_ConfigPtr;
    XStatus Status;

    IicPs_ConfigPtr = XIicPs_LookupConfig(i2c_device_id);
    if (IicPs_ConfigPtr == NULL) {
        log_warnline("XIicPs_LookupConfig failed, (i2c%d)", i2c_device_id);
        return XST_DEVICE_NOT_FOUND;
    }

    Status = XIicPs_CfgInitialize(&IicPs_Instance, IicPs_ConfigPtr, 
                                  IicPs_ConfigPtr->BaseAddress);
    if (Status != XST_SUCCESS) {
        log_warnline("XIicPs_CfgInitialize failed, (i2c%d, Status=%d)", i2c_device_id, Status);
        return Status;
    }

    Status = XIicPs_SelfTest(&IicPs_Instance);
    if (Status != XST_SUCCESS) {
        log_warnline("XIicPs_SelfTest failed, (i2c%d, Status=%d)", i2c_device_id, Status);
        return Status;
    }

    Status = XIicPs_SetSClk(&IicPs_Instance, 100000);// 100000=100K(Standard mode)
    if (Status != XST_SUCCESS) {
        log_warnline("XIicPs_SetSClk failed, (i2c%d, Status=%d)", i2c_device_id, Status);
        return Status;
    }

    return XST_SUCCESS;
}


short GetTempture(u8 channelIndex, u8 tempSlaveAddr)
{
    u8 slaveaddr_9548;
    u8 slaveaddr_lm75;
    u8 SendBuf[1];
	int Status;


    // 等待总线空闲
    int TimeoutMS = 50;
    while (XIicPs_BusIsBusy(&IicPs_Instance)) {
        usleep(1000);
        if (--TimeoutMS == 0) {
            log_warnline("I2C Bus busy, timeout");
            return 0;
        }
    }


    // send enable channel of 9548
    slaveaddr_9548 = 0x70; // 1110 A2A1A0 W  --> 1110 A2A1A0 is slave addr(0x70) of TCA9548APWR
    SendBuf[0] = (1<<channelIndex);//enable channelIndex
    Status = XIicPs_MasterSendPolled(&IicPs_Instance, SendBuf, sizeof(SendBuf), slaveaddr_9548);
    if (Status != XST_SUCCESS) {
        log_warnline("TCA9548APWR Send slaveaddr_9548 failed");
        return 0;
    }

	// check 9548 is OK or not
    Status = XIicPs_MasterRecvPolled(&IicPs_Instance, SendBuf, 1, slaveaddr_9548);
    if (Status != XST_SUCCESS) {
        log_warnline("TCA9548APWR Send slaveaddr_lm75 failed");
        return 0;
    }
    // check: SendBuf[0] == (1<<4)
	// check: SendBuf[0] == (1<<5)


	// usleep(10000);

	// 发送温度寄存器地址,表示接下来将要读取该寄存器值
    slaveaddr_lm75 = tempSlaveAddr; // 1001 A2A1A0 W  --> 1001 A2A1A0 is slave addr(0x48,A2=0,A1=0,A0=0) of STMP75ASOIGR
    SendBuf[0] = 0x00; // 寄存器0x00
    Status = XIicPs_MasterSendPolled(&IicPs_Instance, SendBuf, 
                                    sizeof(SendBuf), slaveaddr_lm75);
    if (Status != XST_SUCCESS) {
        log_warnline("XIicPs_MasterSendPolled lm75 failed");
        return 0;
    }


    u8 ReadBuf[2] = {0x00, 0x00};
    slaveaddr_lm75 = tempSlaveAddr; // 1001 A2A1A0 R  --> 1001 A2A1A0 is slave addr(0x48,A2=0,A1=0,A0=0) of STMP75ASOIGR
    Status = XIicPs_MasterRecvPolled(&IicPs_Instance, ReadBuf, 
                                    sizeof(ReadBuf), slaveaddr_lm75);
    if (Status != XST_SUCCESS) {
        log_warnline("XIicPs_MasterRecvPolled lm75 failed");
        return 0;
    }

    // usleep(10000);

    // 温度数据解析（与原逻辑一致）
    short Temp = (ReadBuf[0] << 3) | (ReadBuf[1] >> 5);
    if (ReadBuf[0] & 0x80) {
        Temp -= 0x1000;
    }
    Temp = Temp * 10 / 8;

    return Temp;
}
```


## 五、代码分析

![[Pasted image 20251225165616.png]]

使能交换芯片的通道4：

1、CPU首先把交换芯片的从机地址告诉I2C控制器；

2、CPU然后把 “写” 告诉i2c控制器 (读写位)；

3、i2c控制器会收到 ACK bit位；

4、CPU然后把寄存器值写入i2c控制器；

5、i2c控制器会收到 ACK bit位；

6、i2c控制器会发送停止位给从机设备；


![[Pasted image 20251225165630.png]]

![[Pasted image 20251225165639.png]]


通过交换芯片访问温度传感器：

![[Pasted image 20251225165653.png]]


1、首先CPU把从机地址和写操作，通过i2c控制器发给温度传感器，告诉传感器接下来我要写东西；其次i2c控制器收到温度传感器的ACK信号；

2、CPU把寄存器地址通过i2c控制器发送给传感器，并收到传感器ACK，然后Master这边主动停止；

3、其次CPU把从机地址和读操作，通过i2c控制器发给温度传感器，并收到传感器的ACK，紧接着传感器会连续发送2字节的数据给i2c控制器，i2c控制器接收完后填充到caller的缓冲区。







# bottom



