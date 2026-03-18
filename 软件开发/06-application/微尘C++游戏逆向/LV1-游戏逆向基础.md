
草稿：[[微尘网络游戏逆向C++.excalidraw]]


```jsx
网盘目录:
C++游戏逆向教程（微尘网络安全）
		01、深造播放器
		02、课程和源码(微尘网络)
		03、DNF靶场
		04、驱动专用win10
		05、微尘知识库(教案笔记)——chrome收藏夹：C++游戏逆向 >> 微尘知识库
```

深造播放器登录账号: wc1052061602

微信小程序验证: 深造绑定登录，手机号: 18968246951，手机微信和电脑播放器在同一网段。

- VisualStudio2022开发环境
- CE地址查找
- OD基地址下断查找追基地址
    - CE追数据的基本方法论以及常用的几种追法
    - OD调试器追数据的方法论以及常用的几种追法
    - 天龙人物血量
    - 天龙人物状态


# 入门介绍

## 入门简介

1、前期需要掌握编程必要的编程语言基础，以及调试工具的使用基础；

2、掌握上述之后，通过靶场游戏来掌握逆向追数据的基本方法，靶场游戏就是不会更新的游戏；

3、掌握上述之后，通过实战游戏来掌握更复杂的逆向方法，该游戏会有检测和更新；

该笔记包含教程里的LV1和LV2，

相当于根据个人的掌握情况重新整理归类梳理了一遍。

工具清单：

- VisualStudio2022.exe —— 开发C++程序
- OllyDebug.rar —— 新手32位调试工具
- 中文版Cheat Engine 7.0.rar —— 内存查看工具

游戏安装包：

- 《新天龙八部》经典怀旧正式服客户端/XTLBB-CZ-0.07.1808_GF.zip ——（包含了32位和64位）
- 03、DNF靶场/DNF客户端New.rar

## 神器VisualStudio使用

- VisualStudio2022 —— 社区版足够，因为企业版和专业版需要激活码

双击安装包运行
![[Pasted image 20251229135801.png]]


点击继续
![[Pasted image 20251229135832.png]]


将以上三个地方勾选并且选好位置后 点击安装
![[Pasted image 20251229135856.png]]


如果你的系统版本不是win11会提示这个 点击继续就可以 不用管 然后等待下载完
![[Pasted image 20251229135912.png]]


![[Pasted image 20251229135931.png]]


然后就可以启动了
![[Pasted image 20251229135958.png]]


右键固定到任务栏或者开始菜单 然后就可以点击打开VS了 打开之后要登录微软账号 没有可以自己注册 如果账号失效了可以重新登录或者重新注册下

启动完成后，新建helloworld工程，能够运行控制台程序即安装成功。

注册账户，

使用自己的邮箱: [[mailto:seafly0616@qq.com]]

登录密码: seaflywrzhd16（微软账户第16）

VS项目的常用术语里，什么叫做【解决方案】？什么叫做【项目】？一个解决方案里面可能有多个项目，它们就是这种关系。不用多纠结。


# C++基础

## C++OOP函数重载

没什么好学的，就是能够识别不同参数类别即可，比如浮点型。

```cpp
	float f1 = 1.2;
00FD5518  movss       xmm0,dword ptr ds:[00FD7BCCh]  
00FD5520  movss       dword ptr [ebp-38h],xmm0  
	float f2 = 1.3;
00FD5525  movss       xmm0,dword ptr ds:[00FD7BD0h]  
00FD552D  movss       dword ptr [ebp-44h],xmm0  
	add(f1, f2);
...//省略其他代码
	double d1 = 1.2;
00FD5552  movsd       xmm0,mmword ptr ds:[00FD7BD8h]  
00FD555A  movsd       mmword ptr [ebp-54h],xmm0  
	double d2 = 1.3;
00FD555F  movsd       xmm0,mmword ptr ds:[00FD7BE0h]  
00FD5567  movsd       mmword ptr [ebp-64h],xmm0  
	add(d1, d2);
```

## C++OOP静态变量

静态变量和全局变量放在同一个内存区域，

```cpp

int add(int a, int b)
{
006A1810  push        ebp  
006A1811  mov         ebp,esp  
006A1813  sub         esp,0C0h  
006A1819  push        ebx  
006A181A  push        esi  
006A181B  push        edi  
006A1831  nop  
	static int c = 3;
	c = 2;
006A1832  mov         dword ptr ds:[006AA020h],2  
	return a + b;
006A183C  mov         eax,dword ptr [ebp+8]  
006A183F  add         eax,dword ptr [ebp+0Ch]  
}
```


![[Pasted image 20251229141412.png]]



模块化，头文件是模块化的基础，把函数声明放到头文件，

推荐文件名相同后缀不同，比如 module1.cpp、module1.h

头文件不要用微软的那种 `#pragma once` 方式，用宏开关的方式。

全局变量可以重复声明，且用 extern 关键字来声明，但定义只能在一个地方定义，且必须有定义。

## C++OOP多态虚函数

因为人家正向的程序员用的就是这个东西，所以我们逆向的肯定也要了解，

多态，就是基类和子类都有相同的方法，但是具体的实例执行时执行的是具体子类的方法。

```cpp
#include <Windows.h>
#include <iostream>

class RenWu {
public:
	std::string name;
	void virtual action(void)   // 在基类弄成虚函数,这样就实现了多态
	{
		printf("我是人物\\n");
	}
};
class XiaoMing : public RenWu {
public:
	void action(void)
	{
		printf("我是小明\\n");      // 最终会调用这个方法
	}
};

void RunAction(RenWu *ren)
{
	ren->action();
}

int main(int argc, const char* argv[])
{
	XiaoMing xm;
	RunAction(&xm);
	return 0;
}
```

## C++OOP类的this指针

探究：类成员函数的内部代码是如何得到这个this指针的？

下面是一个简单的类，主要就是调用实例方法，然后方法内部修改实例属性。

```cpp
#include <Windows.h>
#include <iostream>

class Mydata {
public:
	int a = 1;
	int b = 2;
	void set_a(void) { a = 5;  b = 6; }
};

int main(int argc, const char* argv[])
{
	Mydata data;
	data.set_a();
	return 0;
}
```

类方法 set_a 是不占用结构体内存空间的，它的内容存放在代码段，

但是，类方法访问类属性时，是通过 this 指针来访问的，

那么类方法是如何得到这个 this 指针的？调用者并没有传递this指针给它呀。

下面是反汇编单步调试：下面就是把 this 指针传进成员函数。

![[Pasted image 20251229141437.png]]


在实际的游戏逆向过程中，你调用游戏内置的函数，

你不知道这个函数是普通函数还是类成员函数，

所以一般情况下，保险起见，你默认最好是把 this 指针传进这个函数，

防止该函数在访问相关类属性时发生错误而导致崩溃。

## C++OOP继承属性大小

下面是一个简单的类继承：

```cpp
#include <Windows.h>
#include <iostream>

class Dongwu {
public:
	int a = 1;
	void set_a(void) { a = 5; }
};

class Dog : public Dongwu {
public:
	int a = 2;
	int b = 3;
};

int main(int argc, const char* argv[])
{
	Dog dog1;
	sizeof(dog1);  //12字节,两个类的属性大小总和
	return 0;
}
```

下面是类继承的内存布局：
![[Pasted image 20251229141453.png]]

## C++OOP虚函数表

下面是探究虚函数的简单代码：

```cpp
#include <Windows.h>
#include <iostream>

class Renwu {
public:
	int a = 0;
	void virtual action1(void) { a = 1; }
	void virtual action2(void) { a = 2; }
	void virtual action3(void) { a = 3; }
};

class Nanren : public Renwu {
public:
	int b = 1;
};

int main(int argc, const char* argv[])
{
	Nanren xiaoming;
	Renwu* p = (Renwu*)&xiaoming;

	sizeof(xiaoming);    //三个虚函数仅占4字节
	p->action1();
	p->action2();
	p->action3();
	return 0;
}
```

直接下断点调试，查看 &xiaoming 内存情况：

![[Pasted image 20251229141515.png]]


