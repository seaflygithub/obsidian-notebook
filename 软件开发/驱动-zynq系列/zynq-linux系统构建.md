
## **使用SDK开发Linux应用程序**

1、这一小节比较简单，只要熟练使用SDK，就能轻松掌握。用图形化的目的是帮我们自动生成Makefile。

2、启动SDK，甚至无需HDF文件，直接新建一个存放SDK工程的文件夹，并把全路径填入SDK的工作空间中。只要OS平台选择Linux即可，其他参数无需动，然后直接选择hello world模板，就能创建一个直接可以交叉编译的Linux应用程序。

![[Pasted image 20251225162821.png]]



## **浅度移植UBOOT**

参考文章：Linux系统移植一：移植U-BOOT 添加自己的板子并编译（非petalinux版）

[[128138579]]

01、这里所说的浅度移植，是指修改几个顶层配置文件的移植，后续进阶的时候会继续记录另一个章节，可能称为 "深度移植UBOOT" 类似的章节标题。浅度移植基本上只要跟着标准流程，使用官方指定的UBOOT版本，做浅层的配置修改重新编译，就能成功。

### **HDF转换成设备树**

1、设备树编译命令dtc的准备：url = [[dtc.git]] 通过官方链接下载对应版本的源码包，然后跟着README进行配置编译，最终生成dtc命令，把该命令路径信息弄到环境变量里即可使用该命令。

2、设备树仓库环境准备，到Xilinx github官方仓库里找到 `device-tree-xlnx` 这个仓库，然后clone对应的版本，版本尽量和你XSDK环境版本匹配。比如 XSDK 2018.3，那么就克隆2018.3的版本。在XSDK界面上找到菜单【 Xilinx >> Repositories】并添加刚刚克隆的仓库。

---

1、首先拿到逻辑人员导出的HDF文件，即硬件描述文件，PS这边只需要一个HDF文件即可。

2、然后新建一个空文件夹（比如 hello.sdk ），因为后续这个空文件夹将作为XSDK的workspace。然后把空文件夹的全路径名拷贝下来，启动XSDK，把全路径贴上去（比如 `D:/project/hello.sdk` ）。然后在Welcome界面，点击【创建应用工程】，然后工程模板我们选择FSBL。模板选好后，硬件平台需要选成我们的HDF文件，经过简单几步HDF导入操作后，后续的流程就和XSDK常规流程一样了，这就是硬件平台的导入。最好修改一下FSBL内存空间指定为iram所在地址空间(比如 `ps7_ddr_0` 改为 `ps7_ram_0`)。

![[Pasted image 20251225162850.png]]


3、创建设备树工程，通过XSDK界面，直接新建BSP，选择设备树，然后填充bootargs即可。工程生成完成后，设备树目录下的顶层Makefile是一个空文件，所以需要我们填充编译规则进去，然后这个设备树目录就可以单独拷贝到Linux下进行编译了。

```markdown
#bootargs of devicetree
console=ttyPS0,115200n8 earlyprintk rootwait
```

![[Pasted image 20251225162914.png]]


```makefile
all:
	$(RM) -r system-top.dtb
	gcc -E -nostdinc -undef -D__DTS__ -x assembler-with-cpp -o system-top.dts.tmp system-top.dts
	dtc -I dts -O dtb -o system-top.dtb system-top.dts.tmp
```



### **移植UBOOT-添加设备树信息**

01、下载对应版本UBOOT源码（比如黑金AX7020，我这里下载2018.3分支）: [[u-boot-xlnx]]

02、解压UBOOT源码，并拷贝前面生成的设备树源文件到 arch/arm/dts/ 目录下，并重命名 system-top.dts 为 zynq-ax7020.dts。
```dts
#include "zynq-7000.dtsi"
#include "pl.dtsi"
#include "pcw.dtsi"
```
system-top.dts 可能会包含上面这些文件，把 u-boot 那边没有的 pl.dtsi 和 pcw.dtsi 都拷贝到 u-boot 对应的设备树目录下。


03、修改设备树文件 zynq-ax7020.dts，根据板子和自己的需求配置。

04、进入/arch/arm/dts ，修改Makefile，找到 `dtb-$(CONFIG_ARCH_ZYNQ)` 配置，添加 zynq-ax7020.dtb 在尾部。


### **移植UBOOT-修改配置头文件**

进入/include/configs目录下，拷贝一份 zynq-common.h，并重命名为 ax7020-common.h，并修改这个新命名的文件。打开文件，找到 `Default environment` 字样所在位置，然后开始修改，这一步最为关键，也能更好地理解u-boot是如何启动内核过程的。

找到 CONFIG_EXTRA_ENV_SETTINGS 宏，设置了u-boot是如何加载内核镜像，如何从SD卡、QSPI、USB启动的；由于我们是准备从SD卡启动u-boot，所以我们需要理解并修改 sdboot，找到sdboot关键词，修改成如下内容：

