

# Windows 安装 RustDesk 客户端


直接下载安装包安装使用: https://github.com/rustdesk/rustdesk/releases

RustDesk无需登录，无需充值会员，
RustDesk客户端首先尝试建立直接 P2P 连接，如果 P2P 失败，将使用官方中继服务器。

基本上，默认的客户端就能满足大部分使用场景，
如果你要使用自己的中继服务器，还可以自定义中继服务，继续见后续小节。


# 部署自定义中继服务器


参考文章: 
超详细的 RustDesk 自建中继节点教程
https://blog.csdn.net/weixin_53510183/article/details/143257158


**RustDesk服务架构**

![[Pasted image 20260311174930.png]]


官方仓库地址: https://github.com/rustdesk/rustdesk-server

RustDesk 提供了多种部署方式，您可以根据自己的需求和技术水平选择合适的方式，主要有以下三种方式：
- 1、**使用 Docker / Docker Compose 部署（推荐，选其一）：** 这是最简单、最快速的部署方式，适合大多数用户。您只需要运行几条 Docker 命令，即可完成 RustDesk 中转服务器的安装和配置。
- 2、**使用二进制文件运行：** 下载预编译的二进制文件，解压后即可运行，无需编译安装，适合快速部署和测试。


下面将讲解几个常用部署流程：

---


## 使用Docker部署


**准备工作**

1、一台拥有公网 IP 的 Linux 服务器，例如腾讯云、阿里云等。

2、服务器已开启必要的端口：你可以通过服务器管理面板的安全组或防火墙配置中放行这些端口。
- TCP: 21115, 21116, 21117, 21118, 21119
- UDP: 21116

3、安装 Docker

检查是否安装完毕,如果有正确输出版本 ，那么就代表安装成功了。
```bash
root@ubuntu:~# docker -v
Docker version 27.1.1, build 6312585
```

4、拉取并运行容器
```bash
mkdir -p ~/rustdesk
cd ~/rustdesk
sudo docker image pull rustdesk/rustdesk-server
sudo docker run --name hbbs -p 21115:21115 -p 21116:21116 -p 21116:21116/udp -p 21118:21118 -v ./data:/root -td --net=host rustdesk/rustdesk-server hbbs
sudo docker run --name hbbr -p 21117:21117 -p 21119:21119 -v ./data:/root -td --net=host rustdesk/rustdesk-server hbbr



# 国内镜像网址,可以去该网址拿到自己想要的镜像地址
https://docker.aityp.com/r/docker.io/rustdesk/rustdesk-server
# 拉取国内镜像
sudo docker image pull swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/rustdesk/rustdesk-server
# 运行容器
sudo docker run --name hbbs -v ./data:/root -td --net=host swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/rustdesk/rustdesk-server hbbs
sudo docker run --name hbbr -v ./data:/root -td --net=host swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/rustdesk/rustdesk-server hbbr




# 检查容器运行状态,状态为 Up 表示正常
root@ubuntu:~/rustdesk# docker ps -a
CONTAINER ID   IMAGE                      COMMAND   CREATED          STATUS          PORTS     NAMES
97e8dfc8939e   rustdesk/rustdesk-server   "hbbr"    44 seconds ago   Up 43 seconds             hbbr
64e629c8a41d   rustdesk/rustdesk-server   "hbbs"    49 seconds ago   Up 48 seconds             hbbs
```


运行好后，可以在当前目录下列出文件：其中 id_ed25519.pub 文件内容接下来会使用到。
```bash
root@ubuntu:~/rustdesk# ls -l data
total 132
-rw-r--r-- 1 root root  4096 Oct 26 15:25 db_v2.sqlite3
-rw-r--r-- 1 root root 32768 Oct 26 15:25 db_v2.sqlite3-shm
-rw-r--r-- 1 root root 82432 Oct 26 15:25 db_v2.sqlite3-wal
-rw-r--r-- 1 root root    88 Oct 26 15:25 id_ed25519
-rw-r--r-- 1 root root    44 Oct 26 15:25 id_ed25519.pub
```



## 使用Docker Compose 部署


**也可以尝试使用Docker Compose 部署(可选)**


**1、建立 compose 配置**

```bash
# 新建工作目录
mkdir -p ~/rustdesk
cd ~/rustdesk
vim docker-compose.yaml
```


