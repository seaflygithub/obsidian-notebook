

2、SG链表 sg_table 是个表头，scatterlist 就是sg节点数组。sg_alloc_table 的作用就是申请一个sgt实例，并分配数组，数组元素个数为 pages_nr。

```cpp
// sg_alloc_table(sgt, pages_nr, GFP_KERNEL);
// 申请一个sgt实例，并分配数组，数组元素个数为 pages_nr
struct sg_table {
        struct scatterlist *sgl;        /* the list */
        unsigned int nents;             /* number of mapped entries */
        unsigned int orig_nents;        /* original size of list */
};

struct scatterlist {
        unsigned long   page_link; // 物理页指针 + 链表标记位
        unsigned int    offset;    // 物理页内的偏移量（字节）
        unsigned int    length;    // 该 sg 段的物理内存长度（字节）
        dma_addr_t      dma_address;
#ifdef CONFIG_NEED_SG_DMA_LENGTH     // x86平台默认配置为y
        unsigned int    dma_length; 
#endif
};
```

`offset + length ≤ PAGE_SIZE`（x86 默认 4096 字节），即单个 sg 节点描述的内存范围**不能跨物理页**；也就是说一个sg节点最多只能存放一个物理页信息。





---