```cpp
//原内容
	"sdboot=if mmcinfo; then " \\
			"run uenvboot; " \\
			"echo Copying Linux from SD to RAM... && " \\
			"load mmc 0 ${kernel_load_address} ${kernel_image} && " \\
			"load mmc 0 ${devicetree_load_address} ${devicetree_image} && " \\
			"load mmc 0 ${ramdisk_load_address} ${ramdisk_image} && " \\
			"bootm ${kernel_load_address} ${ramdisk_load_address} ${devicetree_load_address}; " \\
		"fi\\0" \\

//修改之后的内容
	"sdboot=if mmcinfo; then " \\
			"run uenvboot; " \\
			"echo Copying Linux from SD to RAM... && " \\
			/* 从SD卡拷贝bitstream文件到内存 */ \\
			"load mmc 0 ${bitstream_load_address} ${bitstream_image} && " \\
			/* 从内存中加载bitstream数据到FPGA */
			"fpga loadb 0 ${bitstream_load_address} ${bitstream_size} && " \\
			/* 从SD卡拷贝内核镜像到内存 */ \\
			"load mmc 0 ${kernel_load_address} ${kernel_image} && " \\
			/* 从SD卡拷贝设备树到内存 */
			"load mmc 0 ${devicetree_load_address} ${devicetree_image} && " \\
			"bootz ${kernel_load_address} - ${devicetree_load_address}; " \\
		"fi\\0" \\
```

接下来我们需要设置这几个变量，有一些是自动生成的，没有的话须要自行设置。网络环境也需要宏定义一下，否则会报错。

```cpp
//original code
#define CONFIG_EXTRA_ENV_SETTINGS	\\
	"ethaddr=00:0a:35:00:01:22\\0"	\\
	"kernel_image=uImage\\0"	\\
	"kernel_load_address=0x2080000\\0" \\
	"ramdisk_image=uramdisk.image.gz\\0"	\\
	"ramdisk_load_address=0x4000000\\0"	\\
	"devicetree_image=devicetree.dtb\\0"	\\
	"devicetree_load_address=0x2000000\\0"	\\
	"bitstream_image=system.bit.bin\\0"	\\
	"boot_image=BOOT.bin\\0"	\\
	"loadbit_addr=0x100000\\0"	\\
	"loadbootenv_addr=0x2000000\\0" \\
	"kernel_size=0x500000\\0"	\\
	"devicetree_size=0x20000\\0"	\\
	"ramdisk_size=0x5E0000\\0"	\\
	"boot_size=0xF00000\\0"	\\

//modified code
#define CONFIG_EXTRA_ENV_SETTINGS	\\
	/* 网络相关 */ \\
	"ethaddr=00:0a:35:00:01:02\\0" \\
	"ipaddr=192.168.1.10\\0" \\
	"serverip=192.168.1.100\\0" \\
	/* 内核镜像名称和加载地址 */ \\
	"kernel_image=zImage\\0" \\
	"kernel_load_address=0x02080000\\0" \\
	/* 根文件系统ramdisk */ \\
	"ramdisk_image=uramdisk.image.gz\\0" \\
	"ramdisk_load_address=0x04000000\\0" \\
	/* 设备树 */ \\
	"devicetree_image=system-top.dtb\\0" \\
	"devicetree_load_address=0x02000000\\0" \\
	/* 比特流文件 */ \\
	"bitstream_image=system.bit\\0" \\
	"bitstream_load_address=0x00100000\\0" \\
	"bitstream_size=0x00300000\\0" \\
	/* BOOT镜像文件 */ \\
	"boot_image=BOOT.bin\\0" \\
```

进入/include/configs目录下，拷贝一份 zynq_zc70x.h，并重命名为 zynq_ax7020.h，然后修改这个新文件，把 `#include <configs/zynq-common.h>` 改为 `#include <configs/ax7020-common.h>` ，修改之后，继续下一步骤。




### **移植UBOOT-修改顶层配置**

01、进入顶层 configs 目录下，拷贝一份配置文件，把 zynq_zc702_defconfig 拷贝为 zynq_ax7020_defconfig，然后修改新文件，主要修改项及说明如下：

```markdown
# 1. head file in "include/configs/zynq_ax7020.h"
CONFIG_SYS_CONFIG_NAME="zynq_ax7020"
# 2. u-boot start delay for 5s
CONFIG_BOOTDELAY=5
# 3. device tree file in arch/arm/dts/zynq-ax7020.dts
CONFIG_DEFAULT_DEVICE_TREE="zynq-ax7020"
# 4. u-boot start banner
CONFIG_IDENT_STRING="ALINX AX7020 by HAMMER"
# 5. boot command
CONFIG_BOOTCOMMAND="run sdboot"
#CONFIG_BOOTCOMMAND="run default_bootcmd"
# 6. UART BASE ADDRESS
CONFIG_DEBUG_UART_BASE=0xe0001000
```