继续跟到这个红色地址里，然后反汇编 caller 代码，得到如下结论：

![[Pasted image 20251229141535.png]]



红色的地址是一个指针，指向另一个地址，

另一个地址就是一个数组，里面的每个成员，就是类方法的首地址，这个数组就是虚函数表；

另外，普通函数没有这个表，只有虚函数才有这个虚函数表。

```cpp
	Nanren xiaoming;
00FA4C90  lea         ecx,[ebp-14h]    //&xiaoming (this)
00FA4C93  call        00FA141F  
00FA4C98  nop  
	Renwu* p = (Renwu*)&xiaoming;
00FA4C99  lea         eax,[ebp-14h]  
00FA4C9C  mov         dword ptr [ebp-20h],eax  

	sizeof(xiaoming);    //三个虚函数仅占4字节
	p->action1();
00FA4C9F  mov         eax,dword ptr [ebp-20h]  
00FA4CA2  mov         edx,dword ptr [eax]  
00FA4CA4  mov         esi,esp  
00FA4CA6  mov         ecx,dword ptr [ebp-20h]  
00FA4CA9  mov         eax,dword ptr [edx]  
00FA4CAB  call        eax  
00FA4CAD  cmp         esi,esp  
00FA4CAF  call        00FA125D  
00FA4CB4  nop
```

## C++STL-string类

在 C++ 里，string是一个模板类，实例化就是一个对象。

用 `[]` 来访问字符串中的字符，

string 类重载了 “[]” 操作符，所以可以用 str[i] 的形式来访问操作字符串中的字符。

直接用 + 可以将两个 string 对象拼接，

可以直接比较两个 string 对象是否相等，比如 str1 == str2，

str1.find 方法，可以查找字符串中第一个出现的字符，并返回该字符所在下标，

下面是范例代码，大家要掌握这些，比如后续的需要处理文件目录相关的等等。

```cpp
#include <Windows.h>
#include <iostream>
#include <string>

int main(void)
{
	std::string str1 = "aaa bbb ccc   ddd eeee  ";

	int start = 0;
	int end = 0;
	char targetCh = ' ';

	// 遍历str1并打印出里面所有非空字符串str2
	while (end != std::string::npos)
	{
		end = str1.find(targetCh, start);
		std::string str2 = str1.substr(start, end - start);

		if (!str2.empty()) 
			std::cout << "单词: " << str2 << std::endl;

		start = end + 1;
	}
	return 0;
}
```

## C++STL-vector容器类

vector是一个封装了动态大小数组的顺序容器，它是模板类，能够存放各种类型的对象，

但是，同一个容器只能存放同一个类型的对象，它不能像元组(Tuple)那样能存放不同类型的对象，

```cpp
#include <iostream>
#include <string>
#include <vector>

int main()
{
    std::vector <int>v1;
    v1.push_back(10);
    v1.push_back(20);
    v1.push_back(30);
    v1.push_back(3.14);
    printf("v1.size() = %llu\\n", v1.size());

    // 遍历容器
    for (auto i = v1.begin(); i != v1.end(); i++)
    {
        printf("v1 = %d\\n", *i);
    }

    // 去掉容器里最后一个数据
    v1.pop_back();
    printf("v1.size() = %llu\\n", v1.size());

    // 清除容器内容
    v1.clear();
    printf("v1.size() = %llu\\n", v1.size());
    return 0;
}
```



# Windows编程基础

## Windows句柄

Windows之所以要设立句柄，根本上源于内存管理机制的问题 —— 虚拟地址，简而言之数据的地址需要变动，变动以后就需要有人来记录管理变动，因此系统用句柄来记载数据地址的变更。

让我们来先体验一下句柄是个什么东西：

首先通过 VS —》工具 —》Spy++

![[Pasted image 20251229141626.png]]



```cpp
WINUSERAPI
BOOL
WINAPI
MoveWindow(
    _In_ HWND hWnd,
    _In_ int X,
    _In_ int Y,
    _In_ int nWidth,
    _In_ int nHeight,
    _In_ BOOL bRepaint);
```

窗口句柄实操体验：

VS通过API来查找对应的窗口句柄: `FindWindowA()`

1、物色目标窗口，首先通过 Spy++ 拿到类名和标题

2、然后把类名和标题填入 FindWindow 对应的参数里。

```cpp
#include <Windows.h>
#include <iostream>

int main(int argc, const char* argv[])
{
	//HWND hdl = FindWindow(L"Notepad", L"*无标题 - 记事本");//OK

	// 我们先启动一个空白记事本窗口，然后用 Spy++ 拿到记事本窗口句柄，
	// 进而拿到其句柄值 和 类名等信息，
	// 其中 Notepad 就是目标窗口的类名, 注意是类名, 第二个参数才是标题的内容
	// FindWindow 作为新手,怎么知道用这个函数？
	// 直接搜索引擎搜索问: Windows C++ 获取指定窗口的句柄
	HWND hdl = FindWindow(L"Notepad", NULL);//OK
	if (hdl == NULL)
	{
		std::cout << "Error: " << GetLastError() << std::endl;
		return -1;
	}

	std::cout << "hdl: " << hdl << std::endl;

	// 既然拿到窗口句柄,我们操作一下窗口
	for (size_t i = 0; i < 600; i++)
	{
		// 效果: 窗口从左上角缓慢往右边平移
		Sleep(10);
		MoveWindow(
			hdl,       // 窗口的句柄
			5+i, 5,    // 窗口顶角的x,y值
			500, 300,  // 窗口的宽度,高度
			true       // 是否重画
		);
	}

	return 0;
}
```




学习目的：我们做辅助项目时，不会手动用 Spy++ 来抓句柄，那样太 low 了，我们需要通过Windows的 api 来找到目标窗口的句柄，拿到目标窗口的句柄之后，我们后续就可以很方便地**操作控制目标窗口**了。



## Windows进程和线程

进程和线程：进程相当于火车，线程相当于车厢，车厢要依赖火车才能运行；进程是资源分配的最小单位，线程是CPU调度的最小单位。

进程：分配代码段、数据段、堆、栈。

进程与多核：不同火车可以开在多个轨道上，同一火车的车厢不能行进在不同轨道上。

互斥锁：比如火车上的厕所，里面但凡有人就不能进。

信号量：比如火车上的餐厅，允许多个人进入就餐，但如果人满了则需要在门口等待，等有人吃完出来了才能进去。

## Windows进程详解

**进程从来不执行任何东西，真正完成代码执行的是线程，进程只是容器或者是线程的执行环境**。

先简单看看API，我们这节课不使用，只是简单了解其参数，

```cpp
WINBASEAPI
BOOL
WINAPI
CreateProcessA(
    _In_opt_ LPCSTR lpApplicationName,
    _Inout_opt_ LPSTR lpCommandLine,
    _In_opt_ LPSECURITY_ATTRIBUTES lpProcessAttributes,
    _In_opt_ LPSECURITY_ATTRIBUTES lpThreadAttributes,
    _In_ BOOL bInheritHandles,
    _In_ DWORD dwCreationFlags,
    _In_opt_ LPVOID lpEnvironment,
    _In_opt_ LPCSTR lpCurrentDirectory,
    _In_ LPSTARTUPINFOA lpStartupInfo,
    _Out_ LPPROCESS_INFORMATION lpProcessInformation
    );
```

常规启动游戏：一般情况，游戏安装目录下，游戏都会有个登录器比如 launch.exe，而真正的游戏是game.exe，我们直接双击 game.exe 文件会弹窗让我用登陆器启动，这就是游戏官方给我们设置的小小限制。比如游戏本体通过命令行参数 lpCommandLine 来限制游戏启动。

我们如何获取其命令行呢？

首先我们通过登陆器来启动游戏，然后百度 “Windows下获取程序的命令行参数”，

```cpp
// 首先要运行游戏,才能看到 Game.exe 这个进程,才能通过此命令获得参数
wmic process where caption="Game.exe" get caption,commandline /value

// 执行命令后,得到如下结果输出:
Caption=Game.exe
CommandLine=.\\Bin\\Game.exe -fl
```

