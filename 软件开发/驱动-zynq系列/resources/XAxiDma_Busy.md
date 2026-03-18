
```cpp
u32 XAxiDma_Busy(XAxiDma *InstancePtr, int Direction)
{
	return ((XAxiDma_ReadReg(InstancePtr->RegBase +
				(XAXIDMA_RX_OFFSET{0x30} * Direction),
				XAXIDMA_SR_OFFSET{0x04}) &
				XAXIDMA_IDLE_MASK{0x02}) ? FALSE : TRUE);
	// bit: 1=Idle, 0=Not Idle
}
```








