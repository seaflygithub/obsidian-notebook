[TOC]

# 前言

- **实验环境**：物理机 + VMware虚拟机Linux + 交叉工具链。
- 本笔记主要探究 **section** 和 **symbol** 以及它们之间的关系和应用。

![[image_20240924173855.png]]



# Makefile-常用内建函数

参考资料：
GNU Makefile 常用内建函数
https://blog.csdn.net/frank_eos/article/details/46558265

- 函数调用格式：参数之间用逗号分隔，函数与参数用空格分隔。
```makefile
$(函数名 参数1,参数2,参数3)
```


---

## 去掉两边空格

去掉开头和结尾空格
```makefile
str11="    aaa bbb ccc   "
str22=$(strip $(str11))
```


## 替换字符串

模式替换，所有.c替换成所有.o
```makefile
str22=$(patsubst %.c,%.o,111.c 222.c 333.c)
all:
	@echo str22=$(str22)

#str22=111.o 222.o 333.o
```


## 查找字符串

```makefile
str22=$(findstring a,a b c)
str33=$(findstring a,b c)
all:
	@echo str22=$(str22)
	@echo str33=$(str33)

#str22=a
#str33=
```


## 过滤与过滤掉

过滤文件名
```makefile
sources := foo.c bar.c baz.s ugh.h test.h
str22=$(filter %.c %.s,$(sources))
all:
	@echo str22=$(str22)

#str22=foo.c bar.c baz.s
```

反向过滤文件名
```makefile
objects=main1.o foo.o main2.o bar.o add.o
mains=main1.o main2.o
str22=$(filter-out $(mains),$(objects))

all:
	@echo str22=$(str22)

#str22=foo.o bar.o add.o
```


## 文件名排序函数

```makefile
str22=$(sort foo bar lose clone alone abandon)

all:
	@echo str22=$(str22)

#str22=abandon alone bar clone foo lose
```


## 单词处理

- 取1个单词：`$(word $(index),111 222 333 444 555 666)`。
- 取多个单词：`$(wordlist $(start_index), $(end_index), 111 222 333 444 555 666)`。
- 获取单词个数：`$(words 111 222 333 444 555 666)`。
```makefile
srcs:=$(wildcard ../src/*.c)
TEXT = one two three four five
FIRST_WORD = $(word 2, $(TEXT))
WORDS_2_4 = $(wordlist 2,4, $(TEXT))
WORDS_CNT = $(words $(TEXT))

all:
	@echo $(TEXT)
	@echo $(FIRST_WORD)  #two
	@echo $(WORDS_2_4)   #two three four
	@echo $(WORDS_CNT)   #5
```


---

文件名展开函数：返回展开后的文件名列表（空格分隔）
```makefile
ffffffff
```

## 文件名与目录

获取目录函数:
```makefile
str22=$(dir src/foo.c test.c)
str33=$(notdir src/foo.c test.c)

all:
	@echo str22=$(str22)
	@echo str33=$(str33)

#str22=src/ ./
#str33=foo.c test.c
```


## 前缀后缀

取后缀、取前缀：
```makefile
str22=$(suffix src/foo.c src-1.0/bar.c hacks)
str33=$(basename src/foo.c src-1.0/bar.c hacks)

all:
	@echo str22=$(str22)

#str22=.c .c
#str33=src/foo src-1.0/bar hacks
```

添加后缀：
```makefile
$(addsuffix .c,foo bar)
```


添加前缀：
```makefile
$(addprefix src/,foo bar)
```

## 索引成员拼接

成员相互连接：前面和后面的相同索引下的内容拼接。
```makefile
str22=$(join aaa bbb , 111 222 333)

all:
	@echo str22=$(str22)

//str22=aaa111 bbb222 333
```

## 变量来源

获取变量的来源：origin，如下makefile文件，当执行make时，str33的值为file，当执行 `make str22=111` 时，此时str33的值为 `command line`。下面是origin命令的返回结果：
- undefined  —— 表示这个变量未定义。
- default  —— 表示这个变量是默认定义，比如CC这个变量。
- environment  —— 表示这是一个环境变量，比如 HOME 这个变量。
- file  ——  表示这个变量是被定义在Makefile文件中的，执行make时没有赋值。
- commandline  或者  command line  ——  表示这个变量是通过外部执行 make 命令时给该变量赋值了。
```cpp
str22 ?= 222
str33=$(origin str22)

all:
	@echo str22=$(str22)
	@echo str33=$(str33)
```


## foreach循环

foreach循环：
```cpp
names := a b c d
files := $(foreach n,$(names),$(n).o)

all:
	@echo files=$(files)
```


## 条件语句if

```makefile
ifeq ("$(origin V)", "command line")
  KBUILD_VERBOSE = $(V)
endif

ifeq ("$(origin M)", "command line")
  KBUILD_EXTMOD := $(M)
else
  KBUILD_EXTMOD := 
endif

ifeq ($(KBUILD_SRC)/,$(dir $(CURDIR)))
        # building in a subdirectory of the source tree
        srctree := ..
else

str22=$(shell pwd)
newdir=${HOME}

all:
    $(warning 2222222222222222 3333)

srcs:=$(wildcard ../src/*.c)
all:
	@echo $(srcs)
```

# Makefile-高级应用


## 递归make

- 通过调用$(MAKE)来执行子Makefile，实现项目的分层构建。
```makefile
subdirs := dir1 dir2 dir3
.PHONY: all clean
all:
    $(foreach dir, $(subdirs), $(MAKE) -C $(dir);)
clean:
    $(foreach dir, $(subdirs), $(MAKE) -C $(dir) clean;)
```

## 变量的高级用法

- 使用:=定义立即展开变量，确保定义时立即计算值。
- 而单独的=符号则表示延迟展开，直到使用时。
```makefile
VAR_A = A
VAR_B = $(VAR_A) B
VAR_A = AA
# echo "VAR_B = $(VAR_B)" and then result is VAR_B = AA B

VAR_A := A
VAR_B := $(VAR_A) B
VAR_A := AA
# echo "VAR_B = $(VAR_B)" and then result is VAR_B = A B
```

---

- 针对特定目标设置不同的编译选项或依赖。
```makefile
target1.o: CFLAGS += -DTARGET1_FLAG
target2.o: CFLAGS += -DTARGET2_FLAG
```

## 自动依赖管理

- **增量编译检测**：.d文件列出了源文件直接或间接依赖的所有头文件。这使得Makefile能够自动跟踪这些依赖关系，当头文件发生变化时，相应的源文件可以被重新编译，确保编译结果的一致性。在没有.d文件的情况下，开发者需要手动列出每个目标文件的依赖，这在大型项目中既耗时又容易出错。.d文件自动生成这些依赖关系，极大地减轻了这一负担。通过.d文件，Make可以更精确地判断哪些对象文件需要重新编译，只编译那些其依赖项（包括源文件和头文件）已更改的部分，从而加快构建速度。.d文件还可以帮助发现未明确声明的依赖，从而在编译阶段早期捕获潜在的链接错误。
- **集成到Makefile**：通过在Makefile中使用include指令引入.d文件，Makefile能够自动包含所有依赖信息。例如，使用模式规则%.d: %.c和GCC的-MMD选项来生成这些文件，并通过脚本处理或直接在Makefile中处理这些.d文件，确保它们被正确解析和使用。

---

- 生成单个可执行程序文件的例子
```makefile
# 设置编译器和编译选项
EXECUTABLE = my_program
SRCROOTDIR = ..
CC = gcc
CFLAGS = -Wall -g
CPPFLAGS += -MMD -MP
#SOURCES = $(wildcard ../src/*.c)
#SOURCES += $(wildcard ../src/math/*.c)
SOURCES := $(shell find $(SRCROOTDIR) -name "*.c")  # 递归查找所有源文件


OBJECTS := $(SOURCES:.c=.o)
DEPENDS := $(SOURCES:.c=.d)


# 编译规则
all: $(EXECUTABLE)


$(EXECUTABLE): $(OBJECTS)
	$(CC) $(LDFLAGS) -o $@ $^


# 自动包含依赖文件
-include $(SOURCES:.c=.d)


# 清理规则
clean:
	-rm -f $(EXECUTABLE) $(OBJECTS) $(DEPENDS)
```

- gcc编译选项中 **-MD** 和 **-MMD** 的区别，两者都是用来生成依赖文件的，而后者默认排除了系统头文件，只列出用户定义的头文件。这意味着在生成的依赖文件中，你通常只会看到项目内部的头文件依赖。


---

- 生成单个库的例子

```makefile
# 定义源文件和目标文件
SOURCES := add.c sub.c
OBJECTS := $(SOURCES:.c=.o)
SHARED_LIBRARY := libmymath.so

# 编译规则，需要-fPIC以支持位置无关代码
%.o: %.c
    gcc -fPIC -c $< -o $@

# 动态库生成规则
$(SHARED_LIBRARY): $(OBJECTS)
    gcc -shared -o $(SHARED_LIBRARY) $(OBJECTS)

# 清理规则
clean:
    rm -f $(OBJECTS) $(SHARED_LIBRARY)
```

```makefile
# 定义源文件和目标文件
SOURCES = add.c sub.c
OBJECTS = $(SOURCES:.c=.o)
STATIC_LIBRARY = libmymath.a

# 编译规则
%.o: %.c
    gcc -c $< -o $@

# 静态库生成规则
$(STATIC_LIBRARY): $(OBJECTS)
    ar -rcs $(STATIC_LIBRARY) $(OBJECTS)

# 清理规则
clean:
    rm -f $(OBJECTS) $(STATIC_LIBRARY)
```




# ZYNQ-FSBL-BOOT.BIN


## 探究FSBL主流程和地址空间

- **链接器脚本与地址空间**：通过 lscript.ld 文件里的 MEMORY 可以获取其地址空间，并画出地址空间分布图。

```cpp
MEMORY
{
   ps7_ddr_0 : ORIGIN = 0x100000, LENGTH = 0x3FF00000
   ps7_qspi_linear_0 : ORIGIN = 0xFC000000, LENGTH = 0x1000000
   ps7_ram_0 : ORIGIN = 0x0, LENGTH = 0x30000
   ps7_ram_1 : ORIGIN = 0xFFFF0000, LENGTH = 0xFE00
}
```

![[image_20240821220957.png]]


- **FSBL-RAM0**：经过实验结果验证，无论是在启动介质(比如SD卡)中，还是JTAG在线下载，FSBL必须在 ps7_ram_0 里，FSBL只能运行在RAM里，大部分运行在RAM0，因为RAM1空间可能不够。

```cpp {.line-numbers}
MEMORY
{
   ps7_ddr_0 : ORIGIN = 0x100000, LENGTH = 0x3FF00000
   ps7_qspi_linear_0 : ORIGIN = 0xFC000000, LENGTH = 0x1000000
   ps7_ram_0 : ORIGIN = 0x0, LENGTH = 0x30000
   ps7_ram_1 : ORIGIN = 0xFFFF0000, LENGTH = 0xFE00
}

/* Specify the default entry point to the program */
ENTRY(_vector_table)

/* Define the sections, and where they are mapped in memory */
SECTIONS
{
    .text : {
        KEEP (*(.vectors))
        *(.boot)
        *(.text) //The .text of all the files is put here.
        *(.text.*)
        *(.gnu.linkonce.t.*)
        *(.plt)
        *(.gnu_warning)
        *(.gcc_execpt_table)
        *(.glue_7)
        *(.glue_7t)
        *(.vfp11_veneer)
        *(.ARM.extab)
        *(.gnu.linkonce.armextab.*)
    } > ps7_ram_0

    .init : {
        KEEP (*(.init))
    } > ps7_ram_0

    ...
}
```

---


```cpp
#define log_print_debug(fmt,...) do {\
    printf("%s:%s():%d:>> ", __FILE__, __func__, __LINE__);\
    printf(fmt,##__VA_ARGS__);\
    printf("\r\n");\
}while(0)
```


02、**FSBL-主流程**：我们现在控制变量法，默认SD卡启动模式，然后FSBL主程序经过简化，可运行的核心代码如下：
```cpp
//This is the main function for the FSBL ROM code.
int main(void)
{
    u32 BootModeRegister = 0;
    u32 HandoffAddress = 0;
    u32 Status = XST_SUCCESS;
    
    //PCW initialization for MIO,PLL,CLK and DDR
    Status = ps7_init();
    if (Status != FSBL_PS7_INIT_SUCCESS) return -1;

    SlcrUnlock();

    Xil_DCacheFlush();
    Xil_DCacheDisable();

    //Register the Exception handlers
    RegisterHandlers();
    Status = InitPcap();

#if defined(XPAR_PS7_SD_0_S_AXI_BASEADDR) || defined(XPAR_XSDPS_0_BASEADDR)
    log_print_debug("Boot mode is SD");
    Status = InitSD("BOOT.BIN");
    MoveImage = SDAccess;
#endif

    HandoffAddress = LoadBootImage();
    log_print_debug("HandoffAddress = 0x%lx", HandoffAddress);
    FsblHandoff(HandoffAddress);//PC = HandoffAddress
    return Status;
}
```


04、在SD卡启动模式下，下面是一些关键信息：
```cpp
../src/main.c:main():258:>> Boot mode is SD
../src/image_mover.c:LoadBootImage():193:>> Silicon_Version = 3
../src/image_mover.c:LoadBootImage():229:>> Image Start Address: 0x00000000
../src/image_mover.c:PartitionMove():1170:>> //PL
    SourceAddr = 0x100000, Header->LoadAddr = 0x0, Header->ExecAddr = 0x0
../src/image_mover.c:PartitionMove():1170:>> //PS
    SourceAddr = 0x100000, Header->LoadAddr = 0x100000, Header->ExecAddr = 0x100000
../src/main.c:main():264:>> HandoffAddress = 0x100000
../src/helloworld.c:main():28:>> main address is 0x1005b8
```

## 探究BIT文件到BOOT.BIN

- **PcapLoadPartition**：这里我们简化改写了必要的函数，去掉了很多检查和不必要的条件判断。然后重新编译FSBL并下载到开发板，开发板是SD卡启动模式，然后看到必要的日志打印。这里我们探究的是，FSBL如何识别处BOOT.BIN中的比特流文件，并把比特流从BOOT.BIN中读取出来，最终加载到PL端运行。其中最核心的函数就是 PcapLoadPartition 这个函数，它负责把比特流怼到PL硬件里，让PL程序运行起来。

```cpp
u32 LoadBootImage(void)
{
    u32 RebootStatusRegister = 0;
    u32 MultiBootReg = 0;
    u32 ImageStartAddress = 0;
    u32 PartitionNum;
    u32 PartitionDataLength;
    u32 PartitionImageLength;
    u32 PartitionTotalSize;
    u32 PartitionExecAddr;
    u32 PartitionAttr;
    u32 ExecAddress = 0;
    u32 PartitionLoadAddr;
    u32 PartitionStartAddr;
    u32 PartitionChecksumOffset;
    u8 ExecAddrFlag = 0 ;
    u32 Status;
    PartHeader *HeaderPtr;
    u32 EfuseStatusRegValue;
    /*
     * Resetting the Flags
     */
    BitstreamFlag = 0;
    ApplicationFlag = 0;

    RebootStatusRegister = Xil_In32(REBOOT_STATUS_REG);

    //read the multiboot register
    MultiBootReg =  XDcfg_ReadReg(DcfgInstPtr->Config.BaseAddr, XDCFG_MULTIBOOT_ADDR_OFFSET);

    //Compute the image start address
    ImageStartAddress = (MultiBootReg & PCAP_MBOOT_REG_REBOOT_OFFSET_MASK) * GOLDEN_IMAGE_OFFSET;
    log_print_debug("Image Start Address: 0x%08lx\r\n",ImageStartAddress);

    //Get partitions header information
    Status = GetPartitionHeaderInfo(ImageStartAddress);

    //分区[0]是存放FSBL的分区,因此从分区[1]开始,而且在裸机SDK中总共只有3个分区(fsbl+bit+elf)
    for (size_t PartitionIdx = 1; PartitionIdx < 3; PartitionIdx++)
    {
        HeaderPtr = &PartitionHeader[PartitionIdx];
        HeaderDump(HeaderPtr);

        //Load partition header information in to local variables
        PartitionDataLength = HeaderPtr->DataWordLen;
        PartitionImageLength = HeaderPtr->ImageWordLen;
        PartitionExecAddr = HeaderPtr->ExecAddr;
        PartitionAttr = HeaderPtr->PartitionAttr;
        PartitionLoadAddr = HeaderPtr->LoadAddr;
        PartitionChecksumOffset = HeaderPtr->CheckSumOffset;
        PartitionStartAddr = HeaderPtr->PartitionStart;
        PartitionTotalSize = HeaderPtr->PartitionWordLen;

        if (PartitionAttr & ATTRIBUTE_PL_IMAGE_MASK)
        {
            log_print_debug("-------------------------- Now in PL Progress");
            PLPartitionFlag = 1;
            PSPartitionFlag = 0;
            BitstreamFlag = 1;
        }

        if (PartitionAttr & ATTRIBUTE_PS_IMAGE_MASK) {
            log_print_debug("-------------------------- Now in PS Progress");
            PSPartitionFlag = 1;
            PLPartitionFlag = 0;
            ApplicationFlag = 1;

            if (!ExecAddrFlag)
            {
                ExecAddrFlag++;
                //直接获取地址,后续这个内存地址会直接交给PC指针
                ExecAddress = PartitionExecAddr;
            }
        }

        //把BOOT.BIN内各个子文件内容从存储介质拷贝到内存中
        Status = PartitionMove(ImageStartAddress, HeaderPtr);
    }

    return ExecAddress;
}

//This function load the partition from boot device
u32 PartitionMove(u32 ImageBaseAddress, PartHeader *Header)
{
    ...
    ...
    
    /*
     * Load Bitstream partition in to fabric only
     * if checksum and authentication bits are not set
     */
    log_print_debug("SourceAddr = 0x%lx, Header->LoadAddr = 0x%lx, Header->ExecAddr = 0x%lx", 
        SourceAddr, Header->LoadAddr, Header->ExecAddr);
    if (PLPartitionFlag && (!(SignedPartitionFlag || PartitionChecksumFlag))) {
        log_print_debug("PcapLoadPartition execute here ");
        log_print_debug("srcaddr = 0x%lx", SourceAddr);
        log_print_debug("dstaddr = 0x%lx", Header->LoadAddr);
        log_print_debug("ImageWordLen = %d", Header->ImageWordLen);
        log_print_debug("DataWordLen  = %d", Header->DataWordLen);

        //PcapLoadPartition()函数是加载bit到FPGA器件的关键函数
        Status = PcapLoadPartition((u32*)SourceAddr,
                    (u32*)Header->LoadAddr,
                    Header->ImageWordLen,
                    Header->DataWordLen,
                    EncryptedPartitionFlag);
        if(Status != XST_SUCCESS) {
            fsbl_printf(DEBUG_GENERAL, "PCAP Bitstream Download Failed\r\n");
            return XST_FAILURE;
        }
    }
}
```