将以下内容复制粘贴进去：
```yml
networks:
  rustdesk-net:
    external: false

services:
  hbbs:
    container_name: hbbs
    ports:
      - 21115:21115
      - 21116:21116
      - 21116:21116/udp
    image: rustdesk/rustdesk-server
    command: hbbs
    volumes:
      - ./data:/root # 自定义挂载目录
    networks:
      - rustdesk-net
    depends_on:
      - hbbr
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 64M

  hbbr:
    container_name: hbbr
    ports:
      - 21117:21117
    image: rustdesk/rustdesk-server
    command: hbbr
    volumes:
      - ./data:/root # 自定义挂载目录
    networks:
      - rustdesk-net
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 64M
```


**2、运行 compose 配置**

```bash
docker compose up -d
```

之后同样控制台看 STATUS 是否为 Up：
```bash
root@ubuntu:~/rustdesk# docker ps -a
CONTAINER ID   IMAGE                      COMMAND   CREATED          STATUS          PORTS     NAMES
97e8dfc8939e   rustdesk/rustdesk-server   "hbbr"    44 seconds ago   Up 43 seconds             hbbr
64e629c8a41d   rustdesk/rustdesk-server   "hbbs"    49 seconds ago   Up 48 seconds             hbbs
```


运行好后，也可以在当前目录下列出文件: 其中 id_ed25519.pub 文件内容接下来会使用到。
```bash
root@ubuntu:~/rustdesk# ls -l data
total 132
-rw-r--r-- 1 root root  4096 Oct 26 15:25 db_v2.sqlite3
-rw-r--r-- 1 root root 32768 Oct 26 15:25 db_v2.sqlite3-shm
-rw-r--r-- 1 root root 82432 Oct 26 15:25 db_v2.sqlite3-wal
-rw-r--r-- 1 root root    88 Oct 26 15:25 id_ed25519
-rw-r--r-- 1 root root    44 Oct 26 15:25 id_ed25519.pub
```



# 客户端连入自定义中继服务器


1、以Windows为例，在前面最开始的章节，把安装包下载下来安装并打开软件。

![[Pasted image 20260311180100.png]]

![[Pasted image 20260311180249.png]]



2、如下图所示，以下是四个输入框的配置说明，具体配置可能会有所不同，取决于你的最初的设置，如果你使用docker方式时，更改了外部映射的端口，可以根据如下默认端口，填写对应的外部端口。


![[Pasted image 20260319175000.png]]


**ID 服务器（hbbs）**：默认端口：**21116**

**中继服务器（hbbr）**：默认端口：**21117**

**API 服务器**：默认端口：**21118**

**Key**：
- 上面提到的 `id_ed25519.pub` 文件的内容
- 使用 `cat id_ed25519.pub` 命令查看 Key


```bash
# 具体根据你该文件的目录来
cd ~/rustdesk/data/
cat id_ed25519.pub

# 我的输出
Ia42DxVS6hZ07cybqftPxAKXvszpbuj77aM=
```

如果是默认rustdesk官方推荐的端口，那么仅仅需要填写你的服务器 IP 到 ID 服务器 输入框即可。

最后点击**应用**即可。

特别需要注意的是，**你需要在每一个客户端都这样设置好中继服务器**。



**3、启动服务**

![[Pasted image 20260311180638.png]]

然后 返回主页查看底部状态，如果是绿色圆圈，并且是 就绪两字，就表示成功了 。
![[Pasted image 20260311180829.png]]


被控端也同样设置好后，就可以看到 ID 和 密码了，将其给到控制端输入就可以了，跟向日葵和Todesk一样的操作。



# Ubuntu 安装 RustDesk 客户端


Ubuntu 环境： Ubuntu 20.04 LTS

## 安装运行客户端

```bash
# 安装必要依赖
sudo apt install libgtk-3-0 libxdo3

# 安装安装包:
sudo apt-get install ./rustdesk-1.4.6-x86_64.deb
```


## 设置开机启动


参考文章：
在Ubuntu Desktop操作系统下，rustdesk客户端如何设置成开机自动启动？
https://blog.csdn.net/u011732210/article/details/154242618


**使用 systemd 服务设置开机启动**


```bash
# 创建用户服务目录
mkdir -p ~/.config/systemd/user

# 创建服务文件
vim ~/.config/systemd/user/rustdesk.service
```

在文件中粘贴以下内容：
```bash
[Unit]
Description=RustDesk Remote Desktop Client
After=graphical-session.target

[Service]
Type=simple
ExecStartPre=/bin/sleep 10
ExecStart=/usr/bin/rustdesk --service
Restart=on-failure

[Install]
WantedBy=graphical-session.target
```


重新加载 systemd 配置：
```bash
systemctl --user daemon-reload

# 启用开机启动：
systemctl --user enable rustdesk.service

# 启动服务以测试：
systemctl --user start rustdesk.service

# 检查服务是否运行：
systemctl --user status rustdesk.service
```






















