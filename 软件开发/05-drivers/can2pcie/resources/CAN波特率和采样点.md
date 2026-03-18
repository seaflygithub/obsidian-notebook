
## CAN波特率

🎯 假设有如下参数：can时钟为24MHz
BRP = 59  
TSEG1 = 15  
TSEG2 = 2  
SJW = 3

✅ 波特率计算：
$$
波特率 = \frac{CAN\_CLK}{(BRP+1) \times (1+TSEG1+TSEG2)}
=\frac{24000000}{60 \times (1+16+3)}
=20(Kbps)
$$

✅ 总TQ计算式子：
$$
总TQ = 1TQ + TSEG1 + TSEG2 = 1 + 16 + 3 = 20
$$

✅ 单个 TQ 时间
$$
TQ = T \times (BRP+1) = \frac{1}{CAN\_CLK} \times (BRP+1)
$$

👉 重点：
>👉 TQ越多 = 一个 bit 被“切得更细”；TQ多 → 可调整空间更大
>👉 TSEG2 ≥ 2 会明显更稳，而 TQ 大 → 更容易给 TSEG2 留空间

---
## CAN采样点


✅ 采样点位置计算：✔ 采样点在哪里？
$$
采样点位置=\frac{(1+TSEG1)}{(1+TSEG1+TSEG2)} = \frac{16}{(1+16+3)} \times 100\% = 80\%
$$

✅ 工程推荐值（采样点）

| 场景        | 推荐采样点       | 备注                    |
| --------- | ----------- | --------------------- |
| 高速（≥500K） | 75% ~ 87.5% | 速度越高越往中间靠，毕竟越靠边越接近亚稳态 |
| 中速（250K）  | ~80%        |                       |
| 低速（≤100K） | 80%+        |                       |

**当你调 CAN 参数时，优先级这样走**：  
**1️⃣** TSEG ≥ 1
**2️⃣** 采样点尽量落在80%左右
**3️⃣** 确保总TQ尽量大

---

## CAN波特率参考值

下面是调试验证通过的 A7 Microblaze 官方例程波特率参数：

```cpp
// Final formula: BAUD=CAN_CLK/((BRP+1)*(1+TSEG1+1+TSEG2+1))

// // 12MHz --> baud=20K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    29
// #define TEST_BTR_SYNCJUMPWIDTH		3
// #define TEST_BTR_FIRST_TIMESEGMENT	15
// #define TEST_BTR_SECOND_TIMESEGMENT	2


// // 24MHz --> baud=1000K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    2
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	4
// #define TEST_BTR_SECOND_TIMESEGMENT	1


// // 24MHz --> baud=800K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    2
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	5
// #define TEST_BTR_SECOND_TIMESEGMENT	2


// // 24MHz --> baud=500K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    5
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	4
// #define TEST_BTR_SECOND_TIMESEGMENT	1


// // 24MHz --> baud=250K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    5
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	11
// #define TEST_BTR_SECOND_TIMESEGMENT	2


// // 24MHz --> baud=125K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    11
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	11
// #define TEST_BTR_SECOND_TIMESEGMENT	2


// 24MHz --> baud=100K --> (rx/tx)OK
#define TEST_BRPR_BAUD_PRESCALAR	    14
#define TEST_BTR_SYNCJUMPWIDTH		1
#define TEST_BTR_FIRST_TIMESEGMENT	11
#define TEST_BTR_SECOND_TIMESEGMENT	2


// // 24MHz --> baud=50K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    29
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	11
// #define TEST_BTR_SECOND_TIMESEGMENT	2


// // 24MHz --> baud=20K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    59
// #define TEST_BTR_SYNCJUMPWIDTH		3
// #define TEST_BTR_FIRST_TIMESEGMENT	15
// #define TEST_BTR_SECOND_TIMESEGMENT	2


// // 24MHz --> baud=20K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    59
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	15
// #define TEST_BTR_SECOND_TIMESEGMENT	2
```




✅ 24MHz 高速/中速体系（8~16 TQ）

