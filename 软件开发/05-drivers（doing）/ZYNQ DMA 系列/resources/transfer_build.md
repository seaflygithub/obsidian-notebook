该函数主要作用就是把上一层节点提供的数据物理地址信息填充到描述符里，即填充搬运的源地址、目的地址、搬运字节数等信息。比如这里的源地址就是主机物理内存，目的地址就是 ep_addr，这个 ep_addr 类似于文件中的pos信息，是设备那边的数据相对位置，会随着访问不断后移（如下代码中的: req->ep_addr += sdesc->len）。

```cpp
static int transfer_build(struct xdma_engine *engine,
			  struct xdma_request_cb *req, struct xdma_transfer *xfer, unsigned int desc_max)
{
	struct sw_desc *sdesc = &(req->sdesc[req->sw_desc_idx]);
	int i = 0;
	int j = 0;
	dma_addr_t bus = xfer->res_bus;

	for (; i < desc_max; i++, j++, sdesc++) {
		dbg_desc("sw desc %d/%u: 0x%llx, 0x%x, ep 0x%llx.\n",
			 i + req->sw_desc_idx, req->sw_desc_cnt, sdesc->addr,
			 sdesc->len, req->ep_addr);

		/* fill in descriptor entry j with transfer details */
		xdma_desc_set(xfer->desc_virt + j, sdesc->addr, req->ep_addr,
			      sdesc->len, xfer->dir);
		xfer->len += sdesc->len;

		/* for non-inc-add mode don't increment ep_addr */
		if (!engine->non_incr_addr)
			req->ep_addr += sdesc->len;

		if (engine->streaming && engine->dir == DMA_FROM_DEVICE) {
				memset(xfer->res_virt + j, 0, sizeof(struct xdma_result));
				xfer->desc_virt[j].src_addr_lo = cpu_to_le32(PCI_DMA_L(bus));
				xfer->desc_virt[j].src_addr_hi = cpu_to_le32(PCI_DMA_H(bus));
				bus += sizeof(struct xdma_result);
		}

	}
	req->sw_desc_idx += desc_max;
	return 0;
}
```