02、uboot支持图形界面配置，修改 arch/arm/mach-zynq/Kconfig 文件，找到 `config SYS_CONFIG_NAME`，修改如下:

```markdown
config SYS_CONFIG_NAME
	string "Board configuration name"
	default "zynq-common"

#修改为:
config SYS_CONFIG_NAME
	string "Board configuration name"
	default "zynq_ax7020"
```



### **移植UBOOT-编译代码**

```bash
# init environment
export ARCH=arm
export CROSS_COMPILE=arm-linux-gnueabihf-
source /Xilinx_2018_03/SDK/2018.3/settings64.sh

make distclean 
make zynq_ax7020_defconfig 
make -j4
```

### **移植UBOOT-运行UBOOT**

01、只要UBOOT编译出来了，执行它的方法很多，比如把编译生成的ELF文件拷贝到SDK环境下，用SDK直接下载 u-boot.elf 来运行；

**运行方式01：直接通过SDK下载运行**

我们直接通过 SDK 来在线下载，指定elf文件为u-boot相关文件即可。然后往SD卡里拷贝一个bit文件，该文件支持纯PL点亮LED，并命名为 system.bit，然后启动u-boot后，手动加载这个bit文件，查看点灯现象。

```markdown
U-Boot 2018.01 (Aug 22 2024 - 11:12:53 +0800) Xilinx Zynq ax7020

Board: Xilinx Zynq
Silicon: v3.1
I2C:   ready
DRAM:  ECC disabled 1 GiB
MMC:   
Invalid bus 0 (err=-19)
*** Warning - spi_flash_probe_bus_cs() failed, using default environment

In:    serial@e0001000
Out:   serial@e0001000
Err:   serial@e0001000
Net:   No ethernet found.
** Bad device mmc 0 **
Hit any key to stop autoboot:  0 
## Error: "default_bootcmd" not defined
Zynq-UBOOT# 
Zynq-UBOOT# run sdboot
```

如下所示，手动执行比特流加载命令，执行完fpga加载之后，就能立马看到PL点亮LED效果了:

```markdown
Zynq-UBOOT# 
Zynq-UBOOT# load mmc 0 ${bitstream_load_address} ${bitstream_image}
reading system.bit
4045676 bytes read in 233 ms (16.6 MiB/s)
Zynq-UBOOT# fpga loadb 0 ${bitstream_load_address} ${bitstream_size}
  design filename = "design_1_wrapper;UserID=0XFFFFFFFF;Version=2018.3"
  part number = "7z020clg400"
  date = "2024/08/22"
  time = "11:38:50"
  bytes in bitstream = 4045564
zynq_align_dma_buffer: Align buffer at 100070 to fff80(swap 1)
Zynq-UBOOT# 此时可以看到板子上的LED灯闪烁了
Zynq-UBOOT# 
```

## **ZYNQ-浅度移植KERNEL**

参考文章: # ZYNQ跑系统 系列（一） 传统方式移植linux [[86151860]]

官网源代码: [[linux-xlnx]]

对应版本分支: [[xilinx-v2018.3]]

### **配置编译内核**

01、配置并编译Linux内核

```bash
# init environment
export ARCH=arm
export CROSS_COMPILE=arm-linux-gnueabihf-
source /Xilinx_2018_03/SDK/2018.3/settings64.sh

make distclean 
cp -v arch/arm/configs/xilinx_zynq_defconfig .config
make xilinx_zynq_defconfig
make menuconfig
make -j4 uImage LOADADDR=0x00008000
```

02、下面是扩展知识的探究，在本小节可忽略。在编译制作uImage时，有一个显式传递的参数 LOADADDR，根据对 uImage 文件头的初步分析，这个 LOADADDR 最终文件头部前64字节内，这64字节是一个结构体，LOADADDR 的值存放在 ih_load 和 ih_ep 成员里，EP表示入口指针，即内核的运行地址。为了进一步清晰确认，需要分析加载 uImage 的bootm源代码。

```bash
# <https://lxr.missinglinkelectronics.com/linux/arch/arm/boot/Makefile>
ifneq ($(LOADADDR),)
    UIMAGE_LOADADDR=$(LOADADDR)
endif
```

### **启动内核**

02、启动文件的准备，编译好的设备树文件可以在前面u-boot小节对应目录找到，比如 arch/arm/dts/zynq-ax7020.dtb，把这些文件都拷贝到SD卡（system.bit、zynq-ax7020.dtb、uImage、uramdisk.image.gz），然后手动通过SDK下载u-boot.elf 来启动，进入到u-boot命令行之后，手动执行如下加载运行命令。

