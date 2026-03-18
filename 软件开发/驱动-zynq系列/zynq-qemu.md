
# 初体验虚拟zc702


参考笔记: [[docker-qemu虚拟环境]]

qemu官方文档: https://www.qemu.org/docs/master/system/arm/xlnx-zynq.html

QEMU xilinx-zynq-a9 board supports following devices:
- A9 MPCORE
    - cortex-a9
    - GIC v1
    - Generic timer
    - wdt
- OCM 256KB
- SMC [[mailto:SRAM%400xe2000000]] 64MB
- Zynq SLCR
- SPI x2
- QSPI
- UART
- TTC x2
- Gigabit Ethernet Controller x2
- SD Controller x2
- XADC
- Arm PrimeCell DMA Controller
- DDR Memory
- USB 2.0 x2


---

## 编译运行内核


1、**准备qemu运行环境**：在VMware虚拟机Ubuntu 20.04 LTS里的 docker 容器里的 qemu-8.2.0 里虚拟了一个zynq开发板。docker主要方便环境迁移。网盘搜索: docker-image-ubuntu-qemu-8.2.0 关键字。


2、qemu查看支持开发板:
```bash
root@docker:/workdir/docker# qemu-system-arm -machine help
xilinx-zynq-a9       Xilinx Zynq Platform Baseboard for Cortex-A9
```


3、解压Linux内核源码，然后在容器内编译内核和设备树:
```bash
export ARCH=arm
export CROSS_COMPILE=arm-linux-gnueabihf-

#make clean
#make distclean
cd linux-xlnx-xilinx-v2018.3/
make xilinx_zynq_defconfig
#make menuconfig
make -j4 uImage LOADADDR=0x00008000
make dtbs
```


4、根文件系统是 `rootfs.ext4`（块设备镜像）和 `uramdisk.image.gz`（RAM 磁盘镜像）和 `rootfs.cpio.gz`（cpio 格式压缩包）三者的区别。

用qemu启动Linux内核:
```bash
cd linux-xlnx-xilinx-v2018.3/arch/arm/boot

# 参数 rootfs.cpio.gz 可以直接换成 uramdisk.image.gz
qemu-system-arm -M xilinx-zynq-a9 -m 1024 \
		-serial null -serial mon:stdio -display none \
		-dtb dts/zynq-zc702.dtb \
		-kernel zImage \
		-initrd /workdir/sources/uramdisk.zynq.image.gz \
		-append "console=ttyPS0,115200 root=/dev/ram rw init=/linuxrc"
```


5、Ctrl+A x 组合键来结束虚拟系统。


## 编译运行u-boot


1、解压u-boot源码，然后接下来在容器中编译。


2、编译u-boot：
```bash
export ARCH=arm
export CROSS_COMPILE=arm-linux-gnueabihf-

cd u-boot-xlnx-xilinx-v2018.3/
make zynq_zc702_defconfig
make -j4
```


3、qemu运行u-boot:
```bash
qemu-system-arm -M xilinx-zynq-a9 -m 1024 \
	-serial null -serial mon:stdio -display none \
	-nographic \
	-kernel u-boot
```


# 初体验虚拟zcu102


## 编译运行u-boot

```bash
export CROSS_COMPILE=aarch64-linux-gnu-
export ARCH=aarch64

# 配置 u-boot
make xilinx_zynqmp_zcu102_revB_defconfig
export DEVICE_TREE="zynqmp-zcu102-revB"

# 编译 u-boot
make -j4

# qemu-system-aarch64 -machine help 找到 xlnx-zcu102
# 运行u-boot
qemu-system-aarch64 -M xlnx-zcu102 -m 1024 \
	-serial null -serial mon:stdio -display none \
	-nographic \
	-kernel u-boot
	
qemu-system-aarch64 -M xlnx-zcu102,secure=on,virtualization=on \
		-m 2G -serial stdio -display none \
		-device loader,file=/workdir/sources/pmufw.elf,addr=0xFFDF0000 \
		-device loader,file=u-boot.elf \
		-kernel /workdir/sources/bl31.elf
```



在真实 zynqmp 上的启动链路是(在bit两边夹了新东西)：
BootROM → FSBL → PMUFW → bit --> ATF(BL31) → U-Boot → Linux


