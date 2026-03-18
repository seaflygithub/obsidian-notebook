

## zynqmp-ramdisk-to-emmc

当时主要解决了在zu48dr平台上，需要把根文件系统挂在emmc里，即ramdisk切换到emmc根文件系统。因此有了该解决方案的记录。

附件: 网盘: zu48dr_emmc_rootfs_1.1.2.zip

经过验证的解决思路总结: 
（1）无需修改源代码，只需要修改rootfs里面的脚本或配置； 
（2）需要做两份rootfs镜像: uramdisk.image.gz、rootfs.ext4，一份给ramdisk，一份给emmc用； 
（3）当时用的Linux内核是6.12.0版本，因此内核会挂载并执行根目录下的 init 脚本，而更早的内核版本(比如 5.10.0)会挂载并执行根目录下的 linuxrc 程序，该文件是个软链接并直接指向 /bin/busybox 这个ELF程序。

下面是经过验证的思路：
![[Pasted image 20251222154016.png]]



---

**制作rootfs.ext4镜像.txt**

```bash
# 1. 创建镜像: 创建一个空白镜像文件
# 假设需要45MB，创建一个比45MB大点的镜像，比如64MB的镜像（预留一些空间）
dd if=/dev/zero of=rootfs.ext4 bs=1M count=64

# 2. 格式化镜像: 为镜像文件创建文件系统
mkfs.ext4  rootfs.ext4

# 3. 挂载镜像
mkdir -p  ext4dir
mount -o loop  rootfs.ext4  ext4dir

# 4. 拷贝文件系统内容到目标目录(rootfs/*是uramdisk挂载的内容)
cp -arf rootfs/*  ext4dir

# 5. 关闭挂载
umount  ext4dir ; rm -rf  ext4dir

# 6. 至此,rootfs.ext4镜像就制作完了
```

---

**挂载uramdisk镜像.txt**

```bash
挂载uramdisk镜像：

        # 跳过前64字节，输出为纯gzip压缩文件（无头部）
        dd  if=uramdisk.image.gz  of=rootfs.cpio.gz  skip=64  bs=1

        # 解压gzip（得到cpio归档）
        gunzip rootfs.cpio.gz

        # 创建目录并提取cpio内容（保留权限）(rootfs.cpio --> rootfs/ )
        mkdir rootfs && cd rootfs
        cat ../rootfs.cpio | cpio -idm

打包uramdisk镜像：

        # 创建cpio归档
        cd  rootfs
        find . | cpio -H newc -o > ../rootfs.cpio
        
        # 压缩
        cd .. ; gzip -9 rootfs.cpio
        
        # 取消挂载
        umount rootfs; rm -rf rootfs

        # 创建 uramdisk.image.gz
        mkimage -A arm64 -T ramdisk -C gzip -d rootfs.cpio.gz uramdisk.image.gz

        # 创建完毕
```

---

**init_origin（ramdisk根目录下的原始init文件）**

```bash
#!/bin/sh
# devtmpfs does not get automounted for initramfs
/bin/mount -t devtmpfs devtmpfs /dev

# use the /dev/console device node from devtmpfs if possible to not
# confuse glibc's ttyname_r().
# This may fail (E.G. booted with console=), and errors from exec will
# terminate the shell, so use a subshell for the test
if (exec 0</dev/console) 2>/dev/null; then
    exec 0</dev/console
    exec 1>/dev/console
    exec 2>/dev/console
fi

exec /sbin/init "$@"
```

---

**init_in_emmc（修改后用于emmc的init文件）**

```bash
#!/bin/sh

# 1. 挂载必要的虚拟文件系统
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev  # 挂载设备节点
mount -t tmpfs none /tmp     # 临时文件系统（可选）
echo "zu48dr: mounting basic virtual fs"

# devtmpfs does not get automounted for initramfs
# /bin/mount -t devtmpfs devtmpfs /dev

# use the /dev/console device node from devtmpfs if possible to not
# confuse glibc's ttyname_r().
# This may fail (E.G. booted with console=), and errors from exec will
# terminate the shell, so use a subshell for the test
if (exec 0</dev/console) 2>/dev/null; then
   exec 0</dev/console
   exec 1>/dev/console
   exec 2>/dev/console
fi

exec /sbin/init "$@"
```