```markdown
load mmc 0 ${bitstream_load_address} ${bitstream_image}
fpga loadb 0 ${bitstream_load_address} ${bitstream_size}

setenv -f devicetree_image "zynq-ax7020.dtb"
load mmc 0 ${devicetree_load_address} ${devicetree_image}

setenv -f kernel_image uImage
load mmc 0 ${kernel_load_address} ${kernel_image}

# run this cmd if you don't need ramdisk/rootfs. bootm-->uImage, bootz-->zImage
bootm ${kernel_load_address} - ${devicetree_load_address}

# run this cmd for full loading (run with ramdisk)
load mmc 0 ${ramdisk_load_address} ${ramdisk_image}
bootm ${kernel_load_address} ${ramdisk_load_address} ${devicetree_load_address}
```


## **ZYNQ-ramdisk制作（busybox）**

参考文章: 
（1）Linux kernel + busybox自制Linux系统 [[107737843]] 
（2）【野火】busybox根文件系统的构建: [[busybox.html]] 
（3）【野火】根文件系统的介绍: [[rootfs_introduce.html]]

源代码下载: [[busybox-1.36.1.tar.bz2]]

```bash
# init environment
export ARCH=arm
export CROSS_COMPILE=arm-linux-gnueabihf-
source /Xilinx_2018_03/SDK/2018.3/settings64.sh

make defconfig
make menuconfig
make -j4
make install     #默认路径为当期目录的_install文件夹
```

注意一定要勾选这个选项: ，否则根文件系统起不来。

```xml
[*] Don't use /usr
[*] Build static binary (no shared libs)
```

基于busybox制作ramdisk根文件系统rootfs. 基于busybox的文件系统启动过程：`/sbin/init => /etc/inittab => /etc/init.d/rcS => /etc/fstab ...`

```bash
# DIR_INSTALL==busybox-x.xx.x/_install
DIR_CUR=`pwd`
DIR_INSTALL=${DIR_CUR}/_install
echo "    "
echo "---------------------- clean old ramdisk --------------------------"
sudo rm -rf ramdisk*

echo "    "
echo "---------------------- create rootfs dirs -------------------------"
cd ${DIR_INSTALL}
mkdir -p dev etc home lib mnt proc root sys tmp var

echo "    "
echo "---------------------- create etc/inittab -------------------------"
touch etc/inittab ; chmod 755 etc/inittab
cat > etc/inittab <<-EOF
::sysinit:/etc/init.d/rcS
::respawn:-/bin/sh
::askfirst:-/bin/sh
::cttlaltdel:/bin/umount -a -r
EOF

# inittab grammars：
# <id>:<runlevels>:<action>:<process>
# id : /dev/id
# runlevels : you can ignore it
# action : when call it? such as sysinit, respawn, askfirst, wait, once,restart, ctrlaltdel, and shutdown
# process : elf or other executable script or program

echo "    "
echo "---------------------- create etc/init.d/rcS ----------------------"
mkdir -p etc/init.d/
touch etc/init.d/rcS ; chmod 755 etc/init.d/rcS
cat > etc/init.d/rcS <<-EOF
echo "----------mount all in fstab----------------"
/bin/mount -a

mkdir -p /dev/pts
mount -t devpts devpts /dev/pts
echo /sbin/mdev > /proc/sys/kernel/hotplug
mdev -s
echo "**************** Hello ax7020 ******************"
echo "Kernel Version: linux-xlnx-xilinx-v2018.3"
echo "************************************************"

#echo "++ Starting udpfan daemon"
#/sdcard/udpfan.elf 0 5 &
EOF

echo "    "
echo "---------------------- create etc/fstab ---------------------------"
touch etc/fstab
cat > etc/fstab <<-EOF
#device mount-point type option dump fsck
proc  /proc proc  defaults 0 0
temps /tmp  rpoc  defaults 0 0
none  /tmp  ramfs defaults 0 0
sysfs /sys  sysfs defaults 0 0
mdev  /dev  ramfs defaults 0 0
EOF

echo "    "
echo "---------------------- mknod basic devs ---------------------------"
sudo mknod dev/console c 5 1
sudo mknod dev/null c 1 3
sudo mknod dev/tty1 c 4 1

echo "    "
echo "---------------------- package uramdisk ---------------------------"
cd ${DIR_CUR}
sudo dd if=/dev/zero of=ramdisk.image bs=1M count=4
sudo mke2fs -F ramdisk.image -L “ramdisk” -b 1024 -m 0
sudo tune2fs   ramdisk.image -i 0
mkdir          ramdisk
sudo mount -o loop ramdisk.image ramdisk
sudo cp -rf        ${DIR_INSTALL}/* ramdisk/
sudo umount        ramdisk
sudo chmod a+rwx   ramdisk.image
sudo mkimage -n 'ext2ramdisk' \\
    -A arm -O linux -T ramdisk -C gzip -d \\
    ramdisk.image uramdisk.image.gz
```

