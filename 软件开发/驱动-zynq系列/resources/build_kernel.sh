source /xilinx_sdk_settings64.sh

export ARCH=arm
export CROSS_COMPILE=arm-linux-gnueabihf-

make xilinx_zynq_defconfig
make UIMAGE_LOADADDR=0x8000 uImage -j4
make modules -j4