---

- **比特流数据搬运和运行**：下面进一步探究，比特流在BOOT.BIN中的起始内容和大小，以及比特流在 system.bit 文件中的起始内容和大小，通过该方法，探究比特流哪些数据最终被打包进BOOT.BIN并且在板子上电时被加载到PL执行。下面的串口输出信息表示，分别dump了 BOOT.BIN 中比特流的开始位置和结束位置的数据内容，并对比 hardware.bit 文件中的内容。

```cpp
../src/main.c:main():258:>> Boot mode is SD
../src/image_mover.c:LoadBootImage():219:>> Image Start Address: 0x00000000
../src/image_mover.c:LoadBootImage():242:>> ------------ Now in PL Progress
../src/image_mover.c:PartitionMove():863:>> 
    SourceAddr = 0x100000, Header->LoadAddr = 0x0, Header->ExecAddr = 0x0
../src/image_mover.c:PartitionMove():865:>> PcapLoadPartition execute here 
../src/image_mover.c:PartitionMove():866:>> srcaddr = 0x100000
../src/image_mover.c:PartitionMove():867:>> dstaddr = 0x0
../src/image_mover.c:PartitionMove():868:>> ImageWordLen = 1011392
../src/image_mover.c:PartitionMove():869:>> DataWordLen  = 1011392
../src/image_mover.c:PartitionMove():870:>> start of SourceAddr data dump: 
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff |................
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff |................
bb 00 00 00 44 00 22 11 ff ff ff ff ff ff ff ff |....D.".........
66 55 99 aa 00 00 00 20 01 20 02 30 00 00 00 00 |fU..... . .0....
../src/image_mover.c:PartitionMove():873:>> end of SourceAddr data dump: 
00 00 00 20 00 00 00 20 00 00 00 20 00 00 00 20 |... ... ... ... 
00 00 00 20 00 00 00 20 00 00 00 20 00 00 00 20 |... ... ... ... 
00 00 00 20 00 00 00 20 00 00 00 20 00 00 00 20 |... ... ... ... 
00 00 00 20 00 00 00 20 00 00 00 20 00 00 00 20 |... ... ... ... 
```

- 从下图最终对比数据得知，比特流文件打包进BOOT.BIN文件，需要做**字节序转换**，并且以字为单位(4字节)做字节序转换。

![[image_20240820105755.png]]


## 探究ELF文件到BOOT.BIN

问题清单：
- （1）ELF文件开始位置是哪里？
- （2）ELF拷贝到BOOT.BIN大小怎么确定？
- （3）ELF文件里哪些节需要加载到内存中以保证程序能够运行？

---

- **开始执行PS程序**：FSBL加载到PS程序后，会把地址直接交给PC指针，之后PS就跳转到对应的地址，执行PS程序了。

```cpp
int buffer_print8(const void *buf, const uint32_t length, int bytesOneLine)
{
    const uint8_t *data_buffer = (const uint8_t *)buf;
    size_t i = 0, j = 0;
    uint8_t byte = 0;
    for (i = 0; i < length; i++)
    {
        byte = data_buffer[i];
        printf("%02x ", data_buffer[i]);
        if ((i % bytesOneLine == (bytesOneLine - 1)) || (i == length - 1))
        {
            for (j = 0; j < (bytesOneLine - 1) - (i % bytesOneLine); j++)
            {
                printf("   ");
            }
            printf("|");
            for (j = (i - (i % bytesOneLine)); j <= i; j++)
            {
                byte = data_buffer[j];
                if (byte > 31 && byte < 127)
                    printf("%c", byte);
                else
                    printf(".");
            }
            printf("\n");
        }
    }
    return 0;
}

u32 LoadBootImage(void)
{
    ...
    ...
    if (PartitionAttr & ATTRIBUTE_PS_IMAGE_MASK) {
        ...
        //把BOOT.BIN内各个文件从存储介质拷贝到内存中
        log_print_debug("ImageWordLen   = %d", HeaderPtr->ImageWordLen);
        log_print_debug("PartitionStart = %d (words)", HeaderPtr->PartitionStart);
        log_print_debug("ImageStartAddress         = %d", ImageStartAddress);
        Status = PartitionMove(ImageStartAddress, HeaderPtr);
        log_print_debug("begin data:");
        buffer_print8(ExecAddress, 64, 16);
        log_print_debug("end   data:");
        buffer_print8(ExecAddress + HeaderPtr->ImageWordLen*4 - 64, 64, 16);
    }
}
```


```cpp
../src/image_mover.c:LoadBootImage():252:>> -------------------------- Now in PS Progress
../src/image_mover.c:LoadBootImage():261:>> ExecAddress    = 0x100000
../src/image_mover.c:LoadBootImage():265:>> ImageWordLen   = 20484
../src/image_mover.c:LoadBootImage():266:>> PartitionStart = 1049744 (words)
../src/image_mover.c:LoadBootImage():267:>> ImageStartAddress         = 0
../src/image_mover.c:PartitionMove():864:>> SourceAddr = 0x100000, LoadAddr = 0x100000, ExecAddr = 0x100000
../src/image_mover.c:LoadBootImage():269:>> begin data:
49 00 00 ea 25 00 00 ea 2b 00 00 ea 3b 00 00 ea |I...%...+...;...
32 00 00 ea 00 f0 20 e3 00 00 00 ea 0f 00 00 ea |2..... .........
0f 50 2d e9 10 0b 2d ed 20 0b 6d ed 10 1a f1 ee |.P-...-. .m.....
04 10 2d e5 10 1a f8 ee 04 10 2d e5 95 08 00 eb |..-.......-.....
../src/image_mover.c:LoadBootImage():271:>> end   data:
00 00 40 ff 00 00 50 ff 00 00 60 ff 00 00 70 ff |..@...P...`...p.
00 00 80 ff 00 00 90 ff 00 00 a0 ff 00 00 b0 ff |................
00 00 c0 ff 00 00 d0 ff 00 00 e0 ff 0e 4c f0 ff |.............L..
ac aa ff 7f 01 00 00 00 84 05 10 00 40 05 10 00 |............@...
../src/main.c:main():264:>> HandoffAddress = 0x100000
../src/helloworld.c:main():28:>> main address is 0x1005b8
[1] Now led_on == 1
[2] Now led_on == 0
```

![[image_20240820223604.png]]

- 由上下图得知，绿色字体红框截图，是 hello.elf 的section信息表，其中红框所在列Off，表示相对于 hello.elf 文件内的偏移量，通过 fseek 来定位。经过探究，最终把 hello.elf 打包到 BOOT.bin 里的，不是所有内容都打包进去，只把 hello.elf 上面红框范围内的内容打包进 BOOT.bin 即可。这结果是通过上面的实验验证得来。并在期间参考Linux内核模块加载相关的代码来进一步验证。

![[image_20240820224833.png]]


## 手搓ELF浅解析


```bash
readelf -a hello.elf > hello.readelf

ELF Header:
  Magic:   7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF32
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           ARM
  Version:                           0x1
  Entry point address:               0x100000
  Start of program headers:          52 (bytes into file)
  Start of section headers:          348632 (bytes into file)
  Flags:                             0x5000400, Version5 EABI, hard-float ABI
  Size of this header:               52 (bytes)
  Size of program headers:           32 (bytes)
  Number of program headers:         2
  Size of section headers:           40 (bytes)
  Number of section headers:         28
  Section header string table index: 27

Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .text             PROGBITS        00100000 010000 00ebd0 00  AX  0   0 64
  [ 2] .init             PROGBITS        0010ebd0 01ebd0 000018 00  AX  0   0  4
  [ 3] .fini             PROGBITS        0010ebe8 01ebe8 000018 00  AX  0   0  4
  [ 4] .rodata           PROGBITS        0010ec00 01ec00 000524 00   A  0   0  8
  [ 5] .data             PROGBITS        0010f128 01f128 000a14 00  WA  0   0  8
  [ 6] .eh_frame         PROGBITS        0010fb3c 01fb3c 000004 00   A  0   0  4
  [ 7] .mmu_tbl          PROGBITS        00110000 020000 004000 00   A  0   0  1
  [ 8] .ARM.exidx        ARM_EXIDX       00114000 024000 000008 00  AL  1   0  4
  [ 9] .init_array       INIT_ARRAY      00114008 024008 000004 04  WA  0   0  4
  [10] .fini_array       FINI_ARRAY      0011400c 02400c 000004 04  WA  0   0  4
  [11] .ARM.attributes   ARM_ATTRIBUTES  00114010 024010 000033 00      0   0  1
  [12] .bss              NOBITS          00114010 024010 000328 00  WA  0   0  4
  [13] .heap             NOBITS          00114338 024010 002008 00  WA  0   0  1
  [14] .stack            NOBITS          00116340 024010 003800 00  WA  0   0  1
  [15] .comment          PROGBITS        00000000 024043 000031 01  MS  0   0  1
  [16] .debug_info       PROGBITS        00000000 024074 00dbf7 00      0   0  1
  [17] .debug_abbrev     PROGBITS        00000000 031c6b 002d96 00      0   0  1
  [18] .debug_aranges    PROGBITS        00000000 034a08 0003b8 00      0   0  8
  [19] .debug_macro      PROGBITS        00000000 034dc0 0036f8 00      0   0  1
  [20] .debug_line       PROGBITS        00000000 0384b8 00493d 00      0   0  1
  [21] .debug_str        PROGBITS        00000000 03cdf5 00ff5f 01  MS  0   0  1
  [22] .debug_frame      PROGBITS        00000000 04cd54 000ad4 00      0   0  4
  [23] .debug_loc        PROGBITS        00000000 04d828 002d99 00      0   0  1
  [24] .debug_ranges     PROGBITS        00000000 0505c1 000120 00      0   0  1
  [25] .symtab           SYMTAB          00000000 0506e4 002f80 10     26 428  4
  [26] .strtab           STRTAB          00000000 053664 001a65 00      0   0  1
  [27] .shstrtab         STRTAB          00000000 0550c9 00010f 00      0   0  1

Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings)
  I (info), L (link order), G (group), T (TLS), E (exclude), x (unknown)
  O (extra OS processing required) o (OS specific), p (processor specific)
```


下面是完整源代码，主要解析ELF文件的ehdr和shdr：
```cpp
//https://blog.csdn.net/u012787710/article/details/77613298

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>

int file_get_context(const char *file, long off, void *buffer, long rdlen)
{
    FILE *fp = fopen(file, "rb");
    uint8_t *buf = (uint8_t *)buffer;
    
    fseek(fp, off, SEEK_SET);
    fread(buf, 1, rdlen, fp);
    fclose(fp);
    
    return 0;
}

int buffer_print8(const void *buf, const uint32_t length, int bytesOneLine)
{
    const uint8_t *data_buffer = (const uint8_t *)buf;
    size_t i = 0, j = 0;
    uint8_t byte = 0;
    for (i = 0; i < length; i++)
    {
        byte = data_buffer[i];
        printf("%02x ", data_buffer[i]);
        if ((i % bytesOneLine == (bytesOneLine - 1)) || (i == length - 1))
        {
            for (j = 0; j < (bytesOneLine - 1) - (i % bytesOneLine); j++)
            {
                printf("   ");
            }
            printf("|");
            for (j = (i - (i % bytesOneLine)); j <= i; j++)
            {
                byte = data_buffer[j];
                if (byte > 31 && byte < 127)
                    printf("%c", byte);
                else
                    printf(".");
            }
            printf("\n");
        }
    }
    return 0;
}

typedef uint16_t Elf32_Half;
typedef uint16_t Elf32_Half;
typedef uint32_t Elf32_Word;
typedef uint32_t Elf32_Addr;
typedef uint32_t Elf32_Off ;
typedef uint32_t Elf32_Off ;
typedef uint32_t Elf32_Word;
typedef uint16_t Elf32_Half;
typedef uint16_t Elf32_Half;
typedef uint16_t Elf32_Half;
typedef uint16_t Elf32_Half;
typedef uint16_t Elf32_Half;
typedef uint16_t Elf32_Half;
typedef int32_t  Elf32_Sword;

#define EI_NIDENT       16  
typedef struct elf32_hdr{  
    unsigned char e_ident[EI_NIDENT];   
    Elf32_Half    e_type;     /* file type */  
    Elf32_Half    e_machine;  /* architecture */  
    Elf32_Word       e_version;  
    Elf32_Addr    e_entry;    /* entry point */  
    Elf32_Off       e_phoff;        /* PH table offset */  
    Elf32_Off       e_shoff;        /* SH table offset */  
    Elf32_Word    e_flags;  
    Elf32_Half    e_ehsize;       /* ELF header size in bytes */  
    Elf32_Half    e_phentsize;    /* PH size */  
    Elf32_Half    e_phnum;        /* PH number */  
    Elf32_Half    e_shentsize;    /* SH size */  
    Elf32_Half    e_shnum;        /* SH number */  
    Elf32_Half    e_shstrndx; /* SH name string table index */  
} Elf32_Ehdr;
//sizeof(Elf32_Ehdr) == 52

/* Legal values for e_type (object file type).  */
#define ET_NONE     0       /* No file type */
#define ET_REL      1       /* Relocatable file */
#define ET_EXEC     2       /* Executable file */
#define ET_DYN      3       /* Shared object file */
#define ET_CORE     4       /* Core file */




typedef struct {  
    Elf32_Word    sh_name;    /* name of section, index */  
    Elf32_Word    sh_type;      
    Elf32_Word    sh_flags;  
    Elf32_Addr    sh_addr;       /* memory address, if any */  
    Elf32_Off     sh_offset;  
    Elf32_Word    sh_size;        /* section size in file */  
    Elf32_Word    sh_link;  
    Elf32_Word    sh_info;  
    Elf32_Word    sh_addralign;  
    Elf32_Word    sh_entsize;     /* fixed entry size, if have */  
} Elf32_Shdr;
//Section Header sizeof(Elf32_Shdr) == 40

/* Legal values for sh_flags (section flags).  */
#define SHF_WRITE        (1 << 0)   /* Writable */
#define SHF_ALLOC        (1 << 1)   /* Occupies memory during execution */
#define SHF_EXECINSTR        (1 << 2)   /* Executable */
#define SHF_MERGE        (1 << 4)   /* Might be merged */
#define SHF_STRINGS      (1 << 5)   /* Contains nul-terminated strings */

/* Legal values for sh_type (section type).  */
#define SHT_NULL      0     /* Section header table entry unused */
#define SHT_PROGBITS      1     /* Program data */
#define SHT_SYMTAB    2     /* Symbol table */
#define SHT_STRTAB    3     /* String table */
#define SHT_RELA      4     /* Relocation entries with addends */
#define SHT_HASH      5     /* Symbol hash table */
#define SHT_DYNAMIC   6     /* Dynamic linking information */
#define SHT_NOTE      7     /* Notes */
#define SHT_NOBITS    8     /* Program space with no data (bss) */
#define SHT_REL       9     /* Relocation entries, no addends */
#define SHT_SHLIB     10        /* Reserved */
#define SHT_DYNSYM    11        /* Dynamic linker symbol table */
#define SHT_INIT_ARRAY    14        /* Array of constructors */
#define SHT_FINI_ARRAY    15        /* Array of destructors */
#define SHT_PREINIT_ARRAY 16        /* Array of pre-constructors */
#define SHT_GROUP     17        /* Section group */
#define SHT_SYMTAB_SHNDX  18        /* Extended section indeces */
#define SHT_NUM       19        /* Number of defined types.  */

/* Find a module section: 0 means not found. */
// static unsigned int find_sec(const Elf32_Ehdr *ehdr, const char *name)
// {
    // unsigned int i;

    // for (i = 1; i < ehdr->e_shnum; i++) {
        // Elf_Shdr *shdr = &info->sechdrs[i];
        // /* Alloc bit cleared means "ignore it." */
        // if ((shdr->sh_flags & SHF_ALLOC)
            // && strcmp(info->secstrings + shdr->sh_name, name) == 0)
            // return i;
    // }
    // return 0;
// }







typedef struct elf32_phdr{  
    Elf32_Word    p_type;   
    Elf32_Off     p_offset;  
    Elf32_Addr    p_vaddr;        /* virtual address */  
    Elf32_Addr    p_paddr;        /* ignore */  
    Elf32_Word    p_filesz;       /* segment size in file */  
    Elf32_Word    p_memsz;        /* size in memory */  
    Elf32_Word    p_flags;  
    Elf32_Word    p_align;       
} Elf32_Phdr;  
//Program Header sizeof(Elf32_Phdr) == 32







typedef struct elf32_sym{  
    Elf32_Word    st_name;  
    Elf32_Addr    st_value;  
    Elf32_Word    st_size;  
    unsigned char st_info;  
    unsigned char st_other;  
    Elf32_Half    st_shndx;  
} Elf32_Sym;
//Symbol Table sizeof(Elf32_Phdr) == 16

/* Legal values for ST_BIND subfield of st_info (symbol binding).  */
#define STB_LOCAL   0       /* Local symbol 局部符号，对于目标文件的外部不可见*/
#define STB_GLOBAL  1       /* Global symbol 全局符号，外部可见*/
#define STB_WEAK    2       /* Weak symbol 弱引用*/
#define STB_NUM     3       /* Number of defined types.  */
#define STB_LOOS    10      /* Start of OS-specific */
#define STB_GNU_UNIQUE  10      /* Unique symbol.  */
#define STB_HIOS    12      /* End of OS-specific */
#define STB_LOPROC  13      /* Start of processor-specific */
#define STB_HIPROC  15      /* End of processor-specific */

/* Legal values for ST_TYPE subfield of st_info (symbol type).  */
#define STT_NOTYPE  0 /* Symbol type is unspecified */
#define STT_OBJECT  1  /* Symbol is a data object, such as var, array */
#define STT_FUNC    2 /* Symbol is a code object, such as func,or other execode */
#define STT_SECTION 3 /* Symbol associated with a section, must be STB_LOCAL */
#define STT_FILE    4 //file name
#define STT_COMMON  5       /* Symbol is a common data object */
#define STT_TLS     6       /* Symbol is thread-local data object*/
#define STT_NUM     7       /* Number of defined types.  */
#define STT_LOOS    10      /* Start of OS-specific */
#define STT_GNU_IFUNC   10      /* Symbol is indirect code object */
#define STT_HIOS    12      /* End of OS-specific */
#define STT_LOPROC  13      /* Start of processor-specific */
#define STT_HIPROC  15      /* End of processor-specific */

#define SHN_UNDEF   0 //Undefined section, but defined in other file   
#define SHN_ABS     0xfff1 //Associated symbol is absolute, such as filename
#define SHN_COMMON  0xfff2 //Associated symbol is common, uninited global vars