---

**init_in_ramdisk（修改用于ramdisk的init文件，能够检测挂载emmc并跳转）**

```bash
#!/bin/sh

# 初始化根切换标志：默认需要切换（1=需要切换，0=无需切换）
need_change=1
# 超时时间设置（单位：秒）
TIMEOUT=10
# 倒计时计数器（初始为超时时间）
countdown=$TIMEOUT
# 目标根设备和挂载点
TARGET_DEV="/dev/mmcblk0p2"
TARGET_MOUNTPOINT="/"
TARGET_MOUNTED=0

# 1. 挂载必要的虚拟文件系统
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev  # 挂载设备节点
mount -t tmpfs none /tmp     # 临时文件系统（可选）
echo "zu48dr: mounting basic virtual fs"

# 2. 加载 eMMC 相关驱动（如果内核未内置，根据实际模块名调整）
# insmod /lib/modules/mmc_block.ko
# insmod /lib/modules/sdhci.ko

# 3. 带超时机制等待 /dev/mmcblk0p2 设备就绪
echo "zu48dr: Waiting for ${TARGET_DEV} (timeout: ${TIMEOUT}s)..."
while [ ! -b "${TARGET_DEV}" ]; do  # -b 检查是否为块设备节点
    # 倒计时减1
    countdown=$((countdown - 1))
    
    # 检查是否超时
    if [ $countdown -le 0 ]; then
        echo "Timeout! ${TARGET_DEV} not found in ${TIMEOUT}s."
        need_change=0  # 超时，设置为无需切换
        break
    fi
    
    # 未超时，等待0.5秒后重试（平衡响应速度和资源占用）
    sleep 0.5
done

# 若未超时且设备已就绪，打印成功信息
if [ $need_change -eq 1 ]; then
    echo "zu48dr: ${TARGET_DEV} is ready."
else
    echo "zu48dr: ${TARGET_DEV} is not ready."
fi

# 检查挂载点是否已挂载
echo "Checking if ${TARGET_DEV} is already mounted on ${TARGET_MOUNTPOINT}..."
if mountpoint -q "${TARGET_MOUNTPOINT}"; then
    # 确认挂载点的设备是否为目标设备
    mounted_dev=$(mount | grep " on ${TARGET_MOUNTPOINT} " | awk '{print $1}')
    if [ "$mounted_dev" = "$TARGET_DEV" ]; then
        echo "$TARGET_DEV is already mounted on ${TARGET_MOUNTPOINT}"
        need_switch=0  # 已正确挂载，无需切换
    else
        echo "${TARGET_MOUNTPOINT} is mounted by $mounted_dev (not $TARGET_DEV). Continue switching..."
    fi
else
    echo "${TARGET_MOUNTPOINT} is not mounted. Continue switching..."
fi

# 4. 根据 need_change 标志决定是否执行根切换
if [ $need_change -eq 1 ]; then
    # 4.1 挂载目标根分区到 /mnt（文件系统类型需与实际一致，如 ext4）
    echo "Mounting ${TARGET_DEV} to /mnt/newrootfs ..."
    mkdir -p /mnt/newrootfs
    mount -t ext4 -o rw ${TARGET_DEV} /mnt/newrootfs || {
        echo "Failed to mount ${TARGET_DEV}! Skip root switch."
        need_change=0  # 挂载失败，同样取消切换
    }
fi

# 5. 执行根切换（仅当 need_change=1 且挂载成功时）
if [ $need_change -eq 1 ]; then
    echo "Switching root to ${TARGET_DEV}..."

    mkdir -p /mnt/newrootfs/oldrootfs
    cd /mnt/newrootfs 
    pivot_root . oldrootfs
    exec chroot . /init < /dev/console > /dev/console 2>&1
    #exec chroot . sh < /dev/console > /dev/console 2>&1  //ok01,but not other dev resources
    need_change=1
    
    # 切换成功后，卸载旧根（初始 ramdisk）释放内存
    if [ $need_change -eq 1 ]; then
        umount /mnt/oldrootfs 2>/dev/null
        echo "Root switched to ${TARGET_DEV} successfully."
    fi
fi

# 6. 最终启动逻辑（根据 need_change 决定启动哪个 /init）
if [ $need_change -eq 1 ]; then
    # 切换成功：执行新根（/dev/mmcblk0p2）下的 /init
    echo "Starting new root's /init..."
    exec /init  # 此时的 /init 已属于 /dev/mmcblk0p2，PID 保持为 1
else
    if [ $]
    # 未切换/切换失败：使用初始 ramdisk 的急救 shell（或初始 init）
    echo "Entering emergency shell (using initial ramdisk)..."
    #exec sh  # 进入交互 shell，方便调试；若有初始 ramdisk 的 init，可替换为 exec /init.ramdisk
    exec /sbin/init "$@"
fi

# devtmpfs does not get automounted for initramfs
#####/bin/mount -t devtmpfs devtmpfs /dev

# use the /dev/console device node from devtmpfs if possible to not
# confuse glibc's ttyname_r().
# This may fail (E.G. booted with console=), and errors from exec will
# terminate the shell, so use a subshell for the test
####if (exec 0</dev/console) 2>/dev/null; then
####    exec 0</dev/console
####    exec 1>/dev/console
####    exec 2>/dev/console
####fi

####exec /sbin/init "$@"
```

