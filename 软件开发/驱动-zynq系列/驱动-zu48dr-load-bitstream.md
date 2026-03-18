
附件: 网盘: 客户提供的裸机加载例程0730.sdk.zip
附件: 网盘: 27DR测试（PS加载bit文件到Fabric）.7z
附件: 网盘: load_bitstream.sh

下面是裸机加载的核心总体流程代码:

```cpp
Status = XFpga_Initialize(&XFpgaInstance);

Status = zu48dr_XFpga_PL_BitStream_Load(&XFpgaInstance, addr, size, XFPGA_PARTIAL_EN);
if (Status == XFPGA_SUCCESS)
	xil_printf("PL Configuration done successfully");
```

**问题描述**: 由于 zu48dr 运行了linux系统，但是客户在开发调试期间，需要频繁更新替换.bit文件，按照常规的流程，当.bit文件更新，那么就需要重新打包制作成 BOOT.bin 文件并重新用下载器烧写到 QSPI Flash 里，这个过程要耗费半小时左右。为此，在PS资源没有变动的情况下，客户只改动了他们PL部分的代码，那么新的.bit文件就需要一个动态加载的办法，比如能够在板载linux系统下把新的.bit文件加载到PL Fabric 里运行起来，而无需重启整个系统。等定版了在做成固件固化也行。


## 平台支持

**相关驱动代码** 在内核成功编译过后,下面这些文件是被编译成.o文件的:

linux-xlnx-master/drivers/fpga/fpga-bridge.c
linux-xlnx-master/drivers/fpga/fpga-mgr.c
linux-xlnx-master/drivers/fpga/fpga-region.c
linux-xlnx-master/drivers/fpga/of-fpga-region.c
linux-xlnx-master/drivers/fpga/xilinx-afi.c
linux-xlnx-master/drivers/fpga/xilinx-pr-decoupler.c
linux-xlnx-master/drivers/fpga/zynqmp-fpga.c


设备和驱动匹配机制：
![[Pasted image 20251222180712.png]]

- `drivers/fpga/zynqmp-fpga.c —— of_device_id for zynqmp serials`
- `zynqmp.dtsi —— "xlnx,zynqmp_pcap"`
- `drivers/fpga/zynq-fpga.c —— of_device_id for zynq serials`


![[Pasted image 20251222180842.png]]
如上图所示，fpga-region，这个节点具体是干什么的，需探究待续。。。


## 驱动用法

由于zynqmp官方内核以及提供了对应的驱动(zynqmp-fpga.c编译成了.o文件，且代码中的匹配条件和设备树中能够对应上)。因此，直接参考官网提供的动态加载bitstream文章(zynqmp fpga manager)，并封装成了易于操作的脚本。

如何直接使用驱动的参考文章:
- （1）[[Solution+ZynqMP+PL+Programming?atlOrigin=eyJpIjoiMGJiMjQ5ZWRlYWVlNGU3MDhiOTIzMDFhMDNjNjk1NzAiLCJwIjoiYyJ9]]
- （2）[[Solution+Zynq+PL+Programming+With+FPGA+Manager?atlOrigin=eyJpIjoiZTQ5OWE5Y2ZmMTY2NDA3M2FiOTg1OTQxYjZlZDk5MjgiLCJwIjoiYyJ9]]


![[Pasted image 20251222181210.png]]


基于上述的官方参考文章，封装了如下脚本(load_bitstream.sh):

```bash
# bootimage里只能存放一个.bit文件
if [ "$#" -ne 3 ]; then
    echo "Usage: $0  <0=full,1=partial> <bitstream_filename> <bitstream_fullpath>"
    echo "  e.g: $0 0 bitstream_file.bit.bin /emmc/bitstream_file.bit.bin"
    echo "  e.g: $0 1 bitstream_file.bit.bin /emmc/bitstream_file.bit.bin"
    echo " "
    echo "bitstream_file.bit.bin: bootimage only include bitstream.bit"
    exit 1
else
    #模式: 0=full, 1=partial
    BITSTREAM_MODE="$1"
    #文件名,纯文件名,不带路径信息,用于告知驱动要加载哪个文件
    BITSTREAM_FILE="$2"
    #文件名,带路径信息,主要用于把文件拷贝到指定目录
    BITSTREAM_FULLPATH="$3"
fi

# 1)Set flags for Full Bitstream.
echo $BITSTREAM_MODE > /sys/class/fpga_manager/fpga0/flags

# 2) Loading Bitstream into PL.
mkdir -p /lib/firmware
cp -vf "$BITSTREAM_FULLPATH" /lib/firmware/
echo "$BITSTREAM_FILE" > /sys/class/fpga_manager/fpga0/firmware
```


下面是加载效果图:
![[Pasted image 20251222181244.png]]


![[Pasted image 20251222181255.png]]


![[Pasted image 20251222181307.png]]


把镜像加载完之后，可以通过上述的属性文件获取PL运行状态。


## fpga-mgr.c

内核驱动里面涉及到PL的控制、DMA的控制、以及DMA SG的控制，值得探究。

![[Pasted image 20251222181337.png]]

上述内核代码版本是: linux-xlnx-master (Makefile显示6.12.0)

还好核心部分只有一个源文件，这样除了探究fpga子系统框架外，顺便也让我们更容易窥见Linux内核里子系统的构造特征。

核心框架，对具体外设的函数调用，其实都是通过回调实现，或者说通过函数指针实现。为了方便我们集中焦点，下面的结构体成员只保留了我们关心的部分。具体外设通过相关的注册函数，把操作集ops注册到该结构体里的 mops 成员。

```cpp
struct fpga_manager {
    const char *name;
    const struct fpga_manager_ops *mops;
};

// fpga-mgr.c: 框架通过函数指针来执行特定驱动的操作函数
static inline enum fpga_mgr_states fpga_mgr_state(struct fpga_manager *mgr)
{
    if (mgr->mops->state)
        return  mgr->mops->state(mgr);
    return FPGA_MGR_STATE_UNKNOWN;
}
```

fpga-mgr是一个类，它被注册到内核里：结合类注册的代码分析，它被作为一个kset实体，被注册到内核里。由此可见，在内核里，子系统可以用 kset 实体来表示。

![[Pasted image 20251222181357.png]]



```cpp
// 下面是类注册函数,里面是我们当前关心的部分
int class_register(const struct class *cls)
{
	struct subsys_private *cp;
	
	cp = kzalloc(sizeof(*cp), GFP_KERNEL);
	cp->class = cls;
	
	// 类名: 比如 "/sys/class/fpga_manager" 里的 "fpga_manager"
	error = kobject_set_name(&cp->subsys.kobj, "%s", cls->name);
	
	// 设置该类的所属集合
	cp->subsys.kobj.kset = class_kset;
	cp->subsys.kobj.ktype = &class_ktype;

	// 把该类塞到类集合里
	error = kset_register(&cp->subsys);
	sysfs_create_groups(&cp->subsys.kobj, cls->class_groups);
}
```


fpga-mgr的核心数据结构是: struct fpga_manager;

![[Pasted image 20251222181423.png]]


管理核心的数据结构是: struct fpga_manager { … };

![[Pasted image 20251222181439.png]]



