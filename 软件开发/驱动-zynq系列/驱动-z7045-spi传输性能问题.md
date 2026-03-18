
附件: 网盘: src-spi-ss-standalone-hello.zip
附件: 网盘: spi-cadence-z7045-fix166.c

z7045 spi0/spi1 控制器在linux系统下传输文件数据，传输很慢的问题。


## 情况收集

项目中的板子，上面有个zynq芯片(z7045)，另外搭载的两个v13p(v13p_0、v13p_1)芯片，但是这两个v13p芯片没有flash进而没有地方存放固件.bin文件，于是它们的固件文件只能存放在 z7045 这边的emmc文件系统里。且z7045这边系统启动后通过spi把对应的文件发送给对应的 v13p 芯片让它运行起来。

就是比如我们这个用来把数据把bin文件通过spi传给主动传给那个V13p，传过去那边就运行，因为v13p那边没有内存，没有flash。这不就是远程升级吗。主控方是zynq，从设备是V13p，因为那边没有flash存放那个bin文件，所以bin文件存放在zynq这边，然后zynq通过spi主动发给v13p。然后用的是SPI SS模式(Slave Serial Configuration)，斌哥说: 这是我们通常的叫法，是针对被加载的对象来说的，这是他的其中一种加载模式。由于实际板子只有一个slave设备(即spi0——v13p_0， spi1——v13p_1)，所以片选参数可以忽略。

斌哥之前是通过设备树把spi0、spi1两个控制器适配起来，并在嵌入式Linux系统中有对应的设备节点(/dev/spidev1.0、/dev/spidev2.0)，经过查看内核代码得知，小数点左边1表示总线编号，右边0表示片选信号。然后斌哥应用程序(spi_transfer1.c 和 spi_transfer2.c) 把对应的.bin文件发送给对应的v13p处理器。

这里遇到一个问题，就是传输速率很慢，110MB的.bin文件大约每11MB要花费22秒，也就是110MB的数据要花费220秒左右才能传输完，但是按照当前的硬件配置，spi传输不应该这么慢，于是下一步就是要解决速度慢的问题。

```
下面是传输速度的计算:

实际传输速度(496KB/s): spi_ref_clk / 4分频 / 8bit = 15873016Hz / 4 / 8 ≈ 496,031B/s

修复后的传输速度(5MB/s): spi_ref_clk / 4分频 / 8bit = 166666665Hz / 4 / 8 ≈ 5,208,333B/s
```


硬件平台信息：
![[Pasted image 20251222182013.png]]


**方案汇总**:
```cpp
SPI SS模式搬运测试方案验证清单:
——裸机spi200m+4分频: done 灯不亮(v13p_0.bin, 大小110MB, 用时27秒)
——裸机spi200m+8分频: done 灯不亮
——裸机spi166m+4分频: done 灯常亮(R374 LED2)(v13p_0.bin, 大小110MB, 用时32秒)
——mmap移植裸机ss例程: 速度很慢上不来,猜测被系统限制
——mmap移植裸机ss例程+设备树屏蔽spi控制器: 无法正常初始化spi控制器
——阅读内核spi相关的代码+找到时钟相关的代码并分析

找到内核驱动中设置分频的代码:
z7045/linux-xlnx-master/drivers/spi/spi-cadence.c: cdns_spi_config_clock_freq()
    该函数是根据实际应用传输速度配置需求,动态选择合适的分频系数
z7045/linux-xlnx-master/drivers/spi/spi-cadence.c: cdns_spi_probe()
    该函数里面有控制器时钟初始化相关的代码;
    强行设置 ref_clk 频率, 实际频率会比设置的小一点;
```



## 裸机验证

首先想办法编写相应的裸机程序，来传输，看看裸机传输速度能否不一样。

经过裸机传输验证，测速 166M频率经过4分频，最终传输速度大约有3~4MB每秒。

既然裸机环境下速度没问题，系统环境下速度很慢，那么就可能跟系统某些配置有关。

.bin文件转换成头文件: `xxd -i v13p_0.bin v13p_0.bin.h`。

完整例程代码: helloworld_裸机验证spi166m_4分频发送bin文件.c