---

**profile_origin（ramdisk原始的/etc/profile文件）**

```bash
export PATH="/bin:/sbin:/usr/bin:/usr/sbin"

if [ "$PS1" ]; then
	if [ "`id -u`" -eq 0 ]; then
		export PS1='# '
	else
		export PS1='$ '
	fi
fi

export EDITOR='/bin/vi'

# Source configuration files from /etc/profile.d
for i in /etc/profile.d/*.sh ; do
	if [ -r "$i" ]; then
		. $i
	fi
done
unset i

```

---

**profile_in_emmc（用于emmc根文件系统的/etc/profile）**

```bash
export PATH="/bin:/sbin:/usr/bin:/usr/sbin"

if [ "$PS1" ]; then
	if [ "`id -u`" -eq 0 ]; then
		# export PS1='# '

        # 设置命令行提示符（PS1）
        # 格式说明：
        # \\u: 用户名（默认root）
        # \\h: 主机名（可自定义）
        # \\w: 当前工作目录
        # \\$:  root用户显示#，普通用户显示$
        #export PS1='[root@zu48dr_linux \\w]# '
        #export PS1='[root@zu48dr_linux \\w]# '  # 示例：[root@zu48dr_linux /]#
        hostname zu48dr_linux
        export HOME=/root
        export PS1='[\\u@\\h \\w]\\$ '

	else
		export PS1='$ '
	fi
fi

export EDITOR='/bin/vi'

# Source configuration files from /etc/profile.d
for i in /etc/profile.d/*.sh ; do
	if [ -r "$i" ]; then
		. $i
	fi
done
unset i
```

---

**profile_in_ramdisk（用于ramdisk根文件系统的/etc/profile）** 对于 profile 文件，只修改了PS1命令行提示符，用来方便区分运行在ramdisk还是emmc。

```bash
export PATH="/bin:/sbin:/usr/bin:/usr/sbin"

if [ "$PS1" ]; then
	if [ "`id -u`" -eq 0 ]; then
		#export PS1='root@ramdisk# '

        # 设置命令行提示符（PS1）
        # 格式说明：
        # \\u: 用户名（默认root）
        # \\h: 主机名（可自定义）
        # \\w: 当前工作目录
        # \\$:  root用户显示#，普通用户显示$
        #export PS1='[root@zu48dr_ramdisk \\w]# '
        #export PS1='[root@zu48dr_ramdisk \\w]# '  # 示例：[root@zu48dr_ramdisk /]#
        hostname zu48dr_ramdisk
        export HOME=/root
        export PS1='[\\u@\\h \\w]\\$ '

	else
		#export PS1='user@ramdisk$ '
        hostname zu48dr_ramdisk
        export PS1='[\\u@\\h]\\$ '
	fi
fi

export EDITOR='/bin/vi'

# Source configuration files from /etc/profile.d
for i in /etc/profile.d/*.sh ; do
	if [ -r "$i" ]; then
		. $i
	fi
done
unset i

```

---

**uramdisk_to_rootfs.sh** 把 uramdisk.image.gz 解包并挂载到当前目录下的 rootfs 临时目录。

