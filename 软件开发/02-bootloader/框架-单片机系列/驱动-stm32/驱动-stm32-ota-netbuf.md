
**netbuf的解释**: 为了尽量不干扰单片机原本程序，也就是降低耦合，这里的ota输入只需要特定的netbuf网络包，即可触发ota相关的功能执行。

## 软件设计

网盘: stm32_ota网络更新详细工程包归档V250705.zip

1、需求定版(外界主动请求更新单片机固件、支持版本回退)；

2、确定ROM分区(分哪几个区以及各个区的功能)；

3、从使用者角度去设计软件执行流程，目标就是尽量让使用者能够简单上手。

工程1: stm32_ota_bootloader（上电总是首先运行） 工程2: stm32_ota_app_recver（单片机固件程序，包含业务代码，以及作为新固件接收端） 工程3: stm32_ota_bootloader\OTA\sender（上位机代码，新固件的发送端）

硬件信息：stm32f103zet6，Flash大小为512KB，内存大小为 64KB 的SRAM。

![[Pasted image 20251222174538.png]]

- 引导区: 板子上电总是优先运行该区代码(ota_bootloader)；
- 运行区: 引导区代码执行完后, 会固定跳转到该区运行(ota_app)；
- 更新区: 单片机只负责把新固件存放到该区，由引导程序搬运到运行区；
- 恢复区: 当触发更新行为时, 由引导程序把上一个版本备份到该区；
- 状态区: 记录前面每个区的相关状态信息。


**分区大小**: 为了简化实现, 各个分区的大小通过宏定义来设置一个固定大小, 目标镜像.bin文件只要不超过这个大小即可。

**首次固化**: 作为使用者，首次固化需要借助J-Link等烧写器烧写程序，先烧写 ota_bootloader 程序，然后烧写 ota_app 程序，最后板子重新上电，其中 ota_app 程序就是除了单片机自己的业务代码，还有检测并更新固件的ota相关的调用代码。之后就可以通过网络更新 ota_app 固件了，而 ota_bootloader 就无需再更新了。

![[Pasted image 20251222174603.png]]

![[Pasted image 20251222174614.png]]

netbuf构成，以方便识别出特定的更新网络包和解析出固件数据:

```cpp
/*
netbuf[1024], netbuf 构成:
    帧头(4字节) + 数据长度(2字节) + 数据内容 + 校验码(4字节) + 帧尾(4字节)

    校验码只校验: 帧头 + 数据长度 + 数据内容

    帧头: 0xAABBCCDD, 帧尾: 0xDDCCBBAA

**/
#define OTA_NETBUF_FRAMEHEAD 0xAABBCCDD
#define OTA_NETBUF_FRAMETAIL 0xDDCCBBAA
```

帧头帧尾的作用是用来作为识别依据的；校验码的作用是确保收到的每个 netbuf 都是有效的。


---

下面是效果图:
![[Pasted image 20251222174812.png]]


## 首次烧写

下面是首次烧写运行ota_bootloader，根据Flash中是否存有匹配的魔数来确定:
![[Pasted image 20251222174836.png]]


前面烧写完引导程序后，接下来就是烧写 ota_app 程序了：
![[Pasted image 20251222174905.png]]



## 网络更新(ota_app)

发送端上位机例程: stm32_ota_bootloader\OTA\sender

一般用户要更新的单片机程序就是这个, 因此这里提供更新的操作方法.

- （1）确保和单片机网络连接畅通； 
- （2）把你要更新的单片机.bin文件,和发送小程序(tcp_sendfile.exe)放在同一个目录; 
- （3）双击运行小程序的调用脚本即可进行更新,脚本代码如下截图所示.

![[Pasted image 20251222174942.png]]


sender小程序位置: stm32_ota_bootloader\OTA\sender\tcp_sendfile.zip\Release\tcp_sendfile.exe

通过网络更新完后，会自动复位运行新的单片机程序，下图框框部分就是新版单片机程序的版本号信息。

![[Pasted image 20251222175004.png]]


## 网络更新(ota_bootloader)


一般 ota_bootloader 的更新频次特别低, 但这里也提供更新的途径.

- （1）确保和单片机网络连接畅通； 
- （2）把你要更新的bootloader程序的.bin文件,和发送端小程序(tcp_sendfile.exe)放在同一个目录下； 
- （3）双击运行小程序的调用脚本即可,脚本代码如下截图所示.

![[Pasted image 20251222175054.png]]

通过网络更新的引导程序，也会存放在更新区，以及恢复区，而这些区都只给 ota_app 用，

因此 ota_bootloader 会检测自身是否被更新，并自动把这些分区格式化，以防止运行区被误存放 ota_bootloader 程序。

![[Pasted image 20251222175111.png]]

## 接口清单

把常规的单片机程序改造成 ota_app 程序，要调用的接口也仅仅只有下图这几个。

![[Pasted image 20251222175130.png]]


## 参考模板


stm32_ota_bootloader\OTA\main_bootloader.c

main() 函数就是引导主程序

main_ota_app() 函数就是单片机app主程序


## 代码嵌入

就是把OTA相关的代码嵌入到单片机程序里，主要两部分：（1）主函数嵌入；（2）网络嵌入

（1）主函数嵌入：在主函数合适的位置，嵌入相关OTA接口调用。

![[Pasted image 20251222175215.png]]



（2）网络嵌入：在单片机网络处理的合适位置，嵌入OTA的接口调用。

![[Pasted image 20251222175232.png]]



## 工程配置

把OTA相关代码嵌入到原工程以后，然后还需要修改工程配置。 
- （1）修改链接地址； 
- （2）添加.bin文件生成命令；

![[Pasted image 20251222175312.png]]


![[Pasted image 20251222175321.png]]

**注意**: fromelf.exe在你自己电脑的安装路径, 后面的.bin文件名和.axf文件名根据你的实际工程修改。

参考命令:
```cmd
D:\SW\Keil_v5.25\ARM\ARMCC\bin\fromelf.exe --bin --output ../OBJ/UdpServer.bin ../OBJ/UdpServer.axf
```




