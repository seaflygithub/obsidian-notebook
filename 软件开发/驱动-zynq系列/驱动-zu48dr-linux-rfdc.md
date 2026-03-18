
附件: 网盘: zu48dr_linux_rfdc_250725.zip
附件: 网盘: linux-xlnx-master-zu48dr-250815.zip
附件: 网盘: ZU48DR_0608（白云鹏自回环裸机运行效果）.rar
附件: 网盘: loop_test.sdk-250819.zip

总共三大点：

- 驱动支持
- 库支持（libmetal等库）
- 应用开发


## 驱动支持

解决方法: 内核配置打开UIO等配置

经过验证，官方例程能编译，但是运行的返回结果失败，而白工自回环裸机例程运行成功。所以后续会基于白工自回环的例程来进行摸索。

运行失败，应用程序方面，最终定位在找不到 usp_rf_data_converter 设备对应的驱动。 设备树对应的节点为 pl.dtsi: usp_rf_data_converter@80000000。

![[Pasted image 20251222212956.png]]

[[using-rfdc-driver-in-linux-failed-to-open-device?language=zh_CN]] Using RFdc driver in Linux - Failed to open device In order to use use the RFdc driver with libmetal, you need to make the UIO and VFIO kernel modules built-in. My code snippet of the config looks like this:
```bash
#
# DMABUF options
#
CONFIG_SYNC_FILE=y
# CONFIG_SW_SYNC is not set
# CONFIG_AUXDISPLAY is not set
CONFIG_UIO=y
# CONFIG_UIO_CIF is not set
CONFIG_UIO_PDRV_GENIRQ=y
CONFIG_UIO_DMEM_GENIRQ=y
# CONFIG_UIO_AEC is not set
# CONFIG_UIO_SERCOS3 is not set
CONFIG_UIO_PCI_GENERIC=y
# CONFIG_UIO_NETX is not set
# CONFIG_UIO_PRUSS is not set
# CONFIG_UIO_MF624 is not set
CONFIG_UIO_XILINX_APM=y
CONFIG_VFIO_IOMMU_TYPE1=y
CONFIG_VFIO_VIRQFD=y
CONFIG_VFIO=y
# CONFIG_VFIO_NOIOMMU is not set
CONFIG_VFIO_PCI=y
CONFIG_VFIO_PCI_MMAP=y
CONFIG_VFIO_PCI_INTX=y
CONFIG_VFIO_PLATFORM=y
CONFIG_VFIO_AMBA=y
# CONFIG_VFIO_PLATFORM_CALXEDAXGMAC_RESET is not set
# CONFIG_VFIO_PLATFORM_AMDXGBE_RESET is not set
# CONFIG_VFIO_MDEV is not set
CONFIG_IRQ_BYPASS_MANAGER=y
# CONFIG_VIRT_DRIVERS is not set
CONFIG_VIRTIO=y

CONFIG_VFIO_MDEV=y
CONFIG_VIRT_DRIVERS=y
CONFIG_VIRTIO_PCI=y
# CONFIG_VIRTIO_BALLOON is not set
# CONFIG_VIRTIO_INPUT is not set
CONFIG_VIRTIO_MMIO=y
# CONFIG_VIRTIO_DEBUG is not set
```


按照上面的配置，修改defconfig文件，一个一个认真修改，然后重新配置编译内核。

之后移植的例程可以正常运行了。以下是能正常运行rfdc自回环例程的要点：
（1）内核支持rfdc驱动；
（2）bit流文件别用错，其对应的 .xsa 文件自动生成的设备树里，pl.dtsi 里必须要有 usp_rf_data_converter 这个节点。


## 库移植（libmetal等库）

参考: zu48dr_linux_rfdc_250725.zip

## 应用创建

参考: zu48dr_linux_rfdc_250725.zip





