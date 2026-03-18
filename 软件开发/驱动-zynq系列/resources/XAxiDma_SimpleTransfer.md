


```cpp
u32 XAxiDma_SimpleTransfer(XAxiDma *InstancePtr, 
	UINTPTR BuffAddr, u32 Length, int Direction)
{
	if(Direction == XAXIDMA_DMA_TO_DEVICE(0x00))
	{
		// 首先不支持 sg 模式, 检查如果是sg模式, 则直接返回错误
		
		// 检查通道数最少为1
		
		// 检查引擎是否正忙
		XAxiDma_Busy(InstancePtr,Direction)
		{
			// XAXIDMA_DMA_TO_DEVICE=0x00, XAXIDMA_DEVICE_TO_DMA=0x01
			RegBase=InstancePtr->RegBase + (XAXIDMA_RX_OFFSET(0x30) * Direction);
			XAXIDMA_SR_OFFSET==0x04;
			
			// bit: 1=Idle, 0=Not Idle
			XAXIDMA_IDLE_MASK==0x02;
		}
		
		// 设置srcaddr:低32位,高32位
		XAxiDma_WriteReg(InstancePtr->TxBdRing.ChanBase,
                 XAXIDMA_SRCADDR_OFFSET=0x18, LOWER_32_BITS(BuffAddr));
		
		// 启动通道传输(进入就绪状态): 
		XAXIDMA_CR_OFFSET=0x00, XAXIDMA_CR_RUNSTOP_MASK=0x01
		
		// 正式启动dma, 往tail指针写入长度: XAXIDMA_BUFFLEN_OFFSET=0x28
		// 把单次传输长度写入BTT寄存器(Bytes to Transfer)
		XAxiDma_WriteReg(InstancePtr->TxBdRing.ChanBase,
                    XAXIDMA_BUFFLEN_OFFSET, Length);
        
        // DMA 一轮传输完成后的状态：会自动停止、自动进入空闲态
        // XAxiDma_Busy()轮询就是判断这个空闲态
        
        // DMA 启动的唯一核心触发点：对（BTT 寄存器）执行「写操作」，
        // 无论该寄存器当前值是什么，只要写入非 0 的长度值，立刻触发本次 DMA 传输；
        // 相当于是往这个寄存器写的这个动作，能够触发DMA开始工作。
        
	} else if(Direction == XAXIDMA_DEVICE_TO_DMA)
	{
		// 前面步骤相似
		
		// 设置 dstaddr: 低32位,高32位
		XAxiDma_WriteReg(InstancePtr->RxBdRing[RingIndex].ChanBase,
                 XAXIDMA_DESTADDR_OFFSET=0x18, LOWER_32_BITS(BuffAddr));
                 
        // 就绪: XAXIDMA_CR_RUNSTOP_MASK
        
        // 开始: 往 BTT 寄存器写入单次传输长度
	}
}
```