#define log_print_debug(fmt,...) do {\
    printf("%s:%s():%d:>> ", __FILE__, __func__, __LINE__);\
    printf(fmt,##__VA_ARGS__);\
    printf("\r\n");\
}while(0)

int main(int argc, const char *argv[])
{
    const char *file = argv[1];
    log_print_debug("%s", file);
    
    Elf32_Ehdr ehdr;
    file_get_context(file, 0, &ehdr, sizeof(ehdr));
    
    
    do {
        printf("e_ident        = ");
        for(int i=0; i<EI_NIDENT; i++)
        {
            //[0~4]             elf magic number
            //[5]               1=elf is 32bit, 2=elf is 64bit
            //[6]               1=elf is little-endian, 2=...big-endian
            //[7]               fixed=1, version of elf
            //[8~EI_NIDENT-1]   reserved
            printf("%02x ", ehdr.e_ident[i]);
        }
        printf("\n");

        printf("e_type         = 0x%x (ET_REL=1 xxx.o, ET_EXEC=2, ET_DYN=3 xxx.so)\n", ehdr.e_type);
        printf("e_machine      = 0x%x\n", ehdr.e_machine);
        printf("e_version      = 0x%x\n", ehdr.e_version);
        printf("e_entry        = 0x%x\n", ehdr.e_entry);
        printf("e_phoff        = 0x%x\n", ehdr.e_phoff);
        printf("e_shoff        = 0x%x\n", ehdr.e_shoff);
        printf("e_flags        = 0x%x\n", ehdr.e_flags);
        printf("e_ehsize       = 0x%x\n", ehdr.e_ehsize);
        printf("e_phentsize    = 0x%x\n", ehdr.e_phentsize);
        printf("e_phnum        = 0x%x\n", ehdr.e_phnum);
        printf("e_shentsize    = 0x%x\n", ehdr.e_shentsize);
        printf("e_shnum        = 0x%x\n", ehdr.e_shnum);
        printf("e_shstrndx     = 0x%x\n", ehdr.e_shstrndx);  
    }while(0);
    


    do {
        const Elf32_Shdr *shdr;
        const char *secname;
        
        Elf32_Shdr *shdrs = malloc(sizeof(Elf32_Shdr) * ehdr.e_shnum);
        file_get_context(file, ehdr.e_shoff, shdrs, sizeof(Elf32_Shdr) * ehdr.e_shnum);
        

        printf("%64s\n", "----------------------------------------------------------------------");
        printf("%-4s  "  "%-16s  "  "%-12s  "  "%-8s  " "%-8s  "    "%-8s\n", 
               "idx",   "sename",  "sectype", "secaddr", "secoffset", "secsize");
        printf("%64s\n", "----------------------------------------------------------------------");
        for(int i=0; i<ehdr.e_shnum; i++)
        {
            shdr = &shdrs[i];
            
            //这是文件中存放字符串的位置,在文件中的偏移
            shdrs[ehdr.e_shstrndx].sh_offset;
            
            //这是字符串总大小
            shdrs[ehdr.e_shstrndx].sh_size;
            
            char *secstrs = malloc(shdrs[ehdr.e_shstrndx].sh_size);
            file_get_context(file, shdrs[ehdr.e_shstrndx].sh_offset, 
                secstrs, shdrs[ehdr.e_shstrndx].sh_size);
            
            secname = (const char *)&secstrs[shdr->sh_name];
            
            printf("%04d  "  "%-16s  "  "%-12d  "      "%08x  "     "%08x  "       "%08x\n", 
                     i,     secname,    
                     shdr->sh_type, shdr->sh_addr, shdr->sh_offset, shdr->sh_size);
        }
    } while(0);

    
    return 0;
}
```


```cpp
elf-read.c:main():234:>> hello hello.elf
e_ident        = 7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00
e_type         = 0x2 (ET_REL=1 xxx.o, ET_EXEC=2, ET_DYN=3 xxx.so)
e_machine      = 0x28
e_version      = 0x1
e_entry        = 0x100000
e_phoff        = 0x34
e_shoff        = 0x551d8
e_flags        = 0x5000400
e_ehsize       = 0x34
e_phentsize    = 0x20
e_phnum        = 0x2
e_shentsize    = 0x28
e_shnum        = 0x1c
e_shstrndx     = 0x1b
----------------------------------------------------------------------
idx   sename            sectype       secaddr   secoffset  secsize
----------------------------------------------------------------------
0000                    0             00000000  00000000  00000000
0001  .text             1             00100000  00010000  0000ebd0
0002  .init             1             0010ebd0  0001ebd0  00000018
0003  .fini             1             0010ebe8  0001ebe8  00000018
0004  .rodata           1             0010ec00  0001ec00  00000524
0005  .data             1             0010f128  0001f128  00000a14
0006  .eh_frame         1             0010fb3c  0001fb3c  00000004
0007  .mmu_tbl          1             00110000  00020000  00004000
0008  .ARM.exidx        1879048193    00114000  00024000  00000008
0009  .init_array       14            00114008  00024008  00000004
0010  .fini_array       15            0011400c  0002400c  00000004
0011  .ARM.attributes   1879048195    00114010  00024010  00000033
0012  .bss              8             00114010  00024010  00000328
0013  .heap             8             00114338  00024010  00002008
0014  .stack            8             00116340  00024010  00003800
0015  .comment          1             00000000  00024043  00000031
0016  .debug_info       1             00000000  00024074  0000dbf7
0017  .debug_abbrev     1             00000000  00031c6b  00002d96
0018  .debug_aranges    1             00000000  00034a08  000003b8
0019  .debug_macro      1             00000000  00034dc0  000036f8
0020  .debug_line       1             00000000  000384b8  0000493d
0021  .debug_str        1             00000000  0003cdf5  0000ff5f
0022  .debug_frame      1             00000000  0004cd54  00000ad4
0023  .debug_loc        1             00000000  0004d828  00002d99
0024  .debug_ranges     1             00000000  000505c1  00000120
0025  .symtab           2             00000000  000506e4  00002f80
0026  .strtab           3             00000000  00053664  00001a65
0027  .shstrtab         3             00000000  000550c9  0000010f
```


## 探究LOAD地址

- zynq制作BOOT.bin生成的 **output.bif** 文件。
```cpp
//arch = zynq; split = false; format = BIN
the_ROM_image:
{
    [bootloader]E:\Xilinx_SDK\BF_Zynq7010\spiflash\fsbl.elf
    E:\Xilinx_SDK\BF_Zynq7010\spiflash\bf_top.bit
    E:\Xilinx_SDK\BF_Zynq7010\spiflash\u-boot.elf
    [load = 0x1000000]E:\Xilinx_SDK\BF_Zynq7010\spiflash\devicetree.dtb
    [load = 0x800000]E:\Xilinx_SDK\BF_Zynq7010\spiflash\uramdisk.image.gz
    [load = 0x1200000]E:\Xilinx_SDK\BF_Zynq7010\spiflash\uImage
}
```

---

- 上面这个BOOT.BIN打包的文件列表，来源于某个项目，最后3个文件额外设置了load值。于是我直接把当时项目的BOOT.BIN拿到手，然后放到SD卡里，并修改FSBL重新编译后，下载运行FSBL程序，最终串口打印信息如下：
```cpp
../src/main.c:main():243:>> Boot mode is SD
LoadBootImage():296:>> [PL idx:1] LoadAddr = 0x0, ExecAddr = 0x0, imageWLen:0x7f2e8
LoadBootImage():296:>> [PS idx:2] LoadAddr = 0x4000000, ExecAddr = 0x4000000, imageWLen:0x386aa
LoadBootImage():296:>> [PS idx:3] LoadAddr = 0x1000000, ExecAddr = 0x0, imageWLen:0xb92
LoadBootImage():296:>> [PS idx:4] LoadAddr = 0x800000, ExecAddr = 0x0, imageWLen:0x163d10
LoadBootImage():296:>> [PS idx:5] LoadAddr = 0x1200000, ExecAddr = 0x0, imageWLen:0x112178
```

- 在项目中，板子上电之后FSBL只要把u-boot运行起来即可，但在启动u-boot之前，要确保把u-boot以下的其他文件（比如 uImage、设备树、ramdisk）存放到对应的内存地址。因为后续u-boot启动后，u-boot会访问这些地址。

---

- u-boot的入口地址：**0x4000000**，即运行u-boot的第一个函数。
```cpp
elf-read.c:main():234:>> u-boot.elf
e_ident        = 7f 45 4c 46 01 01 01 61 00 00 00 00 00 00 00 00
e_type         = 0x2 (ET_REL=1 xxx.o, ET_EXEC=2, ET_DYN=3 xxx.so)
e_machine      = 0x28
e_version      = 0x1
e_entry        = 0x4000000
e_phoff        = 0x34
e_shoff        = 0xf1b88
e_flags        = 0x0
e_ehsize       = 0x34
e_phentsize    = 0x20
e_phnum        = 0x1
e_shentsize    = 0x28
e_shnum        = 0x5
e_shstrndx     = 0x4
----------------------------------------------------------------------
idx   sename            sectype       secaddr   secoffset  secsize
----------------------------------------------------------------------
0000                    0             00000000  00000000  00000000
0001  .data             1             04000000  00010000  000e1aa7
0002  .symtab           2             00000000  000f1aa8  00000070
0003  .strtab           3             00000000  000f1b18  0000004c
0004  .shstrtab         3             00000000  000f1b64  00000021


----------------------------------------------------------------------
$ readelf.exe -S u-boot.elf
There are 5 section headers, starting at offset 0xf1b88:

Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .data             PROGBITS        04000000 010000 0e1aa7 00  WA  0   0  1
  [ 2] .symtab           SYMTAB          00000000 0f1aa8 000070 10      3   3  4
  [ 3] .strtab           STRTAB          00000000 0f1b18 00004c 00      0   0  1
  [ 4] .shstrtab         STRTAB          00000000 0f1b64 000021 00      0   0  1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings)
  I (info), L (link order), G (group), T (TLS), E (exclude), x (unknown)
  O (extra OS processing required) o (OS specific), p (processor specific)
```



## 探究BOOT.BIN

**Abstract**

- zynq-standalone = fsbl.elf + hw.bit + hello.elf
- zynq-linux = (fsbl+bit) + u-boot.elf + uImage + uramdisk.image.gz + system-top.dtb
- Run PS: ps.cpu.pc = elf.entry.addr (PC pointer)
- Run PL: slcr

---

- excalidraw-url: https://excalidraw.com/
- excalidraw-data: [[ZYNQ-BOOT.BIN.Layout.excalidraw.json]]
- excalidraw-uage: Copy the data from the json file and paste it on the page where the URL is loaded.

![[image_20240821151636.png]]


## 探究ELF哪些节需要加载到内存

- 参考代码: https://elixir.bootlin.com/linux/v4.0/source/kernel/module.c
- 参考函数: load_module

---

- **Elf_Ehdr**：首先拷贝获取到ELF头信息。

```cpp
/* Sets info->hdr and info->len. */
static int copy_module_from_user(const void __user *umod, 
    unsigned long len, struct load_info *info)
{
    info->len = len;

    /* Suck in entire file: we'll want most of it. */
    info->hdr = __vmalloc(info->len, GFP_KERNEL | __GFP_NOWARN);
    copy_chunked_from_user(info->hdr, umod, info->len);
    return err;
}
```

---

- 如下代码所示，上面是从内核代码摘下来简化的核心伪代码，目的是探究内核模块需要把哪些sections弄到内核里，以方便后续使用。跟踪到最后，发现 move_module 函数是核心位置，它的实现基本描述了哪些sections需要弄到内核里。从上述代码中能看到，首先需要满足 **SHF_ALLOC**，然后排除 **SHT_NOBITS**，然后把这两个条件，代入到前面ELF探究的小节验证，果然是这样的，因此ELF文件需要拷贝哪些内容到内存，就是根据这两个条件来确定的。

```cpp
static int move_module(struct module *mod, struct load_info *info)
{
    void *ptr;

    /* Do the allocs. */
    ptr = module_alloc(mod->core_layout.size);

    memset(ptr, 0, mod->core_layout.size);
    mod->core_layout.base = ptr;

    /* Do the allocs. */
    ptr = vzalloc(mod->data_layout.size);
    mod->data_layout.base = ptr;
    
    /* Transfer each section which specifies SHF_ALLOC */
    pr_debug("final section addresses:\n");
    for (i = 0; i < info->hdr->e_shnum; i++) {
        void *dest;
        Elf_Shdr *shdr = &info->sechdrs[i];

        if (!(shdr->sh_flags & SHF_ALLOC))
            continue;

        if (shdr->sh_entsize & INIT_OFFSET_MASK)
            dest = mod->init_layout.base
                + (shdr->sh_entsize & ~INIT_OFFSET_MASK);
        else if (!(shdr->sh_flags & SHF_EXECINSTR))
            dest = mod->data_layout.base + shdr->sh_entsize;
        else
            dest = mod->core_layout.base + shdr->sh_entsize;

        if (shdr->sh_type != SHT_NOBITS)
            memcpy(dest, (void *)shdr->sh_addr, shdr->sh_size);
        /* Update sh_addr to point to copy in image. */
        shdr->sh_addr = (unsigned long)dest;
        pr_debug("\t0x%lx %s\n",
             (long)shdr->sh_addr, info->secstrings + shdr->sh_name);
    }
}
```

- **sh_name**，4字节，是一个索引值，在shstrtable（section header string table，包含section name的字符串表，也是一个section）中的索引。第二讲介绍ELF文件头时，里面专门有一个字段e_shstrndx，其含义就是shstrtable对应的section header在section header table中的索引。
- **sh_type**，4字节，描述了section的类型，常见的取值如下：
  - SHT_NULL 0，表明section header无效，没有关联的section。
  - **SHT_PROGBITS** 1，section包含了程序需要的数据，格式和含义由程序解释。
  - **SHT_SYMTAB** 2， 包含了一个符号表。当前，一个ELF文件中只有一个符号表。SHT_SYMTAB提供了用于(link editor)链接编辑的符号，当然这些符号也可能用于动态链接。这是一个完全的符号表，它包含许多符号。
  - **SHT_STRTAB** 3，包含一个字符串表。一个对象文件包含多个字符串表，比如.strtab（包含符号的名字）和.shstrtab（包含section的名称）。
  - **SHT_RELA** 4，重定位节，包含relocation入口，参见Elf32_Rela。一个文件可能有多个Relocation Section。比如.rela.text，.rela.dyn。
  - SHT_HASH 5，这样的section包含一个符号hash表，参与动态连接的目标代码文件必须有一个hash表。目前一个ELF文件中只包含一个hash表。讲链接的时候再细讲。
  - **SHT_DYNAMIC** 6，包含动态链接的信息。目前一个ELF文件只有一个DYNAMIC section。
  - **SHT_NOBITS** 8，这种section不含字节，也不占用文件空间，section header中的sh_offset字段只是概念上的偏移。
  - **SHT_REL** 9， 重定位节，包含重定位条目。和SHT_RELA基本相同，两者的区别在后面讲重定位的时候再细讲。
  - SHT_DYNSYM 11， 用于动态连接的符号表，推测是symbol table的子集。
- **sh_flags**, 32位占4字节， 64位占8字节。包含位标志，用 readelf -S <elf> 可以看到很多标志。常用的有：
  - SHF_WRITE 0x1，进程执行的时候，section内的数据可写。
  - **SHF_ALLOC** 0x2，进程执行的时候，section需要占据内存。
  - **SHF_EXECINSTR** 0x4，节内包含可以执行的机器指令。
  - **SHF_STRINGS** 0x20，包含0结尾的字符串。
- **sh_addr**, 对32位来说是4字节，64位是8字节。如果section会出现在进程的内存映像中，给出了section第一字节的虚拟地址。
- **sh_offset**，在ELF文件中的偏移，可用 `lseek(fd, sh_offset, SEEK_SET)` 定位到。


---


## 探究symtab和strtab

- 下面代码片段参考自Linux内核模块管理相关代码，它们是关于如何访问symtab和strtab的核心代码。
```cpp
mod->kallsyms->symtab = (void *)symsec->sh_addr;
mod->kallsyms->num_symtab = symsec->sh_size / sizeof(Elf_Sym);

/* Find internal symbols and strings. */
for (i = 1; i < info->hdr->e_shnum; i++) {
    if (info->sechdrs[i].sh_type == SHT_SYMTAB) {
        info->index.sym = i;
        info->index.str = info->sechdrs[i].sh_link;
        info->strtab = (char *)info->hdr
                + info->sechdrs[info->index.str].sh_offset;
        break;
    }
}

if (info->index.sym == 0) {
    pr_warn("%s: module has no symbols (stripped?)\n",
            info->name ?: "(missing .modinfo section or name field)");
    return -ENOEXEC;
}

static const char *kallsyms_symbol_name(struct mod_kallsyms *kallsyms, unsigned int symnum)
{
    //strtab + symtab[symnum].st_name
    return kallsyms->strtab + kallsyms->symtab[symnum].st_name;
}
```

---

- 下面是section访问的接口代码，来自Linux内核模块管理，先搜藏起来以可以用在其他需要的地方。
```cpp
/* Find a module section: 0 means not found. */
static unsigned int find_sec(const struct load_info *info, const char *name)
{
    unsigned int i;

    for (i = 1; i < info->hdr->e_shnum; i++) {
            Elf_Shdr *shdr = &info->sechdrs[i];
            /* Alloc bit cleared means "ignore it." */
            if ((shdr->sh_flags & SHF_ALLOC)
                && strcmp(info->secstrings + shdr->sh_name, name) == 0)
                    return i;
    }
    return 0;
}

/* Find a module section, or NULL. */
static void *section_addr(const struct load_info *info, const char *name)
{
        /* Section 0 has sh_addr 0. */
        return (void *)info->sechdrs[find_sec(info, name)].sh_addr;
}

/* Find a module section, or NULL.  Fill in number of "objects" in section. */
static void *section_objs(const struct load_info *info,
                          const char *name,
                          size_t object_size,
                          unsigned int *num)
{
        unsigned int sec = find_sec(info, name);

        /* Section 0 has sh_addr 0 and sh_size 0. */
        *num = info->sechdrs[sec].sh_size / object_size;
        return (void *)info->sechdrs[sec].sh_addr;
}

/* Find a module section: 0 means not found. Ignores SHF_ALLOC flag. */
static unsigned int find_any_sec(const struct load_info *info, const char *name)
{
        unsigned int i;

        for (i = 1; i < info->hdr->e_shnum; i++) {
                Elf_Shdr *shdr = &info->sechdrs[i];
                if (strcmp(info->secstrings + shdr->sh_name, name) == 0)
                        return i;
        }
        return 0;
}
```


## 探究ELF入口函数和链接地址

1. The code below is the full hello.c code.
```cpp {.line-numbers}
int hello_mul(int a, int b)
{
    return (a*b);
}

