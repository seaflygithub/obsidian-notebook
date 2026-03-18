

## zu48dr-硬件信息

板子CPU信息: XCZU48DR-2FFVG1517I

Part: xczu48dr-ffvg1517-2-i

Family: zynquplusRFSOC

vivado版本: Xilinx_Unified_2020.2_1118_1232

设备树: https://github.com/Xilinx/device-tree-xlnx/tree/xilinx-v2020.2

u-boot: https://github.com/Xilinx/u-boot-xlnx/tree/xilinx-v2020.2

Linux内核: https://github.com/Xilinx/linux-xlnx/tree/xilinx-v2020.2

```bash
sudo apt-get install -y bison
sudo apt-get install -y flex
sudo apt-get install -y swig
sudo apt-get install -y libssl-dev
sudo apt-get install -y libfdt-dev libelf-dev
sudo apt-get install -y device-tree-compiler
sudo apt-get install -y gnutls-bin
sudo apt-get install -y libghc-gnutls-dev
sudo apt-get install -y uuid-dev
sudo apt-get install -y pkg-config
sudo apt-get install -y libncurses-dev
```


## QSPI固化并启动hello

板子CPU信息: XCZU48DR-2FFVG1517I

新建 helloworld 裸机工程，并让它循环打印:

```cpp
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"
#include "sleep.h"

int main()
{
    init_platform();

    unsigned long count = 0;
    while (1)
    {
    	sleep(2);
    	printf("[%lu]Hello World Standalone!\\r\\n", ++count);
    }

    cleanup_platform();
    return 0;
}
```

把 helloworld 制作成启动映像文件 BOOT.bin，对应的配置文件 .bif 内容如下:

```cpp
//D:\\project\\48dr_lwip\\48dr.sdk\\helloworld_system\\_ide\\bootimage\\helloworld_system.bif
/* C:/Users/APWHF/AppData/Local/Temp/bootgen_onlyhello_system301211215360433099/sd_card_temp/boot.bif */
/* Command to create bitstream .bin file:       */
/*   bootgen -image <bif_file> -split bin -w    */
/* Command to create BOOT.BIN file:             */
/*   bootgen -arch zynqmp -image <bif_file> -w -o i BOOT.BIN */
/*whfbsp*/
//arch = zynqmp; split = false; format = BIN
the_ROM_image:
{
	[bootloader, destination_cpu = a53-0]D:/project/48dr_lwip/48dr.sdk/whfbsp/export/whfbsp/sw/whfbsp/boot/fsbl.elf
	[destination_device = pl]D:/project/48dr_lwip/48dr.sdk/helloworld/_ide/bitstream/zu_top.bit
	[destination_cpu = a53-0]D:/project/48dr_lwip/48dr.sdk/helloworld/Debug/helloworld.elf
}
```

下面是 QSPI 固化后的启动串口打印:

```bash
Destination Device is PL, changing LoadAddress
Non authenticated Bitstream download to start now
DMA transfer done 
PL Configuration done successfully 
Partition 1 Load Success 
======= In Stage 3, Partition No:2 ======= 
UnEncrypted data Length: 0x7012 
Data word offset: 0x7012 
Total Data word length: 0x7012 
Destination Load Address: 0x0 
Execution Address: 0x0 
Data word offset: 0x83D4C0 
Partition Attributes: 0x116 
QSPI Reading Src 0x20F5300, Dest 0, Length 1C048
.QSPI Read Src 0x107A980, Dest 0, Length 1C048
Partition 2 Load Success 
All Partitions Loaded 
================= In Stage 4 ============ 
PMU-FW is not running, certain applications may not be supported.
Protection configuration applied
Running Cpu Handoff address: 0x0, Exec State: 0
Exit from FSBL 
[1]Hello World Standalone!
[2]Hello World Standalone!
[3]Hello World Standalone!
[4]Hello World Standalone!
[5]Hello World Standalone!
```



## 裸机调试打印


