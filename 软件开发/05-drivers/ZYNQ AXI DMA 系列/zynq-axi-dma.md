
草稿: 
[[zynq-axi-dma.excalidraw]]

# 参考文档

1、axi dma 参考手册获取，如下图所示：其他官方现成的IP核也是通过该方式获取官方文档。
![[Pasted image 20260120095256.png]]

网盘参考 Vivado 2018.3 工程：
ax7020_axidma_simple_bandwidth.zip
ax7020_axidma_sg_bandwidth_burst16.zip


如下图所示，传输带宽上限受到公式中的两个参数控制：
![[Pasted image 20260317153442.png]]


如下图所示，即使 AXI DMA 的收发数据位宽可以设置很高，但是传输带宽上限受到HP接口位宽的限制。
![[Pasted image 20260317154814.png]]


把上面这些节点的结构细节都摸清楚之后，相当于你就同时掌握了它们的工作原理。



# 简单模式Block Design



1、打开 vivado 2018.3 软件，然后根据开发板处理器选型新建基础工程。


2、创建 Block Design，添加基础的 zynq ip 和一些必要的外设(串口打印)，然后跟随后续步骤，修改 zynq axi-dma 需要的一些配置。


3、下面开始 axi-dma 工程相关的配置，下面是PS端的配置，即ZYNQ IP核的配置。
![[Pasted image 20251225171940.png]]

![[Pasted image 20251225171946.png]]

4、添加 axi-dma ip 核，如下图所示：
![[Pasted image 20260120102246.png]]


5、设置 axi-dma ip 核，大多数使用默认配置，后续优化根据实际项目调整。其中 buffer 长度寄存器这个，指单个BD最大能传输多少数据量，或者指单个sg节点最大能传输多少数据量。
![[Pasted image 20260120103339.png]]


6、下面可选项（二选一）：**用FIFO模拟外设或者直接短接**。

（1）如果不需要FIFO来模拟外设，直接短接 axi-dma 的 S2MM 和 MM2S。
![[Pasted image 20260120104207.png]]

（2）如果需要用FIFO来模拟外设，如下图所示，添加并配置保持默认即可。
![[Pasted image 20251225172012.png]]

点击自动连接后，软件能帮我们自动连接的部分都连接好了，剩下的没有连接的IP核我们根据实际需要手动连接即可。
![[Pasted image 20251225172042.png]]
<font color=blue>axi-dma ip 核上的信号：M_AXI_MM2S 和 M_AXIS_MM2S，这两个信号线唯一差别是多了一个S，它们分别表示什么意思？</font>

M —— 表示该接口由 AXI DMA 核主动发起总线操作，对接的设备是Slave；
AXI —— 表示基础总线类型，无后缀表示**AXI 内存映射协议**；
AXIS —— AXI-Stream，专为**连续高速数据流**设计；
MM2S —— 表示数据流向是从内存映射到Stream。



7、最后，还需要添加concat这个IP核，用来把两根中断线连入到PS这边的 `IQR_F2P` 信号上。
![[Pasted image 20260120105620.png]]


8、之后剩下的比如smartconnect这些让软件自动连接。
![[Pasted image 20260120110004.png]]


如下图所示，下面图是 AXI DMA + FIFO 完整系统BD连接图：

![[Pasted image 20260108095401.png]]

如下图所示，下面图是 AXI DMA + MM2S短接S2MM 完整系统BD连接图：
![[Pasted image 20260120111425.png]]


9、最后还要自动检查一下线路有效性，如果有问题，就修改信号线连接。
![[Pasted image 20260120110631.png]]


10、最后导出生成封装，入选图所示：
![[Pasted image 20260120112826.png]]


11、操作完之后，最后编译生成bitstream即可，然后导出硬件信息并启动SDK。
![[Pasted image 20260120114616.png]]

接下来就是PS那边的事了，单独放在PS小节。




# 简单模式裸机带宽例程


首先拿到官方测试例程代码: 
xaxidma_example_sg_poll.c
xaxidma_example_sg_intr.c
xaxidma_example_simple_poll.c
xaxidma_example_simple_intr.c


![[Pasted image 20251225172126.png]]


如下图所示，例程代码中，涉及到 DEVICE_TO_DMA 和 DMA_TO_DEVICE，下面这张图能帮助你理清谁是 device。

![[Pasted image 20260317110635.png]]


---


**计时参考例程**

下面是一个完整可运行的内存拷贝测速例程，主要提供计时参考代码：
```cpp
#include "xil_printf.h"
#include "xtime_l.h"
#define TEST_SIZE_MB   16
#define TEST_SIZE      (TEST_SIZE_MB * 1024 * 1024)

static u8 src_buf[TEST_SIZE] __attribute__((aligned(64)));
static u8 dst_buf[TEST_SIZE] __attribute__((aligned(64)));
int main(void)
{
    XTime t_start, t_end;
    double elapsed_sec;
    double bandwidth;

    xil_printf("Zynq bandwidth test start\r\n");

    /* 预热 cache，避免首次 miss 干扰 */
    memset(src_buf, 0xAA, TEST_SIZE);
    memset(dst_buf, 0x00, TEST_SIZE);

    XTime_GetTime(&t_start);

    memcpy(dst_buf, src_buf, TEST_SIZE);

    XTime_GetTime(&t_end);

    elapsed_sec = (double)(t_end - t_start) /
                  (double)XPAR_CPU_CORTEXA9_0_CPU_CLK_FREQ_HZ;

    bandwidth = (double)TEST_SIZE_MB / elapsed_sec;

    xil_printf("Size: %d MB\r\n", TEST_SIZE_MB);
    xil_printf("Time: %d us\r\n", (u32)(elapsed_sec * 1e6));
    xil_printf("Bandwidth: %d MB/s\r\n",  (u32)bandwidth);
    return 0;
}
```




---


下面是 axi-dma-simple 裸机带宽测试
下面是基于zynq开发板进行的实验，任何zynq系列的板子都能进行下面的实验。


**1、IP核配置信息**
- zynq PL Fabric clock 频率为一路100MHz
- AXI DMA IP 核配置
	- Stream Data Width = 32bit
	- Buffer 长度寄存器位宽为24，即单个BD节点(或者单个sg节点)最多传输 16MB-1 字节；
	- 最大 Burst Size 为 16，即 16 x sizeof(int32_t)。
- 理论带宽: 100MHz x 数据宽度32bit = 3200bps = 400MB/s


**2、测试带宽记录**
```cpp
--- Entering main() --- 
Running XAxiDma_SimplePollExampleBandwidth ...
  Iter progress      : 100 / 100
  MAX_PKT_LEN        : 8 MB (buffer length width in axi dma ip core)
  COUNTS_PER_SECOND  : 333333343 ticks
  BW Cal Formula     : totalDataMB / (total_ticks / COUNTS_PER_SECOND)
  totalDataMB        : 800 MB
  total_ticks        : 700251027 ticks
  Bandwidth          : 380.82 MB/s
Successfully ran XAxiDma_SimplePoll Example
--- Exiting main() --- 

--- Entering main() --- 
Running XAxiDma_SimplePollExampleBandwidth ...
  Iter progress      : 100 / 100
  MAX_PKT_LEN        : 8 MB (buffer length width in axi dma ip core)
  COUNTS_PER_SECOND  : 333333343 ticks
  BW Cal Formula     : totalDataMB / (total_ticks / COUNTS_PER_SECOND)
  totalDataMB        : 800 MB
  total_ticks        : 700376134 ticks
  Bandwidth          : 380.75 MB/s
Successfully ran XAxiDma_SimplePoll Example
--- Exiting main() --- 
```


**3、完整例程代码**(simple_poll_bandwidth.c)：基于官方例程，做了最小修改。
```cpp
/******************************************************************************
*
* Copyright (C) 2010 - 2018 Xilinx, Inc.  All rights reserved.
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in
* all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
* XILINX  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
* WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
* OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
*
* Except as contained in this notice, the name of the Xilinx shall not be used
* in advertising or otherwise to promote the sale, use or other dealings in
* this Software without prior written authorization from Xilinx.
*
******************************************************************************/
/*****************************************************************************/
/**
 *
 * @file xaxidma_example_simple_poll.c
 *
 * This file demonstrates how to use the xaxidma driver on the Xilinx AXI
 * DMA core (AXIDMA) to transfer packets in polling mode when the AXI DMA core
 * is configured in simple mode.
 *
 * This code assumes a loopback hardware widget is connected to the AXI DMA
 * core for data packet loopback.
 *
 * To see the debug print, you need a Uart16550 or uartlite in your system,
 * and please set "-DDEBUG" in your compiler options. You need to rebuild your
 * software executable.
 *
 * Make sure that MEMORY_BASE is defined properly as per the HW system. The
 * h/w system built in Area mode has a maximum DDR memory limit of 64MB. In
 * throughput mode, it is 512MB.  These limits are need to ensured for
 * proper operation of this code.
 *
 *
 * <pre>
 * MODIFICATION HISTORY:
 *
 * Ver   Who  Date     Changes
 * ----- ---- -------- -------------------------------------------------------
 * 4.00a rkv  02/22/11 New example created for simple DMA, this example is for
 *       	       simple DMA
 * 5.00a srt  03/06/12 Added Flushing and Invalidation of Caches to fix CRs
 *		       648103, 648701.
 *		       Added V7 DDR Base Address to fix CR 649405.
 * 6.00a srt  03/27/12 Changed API calls to support MCDMA driver.
 * 7.00a srt  06/18/12 API calls are reverted back for backward compatibility.
 * 7.01a srt  11/02/12 Buffer sizes (Tx and Rx) are modified to meet maximum
 *		       DDR memory limit of the h/w system built with Area mode
 * 7.02a srt  03/01/13 Updated DDR base address for IPI designs (CR 703656).
 * 9.1   adk  01/07/16 Updated DDR base address for Ultrascale (CR 799532) and
 *		       removed the defines for S6/V6.
 * 9.3   ms   01/23/17 Modified xil_printf statement in main function to
 *                     ensure that "Successfully ran" and "Failed" strings are
 *                     available in all examples. This is a fix for CR-965028.
 *       ms   04/05/17 Modified Comment lines in functions to
 *                     recognize it as documentation block for doxygen
 *                     generation of examples.
 * </pre>
 *
 * ***************************************************************************

 */
/***************************** Include Files *********************************/
#include "xaxidma.h"
#include "xparameters.h"
#include "xdebug.h"

#define DEMO_BANDWIDTH_TEST 1

#if DEMO_BANDWIDTH_TEST
// bandwidth
#include "xtime_l.h"
#include <stdio.h>
#else
#endif // DEMO_BANDWIDTH_TEST

#if defined(XPAR_UARTNS550_0_BASEADDR)
#include "xuartns550_l.h"       /* to use uartns550 */
#endif

/******************** Constant Definitions **********************************/

/*
 * Device hardware build related constants.
 */

#define DMA_DEV_ID		XPAR_AXIDMA_0_DEVICE_ID

#ifdef XPAR_AXI_7SDDR_0_S_AXI_BASEADDR
#define DDR_BASE_ADDR		XPAR_AXI_7SDDR_0_S_AXI_BASEADDR
#elif XPAR_MIG7SERIES_0_BASEADDR
#define DDR_BASE_ADDR	XPAR_MIG7SERIES_0_BASEADDR
#elif XPAR_MIG_0_BASEADDR
#define DDR_BASE_ADDR	XPAR_MIG_0_BASEADDR
#elif XPAR_PSU_DDR_0_S_AXI_BASEADDR
#define DDR_BASE_ADDR	XPAR_PSU_DDR_0_S_AXI_BASEADDR
#endif

#ifndef DDR_BASE_ADDR
#warning CHECK FOR THE VALID DDR ADDRESS IN XPARAMETERS.H, \
		 DEFAULT SET TO 0x01000000
#define MEM_BASE_ADDR		0x01000000
#else
#define MEM_BASE_ADDR		(DDR_BASE_ADDR + 0x1000000)
#endif

#define TX_BUFFER_BASE		(MEM_BASE_ADDR + 0x00100000)
#define RX_BUFFER_BASE		(MEM_BASE_ADDR + 0x00300000)
#define RX_BUFFER_HIGH		(MEM_BASE_ADDR + 0x004FFFFF)

#if DEMO_BANDWIDTH_TEST
#define MAX_PKT_LEN		(8*1024*1024)   // buffer length width is 24, pow(2,24)-1 bytes
#else
#define MAX_PKT_LEN		0x20
#endif // DEMO_BANDWIDTH_TEST

#define TEST_START_VALUE	0xC

#define NUMBER_OF_TRANSFERS	100

/**************************** Type Definitions *******************************/


/***************** Macros (Inline Functions) Definitions *********************/


/************************** Function Prototypes ******************************/

#if (!defined(DEBUG))
extern void xil_printf(const char *format, ...);
#endif

int XAxiDma_SimplePollExample(u16 DeviceId);
int XAxiDma_SimplePollExampleBandwidth(u16 DeviceId);
static int CheckData(void);

/************************** Variable Definitions *****************************/
/*
 * Device instance definitions
 */
XAxiDma AxiDma;


/*****************************************************************************/
/**
* The entry point for this example. It invokes the example function,
* and reports the execution status.
*
* @param	None.
*
* @return
*		- XST_SUCCESS if example finishes successfully
*		- XST_FAILURE if example fails.
*
* @note		None.
*
******************************************************************************/
int main()
{
	int Status;

	xil_printf("\r\n--- Entering main() --- \r\n");

	/* Run the poll example for simple transfer */


#if DEMO_BANDWIDTH_TEST
	Status = XAxiDma_SimplePollExampleBandwidth(DMA_DEV_ID);
#else
	Status = XAxiDma_SimplePollExample(DMA_DEV_ID);
#endif // DEMO_BANDWIDTH_TEST

	if (Status != XST_SUCCESS) {
		xil_printf("XAxiDma_SimplePoll Example Failed\r\n");
		return XST_FAILURE;
	}

	xil_printf("Successfully ran XAxiDma_SimplePoll Example\r\n");

	xil_printf("--- Exiting main() --- \r\n");

	return XST_SUCCESS;

}

#if defined(XPAR_UARTNS550_0_BASEADDR)
/*****************************************************************************/
/*
*
* Uart16550 setup routine, need to set baudrate to 9600, and data bits to 8
*
* @param	None.
*
* @return	None
*
* @note		None.
*
******************************************************************************/
static void Uart550_Setup(void)
{

	/* Set the baudrate to be predictable
	 */
	XUartNs550_SetBaud(XPAR_UARTNS550_0_BASEADDR,
			XPAR_XUARTNS550_CLOCK_HZ, 9600);

	XUartNs550_SetLineControlReg(XPAR_UARTNS550_0_BASEADDR,
			XUN_LCR_8_DATA_BITS);

}
#endif



int XAxiDma_SimplePollExampleBandwidth(u16 DeviceId)
{
	XAxiDma_Config *CfgPtr;
	int Status;
	int Tries = NUMBER_OF_TRANSFERS;
	int Index;
	u8 *TxBufferPtr;
	u8 *RxBufferPtr;
	u8 Value;

	XTime tStart, tEnd;

	TxBufferPtr = (u8 *)TX_BUFFER_BASE;
	RxBufferPtr = (u8 *)RX_BUFFER_BASE;

	CfgPtr = XAxiDma_LookupConfig(DeviceId);
	if (!CfgPtr) {
		xil_printf("No config found for %d\r\n", DeviceId);
		return XST_FAILURE;
	}

	Status = XAxiDma_CfgInitialize(&AxiDma, CfgPtr);
	if (Status != XST_SUCCESS) {
		xil_printf("Initialization failed %d\r\n", Status);
		return XST_FAILURE;
	}

	if (XAxiDma_HasSg(&AxiDma)) {
		xil_printf("Device configured as SG mode\r\n");
		return XST_FAILURE;
	}

	XAxiDma_IntrDisable(&AxiDma, XAXIDMA_IRQ_ALL_MASK,
						XAXIDMA_DEVICE_TO_DMA);
	XAxiDma_IntrDisable(&AxiDma, XAXIDMA_IRQ_ALL_MASK,
						XAXIDMA_DMA_TO_DEVICE);

	Value = TEST_START_VALUE;

	for (Index = 0; Index < MAX_PKT_LEN; Index++) {
		TxBufferPtr[Index] = Value;
		Value = (Value + 1) & 0xFF;
	}

	Xil_DCacheFlushRange((UINTPTR)TxBufferPtr, MAX_PKT_LEN);
	Xil_DCacheFlushRange((UINTPTR)RxBufferPtr, MAX_PKT_LEN);

	xil_printf("Running XAxiDma_SimplePollExampleBandwidth ...\r\n");
	u64 total_ticks = 0;
	for (Index = 0; Index < Tries; Index++) {

		XTime_GetTime(&tStart);

		Status = XAxiDma_SimpleTransfer(&AxiDma,
				(UINTPTR)RxBufferPtr,
				MAX_PKT_LEN,
				XAXIDMA_DEVICE_TO_DMA);

		if (Status != XST_SUCCESS)
			return XST_FAILURE;

		Status = XAxiDma_SimpleTransfer(&AxiDma,
				(UINTPTR)TxBufferPtr,
				MAX_PKT_LEN,
				XAXIDMA_DMA_TO_DEVICE);

		if (Status != XST_SUCCESS)
			return XST_FAILURE;

	

		while ((XAxiDma_Busy(&AxiDma, XAXIDMA_DEVICE_TO_DMA)) ||
			   (XAxiDma_Busy(&AxiDma, XAXIDMA_DMA_TO_DEVICE))) {
			/* polling */
		}

		XTime_GetTime(&tEnd);
		printf("  Iter progress      : %d / %d\r", Index + 1, Tries);
		fflush(stdout);

		total_ticks += (tEnd - tStart);

		Status = CheckData();
		if (Status != XST_SUCCESS)
			return XST_FAILURE;
	}

	int totalDataMB = MAX_PKT_LEN * Tries / 1024 / 1024;

	printf("\r\n");
	printf("  MAX_PKT_LEN        : %d MB (buffer length width in axi dma ip core)\r\n", MAX_PKT_LEN / 1024 / 1024);
	printf("  COUNTS_PER_SECOND  : %d ticks\r\n", COUNTS_PER_SECOND);
	printf("  BW Cal Formula     : totalDataMB / (total_ticks / COUNTS_PER_SECOND)\r\n");
	printf("  totalDataMB        : %d MB\r\n", totalDataMB);
	printf("  total_ticks        : %d ticks\r\n", total_ticks);
	printf("  Bandwidth          : %.2lf MB/s\r\n", (double)totalDataMB * COUNTS_PER_SECOND / total_ticks);

	return XST_SUCCESS;
}


/*****************************************************************************/
/**
* The example to do the simple transfer through polling. The constant
* NUMBER_OF_TRANSFERS defines how many times a simple transfer is repeated.
*
* @param	DeviceId is the Device Id of the XAxiDma instance
*
* @return
*		- XST_SUCCESS if example finishes successfully
*		- XST_FAILURE if error occurs
*
* @note		None
*
*
******************************************************************************/
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
	if (!CfgPtr) {
		xil_printf("No config found for %d\r\n", DeviceId);
		return XST_FAILURE;
	}

	Status = XAxiDma_CfgInitialize(&AxiDma, CfgPtr);
	if (Status != XST_SUCCESS) {
		xil_printf("Initialization failed %d\r\n", Status);
		return XST_FAILURE;
	}

	if(XAxiDma_HasSg(&AxiDma)){
		xil_printf("Device configured as SG mode \r\n");
		return XST_FAILURE;
	}

	/* Disable interrupts, we use polling mode
	 */
	XAxiDma_IntrDisable(&AxiDma, XAXIDMA_IRQ_ALL_MASK,
						XAXIDMA_DEVICE_TO_DMA);
	XAxiDma_IntrDisable(&AxiDma, XAXIDMA_IRQ_ALL_MASK,
						XAXIDMA_DMA_TO_DEVICE);

	Value = TEST_START_VALUE;

	for(Index = 0; Index < MAX_PKT_LEN; Index ++) {
			TxBufferPtr[Index] = Value;

			Value = (Value + 1) & 0xFF;
	}
	/* Flush the SrcBuffer before the DMA transfer, in case the Data Cache
	 * is enabled
	 */
	Xil_DCacheFlushRange((UINTPTR)TxBufferPtr, MAX_PKT_LEN);
#ifdef __aarch64__
	Xil_DCacheFlushRange((UINTPTR)RxBufferPtr, MAX_PKT_LEN);
#endif

	for(Index = 0; Index < Tries; Index ++) {


		Status = XAxiDma_SimpleTransfer(&AxiDma,(UINTPTR) RxBufferPtr,
					MAX_PKT_LEN, XAXIDMA_DEVICE_TO_DMA);

		if (Status != XST_SUCCESS) {
			return XST_FAILURE;
		}

		Status = XAxiDma_SimpleTransfer(&AxiDma,(UINTPTR) TxBufferPtr,
					MAX_PKT_LEN, XAXIDMA_DMA_TO_DEVICE);

		if (Status != XST_SUCCESS) {
			return XST_FAILURE;
		}

		while ((XAxiDma_Busy(&AxiDma,XAXIDMA_DEVICE_TO_DMA)) ||
			(XAxiDma_Busy(&AxiDma,XAXIDMA_DMA_TO_DEVICE))) {
				/* Wait */
		}

		Status = CheckData();
		if (Status != XST_SUCCESS) {
			return XST_FAILURE;
		}

	}

	/* Test finishes successfully
	 */
	return XST_SUCCESS;
}



/*****************************************************************************/
/*
*
* This function checks data buffer after the DMA transfer is finished.
*
* @param	None
*
* @return
*		- XST_SUCCESS if validation is successful.
*		- XST_FAILURE otherwise.
*
* @note		None.
*
******************************************************************************/
static int CheckData(void)
{
	u8 *RxPacket;
	int Index = 0;
	u8 Value;

	RxPacket = (u8 *) RX_BUFFER_BASE;
	Value = TEST_START_VALUE;

	/* Invalidate the DestBuffer before receiving the data, in case the
	 * Data Cache is enabled
	 */
#ifndef __aarch64__
	Xil_DCacheInvalidateRange((UINTPTR)RxPacket, MAX_PKT_LEN);
#endif

	for(Index = 0; Index < MAX_PKT_LEN; Index++) {
		if (RxPacket[Index] != Value) {
			xil_printf("Data error %d: %x/%x\r\n",
			Index, (unsigned int)RxPacket[Index],
				(unsigned int)Value);

			return XST_FAILURE;
		}
		Value = (Value + 1) & 0xFF;
	}

	return XST_SUCCESS;
}
```



# 简单模式裸机接口工作机制




## XAxiDma_LookupConfig


BTT / max_burst_size = N, DMA会自动发起N次突发事务，以完成数据传输。

axi-dma-simple-poll 参数配置情况：
```cpp
XAxiDma_Config XAxiDma_ConfigTable[XPAR_XAXIDMA_NUM_INSTANCES] =
{
	{
	XPAR_AXI_DMA_0_DEVICE_ID,// 0
	XPAR_AXI_DMA_0_BASEADDR,// 0x40400000
	XPAR_AXI_DMA_0_SG_INCLUDE_STSCNTRL_STRM,// 0, 是否包含状态和控制流
	XPAR_AXI_DMA_0_INCLUDE_MM2S,// 1, MM to axi-stream(PL)
	XPAR_AXI_DMA_0_INCLUDE_MM2S_DRE,// 0, 是否启用数据重对齐引擎
	XPAR_AXI_DMA_0_M_AXI_MM2S_DATA_WIDTH,// 32, DMA从DDR读取数据时的单次传输位宽
	XPAR_AXI_DMA_0_INCLUDE_S2MM,// 1
	XPAR_AXI_DMA_0_INCLUDE_S2MM_DRE,// 0, 是否启用数据重对齐引擎
	XPAR_AXI_DMA_0_M_AXI_S2MM_DATA_WIDTH,// 32, DMA写入DDR时的单次传输位宽
	XPAR_AXI_DMA_0_INCLUDE_SG,// 0
	XPAR_AXI_DMA_0_NUM_MM2S_CHANNELS,// 1, DMA可以同时发起独立传输的通道数
	XPAR_AXI_DMA_0_NUM_S2MM_CHANNELS,
	XPAR_AXI_DMA_0_MM2S_BURST_SIZE,// 16, 指单次地址发起后，连续传输 N 个数据
	XPAR_AXI_DMA_0_S2MM_BURST_SIZE,// 16
	XPAR_AXI_DMA_0_MICRO_DMA,// 0
	XPAR_AXI_DMA_0_ADDR_WIDTH,// 32, 决定 DMA 能寻址的最大内存空间
	XPAR_AXI_DMA_0_SG_LENGTH_WIDTH // 14,2^14 - 1 = 16KB, 每一段sg传输的最大长度
	}
};
```


axi-dma-sgdma-poll 参数配置:
```cpp
XAxiDma_Config XAxiDma_ConfigTable[XPAR_XAXIDMA_NUM_INSTANCES] =
{
	{
	XPAR_AXI_DMA_0_DEVICE_ID,//0
	XPAR_AXI_DMA_0_BASEADDR,//0x4040_0000
	XPAR_AXI_DMA_0_SG_INCLUDE_STSCNTRL_STRM,//0
	XPAR_AXI_DMA_0_INCLUDE_MM2S,//1
	XPAR_AXI_DMA_0_INCLUDE_MM2S_DRE,//0
	XPAR_AXI_DMA_0_M_AXI_MM2S_DATA_WIDTH,//32
	XPAR_AXI_DMA_0_INCLUDE_S2MM,//1
	XPAR_AXI_DMA_0_INCLUDE_S2MM_DRE,//0
	XPAR_AXI_DMA_0_M_AXI_S2MM_DATA_WIDTH,//32
	XPAR_AXI_DMA_0_INCLUDE_SG,//1
	XPAR_AXI_DMA_0_NUM_MM2S_CHANNELS,//1
	XPAR_AXI_DMA_0_NUM_S2MM_CHANNELS,//1
	XPAR_AXI_DMA_0_MM2S_BURST_SIZE,//16, 16 x sizeof(32bit)
	XPAR_AXI_DMA_0_S2MM_BURST_SIZE,//16, 16 x sizeof(32bit)
	XPAR_AXI_DMA_0_MICRO_DMA,//0
	XPAR_AXI_DMA_0_ADDR_WIDTH,//32
	XPAR_AXI_DMA_0_SG_LENGTH_WIDTH //14, (power(2,14)-1)=0x3FFF
	}
};
```



## XAxiDma_Reset

XAxiDma_Reset、XAxiDma_ResetIsDone

```cpp
void XAxiDma_Reset(XAxiDma * InstancePtr)
{
	// XAXIDMA_CR_RESET_MASK == 0x04
	// XAXIDMA_CR_OFFSET     == 0x00
	// RegBaseTx             == RegBase + 0x00
	// RegBaseRx             == RegBase + 0x30
	XAxiDma_WriteReg(RegBaseRx, XAXIDMA_CR_OFFSET, XAXIDMA_CR_RESET_MASK);
	XAxiDma_WriteReg(RegBaseTx, XAXIDMA_CR_OFFSET, XAXIDMA_CR_RESET_MASK);
}

int XAxiDma_ResetIsDone(XAxiDma * InstancePtr)
{
	// 读取 XAXIDMA_CR_OFFSET 寄存器并判断刚刚的复位bit
}
```


![[Pasted image 20260317174711.png]]

IRQThreshold 的取值范围表明，单个Packet最多只能有255个BD，或者说 sgt 最多只能有 255 个sg节点。




## XAxiDma_SimpleTransfer


XAxiDma_SimpleTransfer()简单传输的流程：
- 1、检查DMA引擎必须处于空闲状态；
- 2、把Buffer地址和长度写到对应寄存器；
- 3、启动引擎传输。

