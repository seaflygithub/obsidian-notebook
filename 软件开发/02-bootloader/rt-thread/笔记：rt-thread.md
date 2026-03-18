[TOC]

参考资料：
- RT-Thread文档中心: https://www.rt-thread.org/document/site/#/
- RT-Thread内核实现与应用开发实战—基于STM32: https://doc.embedfire.com/rtos/rtthread/zh/latest/index.html
- 野火配套程序代码: https://gitee.com/Embedfire-rtthread/ebf_rtthread_tutorial_code_1


# RT-Thread：软件仿真环境

## 选择仿真软件

仿真软件这里选择KEIL5，只要是KEIL5系列的都可以。

## 新建目录树

下面是现成的CMD批处理脚本：
```batch
@echo off
mkdir \a myrtthread\doc
mkdir \a myrtthread\project
mkdir \a myrtthread\user
echo A > myrtthread\user\main.c
mkdir \a myrtthread\rtthread\4.0.3\bsp
mkdir \a myrtthread\rtthread\4.0.3\src
mkdir \a myrtthread\rtthread\4.0.3\components\finsh
mkdir \a myrtthread\rtthread\4.0.3\include\libc
mkdir \a myrtthread\rtthread\4.0.3\libcpu\arm\cortex-m3
```

## 创建仿真工程

开发环境我们使用KEIL5，版本为5.23，高于或者低于5.23都行，只要是版本5就行。

首先打开KEIL5软件，新建一个工程，工程文件放在目录Project下面，名称命名为myrtt，必须是英文字母，不能是中文，切记。当命名好工程名称，点击确定之后会弹出Select Device for Target的选项框，让我们 选择处理器，这里我们选择ARMCM3。

![[Pastedimage20221024175556.png]]

![[Pastedimage20221024175723.png]]

![[Pastedimage20221024175847.png]]

![[Pastedimage20221024175951.png]]

然后在工程里面新建如下组：
![[Pastedimage20221024180449.png]]

在工程里面添加好组之后，我们需要把本地工程里面新建好的文件添加到工程里面。双击user组，然后添加main.c进该组：
![[Pastedimage20221024180807.png]]

下面是main.c的示例代码，后续软件仿真需要用到：
```cpp
unsigned int flag1;
unsigned int flag2;
void delay (unsigned int count)
{
    for(; count!=0; count--);
}
int main(void)
{
    for (;;)
    {
        flag1 = 1;
        delay( 100 );
        flag1 = 0;
        delay( 100 );
        flag2 = 1;
        delay( 100 );
        flag2 = 0;
        delay( 100 );
    }
}
```

## 配置调试仿真

**启用软件仿真**：为了方便，我们全部代码都用软件仿真，即不需要开发板也不需要仿真器， 只需要一个KEIL软件即可，有关软件仿真的配置具体见：
![[Pastedimage20221024181950.png]]

**修改时钟大小**：在时钟相关文件system_ARMCM3.c的开头，有一段代码定义了系 统时钟的大小为25M。在软件仿真的时候，确保时间的准确性，代码里面的系统时钟跟 软件仿真的时钟必须一致，所以Options forTarget->Target的时钟应该由默认的12M改成25M。如下图：

```cpp
#define __HSI ( 8000000UL)
#define __XTAL ( 5000000UL)

#define __SYSTEM_CLOCK (5*__XTAL) /* 5*5000000 = 25M */
```

![[Pastedimage20221024181611.png]]

**添加头文件路径**：在C/C++选项卡里面指定工程头文件的路径，不然编译会出错。至此，一个完整的基于Cortex-M3（Cortex-M4或Cortex-M7）内核的RT-Thread软件仿真的工程就建立完毕。
![[Pastedimage20221024182714.png]]



## 开始调试仿真


**编译程序**：编译程序如下操作。
![[Pastedimage20221024183047.png]]

![[Pastedimage20221024183208.png]]

![[Pastedimage20221024183324.png]]

![[Pastedimage20221024183548.png]]

![[Pastedimage20221024183642.png]]

![[Pastedimage20221024183913.png]]






# 技术点：时间片调度器


1、时间片，即每个线程执行完指定时长后，就会被强制让出CPU给其他线程。下面就是时间片工作的基本原理动态图展示。

![[gif202307191420.gif]]

2、在rt-thread中，其中跟时间片相关的函数为：rt_tick_increase


3、如果只有两个线程AB，那么可以实现一个最小AB循环调度器。即整个系统中只有A,B两个线程，A运行完某个时长后，主动让出CPU，让线程B执行，线程B执行完指定时长后，主动让出CPU，又让线程A执行。通过本实验可以学到两个线程之间是如何交接CPU使用权的。
![[gif202307191226.gif]]

4、基于前面，增加一个线程，让三个线程之间按顺序不断循环执行，也是通过让线程自觉主动让出CPU给下一个线程的方式来调度。
![[gif202307191210.gif]]









