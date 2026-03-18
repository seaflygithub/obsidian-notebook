
# 开发板：黑金AX7020裸机实验

1、正点原子7010小系统板：

- 《1_ZYNQ小系统板之FPGA开发指南_V1.0.pdf》—— 正点原子7010小系统板(xc7z010clg400-1)
- 《course_s1_ZYNQ那些事儿-FPGA实验篇V1.06.pdf》—— 黑金AX7020开发板(xc7z020clg400-2)

1、参考资料(黑金AX7020)

- 《cource_s1_ALINX_ZYNQ(AX7010_AX7020)开发平台基础教程V1.10.pdf》
- 《course_s2_ALINX_ZYNQ开发平台SDK应用教程V2.04.pdf》

2、工程配置(黑金AX7020)

- xc7z020clg400-2
- DDR: MT41J256M16 RE-125
- Bank0: LVCMOS 3.3V
- Bank1: LVCMOS 1.8V
- 串口UART1: MIO48,49
- 以太网口: MIO16~27, MDIO为 MIO52,53
- SD卡: MIO40~45, CD引脚为: MIO47

## ZYNQPL-点灯闪烁实验

1、通过vivado新建开发板的空工程，添加并编写如下例程模块代码。

```verilog
module led_twinkle(
    input          sys_clk  ,  //系统时钟
    input          sys_rst_n,  //系统复位，低电平有效
    output         led         //LED灯
);

//小系统板原理图得知,高电平表示点亮LED
parameter LED_ON = 1'b1;

reg  [25:0]  sys_clk_cnt ;

//对计数器的值进行判断，以输出LED的状态
//由于输入的系统时钟为50MHz, 所以这里以前半秒钟点亮LED，后半秒熄灭LED
assign led = (sys_clk_cnt < 26'd2500_0000) ? LED_ON : (!LED_ON) ;

//计数器在0~5000_000之间进行计数
always @ (posedge sys_clk or negedge sys_rst_n) begin
    if(!sys_rst_n)
        sys_clk_cnt <= 26'd0;
    else if(sys_clk_cnt < 26'd5000_0000)
        sys_clk_cnt <= sys_clk_cnt + 1'b1;
    else
        sys_clk_cnt <= 26'd0;
end

endmodule

```

2、例程约束文件: 只是文件内的完整代码，只有引脚约束，没有时钟约束。这个章节主要了解引脚的约束关系, 即模块的输入输出是如何作用到FPGA的引脚上的。

```
#IO管脚约束
set_property -dict {PACKAGE_PIN U18 IOSTANDARD LVCMOS33} [get_ports sys_clk]
set_property -dict {PACKAGE_PIN N15 IOSTANDARD LVCMOS33} [get_ports sys_rst_n]
set_property -dict {PACKAGE_PIN J16 IOSTANDARD LVCMOS33} [get_ports led]

```

3、如下图所示，引脚约束参考原理图部分如下，其中时钟和复位引脚，复位引脚用一个PL端的按键来控制。


![[Pasted image 20251225165851.png]]


3、编译生成bit文件，然后把bit文件在线下载到开发板，之后就可以看到开发板LED等闪烁，亮半秒，灭半秒，亮半秒，如此循环。这里可以看到，只要有约束文件绑定顶层模块的输入输出，就相当于例化了顶层模块并激励了顶层模块，使其开始运转。

4、当bitstream一旦下载进去，PL LED4就开始闪烁了，按一下PL KEY1复位一下相关的信号，也能起到复位LED的作用。

![[Pasted image 20251225165908.png]]

## ZYNQPL-封装自定义IP核

1、参考文章：VIVADO 自定义封装ip核（超详细）: [[127758601]]

2、下面我们将用非常简单的模块代码（a+b=c），来演示如何封装成IP核。首先根据开发板(或目标板)型号，新建一个空工程，并且编写要封装的加法模块(seafly_add.v)，模块代码如下:

```verilog
`timescale 1ns / 1ps

module seafly_add(
    input               sys_clk  ,
    input               sys_rst_n,
    input  wire [31:0]  data_a,
    input  wire [31:0]  data_b,
    output reg [31:0]   data_c
);

always @ (posedge sys_clk or negedge sys_rst_n) begin
    if  (!sys_rst_n) begin
        data_c  <= 1'b0;
    end
    else begin
        data_c <= data_a + data_b;
    end
end

endmodule

```

3、然后为了验证模块的正确性，我们再添加一个激励文件来仿真跑一下，确保没问题了，再进行后续的封装。

```verilog
`timescale 1ns / 1ps
module seafly_add_tb();

reg             sys_clk;
reg             sys_rst_n;
reg [31:0]      data_a = 32'h10;
reg [31:0]      data_b = 32'h20;
wire [31:0]     data_c;

seafly_add  u_seafly_add(
    .sys_clk        (sys_clk        ),
    .sys_rst_n      (sys_rst_n      ),
    .data_a         (data_a         ),
    .data_b         (data_b         ),
    .data_c         (data_c         )
);

//仿真激励代码
always #10 sys_clk = ~sys_clk;

initial begin
    sys_clk     = 1'b0;
    sys_rst_n   = 1'b0;
    #200
    sys_rst_n   = 1'b1;
end

endmodule

```


![[Pasted image 20251225165926.png]]

4、经过仿真验证没问题了，接下来我们就要封装这个模块。

![[Pasted image 20251225165937.png]]

![[Pasted image 20251225165952.png]]


5、至此，seafly_add 模块封装完毕。然后我们新建一个 project_call 工程，来调用我们新封装的IP核。

![[Pasted image 20251225170007.png]]


![[Pasted image 20251225170019.png]]

![[Pasted image 20251225170027.png]]


6、直接新建并编写激励文件，通过激励文件来调用这个IP核，激励文件代码如下：

```verilog
`timescale 1ns / 1ps
module call_tb();

reg             sys_clk;
reg             sys_rst_n;
reg [31:0]      data_a = 32'h10;
reg [31:0]      data_b = 32'h20;
wire [31:0]     data_c;

seafly_add_0  u_seafly_add_0 (
    .sys_clk        (sys_clk        ),
    .sys_rst_n      (sys_rst_n      ),
    .data_a         (data_a         ),
    .data_b         (data_b         ),
    .data_c         (data_c         )
);

//仿真激励代码
always #10 sys_clk = ~sys_clk;

initial begin
    sys_clk     = 1'b0;
    sys_rst_n   = 1'b0;
    #200
    sys_rst_n   = 1'b1;
end

endmodule

```

## ZYNQPL-手搓时钟发生器

1、在前面的纯仿真和逻辑模块仿真的经验下，我们来尝试自己手搓一个简单的时钟发生器，后续的自定义IP核，就以这个时钟发生器作为封装对象。

2、首先根据目标板子新建一个空的vivado工程，然后新建一个逻辑文件，比如myclock.v，然后编写一个不依赖外部信号，能够自己产生时钟信号并提供给外部的功能，编写期间可以通过仿真来调试以达到你预期的结果。

```verilog
`timescale 1ns / 1ps

//scale_ns表示尺度为ns,不能小于ns
module myclock_scale_ns
#(
    //时钟极性(1=高电平/0=低电平): Clock polarity
    CLOCK_POLARITY_BEGIN = 0,

    //时钟相位: Clock phase
    CLOCK_PHASE_BEGIN = 0,

    //CLOCK_FREQ_MHZ只能设置这些值(MHz): 1,2,5,10,20,25,50,100,200,250,500
    //为什么只能设置这些值? 根据f=1/T,在纳秒精度下,周期T需要能够被整除
    //比如这里默认生成50MHz时钟信号
    CLOCK_FREQ_MHZ = 50
)
(
    output      o_clock
);

reg tmp_start = 1'b0;
reg o_clock = (CLOCK_POLARITY_BEGIN);

always@(*) begin
    if (tmp_start == 1'b1) begin
        #(1000/CLOCK_FREQ_MHZ/2)

        //TODO:这里本人尝试用组合逻辑的方式来赋值,但是仿真结果为恒定的初始值
        //但是改成时序逻辑赋值之后,就能正常产生时钟信号
        o_clock <= ~o_clock;
    end
    else begin
        #(CLOCK_PHASE_BEGIN)
        tmp_start <= 1'b1;
    end
end

endmodule

```

3、下面是仿真代码，由于该时钟模块没有输入，所以激励文件只起到例化的作用。

```verilog
`timescale 1ns / 1ps
module myclock_tb();
wire clock;

//例如我们需要生成100MHz的时钟信号
parameter CLOCK_FREQ_MHZ = 100;

//时钟起始极性为低电平
parameter CLOCK_POLARITY_BEGIN = 0;

//时钟相位偏移1个时钟,即在1ns精度下,偏移1ns
parameter CLOCK_PHASE_BEGIN = 1;

myclock_scale_ns #(
    .CLOCK_POLARITY_BEGIN   (CLOCK_POLARITY_BEGIN),
    .CLOCK_PHASE_BEGIN      (CLOCK_PHASE_BEGIN),
    .CLOCK_FREQ_MHZ         (CLOCK_FREQ_MHZ)
) u_myclock(
    .o_clock(clock)
);

initial begin
    //由于该时钟发生器没有输入,所以无需初始化任何信号
    ;;;
end

endmodule

```

4、如下图所示，下面是仿真的时序效果图。

![[Pasted image 20251225170047.png]]
## ZYNQPL-封装时钟发生器

1、前面我们手搓了一个时钟发生器模块，本小节我们把该模块进行封装，方便今后其他工程引用。首先直接打开时钟发生器的工程，然后在工程界面里，按照如下步骤进行操作。

![[Pasted image 20251225170058.png]]


2、添加testbench文件，以供引用者参考。

![[Pasted image 20251225170108.png]]


3、定制参数，以限定并指引用户设置。
![[Pasted image 20251225170126.png]]

![[Pasted image 20251225170134.png]]

4、参数设置好之后的预览效果，如下图所示：
![[Pasted image 20251225170147.png]]


5、时钟发生器模块封装好了，存放在前面指定的root目录，现在我们来创建另一个工程，来引用这个封装好的时钟发生器模块。
![[Pasted image 20251225170203.png]]


6、双击来生成该IP核的使用向导，然后就可以在代码里例化它了。

![[Pasted image 20251225170217.png]]

7、我们添加一个顶层（my_top.v），然后通过顶层模块来例化它，然后添加一个仿真激励文件来例化顶层。或者我们可以直接在仿真激励文件中例化该模块，这样就省略了顶层模块的编写。例化好之后，我们就可以启动仿真并查看效果图了。

```verilog
`timescale 1ns / 1ps
module hello_tb();

wire o_clock;

parameter CLOCK_FREQ_MHZ = 200;
parameter CLOCK_POLARITY_BEGIN = 0;
parameter CLOCK_PHASE_BEGIN = 1;
myclock_scale_ns_0
#(
    .CLOCK_POLARITY_BEGIN   (CLOCK_POLARITY_BEGIN),
    .CLOCK_PHASE_BEGIN      (CLOCK_PHASE_BEGIN),
    .CLOCK_FREQ_MHZ         (CLOCK_FREQ_MHZ)
) u_myclock (
  .o_clock(o_clock)  // output wire o_clock
);

initial begin
    //本实验无需初始化任何信号
    ;;;
end

endmodule

```


![[Pasted image 20251225170254.png]]

## ZYNQPL-AXIGPIO点亮LED

1、新建vivado工程，芯片根据开发板实际选择。

2、添加ZYNQ BD设计，外设仅仅勾选串口即可，主要用于观察。

3、添加AXI GPIO这个BD设计，然后设置位宽，这里我们只点亮一颗灯，那么就设置成一位。

![[Pasted image 20251225170309.png]]

4、然后依次点击 `Run Connection Automation`、`Run Block Automation`、`Optimize Routing`，然后修改端口名称，把GPIO口和LED分别改成其他名字，比如这里改成 `axi_led`。最后需要把顶层BD设计生成HDL文件（`Create HDL Wrapper`），然后查看跟这个`axi_led`相关的参数，后续的管脚约束需要用到这个信号参数。

![[Pasted image 20251225170354.png]]


5、好了，BD设计做好了，上图中红圈圈的部分，就是需要ZYNQ这边给个信号，然后信号通过AXI传导，最终传到红圈圈这里，如果这里连接着LED，那么LED将会被点亮或者熄灭。所以这里需要管脚约束，约束到LED。最后编译生成bit文件。

```cpp
set_property IOSTANDARD LVCMOS33 [get_ports {axi_led_tri_io}]
set_property PACKAGE_PIN J16 [get_ports {axi_led_tri_io}]
```


![[Pasted image 20251225170412.png]]

6、导出硬件信息，并加载XSDK，工程模板选择 Hello World，工程创建好之后，双击 system.mss 并找到 axi_gpio_0 ，并到入其相关例程。

![[Pasted image 20251225170424.png]]


7、这个实验PS可以通过AXI总线控制PL，视乎没有体现出 ZYNQ 的优势，因为对于控制 LED 灯，无论是 ARM 还是 FPGA，都可以轻松完成，但是如果把 LED 换成串口呢，控制 100 路串口通信，8 路以太网等应用，我想还没有哪个 SOC 能完成这种功能，只有 ZYNQ 可以，这就是 ZYNQ 和普通 SOC 的不同之处。

![[Pasted image 20251225170439.png]]


## ZYNQPL-自定义寄存器LED

1、接下来的实验，会演示PS如何访问自定义的PL模块功能。根据ZYNQ各个开发板的指导手册，并经过反复实验，得知PS如果想要使用PL这边实现的功能，都要通过统一的AXI总线来访问。因此，从逻辑的角度来看，PS需要通过AXI相关的接口实例来层层访问，最终访问到我们自定义的PL模块功能。这个PS层层访问下来的方向，也是层次之间的例化方向，最终例化到我们自定义的PL模块。