| CAN波特率 | 预分频BRP | SJW    | TSEG1 | TSEG2  | 总TQ    | 特点    |
| ------ | ------ | ------ | ----- | ------ | ------ | ----- |
| 1M     | 2      | 1(1~2) | 4     | 1      | 8(>=8) | 极限    |
| 800K   | 2      | 1(1~2) | 5     | 2(>=2) | 10     | 折中    |
| 500K   | 5      | 1(1~2) | 4     | 1      | 8      | 标准    |
| 250K   | 5      | 1(1~2) | 11    | 2      | 16     | 稳定    |
| 125K   | 11     | 1(1~2) | 11    | 2      | 16     | 高稳定   |
| 100K   | 14     | 1(1~2) | 11    | 2      | 16     | 强稳定   |
| 50K    | 29     | 2(1~2) | 11    | 2      | 16     | 低速工业  |
| 20K    | 59     | 3(1~2) | 15    | 2      | 20     | 低速强稳定 |


可以把一些必要的信息告诉AI，让AI帮你计算合适参数：
- CAN时钟频率（比如 24MHz）
- CAN总线线长（比如 30cm内）
- CAN芯片型号（比如 SIT1050）
- 你想要配置的目标波特率是多少（比如 100K）


## xcan_intr_example.c

下面是 A7 板 microblaze 官方例程修改之后的代码，运行流程是：
- 1、打印发送倒计时（16秒）；
- 2、开始发送标准帧（标准帧：数据最多8字节）；
- 3、打印接收倒计时（30秒，倒计时期间，对端完成标准帧发送，发给microblaze）。
- 4、倒计时结束，例程将打印总共收到的帧数（用来统计丢帧数）。


