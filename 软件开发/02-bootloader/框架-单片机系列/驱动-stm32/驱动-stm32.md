
# **STM32-Keil基础使用**

## **keil新建工程**

1. 新建一个空文件夹，用来存放工程文件(such as myuart.uvprojx, etc.)
2. 创建几个必要的子文件夹：CPU, HAL, APP
3. Copy the relevant source files from the official firmware library to the corresponding directory. 
	1. (1) CPU: core_cm3.c.h, startup_stm32f10x_hd.s 
	2. (2) HAL: stm32f10x_xxx.c.h
	3. (3) APP: main.c uart.c.h ...
4. KEIL新建工程,工程文件存放在新建的顶层目录；
5. KEIL添加(CPU, HAL, APP)这三个组.
6. KEIL为所有组把源文件添加进对应的组(*.c, *.s),头文件无需添加；
7. 配置C/C++, 添加头文件查找路径; 添加宏 USE_STDPERIPH_DRIVER。

```jsx
报错：no section to be FIRST/LAST
组里删除启动组，重新在 CPU 组里指定第一个启动文件即可.
```

## 单步调试

![[Pasted image 20251222151351.png]]


## 推挽输出和开漏输出

![[Pasted image 20251222151412.png]]



## **I2C从设备EV_IRQHandler**

如下图所示，下图结合了中断处理函数 I2C2_EV_IRQHandler 的代码片段和事件EV时序图，这样方便初学者能够看到代码就能想到对应的事件EV时序样貌。

![[Pasted image 20251222151426.png]]

在【STM32F10x参考手册】里，I2C章节还有关于主设备的事件处理时序图，在主设备采用中断模式下，同样是这样的类似对照图，具体代码可以参考主设备中断模式下其他相关代码。一般情况下，主设备大部分通过轮询方式来与从设备进行通讯，也可以用中断方式，中断方式的时序图就类似于下面的收发时序。

![[Pasted image 20251222151441.png]]




## **I2C伪代码探究**

I2C只有两根线（SCL、SDA），当处于空闲状态时，数据线和时钟线都高电平。

（1）起始位：当时钟线为高电平时，数据线从高到低，就表示发起通信。 （2）从机地址：当时钟线为高电平时，数据线上的数据必须保持稳定，比如SCL为高时，数据线稳定为高，此时就完成了逻辑1的传输。在整个通讯过程中，开始和停止条件，时钟线拉低之后，数据线就能随意改变，但是一旦时钟线拉高，数据线就必须保持稳定状态。

下面是发送一个字节的核心伪代码，拉低时钟线后，此时可以给数据线赋值，数据线赋值完成后，就需要给时钟线拉高，时钟线拉高之后，数据线的数据就必须保持稳定不变，让接收端来读取。如此周而复始。

```cpp
void IIC_Send_Byte(u8 txd)
{
    for(t=0;t<8;t++)
    {
	    IIC_SCL=0;//拉低时钟开始数据传输
	    delay_us(2);
        IIC_SDA=(txd&0x80)>>7;
        txd<<=1;
		delay_us(2);
		IIC_SCL=1;//拉高时钟线,此时数据线必须保持稳定
		delay_us(2);
    }
}

u8 IIC_Read_Byte(unsigned char ack)
{
	unsigned char i,receive=0;
	SDA_IN();//SDA设置为输入
	for(i=0;i<8;i++ )
	{
	    IIC_SCL=0;
	    delay_us(2);
		IIC_SCL=1;
	    receive<<=1;
	    if(READ_SDA)
		    receive++;
		delay_us(1);
	}
	if (!ack)
		IIC_NAck();//发送nACK
	else
		IIC_Ack(); //发送ACK
	return receive;
}
```





