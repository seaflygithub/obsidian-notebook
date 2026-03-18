

# 软件整体结构


需求就是 MicroBlaze + exFAT + RAID0，
整个系统结构是：存储设备(microblaze+fpga)里挂载了多块容量相同的硬盘，这些硬盘通过 RAID0 组织，然后采集的数据会落盘存放到该存储设备，用户可以通过PC机和存储设备通过网线连接来访问存储设备里的文件系统。上一个版本的情况是这样的，PC机只能通过安装专用软件才能访问存储设备的文件系统（常规的数据拷贝等等操作），现在提出优化需求，用户PC机不想安装什么专用软件就能像访问本地磁盘的文件那样简单只管操作。经过技术讨论，最终选定通过 smb 服务的方式把存储设备的文件系统映射给PC机器，因为 Windows 和 Linux 都天然支持 smb 方式的文件共享。


MicroBlaze + exFAT + RAID0 整个系统结构：
```txt
                         +----------------------------------+
                         |          PC / Windows            |
                         |  Explorer / File Manager         |
                         +---------------▲------------------+
                                         │
                                         │
                                SMB2 / SMB3 Protocol
                              Ethernet / TCP/IP Stack
                                         │
                                         │
                    ==============================================
                                         │
                                         │
                               SMB Server Service
                              文件API(open/read/write/...)
                                         │
                                         │
                    ==============================================
                                         │
                                         │
                              FatFs (FAT32 / exFAT)    这样FatFs 完全不知道下面是 RAID,它认为只有一块磁盘。
                             disk_read()/disk_write()
                                         │
                                         │
                    ==============================================
                                         │
                                         │
                                       RAID0
                          LBA -> Stripe -> Disk Mapping
                                         │
                                         │
                     ┌───────────────────┴───────────────────┐
                     ▼                                       ▼
                 Disk0 Driver                            Disk1 Driver
                     │                                       │
                SD/NAND/NVMe                           SD/NAND/NVMe
```



## smb2抓包分析

0001.pcapng
0002.pcapng
0003.pcapng

SMB2 客户端请求包  —— SMB2 服务端应答包

## smb2 server


我有一个microblaze的设备，它主要是记录数据并存储到设备的磁盘里。先前如果PC电脑需要访问设备里的文件，需要通过专用软件才能挂载访问。现在想要升级，在原先硬件平台的基础上，能够通过网络的方式，让PC机能够不用专用软件就能访问设备的文件系统，就相当于把设备当作一个大的U盘，然后和电脑通过网线连接，网线连接后，比如在Windows平台，就会出现一个新磁盘，这个磁盘就是设备磁盘，用户能够像访问正常文件一样读写访问该磁盘。


第一种：网络共享（NAS）

实现一个仅支持 Windows Explorer 的 SMB2 Server

```txt
────────────────────────────────────────
           smb_packet.c
────────────────────────────────────────
 SMB Header
 SMB2 Header
 Decode
 Encode
────────────────────────────────────────
           smb_dispatch.c
────────────────────────────────────────
 switch(Command)
────────────────────────────────────────
 negotiate
 session
 tree
 file
 directory
 info
 security
────────────────────────────────────────
        Virtual File System Layer
────────────────────────────────────────
 open()
 read()
 write()
 mkdir()
 rename()
 stat()
────────────────────────────────────────
              FatFs
────────────────────────────────────────
             RAID0
────────────────────────────────────────
```

---

第一阶段：只支持这些命令

Windows Explorer 能工作的最小集合可以控制在十几个命令左右：

```txt
NEGOTIATE

SESSION_SETUP

TREE_CONNECT

CREATE

CLOSE

READ

WRITE

FLUSH

QUERY_DIRECTORY

QUERY_INFO

SET_INFO

ECHO
```


第二阶段增加：
```txt
DELETE

RENAME

MKDIR

RMDIR
```


第三阶段支持：Explorer 会越来越舒服。

```txt
文件时间

文件属性

容量查询

卷信息
```









## lwIP