```cpp
/******************************************************************************
*
* Copyright (C) 2005 - 2018 Xilinx, Inc.  All rights reserved.
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
/****************************************************************************/
/**
*
* @file xcan_intr_example.c
*
* Contains an example of how to use the XCan driver directly.  The example here
* shows using the driver/device in interrupt mode.
*
* @note
*
* This code assumes that Xilinx interrupt controller (XIntc) is used in the
* system to forward the CAN device interrupt output to the processor and no
* operating system is being used.
*
* The Baud Rate Prescaler Register (BRPR) and Bit Timing Register (BTR)
* are setup such that CAN baud rate equals 40Kbps, assuming that the
* the CAN clock is 24MHz. The user needs to modify these values based on
* the desired baud rate and the CAN clock frequency. For more information
* see the CAN 2.0A, CAN 2.0B, ISO 11898-1 specifications.
*
* <pre>
* MODIFICATION HISTORY:
*
* Ver   Who	Date	 Changes
* ----- -----  -------- -----------------------------------------------
* 1.00a xd/sv	01/12/09 First release
* 2.00a ktn	10/22/09 Updated to use the HAL APIs/macros.
*			 The macros have been renamed to remove _m from the
*			 name.
* 2.00a bss	01/11/11 Updated the example to be used with the SCUGIC in
*			 Zynq.
* 2.00a bss	01/16/12 Updated the example to fix CR 694533,
*			 replaced INTC_DEVID with INTC_DEVICE_ID.
* 3.2   ms  01/23/17 Added xil_printf statement in main function to
*                    ensure that "Successfully ran" and "Failed" strings are
*                    available in all examples. This is a fix for CR-965028.
* 3.3   ask  08/01/18 Fixed Cppcheck and GCC warnings in can driver
* </pre>
*
******************************************************************************/

/***************************** Include Files *********************************/

#include "xcan.h"
#include "xparameters.h"
#include "xstatus.h"
#include "xil_exception.h"
#include "sleep.h"

#ifdef XPAR_INTC_0_DEVICE_ID
#include "xintc.h"
#include <stdio.h>
#else  /* SCU GIC */
#include "xscugic.h"
#include "xil_printf.h"
#endif

/************************** Constant Definitions *****************************/

/*
 * The following constants map to the XPAR parameters created in the
 * xparameters.h file. They are defined here such that a user can easily
 * change all the needed parameters in one place.
 */
#define CAN_DEVICE_ID		XPAR_CAN_0_DEVICE_ID
#define CAN_INTR_VEC_ID		XPAR_INTC_0_CAN_0_VEC_ID

#ifdef XPAR_INTC_0_DEVICE_ID
 #define INTC_DEVICE_ID		XPAR_INTC_0_DEVICE_ID
#else
 #define INTC_DEVICE_ID		XPAR_SCUGIC_SINGLE_DEVICE_ID
#endif /* XPAR_INTC_0_DEVICE_ID */


/* Maximum CAN frame length in word */
#define XCAN_MAX_FRAME_SIZE_IN_WORDS (XCAN_MAX_FRAME_SIZE / sizeof(u32))

#define FRAME_DATA_LENGTH	8 /* Frame Data field length */
static unsigned long recved_frame_count = 0;

/*
 * Message Id Constant.
 */
#define TEST_MESSAGE_ID			0x616

/*
 * The Baud Rate Prescaler Register (BRPR) and Bit Timing Register (BTR)
 * are setup such that CAN baud rate equals 40Kbps, assuming that the
 * the CAN clock is 24MHz. The user needs to modify these values based on
 * the desired baud rate and the CAN clock frequency. For more information
 * see the CAN 2.0A, CAN 2.0B, ISO 11898-1 specifications.
 */
// Final formula: BAUD=CAN_CLK/((BRP+1)*(1+TSEG1+1+TSEG2+1))

// // 12MHz --> baud=20K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    29
// #define TEST_BTR_SYNCJUMPWIDTH		3
// #define TEST_BTR_FIRST_TIMESEGMENT	15
// #define TEST_BTR_SECOND_TIMESEGMENT	2





// // 24MHz --> baud=1000K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    2
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	4
// #define TEST_BTR_SECOND_TIMESEGMENT	1


// // 24MHz --> baud=800K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    2
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	5
// #define TEST_BTR_SECOND_TIMESEGMENT	2


// // 24MHz --> baud=500K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    5
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	4
// #define TEST_BTR_SECOND_TIMESEGMENT	1


// // 24MHz --> baud=250K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    5
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	11
// #define TEST_BTR_SECOND_TIMESEGMENT	2


// // 24MHz --> baud=125K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    11
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	11
// #define TEST_BTR_SECOND_TIMESEGMENT	2


// 24MHz --> baud=100K --> (rx/tx)OK
#define TEST_BRPR_BAUD_PRESCALAR	    14
#define TEST_BTR_SYNCJUMPWIDTH		1
#define TEST_BTR_FIRST_TIMESEGMENT	11
#define TEST_BTR_SECOND_TIMESEGMENT	2


// // 24MHz --> baud=50K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    29
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	11
// #define TEST_BTR_SECOND_TIMESEGMENT	2


// // 24MHz --> baud=20K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    59
// #define TEST_BTR_SYNCJUMPWIDTH		3
// #define TEST_BTR_FIRST_TIMESEGMENT	15
// #define TEST_BTR_SECOND_TIMESEGMENT	2


// // 24MHz --> baud=20K --> (rx/tx)OK
// #define TEST_BRPR_BAUD_PRESCALAR	    59
// #define TEST_BTR_SYNCJUMPWIDTH		1
// #define TEST_BTR_FIRST_TIMESEGMENT	15
// #define TEST_BTR_SECOND_TIMESEGMENT	2


#ifdef XPAR_INTC_0_DEVICE_ID
#define INTC		XIntc
#define INTC_HANDLER	XIntc_InterruptHandler
#else
#define INTC		XScuGic
#define INTC_HANDLER	XScuGic_InterruptHandler
#endif /* XPAR_INTC_0_DEVICE_ID */


/**************************** Type Definitions *******************************/


/***************** Macros (Inline Functions) Definitions *********************/


/************************** Function Prototypes ******************************/
static void print_timewait(const char *prefix, u32 timeoutSec);
static int XCanIntrExample(u16 DeviceId);
static void Config(XCan *InstancePtr);
static void SendFrame(XCan *InstancePtr);

static void SendHandler(void *CallBackRef);
static void RecvHandler(void *CallBackRef);
static void ErrorHandler(void *CallBackRef, u32 ErrorMask);
static void EventHandler(void *CallBackRef, u32 Mask);

static int SetupInterruptSystem(XCan *InstancePtr);

/************************** Variable Definitions *****************************/

/*
 * Allocate an instance of the XCan driver
 */
static XCan Can;

/*
 * Buffers to hold frames to send and receive. These are declared as global so
 * that they are not on the stack.
 * These buffers need to be 32-bit aligned
 */
static u32 TxFrame[XCAN_MAX_FRAME_SIZE_IN_WORDS];
static u32 RxFrame[XCAN_MAX_FRAME_SIZE_IN_WORDS];

/*
 * Shared variables used to test the callbacks.
 */
volatile static int LoopbackError;	/* Asynchronous error occurred */
volatile static int RecvDone;		/* Received a frame */
volatile static int SendDone;		/* Frame was sent successfully */

/*****************************************************************************/
/**
*
* This function is the main function of the Can interrupt example.
*
* @param	None.
*
* @return
*		- XST_SUCCESS if the example has completed successfully.
*		- XST_FAILURE if the example has failed.
*
* @note		None.
*
*****************************************************************************/
int main()
{
	/*
	 * Run the Can interrupt example.
	 */
	if (XCanIntrExample(CAN_DEVICE_ID)) {
		xil_printf("Can Interrupt Example Failed\r\n");
		while(1);
		return XST_FAILURE;
	}

	// xil_printf("Successfully ran Can Interrupt Example\r\n");

	while(1);
	return XST_SUCCESS;
}

/*****************************************************************************/
/**
*
* The main entry point for showing the XCan driver in interrupt mode.
* The example configures the device for internal loopback mode, then
* sends a CAN frame and receives the same CAN frame.
*
* @param	DeviceId contains the CAN device ID.
*
* @return	XST_SUCCESS if successful, otherwise driver-specific error code.
*
* @note 	If the device is not working correctly, this function may enter
*		an infinite loop and will never return to the caller.
*
******************************************************************************/
static int XCanIntrExample(u16 DeviceId)
{
	int Status;

	/*
	 * Initialize the XCan driver.
	 */
	Status = XCan_Initialize(&Can, DeviceId);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	/*
	 * Run self-test on the device, which verifies basic sanity of the
	 * device and the driver.
	 */
	// Status = XCan_SelfTest(&Can);
	// if (Status != XST_SUCCESS) {
	// 	return XST_FAILURE;
	// }

	/*
	 * Configure the CAN device.
	 */
	Config(&Can);

	/*
	 * Set interrupt handlers.
	 */
	XCan_SetHandler(&Can, XCAN_HANDLER_SEND,
			(void *)SendHandler, (void *)&Can);
	XCan_SetHandler(&Can, XCAN_HANDLER_RECV,
			(void *)RecvHandler, (void *)&Can);
	XCan_SetHandler(&Can, XCAN_HANDLER_ERROR,
			(void *)ErrorHandler, (void *)&Can);
	XCan_SetHandler(&Can, XCAN_HANDLER_EVENT,
			(void *)EventHandler, (void *)&Can);

	/*
	 * Initialize flags.
	 */
	SendDone = FALSE;
	RecvDone = FALSE;
	LoopbackError = FALSE;

	/*
	 * Connect to the interrupt controller.
	 */
	Status = SetupInterruptSystem(&Can);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	/*
	 * Enable all interrupts in CAN device.
	 */
	XCan_InterruptEnable(&Can, XCAN_IXR_ALL);

	/*
	 * Enter Loop Back Mode.
	 */
	XCan_EnterMode(&Can, XCAN_MODE_NORMAL);
	while(XCan_GetMode(&Can) != XCAN_MODE_NORMAL);

	/*
	 * Loop back a frame. The RecvHandler is expected to handle
	 * the frame reception.
	 */

	int count_index = 0;
	int count_total = 1000;

	// 打印倒计时, 倒计时结束后执行后续动作
	print_timewait("Will send 1000 frames", 16);

	for (count_index=0; count_index<count_total; count_index++)
	{
		SendFrame(&Can); /* Send a frame */
		u8 *FramePtr = (u8 *)(&TxFrame[2]);
		// xil_printf("[%d/%d] TxFrame[]=%08x %08x %02x %02x %02x %02x %02x %02x %02x %02x\r\n",
		// 	count_index+1,
		// 	count_total,
		// 	TxFrame[0],
		// 	TxFrame[1],
		// 	FramePtr[0],
		// 	FramePtr[1],
		// 	FramePtr[2],
		// 	FramePtr[3],
		// 	FramePtr[4],
		// 	FramePtr[5],
		// 	FramePtr[6],
		// 	FramePtr[7]
		// );


		// 下面是 microblaze这边以 100K 波特率发送帧给CAN分析仪的总线利用率测试统计
		// sleep(1); // 总线利用率: 0.555%
		// usleep(100000); // 总线利用率: 1.110%
		// usleep(10000); // 总线利用率: 10.5%, 接收端未丢帧
		// usleep(5000); // 总线利用率: 21.0%, 接收端未丢帧
		// usleep(2000); // 总线利用率: 50%, 接收端未丢帧
		// usleep(1500); // 总线利用率: 70+%, 接收端未丢帧
		usleep(1100); // 总线利用率: 90+%, 接收端未丢帧
	}


	/*
	 * Wait here until both sending and reception have been completed.
	 */
	// while ((SendDone != TRUE) || (RecvDone != TRUE));
	
	while (RecvDone != TRUE);

	// 收到第1帧就会打印这个超时提示, 这里30秒足够CAN分析仪连续发完很多帧了
	print_timewait("Will show recved_frame_count", 30);

	// CAN分析仪尽量快速发送一定数量的帧数据,看看 microblaze 这边接收会不会因为丢帧
	// CAN分析仪那边发送了多少帧是已知, 来对比 microblaze 这边的接收统计来看是否丢帧
	xil_printf("Error=%d, recved_frame_count = %lu\r\n", LoopbackError, recved_frame_count);


	/*
	 * Check for errors found in the callbacks.
	 */
	if (LoopbackError == TRUE) {
		return XST_LOOPBACK_ERROR;
	}



	return XST_SUCCESS;
}

/*****************************************************************************/
/**
*
* This function configures CAN device. Baud Rate Prescaler Register (BRPR) and
* Bit Timing Register (BTR) are set in this function.
*
* @param	InstancePtr is a pointer to the driver instance
*
* @return	None.
*
* @note		If the CAN device is not working correctly, this function may
*		enter an infinite loop and will never return to the caller.
*
******************************************************************************/
static void Config(XCan *InstancePtr)
{
	/*
	 * Enter Configuration Mode if the device is not currently in
	 * Configuration Mode.
	 */
	XCan_EnterMode(InstancePtr, XCAN_MODE_CONFIG);
	while(XCan_GetMode(InstancePtr) != XCAN_MODE_CONFIG);

	/*
	 * Setup Baud Rate Prescaler Register (BRPR) and
	 * Bit Timing Register (BTR) such that CAN baud rate equals 40Kbps,
	 * given the CAN clock frequency equal to 24MHz.
	 */
	XCan_SetBaudRatePrescaler(InstancePtr, TEST_BRPR_BAUD_PRESCALAR);
	XCan_SetBitTiming(InstancePtr, TEST_BTR_SYNCJUMPWIDTH,
					TEST_BTR_SECOND_TIMESEGMENT,
					TEST_BTR_FIRST_TIMESEGMENT);
}

/*****************************************************************************/
/**
*
* Send a CAN frame.
*
* @param	InstancePtr is a pointer to the driver instance.
*
* @return	None.
*
* @note		None.
*
******************************************************************************/
static void SendFrame(XCan *InstancePtr)
{
	u8 *FramePtr;
	int Index;
	int Status;

	/*
	 * Create correct values for Identifier and Data Length Code Register.
	 */
	TxFrame[0] = XCan_CreateIdValue(TEST_MESSAGE_ID, 0, 0, 0, 0);
	TxFrame[1] = XCan_CreateDlcValue(FRAME_DATA_LENGTH);
	// xil_printf("MSGID=0x%x, TxFrame[1]=%08x\r\n", (TxFrame[0] & 0xFFE00000) >> 21, TxFrame[1]);

	/*
	 * Now fill in the data field with known values so we can verify them
	 * on receive.
	 */
	// FramePtr = (u8 *)(&TxFrame[2]);
	// for (Index = 0; Index < FRAME_DATA_LENGTH; Index++) {
	// 	*FramePtr++ = (u8)Index;
	// }
	u32 *dword = (u32 *)(&TxFrame[2]);
	dword[0] = 0x11223344;
	dword[1] = 0x55667788;


	/*
	 * Now wait until the TX FIFO is not full and send the frame.
	 */
	while (XCan_IsTxFifoFull(InstancePtr) == TRUE);

	Status = XCan_Send(InstancePtr, TxFrame);
	if (Status != XST_SUCCESS) {
		/* The frame could not be sent successfully */
		LoopbackError = TRUE;
		SendDone = TRUE;
		RecvDone = TRUE;
	}
}


/*****************************************************************************/
/**
*
* Callback function (called from interrupt handler) to handle confirmation of
* transmit events when in interrupt mode.
*
* @param	CallBackRef is the callback reference passed from the interrupt
*		handler, which in our case is a pointer to the driver instance.
*
* @return	None.
*
* @note		This function is called by the driver within interrupt context.
*
******************************************************************************/
static void SendHandler(void *CallBackRef)
{
	/*
	 * The frame was sent successfully. Notify the task context.
	 */
	SendDone = TRUE;
}


/*****************************************************************************/
/**
*
* Callback function (called from interrupt handler) to handle frames received in
* interrupt mode.  This function is called once per frame received.
* The driver's receive function is called to read the frame from RX FIFO.
*
* @param	CallBackRef is the callback reference passed from the interrupt
*		handler, which in our case is a pointer to the device instance.
*
* @return	None.
*
* @note		This function is called by the driver within interrupt context.
*
******************************************************************************/
static void RecvHandler(void *CallBackRef)
{
	XCan *CanPtr = (XCan *)CallBackRef;
	int Status;
	int Index;
	u8 *FramePtr;
	

	Status = XCan_Recv(CanPtr, RxFrame);
	if (Status != XST_SUCCESS) {
		LoopbackError = TRUE;
		RecvDone = TRUE;
		return;
	}

	/*
	 * Verify Identifier and Data Length Code.
	 */
	// if (RxFrame[0] != XCan_CreateIdValue(TEST_MESSAGE_ID, 0, 0, 0, 0)) {
	// 	LoopbackError = TRUE;
	// 	RecvDone = TRUE;
	// 	return;
	// }

	// if (RxFrame[1] != XCan_CreateDlcValue(FRAME_DATA_LENGTH)) {
	// 	LoopbackError = TRUE;
	// 	RecvDone = TRUE;
	// 	return;
	// }

	// /*
	// * Verify Data field contents.
	// */
	// FramePtr = (u8 *)(&RxFrame[2]);
	// for (Index = 0; Index < FRAME_DATA_LENGTH; Index++){
	// 	if (*FramePtr++ != (u8)Index) {
	// 		LoopbackError = TRUE;
	// 		break;
	// 	}
	// }


	{
		FramePtr = (u8 *)(&RxFrame[2]);
		recved_frame_count += 1;

		// xil_printf("%lu: RxFrame\r\n",++count);

		// xil_printf("%s(): RecvDone\r\n", __func__);
		// xil_printf("%lu: RxFrame[]=%08x %08x %02x %02x %02x %02x %02x %02x %02x %02x\r\n",
		// 	++count,
		// 	RxFrame[0],
		// 	RxFrame[1],
		// 	FramePtr[0],
		// 	FramePtr[1],
		// 	FramePtr[2],
		// 	FramePtr[3],
		// 	FramePtr[4],
		// 	FramePtr[5],
		// 	FramePtr[6],
		// 	FramePtr[7]
		// );
	}


	RecvDone = TRUE;
}


/*****************************************************************************/
/**
*
* Callback function (called from interrupt handler) to handle error interrupt.
* Error code read from Error Status register is passed into this function
*
* @param	CallBackRef is the callback reference passed from the interrupt
*		handler, which in our case is a pointer to the driver instance.
* @param	ErrorMask is a bit mask indicating the cause of the error. Its
*		value equals 'OR'ing one or more XCAN_ESR_* defined in xcan_l.h
*
* @return	None.
*
* @note		This function is called by the driver within interrupt context.
*
******************************************************************************/
static void ErrorHandler(void *CallBackRef, u32 ErrorMask)
{
	LoopbackError = TRUE;
	RecvDone = TRUE;
	SendDone = TRUE;

	if(ErrorMask & XCAN_ESR_ACKER_MASK) {
		/*
		 * ACK Error handling code should be put here.
		 */
		// 如果Microblaze发送数据出去，
		// 如果总线上没有对端接收，就会发生该错误
		LoopbackError = FALSE;
	}

	if(ErrorMask & XCAN_ESR_BERR_MASK) {
		/*
		 * Bit Error handling code should be put here.
		 */
	}

	if(ErrorMask & XCAN_ESR_STER_MASK) {
		/*
		 * Stuff Error handling code should be put here.
		 */
	}

	if(ErrorMask & XCAN_ESR_FMER_MASK) {
		/*
		 * Form Error handling code should be put here.
		 */
	}

	if(ErrorMask & XCAN_ESR_CRCER_MASK) {
		/*
		 * CRC Error handling code should be put here.
		 */
	}

	// /*
	//  * Set the shared variables.
	//  */
	// LoopbackError = TRUE;
	// RecvDone = TRUE;
	// SendDone = TRUE;

	// xil_printf("%s(): ErrorMask=0x%x\r\n", __func__, ErrorMask);
}



/*****************************************************************************/
/**
*
* Callback function (called from interrupt handler) to handle the following
* interrupts:
*   - XCAN_IXR_BSOFF_MASK:  Bus Off Interrupt
*   - XCAN_IXR_RXOFLW_MASK: RX FIFO Overflow Interrupt
*   - XCAN_IXR_RXUFLW_MASK: RX FIFO Underflow Interrupt
*   - XCAN_IXR_TXBFLL_MASK: TX High Priority Buffer Full Interrupt
*   - XCAN_IXR_TXFLL_MASK:  TX FIFO Full Interrupt
*   - XCAN_IXR_WKUP_MASK:   Wake up Interrupt
*   - XCAN_IXR_SLP_MASK:    Sleep Interrupt
*   - XCAN_IXR_ARBLST_MASK: Arbitration Lost Interrupt
*
* Please feel free to change this function to meet specific application needs.
*
* @param	CallBackRef is the callback reference passed from the interrupt
*		handler, which in our case is a pointer to the driver instance.
* @param	IntrMask is a bit mask indicating pending interrupts. Its value
*		equals 'OR'ing one or more of the XCAN_IXR_*_MASK value(s)
*		mentioned above.
*
* @return	None.
*
* @note		This function is called by the driver within interrupt context.
*
******************************************************************************/
static void EventHandler(void *CallBackRef, u32 IntrMask)
{
	XCan *CanPtr = (XCan *)CallBackRef;

	if (IntrMask & XCAN_IXR_BSOFF_MASK) { /* Enter Bus off status */
		/*
		 * Entering Bus off status interrupt requires
		 * the CAN device be reset and re-configurated.
		 */
		XCan_Reset(CanPtr);
		Config(CanPtr);
		return;
	}

	if(IntrMask & XCAN_IXR_RXOFLW_MASK) { /* RX FIFO Overflow Interrupt */
		/*
		 * Code to handle RX FIFO Overflow
		 * Interrupt should be put here.
		 */
	}

	if(IntrMask & XCAN_IXR_RXUFLW_MASK) { /* RX FIFO Underflow Interrupt */
		/*
		 * Code to handle RX FIFO Underflow
		 * Interrupt should be put here.
		 */
	}

	if(IntrMask & XCAN_IXR_TXBFLL_MASK) { /* TX High Priority Full Intr */
		/*
		 * Code to handle TX High Priority Buffer Full
		 * Interrupt should be put here.
		 */
	}

	if(IntrMask & XCAN_IXR_TXFLL_MASK) { /* TX FIFO Full Interrupt */
		/*
		 * Code to handle TX FIFO Full
		 * Interrupt should be put here.
		 */
	}

	if (IntrMask & XCAN_IXR_WKUP_MASK) { /* Wake up from sleep mode */
		/*
		 * Code to handle Wake up from sleep mode
		 * Interrupt should be put here.
		 */
	}

	if (IntrMask & XCAN_IXR_SLP_MASK) { /* Enter sleep mode */
		/*
		 * Code to handle Enter sleep mode
		 * Interrupt should be put here.
		 */
	}

	if (IntrMask & XCAN_IXR_ARBLST_MASK) { /* Lost bus arbitration */

		/*
		 * Code to handle Lost bus arbitration
		 * Interrupt should be put here.
		 */
	}
}

/*****************************************************************************/
/**
*
* This function sets up the interrupt system so interrupts can occur for the
* CAN. This function is application-specific since the actual system may or
* may not have an interrupt controller.  The CAN could be directly connected
* to a processor without an interrupt controller.  The user should modify this
* function to fit the application.
*
* @para		InstancePtr is a pointer to the instance of the CAN
*		which is going to be connected to the interrupt controller.
*
* @return	XST_SUCCESS if successful, otherwise XST_FAILURE.
*
* @note		None.
*
****************************************************************************/
static int SetupInterruptSystem(XCan *InstancePtr)
{
	static INTC InterruptController;
	int Status;

#ifdef XPAR_INTC_0_DEVICE_ID
	/*
 	 * Initialize the interrupt controller driver so that it's ready to use.
	 * INTC_DEVICE_ID specifies the XINTC device ID that is generated in
	 * xparameters.h.
	 */
	Status = XIntc_Initialize(&InterruptController, INTC_DEVICE_ID);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	/*
	 * Connect the device driver handler that will be called when an interrupt
	 * for the device occurs, the device driver handler performs the specific
	 * interrupt processing for the device.
	 */
	Status = XIntc_Connect(&InterruptController,
				CAN_INTR_VEC_ID,
				(XInterruptHandler)XCan_IntrHandler,
				InstancePtr);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	/*
	 * Start the interrupt controller so interrupts are enabled for all
	 * devices that cause interrupts. Specify real mode so that the CAN
	 * can cause interrupts through the interrupt controller.
	 */
	Status = XIntc_Start(&InterruptController, XIN_REAL_MODE);
	if (Status != XST_SUCCESS){
		return XST_FAILURE;
	}

	/*
	 * Enable the interrupt for the CAN.
	 */
	XIntc_Enable(&InterruptController, CAN_INTR_VEC_ID);
#else /* SCUGIC */


	XScuGic_Config *IntcConfig;

	/*
	 * Initialize the interrupt controller driver so that it is ready to
	 * use.
	 */
	IntcConfig = XScuGic_LookupConfig(INTC_DEVICE_ID);
	if (NULL == IntcConfig) {
		return XST_FAILURE;
	}

	Status = XScuGic_CfgInitialize(&InterruptController, IntcConfig,
					IntcConfig->CpuBaseAddress);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}


	XScuGic_SetPriorityTriggerType(&InterruptController, CAN_INTR_VEC_ID,
					0xA0, 0x3);

	/*
	 * Connect the interrupt handler that will be called when an
	 * interrupt occurs for the device.
	 */
	Status = XScuGic_Connect(&InterruptController, CAN_INTR_VEC_ID,
				 (Xil_ExceptionHandler)XCan_IntrHandler,
				 InstancePtr);
	if (Status != XST_SUCCESS) {
		return Status;
	}

	/*
	 * Enable the interrupt for the Can device.
	 */
	XScuGic_Enable(&InterruptController, CAN_INTR_VEC_ID);




#endif

	/*
	 * Initialize the exception table.
	 */
	Xil_ExceptionInit();

	/*
	 * Register the interrupt controller handler with the exception table.
	 */
	Xil_ExceptionRegisterHandler(XIL_EXCEPTION_ID_INT,
			 (Xil_ExceptionHandler)INTC_HANDLER,
			 &InterruptController);

	/*
	 * Enable exceptions.
	 */
	Xil_ExceptionEnable();

	return XST_SUCCESS;
}

void print_timewait(const char *prefix, u32 timeoutSec)
{
	while (timeoutSec)
	{
		xil_printf("%s after %u seconds\r\n", prefix, timeoutSec);

		timeoutSec--;
		sleep(1);
	}
}
```



# Bottom