int hello_add(int a, int b)
{
    return (a+b);
}

void hello_cal(void)
{
    int a = 10;
    int b = 20;
    int c = hello_add(a, b);
    int d = hello_mul(a, b);
}
```

---

02. Entrypoint function of executable program is **hello_cal**, and Address of ".text" is **0x40000000**.
```bash
# Specify the entry point function as hello_cal, 
# and specify the first address of the code section as 0x40000000.
gcc -o hello.elf hello.c -nostdlib -e hello_cal -Ttext 0x40000000

readelf -S hello.elf
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .text             PROGBITS        40000000 008000 0000a4 00  AX  0   0  4

readelf -h hello.elf 
ELF Header:
  Magic:   7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF32
  Data:                              2's complement, little endian
  OS/ABI:                            UNIX - System V
  Type:                              EXEC (Executable file)
  Machine:                           ARM
  Version:                           0x1
  Entry point address:               0x40000060  <--------<hello_cal>
  Start of program headers:          52 (bytes into file)
  Start of section headers:          33104 (bytes into file)
  Flags:                             0x5000002, has entry point, Version5 EABI
  Number of section headers:         7
  Section header string table index: 4
```

---

1.  By disassembling the code, you can see that the function **hello_mul** is **0x40000000** at the first address of the code section. And through the above **ELF** information, we can see that the size of the code section is 0xa4 (164) bytes, and we can directly count the number of instruction lines of each function of the disassembly code section, and we can verify that the code section size is indeed 164 bytes. And in the disassembly code, where the function is called, the jump instruction is directly to the determined address.

```bash
objdump -D -S hello.elf > hello.dump.S
objdump -D -S --section=".text" hello.elf > hello.dump.S
```

---

04. Here's the full disassembly code for the code section:
```cpp {.line-numbers}
hello.elf:     file format elf32-littlearm

Disassembly of section .text:

