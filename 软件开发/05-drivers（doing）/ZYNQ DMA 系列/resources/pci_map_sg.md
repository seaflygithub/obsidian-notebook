该接口核心作用主要两个：
- **作用1**: 将 SG 表中的「物理页地址」转换为「DMA 控制器可识别的总线地址」；
- **作用2**: 合并连续的物理页为更少的 SG 节点（减少DMA 控制器在硬件层面 **处理 SG 节点的次数**，降低硬件的链表遍历开销，提升传输效率）；

![[Pasted image 20251219151854.png]]


<font color=blue>pci_map_sg 实现中，一个SG节点最多能绑定多少个连续物理页？
</font>

x86_64 平台的主流 PCI 设备都支持跨页 SG 节点。x86_64 平台默认使用 32 位 DMA 地址（兼容传统外设），最大可寻址的 DMA 地址范围是 `0 ~ 0xFFFFFFFF`（4GB）。x86_64 标准物理页大小为 4KB（`PAGE_SIZE = 4096`）。最大合并页数 = 4GB / 4KB = 1048576 页（1024 * 1024）

<font color=blue>假设这里的某一个sg节点假设合并了4个连续物理页，那么就是16KB，但是之前不是说一个sg节点最多只能挂一个物理页么？
</font>

之前认为单个SG节点只绑定一个物理页，是因为初始构建 SG 列表时，开发者通常会为**每个物理页**创建一个 SG 节点。用一个 SG 节点描述整段连续地址，可以减少 SG 节点数量、提升 DMA 效率。
```c
struct scatterlist {
    unsigned long page_link;  // 关联的物理页（或下一个SG节点）
    unsigned int offset;      // 页内偏移
    unsigned int length;      // 这段数据的总长度（核心！）
    dma_addr_t dma_address;   // DMA 控制器识别的总线地址
    unsigned int dma_length;  // DMA 传输的总长度
};
```








