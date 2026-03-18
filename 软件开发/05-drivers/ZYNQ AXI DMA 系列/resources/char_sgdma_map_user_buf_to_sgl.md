
1、当用户空间发起h2c或c2h请求时，驱动会通过 get_user_pages_fast()拿到其物理页信息并绑定物理页以防止被swap出，确保 dma 后续的正常访问，因为dma只能访问物理内存。
![[Pasted image 20251217101724.png]]

---

2、char_sgdma_map_user_buf_to_sgl()函数内的代码骨架：
- 1、拿到 pages_nr（假设 pages_nr=3）
- 2、申请sg链表: 
	- [[sgt, pages_nr, GFP_KERNEL]];
	- cb->pages = kcalloc(pages_nr, sizeof(struct page *), ...);
- 3、**拿到物理页**: [[get_user_pages_fast]]
- 4、**绑定物理页与SG节点**: for (i = 0; i < pages_nr; i++, sg = sg_next(sg))
	- 1、冲刷物理页高速缓存: [[cb->pages[i]]];
	- 2、[[sg, cb->pages[i], nbytes, offset]];