```bash
img_uramdisk="uramdisk.image.gz"
dir_rootfs="`pwd`/rootfs"

function check_root()
{
	if [[ $UID -ne 0 ]];then
		echo "Error: need root permission"
		exit 1
	fi
}

function umount_rootfs()
{
	umount ${dir_rootfs} 2>/dev/null
	rm -rf ${dir_rootfs} 2>/dev/null
}

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

# 脚本主流程：
################################################################################
if [[ $# -lt 1 ]];then
	echo "usage: sudo  bash  $0  <0|1>"
    echo " "
	echo "  e.g: sudo  bash  $0  0    --解包: uramdisk.image.gz --> rootfs/ 临时目录"
	echo "  e.g: sudo  bash  $0  1    --打包: rootfs/* --> uramdisk.image.gz"
    echo " "
	exit 1
fi
pack_opt=$1
check_root;

if [[ ${pack_opt} -eq 0 ]];then
	#umount_rootfs;
	uramdisk_to_rootfs;

    # 首先会在当前目录新建一个 rootfs 目录, 用来挂载 uramdisk.image.gz 镜像
    # 其次开始解包并把镜像挂载到 rootfs 目录，之后我们就可以修改 rootfs 里面的内容了

elif [[ ${pack_opt} -eq 1 ]];then	
	rootfs_to_uramdisk;

    # 修改完 rootfs 里面的内容之后，执行该命令参数，
    # 该命令会把 rootfs 目录重新打包成 uramdisk.image.gz 镜像，并删除 rootfs 空目录。
fi
```

---

**uramdisk_to_ext4.sh** 把 uramdisk 解包，并挂载到临时目录 rootfs，并把目录内容制作成 rootfs.ext4 镜像。

```bash
# 该脚本主要作用
# 就是把 uramdisk.image.gz 转换为 ext4 格式的镜像文件,方便在板子上执行挂载操作
img_uramdisk=uramdisk.image.gz
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
	echo "execute rootfs.cpio --> ${srcdir_rootfs}/ ..."
	mkdir ${srcdir_rootfs} && cd ${srcdir_rootfs}
	cat ../rootfs.cpio | cpio -idm
	#cat ../rootfs.cpio | cpio -idmv 
	echo "execute rootfs.cpio --> ${srcdir_rootfs}/ ok"
}

function clean_rootfs_dir()
{
    # 取消挂载
    #umount ${srcdir_rootfs};
    rm -rf ${srcdir_rootfs}
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
fi
```


## zynq-ramdisk-to-emmc

附件: 网盘: z7045_ramdisk_to_emmc_250827.zip

附件: 网盘: linux-xlnx-master-z7045-emmc-250827.zip


经过实际摸索调试，z7045没法在ramdisk跳转，各种问题；唯一办法，只能修改其内核，让其直接从 emmc 启动根文件系统；后来才知道，由于当时内核版本是 5.10.0，它会挂载并执行根目录下的 linurc 程序，该文件指向 /bin/busybox 这个ELF程序，因此无法修改其执行流程。通过修改 rcS 文件也是没法正确跳转，因此只能修改内核代码，直接从源头跳转到 emmc 根文件系统。

做了如下修改:

- 1、修改内核代码，让其适配当时的板子能够正确挂载emmc相关分区；
- 2、引导程序 u-boot 启动参数 bootargs 指定，要有 `root=/dev/mmcblk0p2 rw` 类似这样参数，否则默认从ramdisk启动。

修改的文件(linux-xlnx-master/init/do_mounts.c —— 5.10.0)：
- [[do_mounts.origin.c]]    (origin表示原文件)
- [[do_mounts.emmc.c]]   (emmc表示修改适配emmc的文件)
- [[2508271710-rootfs-emmc.log]]        （调试期间的日志信息）

```bash
# 查询分区的主设备号和次设备号
zynq-linux> ls -l /dev/mmcblk0*
brw-rw----    1 root     root      179,   0 Jan  1 00:00 /dev/mmcblk0
brw-rw----    1 root     root      179,   8 Jan  1 00:00 /dev/mmcblk0boot0
brw-rw----    1 root     root      179,  16 Jan  1 00:00 /dev/mmcblk0boot1
brw-rw----    1 root     root      179,   1 Jan  1 00:00 /dev/mmcblk0p1
brw-rw----    1 root     root      179,   2 Jan  1 00:00 /dev/mmcblk0p2
zynq-linux> 

内核代码分析相关的记录:
do_mounts.c  :: mount_root() 该函数根据 ROOT_DEV 的值来决定创建dev并挂载
do_mounts.c  :: prepare_namespace() 调用 mount_root() 的函数
do_mounts_initrd.c  :: initrd_load :: handle_initrd
```