1、通过本实验我们可以掌握更多的 SDK 调试技巧，掌握了 ARM + FPGA 开发的核心内容，就是ARM 和 FPGA 数据交互。本实验主要掌握像寄存器这种轻量级的数据交互。用户在构建自己的系统中，不可能只使用 Xilinx 官方的免费 IP 核，很多时候需要创建属于自己的用户IP核，创建自己的IP核有很多好处，例如系统设计定制化；设计复用，可以在在IP核中加入license, 有偿提供给别人使用；简化系统设计和缩短设计时间。用 ZYNQ 系统设计 IP 核，最常用的就是使用 AXI 总线将 PS 同 PL 部分的 IP 核连接起来。

2、比如我们可以用纯逻辑写一个PL点灯模块，然后这个模块的功能需要由PS那边来控制。这里提供了一个LED点灯的verilog代码，输入参数是需要点亮哪颗灯，或者是需要熄灭哪颗灯，输出就是灯。先把下面的代码保存成一个led.v文件，后续做成AXI IP核的时候需要用到该文件。

2、根据开发板或者当前使用板子，新建一个干净的PL工程，用该工程封装一个AXI IP寄存器空壳子。真正的IP封装在IP Catalog里，找到我们新建的壳子，然后鼠标右键Edit in IP Packager，之后就根据流程，导入源文件并根据模板来例化对应的源文件模块。

![[Pasted image 20251225170455.png]]

![[Pasted image 20251225170502.png]]


添加逻辑文件，逻辑文件完整源代码如下:
![[Pasted image 20251225170518.png]]



最好把下面要封装的源代码，保存成pl_led.v文件，然后直接以文件形式添加进封装工程即可。

```verilog
`timescale 1ns/1ps
module pl_leds
#(
	//LED_ON_LEVEL: 1表示LED需要高电平点亮, 0表示LED需要低电平点亮
    LED_ON_LEVEL = 4'd1,
    LED_CNT      = 4'd4
 )
(
    input       clk,
    input       rst_n,
    input       led_on,             //reg0: 1=亮, 0=灭(只关心亮灭,不关心高低电平)
    input [LED_CNT-1:0] led_idx,    //reg1: 0=PL_LED0, 1=PL_LED1, ...
    output reg [LED_CNT-1:0] led_o
);