```cpp
u32 XAxiDma_SimpleTransfer(XAxiDma *InstancePtr, UINTPTR BuffAddr, u32 Length, int Direction)
{
	// 这里只展示核心代码
	
	if(Direction == XAXIDMA_DMA_TO_DEVICE){
	
		// DMA引擎必须处于空闲状态
		if (! (XAxiDma_ReadReg(XAXIDMA_SR_OFFSET) & XAXIDMA_HALTED_MASK) )
		{
			if (XAxiDma_Busy(InstancePtr,Direction))
				return XST_FAILURE;// 引擎正忙
		}

		// 填充地址(XAXIDMA_SRCADDR_OFFSET=0x18)
		XAxiDma_WriteReg(TxChanBase, XAXIDMA_SRCADDR_OFFSET, LOWER_32_BITS(BuffAddr));

		// 把长度写进去(XAXIDMA_BUFFLEN_OFFSET==0x28)
        XAxiDma_WriteReg(TxChanBase, XAXIDMA_BUFFLEN_OFFSET, Length);

		// 启动位设为1, 启动传输
        XAxiDma_WriteReg(TxChanBase,
                XAXIDMA_CR_OFFSET,
                XAxiDma_ReadReg(TxChanBase,
                XAXIDMA_CR_OFFSET) | XAXIDMA_CR_RUNSTOP_MASK);

	} else if(Direction == XAXIDMA_DEVICE_TO_DMA){
		// 和上面流程一样,只不过是Rx的寄存器...
	}
}
```


![[Pasted image 20260317181259.png]]



## XAxiDma_Busy


```cpp
u32 XAxiDma_Busy(XAxiDma *InstancePtr, int Direction)
{
	// 读取状态寄存器: XAXIDMA_SR_OFFSET==0x04, 判断 XAXIDMA_IDLE_MASK==0x02,
	// 1=表示不忙, 0=表示忙状态
	return (XAxiDma_ReadReg(XAXIDMA_SR_OFFSET) & XAXIDMA_IDLE_MASK)? FALSE:TRUE;
}
```

![[Pasted image 20260317182209.png]]




# 简单模式Linux驱动带宽例程




在上一章节的基础上，我们继续探究普通dma在系统下的传输带宽。

如下图所示，前面使能了sg模式，那么这章就是关闭sg模式，其他参数不变：
![[Pasted image 20260312171920.png]]

![[Pasted image 20260312172040.png]]


测试驱动：axidma_v006.c


测试记录：
```cpp
// single 模式下最多只能测到 8MB, 测到16MB就会出错
// 2的24次方刚好等于16MB
zynq> insmod axidma_v006.ko txmethod="single"
called axidma_probe
txmethod        = single (list: sg, single, multi-single)
test_iterations = 10
test_buf_size   = 2048 KB
test_seg_size   = 1024 KB (for sg and multi-single)
start test: 10 iterations, 2097152 bytes
[TEST] total_bytes is 20971520
[TEST] total_ns is 53778292      // 371 MBps
all test pass
zynq> rmmod axidma_v006
called axidma_remove
zynq> 
zynq> 
zynq> 
zynq> insmod axidma_v006.ko txmethod="single" test_buf_size=4194304
called axidma_probe
txmethod        = single (list: sg, single, multi-single)
test_iterations = 10
test_buf_size   = 4096 KB
test_seg_size   = 1024 KB (for sg and multi-single)
start test: 10 iterations, 4194304 bytes
[TEST] total_bytes is 41943040
[TEST] total_ns is 106343725      // 376 MBps
all test pass
zynq> rmmod axidma_v006
called axidma_remove
zynq> 
zynq> 
zynq> 
zynq> insmod axidma_v006.ko txmethod="single" test_buf_size=8388608
called axidma_probe
txmethod        = single (list: sg, single, multi-single)
test_iterations = 10
test_buf_size   = 8192 KB
test_seg_size   = 1024 KB (for sg and multi-single)
start test: 10 iterations, 8388608 bytes
[TEST] total_bytes is 83886080
[TEST] total_ns is 211457023      // 378 MBps
all test pass
zynq> rmmod axidma_v006
called axidma_remove
zynq> 
zynq> 
```



下面是 multi-single 测试记录：
```cpp
zynq> insmod axidma_v006.ko txmethod="multi-single" test_buf_size=3355
4432 test_seg_size=8388608
called axidma_probe
txmethod        = multi-single (list: sg, single, multi-single)
test_iterations = 10
test_buf_size   = 32768 KB
test_seg_size   = 8192 KB (for sg and multi-single)
start test: 10 iterations, 33554432 bytes
[TEST] total_bytes is 335544320
[TEST] total_ns is 891870822       // 358.79 MBps
all test pass
zynq> rmmod axidma_v006
called axidma_remove
zynq> 
```



总结：multi-single 起始就是把大数据拆成小批量来逐个传输，传输带宽基本上影响不大，而大数据内存的最大分配空间，取决于 CMA 预留的大小。

```cpp
zynq> cat /proc/meminfo | grep -i cma
CmaTotal:         131072 kB
CmaFree:          128392 kB
zynq> 
```




# SG模式Block Design



如下图所示，和简单模式的唯一区别是，把SG模式的使能开关勾选上即可。

![[Pasted image 20260318105523.png]]




# SG模式裸机带宽例程


首先用一张图简单描述该例程的传输特点：

![[Pasted image 20260319104431.png]]



**1、IP核配置信息**
- zynq PL Fabric clock 频率为一路100MHz
- AXI DMA IP 核配置
	- 使能sg模式；
	- Stream Data Width = 32bit
	- Buffer 长度寄存器位宽为24，即单个BD节点(或者单个sg节点)最多传输 16MB-1 字节；
	- 最大 Burst Size 为 16，即 16 x sizeof(int32_t)。
- 理论带宽: 100MHz x 数据宽度32bit = 3200bps = 400MB/s


**2、测试带宽记录**
```cpp
--- Entering main() --- 
  Iter progress      : 100 / 100
  MAX_PKT_LEN        : 8 MB (buffer length width in axi dma ip core)
  MBs per BD         : 8 MB
  COUNTS_PER_SECOND  : 333333343 ticks
  BW Cal Formula     : totalDataMB / (total_ticks / COUNTS_PER_SECOND)
  total_BdCount      : 100 BDs
  total_ticks        : 10 ticks
  Bandwidth          : 351.94 MB/s
---------------------

--- Entering main() --- 
  Iter progress      : 100 / 100
  MAX_PKT_LEN        : 8 MB (buffer length width in axi dma ip core)
  MBs per BD         : 8 MB
  COUNTS_PER_SECOND  : 333333343 ticks
  BW Cal Formula     : totalDataMB / (total_ticks / COUNTS_PER_SECOND)
  total_BdCount      : 100 BDs
  total_ticks        : 10 ticks
  Bandwidth          : 351.72 MB/s
---------------------
```



**3、完整例程代码**(sg_poll_bandwidth.c)：基于官方例程，做了最小修改。

```cpp
/******************************************************************************
*
* Copyright (C) 2010 - 2018 Xilinx, Inc.  All rights reserved.
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in
* all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
* XILINX  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
* WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
* OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
*
* Except as contained in this notice, the name of the Xilinx shall not be used
* in advertising or otherwise to promote the sale, use or other dealings in
* this Software without prior written authorization from Xilinx.
*
******************************************************************************/
/*****************************************************************************/
/**
 *
 * @file xaxidma_example_sg_poll.c
 *
 * This file demonstrates how to use the xaxidma driver on the Xilinx AXI
 * DMA core (AXIDMA) to transfer packets in polling mode when the AXIDMA
 * core is configured in Scatter Gather Mode.
 *
 * This code assumes a loopback hardware widget is connected to the AXI DMA
 * core for data packet loopback.
 *
 * To see the debug print, you need a Uart16550 or uartlite in your system,
 * and please set "-DDEBUG" in your compiler options. You need to rebuild your
 * software executable.
 *
 * Make sure that MEMORY_BASE is defined properly as per the HW system. The
 * h/w system built in Area mode has a maximum DDR memory limit of 64MB. In
 * throughput mode, it is 512MB.  These limits are need to ensured for
 * proper operation of this code.
 *
 *
 * <pre>
 * MODIFICATION HISTORY:
 *
 * Ver   Who  Date     Changes
 * ----- ---- -------- -------------------------------------------------------
 * 1.00a jz   05/17/10 First release
 * 2.00a jz   08/10/10 Second release, added in xaxidma_g.c, xaxidma_sinit.c,
 *                     updated tcl file, added xaxidma_porting_guide.h, removed
 *                     workaround for endianness
 * 4.00a rkv  02/22/11 Name of the file has been changed for naming consistency
 *       	       	   Added interrupt support for ARM.
 * 5.00a srt  03/05/12 Added Flushing and Invalidation of Caches to fix CRs
 *		       		   648103, 648701.
 *		       		   Added V7 DDR Base Address to fix CR 649405.
 * 6.00a srt  03/27/12 Changed API calls to support MCDMA driver.
 * 7.00a srt  06/18/12 API calls are reverted back for backward compatibility.
 * 7.01a srt  11/02/12 Buffer sizes (Tx and Rx) are modified to meet maximum
 *		       DDR memory limit of the h/w system built with Area mode
 * 7.02a srt  03/01/13 Updated DDR base address for IPI designs (CR 703656).
 * 9.1   adk  01/07/16 Updated DDR base address for Ultrascale (CR 799532) and
 *		       removed the defines for S6/V6.
 * 9.2   vak  15/04/16 Fixed compilation warnings in th example
 * 9.3   ms   01/23/17 Modified xil_printf statement in main function to
 *                     ensure that "Successfully ran" and "Failed" strings are
 *                     available in all examples. This is a fix for CR-965028.
 * </pre>
 *
 * ***************************************************************************
 */
/***************************** Include Files *********************************/
#include "xaxidma.h"
#include "xparameters.h"
#include "xdebug.h"

#include "xtime_l.h"
#include <stdio.h>
#include "sleep.h"

#ifdef __aarch64__
#include "xil_mmu.h"
#endif

#if (!defined(DEBUG))
extern void xil_printf(const char *format, ...);
#endif

/******************** Constant Definitions **********************************/

/*
 * Device hardware build related constants.
 */

#define DMA_DEV_ID		XPAR_AXIDMA_0_DEVICE_ID

#ifndef DDR_BASE_ADDR
#define MEM_BASE_ADDR		0x01000000
#endif // DDR_BASE_ADDR

#define TX_BD_SPACE_BASE	(MEM_BASE_ADDR)
#define TX_BD_SPACE_HIGH	(MEM_BASE_ADDR + 0x00000FFF)
#define RX_BD_SPACE_BASE	(MEM_BASE_ADDR + 0x00001000)
#define RX_BD_SPACE_HIGH	(MEM_BASE_ADDR + 0x00001FFF)
#define TX_BUFFER_BASE		(MEM_BASE_ADDR + 0x00100000)
#define RX_BUFFER_BASE		(MEM_BASE_ADDR + 0x00300000)
#define RX_BUFFER_HIGH		(MEM_BASE_ADDR + 0x004FFFFF)


//#define MAX_PKT_LEN		0x20
#define MAX_PKT_LEN (8*1024*1024)  // buffer length width is 24 --> pow(2,24)-1
#define MARK_UNCACHEABLE        0x701

#define TEST_START_VALUE	0xC



/**************************** Type Definitions *******************************/


/***************** Macros (Inline Functions) Definitions *********************/


/************************** Function Prototypes ******************************/

static int RxSetup(XAxiDma * AxiDmaInstPtr);
static int TxSetup(XAxiDma * AxiDmaInstPtr);
static int SendPacket(XAxiDma * AxiDmaInstPtr);
static int CheckData(void);
static int CheckDmaResult(XAxiDma * AxiDmaInstPtr);

/************************** Variable Definitions *****************************/
/*
 * Device instance definitions
 */
XAxiDma AxiDma;

/*
 * Buffer for transmit packet. Must be 32-bit aligned to be used by DMA.
 */
u32 *Packet = (u32 *) TX_BUFFER_BASE;

/*****************************************************************************/
/**
*
* Main function
*
* This function is the main entry of the tests on DMA core. It sets up
* DMA engine to be ready to receive and send packets, then a packet is
* transmitted and will be verified after it is received via the DMA loopback
* widget.
*
* @param	None
*
* @return
*		- XST_SUCCESS if test passes
*		- XST_FAILURE if test fails.
*
* @note		None.
*
******************************************************************************/
int main(void)
{
	int Status;
	XAxiDma_Config *Config;
	
	xil_printf("\r\n--- Entering main() --- \r\n");

#ifdef __aarch64__
	Xil_SetTlbAttributes(TX_BD_SPACE_BASE, MARK_UNCACHEABLE);
	Xil_SetTlbAttributes(RX_BD_SPACE_BASE, MARK_UNCACHEABLE);
#endif

	Config = XAxiDma_LookupConfig(DMA_DEV_ID);
	if (!Config) {
		xil_printf("No config found for %d\r\n", DMA_DEV_ID);

		return XST_FAILURE;
	}

	/* Initialize DMA engine */
	Status = XAxiDma_CfgInitialize(&AxiDma, Config);
	if (Status != XST_SUCCESS) {
		xil_printf("Initialization failed %d\r\n", Status);
		return XST_FAILURE;
	}

	if(!XAxiDma_HasSg(&AxiDma)) {
		xil_printf("Device must be configured as sg mode (not simple mode)\r\n");

		return XST_FAILURE;
	}

	// start RX first time
	Status = RxSetup(&AxiDma);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	// then start TX
	Status = TxSetup(&AxiDma);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}
	
	XAxiDma_BdRing *TxRingPtr;
	XAxiDma_BdRing *RxRingPtr;
	XAxiDma_Bd *BdPtr;
	int txedBdCount;
	int rxedBdCount;
	int FreeBdCount;
	int total_txedBdCount;
	int total_rxedBdCount;
	u64 total_txticks;
	u64 total_rxticks;
	XTime tStart, tEnd;
	
	
	TxRingPtr = XAxiDma_GetTxRing(&AxiDma);
	RxRingPtr = XAxiDma_GetRxRing(&AxiDma);
	total_txedBdCount = 0;
	total_rxedBdCount = 0;
	total_txticks = 0;
	total_rxticks = 0;
	int total_iters = 100;
	for(int i=0; i<total_iters; i++)
	{
	
		XTime_GetTime(&tStart);
	
		/* Send a packet */
		Status = SendPacket(&AxiDma);
		if (Status != XST_SUCCESS) {
			return XST_FAILURE;
		}
	
		/* Wait until the one BD TX transaction is done */
		while ((txedBdCount = XAxiDma_BdRingFromHw(TxRingPtr,
								   XAXIDMA_ALL_BDS,
								   &BdPtr)) == 0) {
		}
		

		
		/* Free all processed TX BDs for future transmission */
		Status = XAxiDma_BdRingFree(TxRingPtr, txedBdCount, BdPtr);
		if (Status != XST_SUCCESS) {
			xil_printf("Failed to free %d tx BDs %d\r\n",
				txedBdCount, Status);
			return XST_FAILURE;
		}
	
		XTime_GetTime(&tEnd);
		total_txticks += (tEnd - tStart);
		total_txedBdCount += txedBdCount;
	
	
		/////////////// RX ///////////////
		
		XTime_GetTime(&tStart);
		
		/* Wait until the data has been received by the Rx channel */
		while ((rxedBdCount = XAxiDma_BdRingFromHw(RxRingPtr,
								   XAXIDMA_ALL_BDS,
								   &BdPtr)) == 0) {
		}
		
		/* Free all processed RX BDs for future transmission */
		Status = XAxiDma_BdRingFree(RxRingPtr, rxedBdCount, BdPtr);
		if (Status != XST_SUCCESS) {
			xil_printf("Failed to free %d rx BDs %d\r\n",
				rxedBdCount, Status);
			return XST_FAILURE;
		}
		
		/* Return processed BDs to RX channel so we are ready to receive new
		 * packets:
		 *    - Allocate all free RX BDs
		 *    - Pass the BDs to RX channel
		 */
		FreeBdCount = XAxiDma_BdRingGetFreeCnt(RxRingPtr);
		Status = XAxiDma_BdRingAlloc(RxRingPtr, FreeBdCount, &BdPtr);
		if (Status != XST_SUCCESS) {
			xil_printf("bd alloc failed\r\n");
			return XST_FAILURE;
		}

		Status = XAxiDma_BdRingToHw(RxRingPtr, FreeBdCount, BdPtr);
		if (Status != XST_SUCCESS) {
			xil_printf("Submit %d rx BDs failed %d\r\n", FreeBdCount, Status);
			return XST_FAILURE;
		}
		
		XTime_GetTime(&tEnd);
		total_rxticks += (tEnd - tStart);
		total_rxedBdCount += rxedBdCount;
		

		/* Check received data */
		if (CheckData() != XST_SUCCESS) {

			return XST_FAILURE;
		}
		
		printf("  Iter progress      : %d / %d\r", i + 1, total_iters);
		fflush(stdout);
	}
	
	int buflenMB = MAX_PKT_LEN / 1024 / 1024;
	printf("\r\n");
	printf("  MAX_PKT_LEN        : %d MB (buffer length width in axi dma ip core)\r\n", buflenMB);
	printf("  MBs per BD         : %d MB\r\n", buflenMB);
	printf("  COUNTS_PER_SECOND  : %d ticks\r\n", COUNTS_PER_SECOND);
	printf("  BW Cal Formula     : totalDataMB / (total_ticks / COUNTS_PER_SECOND)\r\n");
	
	printf("  total_BdCount      : %d BDs\r\n", total_txedBdCount);
	printf("  total_ticks        : %lu ticks\r\n", total_txticks);
	printf("  Bandwidth          : %.2lf MB/s\r\n", (double)total_txedBdCount * buflenMB * COUNTS_PER_SECOND / total_txticks);
	printf("---------------------\r\n");
	//printf("  total_rxedBdCount  : %d BDs\r\n", total_rxedBdCount);
	//printf("  total_rxticks      : %lu ticks\r\n", total_rxticks);
	//printf("  Rx Bandwidth       : %.2lf MB/s\r\n", (double)total_rxedBdCount * buflenMB * COUNTS_PER_SECOND / total_rxticks);

	return XST_SUCCESS;
}


/*****************************************************************************/
/**
*
* This function sets up RX channel of the DMA engine to be ready for packet
* reception
*
* @param	AxiDmaInstPtr is the pointer to the instance of the DMA engine.
*
* @return	XST_SUCCESS if the setup is successful, XST_FAILURE otherwise.
*
* @note		None.
*
******************************************************************************/
static int RxSetup(XAxiDma * AxiDmaInstPtr)
{
	XAxiDma_BdRing *RxRingPtr;
	int Delay = 0;
	int Coalesce = 1;
	int Status;
	XAxiDma_Bd BdTemplate;
	XAxiDma_Bd *BdPtr;
	XAxiDma_Bd *BdCurPtr;
	u32 BdCount;
	u32 FreeBdCount;
	UINTPTR RxBufferPtr;
	int Index;

	RxRingPtr = XAxiDma_GetRxRing(&AxiDma);

	/* Disable all RX interrupts before RxBD space setup */

	XAxiDma_BdRingIntDisable(RxRingPtr, XAXIDMA_IRQ_ALL_MASK);

	/* Set delay and coalescing */
	XAxiDma_BdRingSetCoalesce(RxRingPtr, Coalesce, Delay);

	/* Setup Rx BD space */
	BdCount = XAxiDma_BdRingCntCalc(XAXIDMA_BD_MINIMUM_ALIGNMENT,
				RX_BD_SPACE_HIGH - RX_BD_SPACE_BASE + 1);

	Status = XAxiDma_BdRingCreate(RxRingPtr, RX_BD_SPACE_BASE,
				RX_BD_SPACE_BASE,
				XAXIDMA_BD_MINIMUM_ALIGNMENT, BdCount);

	if (Status != XST_SUCCESS) {
		xil_printf("RX create BD ring failed %d\r\n", Status);

		return XST_FAILURE;
	}

	/*
	 * Setup an all-zero BD as the template for the Rx channel.
	 */
	XAxiDma_BdClear(&BdTemplate);

	Status = XAxiDma_BdRingClone(RxRingPtr, &BdTemplate);
	if (Status != XST_SUCCESS) {
		xil_printf("RX clone BD failed %d\r\n", Status);

		return XST_FAILURE;
	}

	/* Attach buffers to RxBD ring so we are ready to receive packets */

	FreeBdCount = XAxiDma_BdRingGetFreeCnt(RxRingPtr);

	Status = XAxiDma_BdRingAlloc(RxRingPtr, FreeBdCount, &BdPtr);
	if (Status != XST_SUCCESS) {
		xil_printf("RX alloc BD failed %d\r\n", Status);

		return XST_FAILURE;
	}

	BdCurPtr = BdPtr;
	RxBufferPtr = RX_BUFFER_BASE;
	for (Index = 0; Index < FreeBdCount; Index++) {
		Status = XAxiDma_BdSetBufAddr(BdCurPtr, RxBufferPtr);

		if (Status != XST_SUCCESS) {
			xil_printf("Set buffer addr %x on BD %x failed %d\r\n",
			    (unsigned int)RxBufferPtr,
			    (UINTPTR)BdCurPtr, Status);

			return XST_FAILURE;
		}

		Status = XAxiDma_BdSetLength(BdCurPtr, MAX_PKT_LEN,
				RxRingPtr->MaxTransferLen);
		if (Status != XST_SUCCESS) {
			xil_printf("Rx set length %d on BD %x failed %d\r\n",
			    MAX_PKT_LEN, (UINTPTR)BdCurPtr, Status);

			return XST_FAILURE;
		}

		/* Receive BDs do not need to set anything for the control
		 * The hardware will set the SOF/EOF bits per stream status
		 */
		XAxiDma_BdSetCtrl(BdCurPtr, 0);
		XAxiDma_BdSetId(BdCurPtr, RxBufferPtr);

		RxBufferPtr += MAX_PKT_LEN;
		BdCurPtr = (XAxiDma_Bd *)XAxiDma_BdRingNext(RxRingPtr, BdCurPtr);
	}

	/* Clear the receive buffer, so we can verify data
	 */
	memset((void *)RX_BUFFER_BASE, 0, MAX_PKT_LEN);

	Status = XAxiDma_BdRingToHw(RxRingPtr, FreeBdCount,
						BdPtr);
	if (Status != XST_SUCCESS) {
		xil_printf("RX submit hw failed %d\r\n", Status);

		return XST_FAILURE;
	}

	/* Start RX DMA channel */
	Status = XAxiDma_BdRingStart(RxRingPtr);
	if (Status != XST_SUCCESS) {
		xil_printf("RX start hw failed %d\r\n", Status);

		return XST_FAILURE;
	}

	return XST_SUCCESS;
}

/*****************************************************************************/
/**
*
* This function sets up the TX channel of a DMA engine to be ready for packet
* transmission
*
* @param	AxiDmaInstPtr is the instance pointer to the DMA engine.
*
* @return	XST_SUCCESS if the setup is successful, XST_FAILURE otherwise.
*
* @note		None.
*
******************************************************************************/
static int TxSetup(XAxiDma * AxiDmaInstPtr)
{
	XAxiDma_BdRing *TxRingPtr;
	XAxiDma_Bd BdTemplate;
	int Delay = 0;
	int Coalesce = 1;
	int Status;
	u32 BdCount;

	TxRingPtr = XAxiDma_GetTxRing(&AxiDma);

	/* Disable all TX interrupts before TxBD space setup */

	XAxiDma_BdRingIntDisable(TxRingPtr, XAXIDMA_IRQ_ALL_MASK);

	/* Set TX delay and coalesce */
	XAxiDma_BdRingSetCoalesce(TxRingPtr, Coalesce, Delay);

	/* Setup TxBD space  */
	BdCount = XAxiDma_BdRingCntCalc(XAXIDMA_BD_MINIMUM_ALIGNMENT,
				TX_BD_SPACE_HIGH - TX_BD_SPACE_BASE + 1);

	Status = XAxiDma_BdRingCreate(TxRingPtr, TX_BD_SPACE_BASE,
				TX_BD_SPACE_BASE,
				XAXIDMA_BD_MINIMUM_ALIGNMENT, BdCount);
	if (Status != XST_SUCCESS) {
		xil_printf("failed create BD ring in txsetup\r\n");

		return XST_FAILURE;
	}

	/*
	 * We create an all-zero BD as the template.
	 */
	XAxiDma_BdClear(&BdTemplate);

	Status = XAxiDma_BdRingClone(TxRingPtr, &BdTemplate);
	if (Status != XST_SUCCESS) {
		xil_printf("failed bdring clone in txsetup %d\r\n", Status);

		return XST_FAILURE;
	}

	/* Start the TX channel */
	Status = XAxiDma_BdRingStart(TxRingPtr);
	if (Status != XST_SUCCESS) {
		xil_printf("failed start bdring txsetup %d\r\n", Status);

		return XST_FAILURE;
	}

	return XST_SUCCESS;
}

/*****************************************************************************/
/**
*
* This function transmits one packet non-blockingly through the DMA engine.
*
* @param	AxiDmaInstPtr points to the DMA engine instance
*
* @return	- XST_SUCCESS if the DMA accepts the packet successfully,
*		- XST_FAILURE otherwise.
*
* @note     None.
*
******************************************************************************/
static int SendPacket(XAxiDma * AxiDmaInstPtr)
{
	XAxiDma_BdRing *TxRingPtr;
	u8 *TxPacket;
	u8 Value;
	XAxiDma_Bd *BdPtr;
	int Status;
	int Index;
	static int packet_init = 0;

	TxRingPtr = XAxiDma_GetTxRing(AxiDmaInstPtr);

	if (!packet_init) {

		/* Create pattern in the packet to transmit */
		TxPacket = (u8 *) Packet;

		Value = TEST_START_VALUE;

		for(Index = 0; Index < MAX_PKT_LEN; Index ++) {
			TxPacket[Index] = Value;

			Value = (Value + 1) & 0xFF;
		}

		/* Flush the SrcBuffer before the DMA transfer, in case the Data Cache
		 * is enabled
		 */
		Xil_DCacheFlushRange((UINTPTR)TxPacket, MAX_PKT_LEN);
	#ifdef __aarch64__
		Xil_DCacheFlushRange((UINTPTR)RX_BUFFER_BASE, MAX_PKT_LEN);
	#endif

		packet_init = 1;
	}

	/* Allocate a BD */
	Status = XAxiDma_BdRingAlloc(TxRingPtr, 1, &BdPtr);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	/* Set up the BD using the information of the packet to transmit */
	Status = XAxiDma_BdSetBufAddr(BdPtr, (UINTPTR) Packet);
	if (Status != XST_SUCCESS) {
		xil_printf("Tx set buffer addr %x on BD %x failed %d\r\n",
		    (UINTPTR)Packet, (UINTPTR)BdPtr, Status);

		return XST_FAILURE;
	}

	Status = XAxiDma_BdSetLength(BdPtr, MAX_PKT_LEN,
				TxRingPtr->MaxTransferLen);
	if (Status != XST_SUCCESS) {
		xil_printf("Tx set length %d on BD %x failed %d\r\n",
		    MAX_PKT_LEN, (UINTPTR)BdPtr, Status);

		return XST_FAILURE;
	}

#if (XPAR_AXIDMA_0_SG_INCLUDE_STSCNTRL_STRM == 1)
	Status = XAxiDma_BdSetAppWord(BdPtr,
	    XAXIDMA_LAST_APPWORD, MAX_PKT_LEN);

	/* If Set app length failed, it is not fatal
	 */
	if (Status != XST_SUCCESS) {
		xil_printf("Set app word failed with %d\r\n", Status);
	}
#endif

	/* For single packet, both SOF and EOF are to be set
	 */
	// 虽然是SG模式BD链,但每提交1个BD都作为最后一个BD
	XAxiDma_BdSetCtrl(BdPtr, XAXIDMA_BD_CTRL_TXEOF_MASK |
						XAXIDMA_BD_CTRL_TXSOF_MASK);

	XAxiDma_BdSetId(BdPtr, (UINTPTR)Packet);

	/* Give the BD to DMA to kick off the transmission. */
	Status = XAxiDma_BdRingToHw(TxRingPtr, 1, BdPtr);
	if (Status != XST_SUCCESS) {
		xil_printf("to hw failed %d\r\n", Status);
		return XST_FAILURE;
	}

	return XST_SUCCESS;
}

/*****************************************************************************/
/*
*
* This function checks data buffer after the DMA transfer is finished.
*
* @param	None
*
* @return	- XST_SUCCESS if validation is successful
*		- XST_FAILURE if validation is failure.
*
* @note		None.
*
******************************************************************************/
static int CheckData(void)
{
	u8 *RxPacket;
	int Index = 0;
	u8 Value;


	RxPacket = (u8 *) RX_BUFFER_BASE;
	Value = TEST_START_VALUE;

	/* Invalidate the DestBuffer before receiving the data, in case the
	 * Data Cache is enabled
	 */
#ifndef __aarch64__
	Xil_DCacheInvalidateRange((UINTPTR)RxPacket, MAX_PKT_LEN);
#endif

	for(Index = 0; Index < MAX_PKT_LEN; Index++) {
		if (RxPacket[Index] != Value) {
			xil_printf("Data error %d: %x/%x\r\n",
			    Index, (unsigned int)RxPacket[Index],
			    (unsigned int)Value);

			return XST_FAILURE;
		}
		Value = (Value + 1) & 0xFF;
	}

	return XST_SUCCESS;
}

/*****************************************************************************/
/**
*
* This function waits until the DMA transaction is finished, checks data,
* and cleans up.
*
* @param	None
*
* @return	- XST_SUCCESS if DMA transfer is successful and data is correct,
*		- XST_FAILURE if fails.
*
* @note		None.
*
******************************************************************************/
static int CheckDmaResult(XAxiDma * AxiDmaInstPtr)
{
	XAxiDma_BdRing *TxRingPtr;
	XAxiDma_BdRing *RxRingPtr;
	XAxiDma_Bd *BdPtr;
	int ProcessedBdCount;
	int FreeBdCount;
	int Status;

	TxRingPtr = XAxiDma_GetTxRing(AxiDmaInstPtr);
	RxRingPtr = XAxiDma_GetRxRing(AxiDmaInstPtr);

	/* Wait until the one BD TX transaction is done */
	while ((ProcessedBdCount = XAxiDma_BdRingFromHw(TxRingPtr,
						       XAXIDMA_ALL_BDS,
						       &BdPtr)) == 0) {
	}

	/* Free all processed TX BDs for future transmission */
	Status = XAxiDma_BdRingFree(TxRingPtr, ProcessedBdCount, BdPtr);
	if (Status != XST_SUCCESS) {
		xil_printf("Failed to free %d tx BDs %d\r\n",
		    ProcessedBdCount, Status);
		return XST_FAILURE;
	}

	/* Wait until the data has been received by the Rx channel */
	while ((ProcessedBdCount = XAxiDma_BdRingFromHw(RxRingPtr,
						       XAXIDMA_ALL_BDS,
						       &BdPtr)) == 0) {
	}

	/* Check received data */
	if (CheckData() != XST_SUCCESS) {

		return XST_FAILURE;
	}

	/* Free all processed RX BDs for future transmission */
	Status = XAxiDma_BdRingFree(RxRingPtr, ProcessedBdCount, BdPtr);
	if (Status != XST_SUCCESS) {
		xil_printf("Failed to free %d rx BDs %d\r\n",
		    ProcessedBdCount, Status);
		return XST_FAILURE;
	}

	/* Return processed BDs to RX channel so we are ready to receive new
	 * packets:
	 *    - Allocate all free RX BDs
	 *    - Pass the BDs to RX channel
	 */
	FreeBdCount = XAxiDma_BdRingGetFreeCnt(RxRingPtr);
	Status = XAxiDma_BdRingAlloc(RxRingPtr, FreeBdCount, &BdPtr);
	if (Status != XST_SUCCESS) {
		xil_printf("bd alloc failed\r\n");
		return XST_FAILURE;
	}

	Status = XAxiDma_BdRingToHw(RxRingPtr, FreeBdCount, BdPtr);
	if (Status != XST_SUCCESS) {
		xil_printf("Submit %d rx BDs failed %d\r\n", FreeBdCount, Status);
		return XST_FAILURE;
	}

	return XST_SUCCESS;
}
```