当时现场调试记录常用命令:

```bash
# 如果想要从emmc挂载rootfs，bootargs至少要有mmc分区和读写这两个参数
# 如果不指定emmc挂载rootfs，则默认从ramdisk挂载rootfs
setenv bootargs 'root=/dev/mmcblk0p2 rw'
load mmc 0 0x1000000 uramdisk.z7045.rcS.image.gz
load mmc 0 0x1900000 uImage
bootm 0x1900000 0x1000000 0x1800000
```




## rootfs镜像处理脚本

- mount_rootfs_image.sh

```bash
img_uramdisk="uramdisk.image.gz"
dir_rootfs="`pwd`/rootfs"

function check_root()
{
        if [[ $UID -ne 0 ]];then
                echo "Error: need root permission"
                exit 1
        fi
}

function umount_rootfs()
{
        umount ${dir_rootfs} 2>/dev/null
        rm -rf ${dir_rootfs} 2>/dev/null
}

function uramdisk_to_rootfs()
{
        # 跳过前64字节，输出为纯gzip压缩文件（无头部）
        echo "skip 64 Bytes of ${img_uramdisk} ..."
        dd if=${img_uramdisk} of=rootfs.cpio.gz skip=1 bs=64
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

function rootfs_notice()
{
    echo "请另开一个命令行终端,并把你自定义文件拷贝到 ./rootfs 目录"
    echo "然后在此终端输入OK, 即可完成根文件系统的压缩与转换(to initrd format)"
    echo "拷贝完成后请输入: "
    read copy_ok
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

check_root;
umount_rootfs;
uramdisk_to_rootfs;
rootfs_notice;
rootfs_to_uramdisk;
```

下面是完整的脚本（rootfs_image.sh）