我们就可以使用 CreateProcess 这个函数，来实现跳过登录器的软件，

具体实现例程代码参考跳过登陆器相关的小节，下面是核心代码:

```cpp
#include <windows.h>
#include <iostream>

int main() {
    bool bResult = true;

    /*
        如果项目字符集配置是 Unicode, 
        则字符串类型变为 wchar_t,
        且字符串常量即左引号前要加上L, 比如 L"hello"
        且 std::cout 改为 std::wcout
    */

    // 要执行的命令行
    char szCmdLine[] = "D:\\\\SW\\\\GameTL\\\\Bin\\\\Game.exe -fl";

    // 程序运行的当前目录
    char szCurPath[] = "D:\\\\SW\\\\GameTL\\\\Bin";

    // 进程信息结构体
    PROCESS_INFORMATION pi = { 0 };

    // 启动信息结构体
    STARTUPINFO si = { 0 };
    si.cb = sizeof(si);

    bResult = CreateProcess(
        NULL,                   // NULL 表示使用命令行
        szCmdLine,              // 命令行参数
        NULL,                   // 进程安全属性
        NULL,                   // 线程安全属性
        FALSE,                  // 句柄继承选项
        CREATE_NEW_CONSOLE,     // 创建标志
        NULL,                   // 环境变量
        szCurPath,              // 当前目录
        &si,                    // 启动信息
        &pi                     // 进程信息
    );

    if (bResult)
    {
        std::cout << "进程句柄: " << pi.hProcess << std::endl;
        std::cout << "  进程ID: " << pi.dwProcessId << std::endl;
        std::cout << "线程句柄: " << pi.hThread << std::endl;
        std::cout << "  线程ID: " << pi.dwThreadId << std::endl;

        // 等待进程结束
        WaitForSingleObject(pi.hProcess, INFINITE);

        // 关闭进程和线程句柄
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }
    else
    {
        std::cout << "进程创建失败，错误码: " << GetLastError() << std::endl;
    }

    return 0;
}
```

## Windows内核对象详解

Windows中每个内核对象都只是一个内存块，它由操作系统内核分配，并只能由操作系统内核进行访问，应用程序不能在内存中定位这些数据结构并直接更改其内容。这个内存块是一个数据结构，其成员维护着与对象相关的信息。其中少数成员（比如安全描述符和使用计数）是所有内核对象都有的，但大多数成员都是不同类型对象自己特有的。

常见的内核对象：

文件对象、事件对象、进程对象、线程对象、互斥量对象、信号量对象、注册表对象等。

内核对象里的计数器和生命周期，内核对象的所有者是操作系统内核，而非用户进程。换而言之，就是当用户进程退出了，相关的内核对象不一定会销毁。OS内核通过对象的引用计数器，来获知当前有多少个进程正在使用某个特定的内核对象。初次创建内核对象，引用计数器会设置为1，当另一个进程获得该内核对象的访问权之后，引用计数器会加1。如果某内核对象的引用计数器递减为0了，OS内核就会销毁该内核对象。

Windows提供了一组API可以操作内核对象，成功获得对象后，函数会返回一个句柄，该句柄就表示该内核对象了，后续可以由进程中的任何线程使用。除了内核对象，还有其他类型的对象，比如窗口、菜单、字体等，这些属于用户对象和GDI对象。要想区分内核对象和非内核对象，最简单的方式就是查看创建这个对象的函数，几乎所有创建内核对象的函数都有一个允许我们指定安全属性的参数。

当调用了 CreateThread 等创建内核对象的函数后，就是相当于操作系统多了一个内存块，这个内存块就是内核对象，也是此时内核对象被创建，引用计数器为1。这里实则发生了2件事：

1、创建了一个内核对象（引用计数器初始化为1）；

2、创建线程的函数访问了此对象（引用计数器加1）；

3、此时引用计数器为2；

当调用 CloseHandle(hThread) 的时候，系统通过该句柄计算出此句柄在句柄表中的索引，然后把那一项处理后标注为空闲可用的项，内核对象的引用计数器减1，即此时该内核对象的引用计数器值为1，之后这个线程句柄与前面创建的内核对象已经没有任何关系了，不能通过该句柄再次去访问该内核对象了。

那该内核对象与句柄脱钩之后，其引用计数器为1，那它什么时候会被销毁？当此线程结束的时候，它的引用计数器再减1，此时其引用计数器就为0了，内核对象被销毁。

下面是完善后的代码：

```cpp
#include <windows.h>
#include <iostream>

int main() {
    bool bResult = true;

    /*
        如果项目字符集配置是 Unicode, 
        则字符串类型变为 wchar_t,
        且字符串常量即左引号前要加上L, 比如 L"hello"
        且 std::cout 改为 std::wcout
    */

    // 要执行的命令行
    char szCmdLine[] = "D:\\\\SW\\\\TianLong\\\\Bin\\\\Game.exe -fl";

    // 程序运行的当前目录
    char szCurPath[] = "D:\\\\SW\\\\TianLong\\\\Bin";

    // 进程信息结构体
    PROCESS_INFORMATION pi = { 0 };

    // 启动信息结构体
    STARTUPINFO si = { 0 };
    si.cb = sizeof(si);

    bResult = CreateProcess(
        NULL,                   // NULL 表示使用命令行
        szCmdLine,              // 命令行参数
        NULL,                   // 进程安全属性
        NULL,                   // 线程安全属性
        FALSE,                  // 句柄继承选项
        CREATE_NEW_CONSOLE,     // 创建标志
        NULL,                   // 环境变量
        szCurPath,              // 当前目录
        &si,                    // 启动信息
        &pi                     // 进程信息
    );

    if (bResult)
    {
        std::cout << "进程句柄: " << pi.hProcess << std::endl;
        std::cout << "  进程ID: " << pi.dwProcessId << std::endl;
        std::cout << "线程句柄: " << pi.hThread << std::endl;
        std::cout << "  线程ID: " << pi.dwThreadId << std::endl;

        // 等待进程结束
        WaitForSingleObject(pi.hProcess, INFINITE);

        // 上面Wait会阻塞,直到我们在游戏内主动退出

        // 关闭进程句柄和线程句柄(脱钩)
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }
    else
    {
        std::cout << "进程创建失败，错误码: " << GetLastError() << std::endl;
    }

    return 0;
}
```

## Windows线程详解

每一个进程都有自己的栈空间，

下面是 CreateThread 函数的使用完整演示代码：

```cpp
#include <windows.h>
#include <iostream>

DWORD WINAPI ThreadProc(LPVOID lpParameter)
{
    HANDLE hThread = GetCurrentThread();
   
    for (size_t i = 0; i < 3; i++)
    {
        Sleep(1000);
        std::cout << i << "线程句柄: " << hThread << std::endl;
    }
    return 0;
}

int main() {
    bool bResult = true;

    // 线程ID
    DWORD ThreadId = 0;

    HANDLE hThread = CreateThread(
        NULL,         // 安全描述符
        0,            // 线程的栈大小,单位为字节
        ThreadProc,   // 线程执行的函数
        NULL,         // 线程函数参数
        0,            // 线程创建的标志,0表示立即运行,
                      // CREATE_SUSPENDED, 需要调用 ResumeThread 才会运行
        &ThreadId     // 线程ID
    );

    if (hThread)
    {
        std::cout << "创建线程成功" << std::endl;

        // 等待线程执行完
        WaitForSingleObject(hThread, INFINITE);

        // 关闭句柄(脱钩)
        CloseHandle(hThread);

        std::cout << "等待线程已退出" << std::endl;
    }
    else
    {
        std::cout << "创建线程失败,错误码: " << GetLastError() << std::endl;
    }

    return 0;
}
```

## Windows互斥体Mutex

当多个线程访问全局变量时，会出现竞争情况，因此这里使用互斥锁。

下面是三个线程卖票的完整演示代码：