always@(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        led_o <= {LED_CNT{1'b0}};
    end
    else begin
        //LED_ON_LEVEL==1表示给高电平LED才会亮,LED_ON_LEVEL==0表示给低电平LED才会亮
        if (LED_ON_LEVEL == 1'b1) begin
            led_o <= (led_on)? (led_o | (1<<led_idx)):(led_o & (~(1<<led_idx)));
        end
        else begin
            led_o <= (led_on)? (led_o & (~(1<<led_idx))):(led_o | (1<<led_idx));
        end
    end
end

endmodule
```


![[Pasted image 20251225170542.png]]


```verilog
		// Users to add parameters here
		parameter integer LED_ON_LEVEL = 0,
		parameter integer LED_CNT      = 4,

		// Users to add ports here
		output wire [LED_CNT-1:0] led_o,

	axi_regled_v1_0_S00_AXI # (
		.C_S_AXI_DATA_WIDTH(C_S00_AXI_DATA_WIDTH),
		.C_S_AXI_ADDR_WIDTH(C_S00_AXI_ADDR_WIDTH),
	   .LED_ON_LEVEL       (LED_ON_LEVEL),//////////////////////add this
	   .LED_CNT            (LED_CNT)////////////////////////////add this
	) axi_regled_v1_0_S00_AXI_inst (
		.led_o              (led_o),////////////////////////////add this
		.S_AXI_ACLK(s00_axi_aclk),
		.S_AXI_ARESETN(s00_axi_aresetn),

	// Add user logic here
	pl_leds  # (
	   .LED_ON_LEVEL       (LED_ON_LEVEL),
	   .LED_CNT            (LED_CNT)
	) pl_leds_inst (
	   .clk                (S_AXI_ACLK),
	   .rst_n              (S_AXI_ARESETN),
	   .led_on             (slv_reg0),
	   .led_idx            (slv_reg1),
	   .led_o              (led_o)
	);

```

这里需要注意的点：自动打开IP核的临时封装工程之后，你需要首先添加你要封装的模块文件，然后还需要把模块文件例化到统一的接口代码里。最后才开始刷新操作如下界面。整个过程无需综合无需编译。

![[Pasted image 20251225170557.png]]

![[Pasted image 20251225170606.png]]

![[Pasted image 20251225170613.png]]

在其他工程中，如何使用该IP核？这里我们在其他工程的环境下，首先要把该IP核的仓库导入，然后才能在IP Catalog中找到我们自定义的IP核。导入操作如下图所示。
![[Pasted image 20251225170628.png]]


导入完成之后，我们就可以使用IP核了，这里我们在BD中找到并导入IP核，然后自动连线。最后把想要引出的线印出来，比如该工程中，把led_o这个端口引出来了（通过鼠标右键该端口，选中Make External选项进行引出，引出后会带箭头如下图所示）。

![[Pasted image 20251225170644.png]]


前面不是引出端口了么，但是这个端口输出给谁呢？我们需要让其有具体的输出对象，因此我们需要把引出的这个端口，进行引脚约束，表示让其输出到具体的某个管脚上。在约束管脚之前，我们需要对整个design_1这个BD生成HDL向导，即鼠标右键BD并选择Create HDL Wrapper选项，生成向导之后，我们才能从顶层代码的端口列表中看到我们要约束的引脚regleds。
![[Pasted image 20251225170657.png]]



```verilog
set_property -dict {PACKAGE_PIN M14 IOSTANDARD LVCMOS33} [get_ports {regleds[0]}]
set_property -dict {PACKAGE_PIN M15 IOSTANDARD LVCMOS33} [get_ports {regleds[1]}]
set_property -dict {PACKAGE_PIN K16 IOSTANDARD LVCMOS33} [get_ports {regleds[2]}]
set_property -dict {PACKAGE_PIN J16 IOSTANDARD LVCMOS33} [get_ports {regleds[3]}]

```

添加完引脚约束后，我们就可以编译生成bitstream了。之后导出硬件信息，启动XSDK，参考导出的硬件信息里提供的驱动示例代码，我们新建hello工程，并使用其中某些接口来完成我们的点灯实验。完整的点灯代码如下。

![[Pasted image 20251225170714.png]]


![[Pasted image 20251225170722.png]]


```cpp
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"
#include "sleep.h"
#include "axi_regled.h"

//	   .led_on     (slv_reg0       ),
//	   .led_idx    (slv_reg1       ),
#define AXI_LED_BASE    XPAR_AXI_REGLED_0_S00_AXI_BASEADDR
#define AXI_LED_REG_ON  AXI_REGLED_S00_AXI_SLV_REG0_OFFSET
#define AXI_LED_REG_IDX AXI_REGLED_S00_AXI_SLV_REG1_OFFSET

void axi_leds_off(void)
{
    unsigned int led_on = 0;
    unsigned int led_idx = 0;
    unsigned int led_cnt = 4;
	for(led_idx=0; led_idx<led_cnt;led_idx++)
	{
    	AXI_REGLED_mWriteReg(AXI_LED_BASE, AXI_LED_REG_IDX, led_idx);
    	AXI_REGLED_mWriteReg(AXI_LED_BASE, AXI_LED_REG_ON, led_on);
	}
}

int main()
{
    init_platform();

    unsigned int led_on = 1;
    unsigned int led_idx = 0;
    unsigned int led_cnt = 4;
    long count = 0;

    axi_leds_off();

    while (1)
    {
    	printf("[%ld] Now led_on == %d\\\\r\\\\n", ++count, led_on);
    	for(led_idx=0; led_idx<led_cnt;led_idx++)
    	{
        	AXI_REGLED_mWriteReg(AXI_LED_BASE, AXI_LED_REG_IDX, led_idx);
        	AXI_REGLED_mWriteReg(AXI_LED_BASE, AXI_LED_REG_ON, led_on);
        	usleep(1000 * 400);
    	}
    	led_on = !led_on;
    }

    cleanup_platform();
    return 0;
}

```

总结：你可以理解为，PL那边的模块被AXI统一抽象了，然后PS这边就按照AXI的标准方式来访问PL那边的模块功能。在这里，PL的功能参数通过寄存器来和PS对接，PS这边只要读写对应的寄存器，就能达到给PL这边的模块传递参数从而控制PL这边模块功能的作用。

踩坑经验：封装IP时最好新建一个干净的工程，这个工程只封装该IP。



## ZYNQPL-点灯LED呼吸灯

1、呼吸灯采用 PWM 的方式，即在固定的频率下(或者说在周期相同的情况下)，通过调整占空比的方式来控制 LED 灯亮度的变化。PWM技术利用微处理器输出的 PWM 信号，实现对模拟电路控制的一种非常有效的技术。

2、PWM频率、周期、占空比：PWM频率表示一秒钟有多少个PWM周期，单位为Hz；PWM周期就是PWM频率的倒数；比如1秒钟有50次PWM周期，那么PWM频率为50Hz，根据公式 T=1/f 得到周期T=20ms。

![[Pasted image 20251225170746.png]]

3、下面代码是开发板提供的代码，分析已有代码，掌握其原理，然后不断迭代模仿。

```verilog
module breath_led(
    input   sys_clk   ,  //时钟信号50Mhz(通过引脚约束引入50MHz)
    input   sys_rst_n ,  //复位信号
    output  led          //LED
);

parameter LED_ON = 1'b1; //小系统板原理图得知,高电平表示点亮LED

//reg define
reg  [15:0]  period_cnt ;   //周期计数器频率：1khz 周期:1ms  计数值:1ms/20ns=50000
reg  [15:0]  duty_cycle ;   //占空比数值
reg          inc_dec_flag ; //0 递增  1 递减

//根据占空比和计数值之间的大小关系来输出LED
//组合逻辑: 根据占空比和计数值之间的大小关系来输出LED
assign   led = (period_cnt >= duty_cycle) ?  LED_ON  :  (!LED_ON);

//周期计数器
always @(posedge sys_clk or negedge sys_rst_n) begin
    if(!sys_rst_n)
        period_cnt <= 16'd0;
    else if(period_cnt == 16'd50000)
        period_cnt <= 16'd0;
    else
        period_cnt <= period_cnt + 1'b1;
end

//在周期计数器的节拍下递增或递减占空比
always @(posedge sys_clk or negedge sys_rst_n) begin
    if(!sys_rst_n) begin
        duty_cycle   <= 16'd0;
        inc_dec_flag <= 1'b0;
    end
    else begin
        if(period_cnt == 16'd50000) begin    //计满1ms
            if(inc_dec_flag == 1'b0) begin   //占空比递增状态
                if(duty_cycle == 16'd50000)  //如果占空比已递增至最大
                    inc_dec_flag <= 1'b1;    //则占空比开始递减
                else                         //否则占空比以25为单位递增
                    duty_cycle <= duty_cycle + 16'd25;
            end
            else begin                       //占空比递减状态
                if(duty_cycle == 16'd0)      //如果占空比已递减至0
                    inc_dec_flag <= 1'b0;    //则占空比开始递增
                else                         //否则占空比以25为单位递减
                    duty_cycle <= duty_cycle - 16'd25;
            end
        end
    end
end

endmodule

```

4、对开发板官方代码拆解分析时序图如下，根据开发板提供的呼吸灯代码分析得出如下时序图，也是本人理解了之后的东西。

![[Pasted image 20251225170800.png]]



---

下面我们就根据对开发板代码的理解，自己一步一步慢慢迭代写出功能相同的代码，并一步一步迭代优化代码。

1、最开始我们还不知道怎么写出呼吸灯，我们可以从最基础的闪灯开始，先把闪灯程序写出来。下面代码的实验现象是：当bit下载进开发板以后，LED亮一秒，然后灭一秒，然后亮一秒，然后灭一秒，如此循环。值得注意的是，其中输出参数led, 只能用assign赋值，无法放到always语句块里赋值。

```verilog
module breath_led(
    input   sys_clk   ,  //时钟信号50Mhz
    input   sys_rst_n ,  //复位信号
    output  led          //LED
);

reg [31:0] sys_clk_cnt = 0;
reg        led_on = 0;

assign led = (led_on)? 1:0;//控制LED亮灭

always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n) begin
        sys_clk_cnt <= 0;
    end
    else begin
        if (sys_clk_cnt == 32'd50_000_000) begin
            sys_clk_cnt <= 0;
            led_on <= ~led_on;
        end
        else begin
            sys_clk_cnt <= sys_clk_cnt + 32'd1;
        end
    end
end

endmodule

```

2、该迭代版本是和前面一个版本功能效果一样，只不过这个版本不用assign给led赋值。

```verilog
module breath_led(
    input        sys_clk   ,  //时钟信号50Mhz
    input        sys_rst_n ,  //复位信号
    output  reg  reg_led          //LED
);
reg [31:0] sys_clk_cnt = 0;
reg        led_on = 0;

//assign ass_led = (ass_led)? 1:0;

always @(*) begin
    reg_led = (led_on)? 1:0;//控制LED亮灭
end

always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n) begin
        sys_clk_cnt <= 0;
    end
    else begin
        if (sys_clk_cnt == 32'd50_000_000) begin
            sys_clk_cnt <= 0;
            led_on <= ~led_on;
        end
        else begin
            sys_clk_cnt <= sys_clk_cnt + 32'd1;
        end
    end
end

endmodule

```

3、呼吸灯从最亮慢慢变到最暗，然后立马回到最亮，然后继续从最亮慢慢变到最暗，如此往复。

```verilog
module breath_led(
    input        sys_clk   ,  //时钟信号50Mhz
    input        sys_rst_n ,  //复位信号
    output  reg  reg_led          //LED
);

reg [31:0] pwm_clk_cnt = 0;
reg [31:0] pwm_duty_cnt = 0;

always @(*) begin
    reg_led = (pwm_clk_cnt >= pwm_duty_cnt)? 1:0;//控制LED亮灭
end

always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n) begin
        pwm_duty_cnt <= 0;
    end
    else begin
        if (pwm_clk_cnt == 32'd50_000) begin
            if (pwm_duty_cnt == 32'd50_000)
                pwm_duty_cnt <= 0;
            else
                pwm_duty_cnt <= pwm_duty_cnt + 10;
        end
    end
end

always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n) begin
        pwm_clk_cnt    <= 0;
    end
    else begin
        if (pwm_clk_cnt == 32'd50_000)
            pwm_clk_cnt <= 0;
        else
            pwm_clk_cnt <= pwm_clk_cnt + 1;
    end
end

endmodule

```

4、呼吸灯从最亮慢慢变到最暗，然后从最暗又慢慢变最亮，如此往复。

```verilog
module breath_led(
    input        sys_clk   ,  //时钟信号50Mhz
    input        sys_rst_n ,  //复位信号
    output  reg  reg_led      //LED
);

localparam LED_ON       = 1;  //0=低电平点亮, 1=高电平点亮
reg [31:0] pwm_freq_cnt = 0;  //把sys_clk分频之后的时钟计数器
reg [31:0] pwm_duty_cnt = 0;  //占空比计数器
reg        pwm_duty_dir = 0;  //占空比递增/递减, 0=递增, 1=递减

always @(*) begin
    reg_led = (pwm_freq_cnt > pwm_duty_cnt)? LED_ON:(!LED_ON);
end

always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n) begin
        pwm_duty_cnt <= 0;
    end
    else begin
        if (pwm_freq_cnt == 32'd50_000) begin
            //pwm_duty_dir == 0 (递增)
            if (!pwm_duty_dir) begin
                if (pwm_duty_cnt == 32'd50_000) begin
                    pwm_duty_dir <= ~pwm_duty_dir;
                end
                else begin
                    //随着 pwm_duty_cnt 逐渐增大, 占空比不断也逐渐变小, LED灯会逐渐变暗
                    pwm_duty_cnt <= pwm_duty_cnt + 20;
                end
            end
            else begin //pwm_duty_dir == 1 (递减)
                if (pwm_duty_cnt == 32'd00_000) begin
                    pwm_duty_dir <= ~pwm_duty_dir;
                end
                else begin
                    //随着 pwm_duty_cnt 逐渐变小, 占空比不断也逐渐变大, LED灯会逐渐变亮
                    pwm_duty_cnt <= pwm_duty_cnt - 20;
                end
            end
        end
    end
end

always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n) begin
        pwm_freq_cnt    <= 0;
    end
    else begin
        if (pwm_freq_cnt == 32'd50_000)
            pwm_freq_cnt <= 0;
        else
            pwm_freq_cnt <= pwm_freq_cnt + 1;
    end
end

endmodule

```



## ZYNQPL-通过PWM控制LED亮度

1、在固定的频率下(或者说在周期相同的情况下)，通过调整占空比的方式来控制 LED 灯亮度的变化。这就是PWM技术。PWM技术利用微处理器输出的 PWM 信号，实现对模拟电路控制的一种非常有效的技术。

2、PWM频率、周期、占空比：PWM频率表示一秒钟有多少个PWM周期，单位为Hz；根据频率和周期之间的公式，得知PWM周期就是PWM频率的倒数；比如1秒钟有50次PWM周期，那么PWM频率为50Hz，根据公式 T=1/f 得到周期T=20ms。

![[Pasted image 20251225170852.png]]

3、通过对开发板呼吸灯代码的分析，以及运行代码看效果，得出了如下原理图。

![[Pasted image 20251225170905.png]]


4、根据上图，代入典型值来进行推理，然后通过实验一步步验证这些推理：

- （01）假设PWM周期宽度是1秒，占空比是100%，即全程高电平，那么此时LED灯完全点亮。
- （02）假设PWM周期宽度是1秒，占空比是0%，即全程低电平，那么此时LED灯完全熄灭。
- （03）假设PWM周期宽度是1秒，占空比是50%，那么此时LED灯有很明显的亮半秒，灭半秒的现象。
- （04）假设PWM周期宽度是1秒，占空比是10%，那么此时LED灯有很明显的亮灭现象，亮一下后立马灭，亮一下后立马灭。
- （05）假设PWM周期宽度是1/10秒，占空比是10%，此时LED灯会那种很明显的高亮度快速闪烁。
- （06）假设PWM周期宽度是1/100秒，占空比是10%，此时LED灯明显亮度不高，且肉眼看不到任何闪烁，给人一种低亮度常亮的感觉。如果在频率不变的情况下，仅仅改变占空比，就能达到控制LED灯亮度的效果。

3、下面我们开始验证上述推理，我们用中学时期最朴素的探究方法（控制变量法）：占空比控制在10%固定不变，只调整PWM频率，比如这里1秒只有一个PWM周期，也就是PWM频率只有1Hz，编译下载到开发板，LED灯的现象就是上述的推理（4）。

```verilog
`timescale 1ns / 1ns

module led01_top(
    input          sys_clk  ,  //系统时钟
    input          sys_rst_n,  //系统复位，低电平有效
    output         led         //LED灯
);

parameter LED_ON     = 1'b1;
parameter SYS_FS_CNT = 32'd50_000_000; //SYS时钟计数器: 50MHz
parameter PWM_FS_CNT = 32'd50_000_000; //PWM时钟计数器: 50MHz

reg  [31:0]  sys_freq_cnt = 0;
reg  [31:0]  pwm_freq_cnt = 0;
reg  [31:0]  pwm_duty_cnt = PWM_FS_CNT / 10; //占空比10%

// 根据占空比来点亮或者熄灭LED，此时该版本代码的占空比固定为10%
assign led = (pwm_duty_cnt > pwm_freq_cnt)? (LED_ON):(!LED_ON);

// PWM频率计数器, 由于 (PWM_FS_CNT == SYS_FS_CNT) ,所以此时PWM只有一个PWM周期
always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n)
        pwm_freq_cnt <= 1'b0;
    else begin
        if (pwm_freq_cnt == PWM_FS_CNT)
            pwm_freq_cnt <= 1'b0;
       else
            pwm_freq_cnt <= pwm_freq_cnt + 1'b1;
    end
end

always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n)
        sys_freq_cnt <= 1'b0;
    else begin
        if (sys_freq_cnt == SYS_FS_CNT)
            sys_freq_cnt <= 1'b0;
       else
            sys_freq_cnt <= sys_freq_cnt + 1'b1;
    end
end

endmodule

```



## ZYNQPL-EMIO点亮LED

1、如下图所示，下图就是完整的流程组合套餐了，直接跟着流程走就行。

![[Pasted image 20251225170933.png]]


```cpp
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"
#include "sleep.h"
#include "xgpiops.h"

int main()
{
    init_platform();

    u16 DeviceId = 0;
    int ret = 0;
    XGpioPs_Config *config;
    XGpioPs xgpio_inst;
    XGpioPs *InstancePtr = &xgpio_inst;

    unsigned int led_on = 1;
    unsigned int led_idx = 0;
    unsigned int led_cnt = 4;
    unsigned long count = 0;

    config = XGpioPs_LookupConfig(DeviceId);
    ret = XGpioPs_CfgInitialize(InstancePtr, config, config->BaseAddr);

    XGpioPs_SetDirectionPin(InstancePtr, 54, 1);
    XGpioPs_SetDirectionPin(InstancePtr, 55, 1);
    XGpioPs_SetDirectionPin(InstancePtr, 56, 1);
    XGpioPs_SetDirectionPin(InstancePtr, 57, 1);
    XGpioPs_SetOutputEnablePin(InstancePtr, 54, 1);
    XGpioPs_SetOutputEnablePin(InstancePtr, 55, 1);
    XGpioPs_SetOutputEnablePin(InstancePtr, 56, 1);
    XGpioPs_SetOutputEnablePin(InstancePtr, 57, 1);

    while (1)
    {
    	printf("[%ld] Now led_on == %d\\\\r\\\\n", ++count, led_on);
    	for(led_idx=0; led_idx<led_cnt;led_idx++)
    	{
    		XGpioPs_WritePin(InstancePtr, 54 + led_idx, led_on);
        	usleep(1000 * 400);
    	}
    	led_on = !led_on;
    }

    cleanup_platform();
    return 0;
}

```

下面是需要注意的点，如下图红字所述，我们需要根据实际情况指定位宽。然后修改变动之后，需要重新生成HDL相关的引导文件， 其实就是重新更新一下HDL引导文件。关于更新HDL需要注意的一些点，请继续往下看。

![[Pasted image 20251225170947.png]]


```cpp
//综合的错误日志:runme.log
ERROR: [DRC NSTD-1] Unspecified I/O Standard: 60 out of 194 logical ports use I/O standard (IOSTANDARD) value 'DEFAULT', instead of a user assigned specific value. This may cause I/O contention or incompatibility with the board power or connectivity affecting performance, signal integrity or in extreme cases cause damage to the device or the components to which it is connected.

```

如下图所示，红色数字是操作顺序，2号流程更新HDL引导，以及4号流程来更新顶层文件。

![[Pasted image 20251225171000.png]]



## ZYNQPS-定时器中断

1、很多 SOC 内部都会有定时器，ZYNQ 的 PS 也有，对于 ZYNQ 内到底有什么外设，这些外设有什么特性，都是开发者必须关心的，因此建议经常阅读 xilinx 文档 UG585。

2、基于上一个工程，我们把上一个工程另存为新的工程名即可，同样是通过双击 system.mss 文件，导入 scutimer 相关的例程。下面就是阅读代码，然后修改代码了，当然，可能一下不能完全理解这些代码，只能在以后的应用中去反复练习。

![[Pasted image 20251225171015.png]]


中断发生流程：如下图所示，定时器作为中断源，发送中断信号给GIC，GIC收到后，转发给CPU，CPU这边触发异常，且异常为IRQ类型的异常，然后就会跳转到IRQ相关的异常处理，在保存好现场环境后，就继续调用函数。比如下面IRQ最终进入到ScuGic相关的处理函数，通过分析代码得出，该函数会直接从GIC某寄存器中读取中断ID，这个中断ID就是定时器的中断ID，表明当前中断就是定时器发起的。因此会进一步，利用这个中断ID，作为数组索引，去找到对应的数组元素，这个元素里包含了已经准备好的定时器中断回调函数和参数。如果存在这个回调函数，或者说如果软件注册了这个回调函数，则会自动调用该回调函数。回调函数处理完之后，立马返回，然后就这样层层返回，最终又恢复环境，让CPU的PC指针继续回到之前被打断的位置继续执行被打断的任务。

![[Pasted image 20251225171027.png]]


3、本实验设计一个 1 秒定时器中断一次，然后打印出信息，30 秒后结束，首先修改计数器最大值，修改为 CPU 频率的一半，也就是计数器的时钟频率值，这样就会 1 秒中断一次。

```cpp
//改动的代码如下:

//定时器计数器的值做减法一直减到0之后，又重新从初始值开始做减法
XScuTimer_EnableAutoReload(TimerInstancePtr);

//设置定时器计数器的初始值，当定时器启动之后，定时器计数器就会基于该值做减法
XScuTimer_LoadTimer(TimerInstancePtr, TIMER_LOAD_VALUE);

//由于ug585定时器章节说了,通常定时器时钟频率是CPU频率的1/2，所以这里为了达到1秒一个中断的效果，于是除以2
#define TIMER_LOAD_VALUE    (XPAR_PS7_CORTEXA9_0_CPU_CLK_FREQ_HZ/2)
#define MAX_TIMER_EXPIRED   30

static void TimerIntrHandler(void *CallBackRef)
{
	XScuTimer *TimerInstancePtr = (XScuTimer *) CallBackRef;
	if (XScuTimer_IsExpired(TimerInstancePtr)) {
		XScuTimer_ClearInterruptStatus(TimerInstancePtr);
		TimerExpired++;
		printf("TimerExpired = %d\\\\r\\\\n", TimerExpired);
		if (TimerExpired == MAX_TIMER_EXPIRED) {
			XScuTimer_DisableAutoReload(TimerInstancePtr);
		}
	}
}

```

4、实验中通过简单的修改 SDK 的例程，就完成了定时器，中断的应用，看似简单的操作，可蕴含了丰富的知识，我们需要非常了解定时器的原理、中断的原理，这些基本知识是学习好 ZYNQ 的必要条件。

5、下面是定时器中断的整个软件结构梳理：某外设触发了中断，该中断信号会首先发送给中断控制器，中断控制器再统一发送给CPU，CPU收到中断信号后，立马进入异常向量表，然后外设大部分是IRQ类型的中断，因此CPU异常会进入IRQ这个case里，然后根据函数层层往里调用，最终调用到IQRInterrupt这个函数，这个会执行IRQ类型索引的处理函数，比如索引值为IRQ，在该索引下对应的处理函数里，会继续从GIC里读取相关寄存器，来得知具体是哪个IRQ ID触发了中断，然后继续以这个IRQ ID作为索引，找到具体设备的中断处理函数。

![[Pasted image 20251225171044.png]]


```cpp
XExc_VectorTable[XIL_EXCEPTION_ID_IRQ_INT].Handler = XScuGic_InterruptHandler;
XExc_VectorTable[XIL_EXCEPTION_ID_IRQ_INT].Data    = XScuGicInstance;

//你可以理解为，这些代码就是CPU进入向量表中的IRQ项之后要执行的代码
void XScuGic_InterruptHandler(XScuGic *InstancePtr)
{
	u32 InterruptID;
    u32 IntIDFull;
    XScuGic_VectorTableEntry *TablePtr;

	//获取到具体外设的中断ID，即到底是哪个外设产生了IRQ中断，比如获取到定时器的中断ID
    IntIDFull = XScuGic_CPUReadReg(InstancePtr, XSCUGIC_INT_ACK_OFFSET);
    InterruptID = IntIDFull & XSCUGIC_ACK_INTID_MASK;

	//然后以外设中断ID作为索引，找到对应的处理函数ISR，并执行这个ISR
    TablePtr = &(InstancePtr->Config->HandlerTable[InterruptID]);
    if (TablePtr != NULL) {
        TablePtr->Handler(TablePtr->CallBackRef);
    }

IntrExit:
    XScuGic_CPUWriteReg(InstancePtr, XSCUGIC_EOI_OFFSET, IntIDFull);
}

```

## ZYNQPL-按键中断实验

1、前面的定时器中断实验的中断属于 PS 内部的中断，本实验中断来自 PL，PS 最大可以接收16 个来自 PL 的中断信号，都是上升沿或高电平触发。本实验用按键中断来控制 LED。

2、在前面工程的基础上，新增一个AXI GPIO的BD设计，然后ZYNQ里勾选上 `IRQ_F2P`。最后添加按键的引脚约束，编译。

```cpp
set_property IOSTANDARD LVCMOS33 [get_ports {axi_key_tri_i}]
set_property PACKAGE_PIN N15 [get_ports {axi_key_tri_i}]

```


![[Pasted image 20251225171100.png]]


3、导出硬件信息，并启动XSDK，新建hello模板，并导入 `axi_gpio` 例程，其中选择带intr例程。

```cpp
//整个例程代码里,比较重要的就是这个F2P的中断ID
#define XPAR_FABRIC_GPIO_1_VEC_ID XPAR_FABRIC_AXI_GPIO_1_IP2INTC_IRPT_INTR

```

4、中断ID可根据
![[Pasted image 20251225171113.png]]



## ZYNQPS-按键中断实验


![[Pasted image 20251225171132.png]]


![[Pasted image 20251225171139.png]]


![[Pasted image 20251225171146.png]]





## cortex-a9-gic

一般在系统中，中断控制分为三个部分：模块、中断控制器、处理器。

模块决定是否使用中断；中断控制器管理优先级等，而处理器用来响应中断。

GIC —— Generic Interrupt Controller，目前有四个版本，V1～V4(V2最多支持8个ARM core，V3/V4支持更多的ARM core，主要用于ARM64系统结构）。

GIC-400 —— 该控制器通过 AMBA(Advanced Microcontroller Bus Architecture)片上总线连接到一个或者多个ARM处理器上。ARM CPU 对外的连接只有2 个中断： IRQ和FIQ ，所以GIC 最后要把中断汇集成2 条线，与CPU 对接。GIC内部的分发器总是把优先级最高的那个中断请求送往CPU接口。

中断使能或禁能控制 —— 分发器对中断的控制分成两个级别，一个是全局中断的控制（GIC_DIST_CTRL），一旦禁能了全局的中断，那么任何的中断源产生的中断事件都不会被传递到CPU接口；另外一个级别是对针对各个中断源进行控制（GIC_DIST_ENABLE_CLEAR），禁能某一个中断源会导致该中断事件不会分发到CPU接口，但不影响其他中断源产生中断事件的分发。相当于GIC内部有个总开关，以及更细化的每个外设的开关。

CPU接口功能 —— 相当于CPU这边还有相关的管理功能，用来决定是否相应GIC发过来的中断事件。中断一旦被应答，分发器就会把该中断的状态从pending状态修改成active。当中断处理器处理完了一个中断的时候，会通过某种方式通知GIC已经处理完该中断。做这个动作一方面是通知分发器将中断状态修改为deactive，另外一方面，可以允许其他的pending的中断向CPU接口提交。通过优先级掩码可以mask掉一些优先级比较低的中断，这些中断不会通知到CPU。在多个中断事件同时到来的时候，选择一个优先级最高的通知CPU。

ARM 公司在设计 ARMv7-A 架构时，给 CPU 硬件定了一条**无差别执行、不可修改的硬件硬规则**，这条规则就是你问题的全部答案。**只有异常模式才拥有 SPSR 寄存器，正常模式下这个寄存器不存在，读 / 写都会报错；

ARM处理器要么处在普通模式，要么处在异常模式，普通模式有user、svc两种模式，大部分时间都是在普通模式下，只有发生中断或者其他异常的时候，才会短暂在异常模式下。你可以把处理器的这几种模式理解为一个人的普通状态和紧急状态。


```cpp
.globl _vector_table

.section .vectors
_vector_table:
	B	_boot
	B	Undefined
	B	SVCHandler
	B	PrefetchAbortHandler
	B	DataAbortHandler
	NOP	/* Placeholder for address exception vector*/
	B	IRQHandler
	B	FIQHandler
```




## ZYNQPL-ILA调试核的使用

1、找一个最简单的PL工程，然后我们在这个工程的基础上把ILA用起来，为什么使用最简单的工程，因为我们本小节探究的是ILA的使用。所以尽量把其他因素的复杂度降到最低，从而不会影响大脑对ILA的学习。

2、这里我们找最简单的PL-LED工程，然后在 IP Catalog 中找到 ILA(Integrated Logic Analyzer) 并添加它。


![[Pasted image 20251225171158.png]]

3、PROBE0用来抓取计数器的值，PROBE1用来抓取四颗LED灯的高低电平。然后就可以直接编译生成bitstream文件了。

![[Pasted image 20251225171208.png]]

4、还有一种简便的添加ILA的方法，这是在BD设计图中，选中需要监控的连线，然后右键选择Debug，即可自动为这些信号线添加ILA模块。如下图所示。

![[Pasted image 20251225171220.png]]


## ZYNQPL-PLL时钟分频

1、资料上相关章节首先开篇讲了一大堆理论，我们无需一口气掌握其所有理论基础。我们目前只需要知道，我们要使用该IP核把一个50MHz的时钟公分成多个时钟，每个时钟都不同，这里我们公分成4个时钟。首先通过vivado新建该开发板的空工程（xc7z010clg400-1）。

2、然后在IP核目录里找到 Clocking Wizard 这个IP核，双击进入IP核的配置界面，然后只需要修改如下配置即可。

![[Pasted image 20251225171233.png]]

3、参考该IP核的例化模板文件，例化该IP核。
![[Pasted image 20251225171243.png]]


4、把输出的时钟，约束到引脚上，可以通过示波器来查看这些引脚的输出频率。
![[Pasted image 20251225171253.png]]




```verilog
// 1、根据开发板实物找到印出来的扩展IO口，
// 2、然后根据实物丝印J7, 再选几个合适的引脚，在原理图中，并根据引脚找对最终要约束的引脚编号。
// J7 --> B35_L13_P  --> H16
// J7 --> B35_L13_N  --> H17
// J7 --> B35_L19_P  --> H15
// J7 --> B35_L19_N  --> G15

set_property -dict {PACKAGE_PIN U18 IOSTANDARD LVCMOS33} [get_ports sys_clk]
set_property -dict {PACKAGE_PIN J15 IOSTANDARD LVCMOS33} [get_ports sys_rst_n]
set_property -dict {PACKAGE_PIN H15 IOSTANDARD LVCMOS33} [get_ports clk_100m]
set_property -dict {PACKAGE_PIN H16 IOSTANDARD LVCMOS33} [get_ports clk_100m_180deg]
set_property -dict {PACKAGE_PIN G15 IOSTANDARD LVCMOS33} [get_ports clk_50m]
set_property -dict {PACKAGE_PIN H17 IOSTANDARD LVCMOS33} [get_ports clk_25m]

```

5、下面是纯激励文件，直接通过激励文件来例化该IP核，查看其仿真效果。

```verilog
`timescale 1ns / 1ps
module clk_wiz_tb();

reg        sys_clk;
reg        sys_rst_n;

wire       clk_100m;
wire       clk_100m_180deg;
wire       clk_50m;
wire       clk_25m;
wire       locked;

always #10 sys_clk = ~sys_clk;

initial begin
    sys_clk   = 0;
    sys_rst_n = 0;
    #200;
    sys_rst_n = 1;
end

clk_wiz_0 clk_wiz_0(
    .clk_out1        (clk_100m),
    .clk_out2        (clk_100m_180deg),
    .clk_out3        (clk_50m),
    .clk_out4        (clk_25m),

    .resetn          (sys_rst_n),
    .locked          (locked),
    .clk_in1         (sys_clk)
);

endmodule
```


![[Pasted image 20251225171311.png]]




## ZYNQPL-最简单的三段式状态机

参考资料:

- 状态机FSM的各种写法: [[119421783]]
- 数电和Verilog-时序逻辑实例四：状态机（三段式描述）: [[BV1Et4y1s7MH]]
- 通信帧头检测: [[BV1pT411C7dA]]
- 完全掌握有限状态机的写法: [[424793349]]

1、这里需要首先有个起点，而我们对状态机的初步认识，以及后续对状态机复杂特性的学习，都是从这个起点开始，即需要有个最简单的例子，来不断迭代逐渐展开状态机的更多特性，无论这些特性多少，都是为了解决现实中所面临的问题而产生的特性。所以我们一定要以实际问题出发。比如特性C，在A的实际场景根本不会发生，所以特性C可以在A场景的应用中割舍。

2、比如下面的例子，在字符串中找到 "abc" 的序列，如果匹配上，则 fsm_output 拉高，否则拉低。

```verilog
`timescale 1ns / 1ps
module fsm_tb();

reg             sys_clk;
reg             sys_rst_n;

parameter FSM_S0 = 7'b0000000;
parameter FSM_S1 = 7'b0000001;
parameter FSM_S2 = 7'b0000010;
parameter FSM_S3 = 7'b0000100;
reg [6:0] fsm_curr_state;
reg [6:0] fsm_next_state;

reg [7:0] fsm_input;
reg       fsm_output;

//状态机的第一段采用同步时序描述状态转移
always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n) begin
        fsm_curr_state <= FSM_S0;
        fsm_next_state <= FSM_S0;
    end
    else begin
        fsm_curr_state <= fsm_next_state;
    end
end

//状态机的第二段采用组合逻辑判断状态转移条件
always @(*) begin
    //根据【当前输入 && 当前状态】来决定下一个状态
    case (fsm_curr_state)
        FSM_S0: begin
            if (fsm_input == "a") begin
                fsm_next_state = FSM_S1;
            end
            else begin
                fsm_next_state = FSM_S0;
            end
        end
        FSM_S1: begin
            if (fsm_input == "b") begin
                fsm_next_state = FSM_S2;
            end
            else begin
                fsm_next_state = FSM_S0;
            end
        end
        FSM_S2: begin
            if (fsm_input == "c") begin
                fsm_next_state = FSM_S3;
            end
            else begin
                fsm_next_state = FSM_S0;
            end
        end
        FSM_S3: begin
            if (fsm_input == "a") begin
                fsm_next_state = FSM_S1;
            end
            else begin
                fsm_next_state = FSM_S0;
            end
        end
        default: fsm_next_state = FSM_S0;
    endcase
end

//状态机的第三段描述状态输出（这里采用时序电路输出）
always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n) begin
        fsm_output <= 1'b0;
    end
    else begin
        //根据【当前状态 && 当前输入】,来决定当前输出
        if ((fsm_curr_state == FSM_S2) && (fsm_input == "c")) begin
//        if (fsm_curr_state == FSM_S3) begin
            fsm_output <= 1'b1;
        end
        else begin
            fsm_output <= 1'b0;
        end
    end
end

//仿真激励代码
always #10 sys_clk = ~sys_clk;

initial begin
    sys_clk     = 1'b1;
    sys_rst_n   = 1'b0;
    #200
    sys_rst_n   = 1'b1;

    #20 fsm_input="H";
    #20 fsm_input="i";
    #20 fsm_input="H";
    #20 fsm_input="e";
    #20 fsm_input="l";
    #20 fsm_input="l";
    #20 fsm_input="o";
    #20 fsm_input="h";
    #20 fsm_input="a";
    #20 fsm_input="b";
    #20 fsm_input="c";
    #20 fsm_input="h";
    //fsm_input="niHellohabch"
end

endmodule

```

在状态机的第三段中，`if ((fsm_curr_state == FSM_S2) && (fsm_input == "c")) begin`，即根据【当前状态 && 当前输入】来决定当前输出，输出会刚好在满足实际匹配需求，所以我们是否需要让输出晚一个时钟周期，需要根据实际要解决的问题特性来。
![[Pasted image 20251225171329.png]]


在状态机的第三段中，改写成 `if (fsm_curr_state == FSM_S3) begin` ，即只根据当前状态来决定当前输出，输出会晚一个时钟周期：

![[Pasted image 20251225171351.png]]




## ZYNQPL-同步FIFO基础实验

1、通过vivado新建该开发板的空工程（小系统板：xc7z010clg400-1）。

2、同步FIFO：指读时钟和写时钟为同一个时钟，在时钟沿来临时同时发生读写操作；异步FIFO：指读写时钟不一致，读写时钟是相互独立的。另外，FIFO使用的资源有两种，一种是DRAM(Distribute)，另一种是BRAM(Block)，BRAM支持读写位宽不相同，而DRAM不支持，一般常用BRAM资源类型的FIFO。合理利用almost_full/almost_empty可以有效预防数据丢失。

3、从简答到复杂的顺序来理解下面的写时序。首先下图时序中，wr_clk 是最好理解的，它就是给FIFO写提供基准时钟，后续的其他时序都是基于该时钟时序而进行工作的。其次是 wr_en 写使能信号，该信号在一开始就有拉高的动作，即上升沿的动作，然后后续一直保持高电平的电平状态，简单结合其他信号的动作，可以大致判断出来，该写使能信号是高有效，即要在高电平的时候对FIFO的写操作才能有效写进去。紧接着就是 din 信号，这个是数据信号，即我们要往FIFO写进去的数据。这个信号也是在 wr_en 拉高之后，才能生效，也就是我们在实际操作过程中，必须判断 wr_en 为高时，才往这个信号填入数据，这样才能被FIFO接收。另外 full/almost_full 结合起来看，其中 almost_full 相比提前了一个时钟周期被拉高，说明其所处的D3位置，D3是进入FIFO的最后一个数据，再往里塞就塞不下了。而full被拉高时，此时的FIFO已经是满的状态了，所以一般情况下，大家更倾向于使用almost_full这样的信号来进行满状态预判断，从而预防数据丢失。

![[Pasted image 20251225171434.png]]

下面是FIFO读时序，同样，rd_clk 为整个时序图提供基准时钟。从时序图中看出，当 rd_en 被拉高后，dout并没有马上有数据，而是在 rd_en 被拉高后再过一个时钟周期，dout才有数据，而且valid信号也是在此时才被拉高的，这一点是值得注意的。

![[Pasted image 20251225171450.png]]


4、根据对上面的标准FIFO读写时序的仔细分析，至少可以确定上述哪些信号是我们需要重点关注的，比如上面标准FIFO写时序中，wr_clk,wr_en,din,full,almost_full,wr_ack是我们需要关注的，其中wr_ack是我重点关注的, 因为通过它我才能知道我写入的数据是否已经写入了，我才好决定师傅继续写入下一个数据。同理，在标准FIFO读时序中，valid信号是我着重关注的，因为我需要通过它来判定我当前是否可以读数据。由此，我便明确了我需要一个带哪些信号的IP核，配置如下(相应的IP核为 `FIFO Generator` )：

![[Pasted image 20251225171506.png]]


5、然后根据标准FIFO时序来实现第一版代码，代码直接写到TestBench里，完整代码和其仿真时序图如下所示：

```verilog
`timescale 1ns / 1ps
module fifo_tb();

reg             sys_clk;
reg             sys_rst_n;

wire            wr_clk;
wire            wr_full;
reg             wr_en;
reg   [7 : 0]   wr_data;
wire            wr_ack;

wire            rd_clk;
wire            rd_empty;
reg             rd_en;
wire            rd_valid;
wire  [7 : 0]   rd_data;

assign          wr_clk = sys_clk;
assign          rd_clk = sys_clk;

//标准FIFO写时序
always@( posedge sys_clk or negedge sys_rst_n ) begin
    if (!sys_rst_n) begin
        wr_en       <= 1'b0;
        wr_data     <= 1'b0;
    end
    else begin
        if (wr_full) begin
            wr_en       <= 1'b0;
            wr_data     <= 1'b0;
        end
        else begin
            wr_en       <= 1'b1;
            wr_data     <= wr_data + 1'b1;
        end
    end
end

//标准FIFO读时序
always@( posedge sys_clk or negedge sys_rst_n ) begin
    if (!sys_rst_n) begin
        rd_en       <= 1'b0;
    end
    else begin
        if (!rd_empty) begin
            rd_en       <= 1'b1;
            if (rd_valid) begin
                //see rd_data on the simulation
            end
        end
    end
end

fifo_generator_0 u_fifo_generator_0 (
  .wr_clk   (wr_clk     ),  // input wire wr_clk
  .rd_clk   (rd_clk     ),  // input wire rd_clk
  .din      (wr_data    ),  // input wire [7 : 0] din
  .wr_en    (wr_en      ),  // input wire wr_en
  .rd_en    (rd_en      ),  // input wire rd_en
  .dout     (rd_data    ),  // output wire [7 : 0] dout
  .full     (wr_full    ),  // output wire full
  .wr_ack   (wr_ack     ),  // output wire wr_ack
  .empty    (rd_empty   ),  // output wire empty
  .valid    (rd_valid   )   // output wire valid
);

//仿真激励代码
always #10 sys_clk = ~sys_clk;

initial begin
    sys_clk     = 1'b0;
    sys_rst_n   = 1'b0;
    #200
    sys_rst_n   = 1'b1;
end

endmodule

```

![[Pasted image 20251225171522.png]]



## ZYNQPL-单口RAM基础实验

1、通过vivado新建该开发板的空工程（xc7z010clg400-1）。

2、查找IP核（Block Memory Generator），并配置如下：
![[Pasted image 20251225171538.png]]

![[Pasted image 20251225171546.png]]


3、参考开发板实验手册代码，把例化代码写到TestBench里。

```verilog
`timescale 1ns / 1ps
module ram_tb();

reg         sys_clk;
reg         sys_rst_n;

wire        ram_en;
wire        ram_wea;
reg  [4:0]  ram_addr;
reg  [7:0]  ram_wr_data;
wire [7:0]  ram_rd_data;

reg [5:0]   rw_cnt;
assign      ram_en = sys_rst_n;
assign      ram_wea = ((rw_cnt <= 6'd31) && (ram_en == 1'b1))?   1'b1:1'b0;

//读写控制计数器,计数器范围 0~63
always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n)
        rw_cnt <= 1'b0;
    else if (rw_cnt == 6'd63)
        rw_cnt <= 1'b0;
    else
        rw_cnt <= rw_cnt + 1'b1;
end

always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n)
        ram_wr_data <= 1'b0;
    else if (rw_cnt < 6'd31)
        //在计数器的 0-31 范围内，RAM 写地址累加
        ram_wr_data <= ram_wr_data + 1'b1;
    else
        ram_wr_data <= 1'b0;
end

//读写地址信号 范围：0~31
always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n)
        ram_addr <= 1'b0;
    else if (ram_addr == 5'd31)
        ram_addr <= 1'b0;
    else
        ram_addr <= ram_addr + 1'b1;
end

blk_mem_gen_0 u_blk_mem_gen_0 (
  .clka     (sys_clk        ),  // input wire clka
  .ena      (ram_en         ),  // input wire ena
  .wea      (ram_wea        ),  // input wire [0 : 0] wea
  .addra    (ram_addr       ),  // input wire [4 : 0] addra
  .dina     (ram_wr_data    ),  // input wire [7 : 0] dina
  .douta    (ram_rd_data    )   // output wire [7 : 0] douta
);

//仿真激励代码
always #10 sys_clk = ~sys_clk;

initial begin
    sys_clk     = 1'b0;
    sys_rst_n   = 1'b0;
    #200
    sys_rst_n   = 1'b1;
end

endmodule

```


![[Pasted image 20251225171602.png]]

![[Pasted image 20251225171609.png]]



## ZYNQPL-双口RAM基础实验

1、通过vivado新建该开发板的空工程（xc7z010clg400-1）。

2、查找IP核（Block Memory Generator），并配置如下：

![[Pasted image 20251225171621.png]]


![[Pasted image 20251225171630.png]]



3、RAM 的数据写入和读出都是按时钟的上升沿操作的，端口 A 数据写入的时候需要置高 wea 信号，同时提供地址和要写入的数据。下图为输入写入到 RAM 的时序图。

![[Pasted image 20251225171645.png]]


而端口 B 是不能写入数据的，只能从 RAM 中读出数据，只要提供地址就可以了，一般情况下可以在下一个周期采集到有效的数据。
![[Pasted image 20251225171657.png]]


4、下面进行 RAM 的测试程序的编写，由于测试 RAM 的功能，我们向 RAM 的端口 A 写入一串连续的数据，只写一次，并从端口 B 中读出，使用逻辑分析仪查看数据【ILA(Integrated Logic Analyzer)】。代码如下：
![[Pasted image 20251225171717.png]]



5、根据实验手册编写内存读写访问的TestBench代码如下：

```verilog
`timescale 1ns / 1ps
module ram2_tb();

reg             sys_clk;
reg             sys_rst_n;

reg             ram_wea;
reg  [4:0]      ram_wr_addr;
reg  [4:0]      ram_rd_addr;
reg  [15:0]     ram_wr_data;
wire [15:0]     ram_rd_data;

//产生RAM PORTB读地址
always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n) begin
        ram_rd_addr <= 1'b0;
    end
    //w_addr位或，不等于0
    else if (|ram_rd_addr)
        ram_rd_addr <= ram_rd_addr + 1'b1;
    else
        ram_rd_addr <= 1'b0;
end

//产生RAM PORTA写使能信号
always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n) begin
        ram_wea <= 1'b0;
    end
    else begin
        //w_addr的bit位全为1，共写入32个数据，写入完成
        if (&ram_wr_addr)
            ram_wea <= 1'b0;
        else
            ram_wea <= 1'b1;
    end
end

//产生RAM PORTA写入的地址及数据
always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n) begin
        ram_wr_addr <= 5'd0;
        ram_wr_data <= 16'd0;
    end
    else begin
        if (ram_wea) begin
            //w_addr的bit位全为1，共写入32个数据，写入完成
            if (&ram_wr_addr) begin
                //将地址和数据的值保持住，只写一次RAM
                ;
            end
            else begin
                ram_wr_addr <= ram_wr_addr + 1'b1;
                ram_wr_data <= ram_wr_data + 1'b1;
            end
        end
    end
end

blk_mem_gen_0 u_blk_mem_gen_0 (
  .clka     (sys_clk        ),  // input wire clka
  .wea      (ram_wea        ),  // input wire [0 : 0] wea
  .addra    (ram_wr_addr    ),  // input wire [4 : 0] addra
  .dina     (ram_wr_data    ),  // input wire [15 : 0] dina
  .clkb     (sys_clk        ),  // input wire clkb
  .addrb    (ram_rd_addr    ),  // input wire [4 : 0] addrb
  .doutb    (ram_rd_data    )   // output wire [15 : 0] doutb
);

ila_0 u_ila_0 (
	.clk       (sys_clk        ), // input wire clk
	.probe0    (ram_rd_addr    ), // input wire [0:0]  probe0
	.probe1    (ram_rd_data    )  // input wire [0:0]  probe1
);

//仿真激励代码
always #10 sys_clk = ~sys_clk;

initial begin
    sys_clk     = 1'b0;
    sys_rst_n   = 1'b0;
    #200
    sys_rst_n   = 1'b1;
end

endmodule

```

6、仿真效果如下图：
![[Pasted image 20251225171735.png]]




## ZYNQPL-单口ROM基础实验

1、通过vivado新建该开发板的空工程（xc7z010clg400-1）。

2、新建一个文件(后缀名为.coe)，用来存放ROM初始数据。新建文本文件，最后保存成后缀为.coe的文件即可。

```
memory_initialization_radix=10;
memory_initialization_vector=00,01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31;

```

3、查找IP核（Block Memory Generator），并配置如下：
![[Pasted image 20251225171751.png]]


![[Pasted image 20251225171759.png]]


4、添加ILA的IP核，注意位宽配置：
![[Pasted image 20251225171814.png]]


5、抄写开发板实验手册的代码，编写纯仿真激励代码：

```verilog
`timescale 1ns / 1ps
module rom_tb();

parameter ADDR_WIDTH = 4'd5;
parameter DATA_WIDTH = 4'd8;

reg             sys_clk;
reg             sys_rst_n;

reg     [ADDR_WIDTH-1:0]   rom_addr;
wire    [DATA_WIDTH-1:0]   rom_data;

//产生ROM地址读取数据
always @(posedge sys_clk or negedge sys_rst_n) begin
    if (!sys_rst_n)
        rom_addr <= 1'b0;
    else begin
        if (rom_addr == 5'd31)
            rom_addr <= 1'b0;
        else
            rom_addr <= rom_addr + 1'b1;
    end
end

blk_mem_gen_0 u_blk_mem_gen_0 (
  .clka     (sys_clk    ),  // input wire clka
  .addra    (rom_addr   ),  // input wire [4 : 0] addra
  .douta    (rom_data   )   // output wire [7 : 0] douta
);

ila_0 u_ila_0 (
	.clk       (sys_clk    ), // input wire clk
	.probe0    (rom_addr   ), // input wire [4:0]  probe0
	.probe1    (rom_data   )  // input wire [7:0]  probe1
);

//仿真激励代码
always #10 sys_clk = ~sys_clk;

initial begin
    sys_clk     = 1'b0;
    sys_rst_n   = 1'b0;
    #200
    sys_rst_n   = 1'b1;
end

endmodule

```


![[Pasted image 20251225171833.png]]


6、通过约束文件，以及ILA的配合编译成bit文件下载到开发板运行，调试核抓到的信息如下（同样是慢一个时钟周期）
![[Pasted image 20251225171844.png]]


## ZYNQPL-AXIDMA环通实验

AXIDMA可以参考PG021手册

PG021手册导读: 68_AXI DMA简介（第二讲）.zip 一二三讲




中断例程:

实例对象: 要发送数据的地址，和用于接收数据的地址:

```cpp
#define MEM_BASE_ADDR		0x01000000
#define TX_BUFFER_BASE		(MEM_BASE_ADDR + 0x00100000)
#define RX_BUFFER_BASE		(MEM_BASE_ADDR + 0x00300000)
#define RX_BUFFER_HIGH		(MEM_BASE_ADDR + 0x004FFFFF)

```

实例对象: AXI DMA实例

```cpp
XAxiDma_LookupConfig(DMA_DEV_ID);
XAxiDma_CfgInitialize(&axidmaInst, Config);
if(XAxiDma_HasSg(&axidmaInst)) ;

SetupIntrSystem(&Intc, &axidmaInst, TX_INTR_ID, RX_INTR_ID);

/* Disable all interrupts before setup */
XAxiDma_IntrDisable(&axidmaInst,XAXIDMA_IRQ_ALL_MASK,XAXIDMA_DMA_TO_DEVICE);
XAxiDma_IntrDisable(&axidmaInst,XAXIDMA_IRQ_ALL_MASK,XAXIDMA_DEVICE_TO_DMA);

/* Enable all interrupts */
XAxiDma_IntrEnable(&axidmaInst,XAXIDMA_IRQ_ALL_MASK,XAXIDMA_DMA_TO_DEVICE);
XAxiDma_IntrEnable(&axidmaInst,XAXID

```

实例对象: 中断控制器

```cpp
XScuGic_LookupConfig(INTC_DEVICE_ID);
XScuGic_CfgInitialize(intcInst, IntcConfig,IntcConfig->CpuBaseAddress);

XScuGic_SetPriorityTriggerType(intcInst, TxIntrId, 0xA0, 0x3);
XScuGic_SetPriorityTriggerType(intcInst, RxIntrId, 0xA0, 0x3);

XScuGic_Connect(intcInst, TxIntrId,(Xil_InterruptHandler)TxIntrHandler,axidmaInst);
XScuGic_Connect(intcInst, RxIntrId,(Xil_InterruptHandler)RxIntrHandler,axidmaInst);

XScuGic_Enable(intcInst, TxIntrId);
XScuGic_Enable(intcInst, RxIntrId);

/* Enable interrupts from the hardware */
Xil_ExceptionInit();
Xil_ExceptionRegisterHandler(
		XIL_EXCEPTION_ID_IRQ_INT,
		XScuGic_InterruptHandler,
		intcInst);

Xil_ExceptionEnable();

```

对于中断控制器，当有异常触发时，假设是按键中断，由于按键中断在异常向量表中会进入IRQ这个处理分支，进入IRQ对应的处理函数之后，函数内的代码会直接读取中断控制器相关的寄存器，来获取是哪个中断ID触发的该中断。拿到中断ID之后，然后以这个ID作为数组下标，根据数组下标，找到对应的中断处理函数并执行它，以及中断处理函数所需的参数，比如这个中断是按键产生的，那么这个处理函数的参数应该就是按键相关实例的参数，比如是AXIDMA的中断，那么这个处理函数的参数就是AXIDMA实例。执行完之后，下一步就是直接告知中断控制器，我们已经处理完了。

关于中断这边，我们需要关心的就两个地方，一个是 `XExc_VectorTable[XIL_EXCEPTION_ID_IRQ_INT]`，这个的处理函数直接用官方BSP给我们提供好的handle注册就行，这里所谓的注册，就是赋值；另一个是 `deviceInst->Config->HandlerTable[dev_irq_id]`，这个也是需要用户程序显式注册；以便后续对应的设备发生中断时，最终能够执行到我们具体设备的handle。

![[Pasted image 20251225172143.png]]

![[Pasted image 20251225172150.png]]



```cpp
//axidma_intr.c

#include "xaxidma.h"
#include "xparameters.h"
#include "xil_exception.h"
#include "xdebug.h"
#include "xscugic.h"

#define DMA_DEV_ID		XPAR_AXIDMA_0_DEVICE_ID

#ifndef DDR_BASE_ADDR
#warning CHECK FOR THE VALID DDR ADDRESS IN XPARAMETERS.H, DEFAULT SET TO 0x01000000
#define MEM_BASE_ADDR		0x01000000
#else
#define MEM_BASE_ADDR		(DDR_BASE_ADDR + 0x1000000)
#endif

#define RX_INTR_ID		XPAR_FABRIC_AXIDMA_0_S2MM_INTROUT_VEC_ID
#define TX_INTR_ID		XPAR_FABRIC_AXIDMA_0_MM2S_INTROUT_VEC_ID

#define TX_BUFFER_BASE		(MEM_BASE_ADDR + 0x00100000)
#define RX_BUFFER_BASE		(MEM_BASE_ADDR + 0x00300000)
#define RX_BUFFER_HIGH		(MEM_BASE_ADDR + 0x004FFFFF)

#define INTC_DEVICE_ID          XPAR_SCUGIC_SINGLE_DEVICE_ID

#define INTC         XScuGic
#define INTC_HANDLER XScuGic_InterruptHandler

#define RESET_TIMEOUT_COUNTER	10000

#define TEST_START_VALUE	0xC
#define MAX_PKT_LEN		0x100
#define NUMBER_OF_TRANSFERS	10

static int CheckData(int Length, u8 StartValue);
static void TxIntrHandler(void *Callback);
static void RxIntrHandler(void *Callback);

static int SetupIntrSystem(INTC * intcInst,
			   XAxiDma * axidmaInst, u16 TxIntrId, u16 RxIntrId);
static void DisableIntrSystem(INTC * intcInst,
					u16 TxIntrId, u16 RxIntrId);

static XAxiDma axidmaInst;
static INTC Intc;
volatile int TxDone;
volatile int RxDone;
volatile int Error;

int main(void)
{
	int Status;
	XAxiDma_Config *Config;
	int Tries = NUMBER_OF_TRANSFERS;
	int Index;
	u8 *TxBufferPtr;
	u8 *RxBufferPtr;
	u8 Value;

	TxBufferPtr = (u8 *)TX_BUFFER_BASE ;
	RxBufferPtr = (u8 *)RX_BUFFER_BASE;

	Config = XAxiDma_LookupConfig(DMA_DEV_ID);
	Status = XAxiDma_CfgInitialize(&axidmaInst, Config);
	Status = SetupIntrSystem(&Intc, &axidmaInst, TX_INTR_ID, RX_INTR_ID);

	/* Disable all interrupts before setup */
	XAxiDma_IntrDisable(&axidmaInst,XAXIDMA_IRQ_ALL_MASK,XAXIDMA_DMA_TO_DEVICE);
	XAxiDma_IntrDisable(&axidmaInst,XAXIDMA_IRQ_ALL_MASK,XAXIDMA_DEVICE_TO_DMA);

	/* Enable all interrupts */
	XAxiDma_IntrEnable(&axidmaInst,XAXIDMA_IRQ_ALL_MASK,XAXIDMA_DMA_TO_DEVICE);
	XAxiDma_IntrEnable(&axidmaInst,XAXIDMA_IRQ_ALL_MASK,XAXIDMA_DEVICE_TO_DMA);

	/* Initialize flags before start transfer test  */
	TxDone = 0;
	RxDone = 0;
	Error = 0;

	Value = TEST_START_VALUE;
	for(Index = 0; Index < MAX_PKT_LEN; Index ++) {
			TxBufferPtr[Index] = Value;
			Value = (Value + 1) & 0xFF;
	}

	/* Flush the SrcBuffer before the DMA transfer, in case the Data Cache is enabled */
	Xil_DCacheFlushRange((UINTPTR)TxBufferPtr, MAX_PKT_LEN);
#ifdef __aarch64__
	Xil_DCacheFlushRange((UINTPTR)RxBufferPtr, MAX_PKT_LEN);
#endif

	/* Send a packet */
	for(Index = 0; Index < Tries; Index ++) {
		Status = XAxiDma_SimpleTransfer(&axidmaInst,(UINTPTR) RxBufferPtr,
					MAX_PKT_LEN, XAXIDMA_DEVICE_TO_DMA);
		Status = XAxiDma_SimpleTransfer(&axidmaInst,(UINTPTR) TxBufferPtr,
					MAX_PKT_LEN, XAXIDMA_DMA_TO_DEVICE);

		//Wait TX done and RX done
		while (!TxDone && !RxDone && !Error) {
				/* NOP */
		}

		if (Error) {
			goto Done;
		}

		Status = CheckData(MAX_PKT_LEN, 0xC);
	}

	xil_printf("Successfully ran AXI DMA interrupt Example\\\\r\\\\n");

	/* Disable TX and RX Ring interrupts and return success */
	DisableIntrSystem(&Intc, TX_INTR_ID, RX_INTR_ID);

Done:
	xil_printf("--- Exiting main() --- \\\\r\\\\n");
	return XST_SUCCESS;
}

static int CheckData(int Length, u8 StartValue)
{
	u8 *RxPacket;
	int Index = 0;
	u8 Value;

	RxPacket = (u8 *) RX_BUFFER_BASE;
	Value = StartValue;

	/* Invalidate the DestBuffer before receiving the data, in case the
	 * Data Cache is enabled
	 */
#ifndef __aarch64__
	Xil_DCacheInvalidateRange((UINTPTR)RxPacket, Length);
#endif

	for(Index = 0; Index < Length; Index++) {
		if (RxPacket[Index] != Value) {
			xil_printf("Data error %d: %x/%x\\\\r\\\\n",
			    Index, RxPacket[Index], Value);

			return XST_FAILURE;
		}
		Value = (Value + 1) & 0xFF;
	}

	return XST_SUCCESS;
}

static void TxIntrHandler(void *Callback)
{

	u32 IrqStatus;
	int TimeOut;
	XAxiDma *axidmaInst = (XAxiDma *)Callback;

	/* Read pending interrupts */
	IrqStatus = XAxiDma_IntrGetIrq(axidmaInst, XAXIDMA_DMA_TO_DEVICE);

	/* Acknowledge pending interrupts */
	XAxiDma_IntrAckIrq(axidmaInst, IrqStatus, XAXIDMA_DMA_TO_DEVICE);

	/* If no interrupt is asserted, we do not do anything */
	if (!(IrqStatus & XAXIDMA_IRQ_ALL_MASK)) {
		return;
	}

	if ((IrqStatus & XAXIDMA_IRQ_ERROR_MASK)) {
		Error = 1;
		XAxiDma_Reset(axidmaInst);
		TimeOut = RESET_TIMEOUT_COUNTER;
		while (TimeOut) {
			if (XAxiDma_ResetIsDone(axidmaInst)) {
				break;
			}
			TimeOut -= 1;
		}
		return;
	}

	/*
	 * If Completion interrupt is asserted, then set the TxDone flag
	 */
	if ((IrqStatus & XAXIDMA_IRQ_IOC_MASK)) {
		TxDone = 1;
	}
}

static void RxIntrHandler(void *Callback)
{
	u32 IrqStatus;
	int TimeOut;
	XAxiDma *AxiDmaInst = (XAxiDma *)Callback;

	/* Read pending interrupts */
	IrqStatus = XAxiDma_IntrGetIrq(AxiDmaInst, XAXIDMA_DEVICE_TO_DMA);

	/* Acknowledge pending interrupts */
	XAxiDma_IntrAckIrq(AxiDmaInst, IrqStatus, XAXIDMA_DEVICE_TO_DMA);

	if (!(IrqStatus & XAXIDMA_IRQ_ALL_MASK)) {
		return;
	}

	if ((IrqStatus & XAXIDMA_IRQ_ERROR_MASK)) {
		Error = 1;
		XAxiDma_Reset(AxiDmaInst);
		TimeOut = RESET_TIMEOUT_COUNTER;
		while (TimeOut) {
			if(XAxiDma_ResetIsDone(AxiDmaInst)) {
				break;
			}
			TimeOut -= 1;
		}
		return;
	}

	/*
	 * If completion interrupt is asserted, then set RxDone flag
	 */
	if ((IrqStatus & XAXIDMA_IRQ_IOC_MASK)) {
		RxDone = 1;
	}
}

static int SetupIntrSystem(INTC * intcInst,
			   XAxiDma * axidmaInst, u16 TxIntrId, u16 RxIntrId)
{
	int Status;
	XScuGic_Config *IntcConfig;
	IntcConfig = XScuGic_LookupConfig(INTC_DEVICE_ID);
	Status = XScuGic_CfgInitialize(intcInst, IntcConfig,IntcConfig->CpuBaseAddress);
	XScuGic_SetPriorityTriggerType(intcInst, TxIntrId, 0xA0, 0x3);
	XScuGic_SetPriorityTriggerType(intcInst, RxIntrId, 0xA0, 0x3);
	XScuGic_Connect(intcInst, TxIntrId,(Xil_InterruptHandler)TxIntrHandler,axidmaInst);
	XScuGic_Connect(intcInst, RxIntrId,(Xil_InterruptHandler)RxIntrHandler,axidmaInst);

	XScuGic_Enable(intcInst, TxIntrId);
	XScuGic_Enable(intcInst, RxIntrId);

	/* Enable interrupts from the hardware */
	Xil_ExceptionInit();
	Xil_ExceptionRegisterHandler(
			XIL_EXCEPTION_ID_IRQ_INT,
			XScuGic_InterruptHandler,intcInst);
	Xil_ExceptionEnable();

	return XST_SUCCESS;
}

static void DisableIntrSystem(INTC * intcInst,
					u16 TxIntrId, u16 RxIntrId)
{
	XScuGic_Disconnect(intcInst, TxIntrId);
	XScuGic_Disconnect(intcInst, RxIntrId);
}

```

```cpp
//axidma_poll.c

#include "xaxidma.h"
#include "xparameters.h"
#include "xdebug.h"
#define DMA_DEV_ID		XPAR_AXIDMA_0_DEVICE_ID

#ifndef DDR_BASE_ADDR
#warning CHECK FOR THE VALID DDR ADDRESS IN XPARAMETERS.H, \\\\
		 DEFAULT SET TO 0x01000000
#define MEM_BASE_ADDR		0x01000000
#else
#define MEM_BASE_ADDR		(DDR_BASE_ADDR + 0x1000000)
#endif

#define TX_BUFFER_BASE		(MEM_BASE_ADDR + 0x00100000)
#define RX_BUFFER_BASE		(MEM_BASE_ADDR + 0x00300000)
#define RX_BUFFER_HIGH		(MEM_BASE_ADDR + 0x004FFFFF)

#define MAX_PKT_LEN		0x20
#define TEST_START_VALUE	0xC
#define NUMBER_OF_TRANSFERS	10

#if (!defined(DEBUG))
extern void xil_printf(const char *format, ...);
#endif

int XAxiDma_SimplePollExample(u16 DeviceId);
static int CheckData(void);
XAxiDma AxiDma;

int main()
{
	int Status;

	xil_printf("\\\\r\\\\n--- Entering main() --- \\\\r\\\\n");

	/* Run the poll example for simple transfer */
	Status = XAxiDma_SimplePollExample(DMA_DEV_ID);

	if (Status != XST_SUCCESS) {
		xil_printf("XAxiDma_SimplePoll Example Failed\\\\r\\\\n");
		return XST_FAILURE;
	}

	xil_printf("Successfully ran XAxiDma_SimplePoll Example\\\\r\\\\n");

	xil_printf("--- Exiting main() --- \\\\r\\\\n");

	return XST_SUCCESS;

}

int XAxiDma_SimplePollExample(u16 DeviceId)
{
	XAxiDma_Config *CfgPtr;
	int Status;
	int Tries = NUMBER_OF_TRANSFERS;
	int Index;
	u8 *TxBufferPtr;
	u8 *RxBufferPtr;
	u8 Value;

	TxBufferPtr = (u8 *)TX_BUFFER_BASE ;
	RxBufferPtr = (u8 *)RX_BUFFER_BASE;

	/* Initialize the XAxiDma device.
	 */
	CfgPtr = XAxiDma_LookupConfig(DeviceId);
	Status = XAxiDma_CfgInitialize(&AxiDma, CfgPtr);
	XAxiDma_HasSg(&AxiDma);

	XAxiDma_IntrDisable(&AxiDma, XAXIDMA_IRQ_ALL_MASK,XAXIDMA_DEVICE_TO_DMA);
	XAxiDma_IntrDisable(&AxiDma, XAXIDMA_IRQ_ALL_MASK,XAXIDMA_DMA_TO_DEVICE);

	Value = TEST_START_VALUE;
	for(Index = 0; Index < MAX_PKT_LEN; Index ++) {
			TxBufferPtr[Index] = Value;
			Value = (Value + 1) & 0xFF;
	}

	Xil_DCacheFlushRange((UINTPTR)TxBufferPtr, MAX_PKT_LEN);
#ifdef __aarch64__
	Xil_DCacheFlushRange((UINTPTR)RxBufferPtr, MAX_PKT_LEN);
#endif

	for(Index = 0; Index < Tries; Index ++) {
		Status = XAxiDma_SimpleTransfer(&AxiDma,(UINTPTR) RxBufferPtr,
					MAX_PKT_LEN, XAXIDMA_DEVICE_TO_DMA);
		Status = XAxiDma_SimpleTransfer(&AxiDma,(UINTPTR) TxBufferPtr,
					MAX_PKT_LEN, XAXIDMA_DMA_TO_DEVICE);

		while ((XAxiDma_Busy(&AxiDma,XAXIDMA_DEVICE_TO_DMA)) ||
			(XAxiDma_Busy(&AxiDma,XAXIDMA_DMA_TO_DEVICE))) {
				/* Wait */
		}

		Status = CheckData();
		if (Status != XST_SUCCESS) {
			return XST_FAILURE;
		}

	}

	return XST_SUCCESS;
}

static int CheckData(void)
{
	u8 *RxPacket;
	int Index = 0;
	u8 Value;

	RxPacket = (u8 *) RX_BUFFER_BASE;
	Value = TEST_START_VALUE;

#ifndef __aarch64__
	Xil_DCacheInvalidateRange((UINTPTR)RxPacket, MAX_PKT_LEN);
#endif

	for(Index = 0; Index < MAX_PKT_LEN; Index++) {
		if (RxPacket[Index] != Value) {
			xil_printf("Data error %d: %x/%x\\\\r\\\\n",
			Index, (unsigned int)RxPacket[Index],
				(unsigned int)Value);

			return XST_FAILURE;
		}
		Value = (Value + 1) & 0xFF;
	}

	return XST_SUCCESS;
}

```




## ZYNQPS-AMP双核启动

基于黑金AX7020开发板，做AMP启动实验

![[Pasted image 20251225172236.png]]


内存布局地址设置参考（只要不重叠即可）：
（1）CPU0的lscript.ld设置：`ps7_ddr_0 : ORIGIN = 0x100000, LENGTH = 0x8EFFFFF` 
（2）CPU1的lscript.ld设置：`ps7_ddr_0 : ORIGIN = 0x9000000, LENGTH = 0x7000000`


## ZYNQPS-AMP双核软中断

---

下面是基于AX7020 ARM CPU双核之间软中断模块代码：

software_intr.h

```cpp
#ifndef SRC_SHARED_MEM_SOFTWARE_INTR_H_
#define SRC_SHARED_MEM_SOFTWARE_INTR_H_

#include "xil_cache.h"
#include <stdio.h>
#include "xil_types.h"
#include "Xscugic.h"
#include "Xil_exception.h"
#include "xil_printf.h"
#include "xparameters.h"

// Only 1 SCUGIC For Earch ZYNQ Board (Physical CPU)
#define INTC_DEVICE_ID XPAR_SCUGIC_SINGLE_DEVICE_ID

// interrupt direction between CPU0 and CPU1
#define CPU0_TO_CPU1_INTR_ID 0x01
#define CPU1_TO_CPU0_INTR_ID 0x02
#define INTR_TO_CPU0 XSCUGIC_SPI_CPU0_MASK
#define INTR_TO_CPU1 XSCUGIC_SPI_CPU1_MASK

// One ZYNQ Board (BGA) only One GIC Instance (xparameters.h --> GIC keyword)
// CPU0 and CPU1 share the same interrupt controller instance
// XScuGic SharedScuGicInstance;

/**
 * @brief Initialize the intercore communication interrupt system
 *
 * @param GicInstancePtr You can use global static instance for each core demo
 * @param cpu0_handler CPU0 handler, if NULL, will set default CoreComm_Cpu0_Intr_Handler
 * @param cpu0_arg CPU0 handler arguments
 * @param cpu1_handler CPU1 handler, if NULL, will set default CoreComm_Cpu1_Intr_Handler
 * @param cpu1_arg CPU1 handler arguments
 * @return 0 on success, -1 on failed
 */
int amp_swintr_init(XScuGic *GicInstancePtr,
					void (*cpu0_handler)(void *), void *cpu0_arg,
					void (*cpu1_handler)(void *), void *cpu1_arg);

/**
 * @brief Send software interrupt signal to target CPU
 *
 * @param GicInstancePtr You can use global static instance for each core demo
 * @param SoftwareIntrId Reference such as CPU0_TO_CPU1_INTR_ID,
 * 		indicates that current is CPU0, and target is CPU1
 * @param CpuMask Reference such as INTR_TO_CPU0, indicates target is CPU0
 * @return 0 on success, -1 on failed
 */
int amp_swintr_send(XScuGic *GicInstancePtr, u16 SoftwareIntrId, u32 CpuMask);

#endif // SRC_SHARED_MEM_SOFTWARE_INTR_H_

```

software_intr.c

```cpp
#include "software_intr.h"

/////////////////////////////////////////////////////////////////////////////
// Following is GIC interrupt code
/////////////////////////////////////////////////////////////////////////////

static void Setup_Intr_Exception(XScuGic *IntcInstancePtr)
{
	/* Enable interrupts from the hardware */
	Xil_ExceptionInit();
	Xil_ExceptionRegisterHandler(XIL_EXCEPTION_ID_INT,
								 (Xil_ExceptionHandler)XScuGic_InterruptHandler,
								 (void *)IntcInstancePtr);

	Xil_ExceptionEnable();
}

static int Init_Intr_System(XScuGic *IntcInstancePtr)
{
	int Status;

	XScuGic_Config *IntcConfig;
	/*
	 * Initialize the interrupt controller driver so that it is ready to
	 * use.
	 */
	IntcConfig = XScuGic_LookupConfig(INTC_DEVICE_ID);
	if (NULL == IntcConfig)
	{
		return XST_FAILURE;
	}

	Status = XScuGic_CfgInitialize(IntcInstancePtr, IntcConfig,
								   IntcConfig->CpuBaseAddress);
	if (Status != XST_SUCCESS)
	{
		return XST_FAILURE;
	}
	return XST_SUCCESS;
}

/////////////////////////////////////////////////////////////////////////////
// Following is software interrupt code
/////////////////////////////////////////////////////////////////////////////

static volatile uint8_t sw_intr_from_cpu0 = 0;
static volatile uint8_t sw_intr_from_cpu1 = 0;

// The intercore communication interrupt handler
static void CoreComm_Cpu0_Intr_Handler(void *Callback)
{
	sw_intr_from_cpu1 = 1;
	printf("[CPU%d] sw_intr_from_cpu1 is %d\\\\r\\\\n", XPAR_CPU_ID, sw_intr_from_cpu1);
}

// The intercore communication interrupt handler
static void CoreComm_Cpu1_Intr_Handler(void *Callback)
{
	sw_intr_from_cpu0 = 1;
	printf("[CPU%d] sw_intr_from_cpu0 is %d\\\\r\\\\n", XPAR_CPU_ID, sw_intr_from_cpu0);
}

/**
 * @brief init for software intr between CPU0 and CPU1
 *
 * @param GicInstancePtr You can use global static instance for each core demo
 * @param IntrHanedler Reference such as CoreComm_Cpu0_Intr_Handler
 * @param HandleArg arguments of CoreComm_Cpu0_Intr_Handler or your own handler
 * @param SoftwareIntrId Reference such as CPU0_TO_CPU1_INTR_ID,
 * 		indicates that current is CPU0, and target is CPU1
 * @param CpuId Reference such as XPAR_CPU_ID, indicates target CPU
 */
static void Init_Software_Intr(XScuGic *GicInstancePtr,
							   Xil_InterruptHandler IntrHanedler, void *HandleArg,
							   u16 SoftwareIntrId, u8 CpuId)
{
	int Status;

	XScuGic_SetPriorityTriggerType(GicInstancePtr, SoftwareIntrId, 0xB0, 0x2);

	Status = XScuGic_Connect(GicInstancePtr, SoftwareIntrId,
							 (Xil_InterruptHandler)IntrHanedler, HandleArg);
	if (Status != XST_SUCCESS)
	{
		xil_printf("core%d: interrupt %d set fail! (ret=%d)\\\\r\\\\n",
				   XPAR_CPU_ID, SoftwareIntrId, Status);
		return;
	}

	XScuGic_InterruptMaptoCpu(GicInstancePtr, CpuId, SoftwareIntrId); // map the the Software interrupt to target CPU

	XScuGic_Enable(GicInstancePtr, SoftwareIntrId); // enable the interrupt for the Software interrupt at GIC
}

/**
 * @brief Send software intr signal to target cpu core (CPU0,CPU1,...)
 *
 * @param GicInstancePtr You can use global static instance for each core demo
 * @param SoftwareIntrId Reference such as CPU0_TO_CPU1_INTR_ID,
 * 		indicates that current is CPU0, and target is CPU1
 * @param CpuMask Reference such as INTR_TO_CPU0, indicates target is CPU0
 */
static int Gen_Software_Intr(XScuGic *GicInstancePtr, u16 SoftwareIntrId, u32 CpuMask)
{
	int Status;

	Status = XScuGic_SoftwareIntr(GicInstancePtr, SoftwareIntrId, CpuMask);
	if (Status != XST_SUCCESS)
	{
		xil_printf("CPU%d: interrupt %d gen failed! (ret=%d)\\\\r\\\\n",
				   XPAR_CPU_ID, SoftwareIntrId, Status);
		return Status;
	}
	return 0;
}

int amp_swintr_init(XScuGic *GicInstancePtr,
					void (*cpu0_handler)(void *), void *cpu0_arg,
					void (*cpu1_handler)(void *), void *cpu1_arg)
{
	int Status;

	Status = Init_Intr_System(GicInstancePtr); // initial interrupt system
	if (Status != XST_SUCCESS)
	{
		xil_printf("CPU%d: Init_Intr_System() failed! (ret=%d)\\\\r\\\\n",
				   XPAR_CPU_ID, Status);
		return Status;
	}

	/*initial software interrupt of local cpu*/
	if (XPAR_CPU_ID == 0)
	{
		Init_Software_Intr(GicInstancePtr,
						   cpu0_handler ? cpu0_handler : CoreComm_Cpu0_Intr_Handler, cpu0_arg,
						   CPU1_TO_CPU0_INTR_ID, XPAR_CPU_ID);
	}
	else
	{
		Init_Software_Intr(GicInstancePtr,
						   cpu1_handler ? cpu1_handler : CoreComm_Cpu1_Intr_Handler, cpu1_arg,
						   CPU0_TO_CPU1_INTR_ID, XPAR_CPU_ID);
	}
	Setup_Intr_Exception(GicInstancePtr);
}

int amp_swintr_send(XScuGic *GicInstancePtr, u16 SoftwareIntrId, u32 CpuMask)
{
	return Gen_Software_Intr(GicInstancePtr, SoftwareIntrId, CpuMask);
}

#if 0 //CPU0 demo
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"
#include "sleep.h"
#include "software_intr/software_intr.h"

static XScuGic SharedScuGicInstance;

int main()
{
    init_platform();

    int count = 0;
    amp_swintr_init(&SharedScuGicInstance, NULL, NULL, NULL, NULL);
    while (1)
    {
        printf("[CPU%d] [%d]Hello World\\\\n\\\\r", XPAR_CPU_ID, ++count);
        if ((count % 5) == 0)
        {
        	amp_swintr_send(&SharedScuGicInstance,
        			CPU0_TO_CPU1_INTR_ID, INTR_TO_CPU1);
        }
        sleep(1);
    }
    cleanup_platform();
    return 0;
}
#endif //CPU0 demo

#if 0 //CPU1 demo
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"
#include "sleep.h"
#include "software_intr/software_intr.h"

static XScuGic SharedScuGicInstance;

int main()
{
    init_platform();

    int count = 0;
    amp_swintr_init(&SharedScuGicInstance, NULL, NULL, NULL, NULL);
    while (1)
    {
        printf("[CPU%d] [%d]Hello World\\\\n\\\\r", XPAR_CPU_ID, ++count);
        if ((count % 7) == 0)
        {
        	amp_swintr_send(&SharedScuGicInstance,
        			CPU1_TO_CPU0_INTR_ID, INTR_TO_CPU0);
        }
        sleep(1);
    }
    cleanup_platform();
    return 0;
}
#endif //CPU1 demo

```

## ZYNQPS-AMP双核共享内存

---

ZYNQ裸机AMP双核共享内存的解决方案

SHARED_BASE_ADDR

（1）初始化：指定双方共享内存地址。 （2）访问内存：双方互斥访问共享内存。

为了避免CPU0和CPU1同时对同一块内存进行读写访问， 可以设置乒乓RAM。定义两块共享内存， mem0和mem1，  同时设置标志；交替写入数据。 当CPU0写mem0时，CPU1只能读取mem1；当CPU0开始写mem1时，如果CPU1正在读mem1，可以设置等待读取完成再进行写入。但这里我们从节省内存上考虑，就为难一下CPU本身了，让CPU互斥访问即可。回顾一下原子操作：在一个CPU上执行过程中，不会被其他CPU打断。ARM Cortex-A9 原子操作实现代码可参考本笔记其他文档（关键字：atomic_cmpxchg ）。

![[Pasted image 20251225172317.png]]


下面的实验代码是基于AX7020 AMP环境做的实验，本实验演示的是CPU0往共享内存里存入数据，完成写入后，CPU0通过软中断通知CPU1，CPU1收到软中断后，读取共享内存内的数据并校验。

shared_mem.h

```cpp
#ifndef _SRC_SHARED_MEM_H_
#define _SRC_SHARED_MEM_H_

#include <stdint.h>

/**
 * @brief alloc a structure for this shared mem management
 *
 * @param base  shared memory region
 * @param size  shared memory size
 * @return void* NULL on error
 */
void *shared_mem_init(uintptr_t base, long size);
void shared_mem_exit(void **pshm);

/**
 * @brief Get data from shared mem
 *
 * @param shm   shared mem ptr, ptr=shared_mem_init(...)
 * @param outbuf store data from shared mem
 * @param size  get size
 * @return 0 on success, 1 on locked, -1 on error
 */
int shared_mem_get(void *shm, void *outbuf, long size);

/**
 * @brief Put data into shared mem
 *
 * @param shm   shared mem ptr, ptr=shared_mem_init(...)
 * @param inbuf data will put
 * @param size  put size
 * @return 0 on success, 1 on locked, -1 on error
 */
int shared_mem_put(void *shm, const void *inbuf, long size);

#endif //_SRC_SHARED_MEM_H_

```

shared_mem.c

```cpp
#include "shared_mem.h"
#include <stdio.h>
#include <stdlib.h>
#include "xil_types.h"
#include "xil_cache.h"
#include "string.h"
#include <xil_io.h> //for dsb()

// whf@arrowpoint.com.cn
typedef struct
{
  int counter;
} atomic_t;

// 1=UNLOCK,0=LOCK
enum
{
  ATOMIC_LOCK = 0,  // 0=LOCK,caller can not access shared region
  ATOMIC_UNLOCK = 1 // 1=UNLOCK,caller can access shared region
};

static inline int atomic_cmpxchg(atomic_t *atom, int old, int new)
{
  unsigned long oldval, res;
  atomic_t *ptr = atom;

  //  smp_mb();
  dsb();

  do
  {
    __asm__ __volatile__("@ atomic_cmpxchg\\\\n"
                         "ldrex %1, [%3]\\\\n"
                         "mov %0, #0\\\\n"
                         "teq %1, %4\\\\n"
                         "strexeq %0, %5, [%3]\\\\n"
                         : "=&r"(res), "=&r"(oldval), "+Qo"(ptr->counter)
                         : "r"(&ptr->counter), "Ir"(old), "r"(new)
                         : "cc");
  } while (res);

  //  smp_mb();
  dsb();

  return oldval;
}

struct shared_mem
{
  unsigned char *base;
  long size;
  atomic_t lock;
};

void *shared_mem_init(uintptr_t base, long size)
{
  struct shared_mem *shmem = malloc(sizeof(struct shared_mem));
  if (shmem)
  {
    shmem->base = (uint8_t *)base;
    shmem->size = size;
    shmem->lock.counter = ATOMIC_UNLOCK;
  }
  return shmem;
}

void shared_mem_exit(void **pshm)
{
  struct shared_mem *shmem;
  if (pshm && (*pshm))
  {
    shmem = (*pshm);
    shmem->base = 0;
    shmem->size = 0;
    shmem->lock.counter = ATOMIC_UNLOCK;
    free(shmem);
    *pshm = NULL;
  }
}

int shared_mem_get(void *shm, void *outbuf, long size)
{
  struct shared_mem *shmem = (struct shared_mem *)shm;

  if (shmem == NULL)
  {
    printf("EEEEEEEEEEEEEEEError:first arg shm is null\\\\r\\\\n");
    return -1;
  }

  if (size > shmem->size)
  {
    printf("EEEEEEEEEEEEEEEError:size is out of range of shmem\\\\r\\\\n");
    printf("EEEEEEEEEEEEEEEError:size = %ld, shmem size = %ld\\\\r\\\\n", size, shmem->size);
    return -1;
  }

  int status = atomic_cmpxchg(&shmem->lock, ATOMIC_UNLOCK, ATOMIC_LOCK);
  if (status == ATOMIC_LOCK)
  {
    printf("now shared_mem_get() is locked, wait for a moment\\\\r\\\\n");
    return 1;
  }

  memcpy(outbuf, shmem->base, size);
  atomic_cmpxchg(&shmem->lock, ATOMIC_LOCK, ATOMIC_UNLOCK);
  return 0;
}

int shared_mem_put(void *shm, const void *inbuf, long size)
{
  struct shared_mem *shmem = (struct shared_mem *)shm;

  if (shmem == NULL)
  {
    printf("EEEEEEEEEEEEEEEError:first arg shm is null\\\\r\\\\n");
    return -1;
  }

  if (size > shmem->size)
  {
    printf("EEEEEEEEEEEEEEEError:size is out of range of shmem\\\\r\\\\n");
    printf("EEEEEEEEEEEEEEEError:size = %ld, shmem size = %ld\\\\r\\\\n", size, shmem->size);
    return -1;
  }

  int status = atomic_cmpxchg(&shmem->lock, ATOMIC_UNLOCK, ATOMIC_LOCK);
  if (status == ATOMIC_LOCK)
  {
    printf("now shared_mem_put() is locked, wait for a moment\\\\r\\\\n");
    return 1;
  }
  memcpy(shmem->base, inbuf, size);
  atomic_cmpxchg(&shmem->lock, ATOMIC_LOCK, ATOMIC_UNLOCK);
  return 0;
}

```

CPU0 demo : put data into shared memory

```cpp
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"
#include "sleep.h"
#include "software_intr/software_intr.h"
#include "shared_mem/shared_mem.h"
static XScuGic SharedScuGicInstance;
//Dual-core shared memory
#define SHARED_MEM_REGION 0x10000000
int main()
{
    init_platform();
    int count = 0;
    amp_swintr_init(&SharedScuGicInstance, NULL, NULL, NULL, NULL);
    //init shared memory
    int i = 0;
    unsigned int buffer[256];
    void *shm = shared_mem_init(SHARED_MEM_REGION, sizeof(int)*256);
    while (1)
    {
        printf("[CPU%d] [%d]Hello World\\\\n\\\\r", XPAR_CPU_ID, ++count);
        if ((count % 5) == 0)
        {
            //fill buffer for temp
            for(i=0; i<256; i++)
            	buffer[i] = 1000 * i + i;
            //put inbuf into shared memory
            shared_mem_put(shm, buffer, sizeof(int)*256);
        	amp_swintr_send(&SharedScuGicInstance,
        			CPU0_TO_CPU1_INTR_ID, INTR_TO_CPU1);
        }
        sleep(1);
    }

    shared_mem_exit(&shm);
    cleanup_platform();
    return 0;
}

```

CPU1 demo : get data from shared memory

```cpp
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"
#include "sleep.h"
#include "software_intr/software_intr.h"
#include "shared_mem/shared_mem.h"

static XScuGic SharedScuGicInstance;

//Dual-core shared memory
#define SHARED_MEM_REGION 0x10000000

void *g_cpu1_shm = NULL;
unsigned int g_compare_buffer[256];

static unsigned int temp_buffer[256];

// The intercore communication interrupt handler
static void intr_from_cpu0(void *Callback)
{
	shared_mem_get(g_cpu1_shm, temp_buffer, sizeof(int)*256);
	if ( 0 == memcmp(g_compare_buffer, temp_buffer,sizeof(int)*256) )
		printf("[CPU%d] Get shared memory data succcess!\\\\r\\\\n", XPAR_CPU_ID);
	else
		printf("[CPU%d] Get shared memory data failed!\\\\r\\\\n", XPAR_CPU_ID);
}

int main()
{
    init_platform();

    int count = 0;
    amp_swintr_init(&SharedScuGicInstance, NULL, NULL, intr_from_cpu0, NULL);

    //init shared memory
    int i = 0;
    g_cpu1_shm = shared_mem_init(SHARED_MEM_REGION, sizeof(int)*256);

    //generate compare data for check
    for(i=0; i<256; i++)
    	g_compare_buffer[i] = 1000 * i + i;

    while (1)
    {
        printf("[CPU%d] [%d]Hello World\\\\n\\\\r", XPAR_CPU_ID, ++count);
        if ((count % 7) == 0)
        	amp_swintr_send(&SharedScuGicInstance,
        			CPU1_TO_CPU0_INTR_ID, INTR_TO_CPU0);
        sleep(1);
    }
    shared_mem_exit(&g_cpu1_shm);
    cleanup_platform();
    return 0;
}

```

实验运行效果（串口打印）：
![[Pasted image 20251225172339.png]]



```cpp
  Xil_DCacheInvalidateRange(shmem->base, size);
  memcpy(outbuf, shmem->base, size);

```

如上代码所示，CPU读取这段内存地址的数据之前，需要先 Cache Invalid 操作，以确保该内存对应的每条 Cache Line 都必须从对应内存地址加载数据，其目的就是为了防止 Cache 特性导致内存某些地址的数据不被加载到 Cache Line ，而把 Cache Line 中老旧数据传给CPU，从而导致CPU最终读取到的数据是错乱的。

```cpp
  memcpy(shmem->base, inbuf, size);
  Xil_DCacheFlushRange(shmem->base, size);

```

如上代码所示，CPU往这段内存地址写入数据后，由于不同架构 Cache 特性，导致 CPU 写入 Cache Line 的数据不一定会马上写入内存，这会导致内存中还是旧数据，所以需要显式Flush冲刷一下这片Cache地址。

## ZYNQPS-XADC健康检测

---

```cpp
#include "xadcps.h"
int xadcps_init(XAdcPs *XADCInstPtr)
{
    int status = 0;
    XAdcPs_Config *ConfigPtr;

    ConfigPtr = XAdcPs_LookupConfig(0);
    if (ConfigPtr == NULL)
    {
        printf("XAdcPs_LookupConfig() failed\\\\r\\\\n");
        return XST_FAILURE;
    }

    status = XAdcPs_CfgInitialize(XADCInstPtr, ConfigPtr, ConfigPtr->BaseAddress);
    if (XST_SUCCESS != status)
    {
        print("ADC INIT FAILED\\\\n\\\\r");
        return XST_FAILURE;
    }

    status = XAdcPs_SelfTest(XADCInstPtr);
    if (status != XST_SUCCESS)
    {
        return XST_FAILURE;
    }

    XAdcPs_SetSequencerMode(XADCInstPtr, XADCPS_SEQ_MODE_SINGCHAN);
    XAdcPs_SetAlarmEnables(XADCInstPtr, 0x0);
    XAdcPs_SetSeqInputMode(XADCInstPtr, XADCPS_SEQ_MODE_SAFE);
    XAdcPs_SetSeqChEnables(XADCInstPtr, XADCPS_CH_TEMP | XADCPS_CH_VCCINT | XADCPS_CH_VCCAUX | XADCPS_CH_VBRAM | XADCPS_CH_VCCPINT | XADCPS_CH_VCCPAUX | XADCPS_CH_VCCPDRO);

    return XST_SUCCESS;
}

int xadcps_capture(XAdcPs *XADCInstPtr)
{
    float Z7_Healthy[16];
    float TempData = XAdcPs_GetAdcData(XADCInstPtr, XADCPS_CH_TEMP);
    float VccIntData = XAdcPs_GetAdcData(XADCInstPtr, XADCPS_CH_VCCINT);
    float VBramData = XAdcPs_GetAdcData(XADCInstPtr, XADCPS_CH_VBRAM);
    float VccAuxData = XAdcPs_GetAdcData(XADCInstPtr, XADCPS_CH_VCCAUX);
    float VccPIntData = XAdcPs_GetAdcData(XADCInstPtr, XADCPS_CH_VCCPINT);
    float VccPAuxData = XAdcPs_GetAdcData(XADCInstPtr, XADCPS_CH_VCCPAUX);
    float VDDRData = XAdcPs_GetAdcData(XADCInstPtr, XADCPS_CH_VCCPDRO);

    Z7_Healthy[0] = XAdcPs_RawToTemperature(TempData);
    Z7_Healthy[1] = XAdcPs_RawToVoltage(VccIntData);
    Z7_Healthy[2] = XAdcPs_RawToVoltage(VccAuxData);
    Z7_Healthy[3] = XAdcPs_RawToVoltage(VBramData);
    Z7_Healthy[4] = XAdcPs_RawToVoltage(VccPIntData);
    Z7_Healthy[5] = XAdcPs_RawToVoltage(VccPAuxData);
    Z7_Healthy[6] = XAdcPs_RawToVoltage(VDDRData);

    printf("TempData-----------------------> %f\\\\r\\\\n", Z7_Healthy[0]);
    printf("VccIntData---------------------> %f\\\\r\\\\n", Z7_Healthy[1]);
    printf("VBramData----------------------> %f\\\\r\\\\n", Z7_Healthy[2]);
    printf("VccAuxData---------------------> %f\\\\r\\\\n", Z7_Healthy[3]);
    printf("VccPIntData--------------------> %f\\\\r\\\\n", Z7_Healthy[4]);
    printf("VccPAuxData--------------------> %f\\\\r\\\\n", Z7_Healthy[5]);
    printf("VDDRData-----------------------> %f\\\\r\\\\n", Z7_Healthy[6]);
    return 0;
}

```

# ZYNQPL-PL读写PS端DDR数据

1、AXI4相对复杂，但SOC开发者必须掌握，对于ZYNQ的开发者，能够在已有代码基础上修改即可。AXI协议的具体内容参考《Xilinx UG761 AXI Reference Guide》。AXI4所采用的是一种 READY、VALID握手通信机制，即主从模块进行数据通信前，先握手。发送者A等到接收者B的 READY 信号后，A将数据与VALID信号同时发送给B，这是一种典型的握手机制。







ZYNQPL-SGDMA实验
ZYNQPSPL-BRAM实现PS与PL数据交互
ZYNQPSPL-PL读写PS的DDR数据
AX7020-PL读写DDR3
AX7020-PS串口读写
ZYNQPL-等精度频率计








# bottom