# SG模式裸机接口工作机制








## BD(Buffer描述符)




**BD内存实体**

BD并不存放数据本身，它存放数据地址等信息，所以被称为描述符；

例程代码中，相当于是用一小块连续物理内存，存放BD数组实体，一定要物理内存。

```cpp
// BD: Buffer Descriptor
typedef u32 XAxiDma_Bd[16];

// 用法:
u32 bd1[16];
XAxiDma_Bd bd2;
// bd2也是一个和bd1同类型的整型数组
// 把一个BD作为一个整体，这样方便访问不同BD。
```


那么多个BD如何组成一个环呢？官方已经提供裸机接口了 XAxiDma_BdRingCreate()，该接口就是把多个BD连接成一个首尾相连的环形结构。官方参考例程中，Tx 和 Rx 各自都有自己独立的BdRing(比如 TxBdRing，RxBdRing)。

![[Pasted image 20260115204153.png]]



<font color=blue>BD描述符里，哪些地址必须要物理地址？哪些可以是虚拟地址？</font>

但凡需要axi-dma硬件读取或写入的，都需要是物理地址，所以这里为了简洁，直接把整个BD实例用物理内存来存放。否则你还要区分处理BD实例里哪个字段需要地址转换，哪个字段不需要地址转换等浪费时间的琐事。


<font color=blue>这里的IOMMU 和 你说的DMA是什么关系？为什么会提及到IOMMU？</font>

1、首先区分MMU和IOMMU：MMU是专门给CPU用的，IOMMU是专门给外设用的；

2、AXI-DMA 属于外设，只有在 **经过 IOMMU** 的情况下，DMA 才能使用虚拟地址。

3、MMU是CPU专属，外设主动访问某内存，是看不到MMU页表、TLB。


下面是没有IOMMU的情况：
```
CPU ------> MMU ------> DDR
DMA ------------------> DDR  (DMA or 外设只能访问物理地址)
```
下面是有IOMMU的高端Soc/PC情况：IOMMU 再把 IOVA 转成物理地址
```txt
CPU ------> MMU ------> DDR
DMA -----> IOMMU -----> DDR
```

MMU和IOMMU它们是**两套完全不同的地址空间**。


---


**BD(Buffer Descriptor)描述符字段**


BD的实体存放在RAM中，而 AXI-DMA 控制器寄存器的实体存放在控制器内部。

![[Pasted image 20260116112827.png]]


![[Pasted image 20260116112857.png]]


---


**RingChanBase** 表示每个传输方向的寄存器基地址，比如 TxRingPtr->ChanBase 或者 RxRingPtr->ChanBase。关于寄存器地址和字段的代码定义，都可以在 xaxidma_hw.h 这个头文件里找到。注意，这里的传输方向不仅仅是内存到设备，在常规DMA应用中，还有内存到内存、内存到设备、设备到内存、设备到设备。

```cpp
TxBdRing.ChanBase = XPAR_AXI_DMA_0_BASEADDR + 0x00; //MM2S
RxBdRing.ChanBase = XPAR_AXI_DMA_0_BASEADDR + 0x30; //S2MM
```

![[Pasted image 20260116140309.png]]


```cpp
// 清零中断位,XAXIDMA_CR_OFFSET=0x00,XAXIDMA_IRQ_ALL_MASK=0x7000
#define XAxiDma_BdRingIntDisable(RingPtr, Mask)				\
		(XAxiDma_WriteReg((RingPtr)->ChanBase, XAXIDMA_CR_OFFSET, \
		XAxiDma_ReadReg((RingPtr)->ChanBase, XAXIDMA_CR_OFFSET) & \
			~((Mask) & XAXIDMA_IRQ_ALL_MASK)))
```

![[Pasted image 20260116082839.png]]

---

xaxidma_bdring.h

```cpp
// Check whether a DMA channel is started, meaning the channel is not halted.
// XAXIDMA_SR_OFFSET=0x04, XAXIDMA_HALTED_MASK=0x01
#define XAxiDma_BdRingHwIsStarted(RingPtr)				\
		((XAxiDma_ReadReg((RingPtr)->ChanBase, XAXIDMA_SR_OFFSET) \
			& XAXIDMA_HALTED_MASK) ? FALSE : TRUE)

// Check if the current DMA channel is busy with a DMA operation.
// XAXIDMA_SR_OFFSET=0x04, XAXIDMA_IDLE_MASK=0x02
#define XAxiDma_BdRingBusy(RingPtr)					 \
		(XAxiDma_BdRingHwIsStarted(RingPtr) &&		\
		((XAxiDma_ReadReg((RingPtr)->ChanBase, XAXIDMA_SR_OFFSET) \
			& XAXIDMA_IDLE_MASK) ? FALSE : TRUE))
```

![[Pasted image 20260116093859.png]]






## BdRing(BD环形结构)


XAxiDma 把 BD Ring **明确切成 4 个软件可见的“工作组”**：

```cpp
Free group   :空闲，可分配             FreeHead, FreeCnt
Pre-work     :已分配，未提交硬件        PreHead, PreCnt
HW-work      :硬件正在处理or将要处理    HwHead, HwCnt, HwTail
Post-work    :硬件处理完，待软件回收    PostHead, PostCnt
```


如下图所示，中间大大的FIFO表示整个循环的工作都遵循FIFO原则，比如:
```cpp
	// 参考官方 XAxiDma_BdRingAlloc() 注释
	Alloc(BD1);
	Alloc(BD2);
	ToHw(BD1);
	ToHw(BD2);
```


![[Pasted image 20260317092038.png]]


图中几个操作接口分别对应着：
- XAxiDma_BdRingCreate() 用于创建空闲BD环
- XAxiDma_BdRingAlloc()、XAxiDma_BdRingUnAlloc()
- XAxiDma_BdRingToHw()
- XAxiDma_BdRingFromHw()
- XAxiDma_BdRingFree()

注意：MM2S和S2MM直接短接情况下，发给设备一个BD后，必须要有接收，否则会阻塞。


---


**研究这套接口实现细节，意义是什么？**

这套接口工作机制的场景如下图所示：蓝方无锁访问可访问的节点，红方主动提供节点给蓝方访问。


![[Pasted image 20260121162141.png]]


---

XAxiDma_BdRingAlloc
XAxiDma_BdRingToHw
XAxiDma_BdRingFromHw
XAxiDma_BdRingFree

这里的BD核心接口，基本上**都是在动BD内容**，并且正好对应4状态，**没有修改控制器寄存器**。


## XAxiDma_BdRingAlloc

![[Pasted image 20260121080546.png]]

XAxiDma_BdRingAlloc
XAxiDma_BdSetBufAddr
XAxiDma_BdSetLength
XAxiDma_BdSetCtrl
XAxiDma_BdSetId

一次完整 TX 发送流程（例子：发 3 个 BD）（RX 完全同理，只是方向反了）
XAxiDma_BdRingAlloc(3): 给我 3 个空 BD，我要填数据

```cpp
int XAxiDma_BdRingAlloc(XAxiDma_BdRing * RingPtr, int NumBd,
	XAxiDma_Bd ** BdSetPtr)
{
	/* Enough free BDs available for the request? */
	if (RingPtr->FreeCnt < NumBd) return XST_FAILURE;//Not enough BDs

	/* Set the return argument and move FreeHead forward */
	*BdSetPtr = RingPtr->FreeHead;
	XAXIDMA_RING_SEEKAHEAD(RingPtr, RingPtr->FreeHead, NumBd);
	RingPtr->FreeCnt -= NumBd;
	RingPtr->PreCnt += NumBd;
	return XST_SUCCESS;
}
```


---

## XAxiDma_BdRingToHw

![[Pasted image 20260121080433.png]]

因为 BdRingToHw 实现代码中，用到了内存屏障指令，因此这里画图说明一下smp_mb() 和 mb() 的本质区别，两者本质区别就是smp的针对多核，没smp的针对cpu与设备。

![[Pasted image 20260118092301.png]]

如上图所示，DMA不属于CPU内部器件，它属于外设，比如我们修改BD后，要提交给DMA读取，我们修改BD之后，期望后续DMA读取，那么就需要 dsb 这样的屏障指令来保证。老工程师口诀: **看到外设就用DSB, 看到多核就用DMB, 看到系统寄存器就用ISB**。


下面是 XAxiDma_BdRingToHw 内部核心代码的注释。

```cpp
int XAxiDma_BdRingToHw(XAxiDma_BdRing * RingPtr, int NumBd,
	XAxiDma_Bd * BdSetPtr)
{
	int RingIndex = RingPtr->RingIndex;

	// 一堆检查...
	
	// 读取BD的控制寄存器和状态寄存器
	CurBdPtr = BdSetPtr;
	BdCr = XAxiDma_BdGetCtrl(CurBdPtr);
	BdSts = XAxiDma_BdGetSts(CurBdPtr);
	
	// 这个循环主要就是清理目标BD里的完成字段
	for (i = 0; i < NumBd - 1; i++) {
	
		// Clear the completed status bit
		BdSts &=  ~XAXIDMA_BD_STS_COMPLETE_MASK;
		XAxiDma_BdWrite(CurBdPtr, XAXIDMA_BD_STS_OFFSET, BdSts);
		XAXIDMA_CACHE_FLUSH(CurBdPtr);
		
		CurBdPtr = (XAxiDma_Bd *)((void *)XAxiDma_BdRingNext(RingPtr, CurBdPtr));
		BdCr = XAxiDma_BdRead(CurBdPtr, XAXIDMA_BD_CTRL_LEN_OFFSET);
		BdSts = XAxiDma_BdRead(CurBdPtr, XAXIDMA_BD_STS_OFFSET);
	}
	
	// 处理最后一个BD
	BdSts &= ~XAXIDMA_BD_STS_COMPLETE_MASK;
	XAxiDma_BdWrite(CurBdPtr, XAXIDMA_BD_STS_OFFSET, BdSts);
	XAXIDMA_CACHE_FLUSH(CurBdPtr);
	DATA_SYNC;//dsb() 不加dsb会产生极其隐蔽、极难复现的数据一致性 Bug

	// PreHead += NumBd * sizeof(BD);
	// PreHead 指向的是已经 Alloc 但还没交给硬件的BD
	XAXIDMA_RING_SEEKAHEAD(RingPtr, RingPtr->PreHead, NumBd);
	RingPtr->PreCnt -= NumBd;
	RingPtr->HwTail = CurBdPtr; // 移动 HwTail 后移
	RingPtr->HwCnt += NumBd;    // 硬件待处理的BD数增加
	
	// 如果引擎已经运行
	if (RingPtr->RunState == AXIDMA_CHANNEL_NOT_HALTED) {
		if (RingPtr->IsRxChannel) {
			// 如果是RX环
			
			if (!RingIndex) {
				// 单通道情况
				
				// 把 HwTail 写入 TDESC, XAXIDMA_TDESC_OFFSET=0x10
				XAxiDma_WriteReg(RingPtr->ChanBase,
						XAXIDMA_TDESC_OFFSET, 
						(XAXIDMA_VIRT_TO_PHYS(RingPtr->HwTail) & XAXIDMA_DESC_LSB_MASK));
			} else {
				// 多通道情况,这里暂不探究
			}
		} else {
			// 如果是TX环
			
			// 把HwTail写入TDESC寄存器, XAXIDMA_TDESC_OFFSET=0x10
			XAxiDma_WriteReg(RingPtr->ChanBase,
							XAXIDMA_TDESC_OFFSET, 
							(XAXIDMA_VIRT_TO_PHYS(RingPtr->HwTail) & XAXIDMA_DESC_LSB_MASK));
		}
	}
	
	// Q: 这里往 XAXIDMA_TDESC_OFFSET 这个寄存器，不会引起访问冲突吗？
	// 因为引擎已经启动了，如果和软件访问之间没有竞态保护，万一这里在修改该寄存器的时候，硬件那边同时也在读，这怎么办？
	// A: 不会有访问冲突，也不需要软件加锁。
    // 竞态只会发生在“双方都要修改的状态”上，只要寄存器是“单写者”的，它天然就是无竞态的。
    // 为什么“单写者”= 天然无竞态？
    // 竞态的本质（从硬件角度）: 两个或多个时序源，对同一“可变状态”做写操作
    // 而 TAILDESC 只有 AXI-Lite（软件）在写，不存在 write-write 冲突。
}
```



---

## XAxiDma_BdRingFromHw

![[Pasted image 20260121080247.png]]


```cpp
XAxiDma_BdSetCtrl(BdPtr, 
	XAXIDMA_BD_CTRL_TXEOF_MASK | XAXIDMA_BD_CTRL_TXSOF_MASK);
```

XAxiDma_BdRingBusy
XAxiDma_BdRingFromHw

XAxiDma_BdRingFromHw 其实就是从 HwHead 开始遍历每个BD，检查BD完成状态和EOF标志位，根据EOF标志位来判断一个完整 packet 是否完成，如果没有检测到标志位，则表明一个 packet 没完成，所以前面交给硬件之前，肯定设置了EOF标志位(XAxiDma_BdSetCtrl)。

```cpp
// 作为调用者:
// ProcessedBdCount = XAxiDma_BdRingFromHw(TxRingPtr, XAXIDMA_ALL_BDS, &BdPtr);
// XAxiDma_BdRingFree(TxRingPtr, ProcessedBdCount, BdPtr);
// XAXIDMA_ALL_BDS=0x0FFF_FFFF

int XAxiDma_BdRingFromHw(XAxiDma_BdRing * RingPtr, int BdLimit,
			     XAxiDma_Bd ** BdSetPtr)
{
	CurBdPtr = RingPtr->HwHead;
	BdCount = 0;
	BdPartialCount = 0;
	
	// 各种检查...
	
    // 开始搜寻硬件已经完成传输的BD
	while (BdCount < BdLimit) {
		/* Read the status */
		XAXIDMA_CACHE_INVALIDATE(CurBdPtr);
		BdSts = XAxiDma_BdRead(CurBdPtr, XAXIDMA_BD_STS_OFFSET);
		BdCr = XAxiDma_BdRead(CurBdPtr, XAXIDMA_BD_CTRL_LEN_OFFSET);

		// 如果当前BD没有完成,则表明其后续的也没完成
		if (!(BdSts & XAXIDMA_BD_STS_COMPLETE_MASK)) break;

		// 识别到是已经传输完成的BD,则计数器就加1
		BdCount++;

        // 这里判断的意思是:
        // 不管是TX还是RX, 这里的EOF都表示判断一个 packet 是否完整结束（一个 packet 可能由多个 BD 组成），
        // 它们不控制 DMA 硬件行为，只影响驱动“这次 FromHw 返回多少个 BD”
		if (((!(RingPtr->IsRxChannel) && (BdCr & XAXIDMA_BD_CTRL_TXEOF_MASK)) ||
		((RingPtr->IsRxChannel) && (BdSts & XAXIDMA_BD_STS_RXEOF_MASK)))) 
        { BdPartialCount = 0; } else { BdPartialCount++; }
        // 这段代码的理解，最好是脑海中模拟一个特定小例子代值来触发边界效果，
        // 脑袋模拟起来费劲或者不确信，就可以实际跑起来验证脑袋里的逻辑推理。

        // 比如我之前 ToHw(5) 提交了5个BD用于传输一个packet，且给最后一个BD标记了EOF，
        // 硬件按照顺序进行传输: 0, 1, 2, 3, 4
        // 当硬件传输完3个，还有2个没传输完成，
        // 此时该循环内，BdCount 和 BdPartialCount 的值都是3，
        // 那么下一个BD未完成跳出循环后，两个值相减后变成0，那么最终 FromHw 返回0个BD，
        // 对外表明一个完整 packet 还没传完。
        // 如果最后一个BD没有被设置 EOF 标志位，那么 BdPartialCount 恒定为0

        
        // 如果这个BD是TX的，那么就看它的控制字段，如果是RX的，就看它的状态字段。
        // 留意 MM2S BD 描述符中，MM2S_CONTROL 寄存器的 TXSOF 和 TXEOF 字段，它是由软件这边在传输初期设置，
        // 同理 S2MM BD 描述符中，也有相关字段，
        // 这两个字段用于标记一个 packet 的开始和结束，
        // 比如 TXSOF=1，表明该BD是这个帧的第一个BD；比如 TXEOF=1，表明该BD是这个帧的最后一个BD。
        // 这两个字段在实际工程应用中可以配合逻辑实现业务逻辑定制，但在开发板标准测试 stream-fifo 例子中不受重视。


		/* Reached the end of the work group */
        // 可以理解为硬件已经完成到尾部了，没有新的待传输BD了
		if (CurBdPtr == RingPtr->HwTail) break;

		/* Move on to the next BD in work group */
		CurBdPtr = (XAxiDma_Bd *)((void *)XAxiDma_BdRingNext(RingPtr, CurBdPtr));
	}

	// 如果设置了EOF状态字并且一个packet完整传完，那么就会返回 BdCount, 否则返回0
	BdCount -= BdPartialCount;

	/* If BdCount is non-zero then BDs were found to return. Set return
	 * parameters, update pointers and counters, return success
	 */
	if (BdCount) {
		*BdSetPtr = RingPtr->HwHead;
		if (!RingPtr->Cyclic) {
			RingPtr->HwCnt -= BdCount; // 表示硬件待处理的减少了
			RingPtr->PostCnt += BdCount;// 表示软件待Free的增加了
		}
        // HwHead 向后跳过这几格
		XAXIDMA_RING_SEEKAHEAD(RingPtr, RingPtr->HwHead, BdCount);
		return BdCount;
	}
	else {
		*BdSetPtr = (XAxiDma_Bd *)NULL;
		return 0;
	}
}
```


三、为什么要“数 packet”，而不是“数 BD”

AXI DMA 的一个关键事实
> **一个 packet 可能由多个 BD 组成**

例如：

|BD|BufLen|SOF|EOF|
|---|---|---|---|
|BD0|4 KB|1|0|
|BD1|4 KB|0|0|
|BD2|1 KB|0|1|

这 **3 个 BD = 1 个 packet**
相当于上次 ToHw 之前，根据实际字节数构建了3个BD。

<font color=blue>为什么 FromHw 必须是 packet 粒度，而不是 BD 粒度？如果我想“无视 packet，按 BD 返回”，该怎么改驱动？</font>

因为BD 的存在，只是因为不能保证连续物理内存，需要 scatter-gather，所以 packet  =  BD0 + BD1 + BD2 + ... + BDn。所以 FromHw 的职责是告诉你："哪些 packet 已经完整、安全地可交给上层了"。这种应用场景非常普遍，比如不定长度的协议帧，因为帧的大小不是固定的多少字节，而是根据实际的业务需求可能会变动，比如2K分辨率的视频帧数据，和4K分辨率的视频帧数据，它们按照帧协议都是完整的一帧，但是帧大小不同。所以这里的 packet 就相当于帧，FromHw 以帧为单位返回。再比如一些特殊的网络控制协议，命令帧和数据帧用的是不同大小规格的帧。

这种没法用固定大小来确定帧大小的情况，只能根据现场的实际数据大小，拆分成多个BD，比如前面BD都是承载512字节数据，最后一个不一定有512字节。这也顺便描述了 Stream 这种概念的应用场景，因为 Stream 没有大小的概念，从逻辑角度就是它只识别 TLAST 信号，比如 TLAST 被拉高，表示一个 packet 结束。





---

## XAxiDma_BdRingFree

![[Pasted image 20260121080100.png]]


```cpp
// 调用者:
// TxedCnt = XAxiDma_BdRingFromHw(TxRingPtr, XAXIDMA_ALL_BDS, &BdPtr);
// XAxiDma_BdRingFree(TxRingPtr, TxedCnt, BdPtr);

int XAxiDma_BdRingFree(XAxiDma_BdRing * RingPtr, int NumBd,
		      XAxiDma_Bd * BdSetPtr)
{
	if (NumBd < 0) return XST_INVALID_PARAM;
	if (NumBd == 0) return XST_SUCCESS;

	/* Make sure we are in sync with XAxiDma_BdRingFromHw() */
	// 必须和XAxiDma_BdRingFromHw配对且同步使用
	if ((RingPtr->PostCnt < NumBd) || (RingPtr->PostHead != BdSetPtr)) 
		return XST_DMA_SG_LIST_ERROR;

	/* Update pointers and counters */
	RingPtr->FreeCnt += NumBd;
	RingPtr->PostCnt -= NumBd;
	
	// 比如 NumBd=2, 就向后跳2格, 如果到末尾格子了, 就回环跳
	XAXIDMA_RING_SEEKAHEAD(RingPtr, RingPtr->PostHead, NumBd)
	{
		UINTPTR Addr = (UINTPTR)(void *)(BdPtr);
		Addr += ((RingPtr)->Separation * (NumBd));
		if ((Addr > (RingPtr)->LastBdAddr) || ((UINTPTR)(BdPtr) > Addr))
			Addr -= (RingPtr)->Length;
		(BdPtr) = (XAxiDma_Bd*)(void *)Addr;
	}

	return XST_SUCCESS;
}
```







## XAxiDma_BdRingCreate


XAxiDma_BdRingAlloc
XAxiDma_BdRingToHw
XAxiDma_BdRingFromHw
XAxiDma_BdRingFree

前面的BD核心接口，基本上**都是在动BD内容**，**没有动控制器寄存器**，并且正好对应4状态。

而这里的接口开始要动控制器寄存器了，要真真切切地控制引擎启停等等行为了。

![[Pasted image 20260121161303.png]]


调用 Create 之前，需要准备一些参数：
```cpp
	XAxiDma_GetTxRing(&AxiDma);
	XAxiDma_BdRingIntDisable(...);  // 先屏蔽中断
	XAxiDma_BdRingSetCoalesce(...); // 设置集束中断和包空闲延时
	XAxiDma_BdRingCntCalc(...);     // 这个环一共需要几个BD
	
	// 最后开始Create
	XAxiDma_BdRingCreate(...);
```

![[Pasted image 20260121160637.png]]




```cpp
// TxRingPtr = (&((InstancePtr)->TxBdRing))
// Tx有他自己的Ring实例，同理Rx也是。
XAxiDma_GetTxRing(&AxiDma);

// XAXIDMA_IRQ_ALL_MASK=0x7000 (屏蔽3个中断:Dly,Err,IOC)
// RingPtr->ChanBase + XAXIDMA_CR_OFFSET，清零模块内的所有中断比特位。
XAxiDma_BdRingIntDisable(TxRingPtr, XAXIDMA_IRQ_ALL_MASK);

// 设置批量中断和包空闲延时, 1个Packet有几个BD, 批量中断就设置几
// Coalesce=1, 这里设置为1; Delay=0,无需包空闲延时
// 取值范围: Coalesce={1,255}  Delay={0~255}
// 比如Coalesce设置为6，那么DMA硬件每当传输完6个BD后就会发送一个中断，该参数主要减少中断次数从而减轻CPU压力。
// 比如Timer=16，表示当传输完一个BD之后，在传输下一个BD之前，这个区间的空闲时间，当硬件传输完之后，就会启动内部计时器，当计时器数值超过16，会触发一个中断，用来告知用户，我DMA硬件以及很久没接到传输任务了，该功能可以用来检测最后一个BD传输完毕，完毕后就会导致超时，表示整个数据传输完毕了。
XAxiDma_BdRingSetCoalesce(TxRingPtr, Coalesce, Delay);

// Alignment=64, Bytes=4096
// 表示存放BD的内存空间总大小为4KB, BD与BD之间按照64字节对齐(能被64整除)
XAxiDma_BdRingCntCalc(64, 4096);
XAxiDma_BdRingCreate(TxRingPtr, TxBdBase, TxBdBase, 64, BdCount);
XAxiDma_BdClear(&BdTemplate);
XAxiDma_BdRingClone(TxRingPtr, &BdTemplate);
```


**XAxiDma_BdRingCntCalc**(Alignment, Bytes)
可以直接简单理解为 Bytes/Alignment，实际代码使用位运算来处理的。
(uint32_t)((Bytes)/((sizeof(XAxiDma_Bd)+((Alignment)-1))&~((Alignment)-1)))
为什么这样计算而不直接用除法？
因为这样更健壮,比如后续驱动升级，BD大小变成80字节了：
(1) 80 + 63 = 143 = 0x8F
(2) 64 - 1 = 63 = 0x3F        ~(0x3F) = 0xC0
(3) 0x8F & 0xC0 = 0x80 = 128
原始 80 字节的 BD，按 64 字节对齐后，**每个 BD 实际占 128 字节**

**XAxiDma_BdRingCreate**(TxRingPtr, TxBdBase, TxBdBase, BdAlign{64}, BdCount);
**XAxiDma_BdRingCreate**(RingPtr, PhysAddr, VirtAddr, Alignment, BdCount)

```cpp
XAxiDma_BdRingCreate
	RingPtr->Separation=64; 计算BD之间的间隔字节数
	
	清空所有BD内存垃圾数据
	
	连接每个BD的Next字段: XAXIDMA_BD_NDESC_OFFSET
	
	初始化BD环的一些管理成员: FreeHead, FreeCnt 等等
```




下面是详细的关键代码注释，用于学习分析，不可用于直接运行：

