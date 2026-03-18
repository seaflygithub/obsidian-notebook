1、该函数直接申请内存，req请求实例、req->sdesc数组。

```cpp
static struct xdma_request_cb *xdma_request_alloc(unsigned int sdesc_nr)
{
	// 结构体内末尾的零长数组成员不占用内存空间, 因此才有下面这个加法操作
	struct xdma_request_cb *req;
	unsigned int size = sizeof(struct xdma_request_cb) +
			    sdesc_nr * sizeof(struct sw_desc);
			    
	req = kzalloc(size, GFP_KERNEL);
	if (!req) {
		req = vmalloc(size);
		if (req)
			memset(req, 0, size);
	}
	...
	return req;
}

struct xdma_request_cb {
	struct sg_table *sgt;
	unsigned int total_len;
	u64 ep_addr;
	...
	unsigned int sw_desc_idx;
	unsigned int sw_desc_cnt;
	struct sw_desc sdesc[0];  // 零长数组放结构体末尾
};
```


<font color=blue>
2、零长数组有什么作用？为什么放结构体末尾作为最后一个成员？
</font>

也常叫柔性数组，核心作用是：**让结构体能够灵活地管理一块大小可变的连续内存，实现 “头信息 + 可变长度数据” 的一体化存储**。而用指针的话，释放时还需要分别释放结构体和数据，容易出错。零长数组则能让 “结构体头 + 可变数据” 存放在**连续的一块内存**中，既节省内存，又方便管理。

必须放在结构体末尾，这是由内存布局和访问规则决定的，零长数组本身不占用结构体的内存（大小为 0），它只是一个 “占位符”，如果零长数组不放在末尾，它后面的**成员会覆盖**掉后续分配的可变数据，导致内存错乱。