```cpp
#define log_debug(fmt,...) { xil_printf("%s:%s():%d: ", __FILE__, __func__, __LINE__); xil_printf(fmt, __VA_ARGS__); xil_printf("\\r\\n"); }
#define log_info(fmt,...) { xil_printf("%s:%d: ", __FILE__, __LINE__); xil_printf(fmt, __VA_ARGS__); xil_printf("\\r\\n"); }
#define log_error(fmt,...) { xil_printf("%s:%s():%d:Error: ", __FILE__, __func__, __LINE__); xil_printf(fmt, __VA_ARGS__); xil_printf("\\r\\n"); }
#define log_warning(fmt,...) { xil_printf("%s:%s():%d:Warning: ", __FILE__, __func__, __LINE__); xil_printf(fmt, __VA_ARGS__); xil_printf("\\r\\n"); }

// 两种二选一,上面那种,除了fmt,后面还需要跟上参数
#define log_debug(...) { xil_printf("%s:%s():%d: ", __FILE__, __func__, __LINE__); xil_printf(__VA_ARGS__); xil_printf("\\r\\n"); }
#define log_info(...) { xil_printf("%s:%d: ", __FILE__, __LINE__); xil_printf(__VA_ARGS__); xil_printf("\\r\\n"); }
#define log_error(...) { xil_printf("%s:%s():%d:Error: ", __FILE__, __func__, __LINE__); xil_printf(__VA_ARGS__); xil_printf("\\r\\n"); }
#define log_warning(...) { xil_printf("%s:%s():%d:Warning: ", __FILE__, __func__, __LINE__); xil_printf(__VA_ARGS__); xil_printf("\\r\\n"); }
```

模拟循环进度打印:

```cpp
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"
#include "sleep.h"

int main()
{
    init_platform();

	const char *appname = "hello001";
    int loop_count = 128;
    for(int i=1; i<=loop_count; i++)
    {
    	sleep(3);
    	printf("%s loop progress [%d / %d] Hello World!\\r\\n", appname, i, loop_count);
    }

    cleanup_platform();
    return 0;
}
```





## FSBL启动分析

XFSBL_STAGE1 —— 必要的初始化

XFSBL_STAGE2 —— 识别启动模式、初始化启动设备(比如SD卡、QSPI等)

XFSBL_STAGE3 —— 加载分区

XFSBL_STAGE4 —— 跳转到目标地址执行(比如 helloworld.elf)


**使用FSBL加载helloworld**

FSBL源代码无需做任何修改，只需要在下图中勾选 Use FSBL … 相关的选项即可。

![[Pasted image 20251222221251.png]]

如上图所示，在线下载helloworld程序的时候，勾选使用FSBL来初始化，运行之后串口打印如下：

在 XFSBL_STAGE4 的开始就加了循环打印，循环打印之后，立马就跳转到 helloworld 执行了。

```cpp
Xilinx Zynq MP First Stage Boot Loader 
Release 2020.2   Jun 25 2025  -  10:48:32
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [1 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [2 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [3 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [4 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [5 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [6 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [7 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [8 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [9 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [10 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [11 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [12 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [13 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [14 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [15 / 16] Hello World!
xfsbl_main.c:main():256: zynqmp_fsbl loop progress [16 / 16] Hello World!
PMU-FW is not running, certain applications may not be supported.
hello001 loop progress [1 / 128] Hello World!
hello001 loop progress [2 / 128] Hello World!
hello001 loop progress [3 / 128] Hello World!
hello001 loop progress [4 / 128] Hello World!
hello001 loop progress [5 / 128] Hello World!
hello001 loop progress [6 / 128] Hello World!
```


## 软件复位zynqmp处理器

mpsoc系列的复位与zynq 7000系列不太一样，7000是通过slcr寄存器来实现软件复位，MPSOC是通过CRL_APB，具体含义参考ug1085和ug1087，

