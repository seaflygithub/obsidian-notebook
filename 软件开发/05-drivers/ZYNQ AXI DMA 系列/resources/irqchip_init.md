
```cpp
void __init irqchip_init(void)
{
	of_irq_init(__irqchip_of_table);
	acpi_probe_device_table(irqchip);
}
```

1、在 Zynq（ARM SoC）上，DTB和ACPI可以“同时编译进内核”（代码层面支持两套），运行时只会选择其中一套。ARM只用设备树，ARM64（服务器）常用ACPI。为什么设计成“两套都调用”？（设计哲学），这是 Linux 的一个典型设计，统一入口，内部选择路径。


```cpp
// 设备树路径
irqchip_init()
	→ of_irq_init()
		→ gic_of_init()

// ACPI 路径（服务器用）
irqchip_init()
	→ acpi_probe_device_table()
		→ gic_acpi_init()
```

两者最终都会：注册 irq_chip、建立 irq_domain。