```cpp
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"

//把待发送的.bin文件编译到内存里
#include "v13p_0.bin.h"

#include "xtime_l.h"
#define COUNTS_PER_SECOND          (XPAR_CPU_CORTEXA9_CORE_CLOCK_FREQ_HZ / 2)

#include "xspips.h"
static XSpiPs SpiInstance;
#define SPI_DEVICE_ID		XPAR_XSPIPS_0_DEVICE_ID

void spi_ss_tx(XSpiPs *SpiInstancePtr, uint8_t *WriteBuffer, off_t wrLenBytes)
{
	int Status;
	XTime tEnd, tCur;

	int lenMB = wrLenBytes / 1024 / 1024;
	printf("[%d MB] standalone spi ss writing ...\\r\\n", lenMB);

	XTime_GetTime(&tCur);
	//while (1)
	{
		Status = XSpiPs_PolledTransfer(SpiInstancePtr, WriteBuffer, NULL, wrLenBytes);
	}
	XTime_GetTime(&tEnd);

	u32 tUsedUs = ((tEnd-tCur)*1000000)/(COUNTS_PER_SECOND);
	u32 tUsedMs = tUsedUs / 1000;
	u32 tUsedSec = tUsedMs / 1000;

	if (Status == XST_SUCCESS)
	{
		printf("[%d MB] standalone spi ss writing done (tUsedSec = %d sec) (%d ms)\\r\\n", lenMB, tUsedSec, tUsedMs);
	} else
	{
		printf("[%d MB] standalone spi ss writing failed\\r\\n",lenMB);
	}
}

int main()
{
    init_platform();

    int Status;
    XSpiPs_Config *SpiConfig;
    XSpiPs *SpiInstancePtr = &SpiInstance;
    u16 SpiDeviceId = SPI_DEVICE_ID;

	//u32 MaxSize = MAX_DATA;
	//u32 ChipSelect = FLASH_SPI_SELECT_1;

	/*
	 * Initialize the SPI driver so that it's ready to use
	 */
	SpiConfig = XSpiPs_LookupConfig(SpiDeviceId);
	if (NULL == SpiConfig) {
		return XST_FAILURE;
	}

	Status = XSpiPs_CfgInitialize(SpiInstancePtr, SpiConfig,
					SpiConfig->BaseAddress);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	/*
	 * Perform a self-test to check hardware build
	 */
	Status = XSpiPs_SelfTest(SpiInstancePtr);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	/*
	 * Set the SPI device as a master with manual start and manual
	 * chip select mode options
	 */
	// 设置时序模式以及手动模式
	XSpiPs_SetOptions(SpiInstancePtr, 
        XSPIPS_CLK_ACTIVE_LOW_OPTION | XSPIPS_CLK_PHASE_1_OPTION | \\
		XSPIPS_MANUAL_START_OPTION | \\
		XSPIPS_MASTER_OPTION | XSPIPS_FORCE_SSELECT_OPTION);

	// 设置预分频为4倍分频(比如120M/4=30M)
	XSpiPs_SetClkPrescaler(SpiInstancePtr, XSPIPS_CLK_PRESCALE_4);

	//前面是初始化spi控制器,这里开始发送数据
	spi_ss_tx(SpiInstancePtr, v13p_0_bin, v13p_0_bin_len);

	printf("hello spi ss mode (end of program)\\r\\n");
    cleanup_platform();
    return 0;
}
```


![[Pasted image 20251222182104.png]]


## 内核调试

内核驱动里，有些对象实例并不是数据段里的静态变量，无法通过静态分析找到其定义处。而是通过动态内存分配来生成对应的实例，总的来说，动态分配无非就下面几种:

```
kmalloc  -->  __do_kmalloc
vmalloc  -->  __vmalloc_node_range
```

问题定位: 内核中控制器实际的工作频率就不高, 最终算出来的传输速率和实际速率吻合

![[Pasted image 20251222182120.png]]

传输速率：
15873016 Hz ÷ 4分频 = 3968254.0 Hz
15873016 Hz ÷ 4分频 ÷ 8bit/B = 496031.75 B/s
15873016 Hz ÷ 4分频 ÷ 8bit/B ÷ 1024B = 484.406005859375 KB/s

传输耗时：
110MB ÷ (496031.75 B/s) ÷ 60sec/min = 3.8755368649957047 min


![[Pasted image 20251222182130.png]]


设备树配置如下(pcw.dtsi):