```cpp
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"
#include "xil_io.h"

#define MPSOC_RESET_REASON_REG 0xFF5E0220  //16bit
#define MPSOC_RESET_CTRL_REG   0xFF5E0218  //寄存器RESET_CTRL
#define MPSOC_RESET_VALUE      0x10        //复位bit4 (Width=8)
 
void PsSoftwareReset(void)
{
    Xil_Out8(MPSOC_RESET_CTRL_REG, MPSOC_RESET_VALUE);  //复位
}
 
void getResetReason(void)
{
	int status;
 
	status = Xil_In16(MPSOC_RESET_REASON_REG);
	xil_printf("\\n\\rResetReason = 0x%.8X\\n\\r", status);
	if(status & 0x40)
		xil_printf("6 Software Debugger Reset\\n\\r");
	if(status & 0x20)
			xil_printf("5 Software System Reset\\n\\r");
	if(status & 0x10)
			xil_printf("4 External System Reset\\n\\r");
	if(status & 0x08)
			xil_printf("3 PS-only Reset\\n\\r");
	if(status & 0x04)
			xil_printf("2 Internal System Reset\\n\\r");
	if(status & 0x02)
			xil_printf("1 A system error triggered a POR reset\\n\\r");
	if(status & 0x01)
			xil_printf("0 the PS_POR_B reset signal pin was asserted\\n\\r");
	xil_printf("\\n\\r");
}
 
int main()
{
    init_platform();
 
    xil_printf("Hello World\\n\\r");
    getResetReason();
    PsSoftwareReset();
    printf("PsSoftwareReset\\n\\r");
 
    printf("Successfully ran Hello World application");
    cleanup_platform();
    return 0;
}
//原文链接：<https://blog.csdn.net/aatu/article/details/121506933>
```



## vitis直接运行hello002.bin

bin文件转换成数组方法: xxd -i test.bin test.bin.h

1、vitis新建一个裸机hello001，就用helloworld模板； 
2、vitis新建一个裸机hello002，同理helloworld模板，加个区分代码； 
3、转换: `hello002.elf --> hello002.bin --> hello002.bin.h`；

```bash
# 把ELF文件转换成二进制.bin文件
aarch64-none-elf-objcopy -S -O binary hello002.elf hello002.elf.bin

# 把二进制文件转换成C语言数组文件
xxd -i hello002.elf.bin hello002.elf.bin.h
```

4、然后通过 hello001 来跳转运行 hello002 程序。

下面是修改后的 hello00 主程序代码，是运行 hello002.bin 的完整示例代码：

```cpp
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"

// 包含 hello002 的数组文件
// hello002.elf --> hello002.elf.bin --> hello002.elf.bin.h
#include "hello002.elf.bin.h"

#define log_debug(...) { xil_printf("%s:%s():%d: ", __FILE__, __func__, __LINE__); xil_printf(__VA_ARGS__); xil_printf("\\r\\n"); }
#define log_info(...) { xil_printf("%s:%d: ", __FILE__, __LINE__); xil_printf(__VA_ARGS__); xil_printf("\\r\\n"); }
#define log_error(...) { xil_printf("%s:%s():%d:Error: ", __FILE__, __func__, __LINE__); xil_printf(__VA_ARGS__); xil_printf("\\r\\n"); }
#define log_warning(...) { xil_printf("%s:%s():%d:Warning: ", __FILE__, __func__, __LINE__); xil_printf(__VA_ARGS__); xil_printf("\\r\\n"); }

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
	const char *appname = "sdk-uboot"; // 本程序名字
    int loop_count = 5;
    for(int i=1; i<=loop_count; i++)
    {
    	sleep(2);
    	log_info("%s loop progress [%d / %d] Hello World!", appname, i, loop_count);
    }

    log_info("will run u-boot.bin");

    // 目标程序代码段起始地址
    unsigned long load_addr = 0x400000;

    // 拷贝到起始地址, 并运行目标程序
    run_image(hello002_elf_bin, sizeof(hello002_elf_bin), load_addr);

    cleanup_platform();
    return 0;
}
```

下面是成功运行 hello002 二进制文件的串口打印效果：