内核重新配置，通过menuconfig更改配置：Device Drivers->Block devices->Default RAM disk size

![[Pasted image 20251225163101.png]]

下面是内核启动ramdisk的串口控制台:

```xml
mmc0: new high speed SDHC card at address 59b4
mmcblk0: mmc0:59b4 SDU1  14.8 GiB 
 mmcblk0: p1 p2
RAMDISK: ext2 filesystem found at block 0
RAMDISK: Loading 4096KiB [1 disk] into ram disk... \\
done.
EXT4-fs (ram0): couldn't mount as ext3 due to feature incompatibilities
EXT4-fs (ram0): mounted filesystem without journal. Opts: (null)
VFS: Mounted root (ext4 filesystem) on device 1:0.
Bad inittab entry at line 4
----------mount all in fstab----------------
mount: mounting temps on /tmp failed: No such device
**************** Hello ax7020 ******************
Kernel Version: linux-xlnx-xilinx-v2018.3
************************************************

Please press Enter to activate this console. 
~ # 
~ # fdisk -l /dev/mmcblk0
Disk /dev/mmcblk0: 15 GB, 15938355200 bytes, 31129600 sectors
486400 cylinders, 4 heads, 16 sectors/track
Units: sectors of 1 * 512 = 512 bytes

Device       Boot StartCHS    EndCHS        StartLBA     EndLBA    Sectors  Size Id Type
/dev/mmcblk0p1    0,32,33     130,170,40        2048    2099199    2097152 1024M  e Win95 FAT16 (LBA)
/dev/mmcblk0p2    130,170,41  1023,254,63    2099200   31129599   29030400 13.8G 83 Linux
~ # 
```


## **ZYNQ-Linux应用开发**

### **flash固化脚本**

tmp_mnt/update_qspi.sh

```bash
#/bin/sh

# the purpose of this script is to flash u-boot, Linux, 
# and the Linux ramdisk to QSPI flash

path=$1

if [ $# -ne 1 ] ; then
        echo "usage: update_qspi.sh <path to images>"
        exit
fi

printf "\\nWriting U-boot Image To QSPI Flash\\n\\n"
flashcp -v $path/qspi-u-boot.bin /dev/mtd13

printf "\\nWriting Linux Image To QSPI Flash\\n\\n"
flashcp -v $path/vmlinux.bin /dev/mtd15

printf "\\nWriting Ramdisk Image To QSPI Flash\\n\\n"
flashcp -v $path/ramdisk8M.image.gz /dev/mtd18
```

### **ramdisk打包解包脚本**


ramdisk-uramdisk.sh

```bash
#!/bin/bash

#input:  uramdisk.image.gz
#process: mntdir
#output: uramdisk.image.gz

dir_work=`pwd`
dir_mnt=tmp_mnt
zip_uramdisk=uramdisk.image.gz
zip_ramdisk=ramdisk.image.gz
unzip_ramdisk="${zip_ramdisk%.*}"
SUDO="sudo"

function check_permission()
{
        if [[ $UID -eq 0 ]];then
                SUDO=""
        fi
}

function uramdisk2ramdisk()
{
    mkdir ${dir_work}/${dir_mnt}
    ${SUDO} dd if=${dir_work}/${zip_uramdisk} of=${dir_work}/${zip_ramdisk} skip=16 bs=4
}

function gz2image()
{
    gunzip ${dir_work}/${zip_ramdisk}
    chmod u+rwx ${dir_work}/${unzip_ramdisk}
}

function mntimage()
{
    ${SUDO} mount -o loop ${dir_work}/${unzip_ramdisk} ${dir_work}/${dir_mnt}
}

function umntimage()
{
    ${SUDO} umount ${dir_work}/${dir_mnt}
        if [[ $? -ne 0 ]];then
                echo "current line: $LINENO"
        fi
}

function image2gz()
{
    ${SUDO} gzip ${dir_work}/${unzip_ramdisk}
}

function ramdisk2uramdisk()
{
    #install mkimage: sudo apt-get install -y u-boot-tools
    which mkimage
    if [[ $? -ne 0 ]];then
        echo "please install mkimage: sudo apt-get install -y u-boot-tools"
        exit 1
    fi

    ${SUDO} mkimage -A arm -T ramdisk -C gzip -d ${dir_work}/${zip_ramdisk} ${dir_work}/${zip_uramdisk}

    clean;
}

function clean()
{
    ${SUDO} rm -rf ${dir_work}/${dir_mnt}
    ${SUDO} rm -rf ${dir_work}/${zip_ramdisk}
}

function help()
{
        echo "usage: $0  0   --unpack uramdisk.image.gz"
        echo "usage: $0  1   --pack uramdisk.image.gz"
        exit 1
}

#check arguments
if [[ $# -eq 0 ]];then
        help;
fi

check_permission;
opt=${1}
if [[ $opt -eq 0 ]]; then
        uramdisk2ramdisk;
        gz2image
        mntimage
elif [[ $opt -eq 1 ]]; then
        umntimage
        image2gz
        ramdisk2uramdisk;
else
        help;
fi

#$@
```

