
**xdma_xfer_submit** 核心逻辑：
- nents = [[...,sg, sgt->orig_nents,...]];
- req = [[sgt, ep_addr]];
- while (nents) {
	- 每次循环最多传输8MB: [[transfer_init]]
		- transfer_desc_init(...);
		- transfer_build(...);
		- [[...]];
	- 交给引擎: [[transfer_queue]]
	- 阻塞等待: [[xfer->wq, ...]]
	- 哪里会主动唤醒它？
	- 结束本轮循环: transfer_destroy
- }
- pci_unmap_sg(...,sg, sgt->orig_nents,...);
- xdma_request_free(...);



2、xdma引擎一次能传输多少个SG节点数据，即一次能传输多少个4KB数据，就决定了while(nents)的循环次数。transfer_init() 函数主要作用是单批次 DMA 传输，transfer_queue() 函数开始让xdma引擎开始数据搬运工作，而后面的 wait_event 就是阻塞等待本次搬运完成。


```cpp
xdma_xfer_submit(...,sgt,...)
{
	// 作用1: 将 SG 表中的「物理页地址」转换为「DMA 控制器可识别的总线地址」
	// 作用2: 合并连续的物理页为更少的 SG 节点（减少DMA提交次数，提升 DMA 效率）；
	// 作用3: 返回实际有效的 SG 节点数（nents）；
	nents = pci_map_sg(...,sg, sgt->orig_nents,...);

	// 把sgt散列表绑定到dma请求
	// 计算 SG 表总长度（req->total_len）、SG 节点数（req->sw_desc_cnt）
	// ep_addr就是write(pos)参数
	req = xdma_init_request(sgt, ep_addr);
	
	// 开始处理
	mutex_lock(&engine->desc_lock);
	while (nents) {
		// transfer_init 最多 XDMA_TRANSFER_MAX_DESC(2048) 个描述符
		// 即表明 2048 x 4KB = 8MB, 单次循环最多传输8MB数据
		transfer_init(...); 
		transfer_queue(...);
		wait_event_interruptible_timeout(xfer->wq,
							(xfer->state != TRANSFER_STATE_SUBMITTED),
							msecs_to_jiffies(timeout_ms));;
		//阻塞等待数据搬运完成，等待条件成立，即 state!= xxx 时唤醒等待
		
		// 获取完成状态
		switch (xfer->state)
		{
			case TRANSFER_STATE_COMPLETED:
			{
				...
				done += xfer->len;// xfer->len 最多 2048*4KB=8MB
				break;
			}
			case TRANSFER_STATE_FAILED: { ... }
		}
		
		transfer_destroy(...);

	}
	mutex_unlock(&engine->desc_lock);

	// 解除映射
	pci_unmap_sg(...,sg, sgt->orig_nents,...);
	
	xdma_request_free(...);
}
```



```cpp
while (nents)
{
	xfer = &req->tfer[0];
	
	// 初始化单批次传输,根据DMA引擎能处理的最大节点数
	transfer_init(engine, req, &req->tfer[0]);
	
	// 更新剩余节点数
	nents -= xfer->desc_num;
	
	// 提交批次到 DMA 引擎
	transfer_queue(engine, xfer);
	
	// 阻塞等待传输完成
	wait_event_interruptible_timeout(...);
	
	// 获取完成状态
	switch (xfer->state)
	{
		case TRANSFER_STATE_COMPLETED:
		{
			...
			done += xfer->len;// xfer->len 最多 2048*4KB=8MB
			break;
		}
		case TRANSFER_STATE_FAILED: { ... }
	}
	
	transfer_destroy(...);
}
```






