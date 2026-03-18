
在这里 desc_blen_max=256MB，特殊情况下，如果一个sg节点的数据量超过256MB，那么就按最大256MB来初始化 sdesc 节点，即单个 sdesc 节点最大数据容量256MB。

```cpp
/* maximum size of a single DMA transfer descriptor */
#define XDMA_DESC_BLEN_BITS	28
#define XDMA_DESC_BLEN_MAX	((1 << (XDMA_DESC_BLEN_BITS)) - 1)

unsigned int desc_blen_max = XDMA_DESC_BLEN_MAX;
module_param(desc_blen_max, uint, 0644);
MODULE_PARM_DESC(desc_blen_max,
		 "per descriptor max. buffer length, default is (1 << 28) - 1");
```