```cpp
u32 XAxiDma_BdRingCreate(XAxiDma_BdRing *RingPtr, UINTPTR PhysAddr,
			UINTPTR VirtAddr, u32 Alignment, int BdCount)
{
	int i;
	UINTPTR BdVirtAddr;
	UINTPTR BdPhysAddr;


	// 这些必须置0, 防止垃圾值导致后续其他 Ring 操作开始胡乱工作
	RingPtr->AllCnt = 0;
	RingPtr->FreeCnt = 0;
	RingPtr->HwCnt = 0;
	RingPtr->PreCnt = 0;
	RingPtr->PostCnt = 0;
	RingPtr->Cyclic = 0;


	// 计算出每个BD之间的间隔, IP手册规定需满足规定字节对齐
	RingPtr->Separation = (sizeof(XAxiDma_Bd) + (Alignment - 1)) & ~(Alignment - 1);
 

	/* Initial ring setup:
	 *  - Clear the entire space
	 *  - Setup each BD's next pointer with the physical address of the
	 *    next BD
	 *  - Put hardware information in each BD
	 */
	memset((void *) VirtAddr, 0, (RingPtr->Separation * BdCount));
    xil_printf("%s():%d: RingPtr->Separation = %d\r\n", __func__, __LINE__, RingPtr->Separation);
    xil_printf("%s():%d: BdCount = %d\r\n", __func__, __LINE__, BdCount);

	BdVirtAddr = VirtAddr;
	BdPhysAddr = PhysAddr + RingPtr->Separation;
	for (i = 1; i < BdCount; i++) { 
        // BdCount=64, i=1~63, 最后一个BD用来首尾相连

        // 把下一个BD地址写入到NDESC寄存器
		XAxiDma_BdWrite(BdVirtAddr, XAXIDMA_BD_NDESC_OFFSET, (BdPhysAddr & XAXIDMA_DESC_LSB_MASK));
		XAxiDma_BdWrite(BdVirtAddr, XAXIDMA_BD_NDESC_MSB_OFFSET, UPPER_32_BITS(BdPhysAddr));
        xil_printf("%s():%d: BdWrite(BdVirtAddr=0x%x) = 0x%x\r\n", __func__, __LINE__, BdVirtAddr, BdPhysAddr);

        // 填充其他硬件配置信息
		XAxiDma_BdWrite(BdVirtAddr, XAXIDMA_BD_HAS_STSCNTRL_OFFSET, (u32)RingPtr->HasStsCntrlStrm);
		XAxiDma_BdWrite(BdVirtAddr, XAXIDMA_BD_HAS_DRE_OFFSET, (((u32)(RingPtr->HasDRE)) << XAXIDMA_BD_HAS_DRE_SHIFT) | RingPtr->DataWidth);

        // 确保立即写入BD内存; 然后跳到下一个BD
		XAXIDMA_CACHE_FLUSH(BdVirtAddr);
		BdVirtAddr += RingPtr->Separation; // += 64
		BdPhysAddr += RingPtr->Separation; // += 64
	}

	// 填充最后一个BD, 让它指向第一个BD
	XAxiDma_BdWrite(BdVirtAddr, XAXIDMA_BD_NDESC_OFFSET, (PhysAddr & XAXIDMA_DESC_LSB_MASK));
	XAxiDma_BdWrite(BdVirtAddr, XAXIDMA_BD_NDESC_MSB_OFFSET, UPPER_32_BITS(PhysAddr));
    xil_printf("%s():%d: BdWrite(BdVirtAddr=0x%x) = 0x%x\r\n", __func__, __LINE__, BdVirtAddr, PhysAddr);

	// 填充其他硬件配置信息
	XAxiDma_BdWrite(BdVirtAddr, XAXIDMA_BD_HAS_STSCNTRL_OFFSET, (u32)RingPtr->HasStsCntrlStrm);
	XAxiDma_BdWrite(BdVirtAddr, XAXIDMA_BD_HAS_DRE_OFFSET, (((u32)(RingPtr->HasDRE)) << XAXIDMA_BD_HAS_DRE_SHIFT) | RingPtr->DataWidth);

    // XAxiDma_BdRingCreate():373: RingPtr->Separation = 64
    // XAxiDma_BdRingCreate():374: BdCount = 64
    // XAxiDma_BdRingCreate():384: BdWrite(BdVirtAddr=0x1000000) = 0x1000040
    // XAxiDma_BdRingCreate():384: BdWrite(BdVirtAddr=0x1000040) = 0x1000080
    // XAxiDma_BdRingCreate():384: BdWrite(BdVirtAddr=0x1000080) = 0x10000C0
    // XAxiDma_BdRingCreate():384: BdWrite(BdVirtAddr=0x10000C0) = 0x1000100
    // XAxiDma_BdRingCreate():384: BdWrite(BdVirtAddr=0x1000100) = 0x1000140
    // XAxiDma_BdRingCreate():384: BdWrite(BdVirtAddr=0x1000140) = 0x1000180
    // ...
    // XAxiDma_BdRingCreate():384: BdWrite(BdVirtAddr=0x1000F00) = 0x1000F40
    // XAxiDma_BdRingCreate():384: BdWrite(BdVirtAddr=0x1000F40) = 0x1000F80
    // XAxiDma_BdRingCreate():384: BdWrite(BdVirtAddr=0x1000F80) = 0x1000FC0
    // XAxiDma_BdRingCreate():397: BdWrite(BdVirtAddr=0x1000FC0) = 0x1000000


	/* Setup and initialize pointers and counters */
	RingPtr->RunState = AXIDMA_CHANNEL_HALTED;
	RingPtr->FirstBdAddr = VirtAddr;
	RingPtr->FirstBdPhysAddr = PhysAddr;
	RingPtr->LastBdAddr = BdVirtAddr;
	RingPtr->Length = RingPtr->LastBdAddr - RingPtr->FirstBdAddr +
		RingPtr->Separation;
	RingPtr->AllCnt = BdCount;
	RingPtr->FreeCnt = BdCount;
	RingPtr->FreeHead = (XAxiDma_Bd *) VirtAddr;
	RingPtr->PreHead = (XAxiDma_Bd *) VirtAddr;
	RingPtr->HwHead = (XAxiDma_Bd *) VirtAddr;
	RingPtr->HwTail = (XAxiDma_Bd *) VirtAddr;
	RingPtr->PostHead = (XAxiDma_Bd *) VirtAddr;
	RingPtr->BdaRestart = (XAxiDma_Bd *) VirtAddr;
	RingPtr->CyclicBd = (XAxiDma_Bd *) malloc(sizeof(XAxiDma_Bd));

    // 打印 RingPtr 上面这些成员值, %16s = 0x%x 字符对齐
    xil_printf("%s():%d: ================================================\r\n", __func__, __LINE__);
    xil_printf("%s():%d: RingPtr->FirstBdAddr = 0x%x\r\n", __func__, __LINE__, RingPtr->FirstBdAddr);
    xil_printf("%s():%d: RingPtr->FirstBdPhysAddr = 0x%x\r\n", __func__, __LINE__, RingPtr->FirstBdPhysAddr);
    xil_printf("%s():%d: RingPtr->LastBdAddr = 0x%x\r\n", __func__, __LINE__, RingPtr->LastBdAddr);
    xil_printf("%s():%d: RingPtr->Length = 0x%x\r\n", __func__, __LINE__, RingPtr->Length);
    xil_printf("%s():%d: RingPtr->AllCnt = %d\r\n", __func__, __LINE__, RingPtr->AllCnt);
    xil_printf("%s():%d: RingPtr->FreeCnt = %d\r\n", __func__, __LINE__, RingPtr->FreeCnt);
    xil_printf("%s():%d: RingPtr->FreeHead = 0x%x\r\n", __func__, __LINE__, (UINTPTR)RingPtr->FreeHead);
    xil_printf("%s():%d: RingPtr->PreHead = 0x%x\r\n", __func__, __LINE__, (UINTPTR)RingPtr->PreHead);
    xil_printf("%s():%d: RingPtr->HwHead = 0x%x\r\n", __func__, __LINE__, (UINTPTR)RingPtr->HwHead);
    xil_printf("%s():%d: RingPtr->HwTail = 0x%x\r\n", __func__, __LINE__, (UINTPTR)RingPtr->HwTail);
    xil_printf("%s():%d: RingPtr->PostHead = 0x%x\r\n", __func__, __LINE__, (UINTPTR)RingPtr->PostHead);
    xil_printf("%s():%d: RingPtr->BdaRestart = 0x%x\r\n", __func__, __LINE__, (UINTPTR)RingPtr->BdaRestart);

    // XAxiDma_BdRingCreate():442: ================================================
    // XAxiDma_BdRingCreate():443: RingPtr->FirstBdAddr = 0x1000000
    // XAxiDma_BdRingCreate():444: RingPtr->FirstBdPhysAddr = 0x1000000
    // XAxiDma_BdRingCreate():445: RingPtr->LastBdAddr = 0x1000FC0
    // XAxiDma_BdRingCreate():446: RingPtr->Length = 0x1000
    // XAxiDma_BdRingCreate():447: RingPtr->AllCnt = 64
    // XAxiDma_BdRingCreate():448: RingPtr->FreeCnt = 64
    // XAxiDma_BdRingCreate():449: RingPtr->FreeHead = 0x1000000
    // XAxiDma_BdRingCreate():450: RingPtr->PreHead = 0x1000000
    // XAxiDma_BdRingCreate():451: RingPtr->HwHead = 0x1000000
    // XAxiDma_BdRingCreate():452: RingPtr->HwTail = 0x1000000
    // XAxiDma_BdRingCreate():453: RingPtr->PostHead = 0x1000000
    // XAxiDma_BdRingCreate():454: RingPtr->BdaRestart = 0x1000000

	return XST_SUCCESS;
}
```



## XAxiDma_BdRingStart



经过实验验证表明，无论是先提交(ToHw)再开始(Start)，还是先开始再提交，都能让 axi-dma 正常工作起来。TX 和 RX 都是这样的。

比如 XAxiDma_BdRingStart(TxRingPtr)，它让引擎开始工作，
引擎启动后，会看看有没有待传输的BD数据，如果有则引擎开始执行传输动作，
如果只是调用该接口开始，但是没有给其具体的待传输BD，其也不会执行传输动作。

AXI DMA **不是 CPU**，它只会：看寄存器 → 取 BD → 执行 → 更新状态

CDR 和 TDR —— Current Desc Register、Tail Desc Register


<font color=blue>没有ToHw操作，那DMA硬件那边怎么知道有没有活干？</font>

DMA 硬件完全不知道软件里“有没有 BD”
它只认三样东西：
- **当前 BD 指针（CURDESC）**
- **Tail BD 指针（TAILDESC）**
- **Run/Stop 位**
而 **`XAxiDma_BdRingToHw()`** 的本质就是：**把 “有活干” 这个事实，用寄存器告诉 DMA 硬件**


从硬件 RTL 的角度，逻辑可以抽象成这样：
```cpp
if (RUN == 1) {
    if (CURDESC != 0 && TAILDESC != 0) {
        if (CURDESC != TAILDESC) {
            start_fetch_bd();
        }
    }
}
```


为什么 AXI DMA 要这么设计？（设计动机）
这是为了支持：SG 场景下**动态投喂 BD**，DMA 已在运行时，CPU 继续追加任务



![[Pasted image 20260121092919.png]]


![[Pasted image 20260121100628.png]]

![[Pasted image 20260121153549.png]]

1、核心两大步，第一步是设置 CDESC 寄存器，第二步是写开始位。

```cpp
XAxiDma_BdRingStart
	XAxiDma_UpdateBdRingCDesc
		如果还没启动,就填充 XAXIDMA_CDESC_OFFSET
		(区分TX or RX, 以及单通道 or 多通道)
		如果启动了,直接返回
	
	XAxiDma_StartBdRingHw
		设置启动字段
		设置Tail寄存器
```


```cpp
int XAxiDma_BdRingStart(XAxiDma_BdRing * RingPtr)
{
	// CDesc: Current Descriptor
	XAxiDma_UpdateBdRingCDesc(RingPtr);
	
	// 启动硬件传输
	XAxiDma_StartBdRingHw(RingPtr);
}
```



```cpp
int XAxiDma_UpdateBdRingCDesc(XAxiDma_BdRing* RingPtr)
{
	int RingIndex = RingPtr->RingIndex;

	// 如果模块已经启动了,直接返回
	if (RingPtr->RunState == AXIDMA_CHANNEL_NOT_HALTED)
		return XST_SUCCESS;
	
	if (!XAxiDma_BdRingHwIsStarted(RingPtr)) {
		
		RegBase = RingPtr->ChanBase;
		BdPtr = (UINTPTR)(void *)(RingPtr->BdaRestart);
		
		if (!XAxiDma_BdHwCompleted(BdPtr)) {
			
			if (RingPtr->IsRxChannel) {
				// Rx Channel

				if (!RingIndex) {
					// 如果没有开启多通道
					XAxiDma_WriteReg(RegBase,
							 XAXIDMA_CDESC_OFFSET,
							 (XAXIDMA_VIRT_TO_PHYS(BdPtr) & XAXIDMA_DESC_LSB_MASK));
				} else {
					// 如果开启了多通道支持
					XAxiDma_WriteReg(RegBase,
					(XAXIDMA_RX_CDESC0_OFFSET +
					(RingIndex - 1) * XAXIDMA_RX_NDESC_OFFSET),
					(XAXIDMA_VIRT_TO_PHYS(BdPtr) & XAXIDMA_DESC_LSB_MASK));
				}
			} else {
				// Tx Channel 
				XAxiDma_WriteReg(RegBase,
						 XAXIDMA_CDESC_OFFSET,
						 (XAXIDMA_VIRT_TO_PHYS(BdPtr) & XAXIDMA_DESC_LSB_MASK));
			}
			
		} else {
			// 如果当前BD已经完成硬件传输
			
			// 遍历找到一个未完成传输的BD
			while (XAxiDma_BdHwCompleted(BdPtr)) {
				
				BdPtr = XAxiDma_BdRingNext(RingPtr, BdPtr);
				
				if ((UINTPTR)BdPtr == (UINTPTR) RingPtr->BdaRestart)
					return XST_DMA_ERROR;//no valid cdesc
				
				// 找到一个未完成传输的BD
				if (!XAxiDma_BdHwCompleted(BdPtr)) {
					
					if (RingPtr->IsRxChannel) {
						
						// 如果是单通道模式
						if (!RingIndex) {
							XAxiDma_WriteReg(RegBase,
								XAXIDMA_CDESC_OFFSET,
								(XAXIDMA_VIRT_TO_PHYS(BdPtr) & XAXIDMA_DESC_LSB_MASK));
						} else {
							// 如果开启了多通道支持
							
							XAxiDma_WriteReg(RegBase,
								(XAXIDMA_RX_CDESC0_OFFSET +
								(RingIndex - 1) * XAXIDMA_RX_NDESC_OFFSET),
								(XAXIDMA_VIRT_TO_PHYS(BdPtr) & XAXIDMA_DESC_LSB_MASK));
						}
					} else {
						// TX Channel
						
						XAxiDma_WriteReg(RegBase,
								XAXIDMA_CDESC_OFFSET,
								(XAXIDMA_VIRT_TO_PHYS(BdPtr) & XAXIDMA_DESC_LSB_MASK));
					}
					
					break;
				}
			}
		}
	}
}

int XAxiDma_StartBdRingHw(XAxiDma_BdRing * RingPtr)
{
	int RingIndex = RingPtr->RingIndex;

	// 如果没有启动, 则设置启动字段
	if (!XAxiDma_BdRingHwIsStarted(RingPtr)) {
		RegBase = RingPtr->ChanBase;
		XAxiDma_WriteReg(RegBase, XAXIDMA_CR_OFFSET,
			XAxiDma_ReadReg(RegBase, XAXIDMA_CR_OFFSET)
			| XAXIDMA_CR_RUNSTOP_MASK);
	}

	if (XAxiDma_BdRingHwIsStarted(RingPtr)) {
		RingPtr->RunState = AXIDMA_CHANNEL_NOT_HALTED;
		
		if (RingPtr->HwCnt > 0) {
			
			XAXIDMA_CACHE_INVALIDATE(RingPtr->HwTail);
			
			// 如果是是循环模式
			if (RingPtr->Cyclic) {
				XAxiDma_WriteReg(RingPtr->ChanBase,
						 XAXIDMA_TDESC_OFFSET,
						 (u32)XAXIDMA_VIRT_TO_PHYS(RingPtr->CyclicBd));
				return XST_SUCCESS;
			}
			
			// 如果 HwTail 没完成
			if ((XAxiDma_BdRead(RingPtr->HwTail,
				    XAXIDMA_BD_STS_OFFSET) &
				XAXIDMA_BD_STS_COMPLETE_MASK) == 0) {
			
				if (RingPtr->IsRxChannel) {
					// Rx Channel
					
					if (!RingIndex) {
						// 如果没开启多通道支持
						XAxiDma_WriteReg(RingPtr->ChanBase,
							XAXIDMA_TDESC_OFFSET, 
							(XAXIDMA_VIRT_TO_PHYS(RingPtr->HwTail) & XAXIDMA_DESC_LSB_MASK));
					} else {
						// 如果开启多通道支持
						
						XAxiDma_WriteReg(RingPtr->ChanBase,
							(XAXIDMA_RX_TDESC0_OFFSET +
							(RingIndex - 1) * XAXIDMA_RX_NDESC_OFFSET),
							(XAXIDMA_VIRT_TO_PHYS(RingPtr->HwTail) & XAXIDMA_DESC_LSB_MASK ));
					}
				} else {
					// Tx Channel
					
					XAxiDma_WriteReg(RingPtr->ChanBase,
							XAXIDMA_TDESC_OFFSET, 
							(XAXIDMA_VIRT_TO_PHYS(RingPtr->HwTail) & XAXIDMA_DESC_LSB_MASK));
				}

			}
		}
		
		return XST_SUCCESS;
	}
	
	return XST_DMA_ERROR;
}
```


测试代码里 Each packet 其实指的是单个BD buffer，只不过测试代码简单起见，每个 Tx BD buffer 都有 SOF 和 EOF 标志位，这些标志位的设置一般在构造 Tx BD 的时候设置，这是 axi-dma 硬件决定，软件代码中 XAxiDma_BdRingFromHw 内部会进行 packet 判定，如果没有接收到完整 packet，就会返回0，只有接收到完整 packet，才会返回该 packet 包含的BD数量。而例程中接收端就不需要设置 SOF 和 EOF 标志位，因为这个标志位是由硬件和发送端的BD决定。

axi-dma手册里称为 EOP, 代码里称为EOF(Packet or Frame)，都表达的一个意思。





# SG模式Linux驱动带宽例程





## v003-纯驱动带宽验证


**1、IP核配置信息**
- zynq PL Fabric clock 频率为一路100MHz
- AXI DMA IP 核配置
	- Stream Data Width = 32bit
	- Buffer 长度寄存器位宽为24，即单个BD节点(或者单个sg节点)最多传输 16MB-1 字节；
	- 最大 Burst Size 为 16，即 16 x sizeof(int32_t)。
- 理论带宽: 100MHz x 数据宽度32bit = 3200bps = 400MB/s


纯驱动层面的带宽验证，下面是完整的设备树(pl.dtsi)
```cpp
/*
 * CAUTION: This file is automatically generated by Xilinx.
 * Version: XSCT 2018.3
 * Today is: Wed Jan 21 15:47:31 2026
 */


/ {
	amba_pl: amba_pl {
		#address-cells = <1>;
		#size-cells = <1>;
		compatible = "simple-bus";
		ranges ;

		axi_dma_0: dma@40400000 {
			#dma-cells = <1>;
			clock-names = "s_axi_lite_aclk", "m_axi_sg_aclk", "m_axi_mm2s_aclk", "m_axi_s2mm_aclk";
			clocks = <&clkc 15>, <&clkc 15>, <&clkc 15>, <&clkc 15>;
			compatible = "xlnx,axi-dma-7.1", "xlnx,axi-dma-1.00.a";
			interrupt-names = "mm2s_introut", "s2mm_introut";
			interrupt-parent = <&intc>;
			interrupts = <0 29 4 0 30 4>;
			reg = <0x40400000 0x10000>;
			xlnx,addrwidth = <0x20>;
			xlnx,include-sg ;
			xlnx,sg-length-width = <0xe>;
			dma-channel@40400000 {
				compatible = "xlnx,axi-dma-mm2s-channel";
				dma-channels = <0x1>;
				interrupts = <0 29 4>;
				xlnx,datawidth = <0x20>;
				xlnx,device-id = <0x0>;
			};
			dma-channel@40400030 {
				compatible = "xlnx,axi-dma-s2mm-channel";
				dma-channels = <0x1>;
				interrupts = <0 30 4>;
				xlnx,datawidth = <0x20>;
				xlnx,device-id = <0x1>;  // 注意设备id,默认生成的 device-id 值都是0
			};
		};


		// 引用上面的 axi_dma_0
		// 注意, 该节点一定要在 amba_pl 节点域内
		axidma_chrdev@0 {
			//compatible = "xlnx,axi-dma-iodev-1.00.a";
			compatible = "xlnx,axidma-chrdev";
			status = "okay";
			dmas = <&axi_dma_0 0
					&axi_dma_0 1>;
			dma-names = "tx_channel", "rx_channel";
		};

	};

};
```


![[Pasted image 20260323083837.png]]


下面是设备树顶层文件(zynq-ax7020.dts):
```cpp
/*
 * CAUTION: This file is automatically generated by Xilinx.
 * Version: XSCT 2018.3
 * Today is: Wed Jan 21 15:47:31 2026
 */


/dts-v1/;
#include "zynq-7000.dtsi"
#include "pl.dtsi"
#include "pcw.dtsi"
/ {
	chosen {
		// bootargs = "console=ttyPS1,115200n8 earlyprintk rootwait earlycon";
		bootargs = "console=ttyPS0,115200 root=/dev/ram rw earlyprintk";
		stdout-path = "serial0:115200n8";
	};
	aliases {
		ethernet0 = &gem0;
		i2c0 = &i2c0;
		serial0 = &uart1;
		spi0 = &qspi;
	};
	memory {
		device_type = "memory";
		reg = <0x0 0x40000000>;
	};
};
```



如下图所示，下面是设备树文件的布局和编译方法：
1、其中 Makefile 文件是内核设备树目录里的 Makefile，把其他设备树都注释了，只保留了该板子设备树的编译。
```makefile
dtb-$(CONFIG_ARCH_ZYNQ) += \
	zynq-ax7020.dtb
```

2、zynq开头的设备树源文件是设备树顶层文件，其它源文件是内核设备树目录没有的文件，其他系统级文件可以不用管，直接把内核设备树目录没有的设备树源文件补充拷贝进去即可。

3、最终编译生成 .dtb 文件，该文件在 u-boot 阶段会传递给内核。
![[Pasted image 20260309174239.png]]


![[Pasted image 20260313091945.png]]



下面是完整的驱动源代码(axidma_v003.ko):
```cpp
#include <linux/delay.h>
#include <linux/wait.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/slab.h>
#include <linux/stat.h>
#include <linux/platform_device.h>
#include <linux/device.h>
#include <linux/dmaengine.h>
#include <linux/errno.h>
#include <linux/of.h>
#include <linux/of_device.h>
#include <linux/dma-mapping.h>
#include <linux/completion.h>
#include <linux/jiffies.h>
#include <linux/ktime.h>
#include <linux/random.h>

#define DRV_MODULE_NAME "axidma"

#define TEST_BUF_SIZE        (2*1024*1024)   // 2MB
#define TEST_ITERATIONS      10
#define DMA_TIMEOUT_MS       5000

struct szsywhf_axidma_device {
    struct platform_device *pdev;
    struct dma_chan *tx_chan, *rx_chan;

    dma_addr_t tx_dma_addr;
    dma_addr_t rx_dma_addr;
    void *tx_buf;
    void *rx_buf;
    size_t buf_size;

    struct completion tx_cmp;
    struct completion rx_cmp;

    u64 total_ns;
    u64 total_bytes;
};

static int test_iterations = TEST_ITERATIONS;
static int test_buf_size = TEST_BUF_SIZE;

module_param(test_iterations, int, 0444);
module_param(test_buf_size, int, 0444);

static void tx_cb(void *param)
{
    complete(param);
}

static void rx_cb(void *param)
{
    complete(param);
}

static int verify_data(const u8 *tx, const u8 *rx, size_t len)
{
    size_t i;
    for (i = 0; i < len; i++) {
        if (tx[i] != rx[i]) {
            pr_err("mismatch at %zu: tx=0x%02x rx=0x%02x\n", i, tx[i], rx[i]);
            return -EINVAL;
        }
    }
    return 0;
}

static void fill_buf(u8 *buf, size_t len)
{
    size_t i;
    for (i = 0; i < len; i++)
        buf[i] = (i & 0xFF);
}

static int do_single_test(struct szsywhf_axidma_device *dev)
{
    struct dma_async_tx_descriptor *txd, *rxd;

    // int ret;
    // ktime_t t_start, t_end;
    // u64 ns;

    reinit_completion(&dev->tx_cmp);
    reinit_completion(&dev->rx_cmp);

    // fill_buf(dev->tx_buf, dev->buf_size);
    // memset(dev->rx_buf, 0, dev->buf_size);

    // 先提交 RX
    rxd = dmaengine_prep_slave_single(dev->rx_chan, dev->rx_dma_addr,
                                       dev->buf_size, DMA_DEV_TO_MEM,
                                       DMA_PREP_INTERRUPT | DMA_CTRL_ACK);
    if (!rxd) return -ENOMEM;
    // pr_info("buf_size = %ld\n", dev->buf_size);

    rxd->callback = rx_cb;
    rxd->callback_param = &dev->rx_cmp;
    dmaengine_submit(rxd);

    // 再提交 TX
    txd = dmaengine_prep_slave_single(dev->tx_chan, dev->tx_dma_addr,
                                       dev->buf_size, DMA_MEM_TO_DEV,
                                       DMA_PREP_INTERRUPT | DMA_CTRL_ACK);
    if (!txd) return -ENOMEM;

    txd->callback = tx_cb;
    txd->callback_param = &dev->tx_cmp;
    dmaengine_submit(txd);

    // 计时开始
    // t_start = ktime_get();
    dma_async_issue_pending(dev->rx_chan);
    dma_async_issue_pending(dev->tx_chan);

    if (!wait_for_completion_timeout(&dev->rx_cmp, msecs_to_jiffies(DMA_TIMEOUT_MS))) {
        pr_err("rx timeout\n");
        dmaengine_terminate_all(dev->rx_chan);
        return -ETIMEDOUT;
    }

    if (!wait_for_completion_timeout(&dev->tx_cmp, msecs_to_jiffies(DMA_TIMEOUT_MS))) {
        pr_err("tx timeout\n");
        dmaengine_terminate_all(dev->tx_chan);
        return -ETIMEDOUT;
    }

    // // 计时结束
    // t_end = ktime_get();
    // ns = ktime_to_ns(ktime_sub(t_end, t_start));
    // dev->total_ns += ns;
    // dev->total_bytes += dev->buf_size;

    // ret = verify_data(dev->tx_buf, dev->rx_buf, dev->buf_size);
    // if (ret)
    //     return ret;

    return 0;
}

static int run_all_tests(struct szsywhf_axidma_device *dev)
{
    int i, ret;

    ktime_t t_start, t_end;
    u64 ns;

    dev->total_ns = 0;
    dev->total_bytes = 0;
    dev->buf_size = test_buf_size;

    // 每次传输 1MB
    pr_info("start test: %d iterations, %zu bytes\n", test_iterations, dev->buf_size);

    dev->total_ns = 0;
    dev->total_bytes = 0;

    // 总共传输 10 次
    for (i = 0; i < test_iterations; i++) {

        // 每次传输 1 MB
        fill_buf(dev->tx_buf, dev->buf_size);
        memset(dev->rx_buf, 0, dev->buf_size);
        // printk("dev->buf_size = %ld\n", dev->buf_size);

        // 计时开始
        t_start = ktime_get();
        ret = do_single_test(dev);
        if (ret) {
            pr_err("test %d failed\n", i);
            return ret;
        }

        // 计时结束
        t_end = ktime_get();
        ns = ktime_to_ns(ktime_sub(t_end, t_start));
        dev->total_ns += ns;
        dev->total_bytes += dev->buf_size;

        ret = verify_data(dev->tx_buf, dev->rx_buf, dev->buf_size);
        if (ret)
            return ret;
        
        pr_info("dev->buf_size = %d, test %d ok\n", dev->buf_size, i);
    }

    if (dev->total_ns > 0) {
        u64 total_bytes = dev->total_bytes;
        u64 total_ns = dev->total_ns;

        // 下面是总耗时,内核空间不支持浮点型,所以拿到下面数据后手动计算带宽
        // 手动计算带宽公式: xBytesPS/1000000000 = total_bytes/total_ns
        // 公式中,其中 xBytesPS 就是带宽 (单位: Bytes/sec)
        pr_info("[TEST] total_bytes is %llu\n", total_bytes);
        pr_info("[TEST] total_ns is %llu\n", total_ns);
    }

    return 0;
}

static int axidma_probe(struct platform_device *pdev)
{
    struct szsywhf_axidma_device *dev;
    int ret;
    pr_info("called %s\n", __func__);

    dev = devm_kzalloc(&pdev->dev, sizeof(*dev), GFP_KERNEL);
    if (!dev) return -ENOMEM;

    dev->pdev = pdev;
    init_completion(&dev->tx_cmp);
    init_completion(&dev->rx_cmp);

    dev->tx_chan = dma_request_chan(&pdev->dev, "tx_channel");
    if (IS_ERR(dev->tx_chan)) {
        ret = PTR_ERR(dev->tx_chan);
        pr_err("get tx chan fail\n");
        return ret;
    }

    dev->rx_chan = dma_request_chan(&pdev->dev, "rx_channel");
    if (IS_ERR(dev->rx_chan)) {
        ret = PTR_ERR(dev->rx_chan);
        pr_err("get rx chan fail\n");
        dma_release_channel(dev->tx_chan);
        return ret;
    }

    dev->tx_buf = dma_alloc_coherent(&pdev->dev, test_buf_size,
                                     &dev->tx_dma_addr, GFP_KERNEL);
    if (!dev->tx_buf) {
        ret = -ENOMEM;
        goto err_rx;
    }

    dev->rx_buf = dma_alloc_coherent(&pdev->dev, test_buf_size,
                                     &dev->rx_dma_addr, GFP_KERNEL);
    if (!dev->rx_buf) {
        ret = -ENOMEM;
        goto err_txbuf;
    }

    platform_set_drvdata(pdev, dev);

    ret = run_all_tests(dev);
    if (ret)
        pr_warn("test failed\n");
    else
        pr_info("all test pass\n");

    return 0;

err_txbuf:
    dma_free_coherent(&pdev->dev, test_buf_size, dev->tx_buf, dev->tx_dma_addr);
err_rx:
    dma_release_channel(dev->rx_chan);
    dma_release_channel(dev->tx_chan);
    return ret;
}

static int axidma_remove(struct platform_device *pdev)
{
    struct szsywhf_axidma_device *dev = platform_get_drvdata(pdev);

    dmaengine_terminate_all(dev->tx_chan);
    dmaengine_terminate_all(dev->rx_chan);

    dma_release_channel(dev->tx_chan);
    dma_release_channel(dev->rx_chan);

    dma_free_coherent(&pdev->dev, test_buf_size, dev->tx_buf, dev->tx_dma_addr);
    dma_free_coherent(&pdev->dev, test_buf_size, dev->rx_buf, dev->rx_dma_addr);

    pr_info("called %s\n", __func__);
    return 0;
}

static const struct of_device_id axidma_of_ids[] = {
    { .compatible = "xlnx,axi-dma-iodev-1.00.a" },
    { .compatible = "shsy,axi-dma-iodev-1.00.a" },
    { .compatible = "szsy,axi-dma-iodev-1.00.a" },
    { .compatible = "xlnx,axidma-chrdev" },
    { /* end */ }
};
MODULE_DEVICE_TABLE(of, axidma_of_ids);

static struct platform_driver axidma_drv = {
    .driver = {
        .name = DRV_MODULE_NAME,
        .of_match_table = axidma_of_ids,
    },
    .probe = axidma_probe,
    .remove = axidma_remove,
};

module_platform_driver(axidma_drv);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("szsywhf <seafly0616@qq.com>");
MODULE_DESCRIPTION("AXI DMA driver (pseudo SG, no float, kernel safe)");
```