```cpp
#include <windows.h>
#include <iostream>

unsigned long g_piao = 100; // 多个线程卖票
HANDLE g_mutex = NULL;

DWORD WINAPI ThreadProc(LPVOID lpParameter)
{
    // 线程编号
    DWORD ThreadNo = (DWORD)lpParameter;

    // 线程句柄
    HANDLE hThread = GetCurrentThread();
   
    while (1)
    {
        // 等待互斥锁
        WaitForSingleObject(g_mutex, INFINITE);

        // 得到互斥锁
        if (g_piao == 0)
        {
            break;
        }

        Sleep(50);
        g_piao--; //卖出一张票,票数减1
        printf("线程[%u]卖了1张票,剩余票数:%lu\\n", ThreadNo, g_piao);

        // 放开互斥锁
        ReleaseMutex(g_mutex);
    }

    // 放开互斥锁
    ReleaseMutex(g_mutex);
    return 0;
}

int main() {
    bool bResult = true;

    // 创建互斥体
    g_mutex = CreateMutex(
        NULL,  // 安全描述符
        false, // FALSE表示初始不拥有互斥锁
        NULL   // NULL表示匿名互斥锁
    );

    // 线程ID
    DWORD ThreadId = 0;
    HANDLE hThread1 = NULL;
    HANDLE hThread2 = NULL;
    HANDLE hThread3 = NULL;
    
    hThread1 = CreateThread(
        NULL,         // 安全描述符
        0,            // 线程的栈大小,单位为字节
        ThreadProc,   // 线程执行的函数
        (LPVOID)1,    // 线程函数参数
        0,            // 线程创建的标志,0表示立即运行,
                      // CREATE_SUSPENDED, 需要调用 ResumeThread 才会运行
        &ThreadId     // 线程ID
    );
    Sleep(20);

    hThread2 = CreateThread(
        NULL,         // 安全描述符
        0,            // 线程的栈大小,单位为字节
        ThreadProc,   // 线程执行的函数
        (LPVOID)2,    // 线程函数参数
        0,            // 线程创建的标志,0表示立即运行,
        // CREATE_SUSPENDED, 需要调用 ResumeThread 才会运行
        &ThreadId     // 线程ID
    );
    Sleep(20);

    hThread3 = CreateThread(
        NULL,         // 安全描述符
        0,            // 线程的栈大小,单位为字节
        ThreadProc,   // 线程执行的函数
        (LPVOID)3,    // 线程函数参数
        0,            // 线程创建的标志,0表示立即运行,
        // CREATE_SUSPENDED, 需要调用 ResumeThread 才会运行
        &ThreadId     // 线程ID
    );
    Sleep(20);

    if ((!hThread1) || (!hThread2) || (!hThread3))
    {
        std::cout << "创建线程失败,错误码: " << GetLastError() << std::endl;
        return -1;

    }

    std::cout << "创建线程成功" << std::endl;

    // 等待线程执行完
    WaitForSingleObject(hThread1, INFINITE);
    CloseHandle(hThread1);

    WaitForSingleObject(hThread2, INFINITE);
    CloseHandle(hThread2);

    WaitForSingleObject(hThread3, INFINITE);
    CloseHandle(hThread3);

    // 也可以通过下面方式来等待
    // WaitForMultipleObjects(3, hThreads, true, INFINITE);

    // 关闭互斥体句柄
    CloseHandle(g_mutex);

    std::cout << "所有线程已退出" << std::endl;
    return 0;
}
```

## Windows互斥事件event

事件对象也属于内核对象，它包含3个成员：

引用计数器、自动重置/人工重置、已通知状态/未通知状态。

当人工重置的事件对象得到通知时，等待该事件的所有线程均变为可调度线程；

当自动重置的事件对象得到通知时，等待该事件的线程中只有一个线程变为可调度线程；

函数接口：CreateEvent、SetEvent、ResetEvent、WaitForSingleObject

事件比较适合处理两个线程的情况，因为事件就是起到一个通知的作用，

```cpp
{
	// 初始化代码: 创建手动重置事件，初始状态为未触发
	hEvent = CreateEvent(
	        NULL,   // 安全描述符
	        TRUE,   // TRUE表示需要手动调用 ResetEvent 来设置为无信号
	        FALSE,  // 初始状态为未触发
	        NULL    // NULL表示匿名事件
	);
}

{
	// 消费线程: 阻塞等待事件触发
	WaitForSingleObject(hEvent, INFINITE);
	
	...//消费资源
	
	// 消费线程: 把事件重置为未触发
	ResetEvent(hEvent);
}

{
		// 生产线程: 完成生产,告知消费线程
		SetEvent(hEvent);  // 触发事件
}

{
    // 资源回收: 关闭事件句柄
    CloseHandle(hEvent);
}
```

## Windows信号量Semaphore

这节课可以不用学，因为在实际企业级开发中，信号量比较复杂很少用。

```cpp
{
    // 初始化代码: 创建信号量，初始计数为3，最大计数为3
    hSemaphore = CreateSemaphore(
        NULL,               // 默认安全属性
        RESOURCE_COUNT,     // 初始资源计数
        RESOURCE_COUNT,     // 最大资源计数
        NULL                // 匿名信号量
    );
}

{
    // 消费线程: 请求信号量（获取资源）
    WaitForSingleObject(hSemaphore, INFINITE);
    
    // 模拟访问资源
    Sleep(1000 + rand() % 2000);  // 随机睡眠1-3秒
    
    // 释放信号量（释放资源）
    ReleaseSemaphore(hSemaphore, 1, NULL);
}

{
    // 资源回收: 关闭信号量句柄
    CloseHandle(hSemaphore );
}
```

## Windows文件操作

CreateFile 读写文本文件示例，以及 CreateFile 二进制文件示例，分别支持VS工程属性字符集配置的是多字节字符集和Unicode字符集。使用 C++11 标准。

