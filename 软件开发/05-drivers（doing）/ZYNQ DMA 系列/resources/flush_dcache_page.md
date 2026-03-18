
![[Pasted image 20251217103418.png]]


**关键**：x86 架构因硬件自动维护缓存一致性（MESI 协议），`flush_dcache_page` 几乎无实际操作；而 ARM 等架构必须显式调用，否则会出现数据错乱，即需显式遍历页对应的缓存行，执行 “写回（writeback）+ 失效（invalidate）” 操作。


flush_dcache_page 基本实现原理:
1. **获取页的物理地址**：从 `struct page` 中提取物理页框号（PFN），转换为物理地址 `phys_addr = page_to_phys(page)`；
2. **遍历页内缓存行**：按 CPU 缓存行大小（如 64B）遍历整个 4KB 页的所有缓存行；
3. **写回 + 失效缓存行**


---

**其他关联的缓存操作函数**

1、invalidate_dcache_page: 仅使缓存失效（不写回脏数据）；
2、sync_dcache_for_cpu: Invalid缓存行（ARM 架构常用）；
3、sync_dcache_for_device: Flush脏数据到内存（ARM 架构常用）；


---

1、**CacheLineFlush**: 脏（Dirty）→ 干净（Clean）（仍有效）；把缓存行的内容刷到物理内存，使缓存和内存数据一致，之后缓存行仍保留（状态变为 “干净”）。
2、**CacheLineInvalid**: 有效（Valid）→ 无效（Invalid）（直接不可用）；不区分缓存行是否脏，直接将缓存行标记为 “无效”。

⚠️ 关键风险：若直接对 “脏缓存行” 执行 Invalid，缓存中的修改会丢失（内存中仍是旧数据），因此实际使用中，**对脏缓存行先 Flush 再 Invalid 是标准操作**。




