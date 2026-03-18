1、把传输实例 transfer 提交给引擎，也就是插入到传输链表里，然后启动引擎，引擎会自动传输，传输完成之后，通过某种方式告知驱动，我已传输完成了。

transfer_queue 核心流程:

```cpp
transfer_queue(...)
{
    spin_lock_irqsave(&engine->lock, flags);

    list_add_tail(&transfer->entry, &engine->transfer_list);

        /* engine is idle? */
        if (!engine->running) {
            engine_start(engine);
        }
    spin_unlock_irqrestore(&engine->lock, flags);
}

engine_start(...)
{
    transfer = list_entry(engine->transfer_list.next,...);
    
    // 把首个描述符里的地址信息写到DMA寄存器里
    
	/* write lower 32-bit of bus address of transfer first descriptor */
	w = cpu_to_le32(PCI_DMA_L(transfer->desc_bus));
    write_register(w, &engine->sgdma_regs->first_desc_lo,...);
    
	/* write upper 32-bit of bus address of transfer first descriptor */
	w = cpu_to_le32(PCI_DMA_H(transfer->desc_bus));
    write_register(w, &engine->sgdma_regs->first_desc_hi,...);
    
    write_register(extra_adj, &engine->sgdma_regs->first_desc_adjacent,...);
   
	// 准备启动引擎
	engine_start_mode_config(engine);
	engine->running = 1;
}
```


---

engine_start_mode_config

1、该函数就是根据情况写入control寄存器。

```cpp
/* bits of the SG DMA control register */
#define XDMA_CTRL_RUN_STOP			(1UL << 0)
#define XDMA_CTRL_IE_DESC_STOPPED		(1UL << 1)
#define XDMA_CTRL_IE_DESC_COMPLETED		(1UL << 2)
#define XDMA_CTRL_IE_DESC_ALIGN_MISMATCH	(1UL << 3)
#define XDMA_CTRL_IE_MAGIC_STOPPED		(1UL << 4)
#define XDMA_CTRL_IE_IDLE_STOPPED		(1UL << 6)
#define XDMA_CTRL_IE_READ_ERROR			(0x1FUL << 9)
#define XDMA_CTRL_IE_DESC_ERROR			(0x1FUL << 19)
#define XDMA_CTRL_NON_INCR_ADDR			(1UL << 25)
#define XDMA_CTRL_POLL_MODE_WB			(1UL << 26)
#define XDMA_CTRL_STM_MODE_WB			(1UL << 27)
```

**一、核心控制位（基础运行）**

- **XDMA_CTRL_RUN_STOP**: DMA 引擎启停控制位，1=启动 DMA 引擎, 0=停止 DMA 引擎，立即终止当前传输。
- **XDMA_CTRL_NON_INCR_ADDR**: 地址递增模式控制，0(默认)=DMA 传输时地址自动递增，1=地址非递增（固定地址传输）。

**二、中断使能位（IE=Interrupt Enable，核心）**

- XDMA_CTRL_IE_DESC_STOPPED: 当 DMA 引擎因 “最后一个描述符的 STOPPED 位” 停止时，触发中断；驱动中用于感知 “批次传输完成且引擎已停止”。
- XDMA_CTRL_IE_DESC_COMPLETED: 当单个 / 最后一个描述符执行完成（COMPLETED 位）时触发中断；驱动中最核心的中断 —— 感知传输成功完成，唤醒阻塞线程。
- XDMA_CTRL_IE_DESC_ALIGN_MISMATCH: 当描述符的传输地址 / 长度不符合硬件对齐要求（如非 512 字节对齐）时触发中断；
- XDMA_CTRL_IE_IDLE_STOPPED: 当 DMA 引擎无描述符可执行（空闲状态）且被停止时触发中断；场景：批次传输完成后引擎进入空闲，触发中断清理资源。
- XDMA_CTRL_IE_DESC_ERROR: 覆盖所有描述符相关错误（如描述符格式非法、长度超限、权限错误等）；驱动中用于定位 “描述符构建错误” 导致的传输失败。

**三、模式控制位（特殊传输模式）**

- XDMA_CTRL_POLL_MODE_WB: 置 1：轮询模式下，DMA 完成后自动写回传输状态（如长度、结果）到指定内存；置 0：轮询模式不自动写回，需驱动主动读取状态；驱动中 poll_mode 为 true 时会置该位。
- XDMA_CTRL_STM_MODE_WB: 针对 AXI Stream（AXI ST）流传输，置 1 后：DMA 完成流传输时，自动将流长度、EOP 状态等写回内存；用于流传输的 “长度回传”（如 C2H 流传输后告知用户实际接收长度）。