```cpp
#include <windows.h>
#include <iostream>
#include <string>
#include <vector>
#include <locale>
#include <codecvt>
#include <system_error>

// 根据字符集自动选择正确的字符串类型
#ifdef _UNICODE
using TString = std::wstring;
#define TCHAR wchar_t
#define _T(x) L ## x
#define TO_TSTR(s) std::wstring(s)
#else
using TString = std::string;
#define TCHAR char
#define _T(x) x
#define TO_TSTR(s) std::string(s)
#endif

// 错误处理辅助函数
void PrintLastError(const char* message) {
    DWORD errorCode = GetLastError();
    LPVOID errorMessageBuffer = nullptr;

    FormatMessage(
        FORMAT_MESSAGE_ALLOCATE_BUFFER |
        FORMAT_MESSAGE_FROM_SYSTEM |
        FORMAT_MESSAGE_IGNORE_INSERTS,
        nullptr,
        errorCode,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        (LPTSTR)&errorMessageBuffer,
        0, nullptr
    );

    std::cerr << message << ": " << static_cast<LPTSTR>(errorMessageBuffer) << std::endl;
    LocalFree(errorMessageBuffer);
}

// 写入文本文件函数（兼容多字节/Unicode）
bool WriteTextFile(const TString& filePath, const TString& content) {
    HANDLE hFile = CreateFile(
        filePath.c_str(),
        GENERIC_WRITE,
        0,
        nullptr,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );

    if (hFile == INVALID_HANDLE_VALUE) {
        PrintLastError("创建文件失败");
        return false;
    }

    bool result = false;
    DWORD bytesWritten = 0;

#ifdef _UNICODE
    // Unicode 模式：写入 BOM 并以 UTF-16 格式写入
    const wchar_t BOM = 0xFEFF;
    if (!WriteFile(hFile, &BOM, sizeof(BOM), &bytesWritten, nullptr)) {
        PrintLastError("写入 BOM 失败");
        CloseHandle(hFile);
        return false;
    }

    result = WriteFile(
        hFile,
        content.c_str(),
        static_cast<DWORD>(content.size() * sizeof(wchar_t)),
        &bytesWritten,
        nullptr
    );
#else
    // 多字节模式：直接写入
    result = WriteFile(
        hFile,
        content.c_str(),
        static_cast<DWORD>(content.size()),
        &bytesWritten,
        nullptr
    );
#endif

    if (!result) {
        PrintLastError("写入文件失败");
    }

    CloseHandle(hFile);
    return result;
}

// 读取文本文件函数（兼容多字节/Unicode）
bool ReadTextFile(const TString& filePath, TString& content) {
    HANDLE hFile = CreateFile(
        filePath.c_str(),
        GENERIC_READ,
        FILE_SHARE_READ,
        nullptr,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );

    if (hFile == INVALID_HANDLE_VALUE) {
        PrintLastError("打开文件失败");
        return false;
    }

    DWORD fileSize = GetFileSize(hFile, nullptr);
    if (fileSize == INVALID_FILE_SIZE) {
        PrintLastError("获取文件大小失败");
        CloseHandle(hFile);
        return false;
    }

    std::vector<TCHAR> buffer(fileSize / sizeof(TCHAR) + 1);
    DWORD bytesRead = 0;

    if (!ReadFile(hFile, buffer.data(), fileSize, &bytesRead, nullptr)) {
        PrintLastError("读取文件失败");
        CloseHandle(hFile);
        return false;
    }

    buffer.resize(bytesRead / sizeof(TCHAR));
    buffer.push_back(0); // 添加字符串结束符
    content = buffer.data();

#ifdef _UNICODE
    // 跳过 Unicode BOM
    if (!content.empty() && content[0] == 0xFEFF) {
        content = content.substr(1);
    }
#endif

    CloseHandle(hFile);
    return true;
}

// 写入二进制文件函数（与字符集无关）
bool WriteBinaryFile(const TString& filePath, const std::vector<BYTE>& data) {
    HANDLE hFile = CreateFile(
        filePath.c_str(),
        GENERIC_WRITE,
        0,
        nullptr,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );

    if (hFile == INVALID_HANDLE_VALUE) {
        PrintLastError("创建文件失败");
        return false;
    }

    DWORD bytesWritten = 0;
    bool result = WriteFile(
        hFile,
        data.data(),
        static_cast<DWORD>(data.size()),
        &bytesWritten,
        nullptr
    );

    if (!result) {
        PrintLastError("写入文件失败");
    }

    CloseHandle(hFile);
    return result;
}

// 读取二进制文件函数（与字符集无关）
bool ReadBinaryFile(const TString& filePath, std::vector<BYTE>& data) {
    HANDLE hFile = CreateFile(
        filePath.c_str(),
        GENERIC_READ,
        FILE_SHARE_READ,
        nullptr,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );

    if (hFile == INVALID_HANDLE_VALUE) {
        PrintLastError("打开文件失败");
        return false;
    }

    DWORD fileSize = GetFileSize(hFile, nullptr);
    if (fileSize == INVALID_FILE_SIZE) {
        PrintLastError("获取文件大小失败");
        CloseHandle(hFile);
        return false;
    }

    data.resize(fileSize);
    DWORD bytesRead = 0;

    if (!ReadFile(hFile, data.data(), fileSize, &bytesRead, nullptr)) {
        PrintLastError("读取文件失败");
        CloseHandle(hFile);
        return false;
    }

    data.resize(bytesRead);
    CloseHandle(hFile);
    return true;
}

// 辅助函数：将字符串打印到控制台（兼容多字节/Unicode）
void PrintString(const TString& str) {
#ifdef _UNICODE
    // Unicode 模式：转换为本地多字节编码输出
    try {
        std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;
        std::cout << converter.to_bytes(str) << std::endl;
    }
    catch (const std::range_error&) {
        // 处理转换失败的情况
        std::cerr << "[ERROR] 无法转换字符串为 UTF-8" << std::endl;
    }
#else
    // 多字节模式：直接输出
    std::cout << str << std::endl;
#endif
}

int main() {
    // 设置控制台输出编码，确保中文显示正常
#ifdef _UNICODE
    SetConsoleOutputCP(CP_UTF8);
#else
    SetConsoleOutputCP(GetACP());
#endif

    // 文本文件操作示例
    TString textFilePath = _T("example_text.txt");
    TString textContent = _T("这是1个使用 CreateFile 函数的文本文件示例。\\n");

    std::cout << "\\n=== 文本文件操作 ===" << std::endl;
    if (WriteTextFile(textFilePath, textContent)) {
        std::cout << "文本文件写入成功" << std::endl;

        TString readTextContent;
        if (ReadTextFile(textFilePath, readTextContent)) {
            std::cout << "文本文件内容如下：" << std::endl;
            PrintString(readTextContent);
        }
    }

    // 二进制文件操作示例
    TString binaryFilePath = _T("example_binary.bin");
    std::vector<BYTE> binaryData = {
        0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x2C, 0x20, 0x57, 
        0x6F, 0x72, 0x6C, 0x64, 0x21, // "Hello, World!"
        0x0D, 0x0A, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 
        0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F // 示例字节
    };

    std::cout << "\\n=== 二进制文件操作 ===" << std::endl;
    if (WriteBinaryFile(binaryFilePath, binaryData)) {
        std::cout << "二进制文件写入成功" << std::endl;

        std::vector<BYTE> readBinaryData;
        if (ReadBinaryFile(binaryFilePath, readBinaryData)) {
            std::cout << "二进制文件内容（前20字节）：" << std::endl;

            for (size_t i = 0; i < readBinaryData.size(); ++i) {
                printf("0x%02X ", readBinaryData[i]);
                if ((i + 1) % 10 == 0) std::cout << std::endl;
            }
            std::cout << std::endl;
        }
    }
    return 0;
}
```

## Windows读写配置ini

在稍微有点规模的项目中，都会用到配置文件，

我们在做游戏辅助开发时，比如登录的时候，

我们希望用户第一次登录成功后，我们能够把账号密码存到配置文件，

下次登录的时候可以实现自动登录。

总之，配置文件可以帮助我们存放我们想要的任何信息。

相关函数：WritePrivateProfileString

下面是配置文件读写的完整示例代码:

```cpp
#include <windows.h>
#include <iostream>
#include <string>

// 根据字符集自动选择正确的字符串类型
#ifdef _UNICODE
typedef std::wstring TString;
#define _T(x) L ## x
#else
typedef std::string TString;
#define _T(x) x
#endif

// 写入 INI 文件函数
bool WriteIniFile(
    const TString& appName, // 其实就是 section 名称
    const TString& keyName, const TString& value, 
    const TString& fileName) {
    BOOL result = WritePrivateProfileString(
        appName.c_str(),
        keyName.c_str(),
        value.c_str(),
        fileName.c_str()
    );

    if (!result) {
        DWORD errorCode = GetLastError();
        std::wcout << L"写入 INI 文件失败，错误码: " << errorCode << std::endl;
        return false;
    }

    return true;
}

// 读取 INI 文件函数
TString ReadIniFile(
    const TString& appName, 
    const TString& keyName, const TString& defaultValue, 
    const TString& fileName) {
    const int bufferSize = 256;
    TString buffer(bufferSize, 0);

    DWORD result = GetPrivateProfileString(
        appName.c_str(),
        keyName.c_str(),
        defaultValue.c_str(),
        &buffer[0],
        bufferSize,
        fileName.c_str()
    );

    // 调整缓冲区大小以匹配实际读取的字符串长度
    buffer.resize(result);
    return buffer;
}

int main() {
    TString iniFileName = _T("D:\\\\test.ini");

    // 写入配置项
    std::cout << "写入配置项..." << std::endl;
    WriteIniFile(_T("Settings"), _T("Username"), _T("微尘C++游戏辅助"), iniFileName);
    WriteIniFile(_T("Settings"), _T("Password"), _T("SecurePass123"), iniFileName);
    WriteIniFile(_T("AppInfo"), _T("Version"), _T("1.0.0"), iniFileName);
    WriteIniFile(_T("AppInfo"), _T("ReleaseDate"), _T("2023-05-15"), iniFileName);

    // 删除一个键（将值设为 NULL）
    WriteIniFile(_T("AppInfo"), _T("ReleaseDate"), _T(""), iniFileName);

    // 读取配置项
    std::cout << "\\n读取配置项..." << std::endl;
    TString username = "";
    TString password = "";
    TString version = "";
    TString releaseDate = "";

    username = ReadIniFile(_T("Settings"), _T("Username"), _T("DefaultUser"), iniFileName);
    password = ReadIniFile(_T("Settings"), _T("Password"), _T(""), iniFileName);
    version = ReadIniFile(_T("AppInfo"), _T("Version"), _T("0.0.0"), iniFileName);
    releaseDate = ReadIniFile(_T("AppInfo"), _T("ReleaseDate"), _T("未知"), iniFileName);

    // 输出读取的配置
    std::cout << "Username: " << username << std::endl;
    std::cout << "Password: " << password << std::endl;
    std::cout << "Version: " << version << std::endl;
    std::cout << "ReleaseDate: " << releaseDate << std::endl;

    // 写入数值（需要先转换为字符串）
    int maxConnections = 10;

    // 在实际应用中应使用 std::to_wstring 或 _itow_s
    TString maxConnectionsStr = _T("10"); 
    WriteIniFile(_T("Network"), _T("MaxConnections"), maxConnectionsStr, iniFileName);

    std::cout << "\\nINI 文件已更新，请查看 " << iniFileName << std::endl;

    return 0;
}
```

