
附件: 网盘文件: zu48dr_linux系统构建归档250717.zip

zu48dr_linux系统构建归档250717/README.txt 内容如下：
```

zu48dr Linux系统构建记录

zu48dr BOOT.bin 总概览

	先展示BOOT.bin里的文件列表,然后分别阐述里面每个文件的构建记录

	下面这是 BOOT.bin 打包配置:
	the_ROM_image:
	{
		[bootloader, destination_cpu = a53-0]D:/project/48dr_lwip/48dr.sdk/whfbsp/export/whfbsp/sw/whfbsp/boot/fsbl.elf
		[destination_cpu = pmu]D:\\project\\48dr_lwip\\48dr.sdk\\whfbsp\\export\\whfbsp\\sw\\whfbsp\\boot\\pmufw.elf
		[destination_device = pl]D:/project/48dr_lwip/48dr.sdk/u-boot/_ide/bitstream/zu_top.bit
		[destination_cpu = a53-0, exception_level = el-3, trustzone]D:\\project\\48dr_lwip\\48dr.sdk\\bl31.elf
		[load = 0x08000000, destination_cpu = a53-0, exception_level = el-2]D:\\project\\48dr_lwip\\48dr.sdk\\u-boot.elf
		[load = 0x08800000, destination_cpu = a53-0]D:\\project\\48dr_lwip\\48dr.sdk\\devicetree\\system-top.dtb
		[load = 0x10000000, destination_cpu = a53-0, exception_level = el-1]D:\\project\\48dr_lwip\\48dr.sdk\\uImage
		[load = 0x12000000, destination_cpu = a53-0, exception_level = el-1]D:\\project\\48dr_lwip\\48dr.sdk\\uramdisk.image.gz
	}
	
	下面是固化选项: 
		Flash类型: qspi-x8-dual_parallel
		初始化文件: D:\\project\\48dr_lwip\\48dr.sdk\\fsbl_origin.elf 表示vitis自动生成的没有任何更改的fsbl
	
	
	

zu48dr BOOT.bin 每项更改记录: 下面将对上面的文件列表的每一项详细展开描述.

	平台相关的自动生成文件
		48dr.sdk/whfbsp/export/whfbsp/sw/whfbsp/boot/fsbl.elf
		48dr.sdk\\whfbsp\\export\\whfbsp\\sw\\whfbsp\\boot\\pmufw.elf
			该文件由vitis platform自动生成，无需任何修改。

		48dr.sdk/u-boot/_ide/bitstream/zu_top.bit
			该文件是FPGA逻辑人员提供的bit文件。

		48dr.sdk\\bl31.elf
			源代码包: arm-trusted-firmware-master-zu48dr.zip
			编译脚本: arm-trusted-firmware-master/build_atf.sh 
			编译方法: 进入目录后直接执行 bash build_atf.sh 命令编译

	48dr.sdk\\u-boot.elf
		源代码包: u-boot-xlnx-xilinx-v2020.2-zu48dr.zip
		编译脚本: u-boot-xlnx-xilinx-v2020.2-zu48dr/build_uboot.sh
		
		编译方法:
			该文件是自动配置编译脚本,使用方法如下:
			配置: bash  build_uboot.sh  default
			编译: bash  build_uboot.sh
			
		u-boot更改记录:
			1、修改配置文件: configs/xilinx_zynqmp_virt_zu48dr_defconfig
				CONFIG_BOOTARGS             --启动参数(bootargs)
				CONFIG_BOOTDELAY            --启动倒计时秒数(单位:秒)
				CONFIG_BOOTCOMMAND          --倒计时结束后自动运行
				CONFIG_ENV_ADDR             --环境变量存放在Flash起始位置(不能和BOOT.bin所占空间重叠)
				CONFIG_SYS_PROMPT           --u-boot命令行提示符
				CONFIG_DEFAULT_DEVICE_TREE  --默认设备树
			2、重新编译: bash build_uboot.sh 
			3、编译完成,当前目录下会生成一个 u-boot.elf 文件
		
		JTAG固化后环境变量CRC失败问题,u-boot启动后,会有下面bad CRC的错误提示
			# MMC:   mmc@ff170000: 0
			# Loading Environment from SPI Flash... SF: Detected mt25qu02g with page size 256 Bytes, erase size 64 KiB, total 256 MiB
			# *** Warning - bad CRC, using default environment <---此处问题会导致无法保存环境变量到Flash
			# In:    serial@ff000000
			# Out:   serial@ff000000
			# Err:   serial@ff000000
			# Bootmode: QSPI_MODE
			# Reset reason:   SOFT 
			# Net:   No ethernet found.
			# Hit any key to stop autoboot:  0 
		
			解决方法: 在u-boot命令行执行下面命令即可
				env default -a
				saveenv
			执行完之后, 再重启板子即可解决CRC错误问题,就能正常save环境变量到Flash里.

		
	
	48dr.sdk\\devicetree\\system-top.dtb
		源代码包: vitis-xsa-to-devicetree.zip
		编译脚本: 无 
		编译方法: 
			该文件是先用 .xsa 文件自动生成设备树源码包,然后放到内核源码目录下编译,下面将描述编译步骤:
			为了确保编译的设备树dtb可被内核使用,直接参考内核编译设备树的相关参数;
			因此设备树源代码包需要拷贝到内核源码的顶层目录下,再执行编译操作(确保内核已经执行过编译),下面是参考命令:
			
				unzip -q vitis-xsa-to-devicetree.zip
				cp -rf devicetree  ~/home/whf/zynqmp/linux-xlnx-master/
				cd ~/home/whf/zynqmp/linux-xlnx-master/devicetree
				make
			
			如上述操作执行make之后,当前目录就生成了 system-top.dtb 文件
	
	
	48dr.sdk\\uImage
		该文件是内核镜像,是 Image 文件经过加头之后形成 uImage 文件.
		
			#下面三个操作分别是: 配置、编译、生成 uImage 文件, 脚本不复杂
			bash  build_kernel.sh  hzh250716config
			bash  build_kernel.sh  build
			bash  build_kernel.sh  uimage
	

	48dr.sdk\\uramdisk.image.gz
		这是基础根文件系统,首先通过斌哥的 buildroot 编译打包后生成,
		后续如果需要修改里面的文件,这里提供转换脚本,可以把该镜像文件转换成 rootfs 目录, 目录里面就是文件系统内容;
		注意: 必须要切换到 root 用户然后再修改根文件系统镜像内容;
		
		脚本文件: mount_rootfs_image.sh
		
		使用方法: 
			1、准备好要修改的镜像文件: uramdisk.image.gz (该文件是cpio格式并且gzip压缩)
			2、把脚本和镜像文件放在同一个目录
			3、开启一个终端执行该脚本,此时脚本执行的是转换和挂载;
			4、开启另一个终端,在脚本所在目录下,就会多出一个 rootfs 文件夹, 此时文件夹里就是文件系统内容;
			5、修改 rootfs 文件夹里内容完成后,在原先的终端输入ok并回车,就会把 rootfs 再次打包做成 uramdisk.image.gz 
			
		源代码修改(根文件系统加载相关):
			1、修改位置
				linux-xlnx-master/init/do_mounts.c
				prepare_namespace(): 注释了 initrd_load()调用, 直接执行goto语句;
			2、修改原因: 为了让它能够正常加载 uramdisk.image.gz 镜像.

```