```cpp
&spi0 {
	is-decoded-cs = <0>;
	num-cs = <3>;
	status = "okay";
	clock-frequency = <166666667>;
	spi0_dev_0@0 {
				compatible = "spidev";
				reg = <0>;
				spi-max-frequency = <41666667>;
				#address-cells = <1>;
				#size-cells = <1>;
	};
};
&spi1 {
	is-decoded-cs = <0>;
	num-cs = <3>;
	status = "okay";
	clock-frequency = <166666667>;
	spi0_dev_0@0 {
				compatible = "spidev";
				reg = <0>;
				spi-max-frequency = <41666667>;
				#address-cells = <1>;
				#size-cells = <1>;
	};
};
```



附件:
- [[build_kernel.sh]]
- [[spi_transfer.c]]
- [[spi-cadence.c]]
- [[spi-cadence-z7045-fix166.c]]


## 时钟来源

上面既然知道参考时钟的获取，那么接下来就需要知道从哪里获取的参考时钟。

```
linux-kernel/drivers/clk-gate.c
linux-kernel/drivers/clk-mux.c
linux-kernel/drivers/clk/zynq/pll.c —— PLL操作接口(开,关,roud_rate,recalc_rate)
```

![[Pasted image 20251222182444.png]]


对应的内核函数: __clk_hw_register_gate() 用于各个外设的开关操作接口。

寄存器的其他字段，在内核中也有对应的操作接口，如下图所示:

![[Pasted image 20251222182502.png]]

PLL注册: clk_register_zynq_pll
![[Pasted image 20251222182513.png]]


## SPI工作特性

**SPI工作模式**

![[Pasted image 20251222182530.png]]


![[Pasted image 20251222182538.png]]


![[Pasted image 20251222182551.png]]


## zynq_linux_spi_子系统

参考源文件: linux-xlnx-master/drivers/spi/spi-cadence.c

Q: 在内核代码中，如何动态获取caller？如何向上层caller追溯？ 
A: 直接 dump_stack()，使用栈回溯，回溯层数一般是10层，即往上追踪到10个caller函数名。

![[Pasted image 20251222182619.png]]


spi控制器对应的内核驱动(设备树——驱动匹配):
![[Pasted image 20251222182634.png]]


![[Pasted image 20251222182642.png]]

平台驱动、平台设备: platform_driver、platform_device



## clk子系统-zynq时钟树

如下图所示，zynq的时钟树就是 33.333333MHz 晶振是时钟源头，就像黄河源头一样，小小的不起眼。然后后续经过各种PLL倍频，最终形成三大PLL频率分支，分别是ARMPLL、DDRPLL、IOPLL。后续的各种外设需要的时钟，经过多路选择器Mux，以及分频Div，最后形成各个外设需要的时钟频率。

![[Pasted image 20251222182710.png]]

在内核clk核心相关的代码中，parent就是指上一级的时钟，比如 ARMPLL 的 parent 频率就是晶振 33.333333MHz，SPI的参考时钟的parent就是 IOPLL 时钟。


时钟输出对象列表：
![[Pasted image 20251222182728.png]]


## Linux内核_clk核心

![[Pasted image 20251222182746.png]]


如上图所示，上面的这些文件是clk子系统的核心文件，经过验证，它们都是会被编译进内核的(有对应的.o文件)。因此想要探究clk子系统核心，看这些文件接口。下面将分别说明每个源文件的用途和关键点。


```
linux-xlnx-master/drivers/clk/clk-mux.c
linux-xlnx-master/drivers/clk/clk-gate.c
linux-xlnx-master/drivers/clk/clk-divider.c
```

以之前的spi时钟为例，主要就是用于读写访问 SPI_CLK_CTRL 寄存器的。其中 clk-divider 就是分频系数值字段的访问。clk-gate.c 就是关于 disable/enable 字段的访问，clk-mux.c 就是时钟源选择字段的访问，如下图所示。


![[Pasted image 20251222182805.png]]

999999990 Hz / 0x3F = 999999990 Hz / 63 = 15873015.714285715 Hz

15873015.714285715 Hz / 4分配 / 8bit / 1024 = 484.405997140067 KB/s


上述上图中的注册函数，就是向clk核心注册各个设备自己的相关寄存器相关字段的访问代码。比如我们上面三个注册函数任选一个，找到其caller，然后找到caller列表里的zynq代码如下。

linux-xlnx-master/drivers/clk/zynq/clkc.c

![[Pasted image 20251222182821.png]]