关于控制台打印中文：

CMD控制台中文编码默认支持的是 GBK 编码，也就是多字节编码；

如果你的VS配置的字符集为 Unicode 编码，那么控制台打印中文就会有问题。

```cpp
// 在工程字符集编码为Unicode时, 使用下面代码设置控制台中文编码，
// 之后控制台就能正常打印中文字符串了。
setlocale(LC_CTYPE, "");

// 控制台输出测试
std::wcout << "这是中文字符串ABC123" << std::endl;
```

大家在实际学习开发中会遇到各种问题，

且有时候搜问题，搜到的东西和你实际要的东西又差别很大，

学会使用现有工具，比如搜索引擎，比如AI工具等。

比如你写一个项目写得很深的时候，

这个时候你没有办法去直接问别人问题，

你没有办法给对方清晰表述你当前项目的各种细节背景，

所以这时候你依赖的就只有搜索引擎和AI工具，以及你的相关经验和直觉。


# 练手游戏-事前准备



## 关闭Windows安全设置

由于我们是游戏辅助开发，会被Windows识别为病毒，

甚至是后面要安装的靶场游戏，也可能会被识别为病毒，因此需要一些设置。

1、先按照下图方式，关闭所有防火墙和软件安全相关的东西，**安全中心**，

![[Pasted image 20251229141724.png]]


2、再使用老师提供的 关闭Win10自动更新.EXE 来关闭 Windows Defender，

![[Pasted image 20251229141743.png]]


3、使用老师提供的工具【Wub_x64.exe】关闭Windows更新，








# 练手游戏-找人物状态



## C++读取游戏变量内存

1、利用前面找到的变量基地址，我们用代码来访问变量。

```cpp
#include <iostream>
#include <Windows.h>

//(1) 人物状态值 = [eax + 0x150]
//(2) 人物状态值 = [eax + 0x58] + 0x150]
//(3) 人物状态值 = [[0xd91788]+ 0x58] + 0x150
//(4) 人物状态值 = [[[0xd91788]+ 0x58] + 0x150]

int main(void)
{
	// 通过 PID 拿到游戏进程句柄
	DWORD gamePid = 6260;
	HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, gamePid);

	// 变量基地址, 但电脑重启会变
	DWORD* address = (DWORD*)0xd91788;

	DWORD nBuffer;
	ReadProcessMemory(hProcess, address, &nBuffer, 4, NULL);
	printf("读出的值是: 0x%x\n", nBuffer);

	address = (DWORD*)(nBuffer + 0x58);
	ReadProcessMemory(hProcess, address, &nBuffer, 4, NULL);
	printf("读出的值是: 0x%x\n", nBuffer);

	address = (DWORD*)(nBuffer + 150);
	ReadProcessMemory(hProcess, address, &nBuffer, 4, NULL);
	printf("读出的值是: 0x%x\n", nBuffer);

	// 同理, 往某个地址里写数据, 就是修改游戏内某个变量内存的值
	// WriteProcessMemory(hProcess, address, &nBuffer, 4, NULL);

	return 0;
}
```





# 汇编基础&OD基础

## 汇编-认识x86寄存器

计算机存储数据的地方分别有(读取速度从大到小) CPU> 内存 > 硬盘

32位通用寄存器的指定名称以及用途：

1. eax 累加器 操作数以及结果数据的累加器，也经常用作一个call的返回值
2. ecx 计数器 字符串和循环操作的计数器
3. edx 用于保存乘法形成的的部分结果或者除法之前部分被除数
4. ebx 基地址，DS段的数据指针，在内存寻址时存放基地址
5. esp 堆栈指针，经常被称为栈顶指针
6. ebp 栈底指针
7. esi 字符串操作的源指针
8. edi 字符串操作的目标指针

（**不用痛苦去记忆，后面用多了就清楚了**）

通用寄存器逻辑结构：
![[Pasted image 20251229140054.png]]

一开始的寄存器是16位，也就是ax、cx、dx等等。

下面在C++工程里，通过内嵌汇编来访问通用寄存器：

```jsx
__asm
{
	mov  eax, 0xAAAAAAAA
	mov   ax, 0xBBBB
}
```

下图是打断点，然后单步调试看到的寄存器效果：
![[Pasted image 20251229140117.png]]


EAX通常存放函数的返回值，紧跟call指令的下一条指令，

用来存放 callee 返回值的，可以提供给 caller 使用，

比如子函数(return 0x20)，那么eax里面的值就是 0x20。

## 汇编-认识OD

解压教程老师提供的OD工具，

然后把 Newxd.exe 设置默认以管理员方式运行，然后发送到桌面快捷方式。这里的管理员权限运行OD，其实是根据目标程序，如果目标程序(游戏)是普通用户权限运行的，也可以不使用管理员权限运行OD。

![[Pasted image 20260301053855.png]]


目标程序：进制演示课件.exe

**OD如何附加**：首先运行目标程序，然后老师定制 **Newxd.exe** 打开后，左上角有个【拖拽】，鼠标左键按住它，然后把它拖拽到目标程序所在窗口，就能完成附加。也可以在左上角【文件】里点击【附加】，来直接附加目标游戏进程。

**OD剥离操作**：鼠标右键 >> StrongOD >> Detach

**OD附加进程**：左上角【文件】>> 【附加】>> 选择你要附加的进程

**OD暂停目标**：左上角黄红色，【暂停】表示程序处于暂停状态，这时候给人一种目标程序卡死状态无法拖动。

**PC指针位置**：左侧边深黑色的高亮(地址列)，类似于书签，表示此时PC指针所处位置。

**OD窗口布局**：主窗口就是反汇编窗口，右边是寄存器窗口，左下角是数据窗口，右下角是堆栈窗口。

**OD断点的意义**：程序要断点暂停下来，看寄存器值等等信息才有意义，否则CPU每时每刻都在高速运转。

**OD注释窗口**：就是在反汇编窗口里，中间有根细线分隔，右边就可以直接写行注释。

**OD地址跳转**：先点中窗口中任意一行，然后 Ctrl+g 进行跳转地址操作。

**OD下断点**：在反汇编窗口里的某一行下断点，直接双击该行的机器码，然后地址变红就表示打上断点。这个断点，也称为 int3断点、软件断点、或者 cc断点。


## 汇编-CPU指令集

指令的功能是什么，去哪儿了解，

叫做英特尔白皮书，

首先找到因特尔官网，然后找到开发人员—》资料和文档—》然后输入并搜索指令集
https://www.intel.cn/content/www/cn/zh/resources-documentation/developer.html

给大家展示原生资料是怎么来的，无需大家去痛苦啃英文资料，当然根据个人需要来。

其实老师也不愿意看这些文档，老师遇到不会用的指令，老师都直接百度搜一下就行。

![[Pasted image 20251229140320.png]]

其中 r是 寄存器 m是内存地址 imm是立即数。

如下图所示，添加我们要测试的指令(比如 `mov ah,al` )，然后单步执行，看看右边寄存器窗口对应寄存器的值。
![[Pasted image 20251229140404.png]]


