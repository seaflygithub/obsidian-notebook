
# VMware共享文件夹

**共享文件夹不显示的问题**

- 虚拟机内共享文件夹没有自动挂载问题，执行下面脚本进行手动挂载显示:

```bash
#Ubuntu终端中运行命令行:
vmware-hgfsclient

if [ ! -e /mnt/hgfs ];then sudo mkdir -p /mnt/hgfs; fi

#查看开启的共享文件夹:
sudo vmhgfs-fuse .host:/ /mnt/hgfs  -o nonempty -o allow_other
```




# docker-qemu-stm32

VMware 16 Pro + Ubuntu 20.04 LTS + Docker + ubuntu 20.04 + qemu

qemu-arm-stm32系列: [[qemu_stm32]]

[[stm32_p103_demos]]

**安装虚拟机**

安装 VMware虚拟机Linux，这里用的 ubuntu 20.04 LTS，用户名是linux，密码和用户名一样。

**安装docker工具**

```bash
sudo apt-get install -y docker.io docker
```

后续docker命令操作需要管理员权限(sudo)

**编写 Dockerfile（定制 QEMU 编译环境）**

创建 Dockerfile 文件，基于 Ubuntu 20.04 镜像构建 QEMU 编译环境：

```bash
# 基础镜像（与主机系统一致，减少兼容性问题）
FROM ubuntu:20.04

# 设置非交互式安装（避免apt弹窗）
ENV DEBIAN_FRONTEND=noninteractive

# 把构建上下文路径下的国内源拷贝覆盖到指定目录
COPY ./sources.list /etc/apt/sources.list

# 安装QEMU编译依赖
RUN apt update
RUN apt install -y \\
    git \\
    python2.7 \\
    build-essential \\
    libtool \\
    zlib1g-dev \\
    libglib2.0-dev \\
    libpixman-1-dev \\
    libfdt-dev \\
    pkg-config \\
    libssl-dev \\
    libseccomp-dev \\
    autoconf \\
    automake \\
    && rm -rf /var/lib/apt/lists/*

# 克隆QEMU源码（可指定分支/版本，如支持STM32的分支）
#RUN git clone --depth=1 --branch=master <URL> <localDir>
RUN git clone <https://gitee.com/SeaflyGitee/qemu_stm32> /qemu-src

# 编译安装QEMU（配置支持ARM/STM32，启用调试）
#--enable-debug \\              # 启用调试功能（方便gdb调试）
#--enable-slirp \\              # 启用用户模式网络
#--prefix=/qemu-install        # 安装路径
WORKDIR /qemu-src
RUN ./configure --enable-debug --disable-xen --disable-werror \\
    --target-list="arm-softmmu" --python=/usr/bin/python2.7 \\
    --enable-debug \\
    --prefix=/qemu-install
RUN make -j$(nproc) && make install

# 设置环境变量（让容器内可直接调用qemu-system-arm）
ENV PATH=/qemu-install/bin:$PATH

# 工作目录（挂载主机的单片机程序源码）
WORKDIR /workspace

# 可选：默认命令
CMD ["/bin/bash"]
```

下面是使用国内 apt 源的参考Dockerfile:

```bash
# 基础镜像（与主机系统一致，减少兼容性问题）
FROM ubuntu:20.04

# 设置非交互式安装（避免apt弹窗）
ENV DEBIAN_FRONTEND=noninteractive

# docker容器内替换国内源之前,
# 核心修复步骤：安装CA证书 + 更新证书库,apt clean清理缓存（减小镜像体积）
RUN apt-get update --allow-insecure-repositories
RUN apt-get install -y --no-install-recommends ca-certificates
RUN update-ca-certificates
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# 把构建上下文路径下的国内源拷贝覆盖到指定目录
COPY ./sources.list /etc/apt/sources.list

RUN apt update
RUN apt-get install -y tree

WORKDIR /workdir

# 可选：默认命令
CMD ["/bin/bash"]
```

**设置 Docker 国内镜像源**

```bash
# 创建配置文件
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<EOF
{
    "registry-mirrors": [
        "https://docker.m.daocloud.io",
        "https://mirror.ccs.tencentyun.com",
        "https://docker.xuanyuan.me"
    ]
}
EOF

# 重启docker服务
sudo systemctl daemon-reload
sudo systemctl restart docker
```