```cpp
Xilinx Zynq MP First Stage Boot Loader 
Release 2020.2   Jun 25 2025  -  17:44:48
xfsbl_main.c:main():255: zynqmp_fsbl loop progress [1 / 4] Hello World!
xfsbl_main.c:main():255: zynqmp_fsbl loop progress [2 / 4] Hello World!
xfsbl_main.c:main():255: zynqmp_fsbl loop progress [3 / 4] Hello World!
xfsbl_main.c:main():255: zynqmp_fsbl loop progress [4 / 4] Hello World!
PMU-FW is not running, certain applications may not be supported.
../src/helloworld.c:100: sdk-uboot loop progress [1 / 4] Hello World!
../src/helloworld.c:100: sdk-uboot loop progress [2 / 4] Hello World!
../src/helloworld.c:100: sdk-uboot loop progress [3 / 4] Hello World!
../src/helloworld.c:100: sdk-uboot loop progress [4 / 4] Hello World!
../src/helloworld.c:103: will run u-boot.bin
../src/helloworld.c:81: copying image to 0x400000
../src/helloworld.c:85: running image at 0x400000
hello002 loop progress [1 / 8] Hello World!
hello002 loop progress [2 / 8] Hello World!
hello002 loop progress [3 / 8] Hello World!
hello002 loop progress [4 / 8] Hello World!
hello002 loop progress [5 / 8] Hello World!
hello002 loop progress [6 / 8] Hello World!
hello002 loop progress [7 / 8] Hello World!
hello002 loop progress [8 / 8] Hello World!
```



## vitis直接运行u-boot.bin


在前面成功在线下载运行 hello002.bin 的前提下，我们进一步要运行 u-boot.bin，

u-boot适配过程中，defconfig 文件 和 dts 设备树文件，都需要从中筛选出最合适的配置组合，然后基于其进一步修改适配。

为什么要运行bin文件而不是直接运行elf文件？

因为bin文件能够直接被CPU执行，无需ELF解析器，因此用来作为前期在线下载调试的有效方法。

```cpp
// hello002.elf --> hello002.elf.bin --> hello002.elf.bin.h
// #include "hello002.elf.bin.h"
#include "u-boot.bin.h"
// #include "Image.h"
// #include "devicetree.dtb.h"
    
    unsigned long load_addr = 0x8000000;
    run_image(u_boot_bin, sizeof(u_boot_bin), load_addr);
```

思路：

关于u-boot的移植适配，首先要认识到的一点，不可能直接拿到100%适配的代码或者配置，

当然有的话最好，这个对于项目赶进度还是有用的，

我们能做到的，就是找到一个最接近我们实际设备的配置，然后在其基础上修改适配，

如何找到最接近实际硬件环境的配置呢，最笨的方法就是一个一个去试，

对比不同配置下编译出来的程序，看看哪个配置下最能正常运行起来，

然后就筛选出最能正常运行起来的配置，基于该配置进行修改适配，

而且，适配的过程不是一蹴而就的，适配的过程是在一点一点成就感积累不断完善适配，

比如筛选出了找到了一个最合适的 defconfig 基于它修改，以及找到一个最合适的设备树配置文件基于它修改，

基于算法领域的偏导数、梯度思想，最终筛选出来的最合适的配置组合，

后续的移植适配，就基于这个配置组合进行进一步的修改适配，