下面是编译驱动的 Makefile 文件：
```makefile
# obj-m += axidma_v001.o
# obj-m += axidma_v002.o
obj-m += axidma_v003.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean
```


下面是 u-boot 通过网络 tftp 在线加载镜像启动系统参考命令:
```bash
set ipaddr 192.168.1.10
set serverip 192.168.1.28
setenv bootargs 'console=ttyPS0,115200 root=/dev/ram rw earlyprintk'
#setenv bootargs 'console=ttyPS0,115200 root=/dev/ram rw earlyprintk cma=256M'

tftpboot  0x4000000  design_1_wrapper.bit
if test $? -ne 0;then tftpboot  0x4000000  design_1_wrapper.bit; fi

fpga loadb 0 0x4000000 ${filesize}
tftpboot  0x1800000  zynq-ax7020.dtb
tftpboot  0x1900000  uImage
tftpboot  0x1000000  uramdisk.image.gz
bootm  0x1900000  0x1000000  0x1800000
```


测试记录：
```cpp
zynq> insmod axidma_v006.ko txmethod="single" test_buf_size=16777216
txmethod        = single (list: sg, single, multi-single)
test_iterations = 10
test_buf_size   = 16384 KB
test_seg_size   = 1024 KB (for sg and multi-single)
start test: 10 iterations, 16777216 bytes
dev->buf_size=16384 KB, test_seg_size=1024 KB, test 0 ok
dev->buf_size=16384 KB, test_seg_size=1024 KB, test 1 ok
dev->buf_size=16384 KB, test_seg_size=1024 KB, test 2 ok
dev->buf_size=16384 KB, test_seg_size=1024 KB, test 3 ok
dev->buf_size=16384 KB, test_seg_size=1024 KB, test 4 ok
dev->buf_size=16384 KB, test_seg_size=1024 KB, test 5 ok
dev->buf_size=16384 KB, test_seg_size=1024 KB, test 6 ok
dev->buf_size=16384 KB, test_seg_size=1024 KB, test 7 ok
dev->buf_size=16384 KB, test_seg_size=1024 KB, test 8 ok
dev->buf_size=16384 KB, test_seg_size=1024 KB, test 9 ok
[TEST] total_bytes is 167772160
[TEST] total_ns is 420867056
zynq> 
>>> total = 167772160
>>> ns = 420867056
>>> print(total*1000000000/ns/1024/1024)
380.1675558088823
>>>
```




## v004-CMA连续内存分配器


**1、配置内核支持 DMA CMA**

如下图所示，可以通过相关操作查找CMA相关配置：
![[Pasted image 20260310180515.png]]

下面是给你直接筛选出来的内核相关配置：
```txt
CONFIG_CMA=y
CONFIG_CMA_AREAS=7

CONFIG_DMA_REMAP=y
CONFIG_DMA_CMA=y
CONFIG_CMA_SIZE_MBYTES=16      // 这里配置CMA总大小为16MB
CONFIG_CMA_SIZE_SEL_MBYTES=y
CONFIG_CMA_ALIGNMENT=8
```



**2、设备树无需修改**


**3、u-boot启动参数**

可以通过 u-boot 启动参数 bootargs 灵活指定cma大小：
```bash
setenv bootargs 'console=ttyPS0,115200 root=/dev/ram rw earlyprintk cma=128M'
```


**4、查看cma生效情况**

启动板载 linux 系统后，进入根文件系统后，查看内存信息:
```bash
zynq> cat /proc/meminfo | grep -i cma
CmaTotal:         131072 kB
CmaFree:          124532 kB
```


**5、驱动测试**

CMA总大小决定了 dma_alloc_coherent 所能申请的最大内存，在 zynq linux 测试中，dma_alloc_coherent 默认会从 cma 中申请内存。可以参考驱动中的 do_multi_single_test 函数，它相当于多个 single 的组合。


**6、测试结果**

```cpp
zynq> insmod axidma_v006.ko txmethod="multi-single" test_buf_size=1677
7216 test_seg_size=2097152
txmethod        = multi-single (list: sg, single, multi-single)
test_iterations = 10
test_buf_size   = 16384 KB
test_seg_size   = 2048 KB (for sg and multi-single)
start test: 10 iterations, 16777216 bytes
[TEST] total_bytes is 167772160
[TEST] total_ns is 478160847
zynq> 
>>> total = 167772160
>>> ns = 478160847
>>> print(total*1000000000/ns/1024/1024)
334.6154353787984
>>>
```


## v006-SG多节点传输


上面只能一个sg问题，关键函数接口在 dmaengine_prep_slave_sg 函数。后续将深入分析该函数在内核 dma 引擎中的因果链。

驱动文件路径: linux-xlnx-master/drivers/dma/xilinx/xilinx_dma.c

驱动函数: xilinx_dma_prep_slave_sg


把驱动源文件里的代码完整复制粘贴问 ChatGPT，它帮我解决了多个 sg 节点传输超时问题。


完整代码 axidma_v006.c：

```cpp
#include <linux/delay.h>
#include <linux/wait.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/slab.h>
#include <linux/stat.h>
#include <linux/platform_device.h>
#include <linux/device.h>
#include <linux/dmaengine.h>
#include <linux/errno.h>
#include <linux/of.h>
#include <linux/of_device.h>
#include <linux/dma-mapping.h>
#include <linux/completion.h>
#include <linux/jiffies.h>
#include <linux/ktime.h>
#include <linux/random.h>
#include <linux/scatterlist.h>

#define DRV_MODULE_NAME "axidma"

#define MAX_SEG_SIZE (1*1024*1024)
#define TEST_BUF_SIZE        (2*1024*1024)
#define TEST_ITERATIONS      10
#define DMA_TIMEOUT_MS       5000

struct szsywhf_axidma_device {
    struct platform_device *pdev;
    struct dma_chan *tx_chan, *rx_chan;

    dma_addr_t tx_dma_addr;
    dma_addr_t rx_dma_addr;
    void *tx_buf;
    void *rx_buf;
    size_t buf_size;

    struct completion tx_cmp;
    struct completion rx_cmp;

    u64 total_ns;
    u64 total_bytes;
};

static int test_iterations = TEST_ITERATIONS;
static int test_buf_size = TEST_BUF_SIZE;
static int test_seg_size = MAX_SEG_SIZE;

// 传输方式选择
static char txmethod[64] = "sg"; // "single", "multi-single", "sg"

module_param(test_iterations, int, 0444);
module_param(test_buf_size, int, 0444);
module_param(test_seg_size, int, 0444);
module_param_string(txmethod, txmethod, 64, 0644);
MODULE_PARM_DESC(txmethod, "txmethod list: single, multi-single, sg");

static void tx_cb(void *param)
{
    complete(param);
}

static void rx_cb(void *param)
{
    complete(param);
}

static int verify_data(const u8 *tx, const u8 *rx, size_t len)
{
    size_t i;
    for (i = 0; i < len; i++) {
        if (tx[i] != rx[i]) {
            pr_err("mismatch at %zu: tx=0x%02x rx=0x%02x\n", i, tx[i], rx[i]);
            return -EINVAL;
        }
    }
    return 0;
}

static void fill_buf(u8 *buf, size_t len)
{
    size_t i;
    for (i = 0; i < len; i++)
        buf[i] = (i & 0xFF);
}


static int do_sg_test(struct szsywhf_axidma_device *dev)
{
    struct dma_async_tx_descriptor *txd = NULL, *rxd = NULL;
    struct scatterlist *tx_sg_ptr = NULL, *rx_sg_ptr = NULL;
    struct scatterlist *sg;

    size_t max_seg_size = test_seg_size;
    size_t remaining_len;

    dma_addr_t curr_tx_addr, curr_rx_addr;

    int tx_segs = 0;
    int rx_segs = 0;

    int ret = 0;

    /* 初始化 completion */
    reinit_completion(&dev->tx_cmp);
    reinit_completion(&dev->rx_cmp);

    /* 计算 SG 段数 */
    tx_segs = DIV_ROUND_UP(dev->buf_size, max_seg_size);
    rx_segs = tx_segs;

    pr_info("SG split: %zu bytes -> %d segments (seg_size=%zu)\n",
            dev->buf_size, tx_segs, max_seg_size);

    /* 分配 SG 表 */
    tx_sg_ptr = kcalloc(tx_segs, sizeof(struct scatterlist), GFP_KERNEL);
    rx_sg_ptr = kcalloc(rx_segs, sizeof(struct scatterlist), GFP_KERNEL);

    if (!tx_sg_ptr || !rx_sg_ptr) {
        pr_err("Failed to allocate SG table\n");
        ret = -ENOMEM;
        goto free_sg;
    }

    sg_init_table(tx_sg_ptr, tx_segs);
    sg_init_table(rx_sg_ptr, rx_segs);

    /* ========================= */
    /* 构建 TX SG list */
    /* ========================= */

    curr_tx_addr = dev->tx_dma_addr;
    remaining_len = dev->buf_size;

    for (sg = tx_sg_ptr; remaining_len > 0; sg = sg_next(sg)) {

        size_t seg_len = min(remaining_len, max_seg_size);

        sg_dma_address(sg) = curr_tx_addr;
        sg_dma_len(sg) = seg_len;

        curr_tx_addr += seg_len;
        remaining_len -= seg_len;
    }

    /* ========================= */
    /* 构建 RX SG list */
    /* ========================= */

    curr_rx_addr = dev->rx_dma_addr;
    remaining_len = dev->buf_size;

    for (sg = rx_sg_ptr; remaining_len > 0; sg = sg_next(sg)) {

        size_t seg_len = min(remaining_len, max_seg_size);

        sg_dma_address(sg) = curr_rx_addr;
        sg_dma_len(sg) = seg_len;

        pr_debug("RX SG: addr=0x%llx len=%zu\n",
                 (unsigned long long)sg_dma_address(sg),
                 sg_dma_len(sg));

        curr_rx_addr += seg_len;
        remaining_len -= seg_len;
    }

    /* ========================= */
    /* 准备 RX DMA */
    /* ========================= */

    rxd = dmaengine_prep_slave_sg(dev->rx_chan,
                                  rx_sg_ptr,
                                  rx_segs,
                                  DMA_DEV_TO_MEM,
                                  DMA_PREP_INTERRUPT | DMA_CTRL_ACK);

    if (!rxd) {
        pr_err("RX SG prep failed\n");
        ret = -ENOMEM;
        goto free_sg;
    }

    rxd->callback = rx_cb;
    rxd->callback_param = &dev->rx_cmp;

    dmaengine_submit(rxd);

    /* ========================= */
    /* 准备 TX DMA */
    /* ========================= */

    txd = dmaengine_prep_slave_sg(dev->tx_chan,
                                  tx_sg_ptr,
                                  tx_segs,
                                  DMA_MEM_TO_DEV,
                                  DMA_PREP_INTERRUPT | DMA_CTRL_ACK);

    if (!txd) {
        pr_err("TX SG prep failed\n");
        dmaengine_terminate_all(dev->rx_chan);
        ret = -ENOMEM;
        goto free_sg;
    }

    txd->callback = tx_cb;
    txd->callback_param = &dev->tx_cmp;

    dmaengine_submit(txd);

    /* ========================= */
    /* 启动 DMA */
    /* ========================= */

    dma_async_issue_pending(dev->rx_chan);
    dma_async_issue_pending(dev->tx_chan);

    /* ========================= */
    /* 等待 TX 完成 */
    /* ========================= */

    if (!wait_for_completion_timeout(&dev->tx_cmp,
                                     msecs_to_jiffies(DMA_TIMEOUT_MS))) {

        pr_err("TX SG DMA timeout (%d segments)\n", tx_segs);

        dmaengine_terminate_all(dev->tx_chan);
        dmaengine_terminate_all(dev->rx_chan);

        ret = -ETIMEDOUT;
        goto free_sg;
    }

    /* ========================= */
    /* 等待 RX 完成 */
    /* ========================= */

    if (!wait_for_completion_timeout(&dev->rx_cmp,
                                     msecs_to_jiffies(DMA_TIMEOUT_MS))) {

        pr_err("RX SG DMA timeout (%d segments)\n", rx_segs);

        dmaengine_terminate_all(dev->rx_chan);
        dmaengine_terminate_all(dev->tx_chan);

        ret = -ETIMEDOUT;
        goto free_sg;
    }

free_sg:

    kfree(tx_sg_ptr);
    kfree(rx_sg_ptr);

    return ret;
}


static int do_multi_single_test(struct szsywhf_axidma_device *dev)
{
    struct dma_async_tx_descriptor *txd, *rxd;
    // struct dma_slave_caps caps;
    size_t max_seg_size;
    size_t remaining_len;
    dma_addr_t curr_tx_addr, curr_rx_addr;
    int ret = 0;

    // 初始化完成量
    reinit_completion(&dev->tx_cmp);
    reinit_completion(&dev->rx_cmp);

    // 获取硬件最大单段长度
    max_seg_size = test_seg_size;
    pr_info("Use single segment transfer, max size: %zu bytes\n", max_seg_size);

    // 循环单段传输（替代SG）
    curr_tx_addr = dev->tx_dma_addr;
    curr_rx_addr = dev->rx_dma_addr;
    remaining_len = dev->buf_size;

    while (remaining_len > 0 && ret == 0) {
        size_t seg_len = min(remaining_len, max_seg_size);

        // 准备RX单段传输
        rxd = dmaengine_prep_slave_single(dev->rx_chan, curr_rx_addr,
                                           seg_len, DMA_DEV_TO_MEM,
                                           DMA_PREP_INTERRUPT | DMA_CTRL_ACK);
        if (!rxd) {
            pr_err("RX single prep failed, len: %zu\n", seg_len);
            ret = -ENOMEM;
            break;
        }
        rxd->callback = rx_cb;
        rxd->callback_param = &dev->rx_cmp;
        dmaengine_submit(rxd);

        // 准备TX单段传输
        txd = dmaengine_prep_slave_single(dev->tx_chan, curr_tx_addr,
                                           seg_len, DMA_MEM_TO_DEV,
                                           DMA_PREP_INTERRUPT | DMA_CTRL_ACK);
        if (!txd) {
            pr_err("TX single prep failed, len: %zu\n", seg_len);
            dmaengine_terminate_all(dev->rx_chan);
            ret = -ENOMEM;
            break;
        }
        txd->callback = tx_cb;
        txd->callback_param = &dev->tx_cmp;
        dmaengine_submit(txd);

        // 启动传输
        dma_async_issue_pending(dev->rx_chan);
        dma_async_issue_pending(dev->tx_chan);

        // 等待RX完成
        if (!wait_for_completion_timeout(&dev->rx_cmp, msecs_to_jiffies(DMA_TIMEOUT_MS))) {
            pr_err("RX timeout, len: %zu\n", seg_len);
            dmaengine_terminate_all(dev->rx_chan);
            dmaengine_terminate_all(dev->tx_chan);
            ret = -ETIMEDOUT;
            break;
        }

        // 等待TX完成
        if (!wait_for_completion_timeout(&dev->tx_cmp, msecs_to_jiffies(DMA_TIMEOUT_MS))) {
            pr_err("TX timeout, len: %zu\n", seg_len);
            dmaengine_terminate_all(dev->tx_chan);
            ret = -ETIMEDOUT;
            break;
        }

        // 更新地址和剩余长度
        curr_tx_addr += seg_len;
        curr_rx_addr += seg_len;
        remaining_len -= seg_len;
        pr_debug("Transferred %zu bytes, remaining: %zu\n", seg_len, remaining_len);

        // 重置完成量，准备下一段
        reinit_completion(&dev->tx_cmp);
        reinit_completion(&dev->rx_cmp);
    }

    return ret;
}

static int do_single_test(struct szsywhf_axidma_device *dev)
{
    struct dma_async_tx_descriptor *txd, *rxd;

    // int ret;
    // ktime_t t_start, t_end;
    // u64 ns;

    reinit_completion(&dev->tx_cmp);
    reinit_completion(&dev->rx_cmp);

    // fill_buf(dev->tx_buf, dev->buf_size);
    // memset(dev->rx_buf, 0, dev->buf_size);

    // 先提交 RX
    rxd = dmaengine_prep_slave_single(dev->rx_chan, dev->rx_dma_addr,
                                       dev->buf_size, DMA_DEV_TO_MEM,
                                       DMA_PREP_INTERRUPT | DMA_CTRL_ACK);
    if (!rxd) return -ENOMEM;
    // pr_info("buf_size = %ld\n", dev->buf_size);

    rxd->callback = rx_cb;
    rxd->callback_param = &dev->rx_cmp;
    dmaengine_submit(rxd);

    // 再提交 TX
    txd = dmaengine_prep_slave_single(dev->tx_chan, dev->tx_dma_addr,
                                       dev->buf_size, DMA_MEM_TO_DEV,
                                       DMA_PREP_INTERRUPT | DMA_CTRL_ACK);
    if (!txd) return -ENOMEM;

    txd->callback = tx_cb;
    txd->callback_param = &dev->tx_cmp;
    dmaengine_submit(txd);

    // 计时开始
    // t_start = ktime_get();
    dma_async_issue_pending(dev->rx_chan);
    dma_async_issue_pending(dev->tx_chan);

    if (!wait_for_completion_timeout(&dev->rx_cmp, msecs_to_jiffies(DMA_TIMEOUT_MS))) {
        pr_err("rx timeout\n");
        dmaengine_terminate_all(dev->rx_chan);
        return -ETIMEDOUT;
    }

    if (!wait_for_completion_timeout(&dev->tx_cmp, msecs_to_jiffies(DMA_TIMEOUT_MS))) {
        pr_err("tx timeout\n");
        dmaengine_terminate_all(dev->tx_chan);
        return -ETIMEDOUT;
    }

    // // 计时结束
    // t_end = ktime_get();
    // ns = ktime_to_ns(ktime_sub(t_end, t_start));
    // dev->total_ns += ns;
    // dev->total_bytes += dev->buf_size;

    // ret = verify_data(dev->tx_buf, dev->rx_buf, dev->buf_size);
    // if (ret)
    //     return ret;

    return 0;
}

static int run_all_tests(struct szsywhf_axidma_device *dev)
{
    int i, ret;
	
	// 函数指针,根据用户参数选择指定传输方式
	int (*do_test_method)(struct szsywhf_axidma_device *dev);

    ktime_t t_start, t_end;
    u64 ns;
	
	
	if (strncmp(txmethod, "sg", 2)==0)
	{
		do_test_method = do_sg_test;
	} else if (strncmp(txmethod, "multi-single", 12)==0)
	{
		do_test_method = do_multi_single_test;
	} else 
	{
		do_test_method = do_single_test;
	}
	

    dev->total_ns = 0;
    dev->total_bytes = 0;
    dev->buf_size = test_buf_size;

    // 每次传输 1MB
    pr_info("start test: %d iterations, %zu bytes\n", test_iterations, dev->buf_size);

    dev->total_ns = 0;
    dev->total_bytes = 0;

    // 总共传输 10 次
    for (i = 0; i < test_iterations; i++) {

        // 每次传输 1 MB
        fill_buf(dev->tx_buf, dev->buf_size);
        memset(dev->rx_buf, 0, dev->buf_size);
        // printk("dev->buf_size = %ld\n", dev->buf_size);

        // 计时开始
        t_start = ktime_get();
        // ret = do_single_test(dev);
        // ret = do_sg_test(dev);
		ret = do_test_method(dev);
        if (ret) {
            pr_err("test %d failed\n", i);
            return ret;
        }

        // 计时结束
        t_end = ktime_get();
        ns = ktime_to_ns(ktime_sub(t_end, t_start));
        dev->total_ns += ns;
        dev->total_bytes += dev->buf_size;

        ret = verify_data(dev->tx_buf, dev->rx_buf, dev->buf_size);
        if (ret)
            return ret;
        
        pr_info("dev->buf_size=%d KB, test_seg_size=%d KB, test %d ok\n", 
            dev->buf_size/1024, test_seg_size/1024, i);
    }

    if (dev->total_ns > 0) {
        u64 total_bytes = dev->total_bytes;
        u64 total_ns = dev->total_ns;

        // 下面是总耗时,内核空间不支持浮点型,所以拿到下面数据后手动计算带宽
        // 手动计算带宽公式: xBytesPS/1000000000 = total_bytes/total_ns
        // 公式中,其中 xBytesPS 就是带宽 (单位: Bytes/sec)
        pr_info("[TEST] total_bytes is %llu\n", total_bytes);
        pr_info("[TEST] total_ns is %llu\n", total_ns);
    }

    return 0;
}

static int axidma_probe(struct platform_device *pdev)
{
	int i;
    struct szsywhf_axidma_device *dev;
    int ret;
    pr_info("called %s\n", __func__);

    dev = devm_kzalloc(&pdev->dev, sizeof(*dev), GFP_KERNEL);
    if (!dev) return -ENOMEM;

    dev->pdev = pdev;
    init_completion(&dev->tx_cmp);
    init_completion(&dev->rx_cmp);

    dev->tx_chan = dma_request_chan(&pdev->dev, "tx_channel");
    if (IS_ERR(dev->tx_chan)) {
        ret = PTR_ERR(dev->tx_chan);
        pr_err("get tx chan fail\n");
        return ret;
    }

    dev->rx_chan = dma_request_chan(&pdev->dev, "rx_channel");
    if (IS_ERR(dev->rx_chan)) {
        ret = PTR_ERR(dev->rx_chan);
        pr_err("get rx chan fail\n");
        dma_release_channel(dev->tx_chan);
        return ret;
    }

    dev->tx_buf = dma_alloc_coherent(&pdev->dev, test_buf_size,
                                     &dev->tx_dma_addr, GFP_KERNEL);
    if (!dev->tx_buf) {
        ret = -ENOMEM;
        goto err_rx;
    }

    dev->rx_buf = dma_alloc_coherent(&pdev->dev, test_buf_size,
                                     &dev->rx_dma_addr, GFP_KERNEL);
    if (!dev->rx_buf) {
        ret = -ENOMEM;
        goto err_txbuf;
    }

    platform_set_drvdata(pdev, dev);
	
	
	pr_info("txmethod        = %s (list: sg, single, multi-single)\n", txmethod);
	pr_info("test_iterations = %d\n", test_iterations);
	pr_info("test_buf_size   = %d KB\n", test_buf_size/1024);
	pr_info("test_seg_size   = %d KB (for sg and multi-single)\n\n", test_seg_size/1024);
	
	do {
		ret = run_all_tests(dev);
		if (ret)
		{
			pr_warn("test failed\n");
			break;
		}
	} while(0);

    return 0;

err_txbuf:
    dma_free_coherent(&pdev->dev, test_buf_size, dev->tx_buf, dev->tx_dma_addr);
err_rx:
    dma_release_channel(dev->rx_chan);
    dma_release_channel(dev->tx_chan);
    return ret;
}

static int axidma_remove(struct platform_device *pdev)
{
    struct szsywhf_axidma_device *dev = platform_get_drvdata(pdev);

    dmaengine_terminate_all(dev->tx_chan);
    dmaengine_terminate_all(dev->rx_chan);

    dma_release_channel(dev->tx_chan);
    dma_release_channel(dev->rx_chan);

    dma_free_coherent(&pdev->dev, test_buf_size, dev->tx_buf, dev->tx_dma_addr);
    dma_free_coherent(&pdev->dev, test_buf_size, dev->rx_buf, dev->rx_dma_addr);

    pr_info("called %s\n", __func__);
    return 0;
}

static const struct of_device_id axidma_of_ids[] = {
    { .compatible = "xlnx,axi-dma-iodev-1.00.a" },
    { .compatible = "shsy,axi-dma-iodev-1.00.a" },
    { .compatible = "szsy,axi-dma-iodev-1.00.a" },
    { .compatible = "xlnx,axidma-chrdev" },
    { /* end */ }
};
MODULE_DEVICE_TABLE(of, axidma_of_ids);

static struct platform_driver axidma_drv = {
    .driver = {
        .name = DRV_MODULE_NAME,
        .of_match_table = axidma_of_ids,
    },
    .probe = axidma_probe,
    .remove = axidma_remove,
};

module_platform_driver(axidma_drv);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("szsywhf <seafly0616@qq.com>");
MODULE_DESCRIPTION("AXI DMA driver (pseudo SG, no float, kernel safe)");
```




## 性能参数-BurstSize16

和性能相关的参数，一个是 zynq ip 核时钟配置，另一个是 axi dma ip 核的相关参数。