**构建 Docker 镜像**

```bash
# 自动载入当前目录Dockerfile,构建目标镜像,最后的.表示构建的上下文路径
sudo docker build -t qemu-stm32:latest .

# 构建完成,查看本地镜像列表
sudo docker image ls

# 删除无用镜像（如悬空镜像）
docker image prune
```

**运行容器并挂载主机目录**

将主机的单片机程序目录（如`~/stm32-projects`）挂载到容器的`/workspace`，方便调试：

```bash
# -it 表示交互式
# -v <hostDir>:<dockerDir>
# --network bridge  默认就是桥接模式,该option可省略
# --rm  表示参数容器一旦退出（无论正常退出还是异常退出），会直接删除这个容器实例
docker run -it --rm  -v /home/linux/workdir:/workdir \\
    --name qemu-container \\
    --network bridge \\
    qemu-stm32:latest /bin/bash
    
# 由于 --rm 参数, 如果你在运行容器后,在容器中修改了新配置,你想永久保存配置,
# 则需要在主机系统上再开一个终端, 使用 docker commit 命令进行提交变更到指定镜像
# 详情见下面相关位置
```

**添加网络转发**：若需容器内 QEMU 访问主机网络，可添加`--network host`参数（或配置端口映射）。

```bash
# 桥接模式
docker run --network bridge
```

**安装交叉编译工具链**：若容器内需编译 STM32 固件，可在 Dockerfile 中添加 ARM 交叉编译工具链（如`gcc-arm-none-eabi`）：

```bash
RUN apt install -y gcc-arm-none-eabi
```

镜像保存成本地镜像文件，方便后续直接使用：

```bash
# 保存单个镜像
docker save -o <保存的文件名.tar> <镜像1>

# 保存多个镜像
docker save -o <保存的文件名.tar> <镜像1> <镜像2>

# 加载镜像
docker load -i ubuntu_20.04.tar

# 保存并压缩
docker save ubuntu:20.04 | gzip > ubuntu_20.04.tar.gz
# 解压并加载
gunzip -c ubuntu_20.04.tar.gz | docker load

# 查看镜像列表
root@vm:/home/linux/work/docker# ls
Dockerfile  sources.list
root@vm:/home/linux/work/docker# docker image ls
REPOSITORY   TAG       IMAGE ID       CREATED        SIZE
qemu-stm32   latest    155fb8788ebe   21 hours ago   2.95GB
<none>       <none>    daf679fc542c   21 hours ago   886MB
ubuntu       20.04     b7bab04fd9aa   7 months ago   72.8MB
root@vm:/home/linux/work/docker# 
```

保存容器镜像里的改动，比如在镜像系统里添加了新的配置文件等。

```bash
# 前面docker run之后,另开一个终端命令
# 查看容器信息,前面我们执行 docker run 时指定了name为 qemu-container
docker ps -a

# 接下来提交变更就需要容器id或者容器名称
# docker commit -m "desc string" <容器id> <新镜像名称>[:TAG信息]
# 将容器提交为新镜像（qemu-stm32:v1）
docker commit -m "add txtfile" --author "YourName"  qemu-container qemu-stm32:v1

# 验证：启动新镜像，文件已永久存在
docker run -it qemu-stm32:v1
```








# docker-qemu-8.2.0

qemu源码包直接下载地址: [[download.qemu.org]]



1、虚拟环境层级关系:

```bash
VMware + Ubuntu 20.04 LTS
       + Docker + qemu-8.2.0 
       + arm/aarch64/riscv/riscv64
```

2、下面是已经配置好的虚拟环境，方便直接部署使用。

```bash
root@vm:/home/linux/workdir/docker# ls -hl
total 711M
-rw-r--r--  root     531 12月  15:41 build-qemu-8.2.0.sh
-rw-r--r--  root    2.9K 12月  15:54 Dockerfile.qemu-8.2.0
-rw-r--r--  root    561M 12月  16:24 docker-image-ubuntu-qemu-8.2.0.tar.bz2
-rwxrwxrwx  linux   150M 12月  15:13 qemu-8.2.0.tar.bz2
-rw-rw-r--  linux    450 11月  16:30 sources.list
root@vm:/home/linux/workdir/docker#
```