```bash
# if [[ $# -le 0 ]];then
# 	echo "usage: $0  <uboot_src_dir>"
# 	exit 1
# fi

# dir_uboot="$1"
#dir_uboot=u-boot-xlnx-xilinx-v2020.2

# 初始化编译环境
source /home/vitis_settings64.sh
export CROSS_COMPILE=aarch64-none-elf-
export ARCH=aarch64

# 配置 u-boot
#cd ${dir_uboot}/
make distclean
#make xilinx_zynqmp_mini_emmc0_whf_defconfig
# make xilinx_zynqmp_virt_nospl_whf_defconfig #OKOK
make xilinx_zynqmp_virt_whf_defconfig #OKOKOK
# make xilinx_zynqmp_mini_whf_defconfig

# export DEVICE_TREE="zynqmp-zc1232-revA"
# export DEVICE_TREE="zynqmp-zc1254-revA"
# export DEVICE_TREE="zynqmp-zc1751-xm015-dc1"
# export DEVICE_TREE="zynqmp-zc1751-xm016-dc2"
# export DEVICE_TREE="zynqmp-zc1751-xm017-dc3"
# export DEVICE_TREE="zynqmp-zc1751-xm018-dc4"
# export DEVICE_TREE="zynqmp-zc1751-xm019-dc5"
# export DEVICE_TREE="zynqmp-zcu100-revC"
# export DEVICE_TREE="zynqmp-zcu102-rev1.0" #OK 只能打印基本信息
# export DEVICE_TREE="zynqmp-zcu102-revA"
# export DEVICE_TREE="zynqmp-zcu102-revB" #OK 只能打印基本信息
# export DEVICE_TREE="zynqmp-zcu104-revA"
# export DEVICE_TREE="zynqmp-zcu104-revC" #OKOK 识别到以太网phyaddr=12,页表初始化失败
# export DEVICE_TREE="zynqmp-zcu106-revA" #OKOK 识别到以太网phyaddr=12,页表初始化失败
# export DEVICE_TREE="zynqmp-zcu111-revA" #OKOK 识别到以太网phyaddr=12,页表初始化失败
# export DEVICE_TREE="zynqmp-zcu1275-revA"
# export DEVICE_TREE="zynqmp-zcu1275-revB" #OKOK 识别以太网phyaddr=-1,页表初始化失败
export DEVICE_TREE="zynqmp-zcu1285-revA" #OKOKOK 成功进入到 zynqmp 命令行,但是没识别到以太网
# export DEVICE_TREE="zynqmp-zcu208-revA" #OKOK
# export DEVICE_TREE="zynqmp-zcu216-revA" #OKOK 识别到以太网phyaddr=12

# 编译 u-boot
make -j4
ret=$?

if [[ $ret -eq 0 ]];then
    echo "================ u-boot.bin --> u-boot.bin.h ====================="
    xxd -i u-boot.bin u-boot.bin.h
fi

if [[ -e hello001.elf ]];then
    echo "hello001.elf --> hello001.elf.bin --> hello001.elf.bin.h"
    aarch64-none-elf-objcopy -S -O binary hello001.elf hello001.elf.bin
    xxd -i hello001.elf.bin hello001.elf.bin.h
fi

if [[ -e hello002.elf ]];then
    echo "hello002.elf --> hello002.elf.bin --> hello002.elf.bin.h"
    aarch64-none-elf-objcopy -S -O binary hello002.elf hello002.elf.bin
    xxd -i hello002.elf.bin hello002.elf.bin.h
fi
```

基于上面筛选出来的最优配置，我们新建了自己的配置(build_uboot.sh)：

```bash
# if [[ $# -le 0 ]];then
# 	echo "usage: $0  <uboot_src_dir>"
# 	exit 1
# fi

# dir_uboot="$1"
#dir_uboot=u-boot-xlnx-xilinx-v2020.2

# 初始化编译环境
source /home/vitis_settings64.sh
export CROSS_COMPILE=aarch64-none-elf-
export ARCH=aarch64

# 配置 u-boot
#cd ${dir_uboot}/
make distclean
make xilinx_zynqmp_virt_zu48dr_defconfig
export DEVICE_TREE="zynqmp-zu48dr" #别忘了修改arch/arm/dts/Makefile 让它能编译 zynqmp-zu48dr.dts 

# 编译 u-boot
make -j4
ret=$?

if [[ $ret -eq 0 ]];then
    echo "================ u-boot.bin --> u-boot.bin.h ====================="
    xxd -i u-boot.bin u-boot.bin.h
fi

if [[ -e hello001.elf ]];then
    echo "hello001.elf --> hello001.elf.bin --> hello001.elf.bin.h"
    aarch64-none-elf-objcopy -S -O binary hello001.elf hello001.elf.bin
    xxd -i hello001.elf.bin hello001.elf.bin.h
fi

if [[ -e hello002.elf ]];then
    echo "hello002.elf --> hello002.elf.bin --> hello002.elf.bin.h"
    aarch64-none-elf-objcopy -S -O binary hello002.elf hello002.elf.bin
    xxd -i hello002.elf.bin hello002.elf.bin.h
fi
```