```bash
#!/bin/bash

SUDO=""
function check_root()
{
        if [[ $UID -ne 0 ]];then
                echo "Error: need root permission"
                exit 1
        fi
}

# function to convert uramdisk to ramdisk
# param: $1 - working directory
# param: $2 - uramdisk image file, such as "uramdisk.image.gz"
# param: $3 - mount directory
function uramdisk_to_mountdir()
{
    # set basic work directory
    dir_work="$1"
    
    # such as "uramdisk.image.gz"
    zip_uramdisk="$2"
    
    # mount directory, such as "rootfs" (will mount to ${dir_work})
    dir_mount="$3"
    
    # such as "ramdisk.image.gz" (no compression)
    zip_ramdisk=${zip_uramdisk:1}
    
    # such as "ramdisk.image"
    unzip_ramdisk="${zip_ramdisk%.*}"
    
    # mkdir
    mkdir -p ${dir_work}/${dir_mount}
    
    # total skip 64 bytes of u-boot header (block_size * skip_count)
    echo "${zip_uramdisk} ------> ${zip_ramdisk}"
    ${SUDO} dd if=${dir_work}/${zip_uramdisk} of=${dir_work}/${zip_ramdisk} skip=1 bs=64
    
    
    # decompress ramdisk.image.gz to ramdisk.image
    gunzip ${dir_work}/${zip_ramdisk}
    chmod u+rwx ${dir_work}/${unzip_ramdisk}
    echo "${zip_ramdisk} ------> ${unzip_ramdisk}"
    
    
    # mount image: different image types
    cpio -it < ${dir_work}/${unzip_ramdisk} >/dev/null 2>&1
    if [[ $? -ne 0 ]]; then
        echo "image type: not cpio"
        ${SUDO} mount -o loop ${dir_work}/${unzip_ramdisk} ${dir_work}/${dir_mount}
        echo "${unzip_ramdisk} ------> ${dir_mount}/"
    else
        echo "image type: cpio"
        cd ${dir_work}/${dir_mount}
        cat ../${unzip_ramdisk} | cpio -idm
        echo "${unzip_ramdisk} ------> ${dir_mount}/"
        cd ${dir_work}
    fi
}

# function to convert uramdisk to ramdisk
# param: $1 - working directory
# param: $2 - uramdisk image file, such as "uramdisk.image.gz"
# param: $3 - mount directory
# param: $4 - cpu arch, such as "arm", "arm64"
# param: $5 - image type, such as "cpio", or none
function mountdir_to_uramdisk()
{
    # set basic work directory
    dir_work="$1"
    
    # such as "uramdisk.image.gz"
    zip_uramdisk="$2"
    
    # mount directory, such as "rootfs" (will mount to ${dir_work})
    dir_mount="$3"
    
    # such as "arm"
    cpu_arch="$4"
    
    # image type, such as "cpio", or none
    img_type="$5"
    
    # such as "ramdisk.image.gz" (no compression)
    zip_ramdisk=${zip_uramdisk:1}
    
    # such as "ramdisk.image"
    unzip_ramdisk="${zip_ramdisk%.*}"
    
    
    # umount
    if [[ "${img_type}" != "cpio" ]]; then
        ${SUDO} umount ${dir_work}/${dir_mount}
        rm -rf ${dir_work}/${dir_mount}
    else
        echo "image type: cpio"
        cd ${dir_work}/${dir_mount}/
        
        #find . | cpio -H newc -o | gzip > ../${img_initrd}
        find . | cpio -H newc -o > ../${unzip_ramdisk}
        cd ..
        
        rm -rf ${dir_work}/${dir_mount}
    fi
    
    ${SUDO} gzip ${dir_work}/${unzip_ramdisk}
    echo "${dir_mount} ------> ${zip_ramdisk}"
    
    # check if mkimage is available
    which mkimage 1>/dev/null 2>&1
    if [ $? -ne 0 ]; then
        ${SUDO} apt-get install -y u-boot-tools
        if [ $? -ne 0 ]; then
            echo "Failed to install u-boot-tools for mkimage"
            exit 1
        fi
    fi
    
    ${SUDO} mkimage -A ${cpu_arch} -T ramdisk -C gzip \
    -d ${dir_work}/${zip_ramdisk} ${dir_work}/${zip_uramdisk}
    echo "${zip_ramdisk} ------> ${zip_uramdisk}"
}

# function to create ext4/ext3/ext2 image
# param: $1 - image_mkfs, such as mkfs.ext4
# param: $2 - image name, such as "rootfs.ext4"
# param: $3 - image size in MB, such as 64
function create_ext4_image()
{
    image_mkfs="$1"
    image_name="$2"
    image_sizeMB="$3"
    
    # 1. create new blank image
    # set >45MB if your real image size is less than 45MB
    dd if=/dev/zero of=${image_name} bs=1M count=${image_sizeMB}
    
    # 2. format image
    ${image_mkfs} ${image_name}
}

# function to mount ext4/ext3/ext2 image
# param: $1 - image name, such as "rootfs.ext4"
function mount_ext4_image()
{
    dstdir_rootfs="blank_rootfs"
    
    # 3. mount image and copy rootfs content
    mkdir -p ${dstdir_rootfs}
    ${SUDO} mount -o loop ${image_name} ${dstdir_rootfs}
    echo "${image_name} ------> ${dstdir_rootfs}/ mount OK"
}

function umount_ext4_image()
{
    dstdir_rootfs="blank_rootfs"
    echo "${image_name} umount ..."
    ${SUDO} umount ${dstdir_rootfs}
    rm -rf ${dstdir_rootfs}
    echo "${image_name} umount OK"
}

# usage: bash rootfs_image.sh args
check_root;
$@

# following is args:
#   uramdisk_to_mountdir `pwd` "uramdisk.image.gz" "rootfs"
#   mountdir_to_uramdisk `pwd` "uramdisk.image.gz" "rootfs" "arm"
#   mountdir_to_uramdisk `pwd` "uramdisk.image.gz" "rootfs" "arm" "cpio"
#   mountdir_to_uramdisk `pwd` "uramdisk.image.gz" "rootfs" "arm64"

#   create_ext4_image mkfs.ext4 rootfs.ext4 64
#   mount_ext4_image rootfs.ext4
#   umount_ext4_image
```