**PBUF_POOL_SIZE**
lwIP会在初始化时实现初始化一个池子, 池子里有若干个pbuf实例, PBUF_POOL_SIZE 就决定了池子里 pbuf 个数。

**PBUF_POOL_BUFSIZE**
单个pbuf节点中payload最大数据量。比如默认 PBUF_POOL_BUFSIZE=1700，实际能存放的最大数据量 = 1700 - sizeof(struct pbuf)。其中为什么会选1700而不是以太网帧最大大小1518字节，因为需要留有余量，一个 pbuf 可以装下整个以太网帧，减少链表节点数，另外1700 是 4 的倍数，方便内存对齐。






## fatfs

**推荐方案：FatFs**

这是嵌入式几乎事实上的标准。

支持：
- FAT12
- FAT16
- FAT32
- **exFAT**

而且：完全 ANSI C。专门就是为了 MCU。支持exFAT。


## raid0





难点一：跨 chunk、chunk 分裂、bio 分裂
难点二：不同大小磁盘(方案: 所有盘必须一样大)
难点三：错误处理（根据实际情况返回不同错误码）

---

难点一：跨 Chunk（真正的核心）

```txt
Chunk = 64KB

用户写：
offset = 60KB
size   = 16KB
```

（整个 RAID0 最重要的部分）
逻辑请求 --> 拆成多个 chunk --> 生成多个子请求,后面的读写函数只负责执行这些子请求。

---

如何拆分多个chunk呢？给我个工业界推荐的算法。

逻辑空间：
```txt
0~64KB      -> Disk0

64~128KB    -> Disk1

128~192KB   -> Disk2

192~256KB   -> Disk3

256~320KB   -> Disk0

......
```









---

**难点二：LBA 映射**


三个公式就可以搞定：
```txt
Chunk = 64KB
Disk Number = 2

formula: stripe = offset / chunk
formula: disk = stripe % disk_count
formula: disk_offset = (stripe / disk_count) * chunk + (offset % chunk)
```


整个 RAID0 本质就是：这一部分代码通常几十行就结束了。
```txt
Logical Offset
        │
        ▼
 Stripe Number
        │
        ▼
 Disk Index
        │
        ▼
 Physical Offset
```

---

**难点三：不同容量磁盘**

初始化时检查：Disk0 Size == Disk1 Size
RAID_ERROR_SIZE_MISMATCH


---

**难点四：错误处理**

RAID0 没有恢复能力，所以原则很简单，哪个 IO 失败，就整个请求失败。

```cpp
typedef enum
{
    RAID_OK,

    RAID_ERR_DISK0,

    RAID_ERR_DISK1,

    RAID_ERR_TIMEOUT,

    RAID_ERR_BAD_PARAMETER,

    RAID_ERR_SIZE_MISMATCH,

    RAID_ERR_OUT_OF_RANGE,

} raid_result_t;
```

---

**难点五：边界条件（最容易写 Bug）**


真正开发时，Bug 大多数不是算法，而是各种边界。

例如：size == 0、
offset 正好等于 chunk 边界、
offset 正好等于磁盘末尾、
一次请求覆盖几十个 chunk、
一次请求刚好结束在 chunk 边界 等等。

建议把所有边界都列出来做单元测试。


---

**难点六：性能优化**（以后再做）

多磁盘写要能够并行执行。

如果是 RTOS，task0负责磁盘0，task1负责磁盘1，这样两块盘可以真正同时工作。


```txt
                 raid0_read()
                 raid0_write()    调用底层驱动完成实际 I/O
                      │
                      ▼
          raid0_split_request()   负责跨 Chunk 拆分请求（整个 RAID0 的核心）
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
 raid0_map()                  raid0_map()     负责逻辑地址 → 物理地址映射（纯数学计算）
        ▼                           ▼
 disk0_read()                 disk1_read()
 disk0_write()                disk1_write()
```



## sim_disk

simulate_disk —— 模拟硬盘
我目前手头只有 ax7020开发板，所以用该方案比较合适。

DDR模拟Disk0  
DDR模拟Disk1
DDR模拟Disk2
DDR模拟Disk3 。。。




# Bottom