通过 helloworld 在线加载：

```cpp
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"

#include "hello002.elf.bin.h"  // hello002.elf --> hello002.elf.bin --> hello002.elf.bin.h
#include "u-boot.bin.h"

#define log_debug(...) { xil_printf("%s:%s():%d: ", __FILE__, __func__, __LINE__); xil_printf(__VA_ARGS__); xil_printf("\r\n"); }
#define log_info(...) { xil_printf("%s:%d: ", __FILE__, __LINE__); xil_printf(__VA_ARGS__); xil_printf("\r\n"); }
#define log_error(...) { xil_printf("%s:%s():%d:Error: ", __FILE__, __func__, __LINE__); xil_printf(__VA_ARGS__); xil_printf("\r\n"); }
#define log_warning(...) { xil_printf("%s:%s():%d:Warning: ", __FILE__, __func__, __LINE__); xil_printf(__VA_ARGS__); xil_printf("\r\n"); }

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
    for(int i=1; i<=loop_count; i++)
    {
    	sleep(1);
    	log_info("%s loop progress [%d / %d] Hello World!", appname, i, loop_count);
    }

    log_info("will run u-boot.bin");

    // 目标程序代码段起始地址
    // unsigned long load_addr = 0x400000;

    // 拷贝到起始地址, 并运行目标程序
    //run_image(hello002_elf_bin, sizeof(hello002_elf_bin), load_addr);

    unsigned long load_addr = 0x8000000;
    run_image(u_boot_bin, sizeof(u_boot_bin), load_addr);

    cleanup_platform();
    return 0;
}
```

经过上述的脚本，最终编译u-boot生成 u-boot.elf，进而生成 u-boot.bin，进而生成 u-boot.bin.h 文件，

我们在线下载运行要的就是这个.h文件，把它拖到 hello001 源码目录，重新编译，然后下载运行，

串口日志记录：

```cpp
Xilinx Zynq MP First Stage Boot Loader 
Release 2020.2   Jun 26 2025  -  10:09:00
xfsbl_main.c:main():255: zynqmp_fsbl loop progress [1 / 5] Hello World!
xfsbl_main.c:main():255: zynqmp_fsbl loop progress [2 / 5] Hello World!
xfsbl_main.c:main():255: zynqmp_fsbl loop progress [3 / 5] Hello World!
xfsbl_main.c:main():255: zynqmp_fsbl loop progress [4 / 5] Hello World!
xfsbl_main.c:main():255: zynqmp_fsbl loop progress [5 / 5] Hello World!
PMU-FW is not running, certain applications may not be supported.
../src/helloworld.c:36: sdk-uboot loop progress [1 / 5] Hello World!
../src/helloworld.c:36: sdk-uboot loop progress [2 / 5] Hello World!
../src/helloworld.c:36: sdk-uboot loop progress [3 / 5] Hello World!
../src/helloworld.c:36: sdk-uboot loop progress [4 / 5] Hello World!
../src/helloworld.c:36: sdk-uboot loop progress [5 / 5] Hello World!
../src/helloworld.c:39: will run u-boot.bin
../src/helloworld.c:17: copying image to 0x8000000, size=1071218
../src/helloworld.c:21: running image at 0x8000000

U-Boot 2020.01 (Jun 26 2025 - 14:22:58 +0800)

Model: ZynqMP zu48dr
Board: Xilinx ZynqMP
DRAM:  2 GiB
PMUFW:  v32234.52800
EL Level:       EL3
Chip ID:        unknown
Multiboot:      0
NAND:  0 MiB
MMC:   mmc@ff170000: 0
In:    serial@ff000000
Out:   serial@ff000000
Err:   serial@ff000000
Bootmode: QSPI_MODE
Reset reason:   DEBUG 
Net:   No ethernet found.
Hit any key to stop autoboot:  0 
u-boot-zynqmp-zu48dr# 
```



## u-boot操作eMMC


