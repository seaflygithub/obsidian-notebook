
```cpp
rootfs.ext2 --> rootfs.ext2.cpio --> rootfs.ext2.cpio.gz --> uramdisk.image.gz
```

```bash
img_uramdisk="uramdisk.image.gz"
dir_rootfs="`pwd`/rootfs"

srcdir_rootfs=rootfs
dstdir_rootfs=rootfs_ext4
image_mkfs=mkfs.ext4
image_name=rootfs.ext4
image_sizeMB=64

function uramdisk_to_rootfs()
{
	# 跳过前64字节，输出为纯gzip压缩文件（无头部）
	echo "skip 64 Bytes of ${img_uramdisk} ..."
	dd if=${img_uramdisk} of=rootfs.cpio.gz skip=64 bs=1
	echo "skip 64 Bytes of ${img_uramdisk} ok"  

	# 解压gzip（得到cpio归档）
	echo "gunzip rootfs.cpio.gz ..."
	gunzip rootfs.cpio.gz
	echo "gunzip rootfs.cpio.gz ok"

	# 创建目录并提取cpio内容（保留权限）
	echo "execute rootfs.cpio --> ${dir_rootfs}/ ..."
	mkdir ${dir_rootfs} && cd ${dir_rootfs}
	cat ../rootfs.cpio | cpio -idm
	#cat ../rootfs.cpio | cpio -idmv 
	echo "execute rootfs.cpio --> ${dir_rootfs}/ ok"
}

function rootfs_to_uramdisk()
{
    # 创建cpio归档
    cd ${dir_rootfs}/
    #find . | cpio -H newc -o | gzip > ../${img_initrd}
    find . | cpio -H newc -o > ../rootfs.cpio
    
    # 压缩
    cd .. ; 
    gzip -9 rootfs.cpio
    
    # 取消挂载
    umount ${dir_rootfs}; rm -rf ${dir_rootfs}

    # 创建 uramdisk.image.gz
    mkimage -A arm64 -T ramdisk -C gzip -d rootfs.cpio.gz ${img_uramdisk}

    echo "close rootfs ok" 
    #echo "output: ${img_cpio}.gz"
    echo "output: ${img_uramdisk}"
}

function create_ext4_image()
{
    # 1. 创建镜像: 创建一个空白镜像文件
    # 假设需要45MB，创建一个比45MB大点的镜像，比如50MB的镜像（预留一些空间）
    dd if=/dev/zero of=${image_name} bs=1M count=${image_sizeMB}

    # 2. 格式化镜像: 为镜像文件创建文件系统
    ${image_mkfs} ${image_name}
}

function mount_ext4_image()
{
    # 3. 挂载镜像并复制 rootfs 内容
    mkdir -p ${dstdir_rootfs}
    mount -o loop ${image_name} ${dstdir_rootfs}
}

function copy_rootfs_to_image()
{
    # 复制rootfs目录内容到镜像中（保留权限和属性）
    echo "${image_name} copy ..."
    cp -arf ${srcdir_rootfs}/* ${dstdir_rootfs}

    # 同步数据（确保所有内容写入完成）
    sync
    echo "${image_name} copy OK" 
}

function umount_ext4_image()
{
    echo "${image_name} umount ..."
    umount ${dstdir_rootfs}
    rm -rf ${dstdir_rootfs}
    echo "${image_name} umount OK" 
}

# 脚本主流程：
################################################################################
if [[ $# -lt 1 ]];then
		echo "usage: sudo  bash  $0  <0|1>"
    echo " "
		echo "  e.g: sudo  bash  $0  0    --解包: uramdisk.image.gz --> rootfs/ 临时目录"
		echo "  e.g: sudo  bash  $0  1    --打包: rootfs/* --> rootfs.ext4"
		echo "  e.g: sudo  bash  $0  2    --打包: rootfs/* --> uramdisk.image.gz"
    echo " "
		exit 1
fi
pack_opt=$1

# 检查权限
if [ $UID -ne 0 ]; then echo "请用sudo执行该脚本";  exit 1; fi

if [[ ${pack_opt} -eq 0 ]];then
		uramdisk_to_rootfs;

    # 首先会在当前目录新建一个 rootfs 目录, 用来挂载 uramdisk.image.gz 镜像
    # 其次开始解包并把镜像挂载到 rootfs 目录，之后我们就可以修改 rootfs 里面的内容了

elif [[ ${pack_opt} -eq 1 ]];then

    # 新建ext4空白镜像
    create_ext4_image;

    # 挂载ext4镜像
    mount_ext4_image;

    # 把前面挂载的uramdisk内容复制到ext4镜像中
    copy_rootfs_to_image;

    # 取消挂载ext4镜像
    umount_ext4_image;

		clean_rootfs_dir;

    # 修改完 rootfs 里面的内容之后，执行该命令参数，
    # 该命令会把 rootfs 目录重新打包成 uramdisk.image.gz 镜像，并删除 rootfs 空目录。
elif [[ ${pack_opt} -eq 2 ]];then	
		rootfs_to_uramdisk;

    # 修改完 rootfs 里面的内容之后，执行该命令参数，
    # 该命令会把 rootfs 目录重新打包成 uramdisk.image.gz 镜像，并删除 rootfs 空目录。
fi
```

1、修改内核配置,把根文件系统编译到内核里: /home/whf/zynqmp/linux-xlnx-master/arch/arm64/configs/xilinx_zynqmp_zu48dr_defconfig

```cpp
CONFIG_BLK_DEV_INITRD=y
CONFIG_INITRAMFS_SOURCE=""
CONFIG_RD_GZIP=y
CONFIG_RD_BZIP2=y
CONFIG_RD_LZMA=y
CONFIG_RD_XZ=y
CONFIG_RD_LZO=y
CONFIG_RD_LZ4=y
CONFIG_RD_ZSTD=y
```

免登录，即无需输入用户名和密码，开机就自动进入命令行： 修改 uramdisk.image.gz 里面根目录下的 /etc/inittab 配置文件，内容如下:

```bash
# Put a getty on the serial port
#console::respawn:/sbin/getty -L  console 0 vt100 # GENERIC_SERIAL
#ttyS0::respawn:-/bin/sh
#tty0::respawn:-/bin/sh

#屏蔽上面的这些配置,使用下面这个配置即可达到免登录
console::respawn:-/bin/sh
```