单步运行汇编指令后，寄存器效果（双击对应的寄存器，可以修改寄存器的值）：
![[Pasted image 20251229140422.png]]

如上图所示，执行结果只改变寄存器指定的字段，寄存器的其他字段值不会改变。



```cpp
mov  dword ptr [0],1   //往0这个内存地址写入数据1,中括号表示内存地址
```

如下图所示，往堆栈这个某个地址写入数据1：
![[Pasted image 20251229140449.png]]



## 汇编-mov和lea

lea的主要用途，在实际逆向中，lea主要用于访问指针。

```cpp
mov     eax, dword ptr [2C5F698]  //把这个内存地址里面的数据赋值到eax寄存器
lea     eax, dword ptr [2C5F698]  //把这个内存地址本身赋值到eax寄存器
```

VS如何查看反汇编代码：

Visual Studio 里，在单步调试状态下，选中对应的 C/C++ 代码行，然后鼠标右键【转到反汇编】。

注意在实际逆向中要特别留意这个lea和mov，很多时候最终数据很容易把lea当作mov来导致跟踪失败。

![[Pasted image 20251229140510.png]]


![[Pasted image 20260301064549.png]]



## 汇编-add和sub

```cpp
mov  eax, 1
inc  eax    //自加1,变成2
dec  eax    //自减1,变成1

mov  eax, 5
add  eax, 2 //结果eax=7
sub  eax, 2 //结果eax=5
```

## 汇编-标志寄存器和跳转

![[Pasted image 20251229140540.png]]




P(Parity/Even奇偶), O(Overflow溢出), C(Carry进位), S(Signal正负标志位),

1、 JE, JZ 结果为零则跳转(相等时跳转) ZF=1
2、 JNE, JNZ 结果不为零则跳转(不相等时跳转) ZF=0
3、 JS 结果为负则跳转 SF=1
4、 JNS 结果为非负则跳转 SF=0
5、 JP, JPE 结果中1的个数为偶数则跳转 PF=1
6、 JNP, JPO 结果中1的个数为偶数则跳转 PF=0
7、 JO 结果溢出了则跳转 OF=1
8、 JNO 结果没有溢出则跳转 OF=0
9、 JB, JNAE 小于则跳转 (无符号数) CF=1
10、 JNB, JAE 大于等于则跳转 (无符号数) CF=0
11、 JBE, JNA 小于等于则跳转 (无符号数) CF=1 or ZF=1
12、 JNBE, JA 大于则跳转(无符号数) CF=0 and ZF=0
13、 JL, JNGE 小于则跳转 (有符号数) SF≠ OF
14、 JNL, JGE 大于等于则跳转 (有符号数) SF=OF
15、 JLE, JNG 小于等于则跳转 (有符号数) ZF=1 or SF≠OF
16、 JNLE, JG 大于则跳转(有符号数) ZF=0 and SF=OF

j:jump跳转
e:equal相等
n:not不
b:below低于
a:above高于
l:less少于
g:greater大于
s:sign有符号
c:carry借位
p:parity奇偶
o:overflow溢出
z:zero零


## 汇编-位运算

指令列表: AND、OR、NOT(把每个位取反)

```cpp
mov  eax, 1
and  eax, 2  //结果eax=0
or   eax, 2  //结果eax=2
not  eax     //结果eax=0xFFFFFFFD
```

## 汇编-cmp和test

cmp和sub运算效果一样，也是做减法，也会改变标志寄存器对应的位，

但它和sub不同，它不会把减法后的结果写回到目标寄存器。

cmp经常会和条件跳转指令一起使用，即用过cmp之后，紧接着会使用跳转指令。

![[Pasted image 20251229140639.png]]


test和and运算效果一样，也是做位运算与操作，也会改变标志寄存器对应的位，

但它和and不同，它不会把运算后的结果写回到目标寄存器。

test经常会和条件跳转指令一起使用，即用过test之后，紧接着会使用跳转指令。

![[Pasted image 20251229140657.png]]


## 汇编-数据边界和溢出

数据类型的边界和溢出
![[Pasted image 20251229140715.png]]


用上面这张图彻底搞明白有符号到无符号的边界范围。

下面是通过VS调试查看边界：

![[Pasted image 20251229140737.png]]


## 汇编-逆向if语句

在反汇编中，变量a不应该显示在这里，这里显示的是伪代码，可以取消勾选【显示符号名】：
![[Pasted image 20251229140811.png]]



## 汇编-逆向switch语句

下面是swich的反汇编代码，这里由于我们还没有学习ebp堆栈相关的东西，所以这里我们不用关心ebp相关的东西，就只当它是一个寄存器，或者一个内存地址。

```cpp
	int a = 1;
00035736  mov         dword ptr [ebp-8],1  

	switch (a)
0003573D  mov         eax,dword ptr [ebp-8]  
00035740  mov         dword ptr [ebp+FFFFFF30h],eax  
00035746  cmp         dword ptr [ebp+FFFFFF30h],1  
0003574D  je          0003575A  
0003574F  cmp         dword ptr [ebp+FFFFFF30h],2  
00035756  je          00035769  
00035758  jmp         00035776  
	{
	case 1:
	{
		printf("1\\n");
0003575A  push        39B30h  
0003575F  call        0003144C  
00035764  add         esp,4  
		break;
00035767  jmp         00035776  
	}
	case 2:
	{
		printf("2\\n");
00035769  push        39B34h  
0003576E  call        0003144C  
00035773  add         esp,4  
		break;
	}
	default:
	{
		break;
	}
	}

```

当swich里的分支超过3个之后，编译器会通过向量的方式来跳转：
![[Pasted image 20251229140834.png]]



## 汇编-逆向循环语句

下面通过 VS反汇编代码来看看循环语句，

在实际逆向过程中，这种往上跳转的，要么是循环要么是goto语句。

```cpp
002C5D35  nop  
	int a = 1;
002C5D36  mov         dword ptr [ebp-8],1  

	while (a > 0)
002C5D3D  cmp         dword ptr [ebp-8],0  
002C5D41  jle         002C5D52  
	{
		printf("a\\n");
002C5D43  push        2C9B30h  
002C5D48  call        002C144C  
002C5D4D  add         esp,4  
	}
002C5D50  jmp         002C5D3D 
```

do-while循环的逆向分析

```cpp
	int a = 1;
00EC5D36  mov         dword ptr [ebp-8],1  

	do
	{
		printf("a\\n");
00EC5D3D  push        0EC9B30h  
00EC5D42  call        00EC144C  
00EC5D47  add         esp,4  
	} while (a > 0);
00EC5D4A  cmp         dword ptr [ebp-8],0  
00EC5D4E  jg          00EC5D3D       //jump if greater
```

for循环的逆向分析

```cpp
005D2C55  nop  
	int a = 0;
005D2C56  mov         dword ptr [ebp-8],0  
	for (size_t i = 0; i < 10; i++)
005D2C5D  mov         dword ptr [ebp-14h],0  
005D2C64  jmp         005D2C6F  
005D2C66  mov         eax,dword ptr [ebp-14h]  
005D2C69  add         eax,1  
005D2C6C  mov         dword ptr [ebp-14h],eax  
005D2C6F  cmp         dword ptr [ebp-14h],0Ah  
005D2C73  jae         005D2C7E  
	{
		a = 1;
005D2C75  mov         dword ptr [ebp-8],1  
	}
005D2C7C  jmp         005D2C66
```

## 汇编-push和pop

从这节课开始，后续的指令是为了理解函数的，

push —— 把字或者双字压入堆栈(栈)，

来个最简单的例子: `push 1`
![[Pasted image 20251229140908.png]]


出栈: `pop eax` ，把栈内的数据弹出栈，并存放到 eax 寄存器里，并且 esp 会自动变更。

堆栈的知识以及相关指令很重要，这个是后面逆向动态调试的重要技能。

## 汇编-EIP寄存器

EIP寄存器，指向的是即将要执行的代码段地址，相当于PC指针。

jmp、call、ret、eip

![[Pasted image 20251229140932.png]]


## 汇编-call和retn

call和jmp，很类似，而jmp是直接跳转，

jmp是直接跳转，是无法返回的，因为返回信息已经丢失，

