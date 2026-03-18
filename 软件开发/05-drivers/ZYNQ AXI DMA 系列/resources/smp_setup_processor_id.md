
```cpp
void __init smp_setup_processor_id(void)
{
	int i;
	u32 mpidr = is_smp() ? read_cpuid_mpidr() & MPIDR_HWID_BITMASK : 0;
	u32 cpu = MPIDR_AFFINITY_LEVEL(mpidr, 0);

	cpu_logical_map(0) = cpu;
	for (i = 1; i < nr_cpu_ids; ++i)
		// Linux 逻辑 CPU 编号 和 硬件 CPU 编号是可以“打乱”的
		cpu_logical_map(i) = i == cpu ? 0 : i;

	/*
	 * clear __my_cpu_offset on boot CPU to avoid hang caused by
	 * using percpu variable early, for example, lockdep will
	 * access percpu variable inside lock_release
	 */
	// 初始化当前 CPU（boot CPU）的 per-cpu 数据偏移
	// 让 boot CPU 的 per-cpu 基址 = 0, 避免访问错误地址
	set_my_cpu_offset(0);

	pr_info("Booting Linux on physical CPU 0x%x\n", mpidr);
}
```


**为什么要做映射？**

硬件 CPU 编号可能是乱的，且 boot CPU 可能不是 0，但 Linux 要求 CPU0 = boot CPU。这和你后面学的中断内容强相关，GIC 中断 target CPU → 用的是硬件 ID，Linux 调度 → 用的是 logical CPU，所以必须要有映射。在Linux内核里，CPU用的都是逻辑编号。


**cpu_logical_map 是在哪里被用的？**

1、初始化它：smp_init()
2、引用它：[[secondary_startup]]()
3、引用它：GIC 中断 target CPU。


