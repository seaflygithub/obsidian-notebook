
下面是简化后的 sg = sg_next(sg)

```cpp
// 核心宏定义（include/linux/scatterlist.h）
#define SG_END_FLAG 0x01          // 链表尾标记（最低位）
#define SG_PAGE_LINK_MASK (~0x03) // 页地址掩码（屏蔽低2位标记）

static inline struct scatterlist *sg_next(struct scatterlist *sg)
{
    // 1. 检查当前sg是否是链表尾（最低位为1）
    if (sg->page_link & SG_END_FLAG)
        return NULL;

    // 2. 非尾节点：返回物理内存中连续的下一个sg结构体
    return sg + 1;
}
```

关键：对于`sg_alloc_table`分配的**连续 sg 数组**（如你`pages_nr=4`的场景），`sg_next`本质是`sg+1`（地址偏移），仅通过`SG_END_FLAG`判断是否到尾。




