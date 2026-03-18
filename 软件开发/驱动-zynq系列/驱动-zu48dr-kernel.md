
设备树文件:

参考文件1: linux-xlnx-xilinx-v2020.2/arch/arm64/boot/dts/xilinx/zynqmp-zcu1285-revA.dts

参考文件2: 利用 vitis 生成的设备树工程

配置文件: linux-xlnx-xilinx-v2020.2/arch/arm64/configs/xilinx_zynqmp_defconfig


## Linux内核镜像文件


Linux内核镜像vmlinux、Image、zImage、uImage区别：
![[Pasted image 20251222220221.png]]



## vitis直接下载运行内核

在 zu48dr 板子上要运行内核，最开始的办法就是制作成 BOOT.bin 然后固化到 QSPI Flash 里，再从qspi 启动，这个过程非常漫长，尤其是固化 Flash 需要的时间很多。而在调试期间避免不了反复修改内核代码和编译内核，这非常影响调试效率。因此想办法能够编译好后，通过某种方式能够下载到板子内存直接运行，这样既提高了调试i效率，也不用频繁烧写 Flash，毕竟 Flash 经不起频繁的烧写。

（1）先搞清楚 u-boot 如何把内核运行起来，比如通过命令行传参启动内核;

（2）比如: booti 命令格式为: booti 内存地址of内核镜像 内存地址of设备树dtb

```cpp
u-boot 命令行运行其他程序的方式:
	boot      -读取环境变量bootcmd来引导内核镜像
	booti     -引导 arm64 内核镜像 Image
	bootm     -引导 u-boot 自定义的内核镜像 uImage
	bootz     -引导 arm 内核镜像 zImage
	bootefi   -引导 arm64 压缩内核镜像 Image.gz
	run       - run commands in an environment variable
	reset     - Perform RESET of the CPU
```

下面是自动编译内核的脚本(build_kernel.sh)，编译完内核后，还能把目标映像文件转换成C语言能加载的数组。

```bash
# 初始化编译环境
source /home/vitis_settings64.sh

# 指定交叉工具链
#export CROSS_COMPILE=aarch64-none-elf-
export CROSS_COMPILE=aarch64-linux-gnu-
export ARCH=arm64

# 参数检查
if [ $# -ge 1 ]; then
    # 比如: bash build_kernel.sh dtbs
    make $@
    exit 0
fi

# 如果没有传入任何参数,则默认重新编译
make clean

# 使用官方默认配置
#linux-xlnx-xilinx-v2020.2/arch/arm64/configs
make xilinx_zynqmp_defconfig
make menuconfig

# 开始编译
make -j4
#make -j4 UIMAGE_LOADADDR=0x8000 uImage

# 转换成数据文件
xxd -i arch/arm64/boot/dts/xilinx/zynqmp-zu48dr.dtb devicetree.dtb.h
xxd -i arch/arm64/boot/Image Image.h
```

下面的这个制作 BOOT.bin 的配置文件，是能够让 u-boot 正常找到内核并启动内核的，借助里面的 load 信息，我们修改内存拷贝代码。

```cpp
//arch = zynqmp; split = false; format = BIN
the_ROM_image:
{
	[bootloader, destination_cpu = a53-0]D:/project/48dr_lwip/48dr.sdk/whfbsp/export/whfbsp/sw/whfbsp/boot/fsbl.elf
	[destination_device = pl]D:/project/48dr_lwip/48dr.sdk/u-boot/_ide/bitstream/zu_top.bit
	[destination_cpu = a53-0]D:/project/48dr_lwip/48dr.sdk/u-boot/Debug/u-boot.elf
	[load = 0x10000000, destination_cpu = a53-0]D:\\project\\48dr_lwip\\48dr.sdk\\Image
	[load = 0x8800000, destination_cpu = a53-0]D:\\project\\48dr_lwip\\48dr.sdk\\zynqmp-zu48dr.dtb
}
```

下面就是 vitis 裸机工程C代码，该例程主要负责把 u-boot 运行起来，

只不过在运行 u-boot 之前，事先把内核映像和设备树dtb文件加载到内存指定地址，方便进入 u-boot 之后能够正常找到地址数据。

![[Pasted image 20251222220439.png]]


```cpp
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"

// hello002.elf --> hello002.elf.bin --> hello002.elf.bin.h
#include "hello002.elf.bin.h"
#include "u-boot.bin.h"
#include "Image.h"
#include "devicetree.dtb.h"

#define log_debug(...)                                            \\
    {                                                             \\
        xil_printf("%s:%s():%d: ", __FILE__, __func__, __LINE__); \\
        xil_printf(__VA_ARGS__);                                  \\
        xil_printf("\\r\\n");                                       \\
    }
#define log_info(...)                                \\
    {                                                \\
        xil_printf("%s():%d: ", __func__, __LINE__); \\
        xil_printf(__VA_ARGS__);                     \\
        xil_printf("\\r\\n");                          \\
    }
#define log_error(...)                                     \\
    {                                                      \\
        xil_printf("%s():%d:Error: ", __func__, __LINE__); \\
        xil_printf(__VA_ARGS__);                           \\
        xil_printf("\\r\\n");                                \\
    }
#define log_warn(...)                                     \\
    {                                                     \\
        xil_printf("%s():%d:Warn: ", __func__, __LINE__); \\
        xil_printf(__VA_ARGS__);                          \\
        xil_printf("\\r\\n");                               \\
    }

typedef void (*image_entry_t)(void);
unsigned char *g_run_addr = NULL;
void run_image(unsigned long image_addr, unsigned long size, unsigned long load_addr)
{
    log_info("copying image to 0x%x, size=%ld", load_addr, size);
    g_run_addr = (unsigned char *)load_addr;
    memcpy(g_run_addr, (unsigned char *)image_addr, size);

    log_info("running image at 0x%x", load_addr);
    image_entry_t entry = (image_entry_t)g_run_addr;
    entry();
}

int main()
{
    init_platform();

    // 加载进度模拟
    const char *appname = "sdk-uboot";
    int loop_count = 5;
    for (int i = 1; i <= loop_count; i++)
    {
        sleep(1);
        log_info("%s loop progress [%d / %d] Hello World!", appname, i, loop_count);
    }

    log_info("will run u-boot.bin");

		// 在启动 u-boot 之前, 把内核和设备树都提前放到指定内存地址
    memcpy(0x8800000, arch_arm64_boot_dts_xilinx_zynqmp_zu48dr_dtb, sizeof(arch_arm64_boot_dts_xilinx_zynqmp_zu48dr_dtb));
    log_info("Device Tree copied to 0x8800000, size=%ld", sizeof(arch_arm64_boot_dts_xilinx_zynqmp_zu48dr_dtb));

    memcpy(0x10000000, arch_arm64_boot_Image, sizeof(arch_arm64_boot_Image));
    log_info("Linux kernel Image copied to 0x10000000, size=%ld", sizeof(arch_arm64_boot_Image));

    unsigned long load_addr = 0x8000000;
    run_image(u_boot_bin, sizeof(u_boot_bin), load_addr);

    cleanup_platform();
    return 0;
}
```


u-boot 源码倒计时结束后自动执行默认命令，默认执行 bootcmd 这个变量里的命令，

经过摸索和尝试，最终确定，bootcmd 里的值，可以通过 defconfig 文件来配置，

比如在 defconfig 文件里，添加 `CONFIG_BOOTCOMMAND="booti 0x10000000 - 0x08000000` 来作为 bootcmd 变量的默认值。或者直接在 u-boot 命令终端执行: booti 0x10000000 - 0x8800000