```cpp
// 查看这个内存地址的数据
md.w 0x100000

// 查看内存数据,查看 0x08 个单元
u-boot-zynqmp-zu48dr# md.l 0x100000 0x08
00100000: 00000000 00000000 00000000 00000000    ................
00100010: 00000000 00000000 00000000 00000000    ................

// 修改内存数据
u-boot-zynqmp-zu48dr# mw.l 0x100000 0x11223344 0x08
u-boot-zynqmp-zu48dr# md.l 0x100000 0x08
00100000: 11223344 11223344 11223344 11223344    D3".D3".D3".D3".
00100010: 11223344 11223344 11223344 11223344    D3".D3".D3".D3".
u-boot-zynqmp-zu48dr# 
u-boot-zynqmp-zu48dr# mmc info               // 查看eMMC硬件信息
Device: mmc@ff170000
Manufacturer ID: 2c
OEM: 10e
Name: TCY2D 
Bus Speed: 52000000
Mode: MMC High Speed (52MHz)
Rd Block Len: 512
MMC version 5.1
High Capacity: Yes
Capacity: 58.2 GiB
Bus Width: 4-bit
Erase Group Size: 512 KiB
HC WP Group Size: 16 MiB
User Capacity: 58.2 GiB
Boot Capacity: 4 MiB ENH
RPMB Capacity: 4 MiB ENH
u-boot-zynqmp-zu48dr# mmc part              // 查看eMMC分区信息
## Unknown partition table type 0
u-boot-zynqmp-zu48dr# mmc list              // 查看eMMC存储信息
mmc@ff170000: 0 (eMMC)
u-boot-zynqmp-zu48dr# 
u-boot-zynqmp-zu48dr# mmc dev 0             // 切换到0号存储器
switch to partitions #0, OK
mmc0(part 0) is current device
u-boot-zynqmp-zu48dr# 
u-boot-zynqmp-zu48dr# md.l 0x100000 0x08
00100000: 11223344 11223344 11223344 11223344    D3".D3".D3".D3".
00100010: 11223344 11223344 11223344 11223344    D3".D3".D3".D3".
u-boot-zynqmp-zu48dr# mmc write 0x100000 0x0000 0x01   // 把内存数据写入eMMC,从第0x0000块位置开始写,写入0x01块个数

MMC write: dev # 0, block # 0, count 1 ... 1 blocks written: OK
u-boot-zynqmp-zu48dr# 
u-boot-zynqmp-zu48dr# mw.l 0x100000 0x00000000 8       // 清空当前内存区域
u-boot-zynqmp-zu48dr# md.l 0x100000 0x08               
00100000: 00000000 00000000 00000000 00000000    ................
00100010: 00000000 00000000 00000000 00000000    ................
u-boot-zynqmp-zu48dr# 
00100020: 00000000 00000000 00000000 00000000    ................
00100030: 00000000 00000000 00000000 00000000    ................
u-boot-zynqmp-zu48dr# mmc read 0x100000 0x0000 0x01    // 回读eMMC到指定内存地址

MMC read: dev # 0, block # 0, count 1 ... 1 blocks read: OK
u-boot-zynqmp-zu48dr# md.l 0x100000 0x08               // 查看内存数据
00100000: 11223344 11223344 11223344 11223344    D3".D3".D3".D3".
00100010: 11223344 11223344 11223344 11223344    D3".D3".D3".D3".
u-boot-zynqmp-zu48dr# 
```


## u-boot操作QSPI-Flash


```cpp
// 查看设备信息
sf  probe

// 从Flash的0地址读取512字节到内存的 0x100000 地址
u-boot-zynqmp-zu48dr# sf read 0x100000 0 512
device 0 offset 0x0, size 0x512
SF: 1298 bytes @ 0x0 Read: OK

// 下面是 qspi flash常用操作命令, 注意, u-boot里数字默认识别为十六进制
sf read memaddr offset lenbytes
sf write memaddr offset lenbytes
sf erase offset lenbytes
sf update memaddr offset lenbytes //相当于先执行擦除,再执行write
```


## VSCode远程SSH编辑代码

![[Pasted image 20251222220844.png]]

![[Pasted image 20251222220853.png]]