**docker-image-ubuntu-qemu-8.2.0.tar.bz2**: 这个是已经构建好的镜像，里面带有默认的qemu-8.2.0的命令行工具。当然你也可以不用这个文件自己重新构建，这里是为了考虑网络问题，所以建议直接使用构建好的镜像。

**Dockerfile.qemu-8.2.0**: 这是构建镜像的配置文件，构建方法在该文件内容底部。在镜像构建之初会使用 sources.list 作为国内源，以加快相关依赖安装的速度。

**qemu-8.2.0.tar.bz2**: 这个是从官方下载的源码包(不是从github下载)，为了方便我们在后续调试过程中，如果需要修改 qemu 配置或者源代码，可以方便修改，并在容器内重新编译生成相关的工具。其中 [[build-qemu-8.2.0.sh]] 这个脚本就是在容器内编译qemu源码时需要用到，里面包含了qemu的核心配置和编译，方便自动化编译和安装qemu工具。

下面是从零构建8.2.0镜像的完整流程:

**1、构建镜像**

```bash
docker build -t ubuntu-qemu:8.2.0 . -f Dockerfile.qemu-8.2.0
```

**2、运行容器**

```bash
docker run -it --rm -v /home/linux/workdir:/workdir \\
				--name ubuntu-qemu ubuntu-qemu:8.2.0 /bin/bash
```

**3、容器内编译qemu源代码**

```bash
cd  /workdir/docker
bash  build-qemu-8.2.0.sh
```

**4、提交容器变更**

```bash
docker commit -m "install qemu-8.2.0" qemu-zynq qemu-zynq:8.2.0
```

**5、保存镜像到文件**

```bash
# 查看容器进程
docker ps

# 提交容器更改
docker commit 容器ID或名称 新镜像名:标签

# 保存到文件
docker save -o docker-image-ubuntu-qemu-8.2.0.tar ubuntu-qemu:8.2.0

# 压缩文件
tar -cjf docker-image-ubuntu-qemu-8.2.0.tar.bz2 docker-image-ubuntu-qemu-8.2.0.tar

# 解压文件
tar -xjf docker-image-ubuntu-qemu-8.2.0.tar.bz2

# 加载镜像文件
docker load -i docker-image-ubuntu-qemu-8.2.0.tar
```



# docker-qemu-8.2.0-kernel


百度网盘目录: docker-qemu-8.2.0-kernel

build-qemu-8.2.0.sh

<font color=blue>上面脚本是在 docker 中执行，也就是编译环境在 docker 中，编译的 qemu 版本是官方下载的源码包 qemu-8.2.0.tar.bz2，我后续需要用到这个版本的 qemu 运行调试 Linux 内核 4.x 5.x 6.x 的，尤其是架构级的实验调试。上面的 configure 还需要补充什么吗？如果有补充，给我一个补充好的完整脚本内容。
</font>

**1️⃣ 调试能力不完整**

上面脚本只开了 --enable-debug
缺少真正关键的：
- gdb stub 友好性
- trace / log / plugin 深度支持


**2️⃣ 图形 & 交互调试缺失**

你内核调试看 early boot / framebuffer / panic 图像 → 很有用

**3️⃣ 性能 & profiling 工具缺失**

你没开：
- perf 支持
- fdt（设备树）
- capstone（反汇编）
👉 做架构实验，这些非常关键

**4️⃣ KVM / 加速缺失**（⚠️ 很重要）

你现在只有：--enable-tcg，但没有：--enable-kvm
如果你在 x86 主机跑 x86 内核：👉 没 KVM = 慢 10~50 倍


**5️⃣ 网络/文件系统调试能力不完整**

你开了 slirp（用户态网络），但建议补：
- virtfs（9p共享）
- vhost-net（性能网络）

---