call会把当前指令的下一个指令地址保存到堆栈里，如下图所示：
![[Pasted image 20251229140948.png]]


call目标地址执行完之后，目标子函数最后执行retn来返回。


其中，EIP 其实就是PC指针，ESP 其实就是SP寄存器，SP始终指向栈内的最低地址。




## 汇编-VS初识堆栈

下面是VS实验代码，非常简单，用于探究函数的堆栈：

```cpp
#include <Windows.h>
#include <iostream>

int add(int a, int b)
{
	return a + b;
}

int main(int argc, const char* argv[])
{
	int a = 1;
	int b = 2;
	add(a, b);
	return 0;
}
```

VS里，把上述代码随便打个断点，然后进入调试模式，然后查看反汇编代码：

```cpp
00981FE0  push        ebp       //保存上一个ebp
00981FE1  mov         ebp,esp   //设置新的ebp
00981FE3  sub         esp,0D8h  //设置新的esp
00981FE9  push        ebx       //其他寄存器的压栈保存
00981FEA  push        esi  
00981FEB  push        edi
...//忽略编译器加的代码
	int a = 1;
00982006  mov         dword ptr [ebp-8],1
	int b = 2;
0098200D  mov         dword ptr [ebp-14h],2
	add(a, b);
00982014  mov         eax,dword ptr [ebp-14h]  
00982017  push        eax        //把第2个参数b的值压栈
00982018  mov         ecx,dword ptr [ebp-8]  
0098201B  push        ecx        //把第1个参数a的值压栈
0098201C  call        00981465   //调用 callee
00982021  add         esp,8
```

我们再看看 callee 这边的反汇编代码：

```cpp
int add(int a, int b)
{
00981E70  push        ebp  
00981E71  mov         ebp,esp  
00981E73  sub         esp,0C0h  
00981E79  push        ebx  
00981E7A  push        esi  
00981E7B  push        edi  
...//忽略编译器加的代码
00981E91  nop  
	return a + b;
00981E92  mov         eax,dword ptr [ebp+8]    //+4是返回地址, +8是第1个参数
00981E95  add         eax,dword ptr [ebp+0Ch]  //+C是第2个参数
}
```

## 汇编-函数的调用约定

函数约定就是告诉编译器怎么传递参数，怎么传递返回值，怎么平衡堆栈。

**__cdecl:**

C/C++默认方式，参数从右向左入栈，主调函数负责栈平衡。外平栈 —— 谁调用，谁负责。

**__stdcall**：

windows API默认方式，参数从右向左入栈，被调函数负责栈平衡。内平栈 —— 只调用，不负责。

**__fastcall：**

快速调用方式。所谓快速，这种方式选择将参数优先从寄存器传入（ECX和EDX），剩下的参数再从右向左从栈传入。因为栈是位于内存的区域，而寄存器位于CPU内，故存取方式快于内存，故其名曰“__fastcall”内平栈

__cdecl 外平栈:

```cpp
	int c = add(2, 5);
000718C6  push        5  
000718C8  push        2  
000718CA  call        000712C6  
000718CF  add         esp,8     //call返回出来之后,进行栈平衡
```

__stdcall 内平栈:

```cpp
int __stdcall add(int a, int b)
{
00131820  push        ebp  
00131821  mov         ebp,esp  
00131823  sub         esp,0E4h  
...//忽略编译器加的代码
00131845  nop  
	int c = 1;
00131846  mov         dword ptr [ebp-8],1  
	int d = 2;
0013184D  mov         dword ptr [ebp-14h],2  
	int e = a + b;
00131854  mov         eax,dword ptr [ebp+8]  
00131857  add         eax,dword ptr [ebp+0Ch]  
0013185A  mov         dword ptr [ebp-20h],eax  
	return e;
0013185D  mov         eax,dword ptr [ebp-20h]  
}
00131860  pop         edi  
00131861  pop         esi  
00131862  pop         ebx  
00131863  add         esp,0E4h  
00131869  cmp         ebp,esp  
0013186B  call        00131244  
00131870  mov         esp,ebp  
00131872  pop         ebp  
00131873  ret         8         //在这里进行栈平衡
```

__fastcall 内平栈:

```cpp
	int c = add(2, 5);
001F18C6  mov         edx,5      //直接把参数放到寄存器
001F18CB  mov         ecx,2      //直接把参数放到寄存器
001F18D0  call        001F13C5  
001F18D5  mov         dword ptr [ebp-8],eax 

int __fastcall add(int a, int b)
{
001F1820  push        ebp  
001F1821  mov         ebp,esp  
001F1823  sub         esp,0FCh  
...//忽略编译器加的代码
001F184D  nop  
	int c = 1;
001F184E  mov         dword ptr [ebp-20h],1  
	int d = 2;
001F1855  mov         dword ptr [ebp-2Ch],2  
	int e = a + b;
001F185C  mov         eax,dword ptr [ebp-8]  
001F185F  add         eax,dword ptr [ebp-14h]  
001F1862  mov         dword ptr [ebp-38h],eax  
	return e;
001F1865  mov         eax,dword ptr [ebp-38h]  
}
001F1868  pop         edi  
001F1869  pop         esi  
001F186A  pop         ebx  
001F186B  add         esp,0FCh  
001F1871  cmp         ebp,esp  
001F1873  call        001F1244  
001F1878  mov         esp,ebp  
001F187A  pop         ebp  
001F187B  ret   //由于2个参数直接给寄存器了,没有压栈,所以这里无需栈平衡,直接返回
```

## 汇编-数组与内存布局

下面通过两个简单的数组，探究数组元素在内存中的布局特征：

```cpp
#include <Windows.h>
#include <iostream>

int main(int argc, const char* argv[])
{
	int a[4] = { 1, 2, 3, 4 };
	int b[2][2] = { {5,6}, {7,8} };
	return 0;
}
```

下面是其内存布局特征：无论一维二维，数据都是线性从左往右排布。

![[Pasted image 20251229141146.png]]


## 汇编-字符串与编码

ASCII、UTF-8、Unicode(宽字节编码)、Big5(台湾繁体字)

中文在内存的编码规则，我们不需要知道它的转换规则，

但是我们要能大致识别它们，属于哪种编码，在内存中存放是什么样的特征，

我们使用 Cheat Engine.exe 来查看中文字符串在不同编码下的特征，

Cheat Engine.exe 是一个专门用来查看内存和修改内存的一个工具，非常好用。

![[Pasted image 20251229141209.png]]


9、在上图中，步骤8所在位置，鼠标右键【浏览相关内存区域】，

![[Pasted image 20251229141224.png]]

如上图所示，代码页表示 ASCII 编码方式，一个中文占2个字节，其他字母数字占1个字节。其对应的编码为 GBK 编码。

下面查看其 Unicode 宽字节编码的内存组织方式: 中文占3个字节，其他字母数字占2个字节。

![[Pasted image 20251229141248.png]]


Unicode 编码下，所有单字符至少占用2个字节。

两个都不勾选，则默认编码为 UTF-8 格式: 中文占3个字节，其他字母数字占1个字节。

![[Pasted image 20251229141319.png]]

Big5 编码暂时没法演示，但是很好区分，只要在内存里看到繁体，大概率就是 Big5 编码。

VS工程中的字符集设置：

![[Pasted image 20251229141335.png]]


字符集类型：Unicode字符集（UTF-16），编码：UTF-16，字节数：2 或 4 字节（变长）

字符集类型：多字节字符集，编码：GBK(中文)，字节数：1-2 字节（变长）

字符集类型：宽字节，编码：wchar_t，字节数：2 字节（通常）

字符集类型：UTF-8，编码：UTF-8，1-4 字节（变长）

在多字节模式下，字符串字面量是 `char*` 类型， `MessageBoxA`（多字节），

char 叫多字节，比如一个字母占1个字节，一个中文占2个字节；

在 Unicode 模式下，字符串字面量是 `wchar_t*` 类型，`MessageBoxW`（Unicode）。 wchar_t 叫宽字符，其一个字符至少占用2字节，由此得出编码为 GBK。





# bottom