如下图所示， Buffer 长度寄存器，为 2的24次方，然后减1，最后等于16MB-1 字节。Max Burst Size 在这里的配置值为 16 beats，Stream Data Width 为 32 bits，所以最大突发字节数=16 x sizeof(int32_t) 字节。
![[Pasted image 20260315122749.png]]

![[Pasted image 20260315122803.png]]


测试记录：
```cpp
zynq> insmod axidma_v006.ko txmethod="sg" test_buf_size=33554432 test_seg_size=41943
04
axidma_v005: loading out-of-tree module taints kernel.
called axidma_probe
txmethod        = sg (list: sg, single, multi-single)
test_iterations = 10
test_buf_size   = 32768 KB
test_seg_size   = 4096 KB (for sg and multi-single)
start test: 10 iterations, 33554432 bytes
[TEST] total_bytes is 335544320
[TEST] total_ns is 894036639
>>> total = 335544320
>>> ns = 894036639
>>> print(total*1000000000/ns/1024/1024)
357.92716544360775
>>>


zynq> insmod axidma_v006.ko txmethod="sg" test_buf_size=16777216 test_seg_size=83886
08
called axidma_probe
txmethod        = sg (list: sg, single, multi-single)
test_iterations = 10
test_buf_size   = 16384 KB
test_seg_size   = 8192 KB (for sg and multi-single)
start test: 10 iterations, 16777216 bytes
[TEST] total_bytes is 167772160
[TEST] total_ns is 473488285
zynq> 
>>> total = 167772160
>>> ns = 473488285
>>> print(total*1000000000/ns/1024/1024)
337.91754742147424
```



## 性能参数-BurstSize128

在上面的基础上，仅仅修改了 Max Burst Size 改为 128 beats，从测试情况看，对带宽没影响。

测试记录：
```cpp
smod axidma_v006.ko txmethod="sg" test_buf_size=16777216 test_seg_size=83886
08
txmethod        = sg (list: sg, single, multi-single)
test_iterations = 10
test_buf_size   = 16384 KB
test_seg_size   = 8192 KB (for sg and multi-single)
start test: 10 iterations, 16777216 bytes
[TEST] total_bytes is 167772160
[TEST] total_ns is 472476843
zynq> 
>>> total = 167772160
>>> ns = 472733872
>>> print(total*1000000000/ns/1024/1024)
338.4568136044205
>>>
```


## 性能参数-single

同样在 include-sg 的配置下，驱动使用 single 接口来测带宽，single 比 sg 带宽更高。

```cpp
zynq> insmod axidma_v006.ko txmethod="single" test_buf_size=16777216
txmethod        = single (list: sg, single, multi-single)
test_iterations = 10
test_buf_size   = 16384 KB
test_seg_size   = 1024 KB (for sg and multi-single)
start test: 10 iterations, 16777216 bytes
[TEST] total_bytes is 167772160
[TEST] total_ns is 420850037
>>> total = 167772160
>>> ns = 420850037
>>> print(total*1000000000/ns/1024/1024)
380.1829296263077
>>>
```



## dmaengine_prep_slave_single


文件出处：linux-xlnx-5.10.0/include/linux/dmaengine.h

关键内容：无论 dmaengine_prep_slave_single() 和 dmaengine_prep_slave_sg() 其内部都是调用的 device_prep_slave_sg()，也就是底下都会把传进来的内存最终交给 device_prep_slave_sg() 切分传输，切分的依据就是 axi dma ip 核中 Buffer 最大长度限制，也就是单个BD最大数据量。
```cpp
static inline struct dma_async_tx_descriptor *dmaengine_prep_slave_single(
	struct dma_chan *chan, dma_addr_t buf, size_t len,
	enum dma_transfer_direction dir, unsigned long flags)
{
	struct scatterlist sg;
	sg_init_table(&sg, 1);
	sg_dma_address(&sg) = buf;
	sg_dma_len(&sg) = len;

	if (!chan || !chan->device || !chan->device->device_prep_slave_sg)
		return NULL;

	return chan->device->device_prep_slave_sg(chan, &sg, 1,
						  dir, flags, NULL);
}

static inline struct dma_async_tx_descriptor *dmaengine_prep_slave_sg(
	struct dma_chan *chan, struct scatterlist *sgl,	unsigned int sg_len,
	enum dma_transfer_direction dir, unsigned long flags)
{
	if (!chan || !chan->device || !chan->device->device_prep_slave_sg)
		return NULL;

	return chan->device->device_prep_slave_sg(chan, sgl, sg_len,
						  dir, flags, NULL);
}
```



👉 IRQThreshold 的含义是：“**累计完成多少个 BD 后触发一次中断**”，也就是说：
```txt
IRQThreshold = 1    → 每个 BD 完成都中断（最频繁）
IRQThreshold = 255  → 每完成 255 个 BD 才中断一次
```

其实真实情况是：
👉 DMA 引擎会一直顺着 BD 链表跑（ring / linked list）  
👉 完成一个 BD 就递增计数器  
👉 **当计数器 == IRQThreshold → 触发中断**，
然后计数器清零，继续处理后面的 BD




## Buffer长度和Burst大小


<font color=blue>
关于 zynq axi dma ip 核中的 max burst size = 16，表示单次地址请求最大传输16个beats，也就是 16 * sizeof(data-stream-width) = 16 * 4 = 64字节。以及单个BD最大传输的buffer长度，最高可以设置到 2的26次方-1=64MB-1字节，那么这个 burst size 大小一般给多少合适？它影响了哪些关键点？
</font>

BD：描述一次“逻辑传输”（软件层）
burst：底层 AXI transaction（硬件拆分）

**重点：Max Burst Size 到底影响什么？**

AXI 每个 burst 都有开销，
如果 burst 太小：`[地址][数据][地址][数据][地址][数据]`
如果 burst 大：`[地址][数据数据数据数据数据数据...]`
结论：burst 越大 → 地址开销占比越低 → 带宽利用率越高

如果 burst 太大：DMA 会“占着总线不放”，burst 越大 → 吞吐高，但“霸占总线”更严重。

**Zynq / AXI DMA 实战经验：常见推荐值（经验非常重要）**

| 场景            | 推荐 burst size     |
| ------------- | ----------------- |
| 普通应用          | **16（默认，推荐）**     |
| 高带宽（视频 / ADC） | **16 或 32（如果支持）** |
| 多 master 竞争严重 | **8 或 16**        |
| 低延迟系统         | **4 或 8**         |

**为什么默认就是 16？**

因为这是一个**工程折中最优点**：
✔ 带宽利用率已经很高  
✔ 不会严重阻塞总线  
✔ DDR 友好  
✔ FIFO 压力可控



<font color=blue>这么说来 HP Port 配置也很重要，那么如何知道 HP Port 上挂载了哪些master 呢？
</font>

Zynq 里 AXI 方向是这样的：**真正的 master 在 PL 里**
```txt
PL (master们) 
   ↓
AXI interconnect（你在 Vivado 里连的）
   ↓
HP Port（S_AXI_HP0/1/2/3）
   ↓
PS DDR 控制器
```


举个例子：AXI DMA 就是这个 HP0 上的 master。
```txt
AXI DMA (MM2S/S2MM)
        ↓
AXI Interconnect
        ↓
S_AXI_HP0
```


**一个关键认知（很多人会搞错）**
HP Port 上不是“挂多个 master”，而是：
```txt
        AXI DMA
           ↓
        VDMA
           ↓
        自定义IP（AXI Master）
           ↓
      AXI Interconnect
           ↓
         HP0
```

这时候：HP0 上“有多个 master”，但实际上是 **interconnect 在做仲裁**。

最佳实践，工程里建议：高带宽 IP 分散到不同 HP port，例如：

| IP      | HP Port |
| ------- | ------- |
| AXI DMA | HP0     |
| VDMA    | HP1     |
| 自定义加速器  | HP2     |

<font color=blue>只有一个AXI DMA IP 核，有 MM2S、S2MM、SG，它们三个通过 AXI Interconnect 连入HP0，这算不算多个Master？
</font>

✅ **算多个 AXI Master（从总线角度）**
❗ 但它们都属于**同一个 AXI DMA IP 内部的多个 Master 接口**

AXI DMA ≠ 1 个 master  
AXI DMA = 3 个 AXI master

因为每个通道都有独立的：AR/AW、burst、outstanding transaction，interconnect 需要做仲裁。

你现在的结构本质是这样：
```txt
         MM2S ─┐
         S2MM ─┼──> AXI Interconnect ──> HP0
         SG   ─┘
```


![[Pasted image 20260321161333.png]]



## 软件irq编号获取

<font color=blue>zynq axi-dma 的 mm2s 和 s2mm 有两个中断，其裸机层面的中断irq id 分别是61 和 62，但是生成设备树后，设备树中 axi-dma 的节点里，中断号分别是30 和 31。如果我为其些Linux驱动程序，当用到 request_irq 这个函数接口注册中断的时候，是用设备树中的中断号还是裸机里面的61和62？</font>

在Linux驱动里 request_irq() 注册中断时，用的一定是设备树解析出来的IRQ号。裸机里 61,62 是 PS GIC 的硬件中断号，这是 ARM GIC 的物理中断编号，裸机程序直接面对GIC硬件。而 Linux 驱动中使用的是逻辑中断号。

它们经过了如下转换：
```cpp
硬件 IRQ (61,62) ------> IRQ Domain 映射 -----> Linux逻辑IRQ(30,31)
```


在Linux驱动中，可以通过如下方式获取中断号：
```cpp
int irq_mm2s, irq_s2mm;

irq_mm2s = platform_get_irq_byname(pdev, "mm2s_introut");
irq_s2mm = platform_get_irq_byname(pdev, "s2mm_introut");

request_irq(irq_mm2s, mm2s_isr, 0, "axi-dma-mm2s", dev);
request_irq(irq_s2mm, s2mm_isr, 0, "axi-dma-s2mm", dev);

// 或者通过下面索引方式直接获取
irq_mm2s = platform_get_irq(pdev, 0);
irq_s2mm = platform_get_irq(pdev, 1);
```


<font color=blue>Linux驱动中为什么要经过 IRQ Domain 映射？也就是说Linux中为什么要有 IRQ Domain 层？直接用物理中断号不是更简便吗？</font>

因为一套Linux内核，跑在成百上千种 SoC / 板卡 / 拓扑结构上，哪怕同一个板卡上每一种中断控制器，其控制器内部 IRQ 编号规则都不一样，后续会专门探究Linux内核中的 IRQ Domian 这坨东西。



## v007-应用例程带宽测试


笔记附件：[[driver-axidma-2603220105.zip]]
- axidma_common.h    —— 驱动和应用公共头文件
- axidma_v006.c           —— 上一个版本驱动，仅作为当前版本对比参考
- axidma_v007.c           —— 当前版本驱动代码
- Makefile、build_drv.sh    —— 驱动编译规则（sh 调用 Makefile）
- app_bandwidth.c、build_app.sh    —— 应用和它的编译脚本


驱动更新：
- 相比 v006，新增了用户空间设备节点相关的代码；
- 相比 v006，提供了在用户空间测试收发带宽的代码；
- 内存用法：驱动 dma_alloc_coherent + 用户 mmap 的零拷贝数据传输


测试记录：
```log
zynq> cd /mnt/
zynq> 
zynq> ./app_bandwidth.elf 4KB 10
buffer size = 4096 bytes
iterations  = 10
mmap success: tx=0xb6eeb000 rx=0xb6eea000
[   1 / 10  ] bandwidth test 4KB SUCCESS
[   2 / 10  ] bandwidth test 4KB SUCCESS
[   3 / 10  ] bandwidth test 4KB SUCCESS
[   4 / 10  ] bandwidth test 4KB SUCCESS
[   5 / 10  ] bandwidth test 4KB SUCCESS
[   6 / 10  ] bandwidth test 4KB SUCCESS
[   7 / 10  ] bandwidth test 4KB SUCCESS
[   8 / 10  ] bandwidth test 4KB SUCCESS
[   9 / 10  ] bandwidth test 4KB SUCCESS
[  10 / 10  ] bandwidth test 4KB SUCCESS
============== [In App] Bandwidth Test ===============
    iterations    = 10
    buf_size      = 4096 Bytes
    total_us      = 812
    total_bytes   = 40960
    bandwidth     = 48.11 MB/s
============== [In Driver] Bandwidth Test ===============
    total_ns      = 765096
    total_bytes   = 40960
    bandwidth     = 51.06 MBps
zynq> 
zynq> ./app_bandwidth.elf 1MB 10
buffer size = 1048576 bytes
iterations  = 10
mmap success: tx=0xb6dcd000 rx=0xb6ccd000
[   1 / 10  ] bandwidth test 1MB SUCCESS
[   2 / 10  ] bandwidth test 1MB SUCCESS
[   3 / 10  ] bandwidth test 1MB SUCCESS
[   4 / 10  ] bandwidth test 1MB SUCCESS
[   5 / 10  ] bandwidth test 1MB SUCCESS
[   6 / 10  ] bandwidth test 1MB SUCCESS
[   7 / 10  ] bandwidth test 1MB SUCCESS
[   8 / 10  ] bandwidth test 1MB SUCCESS
[   9 / 10  ] bandwidth test 1MB SUCCESS
[  10 / 10  ] bandwidth test 1MB SUCCESS
============== [In App] Bandwidth Test ===============
    iterations    = 10
    buf_size      = 1048576 Bytes
    total_us      = 29565
    total_bytes   = 10485760
    bandwidth     = 338.24 MB/s
============== [In Driver] Bandwidth Test ===============
    total_ns      = 29510493
    total_bytes   = 10485760
    bandwidth     = 338.86 MBps
zynq> 
zynq> ./app_bandwidth.elf 2MB 10
buffer size = 2097152 bytes
iterations  = 10
mmap success: tx=0xb6ce7000 rx=0xb6ae7000
[   1 / 10  ] bandwidth test 2MB SUCCESS
[   2 / 10  ] bandwidth test 2MB SUCCESS
[   3 / 10  ] bandwidth test 2MB SUCCESS
[   4 / 10  ] bandwidth test 2MB SUCCESS
[   5 / 10  ] bandwidth test 2MB SUCCESS
[   6 / 10  ] bandwidth test 2MB SUCCESS
[   7 / 10  ] bandwidth test 2MB SUCCESS
[   8 / 10  ] bandwidth test 2MB SUCCESS
[   9 / 10  ] bandwidth test 2MB SUCCESS
[  10 / 10  ] bandwidth test 2MB SUCCESS
============== [In App] Bandwidth Test ===============
    iterations    = 10
    buf_size      = 2097152 Bytes
    total_us      = 53428
    total_bytes   = 20971520
    bandwidth     = 374.34 MB/s
============== [In Driver] Bandwidth Test ===============
    total_ns      = 53374230
    total_bytes   = 20971520
    bandwidth     = 374.71 MBps
zynq> 
zynq> 
zynq> ./app_bandwidth.elf 4MB 10
buffer size = 4194304 bytes
iterations  = 10
[main] 00000000: 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 
[main] 00000010: 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 
[main] 00000020: 20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 
[main] 00000030: 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F 
[main] 00000040: 40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F 
[main] 00000050: 50 51 52 53 54 55 56 57 58 59 5A 5B 5C 5D 5E 5F 
[main] 00000060: 60 61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F 
[main] 00000070: 70 71 72 73 74 75 76 77 78 79 7A 7B 7C 7D 7E 7F 
mmap success: tx=0xb6b8e000 rx=0xb678e000
[   1 / 10  ] bandwidth test 4MB SUCCESS
[   2 / 10  ] bandwidth test 4MB SUCCESS
[   3 / 10  ] bandwidth test 4MB SUCCESS
[   4 / 10  ] bandwidth test 4MB SUCCESS
[   5 / 10  ] bandwidth test 4MB SUCCESS
[   6 / 10  ] bandwidth test 4MB SUCCESS
[   7 / 10  ] bandwidth test 4MB SUCCESS
[   8 / 10  ] bandwidth test 4MB SUCCESS
[   9 / 10  ] bandwidth test 4MB SUCCESS
[  10 / 10  ] bandwidth test 4MB SUCCESS
============== [In App] Bandwidth Test ===============
    iterations    = 10
    buf_size      = 4194304 Bytes
    total_us      = 105932
    total_bytes   = 41943040
    bandwidth     = 377.60 MB/s
============== [In Driver] Bandwidth Test ===============
    total_ns      = 105876540
    total_bytes   = 41943040
    bandwidth     = 377.80 MBps
zynq> 
```



## v007-支持应用buf偏移读写

笔记附件：[[driver-axidma-2603241120.zip]]
- axidma_common.h    —— 驱动和应用公共头文件
- axidma_v006.c           —— 上一个版本驱动，仅作为当前版本对比参考
- axidma_v007.c           —— 当前版本驱动代码
- Makefile、build_drv.sh    —— 驱动编译规则（sh 调用 Makefile）
- app_bandwidth.c、build_app.sh    —— 应用和它的编译脚本


**关键修改**：通过偏移的方式来访问大块内存特定位置。
如下图所示，用户空间 read/write 通过偏移和大小即可让DMA传输指定内存块。这为后续的 BdRing 管理算法移植提供了基础保障。

```cpp
// 通过映射拿到一个大buf,比如16MB
tx_buf = mmap(..., 16MB, ...);
rx_buf = mmap(..., 16MB, ...);

// 例子: 读/写 大buf 的偏移0, 也就是整个大buf
retlen = write(h2c_fd, (void *)0, tx_bufsz);
retlen = read(c2h_fd, (void *)0, rx_bufsz);

// 例子: 在大buf 2MB 的偏移处, 读取 4MB 大小的数据
retlen = read(c2h_fd, (void *)(2*1024*1024), (4*1024*1024));


// 后续如果觉得在 read/write 上传递偏移比较奇怪,
// 可以在用户空间把映射得到的数据首地址通过ioctl告知驱动,
// 这样后续用户空间就能直接通过buf方式执行read/write
```


![[Pasted image 20260322191534.png]]



测试日志: 带宽例程由于是短接测试，所以始终从0偏移读/写数据。
```log
zynq> ./app_bandwidth.elf 16KB 16KB 5
remove axidma0
called axidma_probe
axidma probe success
cmdline=insmod axidma_v007.ko tx_bufsize=16KB rx_bufsize=16KB
iterations  = 5
tx_bufsz    = 16KB (16384 Bytes)
rx_bufsz    = 16KB (16384 Bytes)
mmap success: tx=0xb6f67000 rx=0xb6f63000
tx_thread: iterations = 5
tx_thread: tx_bufsz   = 16384
rx_thread: iterations = 5
rx_thread: rx_bufsz   = 16384
[   1 / 5   ] bandwidth test 16KB SUCCESS
[   2 / 5   ] bandwidth test 16KB SUCCESS
[   3 / 5   ] bandwidth test 16KB SUCCESS
[   4 / 5   ] bandwidth test 16KB SUCCESS
[   5 / 5   ] bandwidth test 16KB SUCCESS
============== [In App] Bandwidth Test ===============
    iterations    = 5
    buf_size      = 16384 Bytes
    total_us      = 681
    total_bytes   = 81920
    bandwidth     = 114.72 MB/s
zynq> 
zynq> 
zynq> ./app_bandwidth.elf 512kB 512kB 5
remove axidma0
called axidma_probe
axidma probe success
cmdline=insmod axidma_v007.ko tx_bufsize=512KB rx_bufsize=512KB
iterations  = 5
tx_bufsz    = 512KB (524288 Bytes)
rx_bufsz    = 512KB (524288 Bytes)
mmap success: tx=0xb6e4e000 rx=0xb6dce000
tx_thread: iterations = 5
tx_thread: tx_bufsz   = 524288
rx_thread: iterations = 5
rx_thread: rx_bufsz   = 524288
[   1 / 5   ] bandwidth test 512KB SUCCESS
[   2 / 5   ] bandwidth test 512KB SUCCESS
[   3 / 5   ] bandwidth test 512KB SUCCESS
[   4 / 5   ] bandwidth test 512KB SUCCESS
[   5 / 5   ] bandwidth test 512KB SUCCESS
============== [In App] Bandwidth Test ===============
    iterations    = 5
    buf_size      = 524288 Bytes
    total_us      = 7082
    total_bytes   = 2621440
    bandwidth     = 353.01 MB/s
zynq> 
zynq> 
zynq> ./app_bandwidth.elf 1MB 1MB 5
remove axidma0
called axidma_probe
axidma probe success
cmdline=insmod axidma_v007.ko tx_bufsize=1MB rx_bufsize=1MB
iterations  = 5
tx_bufsz    = 1MB (1048576 Bytes)
rx_bufsz    = 1MB (1048576 Bytes)
mmap success: tx=0xb6e77000 rx=0xb6d77000
tx_thread: iterations = 5
tx_thread: tx_bufsz   = 1048576
rx_thread: iterations = 5
rx_thread: rx_bufsz   = 1048576
[   1 / 5   ] bandwidth test 1MB SUCCESS
[   2 / 5   ] bandwidth test 1MB SUCCESS
[   3 / 5   ] bandwidth test 1MB SUCCESS
[   4 / 5   ] bandwidth test 1MB SUCCESS
[   5 / 5   ] bandwidth test 1MB SUCCESS
============== [In App] Bandwidth Test ===============
    iterations    = 5
    buf_size      = 1048576 Bytes
    total_us      = 13668
    total_bytes   = 5242880
    bandwidth     = 365.82 MB/s
zynq> 
zynq> 
zynq> ./app_bandwidth.elf 2MB 2MB 5
remove axidma0
called axidma_probe
axidma probe success
cmdline=insmod axidma_v007.ko tx_bufsize=2MB rx_bufsize=2MB
iterations  = 5
tx_bufsz    = 2MB (2097152 Bytes)
rx_bufsz    = 2MB (2097152 Bytes)
mmap success: tx=0xb6d20000 rx=0xb6b20000
tx_thread: iterations = 5
tx_thread: tx_bufsz   = 2097152
rx_thread: iterations = 5
rx_thread: rx_bufsz   = 2097152
[   1 / 5   ] bandwidth test 2MB SUCCESS
[   2 / 5   ] bandwidth test 2MB SUCCESS
[   3 / 5   ] bandwidth test 2MB SUCCESS
[   4 / 5   ] bandwidth test 2MB SUCCESS
[   5 / 5   ] bandwidth test 2MB SUCCESS
============== [In App] Bandwidth Test ===============
    iterations    = 5
    buf_size      = 2097152 Bytes
    total_us      = 26788
    total_bytes   = 10485760
    bandwidth     = 373.30 MB/s
zynq> 
zynq> 
zynq> ./app_bandwidth.elf 4MB 4MB 5
remove axidma0
called axidma_probe
axidma probe success
cmdline=insmod axidma_v007.ko tx_bufsize=4MB rx_bufsize=4MB
iterations  = 5
tx_bufsz    = 4MB (4194304 Bytes)
rx_bufsz    = 4MB (4194304 Bytes)
mmap success: tx=0xb6b8a000 rx=0xb678a000
tx_thread: iterations = 5
tx_thread: tx_bufsz   = 4194304
rx_thread: iterations = 5
rx_thread: rx_bufsz   = 4194304
[   1 / 5   ] bandwidth test 4MB SUCCESS
[   2 / 5   ] bandwidth test 4MB SUCCESS
[   3 / 5   ] bandwidth test 4MB SUCCESS
[   4 / 5   ] bandwidth test 4MB SUCCESS
[   5 / 5   ] bandwidth test 4MB SUCCESS
============== [In App] Bandwidth Test ===============
    iterations    = 5
    buf_size      = 4194304 Bytes
    total_us      = 53093
    total_bytes   = 20971520
    bandwidth     = 376.70 MB/s
zynq> 
zynq> 
zynq> 
zynq> ./app_bandwidth.elf 8MB 8MB 5
remove axidma0
called axidma_probe
axidma probe success
cmdline=insmod axidma_v007.ko tx_bufsize=8MB rx_bufsize=8MB
iterations  = 5
tx_bufsz    = 8MB (8388608 Bytes)
rx_bufsz    = 8MB (8388608 Bytes)
mmap success: tx=0xb674a000 rx=0xb5f4a000
tx_thread: iterations = 5
tx_thread: tx_bufsz   = 8388608
rx_thread: iterations = 5
rx_thread: rx_bufsz   = 8388608
[   1 / 5   ] bandwidth test 8MB SUCCESS
[   2 / 5   ] bandwidth test 8MB SUCCESS
[   3 / 5   ] bandwidth test 8MB SUCCESS
[   4 / 5   ] bandwidth test 8MB SUCCESS
[   5 / 5   ] bandwidth test 8MB SUCCESS
============== [In App] Bandwidth Test ===============
    iterations    = 5
    buf_size      = 8388608 Bytes
    total_us      = 105704
    total_bytes   = 41943040
    bandwidth     = 378.42 MB/s
zynq> 
```






# ZYNQ ARM GIC standalone 裸机驱动剖析


## IRQ回调的软件原理


其软件层面的底层本质，就是数组索引。

1、下面是注册中断回调函数的核心代码：就是利用数组索引来存放和调取相关的回调实体。
```cpp
	Xil_ExceptionRegisterHandler(XIL_EXCEPTION_ID_INT, // XIL_EXCEPTION_ID_IRQ_INT
			(Xil_ExceptionHandler)INTC_HANDLER, // XScuGic_InterruptHandler
			(void *)IntcInstancePtr);

void Xil_ExceptionRegisterHandler(u32 Exception_id,
				    Xil_ExceptionHandler Handler,
				    void *Data)
{
	XExc_VectorTable[Exception_id].Handler = Handler;
	XExc_VectorTable[Exception_id].Data = Data;
}

s32  XScuGic_Connect(XScuGic *InstancePtr, u32 Int_Id,
				Xil_InterruptHandler Handler, void *CallBackRef)
{
	InstancePtr->Config->HandlerTable[Int_Id].Handler = (Xil_InterruptHandler)Handler;
	InstancePtr->Config->HandlerTable[Int_Id].CallBackRef = CallBackRef;
	return XST_SUCCESS;
}
```


![[Pasted image 20260319110708.png]]


2、触发回调调用
```cpp
void IRQInterrupt(void)
{
	XExc_VectorTable[XIL_EXCEPTION_ID_IRQ_INT].Handler(
		XExc_VectorTable[XIL_EXCEPTION_ID_IRQ_INT].Data);
}

void XScuGic_InterruptHandler(XScuGic *InstancePtr)
{
	u32 InterruptID;
    u32 IntIDFull;
    XScuGic_VectorTableEntry *TablePtr;

	// 找到触发中断的id
    IntIDFull = XScuGic_CPUReadReg(InstancePtr, XSCUGIC_INT_ACK_OFFSET);
    InterruptID = IntIDFull & XSCUGIC_ACK_INTID_MASK;
    if (XSCUGIC_MAX_NUM_INTR_INPUTS <= InterruptID) {
        goto IntrExit;
    }

	// 拿到中断id作为索引,找到回调实例
    TablePtr = &(InstancePtr->Config->HandlerTable[InterruptID]);
    if (TablePtr != NULL) {
        TablePtr->Handler(TablePtr->CallBackRef);
    }

IntrExit:
    /*
     * Write to the EOI register, we are all done here.
     * Let this function return, the boot code will restore the stack.
     */
    XScuGic_CPUWriteReg(InstancePtr, XSCUGIC_EOI_OFFSET, IntIDFull);
}
```





## axi-dma-standalone-intr


和poll例程区别不大，中断例程主干:
- 在 XAxiDma_CfgInitialize 之后，
- 初始化中断: SetupIntrSystem(TX_INTR_ID=62, RX_INTR_ID=63); // TX(MM2S), RX(S2MM)
- 其他流程都一样