### **交叉编译环境**

- 网盘: xilinx_2018.03_crosstools_linux.zip
- Linux发行版: ubuntu18.04
- 第01步: 执行安装脚本(xilinx_2018.03_crosstools_linux/setup.sh)

```bash
#!/bin/bash

dir_cur=`pwd`
dir_sdk=`pwd`/SDK/2018.3

echo "#!/bin/bash" > setzynq.sh
echo "export dir_zynq_sdk=${dir_sdk}" >> setzynq.sh
echo "source ${dir_zynq_sdk}/settings64.sh" >> setzynq.sh
```

第02步: 执行环境变量脚本(xilinx_2018.03_crosstools_linux/setzynq.sh)

```bash
source setzynq.sh
```

第03步: 测试交叉编译命令

```bash
arm-linux-gnueabihf-gcc -v
COLLECT_GCC=arm-linux-gnueabihf-gcc
COLLECT_LTO_WRAPPER=/home/rlk/szsy/zynq/xilinx_2018.03/SDK/2018.3/gnu/aarch32/lin/gcc-arm-linux-gnueabi/bin/....
Target: arm-linux-gnueabihf
Thread model: posix
gcc version 7.3.1 20180314 (Linaro GCC 7.3-2018.04-rc3)
```

第04步: 用xsdk新建Linux应用工程，然后直接把工程拷贝到Linux系统下执行make编译。

至此，完成环境搭建。

SDK/2018.3/settings64.sh

```bash
source ${dir_zynq_sdk}/.settings64-Vivado.sh
source ${dir_zynq_sdk}/.settings64-SDK_Core_Tools.sh

#source /Xilinx_2018_03/Vivado/2018.3/.settings64-Vivado.sh
#source /Xilinx_2018_03/SDK/2018.3/.settings64-SDK_Core_Tools.sh
```

1、GDB利用coredump进行错误定位分析：

![[Pasted image 20251225163152.png]]


## **ZYNQ-uboot启动流程剖析**

```cpp
Model: Zynq ZC702 Development Board

show_board_info(void);

static init_fnc_t init_sequence_r[] = { ... show_board_info, ... };

void board_init_r(gd_t *new_gd, ulong dest_addr)
	...
	run_main_loop();
		main_loop();
```

```cpp
//board/xilinx/zynq/board.c
int board_init(void);

//from drivers/fpga/fpga.c
int __weak fpga_loadbitstream(...);

//from drivers/fpga/xilinx.c
int fpga_loadbitstream(...);
```

## **ZYNQ-Linux-柏飞项目**

QSPI Flash固件组成树状图：

![[Pasted image 20251225163218.png]]

### **自动生成设备树**

1、确保为设备树的生成提供好了仓库：

![[Pasted image 20251225163231.png]]

2、直接通过新建BSP的菜单功能，新建一个设备树，之后会自动根据板子hw信息生成设备树。不过生成的设备树目录里的Makefile几乎是空的没有内容，需要手动添加必要的设备树编译，ZYNQ官方有提供，本笔记代码也贴了。

![[Pasted image 20251225163256.png]]

从官方抄的可以直接用的设备树编译规则：

```makefile
# Makefile generated by Xilinx.
all:
	$(RM) -r system-top.dtb
	gcc -E -nostdinc -undef -D__DTS__ \\
			-x assembler-with-cpp \\
			-o system-top.dts.tmp system-top.dts
	dtc -I dts -O dtb -o system-top.dtb system-top.dts.tmp
```


### **配置和编译u-boot**

01、环境的安装配置: [[Install+Xilinx+Tools]]

02、源代码获取:

- [[embeddedsw.git]]
- [[u-boot-xlnx.git]]
- [[linux-xlnx.git]]
- [[device-tree-xlnx.git]]
- [[dtc.git]]

03、构建u-boot官方说明书: [[Build+U-Boot]]

```markdown
u-boot-master/include/configs/zynq-common.h
#define BOOTENV_DEV_QSPI(devtypeu, devtypel, instance) \\
	"bootcmd_qspi=bootm 0x1200000 0x800000 0x1000000\\0"

Zynq-u-boot> help bootm
bootm - boot application image from memory

Sub-commands to do part of the bootm sequence.  The sub-commands must be
issued in the order below (it's ok to not issue all sub-commands):
	start [addr [arg ...]]
	loados  - load OS image
	ramdisk - relocate initrd, set env initrd_start/initrd_end
	fdt     - relocate flat device tree
	cmdline - OS specific command line processing/setup
	bdt     - OS specific bd_info processing
	prep    - OS specific prep before relocation or go
	go      - start OS
```

