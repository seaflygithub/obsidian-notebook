

1、初始化，主要执行复位操作，并等待复位完成。
```cpp
int XAxiDma_CfgInitialize(XAxiDma * InstancePtr, XAxiDma_Config *Config)
{
	// 填充 InstancePtr 结构体
	
	// 复位
	XAxiDma_Reset(InstancePtr)
	{
		// 复位的核心代码
		ChanBase = InstancePtr->RegBase + XAXIDMA_TX_OFFSET{0x00};
		ChanBase = InstancePtr->RegBase + XAXIDMA_RX_OFFSET{0x30};
		XAxiDma_WriteReg(ChanBase, 
			XAXIDMA_CR_OFFSET{0x00}, XAXIDMA_CR_RESET_MASK={0x04});
	}
	
	// 等待复位完成
	while(...)
	{
		XAxiDma_ResetIsDone(InstancePtr)
		{
			// 读取寄存器: XAXIDMA_CR_OFFSET{0x00}
			if(regval & XAXIDMA_CR_RESET_MASK)
				return false;
		}
	}

}
```