```txt
--enable-debug-info    gdb 看 QEMU 内部结构
trace                  跟踪设备/中断/调度
capstone               反汇编（分析异常/指令）
--enable-plugins       可以做:指令统计、cache 行为分析、syscall tracing
--enable-virtfs        允许你: -virtfs local,path=host_dir,mount_tag=host0,security_model=passthrough
                       在 guest 里: mount -t 9p -o trans=virtio host0 /mnt
                       比 scp 快 100 倍（调试神器）

--enable-kvm           KVM跑真实内核（高性能），TCG跨架构实验
--enable-fdt           设备树，ARM / RISC-V 必备
```

✅ Docker编译环境补齐依赖

```bash
apt install -y libsdl2-2.0-0 libsdl2-dev
apt install -y libcapstone3
apt install -y libcapstone-dev
apt install -y libglib2.0-0
apt install -y libpixman-1-0
apt install -y libgtk-3-0
apt install -y libgtk-3-dev
apt install -y libfdt1
apt install -y libslirp0
```


✅ **Docker 版本 ≤ 宿主机版本**

✅ **宿主机补齐依赖**

```bash
apt install -y libsdl2-2.0-0 libsdl2-dev
apt install -y libcapstone3
apt install -y libcapstone-dev
apt install -y libglib2.0-0
apt install -y libpixman-1-0
apt install -y libgtk-3-0
apt install -y libgtk-3-dev
apt install -y libfdt1
apt install -y libslirp0
```

**✅ 调试用法**

```bash
qemu-system-x86_64 \
    -kernel bzImage \
    -append "root=/dev/sda console=ttyS0" \
    -nographic \
    -s -S
```

然后：
```bash
gdb vmlinux
(gdb) target remote :1234
```


docker运行容器后，终端命令默认所在目录



# qemu-网络tap

下面是基于 qemu-8.2.0 的版本下的配置流程.

**1、安装工具**: 先安装网桥和 TAP 设备管理工具，以 Debian/Ubuntu 为例：

```bash
# bridge-utils用于网桥，uml-utilities用于TAP设备
apt-get install bridge-utils uml-utilities  
```

**2、配置宿主机网桥**

假设宿主机上网网卡为 enp0s3, （可通过 ip addr 查看），创建并配置网桥 br0：

```bash
# 1. 关闭宿主机上网网卡
sudo ifconfig enp0s3 down
# 2. 创建网桥br0
sudo brctl addbr br0
# 3. 将物理网卡添加到网桥
sudo brctl addif br0 enp0s3
# 4. 关闭生成树协议（单网桥场景无需）
sudo brctl stp br0 off
# 5. 启用网桥和物理网卡，并设置为混杂模式
sudo ifconfig br0 0.0.0.0 promisc up
sudo ifconfig enp0s3 0.0.0.0 promisc up
# 6. 为网桥获取IP（通过DHCP，静态IP可手动配置）
sudo dhclient br0
# 7. 查看网桥状态，确认enp0s3已加入
sudo brctl show br0
```

**3、创建并配置TAP设备**

创建 TAP 设备并关联到网桥，作为虚拟机与网桥的连接口：

```bash
# 1. 创建TAP设备tap0，仅允许root访问
sudo tunctl -t tap0 -u root
# 2. 将tap0添加到网桥br0
sudo brctl addif br0 tap0
# 3. 启用tap0设备
sudo ifconfig tap0 0.0.0.0 promisc up
```

4、**启动QEMU并关联TAP设备**

启动虚拟机时指定 TAP 设备，以 ARM 架构镜像为例（适配你之前关注的 STM32 相关场景，其他架构替换对应`qemu-system-xxx`命令即可）：

```bash
sudo qemu-system-arm -M stm32vldiscovery -kernel zImage -dtb stm32.dtb \\
-netdev tap,id=net0,ifname=tap0,script=no,downscript=no \\
-device virtio-net-pci,netdev=net0
```

其中参数含义：

- `netdev tap,...`：定义 TAP 类型的网络后端，指定设备名为 tap0，禁用自动脚本；
- `device virtio-net-pci,netdev=net0`：为虚拟机添加 virtio 网卡，并关联到上述网络后端。

**5、验证网络**

虚拟机启动后，手动配置与宿主机同网段的 IP（或通过 DHCP 获取），执行`ping www.baidu.com`，若正常通信则配置成功。