40000000 <hello_mul>:
40000000:    e52db004     push    {fp}        ; (str fp, [sp, #-4]!)
40000004:    e28db000     add    fp, sp, #0
40000008:    e24dd00c     sub    sp, sp, #12
4000000c:    e50b0008     str    r0, [fp, #-8]
40000010:    e50b100c     str    r1, [fp, #-12]
40000014:    e51b3008     ldr    r3, [fp, #-8]
40000018:    e51b200c     ldr    r2, [fp, #-12]
4000001c:    e0030392     mul    r3, r2, r3
40000020:    e1a00003     mov    r0, r3
40000024:    e28bd000     add    sp, fp, #0
40000028:    e8bd0800     ldmfd    sp!, {fp}
4000002c:    e12fff1e     bx    lr

40000030 <hello_add>:
40000030:    e52db004     push    {fp}        ; (str fp, [sp, #-4]!)
40000034:    e28db000     add    fp, sp, #0
40000038:    e24dd00c     sub    sp, sp, #12
4000003c:    e50b0008     str    r0, [fp, #-8]
40000040:    e50b100c     str    r1, [fp, #-12]
40000044:    e51b2008     ldr    r2, [fp, #-8]
40000048:    e51b300c     ldr    r3, [fp, #-12]
4000004c:    e0823003     add    r3, r2, r3
40000050:    e1a00003     mov    r0, r3
40000054:    e28bd000     add    sp, fp, #0
40000058:    e8bd0800     ldmfd    sp!, {fp}
4000005c:    e12fff1e     bx    lr

40000060 <hello_cal>:
40000060:    e92d4800     push    {fp, lr}
40000064:    e28db004     add    fp, sp, #4
40000068:    e24dd010     sub    sp, sp, #16
4000006c:    e3a0300a     mov    r3, #10
40000070:    e50b3008     str    r3, [fp, #-8]
40000074:    e3a03014     mov    r3, #20
40000078:    e50b300c     str    r3, [fp, #-12]
4000007c:    e51b0008     ldr    r0, [fp, #-8]
40000080:    e51b100c     ldr    r1, [fp, #-12]
40000084:    ebffffe9     bl    40000030 <hello_add>
40000088:    e50b0010     str    r0, [fp, #-16]
4000008c:    e51b0008     ldr    r0, [fp, #-8]
40000090:    e51b100c     ldr    r1, [fp, #-12]
40000094:    ebffffd9     bl    40000000 <hello_mul>
40000098:    e50b0014     str    r0, [fp, #-20]
4000009c:    e24bd004     sub    sp, fp, #4
400000a0:    e8bd8800     pop    {fp, pc}
```


## 探究eclipse工程编译

- eclipse-like-makefile
- eclipse编译工程的时候，会自动生成一个Debug目录，这个目录与源码目录分开，编译产生的中间文件不会污染源码目录，并且 Debug 目录下的子目录树和 src 目录里的目录树一模一样，并且 Debug 里面每个子目录下都有 subdir.mk 文件，用来生成当前目录下对应的.o文件。当src目录以及其子目录新增源文件时，或者新增/删减子目录或者源文件时，Debug 目录在编译时都会自动更新。

---

- 下面的目录树和注释，整个工程的编译链接，是基于顶层Makefile进行构建，因此相对路径也是基于顶层Makefile。
- hello/
  - src/
    - math/
      - add.c
      - sub.c
    - main.c
  - debug/
    - objects.mk
    - sources.mk
    - Makefile —— 变量初始化, 文件包含, 最终目标生成语句，最终输出一个可执行文件.
    - main.o
    - math/
      - subdir.mk —— 负责本子目录的.o文件的生成
      - add.o
      - sub.o

---

- subdir.mk
```makefile
LD_SRCS += \
../src/lscript.ld 

C_SRCS += \
../src/helloworld.c \
../src/platform.c 

OBJS += \
./src/helloworld.o \
./src/platform.o 

C_DEPS += \
./src/helloworld.d \
./src/platform.d 


# Each subdirectory must supply rules for building sources it contributes
src/%.o: ../src/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM v7 gcc compiler'
	arm-none-eabi-gcc -Wall -O0 -g3 -c \
            -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard \
            -I../../hello_bsp/ps7_cortexa9_0/include -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '
```

---

- objects.mk
```makefile
USER_OBJS :=
LIBS := -Wl,--start-group,-lxil,-lgcc,-lc,--end-group
```

---

- sources.mk
```makefile
LD_SRCS := 
OBJ_SRCS := 
S_SRCS := 
C_SRCS := 
S_UPPER_SRCS := 
O_SRCS := 
EXECUTABLES := 
OBJS := 
S_UPPER_DEPS := 
C_DEPS := 
ELFSIZE := 

# Every subdirectory with source files must be described here
SUBDIRS := \
src \
```

---

- Makefile
```makefile
RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include src/subdir.mk
-include subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(S_UPPER_DEPS)),)
-include $(S_UPPER_DEPS)
endif
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
endif

-include ../makefile.defs

# Add inputs and outputs from these tool invocations to the build variables 
ELFSIZE += \
hello.elf.size \


# All Target
all: pre-build main-build

# Main-build Target
main-build: hello.elf secondary-outputs

# Tool invocations
hello.elf: $(OBJS) ../src/lscript.ld $(USER_OBJS)
	@echo 'Building target: $@'
	@echo 'Invoking: ARM v7 gcc linker'
	arm-none-eabi-gcc -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard \
    -Wl,-build-id=none -specs=Xilinx.spec \
    -Wl,-T -Wl,../src/lscript.ld \
    -L../../hello_bsp/ps7_cortexa9_0/lib -o "hello.elf" $(OBJS) $(USER_OBJS) $(LIBS)
	@echo 'Finished building target: $@'
	@echo ' '

hello.elf.size: hello.elf
	@echo 'Invoking: ARM v7 Print Size'
	arm-none-eabi-size hello.elf  |tee "hello.elf.size"
	@echo 'Finished building: $@'
	@echo ' '

# Other Targets
clean:
	-$(RM) $(EXECUTABLES)$(OBJS)$(S_UPPER_DEPS)$(C_DEPS)$(ELFSIZE) hello.elf
	-@echo ' '

pre-build:
	-a9-linaro-pre-build-step
	-@echo ' '

secondary-outputs: $(ELFSIZE)

.PHONY: all clean dependents
.SECONDARY: main-build pre-build

-include ../makefile.targets
```

---

- my_top_makefile
```makefile
# Variable values can be set by the user
OUTPUT_PROGRAM  ?= demo_main
FLAGS_EXTERNAL  ?= 
CROSS_COMPILER  ?= 

# These variables are automatically generated
AS           = $(CROSS_COMPILER)as
LD           = $(CROSS_COMPILER)ld
CC           = $(CROSS_COMPILER)gcc
CPP          = $(CC) -E
AR           = $(CROSS_COMPILER)ar
NM           = $(CROSS_COMPILER)nm
STRIP        = $(CROSS_COMPILER)strip
OBJCOPY      = $(CROSS_COMPILER)objcopy
OBJDUMP      = $(CROSS_COMPILER)objdump
FILE_SRCS   := 
FILE_OBJS   := 
TARGET_ELF  := $(OUTPUT_PROGRAM).elf
TARGET_HEX  := $(OUTPUT_PROGRAM).hex
TARGET_BIN  := $(OUTPUT_PROGRAM).bin
TARGET_ASM  := $(OUTPUT_PROGRAM).asm
RM          := rm -rf 

FILE_SRCS += \
    ../src/myudp.c \
    ../src/demo_send.c \
    ../src/math/add.c \
    ../src/math/accelerate/speed_up.S \

FILE_OBJS += \
    ./src/myudp.o \
    ./src/demo_send.o \
    ./src/math/add.o \
    ./src/math/accelerate/speed_up.o \


./src/%.o: ../src/%.c
	$(CC) -c -o "$@" "$<" $(FLAGS_EXTERNAL)
./src/math/%.o: ../src/math/%.c
	$(CC) -c -o "$@" "$<" $(FLAGS_EXTERNAL)
./src/math/accelerate/%.o: ../src/math/accelerate/%.S
	$(CC) -c -o "$@" "$<" $(FLAGS_EXTERNAL)

# All Target
all: $(TARGET_ELF) $(TARGET_HEX) $(TARGET_BIN) $(TARGET_ASM)

# Tool invocations
$(TARGET_ELF): $(FILE_OBJS)
	$(CC) -o $(TARGET_ELF) $(FILE_OBJS) $(FLAGS_EXTERNAL)

$(TARGET_HEX): $(TARGET_ELF)
	$(OBJCOPY) -O ihex "$(TARGET_ELF)"  "$(TARGET_HEX)"

$(TARGET_BIN): $(TARGET_ELF)
	$(OBJCOPY) -O binary "$(TARGET_ELF)"  "$(TARGET_BIN)"

$(TARGET_ASM): $(TARGET_ELF)
	$(OBJDUMP) -D -S "$(TARGET_ELF)" > "$(TARGET_ASM)"

clean:
	-$(RM) $(FILE_OBJS) $(TARGET_ELF) $(TARGET_HEX) $(TARGET_BIN) $(TARGET_ASM)
```

---

- Where `prerequisites` represent dependencies, and `prerequisites` can be nested in layers. For example, in the above AAA example, the meaning of nesting is that the AAA depends on the BBB, and the BBB can be the `Target` of the inner layer, and so on.
- The basic format of `Makefile` is as follows:
```makefile
target1 ...: prerequisites ...
	# Note that you need to add a tab key before the command
	command
	...
target2 ...: prerequisites ...
	command

BBB: DDD EEE
	command222
CCC: FFF
	command333
AAA: BBB CCC
	command111
```

---

- As shown in the code below, in the case of `=` and `:=`, the use of these two is also related to timing requirements. Where `:=` means that the value is assigned immediately, and then `VAR_B` does not change with the update of `VIR_A` value. But if you use `=`, the value of the variable referencing `VIR_A` is updated to the latest value as `VAR_A` is updated.

```makefile
VAR_A = A
VAR_B = $(VAR_A) B
VAR_A = AA
# echo "VAR_B = $(VAR_B)" and then result is VAR_B = AA B

VAR_A := A
VAR_B := $(VAR_A) B
VAR_A := AA
# echo "VAR_B = $(VAR_B)" and then result is VAR_B = A B
```

---


The Eclipse-like Makefile is a small tool that generates a corresponding Makefile based on the source code to facilitate programmers to quickly build a compilation directory. You can contact the author to ask for the source file, and the author needs to go to the network disk to find the `eclipse-like-makefile` keyword file.

Here's a structure of the project directory tree for testing tools: 
```cpp
// Run eclipse-like-makefile
demo-udp
├── build    <------ This dir is automatically generated by the eclipse-like-makefile.
│   ├── Makefile
│   ├── math
│   │   └── console
│   └── src
├── math
│   ├── add.c
│   └── console
│       └── print.c
└── src
    ├── demo_send.c
    ├── myudp.c
    └── myudp.h

linux@vm:~/Desktop/demo-udp$ eclipse-like-makefile.elf build
linux@vm:~/Desktop/demo-udp$ make -C build/
make: Entering directory '/home/linux/Desktop/demo-udp/build'
gcc -c -o "src/myudp.o" "../src/myudp.c" 
gcc -c -o "src/demo_send.o" "../src/demo_send.c" 
gcc -o demo_main.elf  ./src/myudp.o ./src/demo_send.o  
objcopy -O ihex "demo_main.elf"  "demo_main.hex"
objcopy -O binary "demo_main.elf"  "demo_main.bin"
objdump -D -S "demo_main.elf" > "demo_main.asm"
make: Leaving directory '/home/linux/Desktop/demo-udp/build'
linux@vm:~/Desktop/demo-udp$ tree build/
build/
├── demo_main.asm
├── demo_main.bin
├── demo_main.elf
├── demo_main.hex
├── Makefile
└── src
    ├── demo_send.o
    └── myudp.o

1 directory, 7 files
vm:~/Desktop/demo-udp$ 
```

The following `Makefile` file is automatically generated by the `eclipse-like-makefile` program, if you need to modify some parameters semi-permanently, please modify the source code of the program directly. The following is the top-level makefile file in the `build` directory:
```makefile
# Variable values can be set by the user
OUTPUT_PROGRAM  ?= demo_main
FLAGS_EXTERNAL  ?= 
CROSS_COMPILER  ?= 

# These variables are automatically generated
AS           = $(CROSS_COMPILER)as
LD           = $(CROSS_COMPILER)ld
CC           = $(CROSS_COMPILER)gcc
CPP          = $(CC) -E
AR           = $(CROSS_COMPILER)ar
NM           = $(CROSS_COMPILER)nm
STRIP        = $(CROSS_COMPILER)strip
OBJCOPY      = $(CROSS_COMPILER)objcopy
OBJDUMP      = $(CROSS_COMPILER)objdump
FILE_SRCS   := 
FILE_OBJS   := 
TARGET_ELF  := $(OUTPUT_PROGRAM).elf
TARGET_HEX  := $(OUTPUT_PROGRAM).hex
TARGET_BIN  := $(OUTPUT_PROGRAM).bin
TARGET_ASM  := $(OUTPUT_PROGRAM).asm
RM          := rm -rf 


FILE_SRCS += \
    ../src/myudp.c \
    ../src/demo_send.c \
    ../math/add.c \
    ../math/console/print.c \
#<------ The path information here is relative to the build directory.

FILE_OBJS += \
    ./src/myudp.o \
    ./src/demo_send.o \
    ./math/add.o \
    ./math/console/print.o \


./src/%.o: ../src/%.c
	$(CC) -c -o "$@" "$<" $(FLAGS_EXTERNAL)
./math/%.o: ../math/%.c
	$(CC) -c -o "$@" "$<" $(FLAGS_EXTERNAL)
./math/console/%.o: ../math/console/%.c
	$(CC) -c -o "$@" "$<" $(FLAGS_EXTERNAL)


# All Target
all: $(TARGET_ELF) $(TARGET_HEX) $(TARGET_BIN) $(TARGET_ASM)

# Tool invocations
$(TARGET_ELF): $(FILE_OBJS)
	$(CC) -o $(TARGET_ELF) $(FILE_OBJS) $(FLAGS_EXTERNAL)

$(TARGET_HEX): $(TARGET_ELF)
	$(OBJCOPY) -O ihex "$(TARGET_ELF)"  "$(TARGET_HEX)"

$(TARGET_BIN): $(TARGET_ELF)
	$(OBJCOPY) -O binary "$(TARGET_ELF)"  "$(TARGET_BIN)"

$(TARGET_ASM): $(TARGET_ELF)
	$(OBJDUMP) -D -S "$(TARGET_ELF)" > "$(TARGET_ASM)"

clean:
	-$(RM) $(FILE_OBJS) $(TARGET_ELF) $(TARGET_HEX) $(TARGET_BIN) $(TARGET_ASM)
```



Here is the full source code of the `eclipse-like-makefile.c` file:
```cpp
/**
 * @file eclipse-like-makefile.c
 * @author seafly (seafly0616@gmail.com)
 * @brief A gadget similar to Eclipse for generating compiled output directories.
 * @version 20240314
 * @date 2024-03-14
 * @details 
 * 
 * After analyzing the eclipse-like C code compilation link environment, 
 * I imitated the compilation rules of eclipse and 
 * created an independent small tool for generating the corresponding compilation directory. 
 * This allows me to use the gadget to generate the same directory as the Eclipse compilation directory.
 * For example, I analyzed the Xilinx SDK Standalone Hello World template example, 
 * and I analyzed the MounRiver Studio microcontroller bare metal engineering example. 
 * In the example above, 
 * the intermediate process compiles all the source files into the corresponding .o files, 
 * and finally links the .o files into an executable file with the linker script. 
 * 
 * How to use it:
 *  1) gcc eclipse-like-makefile.c -o eclipse-like-makefile.elf
 *  2) sudo cp -rvf eclipse-like-makefile.elf /usr/bin/
 *  3) run eclipse-like-makefile.elf
 * 
 * @copyright Copyright (c) 2024
 * 
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdarg.h>
#include <stdint.h>

#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>

#define MAX_CMD_SIZE 256
#define MAX_PATH_SIZE 256
#define console_error(fmt, ...) fprintf(stderr, fmt, ##__VA_ARGS__);

// The first content of the Makefile file
#define MAKEFILE_HEAD                                 \
    "# Variable values can be set by the user\n"      \
    "OUTPUT_PROGRAM  ?= demo_main\n"                  \
    "FLAGS_EXTERNAL  ?= \n"                           \
    "CROSS_COMPILER  ?= \n"                           \
    "\n"                                              \
    "# These variables are automatically generated\n" \
    "AS           = $(CROSS_COMPILER)as\n"            \
    "LD           = $(CROSS_COMPILER)ld\n"            \
    "CC           = $(CROSS_COMPILER)gcc\n"           \
    "CPP          = $(CC) -E\n"                       \
    "AR           = $(CROSS_COMPILER)ar\n"            \
    "NM           = $(CROSS_COMPILER)nm\n"            \
    "STRIP        = $(CROSS_COMPILER)strip\n"         \
    "OBJCOPY      = $(CROSS_COMPILER)objcopy\n"       \
    "OBJDUMP      = $(CROSS_COMPILER)objdump\n"       \
    "FILE_SRCS   := \n"                               \
    "FILE_OBJS   := \n"                               \
    "TARGET_ELF  := $(OUTPUT_PROGRAM).elf\n"          \
    "TARGET_HEX  := $(OUTPUT_PROGRAM).hex\n"          \
    "TARGET_BIN  := $(OUTPUT_PROGRAM).bin\n"          \
    "TARGET_ASM  := $(OUTPUT_PROGRAM).asm\n"          \
    "RM          := rm -rf \n"

// The last content of the Makefile file
#define MAKEFILE_TAIL                                                \
    "\n\n"                                                           \
    "# All Target\n"                                                 \
    "all: $(TARGET_ELF) $(TARGET_HEX) $(TARGET_BIN) $(TARGET_ASM)\n" \
    "\n"                                                             \
    "# Tool invocations\n"                                           \
    "$(TARGET_ELF): $(FILE_OBJS)\n"                                  \
    "\t$(CC) -o $(TARGET_ELF) $(FILE_OBJS) $(FLAGS_EXTERNAL)\n"      \
    "\n"                                                             \
    "$(TARGET_HEX): $(TARGET_ELF)\n"                                 \
    "\t$(OBJCOPY) -O ihex \"$(TARGET_ELF)\"  \"$(TARGET_HEX)\"\n"    \
    "\n"                                                             \
    "$(TARGET_BIN): $(TARGET_ELF)\n"                                 \
    "\t$(OBJCOPY) -O binary \"$(TARGET_ELF)\"  \"$(TARGET_BIN)\"\n"  \
    "\n"                                                             \
    "$(TARGET_ASM): $(TARGET_ELF)\n"                                 \
    "\t$(OBJDUMP) -D -S \"$(TARGET_ELF)\" > \"$(TARGET_ASM)\"\n"     \
    "\n"                                                             \
    "clean:\n"                                                       \
    "\t-$(RM) $(FILE_OBJS) $(TARGET_ELF) $(TARGET_HEX) $(TARGET_BIN) $(TARGET_ASM)\n\n"

#define check_ret_neexit(ret, expect, fmt, ...)           \
    do                                                    \
    {                                                     \
        if ((ret) != (expect))                            \
        {                                                 \
            fprintf(stderr, "%s():%d: perror -> %s ; ",   \
                    __func__, __LINE__, strerror(errno)); \
            fprintf(stderr, fmt, ##__VA_ARGS__);          \
        };                                                \
    } while (0);

#define check_ret_ltexit(ret, expect, fmt, ...)           \
    do                                                    \
    {                                                     \
        if ((ret) < (expect))                             \
        {                                                 \
            fprintf(stderr, "%s():%d: perror -> %s ; ",   \
                    __func__, __LINE__, strerror(errno)); \
            fprintf(stderr, fmt, ##__VA_ARGS__);          \
        };                                                \
    } while (0);

#define check_ret_eqexit(ret, expect, fmt, ...)           \
    do                                                    \
    {                                                     \
        if ((ret) == (expect))                            \
        {                                                 \
            fprintf(stderr, "%s():%d: perror -> %s ; ",   \
                    __func__, __LINE__, strerror(errno)); \
            fprintf(stderr, fmt, ##__VA_ARGS__);          \
        };                                                \
    } while (0);

static char g_makefile[MAX_PATH_SIZE] = ""; // such as projdir/output-build/Makefile
static char g_makedir[MAX_PATH_SIZE] = "";  // such as projdir/output-build
static char g_findcmd[MAX_CMD_SIZE] = "";

int run_shell(const char *cmd, ...)
{
    int arglen = 0;
    char cmdline[MAX_CMD_SIZE];
    va_list argPtr;
    const char *arg;
    memset(cmdline, 0, sizeof(cmdline));
    strncat(cmdline, cmd, strnlen(cmd, MAX_CMD_SIZE));

    va_start(argPtr, cmd);
    while (1)
    {
        arg = va_arg(argPtr, const char *);
        if ((arg == NULL) || (strnlen(arg, MAX_CMD_SIZE) == 0))
        {
            break;
        }

        arglen = strnlen(arg, MAX_CMD_SIZE);
        if (arglen > (MAX_CMD_SIZE - 1 - strlen(cmdline)))
        {
            arglen = (MAX_CMD_SIZE - 1 - strlen(cmdline));
        }
        strncat(cmdline, arg, arglen);
    }
    va_end(argPtr);

    // printf("cmdline = %s\n", cmdline);
    return system(cmdline);
}

char *path_modsuffix(const char *oldpath, char *newpath, const char *new_suffix)
{
    int suflen = 0;
    memset(newpath, 0, MAX_PATH_SIZE);
    memcpy(newpath, oldpath, MAX_PATH_SIZE);

    int i = strnlen(newpath, MAX_PATH_SIZE);
    while (newpath[i] != '.')
    {
        i--;
    }
    int pos_dot = i;

    int tailLen = 32 < (MAX_PATH_SIZE-1-pos_dot)? 32:(MAX_PATH_SIZE-1-pos_dot);
    memset(&newpath[pos_dot + 1], 0, tailLen);

    suflen = strlen(new_suffix);
    if (suflen > (MAX_PATH_SIZE - 1 - strnlen(newpath, MAX_PATH_SIZE)))
    {
        suflen = (MAX_PATH_SIZE - 1 - strnlen(newpath, MAX_PATH_SIZE));
    }
    strncpy(&newpath[pos_dot], new_suffix, suflen);
    return newpath;
}

char *path_addsuffix(const char *oldpath, char *newpath,
                     const char *suffix)
{
    int suflen = 0;
    memset(newpath, 0, MAX_PATH_SIZE);
    memcpy(newpath, oldpath, MAX_PATH_SIZE);

    suflen = strlen(suffix);
    if (suflen > (MAX_PATH_SIZE - 1 - strnlen(newpath, MAX_PATH_SIZE)))
    {
        suflen = (MAX_PATH_SIZE - 1 - strnlen(newpath, MAX_PATH_SIZE));
    }
    strncat(newpath, suffix, suflen);
    return newpath;
}

char *path_addprefix(const char *oldpath, char *newpath, const char *prefix)
{
    int cplen = 0;
    memset(newpath, 0, MAX_PATH_SIZE);
    strncpy(newpath, prefix, strnlen(prefix, MAX_PATH_SIZE));

    cplen = strnlen(oldpath, MAX_PATH_SIZE);
    if (cplen > (MAX_PATH_SIZE - 1 - strnlen(newpath, MAX_PATH_SIZE)))
    {
        cplen = (MAX_PATH_SIZE - 1 - strnlen(newpath, MAX_PATH_SIZE));
    }

    strncat(newpath, oldpath, cplen);
    return newpath;
}

char *path_dellinebrk(const char *oldpath, char *newpath)
{
    int i = 0;
    memset(newpath, 0, MAX_PATH_SIZE);
    memcpy(newpath, oldpath, MAX_PATH_SIZE);

    while (newpath[i] != '\0')
    {
        if ((newpath[i] == '\r') || (newpath[i] == '\n'))
        {
            newpath[i] = '\0';
        }
        i++;
    }

    memset(&newpath[i], 0, MAX_PATH_SIZE - 1 - i);
    return newpath;
}

// such as "../src/demo_send.c" --> "../src/"
char *path_clearfile(const char *oldpath, char *newpath)
{
    int i = 0;
    memset(newpath, 0, MAX_PATH_SIZE);
    memcpy(newpath, oldpath, MAX_PATH_SIZE);

    int newlen = strnlen(newpath, MAX_PATH_SIZE);

    for (i = newlen; i > 0; i--)
    {
        if (newpath[i] == '/')
        {
            memset(&newpath[i + 1], 0, MAX_PATH_SIZE - 1 - i);
            break;
        }
    }
    return newpath;
}

// if ./src/demo.c --> will get ".c"
const char *path_getsuffix(const char *oripath)
{
    const char *suffix;
    int i = strnlen(oripath, MAX_PATH_SIZE);

    while (1)
    {
        if ( (oripath[i] == '.') || (i==0))
        {
            suffix = &oripath[i];
            break;
        }

        if (i==0)
        {
            suffix = NULL;
            break;
        }
        i--;
    }

    return suffix;
}

int demo_test(void)
{
    char oldpath[MAX_PATH_SIZE];
    char newpath[MAX_PATH_SIZE];
    FILE *fp = NULL;

    fp = popen("find . -name \"*.c\"", "r");
    if (!fp)
    {
        console_error("popen(find) failed, %s\n", strerror(errno));
        return -1;
    }

    /*
        The following loop print looks like this:
        (Current working directory: output)

        objfdir = ./src/
        srcfile = ../src/myudp.c
        objfile = ./src/myudp.o

        objfdir = ./src/
        srcfile = ../src/demo_send.c
        objfile = ./src/demo_send.o

    */
    while (!feof(fp))
    {
        memset(oldpath, 0, sizeof(oldpath));
        fgets(oldpath, sizeof(oldpath), fp);
        if (strlen(oldpath) > 0)
        {
            printf("objfdir = %s\n", path_clearfile(oldpath, newpath));
            printf("srcfile = %s", path_addprefix(oldpath, newpath, "."));
            printf("objfile = %s\n", path_modsuffix(oldpath, newpath, ".o"));
        }
    }

    fclose(fp);
}

int set_makefile_path(const char *outdir)
{
    memset(g_makefile, 0, MAX_PATH_SIZE);
    strncat(g_makefile, outdir, MAX_PATH_SIZE);
    strncat(g_makefile, "/Makefile", strlen("/Makefile"));
    return 0;
}

int generate_MAKEFILE_HEAD(void)
{
    FILE *fp;
    long length = 0;
    const char *makefile = g_makefile;

    fp = fopen(makefile, "wb+");
    check_ret_eqexit(fp, 0, "fopen(%s)\n", makefile);

    length = fwrite(MAKEFILE_HEAD, 1, strlen(MAKEFILE_HEAD), fp);
    check_ret_ltexit(length, 0, "fwrite(%s:MAKEFILE_HEAD)\n", makefile);

    fclose(fp);
    return 0;
}

int generate_MAKEFILE_TAIL(void)
{
    long length = 0;
    const char *makefile = g_makefile;
    FILE *fp = fopen(makefile, "a+");
    check_ret_eqexit(fp, 0, "fopen(%s)\n", makefile);

    length = fwrite(MAKEFILE_TAIL, 1, strlen(MAKEFILE_TAIL), fp);
    check_ret_ltexit(length, 0, "fwrite(%s:MAKEFILE_TAIL)\n", makefile);

    fclose(fp);
    return 0;
}

/**
 * @brief generate findcmd, such as "find . -name '*.[cS]'"
 * 
 * NOTE: Only single-character types are supported now.
 * 
 * @param cmdline will store the command line
 * @param types   single-character types, such as "c", "S"
 * @param ... 
 * @return int 
 */
int generate_findcmd_singlechar(char *cmdline, const char *types, ...)
{
    va_list argptr;
    const char *type;
    strcpy(cmdline, "find . -name '*.?'");
    char *ptr = strchr(cmdline, '*') + 2; //point to '?'

    *ptr = '[';
    *(++ptr) = types[0];

    va_start(argptr, types);
    while (1)
    {
        type = va_arg(argptr, const char *);
        if (type == NULL)
        {
            break;
        }

        *(++ptr) = type[0];
    }
    va_end(argptr);

    *(++ptr) = ']';
    *(++ptr) = '\'';
    // printf("cmdline = %s\n", cmdline);
    return 0;
}

/**
 * @brief generate findcmd, such as find . -name '*.c' -o -name '*.cpp' ...
 * 
 * @param cmdline 
 * @param types "*.c", "*.cpp", "*.S", ...
 * @param ... 
 * @return int 
 */
int generate_findcmd_multichar(char *cmdline, const char *types, ...)
{
    // find . -name '*.c'    -o -name '*.cpp'
    va_list argptr;
    const char *type;
    char subcmd[32] = {0}; // store such as "-o -name '*.cpp'"

    memset(cmdline, 0, MAX_CMD_SIZE);

    // such as "find . -name '"
    strcpy(cmdline, "find . -name '");

    // such as "find . -name '*.c"
    strcat(cmdline, types);

    // such as "find . -name '*.c'"
    strcat(cmdline, "'");

    va_start(argptr, types);
    while (1)
    {
        type = va_arg(argptr, const char *);
        if (type == NULL)
        {
            break;
        }

        // such as "find . -name '*.c' -o -name '"
        strcat(cmdline, " -o -name '");

        // such as "find . -name '*.c' -o -name '*.cpp"
        strcat(cmdline, type);

        // such as "find . -name '*.c' -o -name '*.cpp'"
        strcat(cmdline, "'");
    }
    va_end(argptr);
    // printf("%s():cmdline = %s\n", __func__, cmdline);
    return 0;
}

/*
    This function generates the following content and fills it in the Makefile:

    FILE_SRCS += \
        ../src/myudp.c \
        ../src/demo_send.c

 */
int generate_FILE_SRCS(const char *findcmd)
{
    long len;
    char oldpath[MAX_PATH_SIZE];
    char newpath[MAX_PATH_SIZE];
    FILE *fp = NULL;
    const char *makefile = g_makefile;
    
    // Note in outdir
    fp = popen(findcmd, "r");
    check_ret_eqexit(fp, 0, "popen(%s)\n", findcmd);

    FILE *fp_mk = fopen(makefile, "a+");
    check_ret_eqexit(fp_mk, 0, "fopen(%s)\n", makefile);

    len = fwrite("\n\nFILE_SRCS += \\\n", 1, strlen("\n\nFILE_SRCS += \\\n"), fp_mk);
    check_ret_ltexit(len, 0, "fwrite(%s):FILE_SRCS +=\n", makefile);

    while (!feof(fp))
    {
        memset(oldpath, 0, sizeof(oldpath));

        if (fgets(oldpath, sizeof(oldpath), fp))
        {
            if (strlen(oldpath) > 0)
            {

                path_addprefix(oldpath, newpath, ".");

                path_addprefix(newpath, oldpath, "    ");

                path_dellinebrk(oldpath, newpath);

                path_addsuffix(newpath, oldpath, " \\\n");

                len = fwrite(oldpath, 1, strlen(oldpath), fp_mk);
                check_ret_ltexit(len, 0, "fwrite(%s):%s\n", makefile, oldpath);
            }
        }
    }

    fclose(fp);
    fclose(fp_mk);

    return 0;
}

/*
    This function generates the following content and fills it in the Makefile:

    FILE_OBJS += \
        ./src/myudp.o \
        ./src/demo_send.o

 */
int generate_FILE_OBJS(const char *findcmd)
{
    long len;
    char oldpath[MAX_PATH_SIZE];
    char newpath[MAX_PATH_SIZE];
    FILE *fp = NULL;
    const char *makefile = g_makefile;

    fp = popen(findcmd, "r");
    check_ret_eqexit(fp, 0, "popen(%s)\n", findcmd);

    FILE *fp_mk = fopen(makefile, "a+");
    check_ret_eqexit(fp_mk, 0, "fopen(%s)\n", makefile);

    len = fwrite("\n\nFILE_OBJS += \\\n", 1, strlen("\n\nFILE_OBJS += \\\n"), fp_mk);
    check_ret_ltexit(len, 0, "fwrite(%s):FILE_SRCS +=\n", makefile);

    while (!feof(fp))
    {
        memset(oldpath, 0, sizeof(oldpath));
        if (fgets(oldpath, sizeof(oldpath), fp))
        {
            if (strlen(oldpath) > 0)
            {

                path_modsuffix(oldpath, newpath, ".o");

                path_addprefix(newpath, oldpath, "    ");

                path_dellinebrk(oldpath, newpath);

                path_addsuffix(newpath, oldpath, " \\\n");

                len = fwrite(oldpath, 1, strlen(oldpath), fp_mk);
                check_ret_ltexit(len, 0, "fwrite(%s):%s\n", makefile, oldpath);
            }
        }
    }

    fclose(fp);
    fclose(fp_mk);

    return 0;
}

/*
    Generate Following sentence for Makefile:

    src/%.o: ../src/%.c
        $(CC) -c -o "$@" "$<" $(FLAGS_EXTERNAL)
*/
int generate_COMPILE_TARGET(const char *findcmd)
{
    long len;
    FILE *fp = NULL;
    const char *makefile = g_makefile;

    fp = popen(findcmd, "r");
    check_ret_eqexit(fp, 0, "popen(%s)\n", findcmd);

    FILE *fp_mk = fopen(makefile, "a+");
    check_ret_eqexit(fp_mk, 0, "fopen(%s)\n", makefile);

    char oripath[MAX_PATH_SIZE];
    char objdir[MAX_PATH_SIZE];
    char objobj[MAX_PATH_SIZE];
    char srcdir[MAX_PATH_SIZE];
    char srcdir2[MAX_PATH_SIZE];
    char srcsrc[MAX_PATH_SIZE];
    char history[MAX_PATH_SIZE];
    char suffix[16];
    const char *ptrsuf;

    fwrite("\n\n", 1, strlen("\n\n"), fp_mk);
    while (!feof(fp))
    {
        memset(oripath, 0, sizeof(oripath));

        if (fgets(oripath, sizeof(oripath), fp))
        {

            if (strlen(oripath) > 0)
            {
                path_clearfile(oripath, objdir);
                // oripath == "./src/myudp.c"
                // objdir == "./src/"
                // printf("objdir = %s\n", objdir);

                path_addsuffix(objdir, objobj, "\%.o: ");
                // objobj == "./src/%.o: "

                path_addprefix(objdir, srcdir, ".");
                // srcdir == "../src/"

                path_addsuffix(objobj, srcdir2, srcdir);
                // srcdir2 == "./src/%.o: ../src/"

                memset(suffix, 0, sizeof(suffix));
                suffix[0] = '%'; // %.c or %.S or others
                ptrsuf = path_getsuffix(oripath);
                memcpy(&suffix[1], ptrsuf, strlen(ptrsuf));
                path_addsuffix(srcdir2, srcsrc, suffix);
                // srcsrc == "./src/%.o: ../src/%.c"
                // srcsrc == "./src/%.o: ../src/%.S"

                // skip repeat dir
                if (0 == strncmp(history, srcsrc, strlen(srcsrc)))
                {
                    continue;
                }
                else
                {
                    len = fwrite(srcsrc, 1, strlen(srcsrc), fp_mk);
                    len = fwrite("	$(CC) -c -o \"$@\" \"$<\" $(FLAGS_EXTERNAL)\n", 1,
                                 strlen("	$(CC) -c -o \"$@\" \"$<\" $(FLAGS_EXTERNAL)\n"), fp_mk);

                    memset(history, 0, MAX_PATH_SIZE);
                    strncpy(history, srcsrc, MAX_PATH_SIZE);
                }
            }
        }
    }

    fclose(fp);
    fclose(fp_mk);
    return 0;
}

/**
 * @brief Find all the directories (including subdirectories) that store the source code files in the project, 
 * and then create the same directory tree structure in the [outdir] directory.
 * 
 * Such as following directories tree:
 * demo-udp
 * ├── math                <----------------- source code directory
 * │   ├── add.c
 * │   └── console
 * │       └── print.c
 * ├── src                 <----------------- source code directory
 * |   ├── demo_send.c
 * |   ├── myudp.c
 * |   └── myudp.h
 * └── obj                 <----------------- output directory
 *     ├── demo_main.bin
 *     ├── demo_main.elf
 *     ├── demo_main.hex
 *     ├── Makefile
 *     ├── math
 *     │   ├── add.o
 *     │   └── console
 *     │       └── print.o
 *     └── src
 *         ├── demo_send.o
 *         └── myudp.o
 * 
 * @return int 
 */
int generate_OUTDIR_TREE(const char *findcmd)
{
    FILE *fp = NULL;
    int ret = 0;
    fp = popen(findcmd, "r");
    check_ret_eqexit(fp, 0, "popen(%s)\n", findcmd);

    char oripath[MAX_PATH_SIZE];
    char objdir[MAX_PATH_SIZE];
    char history[MAX_PATH_SIZE];
    char cmdline[MAX_PATH_SIZE];

    while (!feof(fp))
    {
        memset(oripath, 0, sizeof(oripath));
        fgets(oripath, sizeof(oripath), fp);
        if (strlen(oripath) > 0)
        {

            path_clearfile(oripath, objdir);
            // oripath == "./src/myudp.c"
            // objdir == "./src/"

            // skip repeat dir
            if (0 == strncmp(history, objdir, MAX_PATH_SIZE))
            {
                continue;
            }
            else
            {
                strncpy(history, objdir, MAX_PATH_SIZE);
                path_clearfile(g_makefile, g_makedir);
                ret = run_shell("mkdir -p ", g_makedir, objdir, NULL);
                check_ret_neexit(ret, 0, "mkdir -p %s/%s\n", g_makedir, objdir);
            }
        }
    }

    fclose(fp);
    return 0;
}

int main(int argc, char const *argv[])
{
    if (argc == 1)
    {
        console_error("usage: %s  <outdir>\n", argv[0]);
        console_error("  e.g: %s  obj\n", argv[0]);
        console_error("  e.g: %s  build\n", argv[0]);

        console_error("\n\n");
        console_error("such as: %s  build\n", argv[0]);
        console_error("     1. You will see: ./build\n");
        console_error("     2. make all -C ./build\n");
        console_error("     3. make clean -C ./build\n");
        console_error("     4. If you added some source files, enter project top directory and then run %s again.\n", argv[0]);
        return -1;
    }
    int ret = 0;
    const char *outdir = argv[1];
    set_makefile_path(outdir);

    ret = run_shell("rm -rf ", outdir, NULL);
    check_ret_neexit(ret, 0, "rmdir(%s)\n", outdir);

    ret = run_shell("mkdir -p ", outdir, NULL);
    check_ret_neexit(ret, 0, "mkdir -p %s\n", outdir);

    generate_MAKEFILE_HEAD();

    // generate_findcmd_singlechar(g_findcmd, "c", "S", NULL);
    generate_findcmd_multichar(g_findcmd, "*.c", "*.S", NULL);
    generate_FILE_SRCS(g_findcmd);
    generate_FILE_OBJS(g_findcmd);
    generate_COMPILE_TARGET(g_findcmd);
    generate_OUTDIR_TREE(g_findcmd);

    generate_MAKEFILE_TAIL();
    return 0;
}
```


## 探究链接器脚本LMA和VMA

- 大部分情况下，LMA和VMA的值是相等的。

---


链接脚本中 AT> 的作用
https://www.cnblogs.com/LogicBai/p/16982841.html

```cpp
  /* Used by the startup to initialize data */
  _sidata = LOADADDR(.data);

  /* Initialized data sections into "RAM" Ram type memory */
  .data :
  {
    . = ALIGN(4);
    _sdata = .;        /* create a global symbol at data start */
    *(.data)           /* .data sections */
    *(.data*)          /* .data* sections */
    *(.RamFunc)        /* .RamFunc sections */
    *(.RamFunc*)       /* .RamFunc* sections */

    . = ALIGN(4);
    _edata = .;        /* define a global symbol at data end */

  } >RAM AT> FLASH
```

- **显式搬运**：data段的汇编代码，当LMA和VMA不同时，需要用代码显式地搬运:
```cpp
/* Copy the data segment initializers from flash to SRAM */  
  ldr r0, =_sdata
  ldr r1, =_edata
  ldr r2, =_sidata
  movs r3, #0
  b LoopCopyDataInit

CopyDataInit:
  ldr r4, [r2, r3]
  str r4, [r0, r3]
  adds r3, r3, #4

LoopCopyDataInit:
  adds r4, r0, r3
  cmp r4, r1
  bcc CopyDataInit
  
/* Zero fill the bss segment. */
  ldr r2, =_sbss
  ldr r4, =_ebss
  movs r3, #0
  b LoopFillZerobss
```




## 探究Hex文件烧写技术

- 分析下面这个库，利用该库解析.hex文件，并把解析出来的数据，通过网络传递给单片机，单片机收到后，存放到Flash对应的位置，方便下次启动时可以直接从该位置加载程序代码。 https://github.com/sfyip/Intel-HEX-file-parser


# Linux驱动模块管理


## Linux模块加载原理

参考代码: https://elixir.bootlin.com/linux/v4.0/source/kernel/module.c

- insmod是怎么把一个静态驱动程序弄到运行时内核里并执行它？

---

- 任意找一个.ko文件，**可重定向ELF**文件。
```bash
file kernel/drivers/virtio/virtio_input.ko 
virtio_input.ko: ELF 64-bit LSB relocatable, x86-64, version 1 (SYSV) ...
```

---

- 直接跑到源文件的尾部，找一个值得分析的简单函数，于是找到了 **print_modules** 函数。下面贴的代码是经过简化后，整个代码中，我们能轻松知道该函数的功能就是遍历某个链表，然后遍历并打印每个valid节点的模块名称等信息。这里我们Get到一个信息，就是某个链表，代码里有一个 **modules** 链表，而且它不是该函数的局部变量，果断确定它是一个全局链表。
```cpp
//https://elixir.bootlin.com/linux/v4.0/source/kernel/module.c
void print_modules(void)
{
    struct module *mod;
    
    preempt_disable();
    list_for_each_entry_rcu(mod, &modules, list)
    {
        if (mod->state == MODULE_STATE_UNFORMED)
                continue;
        pr_cont(" %s%s", mod->name, module_flags(mod, buf));
    }
    preempt_enable();
}
```

---

- **moudles链表**：这确实是一个全局链表，该链表名字叫 **moudles**, 而且该链表有对应的互斥锁 **mudule_mutex。**
```cpp
//https://elixir.bootlin.com/linux/v4.0/source/kernel/module.c
static DEFINE_MUTEX(module_mutex);
static LIST_HEAD(modules);
```

---

- 上面的函数分析完了，没啥可分析了，好继续从文件底部往上找另一个函数来分析，比如 **`__module_address(addr)`** 函数。里面有两个比较重要的结构体成员。该函数的功能就是根据给定的地址，找到对应的**模块实例**。

```cpp
//https://elixir.bootlin.com/linux/v4.0/source/kernel/module.c
mod->module_init;
mod->module_core;
```

---

04、**section搬运**：下面这个函数是比较核心的代码，该代码的核心功能就是向内核申请一块内存空间，然后存放模块后续要执行的代码，只要是满足 SHF_ALLOC 和 (!SHT_NOBITS) 这两个条件的section，都拷贝到目标地址去。如下代码是精简之后的伪代码，从0号section开始拷贝，一直到遍历完所有sections为止。这里说明一下，0号索引的section是一个空的，相当于在遍历0号索引时没有执行拷贝操作。

```cpp
struct load_info
{
    Elf_Ehdr *hdr;//ELF memory header address(get via vmalloc)
    unsigned long len;//Represents the xxx.ko file size (bytes)
    Elf_Shdr *sechdrs;//section header table
    char *secstrings, *strtab;//section strings and symbol strings
    unsigned long symoffs, stroffs;
    struct
    {
        unsigned int sym, str, mod, vers, info, pcpu;
    } index; //Index values (subscript values) for these named sections.
};

static int move_module(struct module *mod, struct load_info *info)
{
    void *ptr;
    ptr = module_alloc(mod->core_layout.size);
    memset(ptr, 0, mod->core_layout.size);
    
    mod->init_layout.base = ptr;
    
    /* Transfer each section which specifies SHF_ALLOC */
    for (i = 0; i < info->hdr->e_shnum; i++) {
        void *dest;
        Elf_Shdr *shdr = &info->sechdrs[i];
        
        if (!(shdr->sh_flags & SHF_ALLOC))
            continue;
        
        dest = mod->init_layout.base + shdr->sh_entsize;
        
        if (shdr->sh_type != SHT_NOBITS)
            memcpy(dest, (void *)shdr->sh_addr, shdr->sh_size);
        
        /* Update sh_addr to point to copy in image. */
        shdr->sh_addr = (unsigned long)dest;
    }
    
}
```

---

05、**获取sechdrs**：接下来就是探究 `info->sechdrs`，首先要找到哪里给它赋值，然后找到如何从它这里取出想要的section。直接在 module.c 中通过关键字查找 `->sechdrs =`，找到了如下一行。至此，结合ELF相关的知识，就算是基本确定了这个sechdrs的具体信息了。后续直接看它的各种访问方法。
```cpp
info->sechdrs = (void *)info->hdr + info->hdr->e_shoff;
```

---

06、**sechdrs访问函数**：下面是 sechdrs 的各种访问函数，都在 module.c 文件里：
```cpp

/* Find a module section: 0 means not found. */
static unsigned int find_sec(const struct load_info *info, const char *name)
{
        unsigned int i;

        for (i = 1; i < info->hdr->e_shnum; i++) {
                Elf_Shdr *shdr = &info->sechdrs[i];
                /* Alloc bit cleared means "ignore it." */
                if ((shdr->sh_flags & SHF_ALLOC)
                    && strcmp(info->secstrings + shdr->sh_name, name) == 0)
                        return i;
        }
        return 0;
}

/* Find a module section, or NULL. */
static void *section_addr(const struct load_info *info, const char *name)
{
        /* Section 0 has sh_addr 0. */
        return (void *)info->sechdrs[find_sec(info, name)].sh_addr;
}

/* Find a module section, or NULL.  Fill in number of "objects" in section. */
static void *section_objs(const struct load_info *info,
                          const char *name,
                          size_t object_size,
                          unsigned int *num)
{
        unsigned int sec = find_sec(info, name);

        /* Section 0 has sh_addr 0 and sh_size 0. */
        *num = info->sechdrs[sec].sh_size / object_size;
        return (void *)info->sechdrs[sec].sh_addr;
}

/* Find a module section: 0 means not found. Ignores SHF_ALLOC flag. */
static unsigned int find_any_sec(const struct load_info *info, const char *name)
{
        unsigned int i;

        for (i = 1; i < info->hdr->e_shnum; i++) {
                Elf_Shdr *shdr = &info->sechdrs[i];
                if (strcmp(info->secstrings + shdr->sh_name, name) == 0)
                        return i;
        }
        return 0;
}
```



## Linux模块多文件编译

- 源码目录文件列表: 
  - <font color=blue>Makefile main.c add.c build.sh</font>

---

- 多文件编译成一个.ko文件的简单例子如下：
```makefile
KDIR:=/lib/modules/$(shell uname -r)/build
PWD=$(shell pwd)
TARGET=drv_hello  # --> drv_hello.ko
DEPEND=add.o sub.o
obj-m := $(TARGET).o
$(TARGET)-objs:= $(DEPEND)

export CROSS_COMPILE=arm-linux-
export ARCH=arm

all:
	@echo You will generate $(TARGET).ko
	@echo "It depends on:"
	@echo "    $(DEPEND)"
	make -C $(KDIR) M=$(PWD) modules

clean:
	make clean -C $(KDIR) M=$(PWD)
```

- build.sh
```cpp
make TARGET=drv_hello DEPEND=add.o
```

- add.c, sub.c
```cpp
int add(int a, int b)
{
	return a+b;
}
int sub(int a, int b)
{
	return a-b;
}
```

- main.c
```cpp
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/init.h>
#include <linux/kernel.h>   
#include <linux/proc_fs.h>
#include <asm/uaccess.h>
#define BUFSIZE  100


MODULE_LICENSE("Dual BSD/GPL");
MODULE_AUTHOR("Liran B.H");

static int irq=20;
module_param(irq,int,0660);

static int mode=1;
module_param(mode,int,0660);

static struct proc_dir_entry *myproc,*mysym,*mydir,*myfile;

static ssize_t mywrite(struct file *file, const char __user *ubuf, size_t count, loff_t *ppos) 
{
	int num,c,i,m;
	char buf[BUFSIZE];
	if(*ppos > 0 || count > BUFSIZE)
		return -EFAULT;
	if(copy_from_user(buf, ubuf, count))
		return -EFAULT;
	num = sscanf(buf,"%d %d",&i,&m);
	if(num != 2)
		return -EFAULT;
	irq = i; 
	mode = m;
	c = strlen(buf);
	*ppos = c;
	return c;
}

static ssize_t myread(struct file *file, char __user *ubuf,size_t count, loff_t *ppos) 
{
	char buf[BUFSIZE];
	int len=0;
	if(*ppos > 0 || count < BUFSIZE)
		return 0;
	len += sprintf(buf,"irq = %d\n",irq);
	len += sprintf(buf + len,"mode = %d\n",mode);
	
	if(copy_to_user(ubuf,buf,len))
		return -EFAULT;
	*ppos = len;
	return len;
}

#ifdef HAVE_PROC_OPS
static struct proc_ops myops = {
	.owner = THIS_MODULE,
	.proc_read = myread,
	.proc_write = mywrite,
};
#else
static struct file_operations myops = {
	.owner = THIS_MODULE,
	.read = myread,
	.write = mywrite,
};
#endif

static int simple_init(void)
{
    myproc = proc_create("myproc",0660,NULL,&myops);///proc/myproc
    mysym  = proc_symlink("mysym", NULL, "myproc");///proc/mysym -> /proc/myproc
    mydir  = proc_mkdir("mydir", NULL);///proc/mydir
    myfile = proc_create("myfile", 0660, mydir, &myops);///proc/mydir/myfile

    printk(KERN_ALERT "hello %s ...\n", __FILE__);
    return 0;
}

static void simple_cleanup(void)
{
    proc_remove(myproc);
    proc_remove(mysym);

	proc_remove(myfile);
	proc_remove(mydir);
    printk(KERN_ALERT "rmmod %s ...\n", __FILE__);
}

module_init(simple_init);
module_exit(simple_cleanup);
```



## Linux模块参数使用

- 模块传递数组参数：
```cpp
//module->kp;//struct kernel_param
static int data_cnt;
static int data_table[5];
module_param_array(data_table, int, &data_cnt, S_IRUSR);

//数组传参方法: insmod xxx.ko data_table=1,2,3,4,5
//查看参数权限: ls -l /sys/module/parameter/parameters/data_table
//注意：如果我们卸载了该模块再重新加载该模块,我们传入6个成员,则会报错
```

## Linux模块参数原理

- 原理概述：**insmod** 命令把参数字符串化，然后传给内核。内核在模块加载时已经确定了参数的个数，从而可以事先初始化好每个参数对应的 **kernel_param** 结构体实例，并初始化好该模块的总共参数个数。内核空间Get到这一串字符串类型的参数后，开始解析，并识别字符串中每个参数的symbol名称和数据，并把它们保存到自己对应的参数结构体实例中。下面是简化后的探究过程。
```cpp
//https://elixir.bootlin.com/linux/v4.0/source/kernel/module.c
module->kp;//struct kernel_param

//such as insmod hello.ko aaa=111,222,333 bbb="helloworld"
```

---

- 在内核空间的模块管理相关代码里，找不到我们想要的信息，我们想要探究在insmod后面跟随的一大坨参数是怎么传递给内核的。于是直接去网上查找 **insmod** 的源代码，并开始针对性的探究其如何把参数处理并传递给内核空间。
```cpp
//insmod.c
static int do_insmod(int argc, char *argv[])
{
	struct kmod_ctx *ctx;
	struct kmod_module *mod;
	const char *filename;
	char *opts = NULL;
	size_t optslen = 0;

	for (;;) {
		int c, idx = 0;
		c = getopt_long(argc, argv, cmdopts_s, cmdopts, &idx);
		if (c == -1)
			break;
        //...
	}

	filename = argv[optind];

    //insmod hello.ko aaa=111,222 bbb="helloworld"
    //把.ko之后的参数全部以字符串形式拷贝下来
	for (i = optind + 1; i < argc; i++) {
		size_t len = strlen(argv[i]);
		void *tmp = realloc(opts, optslen + len + 2);

		opts = tmp;
		if (optslen > 0) {
			opts[optslen] = ' ';
			optslen++;
		}
		memcpy(opts + optslen, argv[i], len);
		optslen += len;
		opts[optslen] = '\0';
	}

	err = kmod_module_insert_module(mod, flags, opts);
}

KMOD_EXPORT int kmod_module_insert_module(struct kmod_module *mod,
    unsigned int flags,
    const char *options)
{
	const char *args = options ? options : "";
    //...
    err = finit_module(kmod_file_get_fd(mod->file), args, kernel_flags);
    //...
}

static inline int finit_module(int fd, const char *uargs, int flags)
{
    //...
	return syscall(__NR_finit_module, fd, uargs, flags);
}
```

---

- 传递给内核之后，内核开始获取并解析参数字符串，然后存放到 **kernel_param** 这个结构体实例里。
- 模块里面的参数结构和参数个数，都在insmod之后已经确定好了参数个数，因为参数由模块本身决定。
```cpp
struct module {
	/* Kernel parameters. */
	struct kernel_param *kp;
	unsigned int num_kp;
};

static int load_module(struct load_info *info, 
    const char __user *uargs, int flags)
{
	struct module *mod;
	long err;
	...
	mod->args = strndup_user(uargs, ~0UL >> 1);
	...
	parse_args(mod->name, mod->args, mod->kp, mod->num_kp);
	...
}

/* Args looks like "foo=bar,bar2 baz=fuz wiz". */
char *parse_args(const char *doing,
		 char *args,
		 const struct kernel_param *params,
		 unsigned num)
{
	char *param, *val;

	while (*args) {
		args = next_arg(args, &param, &val);
		ret = parse_one(param, val, doing, params, num);
	}

	/* All parsed OK. */
	return NULL;
}
```



## Linux模块卸载原理

模块卸载

- 1, uninstall command: ```rmmod demodev```
- 2, system call: ```long sys_delete_module(const char __user *name_user, unsigned int flags);```
- 3, ```struct module *find_module(const char *name)```
- 4, check dependence of module:
```cpp
    if (!list_empty(&mod->source_list)) {
        /* Other modules depend on us: get rid of them first. */
        ret = -EWOULDBLOCK;
        goto out;
    }
```
- 5, ```static void free_module(struct module *mod);```
  - (1) update status: ```mod->state = MODULE_STATE_UNFORMED;```
  - (2) delete relative list node.
  - (3) free core section memory: ```module_memfree(mod->module_core);```
  - (4) free module param memory: ```destroy_params(mod->kp, mod->num_kp);```
```cpp
module->kp;//struct kernel_param
```

# rt-thread设备管理

## 探究设备对象继承

- 继承原理概述：子寻父，直接访问 **parent** 成员，父寻子，直接用 **rt_container_of** 来获取。
- 基本上设备实例对应的结构体里，都有 parent 成员，它表示该结构体的父类。
```cpp
struct rt_device
{
    struct rt_object parent; /**< inherit from rt_object */
    ...
};

struct rt_serial_device
{
    struct rt_device parent;
    const struct rt_uart_ops *ops;
    ...
};

rt_err_t rt_hw_serial_register(struct rt_serial_device *serial,
                               const char              *name,
                               rt_uint32_t              flag,
                               void                    *data)
{
    rt_err_t ret;
    struct rt_device *device;

    device = &(serial->parent);

    device->ops         = &serial_ops;
    device->user_data   = data;

    /* register a character device */
    ret = rt_device_register(device, name, flag);
    //这里的name,最终会存放到基类的成员 object.name 上。

    return ret;
}
```

---

- 下面代码是跑到容器里面查找，容器是一个数组，数组每个元素就是一类链表，比如设备类，就跑到设备对应的索引下的链表，去遍历链表来查找到对应的设备信息。
```cpp
rt_device_t rt_device_find(const char *name)
{
    return (rt_device_t)rt_object_find(name, RT_Object_Class_Device);
}
RTM_EXPORT(rt_device_find);
```

---

- **插入链表**：串口设备实例注册案例，rt-thread在执行板级初始化时，就会调用 rt_hw_uart_init 函数，该函数的主要功能就是把当前串口的实例注册给系统，简化版的说法，就是把这个实例挂载到某个链表里，在RTT里就是往容器里的设备链表里塞入该实例。
```cpp
static int s3c2440_putc(struct rt_serial_device *serial, char c)
{
    struct hw_uart_device *uart = serial->parent.user_data;

    while (!(readl(uart->hw_base + UTRSTAT_OFS) & (1 << 2))) ;
    writel(uart->hw_base + UTXH_OFS, c);
    return 0;
}

static struct rt_uart_ops s3c2440_uart_ops =
{
    .configure = s3c2440_serial_configure,
    .control = s3c2440_serial_control,
    .putc = s3c2440_putc,
    .getc = s3c2440_getc
};

static struct rt_serial_device _serial0 =
{
    .ops = &s3c2440_uart_ops,
    .config = RT_SERIAL_CONFIG_DEFAULT,
    .serial_rx = NULL,
    .serial_tx = NULL
};

static struct hw_uart_device _hwserial0 =
{
    .hw_base = 0x50000000,
    .irqno = INTUART0
};

int rt_hw_uart_init(void)
{
    /* UART0  UART1 UART2 port configure */
    GPHCON |= 0xAAAA;
    /* PULLUP is disable */
    GPHUP |= 0xFFF;

    /* register UART0 device */
    rt_hw_serial_register(&_serial0, "uart0", \
            RT_DEVICE_FLAG_RDWR | RT_DEVICE_FLAG_INT_RX, &_hwserial0);
    rt_hw_interrupt_install(_hwserial0.irqno, rt_hw_uart_isr, &_serial0, "uart0");
    rt_hw_interrupt_umask(INTUART0);

    return RT_EOK;
}
INIT_BOARD_EXPORT(rt_hw_uart_init);
```

---

![[image_20240829152408.png]]

- 如上图所示，这个全局数组就是容器，数组里每个成员都有一条链表。图中的绿色小方块，也就是对象节点，每个对象节点实例里都有一个list成员，用来作为挂载到链表里的挂载点entry。通过枚举值来标记这些不同类型的链表，比如设备类这个成员，那么它对应的链表里面的节点，就是设备的对象实例。设备注册，就是往该链表里添加节点。
```cpp
//rt-thread-5.0.0/include/rtdef.h
enum rt_object_class_type
{
    RT_Object_Class_Null          = 0x00,      /**< The object is not used. */
    RT_Object_Class_Thread        = 0x01,      /**< The object is a thread. */
    RT_Object_Class_Mutex         = 0x03,      /**< The object is a mutex. */
    RT_Object_Class_Event         = 0x04,      /**< The object is a event. */
    RT_Object_Class_Device        = 0x09,      /**< The object is a device. */
    RT_Object_Class_Module        = 0x0b,      /**< The object is a module. */
};

struct rt_object_information
{
    enum rt_object_class_type type;        /**< object class type */
    rt_list_t object_list; /**< object list */
    rt_size_t object_size; /**< object size */
};

struct rt_object
{
    const char *name;/**< static name of kernel object */
    rt_list_t   list; /**< list node of kernel object */
    ...
};
```

## 探究INIT_EXPORT

- **INIT_EXPORT** 原理摘要：该接口专门把各个模块的初始化函数统一放到某个特定节里，后续的初始化主程序就直接遍历执行这个节里面的初始化函数即可。这样做的好处是每次添加新模块，只会改动新模块自己的代码，无需修改主程序代码。这里的主程序，就是指RTT内核代码。

---

- **获取gcc默认链接器脚本**：通过 `-Wl` 向链接器传递 `--verbose` 参数。使用 gcc 编译的时候指定 --verbose 没有找到链接脚本的内容。搜索了下发现这个参数要传递给 ld 命令，最后确认可以通过 gcc 的 -Wl 选项将 --verbose 参数传递给 linker 来获取。
- **注意**：在gcc命令中向链接器传递的每个参数，都需要用 `-Wl,` 来传递，比如 `-Wl,-Ttext -Wl,0x40000000`。
```bash
gcc hello.c -Wl,--verbose
```

- **代码段见缝插针**：我们查看gcc默认的链接器脚本内容，主要目的是为了过一会儿我们要往代码段里某个子段新增东西，没错，就是我们要把我们自己写的函数插入到指定代码段里。比如下面关键信息 `.data.*` 就给了我们见缝插针的机会。
```cpp
...
  .data           :
  {
    __data_start = . ;
    *(.data .data.* .gnu.linkonce.d.*)
    SORT(CONSTRUCTORS)
  }
...
```

---

- 下面是 hello.c 的完整代码。
- 直接编译运行即可：`gcc hello.c && ./a.out`，可以看到三个函数被调用。
```cpp {.line-numbers}
#include <stdio.h>
#include <stdint.h>

typedef void (*init_fn_t)(void);
#define rt_section(x) __attribute__((section(x)))
#define INIT_EXPORT(fn,level) \
	init_fn_t __rt_init_##fn rt_section(".data.seafly." level) = fn

// setting section boundary
void seafly_func0(void) { }
void seafly_func1(void) { }
void testfn_func1(void) { /* printf("invoke %s\n",__func__); */ }
void testfn_func2(void) { /* printf("invoke %s\n",__func__); */ }
void testfn_func3(void) { /* printf("invoke %s\n",__func__); */ }
INIT_EXPORT(seafly_func0, "0");  //1st of ".data.seafly.0"
INIT_EXPORT(seafly_func1, "1");
INIT_EXPORT(testfn_func1, "0");  //2nd of ".data.seafly.0"
INIT_EXPORT(testfn_func2, "0");  //3th of ".data.seafly.0"
INIT_EXPORT(testfn_func3, "0");  //4th of ".data.seafly.0"

int main(void)
{
	init_fn_t *pfn;
	init_fn_t *pfn_start;
	init_fn_t *pfn_end;

	pfn_start = (init_fn_t *)&__rt_init_seafly_func0; 
	pfn_end   = (init_fn_t *)&__rt_init_seafly_func1;

	for (pfn = pfn_start; pfn < pfn_end; pfn++)
		(*pfn)();

	return 0;
}
```

---

- **疑问1**：INIT_EXPORT 为什么要定义一个变量，而不是直接把函数地址塞到指定section？因为函数已经有属于自己的section了，就是代码段，在程序文件里，symbol有两个信息（名字、地址），而目标函数已经有自己的名字和地址了，而且已经在代码段了。所以我们需要再定义一个变量，并把它放到指定section，用它来存放目标symbol的地址。
- **疑问2**：在主程序中，如何确定或者说如何找到目标section的边界信息？一般情况下，在链接器脚本里会定义某个symbol来存放目标section的开始地址和结束地址，我们在代码中声明一下，然后就能直接引用它。

---


## 探究RTM_EXPORT

- **INIT_EXPORT** 和 **RTM_EXPORT** 的根本区别是，前者是在系统初始化的时候要调用的，而且只调用一次。后者是往某个固定的节里塞入指定模块，比如往 "**RTMSymTab**" 这个节里塞入模块接口，以方便其他模块调用。

```cpp
rt_err_t rt_device_open(rt_device_t dev, rt_uint16_t oflag)
{
    ...
}
RTM_EXPORT(rt_device_open);
```

---

- 其他模块怎么找到这个模块呢？
- 根据 RTMSymTab 关键字全局查找，于是找到 `__rtmsymtab_start` 字样，它是一个全局变量，而 `__rtmsymtab_start` 这个全局变量，在链接器脚本中指定地址。
```cpp
    /* in .text section */
        /* section information for modules */
        . = ALIGN(4);
        __rtmsymtab_start = .;
        KEEP(*(RTMSymTab))
        __rtmsymtab_end = .;
```

```cpp
rt_uint32_t dlmodule_symbol_find(const char *sym_str)
{
    /* find in kernel symbol table */
    struct rt_module_symtab *index;
    for (index = _rt_module_symtab_begin; index != _rt_module_symtab_end; index ++)
    {
        if (rt_strcmp(index->name, sym_str) == 0)
            return (rt_uint32_t)index->addr;
    }
    return 0;
}

int rt_system_dlmodule_init(void)
{
    //#if defined(__GNUC__) && !defined(__CC_ARM)
    extern int __rtmsymtab_start;
    extern int __rtmsymtab_end;
    _rt_module_symtab_begin = (struct rt_module_symtab *)&__rtmsymtab_start;
    _rt_module_symtab_end   = (struct rt_module_symtab *)&__rtmsymtab_end;
    return 0;
}

int demo_test_call(void)
{
    Elf_Sym *symtab = (Elf_Sym *)((rt_uint8_t *)
        module_ptr + shdr[shdr[index].sh_link].sh_offset);
    rt_uint8_t *strtab = (rt_uint8_t *)
        module_ptr + shdr[shdr[shdr[index].sh_link].sh_link].sh_offset;

    //#if (defined(__arm__) || defined(__i386__) || (__riscv_xlen == 32))
    Elf_Sym *sym = &symtab[ELF32_R_SYM(rel->r_info)];
    addr = dlmodule_symbol_find((const char *)(strtab + sym->st_name));
}
```

---

**zynq-xsdk-standalone应用例子**

- RTM_EXPORT 实现代码：
```cpp
#ifndef __RTM_H__
#define __RTM_H__

struct rt_module_symtab
{
    void       *addr;
    const char *name;
};

#define RTM_EXPORT(symbol)                                            \
const char __rtmsym_##symbol##_name[] rt_section(".rodata.name") = #symbol;     \
const struct rt_module_symtab __rtmsym_##symbol rt_section("RTMSymTab")= \
{                                                                     \
    (void *)&symbol,                                                  \
    __rtmsym_##symbol##_name                                          \
};

#endif //__RTM_H__
```

- 修改链接器脚本，在 .text 段末尾添加如下内容：
```cpp
__text_start = .;
.text : {
   KEEP (*(.vectors))
   *(.boot)
   *(.text)
   *(.text.*)
   *(.gnu.linkonce.t.*)
   *(.plt)
   *(.gnu_warning)
   *(.gcc_execpt_table)
   *(.glue_7)
   *(.glue_7t)
   *(.vfp11_veneer)
   *(.ARM.extab)
   *(.gnu.linkonce.armextab.*)

   /* seafly: copy from zynqmp-r5.ld */
   /* section information for modules */
   . = ALIGN(4);
   __rtmsymtab_start = .;
   KEEP(*(RTMSymTab))
   __rtmsymtab_end = .;
} > ps7_ddr_0
__text_end = .;
```


- 在 main 程序中，修改代码，实现模块的插入，以及模块的取出和执行，完整参考代码如下：
```cpp
#include "rtdef.h"
#include "rtm.h"

static uintptr_t _rt_module_symtab_begin = 0;
static uintptr_t _rt_module_symtab_end   = 0;

void module_adder(int a, int b)
{
    xil_printf("%s(%d, %d) = %d\r\n", __func__, a, b, a+b);
}
RTM_EXPORT(module_adder);

void module_print(const char *exinfo)
{
    xil_printf("%s: hello module!!! (%s)\r\n", __func__, exinfo);
}
RTM_EXPORT(module_print);

uint32_t dlmodule_symbol_find(const char *sym_str)
{
    /* find in kernel symbol table */
    struct rt_module_symtab *index;
    for (index = _rt_module_symtab_begin; index != _rt_module_symtab_end; index ++)
    {
        if (strcmp(index->name, sym_str) == 0)
            return (uint32_t)index->addr;
    }
    return 0;
}

int main(int argc, const char *argv[])
{
    init_platform();

    //#if defined(__GNUC__) && !defined(__CC_ARM)
    extern int __rtmsymtab_start;
    extern int __rtmsymtab_end;
    _rt_module_symtab_begin = (struct rt_module_symtab *)&__rtmsymtab_start;
    _rt_module_symtab_end   = (struct rt_module_symtab *)&__rtmsymtab_end;

    xil_printf("_rt_module_symtab_begin = 0x%x\r\n", _rt_module_symtab_begin);
    xil_printf("_rt_module_symtab_end   = 0x%x\r\n", _rt_module_symtab_end  );

    uintptr_t ptr = 0;
    ptr = dlmodule_symbol_find("module_print");
    if (ptr)
    {
        void (*fn_print)(const char *) = (void (*)(const char *))ptr;
        fn_print("call this func with method 1");//call it

        typedef void (*fn_print_t)(const char *);
        fn_print_t fn = (fn_print_t)ptr;
        fn("call this func with method 2");      //call it
    }

    ptr = dlmodule_symbol_find("module_adder");
    if (ptr)
    {
        void (*fn_adder)(int, int) = (void (*)(int, int))ptr;
        fn_adder(100, 200); //call it (method 1)

        typedef void (*fn_adder_t)(int, int);
        fn_adder_t fn = (fn_adder_t)ptr;
        fn(300, 400);       //call it (method 2)
    }

    cleanup_platform();
    return 0;
}
```

- 下载到板子上运行后，串口打印效果：
```c
 dlmodule_symbol_find = 0x100638
&dlmodule_symbol_find = 0x100638
_rt_module_symtab_begin = 0x1019C4
_rt_module_symtab_end   = 0x1019D4
module_print: hello module!!! (call this func with method 1)
module_print: hello module!!! (call this func with method 2)
module_adder(100, 200) = 300
module_adder(300, 400) = 700
```


## 探究section与symbol构成

section与symbol原理概述：
- 不管是section还是symbol，它们都共同有两个属性 **(name, data)** 。
- 为了辅助理解，下面用组和人来举例：
  - 【**男人组**】小明、小刚、小强、... （实实在在的人,symbol.data）
  - 【**女人组**】小红、小霞、小美、... （实实在在的人,symbol.data）
  - 【**姓名组**】"小明"、"小霞"、"小美"、"小红"、"小刚"、"小强"、... (symbol.name)
  - 【**组名组**】"男人组"、"女人组"、"姓名组"、"组名组"、... (section.name)
- 比如定义了一个全局变量：`static int var_aaa = 100;`，变量名 "var_aaa" 就表示symbol.name，而变量的值 100 就表示 symbol.data，这里没有指定section，所以默认放到一个名为 ".data" 的section里。如果显式指定了section，则会追加到这个指定的section里，如果没有该section，就创建它。

---

- **section和symbol**：section翻译为节，程序被分为不同的节，我们以数据节为例，比如下面名为aaa的节，它所管辖的范围内有三个symbol，翻译为符号，每个符号包含两个信息，一个是名字，一个是数据，在程序中，名字单独存放在一个专门存放字符串的节里，这个节通常为 ".strtab" 节，而符号的数据就放在指定的或者默认的节里，比如下面的 var_aaa 是一个全局变量，被放在要给名为 ".data" 的节里，如果没有指定节，根据C语言特性，则默认放到 ".data" 节里。
```cpp
section aaa
    symbol_a (比如说变量var_a所占用的坑位,)
    symbol_b (而变量var_a的名字"var_a"就存放在其他专门存放字符串的section)
    symbol_c
section bbb
    symbol_d
    symbol_e
    symbol_f
```

---

- **symbol的名称和数据**：如下图所示，为了方便理解symbol，暂时认为symbol就是表示变量，下面定义了一个全局变量 var_aaa，其中含有变量名 "var_aaa"，和变量值 100，因此可以得出，变量包含两个信息，一个是名称，一个是数据。
![[image_20240924083429.png]]

```cpp
#define rt_used                     __attribute__((used))
#define rt_section(x)               __attribute__((section(x)))
#define rt_align(x)                 __attribute__((aligned(x)))

// Insert the following variables into ".seafly" section
static rt_used rt_section(".seafly") uint32_t *seafly_data32_start = 0;
static rt_used rt_section(".seafly") uint32_t *seafly_data32_0 = 100;
static rt_used rt_section(".seafly") uint32_t *seafly_data32_1 = 110;
static rt_used rt_section(".seafly") uint32_t *seafly_data32_end = 1;

int main(int argc, char *argv[])
{
	uint32_t *ptr = NULL;
	for (ptr = &seafly_data32_start; ptr <= &seafly_data32_end; ptr++)
		printf("(*ptr) = %d\r\n", (*ptr));
	return 0;
}
// (*ptr) = 0
// (*ptr) = 100
// (*ptr) = 110
// (*ptr) = 1
```


```cpp
//总共存放了4个指针,在32位的ARM里，总共占用16字节
arm-none-eabi-readelf -S rt-thread-demo.elf | findstr "seafly"
Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 6] .seafly           PROGBITS        0010e5c8 01e5c8 000010 00  WA  0   0  4

arm-none-eabi-readelf -s rt-thread-demo.elf | findstr "seafly"
Symbol table '.symtab' contains 724 entries:
   Num:    Value  Size Type    Bind   Vis      Ndx Name
   112: 0010e5c8     4 OBJECT  LOCAL  DEFAULT    6 seafly_data32_start
   113: 0010e5cc     4 OBJECT  LOCAL  DEFAULT    6 seafly_data32_0
   114: 0010e5d0     4 OBJECT  LOCAL  DEFAULT    6 seafly_data32_1
   115: 0010e5d4     4 OBJECT  LOCAL  DEFAULT    6 seafly_data32_end
```


---


## 探究symbol的空间占用

symbol空间占用原理摘要：
- 链接器脚本中对某个symbol的赋值操作就是对symbol的定义行为，汇编中.word symbol就是对symbol的声明行为。
- symbol占用空间大小取决于其类型。

---

- Below we will create two files from scratch, one is the startup file(start.S) and the other is the link script file(link.lds). This is the simplest link instance.

![[image_20240907174737.png]]

- 下面是完整的链接器脚本文件内容：
```cpp
MEMORY
{
    ROM (rx) : ORIGIN = 0x08000000, LENGTH = 128k /* 128KB flash */
    RAM (rw) : ORIGIN = 0x20000000, LENGTH =  20k /* 20K sram */
}

ENTRY(_start)
_lds_system_stack_size = 0x400;

SECTIONS
{
    .text :
    {
        . = ALIGN(4);
        _stext = .;
        *(.text)                        /* remaining code */
        *(.rodata)                      /* read-only data (constants) */
        . = ALIGN(4);
        _etext = .;
    } > ROM = 0

    .data : 
    {
        . = ALIGN(4);
		_lds_data_start = .;
        _sdata = . ;
        *(.data)
        . = ALIGN(4);
        _edata = . ;
    } >RAM

    .stack :
    {
        . = ALIGN(4);
        _sstack = .;
        . = . + _lds_system_stack_size;
        . = ALIGN(4);
        _estack = .;
    } >RAM

    __bss_start = .;
    .bss :
    {
        . = ALIGN(4);
        *(.bss)
    } > RAM
    __bss_end = .;
    _end = .;
}
```

- 下面是 start.S 完整代码：
```cpp
.section .text
.global _start
_start:
	mov lr, pc
	mov r1, #0
	mov r2, #0
	mov pc, lr

.section .data
//Declare a variable called _lds_system_stack_size
.word _lds_system_stack_size 

//Declare a variable called _lds_data_start
.word _lds_data_start
```

- 下面是编译运行测试：
```bash
linux@linux-virtual-machine:~/myrtt$ arm-none-eabi-gcc start.S -T link.lds -o start.elf -nostdlib
linux@linux-virtual-machine:~/myrtt$ arm-none-eabi-readelf -S start.elf 
There are 8 section headers, starting at offset 0x1005c:

Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .text             PROGBITS        08000000 008000 000010 00  AX  0   0  4
  [ 2] .data             PROGBITS        20000000 010000 000008 00  WA  0   0  1
  [ 3] .stack            NOBITS          20000008 010008 000400 00  WA  0   0  1
  [ 4] .ARM.attributes   ARM_ATTRIBUTES  00000000 010008 000014 00      0   0  1
  [ 5] .shstrtab         STRTAB          00000000 01001c 00003e 00      0   0  1
  [ 6] .symtab           SYMTAB          00000000 01019c 000130 10      7   7  4
  [ 7] .strtab           STRTAB          00000000 0102cc 00007c 00      0   0  1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings)
  I (info), L (link order), G (group), T (TLS), E (exclude), x (unknown)
  O (extra OS processing required) o (OS specific), p (processor specific)
linux@linux-virtual-machine:~/myrtt$ 
```



## 探究ELF可执行文件和中间文件

- 下面是对比可执行文件和.o文件的操作记录。从记录中可以看出，中间生成的.o文件，里面存放的sections，其对应的地址都为0，表示这些地址待分配。而生成的可执行文件，各个section的地址都有一个确定值，是可以直接交给CPU的PC指针的值。

```cpp
>>> arm-none-eabi-gcc -c hello.c
>>> arm-none-eabi-readelf -S hello.o 
There are 14 section headers, starting at offset 0x224:
Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .text             PROGBITS        00000000 000034 0000d4 00  AX  0   0  4
  [ 2] .rel.text         REL             00000000 0006a4 000048 08     12   1  4
  [ 3] .data             PROGBITS        00000000 000108 000000 00  WA  0   0  1
  [ 4] .bss              NOBITS          00000000 000108 000000 00  WA  0   0  1
  [ 5] .data.seafly.0    PROGBITS        00000000 000108 000010 00  WA  0   0  4
  [ 6] .rel.data.seafly. REL             00000000 0006ec 000020 08     12   5  4
  [ 7] .data.seafly.1    PROGBITS        00000000 000118 000004 00  WA  0   0  4
  [ 8] .rel.data.seafly. REL             00000000 00070c 000008 08     12   7  4
  [ 9] .comment          PROGBITS        00000000 00011c 000071 01  MS  0   0  1
  [10] .ARM.attributes   ARM_ATTRIBUTES  00000000 00018d 000030 00      0   0  1
  [11] .shstrtab         STRTAB          00000000 0001bd 00006f 00      0   0  1
  [12] .symtab           SYMTAB          00000000 00045c 000180 10     13  13  4
  [13] .strtab           STRTAB          00000000 0005dc 0000c8 00      0   0  1


>>> arm-none-eabi-gcc hello.c -o hello.elf -e main -Ttext 0x40000000 -nostdlib
>>> arm-none-eabi-readelf -S hello.elf 
There are 8 section headers, starting at offset 0x81c0:
Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .text             PROGBITS        40000000 008000 0000d4 00  AX  0   0  4
  [ 2] .data             PROGBITS        400080d4 0080d4 000014 00  WA  0   0  4
  [ 3] .comment          PROGBITS        00000000 0080e8 000070 01  MS  0   0  1
  [ 4] .ARM.attributes   ARM_ATTRIBUTES  00000000 008158 000030 00      0   0  1
  [ 5] .shstrtab         STRTAB          00000000 008188 000040 00      0   0  1
  [ 6] .symtab           SYMTAB          00000000 008308 0001e0 10      7  10  4
  [ 7] .strtab           STRTAB          00000000 0084e8 000121 00      0   0  1


>>> arm-none-eabi-gcc hello.c -o hello.elf \
    -e main -Ttext 0x40000000 -nostdlib -Wl,--verbose
...
  .data           :
  {
    __data_start = . ;
    *(.data .data.* .gnu.linkonce.d.*)
    SORT(CONSTRUCTORS)
  }
...
```

- 由图片可以看出，目标section的大小，跟重定向相关的section没关系。
![[image_20240924080007.png]]


## 探究全局变量同名局部变量

- 两个同名变量，都是静态修饰的，但一个在函数里，一个在函数外。局部那个变量，在其所属函数里被引用时，会先引用局部的这个静态变量。在编译器处理这两个symbol的名字时，会通过给名字添加尾缀来区分两个变量。在实际的 section 中，编译器会将其区分开来，通过地址特征，我们可以进一步确定，两个变量并不是指向同一个地址的变量，这点需要注意。

```cpp
#include <stdio.h>
static int static_data = 10;
int main(int argc, char *argv[])
{
	static int static_data = 1000;
	printf("&static_data = 0x%x, static_data = %d\r\n", &static_data, static_data);
	return 0;
}

readelf -s demo.elf | grep "static_data"
0000000000201010     4 OBJECT  LOCAL  DEFAULT   23 static_data
0000000000201014     4 OBJECT  LOCAL  DEFAULT   23 static_data.3075
```


# QEMU-硬件设备实例


## QEMU设备对象继承

- 继承原理摘要：在qemu中，父子实例的相互转换，是通过首地址类型强转来实现的。

```cpp
//qemu-stable-8.0/hw/char/xilinx_uartlite.c
struct XilinxUARTLite {
    SysBusDevice parent_obj;
    ...
};

struct SysBusDevice {
    /*< private >*/
    DeviceState parent_obj;
    /*< public >*/
    ...
};

struct DeviceState {
    /*< private >*/
    Object parent_obj;
    /*< public >*/
    ...
};

struct Object
{
    /* private: */
    ObjectClass *class;
    ...
    Object *parent;
};
```

---

- **XILINX_UARTLITE** —— 下面的案例就是把基类实例转换成具体的设备结构体实例。
```cpp
#define TYPE_XILINX_UARTLITE "xlnx.xps-uartlite"

#define XILINX_UARTLITE(obj) \
    OBJECT_CHECK(XilinxUARTLite, (obj), TYPE_XILINX_UARTLITE)

#define OBJECT_CHECK(type, obj, name) \
    ((type *)object_dynamic_cast_assert(OBJECT(obj), (name)))

Object *object_dynamic_cast_assert(Object *obj, const char *typename)
{
    return obj;
}

static void xilinx_uartlite_reset(DeviceState *dev)
{
    uart_update_status(XILINX_UARTLITE(dev));
}

static void xilinx_uartlite_init(Object *obj)
{
    XilinxUARTLite *s = XILINX_UARTLITE(obj);

    sysbus_init_irq(SYS_BUS_DEVICE(obj), &s->irq);

    memory_region_init_io(&s->mmio, obj, &uart_ops, s,
                          "xlnx.xps-uartlite", R_MAX * 4);
    sysbus_init_mmio(SYS_BUS_DEVICE(obj), &s->mmio);
}
```




## QEMU设备实例注册

设备实例注册原理摘要：
- 用哈希表来存放硬件设备的句柄实例（实例名，实例数据）。
- 设备各自的初始化函数，都会打包成节点，而后保存在 **init_type_list** 链表里。

---

```cpp
//qemu-stable-8.0/hw/char/xilinx_uartlite.c
static void xilinx_uart_register_types(void)
{
    type_register_static(&xilinx_uartlite_info);
}

type_init(xilinx_uart_register_types)
```

**type_register_static**
- malloc a **TypeImpl** instance
- TypeImpl.elements = TypeInfo.elements (xilinx_uartlite_info)
- `hash_table_insert(ti->name, ti)`

**type_init**
- Wrap the registration function into a node, 
- put it in a linked list, and execute the registration function at a certain stage.
- This linked list is one of the members of the global array `init_type_list[]`.


---


**Details**

```cpp
//qemu-stable-8.0/util/module.c

//MODULE_INIT_QOM is an enum value
#define type_init(function) module_init(function, MODULE_INIT_QOM)

#define module_init(function, type)                                         \
static void __attribute__((constructor)) do_qemu_init_ ## function(void)    \
{                                                                           \
    register_module_init(function, type);                                   \
}

static ModuleTypeList *find_type(module_init_type type)
{
    init_lists();

    return &init_type_list[type];
}

void register_module_init(void (*fn)(void), module_init_type type)
{
    ModuleEntry *e;
    ModuleTypeList *l;

    e = g_malloc0(sizeof(*e));
    e->init = fn;
    e->type = type;

    l = find_type(type);

    QTAILQ_INSERT_TAIL(l, e, node);
}
```

**module_call_init** function is to traverse a specific linked list (**type=index**) and execute a pre-registered function for each hardware module.
```cpp
//qemu/util/module.c
void module_call_init(module_init_type type)
{
    ModuleTypeList *l;
    ModuleEntry *e;
    if (modules_init_done[type]) {
        return;
    }
    l = find_type(type);
    QTAILQ_FOREACH(e, l, node) {
        e->init();
    }
    modules_init_done[type] = true;
}
```



# 代码与对象对应

## 探究结构体成员指针类型

- 如下所示，各种结构体成员都不可避免有指针类型。首先我们已经知道，指针变量的作用就是用来存放地址，而且指针变量自己也有地址，这两者别搞混就行。
```cpp
struct kset {
	struct list_head list;
	spinlock_t list_lock;
	struct kobject kobj;
	const struct kset_uevent_ops *uevent_ops;
};

struct kobject {
	const char		*name;
	struct list_head	entry;
	struct kobject		*parent;
	struct kset		*kset;
	struct kobj_type	*ktype;

	unsigned int state_initialized:1;
	unsigned int state_in_sysfs:1;
	unsigned int state_add_uevent_sent:1;
	unsigned int state_remove_uevent_sent:1;
	unsigned int uevent_suppress:1;
};
```

- object.c
- bus.c
- module.c
- 通过快速查看上述几个源文件的所有代码，主要关注它们对结构体成员指针类型的引用访问（通过搜索高亮 `->` 来快速浏览）。这里为了方便我们推演理解，我们有如下几种假设，并根据假设构造使用场景。
- 假设某结构体所有成员都不是指针类型
- 假设某结构体所有成员都是指针类型
- 假设某结构体所有成员两者类型都有。


```txt
交通工具
    车子
        机动车
            公交车
            小轿车
            货运车
            客运车
        非机动车
            自行车
            电瓶车
    飞机
        直升机
        客运机
    火车
        绿皮
        高铁

用户要出行了（用户程序），用户要坐交通工具出行。
用户调用 ---> 驱动程序 ---> 具体设备


机动车
    构造:类型、车窗、车门、车轮、车灯、...
    操作
        点火（每种机动车都有点火操作，只不过不同品牌操作略有区别）
        熄火
        加速
        鸣笛
        刹车
```



## 二级指针传参


- 如下图所示，无论是几级指针，它的一级引用（一颗星）都是指向这个整体的首地址，所以利用这个特点，我们在尤其函数参数传递复杂多级指针时，都可以用一级指针来传递。下面的代码就是例子。

![[image_20240929104548.png]]

```cpp
#include <stdio.h>

/**
 *
 * @param xys     传进多个xy
 * @param xycnt   有多少个xy
 * @param rowcnt  xy里有多少个y，即多少行
 * @param columncnt y里有多少个x，即一行里有多少列
 */
void test_arrays(void *xys, int xycnt, int rowcnt, int columncnt)
{
	int *data_xys = (int *)xys;
	int *data_xy;
	int *data_y;

	for (int xyidx=0; xyidx<xycnt; xyidx++)
	{
		data_xy = &data_xys[xyidx * (rowcnt * columncnt)];

		for (int y=0; y<rowcnt; y++)
		{
			data_y = &data_xy[y*columncnt];
			for (int x=0; x<columncnt; x++)
			{
				printf("%d, ", data_y[x]);
			}
			printf("\n");
		}
		printf("\n");
	}
}

int main(void)
{
	int arrays[][3][3] = {
        {
            { 100, 110, 120 },
            { 130, 140, 150 },
            { 160, 170, 180 },
        },
        {
            { 200, 210, 220 },
            { 230, 240, 250 },
            { 260, 270, 280 },
        },
        {
            { 300, 310, 320 },
            { 330, 340, 350 },
            { 360, 370, 380 },
        },
        {
            { 400, 410, 420 },
            { 430, 440, 450 },
            { 460, 470, 480 },
        }
	};
	test_arrays((void *)arrays, sizeof(arrays)/sizeof(arrays[0]), 3, 3);
    return 0;
}
```

---

```cpp
#include <stdio.h>

typedef void (*testfunc_t)(void);
void testfunc_1(void) { printf("%s\n", __func__); }
void testfunc_2(void) { printf("%s\n", __func__); }
void testfunc_3(void) { printf("%s\n", __func__); }

void test_arrays(void *funclist, int funccnt)
{
	testfunc_t *funcs = (testfunc_t *)funclist;
	for (int i=0; i<funccnt; i++)
	{
		funcs[[]];
	}
}

int main(void)
{
	unsigned long arrays[] = {
		(unsigned long)&testfunc_1,
		(unsigned long)&testfunc_2,
		(unsigned long)&testfunc_3,
	};
	test_arrays((void *)arrays, sizeof(arrays)/sizeof(arrays[0]));
    return 0;
}
```




## PFP非继承技术

---

- B站：【实例演示】高内聚，低耦合，并不需要“面向对象”技术 —— https://www.bilibili.com/video/BV1sppvesE1T
- PFP技术，就是 `p->f(p)` 技术，其最核心的特点就是结构体首地址强制类型转换。
- 版本3：注释整理
```cpp
#include <stdio.h>

struct led_i;

//LED各自的私有结构体
struct usb_led_data {
    struct led_i *interface;//必须放在首地址
    int state;
    int toggle_count;
    int io_num;
};

//LED各自的私有结构体
struct iic_led_data {
    struct led_i *interface;//必须放在首地址
    int state;
    int toggle_count;
    int address;
};

int usb_led_toggle(struct usb_led_data *self)
{
    printf("toggle usb led (curstate: %d, count: %d\n",
        self->state, self->toggle_count);
        
	//末端设备的功能函数，可以访问自己的结构体成员
	self->toggle_count++;
    self->state = !self->state;
    return 0;
}

int iic_led_toggle(struct iic_led_data *self)
{
    printf("toggle iic led (curstate: %d, count: %d\n",
        self->state, self->toggle_count);
        
	//末端设备的功能函数，可以访问自己的结构体成员
    self->toggle_count++;
    self->state = !self->state;
    return 0;
}







enum {
        IIC_LED_ID = 0,
        USB_LED_ID,
};

typedef int (*led_toggle_fn_t)(struct led_i **self);
struct led_i {
	//每个厂家都有toggle方法,但实现不同
    led_toggle_fn_t toggle;
};

static struct led_i iic_led_interface = {
    .toggle = (led_toggle_fn_t)iic_led_toggle,
};
static struct led_i usb_led_interface = {
    .toggle = (led_toggle_fn_t)usb_led_toggle,
};

//用来存放LED接口
static struct led_i **led_table[] = {
    (struct led_i **)&(struct iic_led_data){
        .interface = &iic_led_interface
    },
    
    (struct led_i **)&(struct usb_led_data){
        .interface = &usb_led_interface
    },
};







//核心层，去遍历某个table，找到对应的LED并执行
void led_toggle(int id)
{
    struct led_i **led = led_table[id];
    (*led)->toggle(led);
}

int main(void)
{
    printf(">>> this is version 2\n");
    
	//顶层调用
    led_toggle(IIC_LED_ID);
    led_toggle(IIC_LED_ID);
    led_toggle(IIC_LED_ID);
    
    led_toggle(USB_LED_ID);
    led_toggle(USB_LED_ID);
    led_toggle(USB_LED_ID);
    return 0;
}
```





# bottom