```cpp
#define  XAxiDma_IntrGetIrq(InstancePtr, Direction)
	ChanBase = RegBase + (XAXIDMA_RX_OFFSET{0x30} * Direction);
	Offset = XAXIDMA_SR_OFFSET{0x04};
	value = value & XAXIDMA_IRQ_ALL_MASK{0x7000};

static void TxIntrHandler(void *Callback)
{
	XAxiDma *AxiDmaInst = (XAxiDma *)Callback;
	
	// 从AXIDMA控制器拿到中断信息
	IrqStatus = XAxiDma_IntrGetIrq(AxiDmaInst, XAXIDMA_DMA_TO_DEVICE{0x00});
	XAxiDma_IntrAckIrq(AxiDmaInst, IrqStatus, XAXIDMA_DMA_TO_DEVICE);
	
	// 如果没有模块中断发生,直接返回
    if (!(IrqStatus & XAXIDMA_IRQ_ALL_MASK{0x7000})) {
        return;
    }
    
    // 如果发生的错误中断
    if ((IrqStatus & XAXIDMA_IRQ_ERROR_MASK{0x4000})) {
	    XAxiDma_Reset(AxiDmaInst);
	    
	    // 等待复位完成
	    while (TimeOut--) {
		    if (XAxiDma_ResetIsDone(AxiDmaInst)) break;
	    }
    }
    
    // 如果发生的是传输完成中断
    if ((IrqStatus & XAXIDMA_IRQ_IOC_MASK{0x1000})) {
        TxDone = 1;
    }
}

static void RxIntrHandler(void *Callback)
{
	XAxiDma *AxiDmaInst = (XAxiDma *)Callback;
	
	// 从AXIDMA控制器拿到中断信息
	IrqStatus = XAxiDma_IntrGetIrq(AxiDmaInst, XAXIDMA_DEVICE_TO_DMA);
	XAxiDma_IntrAckIrq(AxiDmaInst, IrqStatus, XAXIDMA_DEVICE_TO_DMA);
	
	// 如果没有模块中断发生,直接返回
    if (!(IrqStatus & XAXIDMA_IRQ_ALL_MASK{0x7000})) {
        return;
    }
    
    // 如果发生的错误中断
    if ((IrqStatus & XAXIDMA_IRQ_ERROR_MASK{0x4000})) {
	    XAxiDma_Reset(AxiDmaInst);
	    
	    // 等待复位完成
	    while (TimeOut--) {
		    if (XAxiDma_ResetIsDone(AxiDmaInst)) break;
	    }
    }
    
    // 如果发生的是传输完成中断
    if ((IrqStatus & XAXIDMA_IRQ_IOC_MASK{0x1000})) {
        TxDone = 1;
    }
}
```

---


SG模式中断的注册：
```cpp
// TxIntrId=62, RxIntrId=63
// void XScuGic_SetPriorityTriggerType(..., u32 Int_Id, u8 Priority, u8 Trigger);
// Priority: 0 是最高优先级, 0xF8 是最低优先级
// Trigger: 触发方式,对于共享中断(SPI),b01=高电平有效,b11=上升沿有效
XScuGic_SetPriorityTriggerType(IntcInstancePtr, TxIntrId, 0xA0, 0x3);
XScuGic_SetPriorityTriggerType(IntcInstancePtr, RxIntrId, 0xA0, 0x3);
Status = XScuGic_Connect(IntcInstancePtr, 
			TxIntrId,
			(Xil_InterruptHandler)TxIntrHandler,
			TxRingPtr);
```


SG模式中断的ISR：
```cpp
// 裸机的中断ISR程序
static void TxCallBack(XAxiDma_BdRing * TxRingPtr)
{
	/* Get all processed BDs from hardware */
	BdCount = XAxiDma_BdRingFromHw(TxRingPtr, XAXIDMA_ALL_BDS, &BdPtr);

	/* Handle the BDs */
	BdCurPtr = BdPtr;
	for (Index = 0; Index < BdCount; Index++) {
		BdSts = XAxiDma_BdGetSts(BdCurPtr);
		if ((BdSts & XAXIDMA_BD_STS_ALL_ERR_MASK) ||
		    (!(BdSts & XAXIDMA_BD_STS_COMPLETE_MASK))) {
			Error = 1;
			break;
		}

		// 如果是RTOS,可能需要及时释放BD所属的buffer

		/* Find the next processed BD */
		BdCurPtr = (XAxiDma_Bd *)XAxiDma_BdRingNext(TxRingPtr, BdCurPtr);
	}

	/* Free all processed BDs for future transmission */
	Status = XAxiDma_BdRingFree(TxRingPtr, BdCount, BdPtr);
	if (Status != XST_SUCCESS) {
		Error = 1;
		ErrorCount += 1;
	}

	if(!Error) {
		TxDone += BdCount;
	}
}

static void TxIntrHandler(void *Callback)
{
	XAxiDma_BdRing *TxRingPtr = (XAxiDma_BdRing *) Callback;

	IrqStatus = XAxiDma_BdRingGetIrq(TxRingPtr);//get pending intrs
	XAxiDma_BdRingAckIrq(TxRingPtr, IrqStatus);//ack pending intrs

	// 如果不是该设备的中断,则直接返回
	if (!(IrqStatus & XAXIDMA_IRQ_ALL_MASK)) return;

	// 如果是错误中断, 则这里直接复位axi-dma模块
	if ((IrqStatus & XAXIDMA_IRQ_ERROR_MASK)) {
		XAxiDma_BdRingDumpRegs(TxRingPtr);
		Error = 1;
		ErrorCount += 1;

		// 复位模块,并等待复位完成
		XAxiDma_Reset(&AxiDma);
		TimeOut = RESET_TIMEOUT_COUNTER;
		while (TimeOut) {
			if (XAxiDma_ResetIsDone(&AxiDma)) {
				break;
			}
			TimeOut -= 1;
		}
		return;
	}

	/*
	 * If Transmit done interrupt is asserted, call TX call back function
	 * to handle the processed BDs and raise the according flag
	 */
	if ((IrqStatus & (XAXIDMA_IRQ_DELAY_MASK | XAXIDMA_IRQ_IOC_MASK))) {
		TxCallBack(TxRingPtr);
	}
}
```




## 内存屏障（多核顺序访问）



你掏出「任务清单（ROB）」，按顺序写下：先放商品 A 到货架，后放商品 B 到货架。
ROB 保证了你不会记错顺序，也不会先做 “放 B” 再做 “放 A”（核内提交顺序绝对对）

先把商品 A 拿到手，按清单顺序放到「临时台面（Store Buffer）」（完成 ROB 的第一个任务 “提交”）；
再把商品 B 拿到手，按清单顺序放到「临时台面（Store Buffer）」（完成 ROB 的第二个任务 “提交”）；
此时 ROB 的任务都 “提交” 完了，你觉得 “反正都放台面上了，等下一起搬去货架就行”。

商品 A 要放的货架位置，现在被其他同事占着（Cache 行是 S 共享状态，需要先发无效请求）；
商品 B 要放的货架位置是空的（Cache 行是 E 独占状态，能直接放）。
为了 “高效”，你决定：**先把商品 B 搬到货架上，等货架 A 空了再搬商品 A**。
此时「临时台面（Store Buffer）」虽然按序放了 A、B，但刷到「货架（L1 Cache）」的顺序变成了 B 先、A 后。

好友 A 看到了错误的顺序（多核可见性问题）



**为什么 ROB 保证了顺序还会出问题？**

ROB 管的是「你把商品放到临时台面的顺序」（核内提交顺序），保证你不会先放 B 到台面、再放 A；
但 ROB 不管「你把商品从台面搬到货架的顺序」（Store Buffer 刷 Cache 的顺序），硬件为了效率会乱序刷；
好友 A 只能看货架（L1 Cache），看不到你的临时台面（Store Buffer），所以他看到的顺序和你 “提交” 的顺序不一致。


内存屏障的作用：老板监督你按序搬
“必须先把台面上的 A 搬到货架，确认放好了，再搬 B 到货架，不准偷懒！”


执行 `DMB sy`（ARM 内存屏障）时，CPU 会强制：
屏障前的所有写操作（A=1）必须从 Store Buffer 刷入 L1 Cache；
等待 MESI 协议同步（通知好友 A “货架 A 的内容变了”）；确认完成后，才能执行屏障后的写操作（B=1）。


<font color=blue>利用上面的例子，给我举例 dmb、dsb、isb 的区别？</font>

DMB——只管数据读写的顺序——Store Buffer ↔ Cache 的刷写顺序；
所以多核之间的顺序性就用dmb，smp_mb() 也是封装 dmb；

DSB——管所有数据操作的完成——所有数据操作（Cache / 总线 / Memory）完成；
所以涉及到外设的访问就用dsb，它是保证直达地址空间的位置，而不是仅仅保证刷到Cache。

ISB——管 CPU 流水线的指令刷新——指令取指 / 译码 / 执行的流水线同步。
这种涉及到CPU工作模式的切换了，接下来的指令不能和之前的指令混合执行。


# ZYNQ硬件基础


## AXI4总线

1、AXI4是ARM公司提出的一种高性能、高带宽、低延迟的**片内总线**。
2、AXI4分类为：AXI4_FULL、AXI4_LITE、AXI4_STREAM

**AXI4_LITE**：不支持突发传输，发送一个数据的时候，也必须发送一个地址。
**AXI4_FULL**：支持突发传输，突发长度为 1~256 Beats。
**AXI4_STREAM**：在FULL的基础上，丢弃了地址项，常用于高速数据传输。


**什么是片内、片外？**
👉 关键点只有一个：❗**是否在同一块硅片（die）上**

一颗 SoC（比如 Zynq）：
```txt
+-------------------------+
|         芯片（die）      |
|                         |
|  CPU  SRAM  DMA  AXI    |  ← 片内
|                         |
+-------------------------+
        ↓ 引脚（pin）
=========================
        ↓ PCB 走线
+-------------------------+
|    DDR / Flash / 外设    |  ← 片外
+-------------------------+
```

✔典型1：CPU → AXI → DDR Controller（片内） → DDR 芯片（片外）
✔典型2：CPU → AXI → AXI DMA（片内） → ADC芯片（片外）


<font color=blue>片内和片外性能差异的最主要原因还是因为距离吗？以及耗电的最主要原因也是因为距离吗？
</font>

如果只是距离：
👉 芯片内部几毫米 vs PCB 几厘米  
👉 延迟差不会达到几十倍

而现实是：
- 片内 SRAM：~1ns
- DDR：~50–100ns
- SPI Flash：更慢
👉 差距远远大于“距离比例”

👉 **真正慢的不是“走远了”，而是“要经过复杂接口”**

👉 **电容负载（核心中的核心）**
这是**功耗 + 速度的根本来源**。

公式: $$P = CV^{2}f$$
👉 含义：
- C：负载电容
- V：电压
- f：频率

❗**功耗主要来自“驱动电容”，而不是距离本身**

✔ 片内：电容：极小（fF级），电压：低（~0.8–1V）
❌ 片外：电容：很大（pF~nF），电压：高（1.8V / 3.3V）

👉 关键结论：
```txt
性能差异：主要是 IO + 协议复杂度
功耗差异：主要是电容 C 和电压 V
距离：只是次要因素
```


<font color=blue>为什么 IO 会带来巨大开销？
</font>

因为它要解决“数字 → 模拟 → 数字”的问题：

**片内**：数字信号 → 数字逻辑
**片外**：数字 → 模拟电压 → PCB传输 → 模拟 → 数字

👉 需要：
- 驱动能力（drive strength）
- 信号完整性（SI）
- 终端匹配（termination）
- 抗干扰（EMI）

**一个非常直观的类比（帮助你建立直觉）**

**片内**：你在房间里和房间里另一个人说话。

**片外**：你用扩音器对着马路喊
👉 为什么耗电大？
- 要推动空气（电容）
- 要更大能量（电压）
- 要抗噪声（干扰）


👉 所有高性能系统都在做一件事：尽量把数据留在“片内”
比如：
- cache（L1/L2/L3）
- on-chip SRAM
- register
- FIFO（PL 里）
👉 原因：❗避免访问“高电容 + 高延迟”的片外资源





<font color=blue>为什么驱动电容会导致功耗增加？功耗不是跟电流有关吗？
</font>

👉 你这个问题问得非常到位，本质是在问：**“电容为什么会消耗功率？它不是不耗能吗？”**

❗**电容本身不“消耗能量”，但在“反复充放电过程中”，电源需要不断提供能量 → 这就是功耗**

**电容什么时候会产生电流？**
👉 答案：**只有在“电压变化”的时候**

电容电流公式：$$I = C\frac{d{V}}{d{t}}$$
👉 含义：
- 电压变化越快（频率高，时间短） → 电流越大：磁球来回摩擦越剧烈，做功越大。
- 电容越大 → 电流越大：相同的电压，容量越大，单位时间流经的磁球数越多，电流越大。




**什么是主，什么是从？**

1、写数据：（主动方都是主机）主机先发起写请求，再开始向从机发送数据，读同理；

👉 可以把它理解为：**谁发起操作(主)，谁响应操作(从)**

为什么必须区分主/从？
核心原因一句话：❗**避免冲突，让通信“有秩序”**

如果没有主从会发生什么？
想象：
设备A：我要发数据！  
设备B：我也要发！  
设备C：我也发！

👉 结果：
- 总线冲突（bus contention）
- 数据混乱
- 信号损坏

有了主从：👉 有序执行
主设备：现在我要访问设备B  
从设备B：收到，我响应  
其他设备：保持安静

**老师点名回答问题**：“B同学回答问题”，B同学回答，其他同学闭嘴。

**为什么“从设备不能主动”？**

总线是共享资源：👉 必须有人统一调度

为了硬件实现简单，如果每个设备都能抢总线：👉 需要复杂仲裁

可预测性，主设备控制：什么时候访问，访问谁，访问多少，👉 系统可控

<font color=blue>在 AXI 总线中：为什么允许“多个 master”同时存在？它是如何避免冲突的？
</font>

```txt
AXI 允许多个 master，是为了提高并行度和带宽利用率；
但通过 interconnect + 仲裁（arbiter）+ 独立通道，把冲突变成“有序调度”。
```

AXI 如何避免冲突？（核心机制）
① Interconnect（互连网络）⭐最关键：Master → AXI Interconnect → Slave

② 仲裁器⭐核心冲突解决
当多个 master 访问同一个 slave：
```txt
CPU  → DDR
DMA  → DDR
```
👉 Interconnect 内部仲裁

👉 AXI 的本质不是“避免冲突”，而是：把冲突变成“可调度的资源竞争”


---

M_AXI_GP0、M_AXI_GP1：开头的M表示PS作为主；
S_AXI_GP0、S_AXI_GP1：开头的S表示PS作为从。

S_AXI_ACP：加速器一致性端口，cache一致性回话。

S_AXI_HP0、S_AXI_HP1、S_AXI_HP2、S_AXI_HP3：带有读/写FIFO的高性能端口。

理论带宽 = 时钟频率 x 数据位宽，比如 100MHz x 32bit = 3200bps

![[Pasted image 20260326104112.png]]


<font color=blue>S_AXI_HP0 中，PS作为从机，PL作为主机，它们通过 S_AXI_HP0 传输数据，那么DDR3 和 S_AXI_HP0 是什么关系？
</font>

关系是：PL → S_AXI_HP0 → PS内部互连 → DDR Controller → DDR3

👉 一句话：
❗**S_AXI_HP0 只是“入口”，DDR3 才是“目的地”**


👉 关键问题：❗“Slave ≠ 被动设备”
PL（DMA） → 发起访问 → Master  
PS（HP口） → 被访问 → Slave
👉 但 PS 内部：
CPU → 访问 DDR → CPU 又是 Master


<font color=blue>在 Zynq 中，为什么 HP口访问 DDR 时，一定要做 cache flush / invalidate？
</font>

在 Zynq 里：
CPU：操作 cache（L1/L2）  
DMA：操作 DDR（物理内存）

👉 它们之间：
❗**默认没有自动一致性（non-coherent）**

```txt
        CPU
         ↓
     L1 / L2 Cache   ← ⭐CPU看到的数据
         ↓
        DDR          ← ⭐DMA看到的数据
         ↑
       DMA（HP口）
```

✔ 关闭 cache（这会使整个系统所有内存都不走 cache）：
```txt
CPU ───────→ DDR ←────── DMA
```

✔ 局部关闭 cache
MMU 标记为 non-cacheable，MMU 标记为 non-cacheable。
dma_alloc_coherent() 的实现本质就是分配一块 non-cacheable（或 coherent）内存。






手动 remap（高级玩法）
普通内存 —— remap_pfn_range()
设备地址 —— vm_iomap_memory()

👉 这个才是你要找的：❗**真正修改 cache 属性的接口**
pgprot_t prot = pgprot_noncached(vma->vm_page_prot);

👉 `pgprot_noncached()` 本质：修改页表属性 → MMU 按该属性访问
- Normal memory（cacheable / non-cacheable）
- Device memory



<font color=blue>为什么 ioremap 只能作为寄存器内存？不能作为普通内存？
</font>

✅ **ioremap 底层做了什么?**
`void __iomem *ioremap(phys_addr_t phys, size_t size);`
- 内核会把这段物理地址映射到虚拟地址
- 并设置页表属性为 **Device Memory**（非 cacheable, strong ordering）


✅ **CPU 对这块内存的访问行为**：
读：直接读寄存器  
写：直接写寄存器  
顺序：严格按照代码顺序执行，不会乱序  
cache：绕过 cache
**普通内存需要 cache、预取和乱序优化**， 从而提高访问性能， 所以 ioremap 不适合映射普通内存。










# 关键内核接口


由于内核代码太庞杂了，各个子系统之间又盘根错节，直接看内核代码容易给人看emo，所以切入点只能从驱动代码入手，更细化一点就是从驱动里各个调用的接口入手，把每个接口的工作特性和背后的原理搞清楚，就可以了，以后这种星星点点的原理积累多了，有机会或者有灵感了自然而然就串起来了。


## dma_alloc_coherent


参考文章：
Cache和DMA一致性: https://zhuanlan.zhihu.com/p/109919756


如下图所示，主要是搞清楚下图的 Cache 一致性的关系，但凡涉及到CPU这边，你就必然要想到Cache。
![[Pasted image 20260325093448.png]]

如上图所示，后面的问题都是围绕着上面简图进行更细化描述：

- **最简单的方法(nocahe)**
了避免cache的影响，我们可以将这段内存映射 nocache，即不使用cache。映射的最小单位是4KB，因此在内存映射上至少4KB是nocahe的。这种方法简单实用，如果需要大量高频传输的场景，会由于nocache导致性能损失。这也是 Linux 系统中 dma_alloc_coherent() 接口的实现方法。这种 nocache 的方法，对CPU访问内存的性能不太友好，不太适合那种CPU需要频繁访问相关内存的场景，所以根据需求使用。

- **软件维护cache一致性**
如果是数据从**外设到内存**，那么在DMA传输之前，可以invalid DMA Buffer地址范围的高速缓存。在DMA传输完成后，CPU程序读取数据不会由于cache hit(命中)导致读取过时的数据。如果数据是从**内存到外设**，那么在DMA传输之前，可以clean DMA Buffer地址范围的高速缓存，clean的作用是写回cache中修改的数据。在DMA传输时，不会把主存中的过时数据发送到I/O设备。注意，在DMA传输没有完成期间CPU不要访问DMA Buffer。这也是Linux系统中流式DMA映射 dma_map_single() 接口的实现方法。

- **DMA Buffer对齐要求**
dma_alloc_coherent() 本身保证申请到的内存是 cacheline 对齐的，实际上通常是页对齐，页对齐自然满足cacheline对齐。而 dma_map_single() 只是把一段你已经有的内存的 **cpu虚拟地址** 转换成 **DMA可访问地址** + 做cache同步(也就是根据 `dir` 做 cache flush / invalidate)，所以它不保证对齐。dma_map_single() 的使用场景就是那种我需要用一下DMA，则把已有内存 dma_map_single() 一下，用完就 unmap，这种场景就很合适。


<font color=blue>同时访问这块内存的情况下，如果还是坚持使用 dma_map_single，会有哪些坑？</tont>

`dma_map_single()` 的模型是：
👉 **map（按方向做一次 cache 同步） → DMA 使用（期间 CPU 不访问） → unmap（按方向做必要的 cache 同步）**

它假设：
> ❗ **在 map ~ unmap 期间，CPU 不再访问这块内存**



## 结构体：dev_pm_ops


```cpp
struct dev_pm_ops {
	int (*prepare)(struct device *dev);
	void (*complete)(struct device *dev);
	int (*suspend)(struct device *dev); // 👉 **系统级休眠（如待机）时整体断电 / 唤醒恢复**
	int (*resume)(struct device *dev);
	...
	int (*runtime_suspend)(struct device *dev); // 👉 **设备空闲时自动省电 / 需要用时自动唤醒**
	int (*runtime_resume)(struct device *dev);
	int (*runtime_idle)(struct device *dev);
};
```

suspend / resume 到底在什么场景下触发？目的是什么？

👉 **设备“暂时不用”时**
典型例子：
- UART 一段时间没收发数据
- I2C 控制器空闲
- DMA 没有任务
- SPI 控制器 idle


✅ **suspend 触发时机**
```txt
driver 或内核调用：

pm_runtime_put()
    ↓
设备进入 idle
    ↓
runtime_suspend()
```

✅ **resume 触发时机**
```txt
用户 / 内核再次使用设备：

pm_runtime_get()
    ↓
runtime_resume()
```


```txt
内部逻辑（简化）：
if (dev->driver->pm && dev->driver->pm->runtime_suspend)  
	调 driver 的

👉 也就是说：bus 提供默认行为，driver 可以覆盖
```


🧠 **举个直观例子**
一个 UART：
```txt
空闲 → runtime_suspend → 关闭时钟
写数据 → runtime_resume → 打开时钟 → 发送
```

🔥 **关键点**
> runtime PM 是“**细粒度**、按需”的电源管理


**🔥 runtime PM：一个完整流程（你应该掌握）**
```txt
设备空闲
   ↓
pm_runtime_put()
   ↓
runtime_suspend()
   ↓
关闭时钟 / 电源


设备使用
   ↓
pm_runtime_get()
   ↓
runtime_resume()
   ↓
恢复设备
```


<font color=blue>怎么判断一段时间没有任务的？</font>

这个问题问到 **runtime PM 的核心机制了**。
内核并不会“自动检测设备有没有任务”，而是靠“使用计数 + 驱动主动标记空闲”来判断。

也就是说：
```txt
“有没有任务” ≠ 内核猜的
“有没有任务” = 驱动告诉内核的
```

**核心机制：usage_count（使用计数）**

每个设备都有一个 runtime PM 状态：
```cpp
struct dev_pm_info {
    atomic_t usage_count;
    ...
};
```

👉 **工作原理**：
```txt
usage_count > 0  → 设备正在使用（busy）
usage_count == 0 → 设备空闲（idle）
```

👉 **谁来维护这个 usage_count？驱动！！**

1️⃣ **使用设备时**
pm_runtime_get(dev);

👉 **做的事情**：
usage_count++  
如果设备已 suspend → 触发 runtime_resume

2️⃣ **用完设备时**
pm_runtime_put(dev);

👉 **做的事情**：
usage_count--  
如果变成 0 → 设备变 idle → 可能触发 runtime_suspend

👉 不是立即 suspend，而是“**延迟判断**”
```txt
pm_runtime_put_autosuspend()
    ↓
usage_count--
    ↓
如果 == 0
    ↓
启动一个 timer（autosuspend delay）
    ↓
延迟一段时间
    ↓
如果期间没人再 get()
    ↓
执行 runtime_suspend()
```

👉 **延迟时间在哪设置？**
```cpp
pm_runtime_set_autosuspend_delay(dev, 1000); // 1秒
```


**为什么要这样设计？（为什么要延迟判断）（非常关键）**

👉 如果不延迟，则结果：**疯狂开关电源**（性能差 + 功耗反而更高）

👉 典型的现实中的例子：
```txt
你在操作（pm_runtime_get） → 屏幕亮
停止操作（pm_runtime_put） → 开始计时
1分钟没动 → 熄屏（runtime_suspend）
触摸一下 → 亮屏（runtime_resume）
```




---

上面是 Runtime 级别的功耗管理，接下来就是系统级别(粗粒度的功耗管理介绍)

✅ **应用场景**
👉 **整个系统进入低功耗状态**
比如：
- `echo mem > /sys/power/state`
- suspend-to-RAM
- suspend-to-idle

✅ **suspend调用流程**
```txt
用户空间触发
   ↓
kernel suspend 流程
   ↓
遍历所有 device
   ↓
调用 device->pm->suspend()
```

✅ **resume调用流程**
```txt
系统唤醒（按键 / RTC / 中断）
   ↓
调用 device->pm->resume()
```

✅ **目的**
保证系统能安全“关机式休眠”，再恢复




## 结构体：device和device_driver


```cpp
// include/linux/device.h
struct device {
	struct kobject kobj;
	struct device_driver *driver; // 设备对应的驱动实例
	void		*platform_data;	/* Platform specific data, device
					   core doesn't touch it */
	void		*driver_data;	/* Driver data, set and get with
					   dev_set_drvdata/dev_get_drvdata */

	struct class		*class;
	void	(*release)(struct device *dev);

	// 省略其他成员
};


// include/linux/device/driver.h
struct device_driver {
	const char		*name;

	// 👉 含义：
	// 这个 driver 属于哪条 bus
	// 只会匹配同一 bus 的 device
	struct bus_type		*bus;

	// 👉 用于：设备树匹配（platform 设备最常见）
	const struct of_device_id	*of_match_table;
	const struct acpi_device_id	*acpi_match_table;

	int (*probe) (struct device *dev);
	int (*remove) (struct device *dev);
	void (*shutdown) (struct device *dev);
	int (*suspend) (struct device *dev, pm_message_t state);
	int (*resume) (struct device *dev);

	const struct dev_pm_ops *pm;
	struct driver_private *p;
};

```

**真正建立关联**的“瞬间”
发生在：driver_match_device()、driver_probe_device ()，其核心逻辑（简化）：
```cpp
if (bus->match(dev, drv)) {
    drv->probe(dev);
    dev->driver = drv;   // ⭐关键绑定
}
```

<font color=blue>既然 device 里已经有 driver 指针，那为什么还需要：dev_set_drvdata(dev, data)?
</font>

driver_data 属于是驱动的私有数据，由 driver 自己管理维护，而 dev->driver 由内核维护。

**为什么必须要有 driver_data？**

1️⃣ **一个 driver 可以对应多个 device（核心原因）**
例如：
```txt
I2C 驱动 foo_driver
    ├── 设备1 (addr 0x50)
    ├── 设备2 (addr 0x60)
    └── 设备3 (addr 0x70)
```

👉 这些 device：dev->driver = foo_driver; 👉 都一样！

但问题来了：
👉 每个设备的运行状态是不同的，比如：寄存器基地址、中断号等等都是有进一步区分的。
👉 所以必须有：dev_set_drvdata(dev, my_dev);

2️⃣ **回调函数只有一个参数**：dev
你看 driver 接口：
```cpp
int (*probe)(struct device *dev);
int (*remove)(struct device *dev);
```

👉 没有传你的私有结构体！
所以你必须这样取回：`struct my_dev *d = dev_get_drvdata(dev);`

👉 `driver_data` 解决：✅ 每个 device 独立一份上下文



<font color=blue>为什么不用把 driver_data 放进 device_driver？
</font>

❌ 问题1：一个 driver 下有多个 device 怎么办？👉 data 放哪一个？
❌ 问题2：并发冲突，多个设备共享同一 driver：👉 状态会互相覆盖

👉 所以必须放在：device → 每个设备实例一份。


## driver_data 和 container_of

前面我们知道，一个驱动可能会管理多个设备，且每个设备都有一定的区分，比如LED1、LED2两个设备，它们都共同由驱动 drvled 控制，那么驱动这边，拿到设备实例后，肯定要根据把各自的私有数据绑定到设备实例里。

👉 **方式一：通过内嵌device+container_of来管理驱动私有数据**
```cpp
struct my_dev {
    struct device dev;   // ⭐更“高级”的写法: 直接嵌进去
    void __iomem *regs;
    int irq;
};
```

然后：`struct my_dev *d = container_of(dev, struct my_dev, dev);` 根据成员地址反推出实例容器。

🔥 **方式二：通过 dev->driver_data 管理驱动私有数据**
```cpp
struct my_dev {
    void __iomem *regs;
    int irq;
};

// 在 probe：
struct my_dev *d = devm_kzalloc(dev, sizeof(*d), GFP_KERNEL);
dev_set_drvdata(dev, d);

// 之后任何地方：
struct my_dev *d = dev_get_drvdata(dev);
```


👉 **什么时候用 container_of，什么时候用 drvdata？**
- container_of：结构体“嵌入式设计”，一个是“**你是我身体的一部分**”；
- drvdata：结构体“外部分配”，一个是 “**我挂在你身上**”。

👉 **什么时候必须用 container_of？**
✅ 1. 内核回调给你的只是“子对象”
✅ 2. 你需要拿回“完整对象”