### **自动创建下位机APP**

1、这一小节比较简单，只要熟练使用SDK，就能轻松掌握。用图形化的目的是帮我们自动生成Makefile。

2、启动SDK，甚至无需HDF文件，直接新建一个存放SDK工程的文件夹，并把全路径填入SDK的工作空间中。只要OS平台选择Linux即可，其他参数无需动，然后直接选择hello world模板，就能创建一个直接可以交叉编译的Linux应用程序。比如本项目创建的 udpfan 应用程序。

![[Pasted image 20251225163322.png]]


扩展：使用SDK下载u-boot运行。新建一个hello例程，然后按照SDK方式在线下载运行，唯一的区别是，把目标hello.elf文件改成u-boot.elf文件即可。

### **udpfan.elf-网络udp**

就是常规的网络编程

### **udpfan.elf-APB读写模块**

```cpp
struct mod_apb {
	int devfd;
	uintptr_t vaddr;
	uintptr_t paddr;
	long psize;
};
instance_t apb_new(uintptr_t paddr, long psize);
void apb_delete(instance_t *papb);
void apb_wr(instance_t apb, long pos, uint32_t value);
uint32_t apb_rd(instance_t apb, long pos);

uint32_t apb_rd(instance_t apb, long pos)
{
	struct mod_apb *inst = (struct mod_apb *)apb;
	return *(volatile uint32_t *)(inst->vaddr+pos);
}

void apb_wr(instance_t apb, long pos, uint32_t value)
{
	struct mod_apb *inst = (struct mod_apb *)apb;
	volatile uint32_t *LocalAddr = (volatile uint32_t *)(inst->vaddr+pos);
	*LocalAddr = value;
}

void apb_delete(instance_t *papb)
{
	if ( (papb) && (*papb) )
	{
		struct mod_apb *inst = (struct mod_apb *)*papb;

		if (inst->devfd > 0)
			close(inst->devfd);

		if( inst->vaddr >= 0)
			munmap(inst->vaddr, inst->psize);

		memset(inst, 0, sizeof(*inst));
		free(*papb); *papb = NULL;
	}
}

instance_t apb_new(uintptr_t paddr, long psize)
{
	struct mod_apb *inst;
	inst = malloc(sizeof(*inst));
	if (inst == NULL)
	{
		fprintf(stderr,"new apb faild, %s\\r\\n", strerror(errno));
		return NULL;
	}

	inst->paddr = paddr;
	inst->psize = psize;

	inst->devfd = open("/dev/mem", O_RDWR, 0777);
	if( inst->devfd < 0 )
	{
		fprintf(stderr, "open %s failed, %s\\r\\n", "/dev/mem", strerror(errno));
		apb_delete(&inst);
		return NULL;
	}

	inst->vaddr = mmap(NULL, inst->psize, PROT_READ|PROT_WRITE, 
			MAP_SHARED, inst->devfd, inst->paddr);
	if( inst->vaddr == MAP_FAILED )
	{
		fprintf(stderr, "mmap apb failed, %s\\r\\n", strerror(errno));
		apb_delete(&inst);
		return NULL;
	}

	return (instance_t)inst;
}
```




# ZYNQ-调试技巧


1、如何快速下载程序到板子里运行？这里无需启动xsdk界面，这里前期建立好sdk工程后，后续无需启动sdk界面即可实现程序的下载运行操作。

2、下面是参考脚本文件: download_and_run.tcl
脚本参考自: ax7020_axi_dma.sdk\.sdk\launch_scripts 目录里的指定例程运行配置tcl文件。
```tcl
set jtag_name "Digilent JTAG-HS1 210512180081"
set file_init "./ps7_init.tcl"
set file_bit  "./design_1_wrapper.bit"
set file_hdf  "./system.hdf"
set file_elf  "./u-boot.elf"

connect -url tcp:127.0.0.1:3121
source $file_init
targets -set -nocase -filter {name =~"APU*" && jtag_cable_name =~ "$jtag_name"} -index 0
rst -system
after 3000
targets -set -filter {jtag_cable_name =~ "$jtag_name" && level==0} -index 1
fpga -file $file_bit
targets -set -nocase -filter {name =~"APU*" && jtag_cable_name =~ "$jtag_name"} -index 0
loadhw -hw $file_hdf -mem-ranges [list {0x40000000 0xbfffffff}]
configparams force-mem-access 1
targets -set -nocase -filter {name =~"APU*" && jtag_cable_name =~ "$jtag_name"} -index 0
ps7_init
ps7_post_config
targets -set -nocase -filter {name =~ "ARM*#0" && jtag_cable_name =~ "$jtag_name"} -index 0
dow $file_elf
configparams force-mem-access 0

targets -set -nocase -filter {name =~ "ARM*#0" && jtag_cable_name =~ "$jtag_name"} -index 0
con
```

