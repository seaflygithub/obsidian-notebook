

该笔记包含完整Linux系统启动链路概览、u-boot、rootfs



在真实 zynqmp 上的启动链路是(在bit两边夹了新东西)：
BootROM → FSBL → PMUFW → bit --> ATF(BL31) → U-Boot → Linux




