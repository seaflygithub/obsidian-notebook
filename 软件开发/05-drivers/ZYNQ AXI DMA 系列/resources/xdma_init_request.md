该函数的核心作用就是申请一个请求实例，然后初始化 req->sdesc 数组，并把来自上一层(SG)的每个节点的数据地址和数据长度赋值给对应的每个 sdesc 节点，这里每个 sdesc 节点最大数据量做了限制，最大数据量为 desc_blen_max(256MB)。

1、下面是裁剪后的伪代码。
```cpp
// 下面是 xdma_init_request 函数的骨架代码和注释
static struct xdma_request_cb *xdma_init_request(struct sg_table *sgt,
						 u64 ep_addr)
{
	struct xdma_request_cb *req;
	struct scatterlist *sg = sgt->sgl;
	int max = sgt->nents;
	int extra = 0;
	int i, j = 0;

    // 遍历每个sg节点
	for (i = 0; i < max; i++, sg = sg_next(sg)) {
		// 获取该sg节点的dma搬运长度(字节)
		unsigned int len = sg_dma_len(sg);

		// 默认 desc_blen_max = XDMA_DESC_BLEN_MAX, 即256MB
		// 表示每个描述符最大能搬运 256MB 数据
		if (unlikely(len > desc_blen_max))
			extra += (len + desc_blen_max - 1) / desc_blen_max;
			
		// 这里根据每个sg节点搬运长度来决定需要新增多少个desc
	}
	dbg_tfr("ep 0x%llx, desc %u+%u.\n", ep_addr, max, extra);

	// 主要分配 req->sdesc 数组内存
	max += extra;
	req = xdma_request_alloc(max);
	if (!req)
		return NULL;

	req->sgt = sgt;
	req->ep_addr = ep_addr;

	for (i = 0, sg = sgt->sgl; i < sgt->nents; i++, sg = sg_next(sg)) {
		unsigned int tlen = sg_dma_len(sg);   // 4KB
		dma_addr_t addr = sg_dma_address(sg); // 前面 pci_map_sg 拿到的dma物理地址

		req->total_len += tlen;
		while (tlen) {
			req->sdesc[j].addr = addr;
			// 这个条件我们基本不满足,比如我们实验总共写入12KB
			// 也就是每个sg才4KB, 远远小于 desc_blen_max 所指的256MB
			if (tlen > desc_blen_max) {
				req->sdesc[j].len = desc_blen_max;
				addr += desc_blen_max;
				tlen -= desc_blen_max;
			} else {
				req->sdesc[j].len = tlen;
				tlen = 0;
			}
			j++;
		}
	}

	if (j > max) {
		pr_err("Cannot transfer more than supported length %d\n", desc_blen_max);
		xdma_request_free(req);
		return NULL;
	}
	req->sw_desc_cnt = j;// 这里总共试验了3个物理页,所以其值为3
	return req;
}
```