上面脚本的执行方法:
```tcl
# 通过source命令来执行脚本
xsct% cd d:/project/tftp-workdir
xsct% source download_and_run.tcl
```


下面是封装成批处理脚本(download_uboot.bat)，方便填充路径信息:
```bat
@echo off
::由于windows反斜杠,xsct不支持反斜杠
::所以用批处理间接调用上面的 tcl 脚本, (PATH要能找到xsct命令)
::set file_tcl="D:\project\ax7020\ax7020_axi_dma\ax7020_axi_dma.sdk\.sdk\launch_scripts\xilinx_c-c++_application_(system_debugger)\system_debugger_using_debug_myboot.elf_on_local.tcl"

set file_tcl="D:\project\tftp-workdir\download_and_run.tcl"

xsct %file_tcl%
```


下面是 Linux 系统下的脚本文件: download_uboot.sh
```bash
source ~/sw/desktop/xsdk-2018.3-settings64.sh

file_tcl=download_and_run.tcl

xsct ${file_tcl}
```




---

这里为了调试期间方便起见，这里直接用u-boot命令：

```bash
# 加载bit文件,执行完后,会反馈字节数,后续需要用到这个字节数
fatload mmc 0 0x4000000 /system-top-sgdma.bit
fpga loadb 0 0x4000000  <字节数>

fatload mmc 0 0x1800000 /system-top-sgdma.dtb
fatload mmc 0 0x1900000 /uImage
fatload mmc 0 0x1000000 /uramdisk.image.gz
bootm  0x1900000  0x1000000  0x1800000
# bootm  <kernel>  <ramdisk>  <dtb>
```


下面是通过网络tftp方式获取相关文件并运行：
```bash
set ipaddr 192.168.1.10
set serverip 192.168.1.28
setenv bootargs 'console=ttyPS0,115200 root=/dev/ram rw earlyprintk'
tftpboot  0x4000000  design_1_wrapper.bit
fpga loadb 0 0x4000000 ${filesize}
tftpboot  0x1800000  zynq-ax7020.dtb
tftpboot  0x1900000  uImage
tftpboot  0x1000000  uramdisk.image.gz
bootm  0x1900000  0x1000000  0x1800000
```

---

也可以把上面这些写到文件里并存放在sd卡里，方便快速加载执行
```bash
fatload mmc 0:1 0x03000000 boot.txt
source 0x03000000
```


但是需要修改 u-boot 源代码文件，让其支持txt纯文本文件加载并执行：
```cpp
// u-boot-xlnx-xilinx-v2018.3/cmd/source.c
// source()函数的default分支:

{
	// max 8KB script content
	// 该大数组建议放到全局变量区
	static char tmpcmd[8192] = "";
	const char *strcmd = (const char *)addr;

	printf("script content: \r\n");
	printf("%s\r\n", strcmd);

	//合并换行符,并添加分号
	memset(tmpcmd, 0, sizeof(tmpcmd));
	for(int i=0; i<8192; i++)
	{
		if (strcmd[i] == 0)
				break;

		if ( (strcmd[i] == '\r') || (strcmd[i] == '\n') ) 
		{
			tmpcmd[i] = ';';
		} else
		{
			tmpcmd[i] = strcmd[i];
		}
	}

	// run 
	if (tmpcmd[0] != 0)
	{
		run_command(tmpcmd, 0);
	}
}
```


---





<font color=blue>CHATGPT: 我现在有一个 system.hdf 文件，是 ax7020 的，电脑上有 Xilinx SDK 2018.3 环境。现在我不想启动SDK界面程序，我想通过 TCL 命令来自动生成设备树。</font>

1、先激活编译环境:
```bash
source /opt/Xilinx/SDK/2018.3/settings64.sh
```


2、最小可用 TCL 脚本（核心部分）
```tcl
# =========================
# gen_dts.tcl
# =========================

# 1. 设置路径
set hdf_file "./system.hdf"
set ws_path  "./sdk_ws"

# 2. 创建 workspace
setws $ws_path

# 3. 导入硬件平台
createhw -name hw_0 -hwspec $hdf_file

# 4. 创建 device-tree BSP
createbsp -name device_tree_bsp \
          -hwproject hw_0 \
          -proc ps7_cortexa9_0 \
          -os device_tree

# 5. 生成 BSP（关键）
generatebsp -bsp device_tree_bsp

# 6. 退出
exit
```


3、执行tcl脚本: xsct gen_dts.tcl

执行完成后，你会得到:
```txt
sdk_ws/
└── device_tree_bsp/
    └── device-tree/
        └── system.dts
```













# bottom