比如：
```cpp
struct my_dev {
    struct cdev cdev;     // ⭐嵌入内核对象
    struct device *dev;   // 设备模型里的 device（可选）
    int value;
};

static int my_open(struct inode *inode, struct file *file)
{
    struct my_dev *d;
	// open 回调参数里, 只有子对象: inode->i_cdev
	// cdev 是“内核回调入口”: VFS → inode → cdev → file_operations
    d = container_of(inode->i_cdev, struct my_dev, cdev);
    file->private_data = d;
    return 0;
}
```

👉 在 platform 驱动 probe 里：`probe(struct device *dev)`
为什么**不推荐你用 container_of(dev, xxx, dev)**？

提示你方向：device 是谁创建的？你是否“拥有”这个 device？
因为probe()参数里的device是“**内核拥有的对象**”，**不是你嵌进去的成员**，所以不能用 container_of 反推你自己的结构体。


👉 Linux 内核为什么大量使用“侵入式结构体（container_of）”，但驱动却推荐“外挂（drvdata）”？
**为什么内核核心大量用 container_of？**
- container_of 的本质是：(container_ptr - offset) 👉 纯编译期结构布局计算.
- 内核喜欢这样干：**通用节点**（node）嵌入业务结构体，比如典型的链表实例嵌入到业务实例里，内核根本不知道“my是什么”，但仍然能操作链表(增删改查)。


## 接口：devm自动回收机制


👉 devm_ 接口的实现原理，为什么它能够让驱动开发者不用关心资源回收问题？

devm__ 的本质：把“资源释放函数”注册到 device 上，等 device detach 时统一反向执行释放。

2️⃣ device 里有一条链表：👉 所有 devm 资源都挂在这里
```cpp
struct device {
    struct list_head devres_head;
};
```

**devm_kzalloc 实际做了什么？**

```cpp
devm_kzalloc(dev, size, GFP_KERNEL);

// Step 1：分配内存
p = kzalloc(size);

// Step 2：创建 devres 节点
dr = kzalloc(sizeof(*dr));  
dr->data = p;

// Step 3：注册释放函数
dr->release = devm_kzfree;

// Step 4：挂到 device
list_add(&dr->node, &dev->devres_head);

👉 到这里为止：❗devm 只是“登记”，不是“管理”
```

**真正释放发生在什么时候？**

👉 核心触发点：device detach，跟当前 device detach 相关的行为都会调用。
释放机制（核心逻辑），内核会调用：devres_release_all(dev);
执行流程：
```cpp
devres_release_all()
{
	for each devres in dev->devres_head:
	    devres->release(dev, devres->data);
}
```

**为什么 devm 能让驱动“不关心释放”？**
1️⃣ 生命周期绑定 device
device 活着 → 资源活着  
device 死了 → 全部释放

2️⃣ 自动 rollback（probe 失败）
如果 probe 中途失败：内核会自动反向顺序释放。

3️⃣ 不需要“手写错误路径”，不需要各种goto err相关的代码了。

devm 的本质模型（非常重要）可以理解为：
```txt
device
  ├── resource A (release A)
  ├── resource B (release B)
  ├── resource C (release C)
```

👉 device 销毁时统一：release C → B → A


**真正发生 rollback 的地方：really_probe()**
简化后的逻辑：
```cpp
static int really_probe(struct device *dev, struct device_driver *drv)
{
    int ret;

    dev->driver = drv;

    ret = drv->probe(dev);

    if (ret) {
        // ❗probe失败，进入rollback
        devres_release_all(dev);   // ⭐核心
        dev->driver = NULL;
        return ret;
    }

    return 0;
}
```


**rollback 的核心函数：devres_release_all()**
👉 这个函数做的事情：
- 遍历 dev->devres_head
- 反向释放资源: dr->release(dev, dr->data);
- 删除 devres 节点: kfree(dr);

关键理解：**rollback 是“driver core 控制的”**，不是 devm 自己触发的；
devm 做的事情只有一个：👉 “注册资源 + 挂到 devres 链表”
另外，devm 它能起这个名字呢，也是因为它生命周期跟随着该 device 实例。
devm 不是管理资源，而是让 **device 成为资源管理器（owner）**




## 结构体：device和内嵌kobject

```cpp
// include/linux/device.h
struct device {
	struct kobject kobj;
	// 省略其他成员
};
```

**为什么 device 不自己实现，而要嵌入一个 kobject 实例成员？**
👉 Linux 的很关键的设计思想：**分层复用**




## 为什么资深程序员读得快？


不是因为他们“看得快”，而是因为他们在做：
> **语义跳跃（semantic jump）**

新手：一行代码 → 一行代码
高手：10 行代码 → 一个语义块，100 行代码 → 一个功能模块。


👉 这就是**模式识别（pattern recognition）**
资深程序员脑子里其实有很多“**压缩过的模板**”，他们在做有选择的信息获取，他们在做“**语义压缩**”。
资深程序员读代码时：允许自己“跳过细节”，他们知道“**哪些可以不懂**”，只在必要时下钻细节。
你目前在做的是：“**语法级理解 → 语义级理解**”
而资深程序员已经在：“**语义级 → 架构级**”


通过人脑**理解对方代码真正要做什么**？
> **资深程序员是在逐层恢复代码的语义，并最终推断出作者的设计意图。**

最后一句点醒本质
> **读代码的最高境界，不是“看懂”，而是“能在脑子里重新设计一遍它”。**


---

<font color=blue>"底层原理要懂，但日常操作可以交给AI工具"，请问这里的底层原理要懂，什么样的程度才叫懂底层原理？"知道what + 知道why" 吗？
</font>

**一句话：知道设计者层次的语义，并能根据需要来取舍平衡低层的子语义**。

**入门层：what + why**
👉 知道“为什么这么设计”，✔ 这层 = **能解释现象**

👉 但问题是：
- 遇到 bug 还是懵
- 性能问题解决不了
- 只能“理解”，不能“推导”
👉 👉 **这就是大多数工程师停留的层次**


**进阶层：机制级理解（真正开始“懂底层”）**

👉 不只是 why，而是**你能推导系统行为**

👉 **你可以不查资料，自己推出来**，比如你能回答：
- 如果不 flush cache，会发生什么？
- AXI burst size 为什么影响带宽？
- interrupt coalescing 为什么提高吞吐？
✔ 这层 = **能 debug / 能优化**

👉 特征：
- 看源码不迷路
- 能改驱动
- 能定位复杂问题


**专家层：模型级理解（极少数人）**

👉 你脑子里有一套“抽象模型”

比如你看 DMA，不是看代码，而是 memory consistency 模型等知识块，
甚至你能设计一个 DMA IP（哪怕是简化版）或自己写一个 mini 驱动框架。
✔ 这层 = **能设计系统**


**一个非常实用的判断标准（强烈建议你用）**

你可以用这个问题自测：
👉 “如果没有文档，我能不能自己把这个东西重新设计/实现一个简化版？”
✅ 基本能实现 → 你真的懂了
1️⃣ 能解释 bug（不是复述），比如为什么 DMA 偶发丢数据？等等
2️⃣ 能预测系统行为，比如 burst 从 16 改 256 会怎样？interrupt 频率降低吞吐为什么提高？等等
3️⃣ 能做 trade-off，即在多个“互相冲突的目标”之间做取舍。



## sysfs

kset_create_and_add("platform", NULL, bus_kobj);
👉 sysfs 中会出现：/sys/bus/platform/

bus 本质上就是一个 kset
```txt
/sys/bus/
    ├── platform   ← kset
    │     ├── devices/
    │     └── drivers/
    ├── pci
    ├── i2c
```

Linux 里很多“子系统”其实就是 kset：bus、class、devices，要么就是kobject比如/sys/kernel

🔹 kset_create_and_add
👉 一步到位：创建 + 初始化 + 注册

🔹 kset_register
👉 只做：把已有 kset 加入 sysfs


---

```cpp
struct kset_uevent_ops {
        int (* const filter)(struct kset *kset, struct kobject *kobj);
        const char *(* const name)(struct kset *kset, struct kobject *kobj);
        int (* const uevent)(struct kset *kset, struct kobject *kobj,
                      struct kobj_uevent_env *env);
};
```

其中 filter 和  uevent 在实际应用中有什么作用？也就是这两者的目的分别是什么？

filter() 👉 决定“这个事件要不要发出去”（开关）
uevent() 👉 决定“事件里带什么内容”（填充数据）

```cpp
static struct kobj_type bus_ktype = {
        .sysfs_ops        = &bus_sysfs_ops,
        .release        = bus_release,
};

// 决定这个 kobject 的 uevent 是否应该发给用户空间
// 返回值：1 → 允许发送，0 → 丢弃事件（不会通知用户空间）
static int bus_uevent_filter(struct kset *kset, struct kobject *kobj)
{
        struct kobj_type *ktype = get_ktype(kobj);

        if (ktype == &bus_ktype)
                return 1;
        return 0;
}
```













## dmaengine




## module_platform_driver


```cpp
module_platform_driver(my_driver);

// 等价于:
static int __init my_driver_init(void)  
{  
return platform_driver_register(&my_driver);  
}  

static void __exit my_driver_exit(void)  
{  
platform_driver_unregister(&my_driver);  
}  
  
module_init(my_driver_init);  
module_exit(my_driver_exit);
```


## platform_device从哪里来？


```txt
设备树（DT）
   ↓
of_platform_populate()
   ↓
创建 platform_device
   ↓
driver match → probe
```


drivers/base/platform.c
```cpp

// 参数: 设备, 驱动
static int platform_match(struct device *dev, struct device_driver *drv)
{
	// 设备 --> 平台设备
	// 驱动 --> 平台驱动
	struct platform_device *pdev = to_platform_device(dev);
	struct platform_driver *pdrv = to_platform_driver(drv);

	// 先匹配设备自定义的覆写数据
	if (pdev->driver_override)
		return !strcmp(pdev->driver_override, drv->name);

	// 再尝试设备树匹配
	if (of_driver_match_device(dev, drv))
		return 1;

	// 再尝试ACPI匹配
	if (acpi_driver_match_device(dev, drv))
		return 1;

	// 再尝试驱动的 id_table 匹配
	if (pdrv->id_table)
		return platform_match_id(pdrv->id_table, pdev) != NULL;

	// 最后尝试设备名和驱动名匹配
	return (strcmp(pdev->name, drv->name) == 0);
}

static inline int __platform_match(struct device *dev, const void *drv)
{
	return platform_match(dev, (struct device_driver *)drv);
}

```



## 结构体：scatterlist


# 四、这个函数在什么时候被调用？

调用链（你要重点记住）：

device_register  
  ↓  
bus_add_device  
  ↓  
device_attach  
  ↓  
__device_attach_driver  
  ↓  
driver_match_device  
  ↓  
bus->match   ←—— 就是 platform_match

---

👉 所以：

> 👉 **每当有 device 或 driver 注册时，都会触发这个 match 过程**


# 六、匹配成功之后发生什么？

---

## 调用链：

platform_match → true  
        ↓  
driver_probe_device  
        ↓  
really_probe  
        ↓  
drv->probe(dev)

---

👉 最终调用你写的：

xilinx_dma_probe()






# Linux内核全局知识体系


## 内核启动顺序


**第一步、入口**
head.S —— start_kernel()

**第二步（架构 + 设备树）**
setup_arch()、early_init_dt_scan()

**第三步（中断系统）**
init_IRQ()、irqchip_init()、irq-gic.c

**第四步（驱动）**
xilinx_dma_probe()、request_irq()

**第五步（中断触发路径）**
gic_handle_irq()



## 设备内核驱动



![[Pasted image 20260320104234.png]]


## 设备——内核


如上图所示，首先探究左侧设备和内核之间的瓜葛。

<font color=blue>内核通过什么方式获取设备硬件信息？</font>
（1）**设备树**，u-boot提供dtb，一种树结构；
（2）**ACPI** Tables(高级配置和电源接口)，BIOS/UEFI提供，一种硬件描述表。

一句话总结：嵌入式 Linux 用“**设备树描述世界**”，PC Linux 用“**ACPI描述世界**”。


内核早期扫描(设备树):
early_init_dt_scan()
of_platform_populate()

内核早期扫描(ACPI):
acpi_bus_scan()
acpi_get_devices()

驱动获取设备信息:
of_match_device()

举个例子，在 PC 上：网卡、USB控制器、PCI 都是通过 ACPI+PCI枚举出来的。


<font color=blue>除了设备树、ACPI，还有没有其他方式？</font>

（1）老内核里，platform_device_register()；
（2）总线枚举，比如PCI、USB、I2C、SPI 这些总线可以自己发现设备，例如 PCI 扫描 → 发现设备 → 读取 config space。但注意：它们不能描述“**板级连接关系**”，比如中断号、GPIO、DMA通道等这些，这些还是需要DT/ACPI。什么是 "板级连接关系"，更准确的描述就是**操作系统“无法自动发现”，必须提前描述的硬件连接信息**。










## 内核——驱动





## start_kernel


1、映射cpu核编号：[[smp_setup_processor_id]]();

2、关闭本地中断：local_irq_disable();

3、IRQ相关初始化：init_IRQ();







# ZYNQ AXI DMA Linux 中断链路



## Linux中断全局链路


下面基于 linux-xilnx-5.10.0 分析

Linux 中断体系不是一个模块，而是一个**分层架构**：

```txt
[OK]硬件 (Zynq PL/PS 中断)
   ↓
[OK]GIC (ARM Generic Interrupt Controller)
   ↓
[OK]arch/arm/ (中断入口 + 异常向量)
   ↓
irqchip (中断控制器抽象)
   ↓
irq domain (中断号映射)
   ↓
generic irq layer (request_irq / handle_irq)
   ↓
驱动程序
```


## 一、中断入口（架构相关）

arch/arm/kernel/entry-armv.S —— 重点函数 `__irq_svc`，这是 IRQ 的真正入口（异常向量）

你要搞清：
- IRQ 和 FIQ 区别
- CPU 是怎么跳进来的
- 保存了哪些寄存器


## 二、GIC中断处理（Zynq核心）


主线索：
1、重点源文件：drivers/irqchip/irq-gic.c
2、重点函数：gic_handle_irq()
3、核心逻辑：这里是“硬件 → Linux”的桥梁
```cpp
irqnr = readl(GICC_IAR); // 读取中断号  
handle_domain_irq(...); // 进入通用层
```

---

你 AX7020 一定会用：`IRQ_F2P[15:0]`

PL 中断怎么接到 GIC？
多个中断怎么 multiplex？
latency 会不会变？

---

Zynq 用的是：GICv1 (Cortex-A9)，你要理解：Distributor、CPU Interface、SGI / PPI / SPI。

研究方法：不要“看代码”，要**带问题追踪一条中断**



## 三、irqdomain

主线索：
1、重点源文件：kernel/irq/irqdomain.c
2、作用：把硬件中断号 → Linux 虚拟 irq号
3、关键函数：不理解这个，你永远搞不清 irq number 从哪来的
```cpp
irq_create_mapping()  
irq_find_mapping()
```

---

设备树描述：arch/arm/boot/dts/zynq-7000.dtsi
例子：interrupts = <0 61 4>;   0表示SPI，61表示hwirq，4表示触发方式。
这和 irq domain 是直接关联的








## 四、generic IRQ 层


主线索：

1、重点文件：
```txt
kernel/irq/irqdesc.c
kernel/irq/handle.c
kernel/irq/manage.c
```

2、关键函数链：这就是最终调用你驱动的地方
```cpp
handle_domain_irq()  
	→ generic_handle_irq()  
		→ __handle_irq_event_percpu()  
			→ action->handler()
```


## 五、驱动层（申请irq）


1、典型代码：request_irq(irq, handler, flags, name, dev);

你要反向理解：
request_irq 做了什么？
handler 是怎么被挂进去的？


## 六、摸底试题


如果你能回答这几个问题，就算吃透了：
1. 中断从 FPGA 到 CPU 的完整路径？
2. IRQ number 是怎么生成的？
3. irq domain 为什么存在？
4. request_irq 到底做了什么？
5. GIC 是怎么决定哪个 CPU 收中断？
6. edge 和 level 在内核里如何处理？
7. 为什么会有中断丢失 / storm？
















# 驱动总结

## ❌ Level 0

- 会跑 demo
- 改参数
- 看不懂驱动 API

👉 ❗ 不建议doc

## ⚠️ Level 1

你能解释：

- DMA 基本原理
- 数据流方向
- 大致流程

👉 但：

- 不懂 SG
- 不懂 cache
- 不懂内核 API

👉 ds容易被刷


## ✅ Level 2

你必须能：

---

### ✔ 1. 完整数据路径

用户态 buffer  
→ 内核 pin page  
→ SG list  
→ DMA mapping  
→ 硬件传输

---

### ✔ 2. 关键 API 的作用

至少要懂：

- `dma_map_sg`
- `dmaengine_prep_slave_sg`
- `dma_async_issue_pending`
- `dmaengine_submit`

---

### ✔ 3. 解释性能问题

比如：

- 为什么 SG 多会变慢
- 为什么 burst=16 是 sweet spot

---

👉 到这里：

> ✔ 可以 confidently 写进简历  
> ✔ 能过大部分面试

---

## 🔥 Level 3（高质量项目）

如果你做到这些：

---

### 🚀 1. 做过性能优化

比如：

- SG 优化（减少段数）
- HP port 分配
- burst 调优

---

### 🚀 2. 做过架构改进

比如：

- 用户态 mmap DMA buffer（零拷贝）
- 替换 read/write 路径

---

### 🚀 3. 能画架构图

👉 这个非常加分：

User → Driver → DMAEngine → AXI DMA → DDR

---

👉 到这个程度：

> 💰 可以冲中高级驱动岗






# (TODO)Linux DMA Engine 和 AXI DMA








# 理解 ZYNQ-AXI 流式传输




## AXI-Stream：我有数据你要不要



<font color=blue>作为DMA传输的两个目标，为什么外设侧更倾向于用stream？</font>

本质上是在问：为什么 DMA 的一端（外设）几乎总是 AXI-Stream，而不是 AXI Memory-Mapped？

MM 是基于（Address-based），Stream是基于（Data-based）；

这些外设的特点：
- 1、不会停下来等你；
- 2、没有地址概念，只有数据，比如ADC 根本不知道写到哪个地址；
- 3、TVALID、TREADY：我ADC此刻有数据了(TVALID=1)，DMA此刻就绪(TREADY=1)
- 4、ADC场景: ADC → FIFO → AXI-Stream → DMA


DMA **不用关心设备内部地址**，
很多外设(ADC、网络、视频采集等)它们的典型特征是：“**我什么时候有数据，我说了算**”

AXI-Stream 正好表达了这件事：
- 我有数据 → `TVALID`
- 你能接 → `TREADY`
于是DMA 只需要“接水管”。

Stream 的概念里，提到了背压(Backpressure)，AXI-Stream 天然支持背压，作为发送方，比如 TVALID=1(我有数据)，且 TREADY=1(你能接)，数据才会"真正传输"；两个条件必须同时满足，数据才能流动起来。当接收方接不住(TREADY=0)，发送方必须停住，数据保持不变，不丢数据、不乱序，这就是背压。

ADC系统是一个特殊的硬实时工程场景，也就是说ADC一旦开始采集，就没法停下来，因为ADC采集的是物理世界的信号，物理世界的信号不会因为你接收端慢了就停下来等等你。所以在工程结构上，ADC采到数据后，会先经过一个 FIFO，再从 FIFO 给到接收端。

FIFO 天生适合做：TVALID、TREADY，比如：
```cpp
TVALID <= (!fifo_empty);
TREADY <= (!fifo_full);
```


![[Pasted image 20260119222345.png]]

如上图所示，ADC一旦开始工作，就像一个一直出水的水龙头，水流经过水桶然后提供给系统，正常情况下，水桶里的水一直不会满，此时系统接收速度快于ADC采集速度，但凡速度相等或者慢于ADC，那么水桶早晚会满。当系统短时间内接收不过来时，水龙头并不会停止，水桶里的水会越来越多，只要水桶装满之前系统能及时消耗掉水桶里的水，水桶就不会满，就不会丢数据。

ADC 系统永远存在“可能丢数据”的风险，FIFO 只是把这个风险推迟。
所以工程师关心的不是：“会不会丢”，而是 “在最坏情况下，FIFO 能撑多久？”



<font color=blue>用最简单的伪代码(verilog)来描述 TVALID和 TREADY 的配合逻辑。</font>

```verilog
// 当只有在这一拍：
if (TVALID && TREADY)
	// 数据真正被“传输成功”,这是唯一的“数据生效条件”
```

发送端(比如ADC)负责：提供数据（TDATA）、拉高 TVALID 表示“我有数据”
```verilog
if (TVALID && !TREADY) // 如果我有数据了,但你还没准备接收
	// 必须保持：  
	TVALID = 1  
	TDATA 不变     // 不能变,因为不能丢数
```


接收端负责：拉高 TREADY 表示“我可以接收”
```cpp
// 接收端Sink代码
always @(posedge clk) begin
    if (rst) begin
        TREADY <= 0;
    end
    else begin
        if (can_accept_data) begin  // 是否能接收,取决于该位置
            TREADY <= 1;
        end else begin
            TREADY <= 0;
        end
    end
end

// 接收数据逻辑
always @(posedge clk) begin
    if (TVALID && TREADY) begin
        // 真正接收数据
        fifo_write(TDATA);
    end
end
```



如下图所示，下图就刚好形象展示了 TVALID 的含义，比如外设有数据给 axi dma，会通过 s_axis_s2mm_tvalid 告诉 axi dma "我有数据了你要不要"，而 m_axis_mm2s_tvalid 则用来往外设写入数据时需要拉高的信号，告诉外设 "我有数据了你要不要"。
![[Pasted image 20260318172917.png]]





## AXI transaction：我要往某地址写1KB数据


AXI transaction = 一次“带地址的总线操作”，也就是一次完整的读 或 写 请求。

比如写请求，你可以理解为："**我要往 0x1000 写 4KB 数据**"，这就是一个 transaction。

先地址，再数据，也就是先有“访问意图”，再有数据传输。

而 AXI-Stream：没有地址、没有读写请求，它只有 TVALID / TREADY / TDATA。

transaction 里包含：burst（突发）、len（长度）、size（每拍字节）。

AXI-Stream 的一次 TVALID/TREADY 是一个 transaction，这是错误理解，只是一个 data beat。



<font color=blue>为什么有的外设能使用DMA，有的外设不支持使用DMA呢？</font>

DMA 控制器是系统的 “专用数据搬运工”，但它无法主动感知外设的 “数据就绪 / 空闲” 状态，也无法直接操作任意外设寄存器 ——**外设必须为 DMA 做专门的硬件设计**，拥有**DMA 可直接访问的专用数据寄存器**，「写寄存器」：DMA 控制器向该寄存器写数据时，外设能直接将数据发送出去（如 UART 的发送数据寄存器 TDR）；「读寄存器」：外设将采集 / 接收的数据存入该寄存器后，DMA 控制器能直接从寄存器中读取数据。且数据写入 / 读取后，外设硬件会自动完成后续操作。



<font color=blue>axidma 100MHz的时钟，max burst size = 16beats，data width=32bit，这个16虽然是官方提供的默认值，我觉得也是官方综合考量的平衡值，太大会过多占用 HP总线带宽，太少传输效率也高不起来，那么这个值，从更底层的角度（比如总线带宽），如何依据底层角度来确定这个 burst size 值？
</font>

你这个问题已经到了**能做 trade-off 的工程师”才会问的层级了** 👍
👉 一次 burst 传输数据量：16 × 4B = 64 Bytes
👉 理论带宽（不考虑任何开销）：100 MHz × 4B = 400 MB/s

但现实中达不到，因为：
👉 **总线不是一直在“传数据”，而是：** 
地址阶段 + 仲裁 + 数据阶段 + 空隙 + 地址阶段 + 仲裁 + 数据阶段 + 空隙 ...

关键底层模型：**为什么 burst 会影响带宽？**
👉 **burst 越大，“地址/仲裁开销”被摊薄得越少**，也就是这些固定开销的占比越小。

每次 burst：
1️⃣ 发一次地址（AW/AR）  
2️⃣ 仲裁（可能等待）  
3️⃣ 连续传 N 个数据 beat  
4️⃣ 结束

👉 用一个简化模型表示：
- 地址+仲裁开销 = T_overhead（单位：cycle）
- burst = N beats
👉 总耗时：T_total = T_overhead + N
👉 有效带宽利用率：Efficiency = N / (T_overhead + N)

👉 T_overhead ≈ 10~20 cycles（仲裁 + 地址 + pipeline）（Zynq HP口很典型）
我们取：T_overhead = 16 cycles

**计算不同 burst 的效率**

🔹 burst = 4 时：Efficiency = 4 / (16 + 4) = 20% 很差 ❌
🔹 burst = 16 时：Efficiency = 16 / (16 + 16) = 50% 明显提升 ✔
🔹 burst = 64 时：Efficiency = 64 / (16 + 64) ≈ 80% 很高 ✔✔
🔹 burst = 256 时：Efficiency ≈ 94% 接近极限 ✔✔✔

**那为什么不用 256？（关键 trade-off）**
总线占用时间变长（最核心）
256 beats × 1 cycle = 256 cycles，100MHz，256 cycles = 256


2️⃣ HP port / DDR 控制器限制
👉 **它本身也在做调度（reorder / QoS / page policy）**
如果 burst 太大：
- 可能跨 row（DDR row miss）
- 影响 DDR efficiency
- 阻塞其他 master（CPU / GPU / other DMA）


<font color=blue>为什么有些系统不用大 burst，而是用“多 outstanding transaction”？
</font>

👉 **“大 burst 是线性优化，多 outstanding 是并行优化”**

**为什么“多 outstanding”更高级？**

核心原因：
👉 **现代瓶颈不在 AXI，而在 DDR（内存系统）**

DDR 的真实工作方式（关键理解点）
DDR 不是“线性读写”，而是：👉 **bank + row + column**


1️⃣ **Row hit vs Row miss**
- ✔ row hit：很快
- ❌ row miss：要 precharge + activate（很慢）
2️⃣ **DDR 可以并行（多 bank）**


✅ **多 outstanding 的优势**

**比如：多 outstanding（4个请求）**

请求1（miss）  
请求2（hit）  
请求3（hit）  
请求4（miss）

👉 DDR controller 会：先做 请求2/3 → 再做 1/4
👉 总线几乎不空转 ✔


👉 为什么有些 DMA（比如 Xilinx AXI DMA）：
- burst 不大（默认16）
- 但 throughput 依然不错？
👉 答案就在：
👉 **它内部已经在做 pipeline / outstanding**




# ZYNQ-AXI-DMA引擎优化


在实际测试中发现一个问题，当 axidma ip 核没有勾选 sg 模式的时候，在嵌入式Linux系统里，运行带宽例程，如果单向传输长度超过 Buffer Length 指定的最大长度，就会超时，且超时后如果再次重新传输，无法停止上一次的传输。

```bash
# 当 axidma ip 核没有勾选 sg 模式
zynq> ./app_bandwidth.elf 18MB 18MB                   # 最大BufferLen=16MB-1
axidma_v007: loading out-of-tree module taints kernel.
called axidma_probe
axidma probe success
cmdline=insmod axidma_v007.ko tx_bufsize=18MB rx_bufsize=18MB
iterations  = 10
tx_bufsz    = 18MB (18874368 Bytes)
rx_bufsz    = 18MB (18874368 Bytes)
mmap success: tx=0xb5d35000 rx=0xb4b35000
tx_thread: iterations = 10
tx_thread: tx_bufsz   = 18874368
rx_thread: iterations = 10
rx_thread: rx_bufsz   = 18874368
data check error
random: fast init done
start_tx_dma: timeout (max_timeout_ms=30000)
[tx_thread] write failed Connection timed out
zynq> ./app_bandwidth.elf 18MB 18MB                   # 最大BufferLen=16MB-1
remove axidma0
xilinx-vdma 40400000.dma: Cannot stop channel (ptrval): 0 # 无法停止上一次的引擎
called axidma_probe
axidma probe success
cmdline=insmod axidma_v007.ko tx_bufsize=18MB rx_bufsize=18MB
iterations  = 10
tx_bufsz    = 18MB (18874368 Bytes)
rx_bufsz    = 18MB (18874368 Bytes)
mmap success: tx=0xb5d9b000 rx=0xb4b9b000
tx_thread: iterations = 10
tx_thread: tx_bufsz   = 18874368
rx_thread: iterations = 10
rx_thread: rx_bufsz   = 18874368
data check error
start_tx_dma: timeout (max_timeout_ms=30000)
[tx_thread] write failed Connection timed out
zynq> 
```
















# bottom




