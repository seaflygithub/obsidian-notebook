
草稿：[[微尘网络游戏逆向C++.excalidraw]]



# 工具基础-CheatEngine


下面即将进入32位网络游戏辅助开发的教程，靶场的意思是游戏不更新，用来给大家熟悉逆向流程。这一阶段的第一节课老师不会讲太多的东西。第一节课老师更希望是能够激发起大家对逆向开发的兴趣，有兴趣的话，你能学得更好，能坚持得更久。我们先来讲一下CE(Cheat Engine)，官网在: https://www.cheatengine.org/

大家肯定很早就对逆向感兴趣了，所以多多少少也接触过用过CE。但是，大家会发现自己了解的那一套时灵时不灵，有的游戏改得了，有的游戏改不了，有的游戏甚至附加都附加不上，那么我们这里微尘呢就是教大家系统地学习，能搞定所有的游戏，能把所有底层的东西都能给它了解透彻，具体是怎么一回事，那我们第一节课呢，不会讲那么多内容，我们要一节课一节课地来讲，我们还要写代码，还有很多很多的内容去做，我们一步一步的来，一天吃不成一个胖子。


## CE查找血量

明确的数值，且是明确的整型值，附加到指定游戏进程后，可以根据血量数值变化定位到其进程内的地址。


## CE查找角色状态


比如天龙八部，为什么我们要找角色状态标志？因为当你去做一个辅助的时候，你需要及时地直到特定角色当前正在干什么，正在打坐、正在走路、正在站着不动等等。针对不同的状态，我们需要有一个不同的判断和处理。所以我们需要找到这个存放状态的内存地址。



## CE查找字符串

比如下图所示，查找角色名字，字符串类型。下图CE中注意右侧的【代码页】和【UTF-16】，两者分别对应的是多字节字符集(ANSI) 和 Unicode 字符集，两者二选一。

![[Pasted image 20251229145752.png]]



## CE定位变量地址


**V1-CE查找目标变量绝对地址**

比如人物状态这个变量，老师演示的是天龙八部，里面的主角角色的状态有正在打坐、正在走路、正在站着不动等等。老师演示了用CE直接查找这个状态，最终找到了状态的绝对地址。但是有个问题，这个绝对地址，当游戏重启后或者人物切换地图后，这个绝对地址就失效了，就不再是人物状态的地址了。


**V2-CE查找目标变量基地址**

```txt
1、CE找到的人物状态变量绝对地址: 0x2BCAED78

2、鼠标右键该地址,选择【是谁访问了该地址】

3、cmp dword ptr [eax + 0x150], 02
   
   得知[eax + 0x150]的值和0x02这个状态值比较

4、eax + 0x150 = 变量绝对地址 0x2BCAED78

   根据汇编代码从下往上追,下面就是不断追出来的过程:
   (1) 人物状态值 = [eax+0x150]
   (2) 人物状态值 = [eax+0x58]+0x150]
   (3) 人物状态值 = [[0xd91788]+0x58]+0x150
   (4) 人物状态值 = [[[0xd91788]+0x58]+0x150]

   其中 0xd91788 就是这个人物状态的基地址,
   且偏移 0x58、0x150 这些不会变, 因为这些偏移是写死写进汇编代码里的,
   除非游戏更新代码改动了, 因此基地址和偏移都是后续要用到的。
```



**V3-OD查找目标变量基地址**

上面只是讲课演示的简单变量查找，现实中大多数变量不可能简单往上看几行汇编代码就能找到变量基地址的，可能在其他函数代码里。这时候用 CE 找变量基地址就比较吃力了，因为它能看到的汇编代码范围有限，这时候就需要OD等调试工具来在整个游戏代码里全局往上追地址了。


# 工具基础-OD调试器




## OD附加和脱离

1、附加好理解，但是脱离，操作不好，导致程序退出。

2、这里重点讲脱离，脱离之前，确保目标程序让他处于运行状态，然后再在汇编窗口右键操作选择 detach 来脱离，这样就不会影响到目标程序的运行。

![[Pasted image 20260302104858.png]]







## OD让程序运行起来


如下图所示，附加目标游戏后，先点击1让其运行起来，这是能看到2的状态是运行，如果此时游戏界面还是卡死状态，那么继续进行步骤3，点击那个T(Threads)，然后鼠标右键把所有线程恢复运行。步骤4是切换回汇编代码这个界面。

![[Pasted image 20260302094102.png]]

![[Pasted image 20260302094515.png]]



## OD全局查找注释定位点

![[Pasted image 20260302103031.png]]


![[Pasted image 20260302123322.png]]


## OD进入函数和回退


1、鼠标定位到 call 汇编行，然后双击汇编或者按回车键，即可进入callee的函数头部。

2、基于上面操作后，我想回退，直接按一下减号，反向操作则按加号(shift+=)。


## OD执行往上返到caller

1、如果断点触发了，并且程序暂停了，此时按一下 Ctrl+F9，即可执行完当前callee，回到 caller 的调用点，或者 OD 上面菜单栏上有个【调试 --> 执行到返回】效果也一样。


## OD数据窗口显示



如下图所示：
1、鼠标单击数据窗口；
2、执行内存数据查看命令，回车，即可在数据窗口看到内存数据。
![[Pasted image 20260303113013.png]]


下面是常用的几种内存查看格式：
```txt
db [[0xba123+0x111] + 0x222] 其中db是以单字节显示

dd [[0xba123+0x111] + 0x222] 其中dd是以4字节dword显示

du [[0xba123+0x111] + 0x222] 其中du是以Unicode形式显示

dw [[0xba123+0x111] + 0x222] 其中dw是以word长度显示出来
```





## OD常用功能点

如下图所示，有打开和附加，【打开】是直接用OD运行目标程序，而附加常用在大型程序，比如游戏很大，你如果不用附加的话，游戏是打不开的。

![[Pasted image 20251229142211.png]]

代码窗口，和数据窗口，都是内存地址，只不过代码窗口是以汇编代码来识别，

Ctrl+G 跳转，可以输入函数名称，也可以输入地址(比如: 0x666)；

![[Pasted image 20251229142225.png]]


还有，如果窗口布局乱了，直接在标题栏空白处双击，就能归位布局。

![[Pasted image 20251229142247.png]]


L —— 表示日志

E —— 表示模块，比如微信，它会显示相关的所有文件，并不只有wechat.exe

![[Pasted image 20251229142305.png]]


T —— 是线程，表示当前程序运行了哪些线程

![[Pasted image 20251229142320.png]]

W —— 显示当前程序的窗口

![[Pasted image 20251229142337.png]]


C —— Com back 表示回到我们常规的反汇编状态

K —— 显示堆栈，这个只有运行遇到断点断下来了才能看到

B —— 显示断点

上面只是我们常用的很少的点，不会这么简单，

只是这里让大家循序渐进熟练一下，

OD是一个动态调试器，后续我们就要用 OD 来动态调试程序，



# 注入基础-注入相关的技术












## 初识跨进程和注入

为什么要分为跨进程和注入？跨进程那种方式，适合代码量少、功能简单的场景；而如果辅助的功能比较复杂，代码量比较多，那么就适合通过注入的方式来写。

什么是注入？它是我们实现的一个辅助程序，它是DLL的形式，它无法独立运行，需要注入到目标进程上才能运行。并且一旦 DLL 注入到目标进程后，那么DLL将拥有该进程的地址空间，可以直接访问相关地址(比如指针引用)，而无需像跨进程那样需要手动获取地址空间(比如 ReadProcessMemory)。我们通过VS编写的DLL代码，注入到目标游戏之后，代码就成为游戏的一部分了。



## 创建MFC对话框DLL

上节课老师不是找到了人物名字基地址嘛，

这节课先画个窗口出来，注入进去，

然后下一节课讲怎么注入的，注入代码怎么写，

然后再下一节课老师就讲怎么把名字显示到界面上，

那么老师为什么要注入进去，

因为老师之前演示的跨进程读写的方式，跨进程读写那种方式比较适合代码量比较少的方式，

老师实际中会写主线，会写Lua来达到目的，这个时候呢，功能比较复杂代码量多，

所以呢用跨进程读写这个方式不是很合适，更适合用注入的方式来写，

注入的方式是什么意思呢，

就是我们会做一个程序，这个程序是DLL的形式，它没有办法独立运行，

需要注入到别的程序上面，比如注入到游戏，然后才能运行，

所以呢，我们要画一个带有MFC窗口的DLL，然后呢去依附着游戏程序来运行，


为什么要创建MFC对话框DLL？而不是控制台形式的DLL？因为我们需要把辅助程序注入后，辅助能够停留供我们操作，比如点击按钮实现什么功能之类的，然后点击退出才完成辅助的退出和资源回收。


下面我们开始用VS创建MFC项目，大家VS可能没有安装MFC组件，我们使用如下安装器来安装，下载大约200多MB，然后安装完之后，我们开始后面的建立MFC工程。

![[Pasted image 20251229142621.png]]

![[Pasted image 20251229142643.png]]


上述MFC组件安装完之后，重新打开VS，通过 “MFC 动态链接库” 新建工程：
![[Pasted image 20251229142658.png]]


选择静态的选项，否则你做出来的东西不完整，无法依附到游戏上，
![[Pasted image 20251229142719.png]]


然后选择x86，别选择x64，因为我们的目标游戏是32位的，

下面是一些常用的窗口菜单，

![[Pasted image 20251229142738.png]]


下面我们来添加资源，首先双击右边的 .rc 文件，

进入资源视图窗口后，右键顶层 .rc 选择 “添加资源”，如下图所示：

![[Pasted image 20251229142752.png]]



在弹出的小窗口中，双击 “Dialog”，然后就会添加一个对话框窗口，

然后紧接着在空白处右键并添加类，

![[Pasted image 20251229142811.png]]


下面开始改代码了，直接改DLL的入口文件，上面为 WCDXF.cpp，

主要修改点如下：

```cpp
static DWORD ShowDlg(LPVOID lpThreadParameter)
{
	OutputDebugString("流程执行3");
	DXFDlg *dxf = new DXFDlg();

	//以模态窗口显示
	OutputDebugString("流程执行4");
	dxf->DoModal();// 该调用会阻塞在此,除非用户主动关闭窗口
	OutputDebugString("流程执行5");

	delete dxf;
	FreeLibraryAndExitThread(theApp.m_hInstance, 1);
	return 0;
}

BOOL CWCDXFApp::InitInstance()
{
	//这里是DLL最开始执行的地方
	OutputDebugString("流程执行1");
	
	//双冒号表示使用Windows标准API,否则会使用MFC的API
	::CreateThread(0, 0, (LPTHREAD_START_ROUTINE)ShowDlg, 0, 0, 0);
	OutputDebugString("流程执行2");

	CWinApp::InitInstance();

	return TRUE;
}
```

可以用老师提供的 进制演示课件.exe 作为被注入对象，DebugView 显示信息:
```txt
注入DLL,弹出模态窗口时:
	流程执行1
	流程执行2
	流程执行3
	流程执行4
点击模态窗口的确认按钮后:
	流程执行5

当在 CWinApp::InitInstance() 之前睡眠10秒, Sleep(10000)
	开始注入:
		流程执行1
		流程执行2
	卡住10秒,10秒后打印:
		流程执行3
		流程执行4
	InitInstance()表示MFC DLL总入口, 前面创建线程, 但并没有被调度,
	只有等总入口被调用后,MFC DLL全局执行环境初始化完毕, 其他线程才能正常使用MFC的API
```



什么是模态窗口？

比如一个程序有两个独立的窗口，A窗口在前，B窗口在后，

假设A窗口为模态窗口，那么点击B窗口会发出 “蹦蹦蹦” 的警告音，并且点不了B窗口，

这就是模态窗口。

上述执行到 `DXF.DoModal();` 这句位置，会一直卡在这个位置，

除非你主动把该窗口关闭了，代码才会继续往下执行，

FreeLibraryAndExitThread 就是把这个DLL线程卸载和杀死，

OutputDebugString 用于调试打印，该函数会把信息打印到窗口上，

Dbgview.exe

这时候我们需要用到这个工具，最好是以管理员方式打开它，

然后我们过滤信息，只显示包含 “执行流程” 字样的信息，

![[Pasted image 20251229142830.png]]


![[Pasted image 20251229142844.png]]



接下来还有一个工具，是malloc老师自己写的注入工具，后续课程老师给大家讲怎么写出这个工具，

wctool.exe

老师使用注入工具，把我们刚刚编写的DLL文件注入到了DNF游戏里，

并且看到了 DebugView 窗口的打印信息，

![[Pasted image 20251229142905.png]]



我们后续的课程直接用这个工具来注入我们开发的DLL，本阶段最后一节课就教大家自己实现这个注入工具，它其实就是调用Windows函数实现远线程注入。

## 远线程注入的实现

前面我们使用的是老师提供好的注入工具，

微尘开发了一个注入工具，其用到的核心函数列表：

OpenProcess

VirtualAllocEx

WriteProcessMemory

CreateRemoteThread

WaitForSingleObject

CloseHandle、VirtualFreeEx

从课程看出，老师其实也不熟练编程，各个函数的参数也要去查，平时都是复制粘贴，我们一生很短，不可能把每个东西都学得很精通，所以我们主要学习的就是缝合技术，特别是编程，你写过一遍，有个基本印象就可以了，以后用到直接翻源码，或者上网查，一查到，看看源码一看就知道怎么用了，不可能事事精通，人的精力有限。

如何把自己编写的DLL注入到目标进程里，这是老师实现的简化版本：

```cpp
#include <windows.h>
#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    // 检查命令行参数
    if (argc != 3) {
        std::cerr << "用法: " << argv[0] << " <进程ID> <DLL路径>" << std::endl;
        return 1;
    }

    // 获取进程ID和DLL路径
    DWORD pid = std::stoul(argv[1]);
    const char* dllpath = argv[2];
    DWORD vsize = 0x4000;
    SIZE_T wrlen;

    // 打开游戏进程
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, 0, pid);
    
    // 申请内存块
    LPVOID vaddr = VirtualAllocEx(hProcess, NULL, vsize, 
        MEM_COMMIT, PAGE_EXECUTE_READWRITE);

    // 把DLL路径写入虚拟地址
    WriteProcessMemory(hProcess, vaddr, dllpath, vsize, &wrlen);

    // 利用线程来调用 LoadLibrary
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, 
        (LPTHREAD_START_ROUTINE)LoadLibrary, vaddr, 0, NULL);

    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);
    
    VirtualFreeEx(hProcess, vaddr, 0, MEM_RELEASE);
    CloseHandle(hProcess);
    return 0;
}
```

下面我们借助AI来完成代码编写：Windows编程中，使用上述函数，实现一个注入器，能够把我们自己编写的DLL注入到目标进程里运行起来。

```cpp
#include <windows.h>
#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    // 检查命令行参数
    if (argc != 3) {
        std::cerr << "用法: " << argv[0] << " <进程ID> <DLL路径>" << std::endl;
        return 1;
    }

    // 获取进程ID和DLL路径
    DWORD processId = std::stoul(argv[1]);
    const char* dllPath = argv[2];

    // 打开目标进程
    HANDLE hProcess = OpenProcess(
        PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION |
        PROCESS_VM_WRITE | PROCESS_VM_READ,
        FALSE,
        processId
    );

    if (hProcess == NULL) {
        std::cerr << "无法打开目标进程，错误码: " << GetLastError() << std::endl;
        return 1;
    }

    std::cout << "成功打开目标进程，进程ID: " << processId << std::endl;

    // 在目标进程中分配内存
    LPVOID pDllPath = VirtualAllocEx(
        hProcess,
        NULL,
        strlen(dllPath) + 1,
        MEM_COMMIT,
        PAGE_READWRITE
    );

    if (pDllPath == NULL) {
        std::cerr << "无法在目标进程中分配内存，错误码: " << GetLastError() << std::endl;
        CloseHandle(hProcess);
        return 1;
    }

    std::cout << "成功在目标进程中分配内存，地址: " << pDllPath << std::endl;

    // 写入DLL路径到目标进程
    if (!WriteProcessMemory(hProcess, pDllPath, dllPath, strlen(dllPath) + 1, NULL)) {
        std::cerr << "无法写入DLL路径到目标进程，错误码: " << GetLastError() << std::endl;
        VirtualFreeEx(hProcess, pDllPath, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return 1;
    }

    std::cout << "成功写入DLL路径到目标进程" << std::endl;

    // 获取LoadLibraryA函数地址
    HMODULE hKernel32 = GetModuleHandleA("kernel32.dll");
    LPTHREAD_START_ROUTINE pLoadLibraryA = (LPTHREAD_START_ROUTINE)GetProcAddress(hKernel32, "LoadLibraryA");

    if (pLoadLibraryA == NULL) {
        std::cerr << "无法获取LoadLibraryA函数地址，错误码: " << GetLastError() << std::endl;
        VirtualFreeEx(hProcess, pDllPath, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return 1;
    }

    // 在目标进程中创建远程线程，调用LoadLibraryA加载DLL
    HANDLE hThread = CreateRemoteThread(
        hProcess,
        NULL,
        0,
        pLoadLibraryA,
        pDllPath,
        0,
        NULL
    );

    if (hThread == NULL) {
        std::cerr << "无法在目标进程中创建远程线程，错误码: " << GetLastError() << std::endl;
        VirtualFreeEx(hProcess, pDllPath, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return 1;
    }

    std::cout << "成功在目标进程中创建远程线程，线程ID: " << GetThreadId(hThread) << std::endl;

    // 等待远程线程执行完成
    std::cout << "等待DLL加载完成..." << std::endl;
    WaitForSingleObject(hThread, INFINITE);

    // 获取远程线程的返回值（LoadLibraryA的返回值是DLL句柄）
    DWORD dllHandle = 0;
    GetExitCodeThread(hThread, &dllHandle);

    if (dllHandle != 0) {
        std::cout << "DLL成功注入到目标进程，DLL句柄: " << std::hex << dllHandle << std::endl;
    }
    else {
        std::cerr << "DLL注入失败，LoadLibraryA返回0" << std::endl;
    }

    // 清理资源
    CloseHandle(hThread);
    VirtualFreeEx(hProcess, pDllPath, 0, MEM_RELEASE);
    CloseHandle(hProcess);

    std::cout << "资源已释放，注入过程完成" << std::endl;
    return 0;
}

```

只要这个游戏没有注入相关的限制，只要你注入成功了，你这个DLL就成为该游戏的一部分了。

一旦你注入成功，就会从DLL入口函数开始执行，直到执行到前面调用的模态窗口显示出来。

## VS2022远程调试

当你们遇到问题，比如注入的时候崩溃，或者说注入之后，点某个按钮崩溃，

可以通过在DLL相应代码位置加调试打印，结合 DbgView 来看看它崩在哪一行，

还有一种动态调试的方法，

就是通过 【VS —》调试 —》附加到进程 —》选择目标进程】，

然后你就可以在VS里下断单步调试了。



# VS MFC 开发基础


## MFC控件日志窗口


![[Pasted image 20260303162206.png]]


如下图所示，修改控件属性(比如垂直滚动、多行等等)，以满足日志显示的基本功能需求。
![[Pasted image 20260303162547.png]]



**为 Edit Control 关联变量**

如下图所示：
- 右键控件 → 类向导 → 成员变量 → 添加变量，变量名建议 `m_ctlLogEdit`，类型选 `CEdit`。
- 拖入一个 Button 按钮，Caption 设为 “清空日志”，为其添加点击事件（BN_CLICKED），函数名建议 `OnBnClickedBtnClearLog`。

![[Pasted image 20260303163558.png]]




**实现日志写入和清空的接口**

下面是对话框头文件参考内容(DXFDlg.h): 
```cpp
// 你的对话框类
class DXFDlg : public CDialogEx
{
	DECLARE_DYNAMIC(DXFDlg)

public:
	DXFDlg(CWnd* pParent = nullptr);   // 标准构造函数
	virtual ~DXFDlg();

// 对话框数据
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_DIALOG1 };
#endif

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV 支持

	DECLARE_MESSAGE_MAP()
public:

	// 日志控件成员变量 m_ctlLogEdit
	CEdit m_ctlLogEdit;

	// 追加日志的接口（核心）
	void AppendLog(CString strLog);

	// 清空日志的接口
	void ClearLog();

	// 清空日志按钮的点击事件
	afx_msg void OnBnClickedBtnClearLog();

	// 你的其他事件接口...
};
```


下面是对话框源文件参考内容(DXFDlg.cpp)：
```cpp

DXFDlg::DXFDlg(CWnd* pParent /*=nullptr*/)
	: CDialogEx(IDD_DIALOG1, pParent)
{

}

DXFDlg::~DXFDlg()
{
}

void DXFDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);

	// 绑定控件ID和成员变量
	DDX_Control(pDX, IDC_EDIT_LOGMSG, m_ctlLogEdit);
}

BEGIN_MESSAGE_MAP(DXFDlg, CDialogEx)
	// 添加点击事件的绑定
	ON_BN_CLICKED(IDC_BUTTON_CLEAR_LOGMSG, &DXFDlg::OnBnClickedBtnClearLog)

	// 你的其他事件...
END_MESSAGE_MAP()

// 追加日志的实现：自动换行、自动滚动到底部
void DXFDlg::AppendLog(CString strLog)
{
    // 1. 获取当前编辑框内容
    CString strContent;
    m_ctlLogEdit.GetWindowText(strContent);

    // 2. 追加新日志（加换行符）
    if (!strContent.IsEmpty())
    {
        strContent += _T("\r\n"); // 换行，兼容Windows换行格式
    }
    strContent += strLog;

    // 3. 设置回编辑框
    m_ctlLogEdit.SetWindowText(strContent);

    // 4. 自动滚动到底部（关键：让滚动条跟随最新日志）
    int nLength = m_ctlLogEdit.GetWindowTextLength();
    m_ctlLogEdit.SetSel(nLength, nLength); // 选中最后一个字符
    //m_ctlLogEdit.ScrollCaret();            // 滚动光标到可视区域
}


// 清空日志的实现
void DXFDlg::ClearLog()
{
    m_ctlLogEdit.SetWindowText(_T("")); // 清空编辑框内容
}

// 清空日志按钮点击事件（调用清空接口）
void DXFDlg::OnBnClickedBtnClearLog()
{
    ClearLog();
}
```




# 保护机制-游戏过检测过保护


## DXF内存访问过检测


特征1：弹窗提示出错，然后点击确定后才退出程序。


如下图所示，DXF靶场，无论老师演示还是学生实操，在调试操作过程中，一旦尝试访问(读or写)游戏内某些内存，会触发**游戏保护机制**，DXF这里表现为会弹窗(MessageBoxW)，然后当点击消息窗口确认后，游戏直接终止退出了。

反调试 + 内存保护（Anti-Debug + Memory Protection）

1、2、3、当我们用CE调试器尝试窥探内存；
4、执行完上面3步后，触发了检测弹窗，此时游戏已经卡死没法继续调试or运行了；
4、同理，比如在OD里下硬件访问断，也会触发该保护机制。
![[Pasted image 20260303181833.png]]


本小节就是专门解决这个问题，让我们能够自由访问游戏内存。

如下图所示，OD代码窗口中 【Ctrl+G】先找到 MessageBoxA 和 MessageBoxW 函数，然后在其各自返回处之前下个断点。
![[Pasted image 20260305175054.png]]

如下图所示，然后去CE随便找个内存地址，当然是能够触发保护机制的地址，然后下个硬件写入断，不出意外，一旦下断，立马触发保护机制，然后就会断在 MessageBoxW 断点处。
![[Pasted image 20260305174831.png]]


前面老师通过往上返，返到上一层后程序就终止了，不好追，并且上层代码有VM混淆保护。于是老师把目光转移到 OD 的堆栈窗口，并且老师强调，堆栈只能是辅助你查找线索。
![[Pasted image 20260305175555.png]]


如下图所示，通过堆栈那边的回车，返到 caller 调用点，然后只要不调用它，即可绕过保护机制，于是老师把上一行的 je 指令直接改成 jmp 指令，并记下它的机器码和内存地址。
![[Pasted image 20260305175855.png]]


如下图所示，直接改跳转指令，改成无条件跳转：
![[Pasted image 20260305180320.png]]


如下图所示，下面是修改之后的指令机器码，记住这条指令的内存地址(0x755B88)，以及机器码(EB)。
![[Pasted image 20260305180424.png]]


---

如下图所示，接下来就是重启游戏，然后用 CE 直接改那个地址的指令，改成我们想要的机器码，这样后续你下内存访问断就不会触发该保护机制了：
![[Pasted image 20260305181113.png]]








# 核心基础-OD剖析堆栈


## OD剖析堆栈

这里其实就是说的栈，即函数调用栈，
我们先写一个正向的函数调用程序，然后再逆向分析它看它的堆栈变化，

为了能让OD附加，我们在程序代码中调用窗口阻塞函数，比如 MessageBox 函数，防止程序立马结束。

```cpp
#include <Windows.h>
#include <iostream>

int add(int a, int b)
{
	return a + b;
}

int main(void)
{
	MessageBox(0, 0, 0, 0);
	add(2, 3);
	return 0;
}
```

编译上述代码后，直接双击.exe文件运行而不是在VS里运行，然后会弹出一个黑窗口和一个MessageBox窗口。

然后我们用OD附加，这里有两种附加，一个是直接附加主程序(即黑窗口)，另一个是附加子程序(即消息窗口)，这里我们集中精力先把堆栈的事完成，因此这里我们先附加主程序。直接OD拖拽放到黑窗口即可附加。

这里我们由内往外返(**从callee往上返到caller**)，即先找到 MessageBox 代码处，即 MessageBox 函数的实现代码，然后我们在在其函数内部(比如retn之前)加个断点，然后我们执行时它会断在那里，然后我们单步执行，最终会往外返回，即返回到调用者(caller)调用它的位置的下一条语句位置，至此我们就这样回到了上一层函数的代码处了。

由于我们VS工程配置的字符集是多字节字符集，且 MessageBox 是宏，因此我们通过OD搜索该函数时需要直接输入 MessageBoxA，如果配置的是Unicode字符集，则是 MessageBoxW，这点大家需要留意一下。

![[Pasted image 20251229142400.png]]


至此，我们找到窗口函数的函数体，然后我们在函数返回处打断点，
![[Pasted image 20251229142416.png]]


然后点击运行，等几秒中运行后，消息窗口就可以操作了。然后我们点击消息窗口的确认按钮，然后OD中的代码窗口就会运行到刚刚的函数返回处，即断点处，并且程序处于暂停状态。
![[Pasted image 20251229142443.png]]


然后单步执行，即可回到上一层caller的代码处。
![[Pasted image 20251229142457.png]]


如上图所示的 caller 代码处，其中 `call 006D1244` 这句我们双击进去发现是堆栈检查函数，这个是编译器加进去的，我们不用深究它。直接看我们自己写的 add 函数。

我们直接单步步过(F8)运行到 `push 3` 这一行，让 EIP 指针指向这一行。这也是我们向 add 函数传递参数的位置，从这个时候开始，我们就要一边观察堆栈窗口，一边单步执行，一边画堆栈图，看看这个堆栈到底是怎么工作的。

![[Pasted image 20251229142515.png]]



![[Pasted image 20260301101850.png]]

如上图所示，上图是函数调用栈最核心的图，也是本小节最核心的图，因为在实战中各种调用者与被调用者的追踪，以及参数传递分析，都离不开对函数栈的深刻掌握。上图中 callee 的EBP和ESP之间的内存空间，就是用来存放该函数内部局部变量的。函数执行到尾部后，会把返回值存放到 EAX 寄存器。





## OD定位caller

在实际的逆向分析中，我们如果知道了对方调用Windows API，我们可以根据该信息找到其调用点，进而跳到其代码位置。首先用VS写一个窗口函数调用，然后直接双击.exe文件执行，不使用单步调试执行，然后用OD附加该程序的弹窗。

```cpp
#include <Windows.h>
#include <iostream>

int add(int a, int b)
{
	int c = 1;
	int d = 2;
	int e = a + b;
	return e;
}

int main(int argc, const char* argv[])
{
	MessageBoxW(0, 0, 0, 0);
	int c = add(2, 5);       //在此处打断点
	return 0;
}
```


![[Pasted image 20251229141021.png]]

然后使用 OD 附加操作来附加该窗口程序，直接附加控制台黑窗口而不是消息窗口，并找到 MessageBoxW 位置：
![[Pasted image 20251229141038.png]]


按回车进入到 MessageBoxW 函数内部，然后在其返回处打上断点，然后让程序运行至断点后暂停，然后通过单步执行的方式，最终 MessageBoxW 返回到 caller 位置。

![[Pasted image 20251229141058.png]]


如下图所示，这样我们就到了我们熟悉的调用位置了。

![[Pasted image 20251229141114.png]]

知识点：在汇编代码中，可以通过 retn 相关的指令来确定函数尾部。

知识点：eax在call的旁边，通常大部分情况是用来存储函数返回值的。




# 练手游戏-DXF读取本地变量


## DXF靶场安装与登录

关闭 Windows Defender，即关闭Windows安全设置，

直接使用老师提供的: DNF客户端New.rar，

把游戏包解压到自己指定的一个目录，无需安装，解压即可，

之后，里面有两个登陆器（复古登录器1119.exe、星星登录器时尚1120.exe），二选一都可以用，

双击运行登陆器程序文件，然后使用账号密码登录，下面是可用的账号密码：

账号: 111 密码: 111              —— Lv.1、Lv.95

账号: 222   密码: 222            —— Lv.100

账号: 333   密码: 333            —— Lv.95、Lv.1

账号: 444   密码: 444            —— Lv.2

账号: 666   密码: 666            —— Lv.95

账号: aaa   密码: aaa             —— 无角色

账号: abc   密码: 123456      —— Lv.2

账号: 123456 密码: 123456          —— Lv.100、Lv.100

登录进去后，尽量选择一个有等级的角色，不要选择Lv1级的，因为没有装备，后续抓数据不好抓。



## DXF用CE查找人物名字


前面函数堆栈知识必须要掌握。首先启动目标游戏，先用 CE 找到游戏内已知的人物名字，找到其内存地址。然后拿着这个地址，打开OD，用OD的数据窗口，找到这个地址，并下硬件访问断点。

前面我们已经通过 CE 方式简单了解了【是谁访问了这个地址】，从中看出访问目标地址的不一定只有一个，可能有多个(多线程)都在时刻访问目标变量的地址。在OD这边也一样，当我们下访问断点之后，开始执行程序后，每次触发访问断点的代码不一定是同一个，我们能做的，就是从多个访问者里，尽量选择好追的那个访问者，然后反向去追这个访问者，找到目标变量的基地址。


---

下面是自己亲自找名字的记录


如下图所示，先登录游戏进入大厅，然后用 CE 附加游戏。
![[Pasted image 20260303093754.png]]



如下图所示，【Shift+鼠标单击】进行批量修改，用二分法的方法来快速筛选。
![[Pasted image 20260303094339.png]]


如下图所示，最终找到名字的绝对地址，但是这个地址没有实用意义，我们接下来还要借助OD找到它的基地址。
![[Pasted image 20260303094852.png]]



## DXF用OD找名字基地址


如下图所示，紧接着上面的小节，拿到上面找到的绝对地址 0x7F090998，用OD附加游戏，然后让游戏处于运行状态(游戏界面不卡死)。然后在 OD 的数据窗口，【Ctrl+G】并填入绝对地址，找到并确认这是存放名字的位置。

![[Pasted image 20260303100329.png]]


如下图所示，然后给该地址下断，用于随机抓取一个访问者。
![[Pasted image 20260303100654.png]]


如下图所示，当我们下硬件访问断之后，立马抓取到一个访问者。但是，这种【ebp-大数字】的这种风格的代码不好追，这是老师亲自验证过的。因此我们继续运行游戏，继续抓取其他访问者。
![[Pasted image 20260303101022.png]]



如下图所示，这也是老师演示的比较好追的访问者。
![[Pasted image 20260303103015.png]]


如下图所示，我们最终知道地址来自 caller 第1个参数，于是需要执行完此处代码并返回到 caller 的调用处。
![[Pasted image 20260303103913.png]]


如下图所示：
1、抓到访问者后，Ctrl+F9 执行到 caller 处；
2、此时进一步验证 `[eax+258]`，所以需要在2处打断点(双击机器码)，然后让游戏继续运行，从而触发断点。
![[Pasted image 20260303104846.png]]


如下图所示：
1、打上断点，继续运行游戏，然后断在断点处；
2、在数据窗口直接 Ctrl+G 查找 `[eax+0x258]`，看看数据内容是不是名字；
3、最终找到基地址，是一个常量值 1AB7CDC，这一个也可以通过同样流程打断点在数据段验证。
![[Pasted image 20260303105533.png]]


如下图所示：
1、通过打断点并继续运行游戏，断在了断点处；
2、此时直接在数据断把这个常量值代入查询，发现还是名字所在的地址，至此基地址找到了。
![[Pasted image 20260303110223.png]]



最终表达式的追踪如下：
```txt
eax == 名字地址
[eax+0x258] == 名字地址
[[0x1AB7CDC]+0x258] == 名字地址
```



经过本人亲自验证，游戏重启了(包括重启登陆器)，也能在OD数据窗口通过上面基地址表达式正确找到名字地址。经过验证，电脑关机重新开机后，同样用上面的基地址表达式能够在OD数据窗口看到人物名字。



## DXF通过注入读取名字


前面我们拿到人物名字的基地址和偏移量，我们接下来通过 C++ 代码来把名字读出来。

如下图所示，注入之后就会立马弹出 Dialog 对话框界面，然后我们点击按钮读取角色名字。由于是初次写辅助程序，所以后续下面将详细展示整个辅助的编写到注入运行的完整过程。
![[Pasted image 20260303154536.png]]

---

下面将演示完整过程

首先在前面 MFC DLL 工程的基础上，我们添加按钮，比如【角色名字】按钮，当我们点击该按钮时，能够执行相关代码读取并展示角色名字信息。MFC DLL 工程的创建，请参考注入相关的章节 [[#创建MFC对话框DLL]] 。


如下图所示，首先从工具箱中找到【Button】控件，然后拖拽到对话框界面上，并改名字。
![[Pasted image 20260303161229.png]]


如下图所示：
0、修改控件ID，方便阅读理解；
1、2、找到按钮控件，鼠标右键并【添加事件处理程序】；
3、确认相关信息后，点击确定即可，最终会生成回调函数供你修改。
![[Pasted image 20260303161608.png]]


本工程还用了日志窗口，也就是把相关信息也能显示在窗口里，这样就不需要额外用 DebugView 来查看。MFC 实现日志窗口，直接参考 MFC 相关的章节 [[#MFC控件日志窗口]]，其提供了操作方法和参考代码。


下面是注入到目标程序之后，点击【角色名字】按钮后执行的代码：
```cpp
void DXFDlg::OnBnClickedButtonPlayerName()
{
    std::string strInfo;
    CString cstrInfo;
    std::wstring wstrInfo;

    // [[0x1AB7CDC]+0x258] == 名字地址
    DWORD* addr = (DWORD*)(0x1AB7CDC);
    addr = (DWORD*)(*(DWORD*)(*addr + 0x258));

    wchar_t* name = (wchar_t*)addr;
    std::string strName = WStringToANSI(name);

	// 以 ANSI 格式打印到 DebugView 里, 能正常显示
    strInfo = std::string("[A]角色名字: ") + strName;
    OutputDebugString(strInfo.c_str());

	// 以 宽字符 格式打印到 DebugView 里, 能正常显示
    wstrInfo = std::wstring(L"[W]角色名字: ") + std::wstring(name);
    OutputDebugStringW(wstrInfo.c_str());

	// 日志窗口仅支持 ANSI 格式的字符串
    CString cstrName(strName.c_str());
    cstrInfo = CString("[A]角色名字: ") + CString(strName.c_str());
    AppendLog(cstrInfo);

}
```




## DXF用CE查找人物坐标


如下图所示：
1、首先操作角色，从大厅进入到任意地图；
2、3、坐标 x,y 值，根据老师推荐，首次扫描，选择单浮点，并且不知道当前值；
![[Pasted image 20260303171831.png]]


然后如下图所示：
1、游戏里只按一下右键，让角色仅仅往右边走动一下；
2、3、扫描选择【变动的数值】，然后点击【再次扫描】；
3、以此类推，我们仅仅左右移动，来逐渐减少扫描到的地址个数；
![[Pasted image 20260303172241.png]]


经过实际操作过程中，一旦尝试访问(读or写)游戏内内存，会触发**游戏保护机制**，DXF这里表现为会弹窗(MessageBoxW)，然后当点击消息窗口确认后，游戏直接退出。这里专门提炼了【过检测过保护】相关的章节，用于其他需要的地方引用。关于本节过检测可直接参考 [[DXF内存访问过检测]] 小节。


如下图所示，最终通过 CE 找到 X坐标绝对地址 0x5F14408C，后续我们紧接着拿着这个绝对地址，用OD来追到它的基地址。
![[Pasted image 20260304091734.png]]



## (TODO)DXF用OD找坐标基地址


紧接着上面，上面用 CE 拿到了坐标的绝对地址，这里我们这把用 OD 追到其基地址。


如下图所示，首先在 OD 数据窗口，【Ctrl+G】把绝对地址 0x5F14408C 填上，然后给这个绝对地址首地址下一个断点，硬件访问断点：
1、2、给指定内存地址下一个硬件访问断；
3、继续运行目标游戏，让其主动触发断点。
![[Pasted image 20260304092245.png]]













# 网游核心-DXF寻找公共call


## DXF初探发包


## DXF发包函数










## (DOING)DXF常规发包

常规发包，就是玩家操作走路，那么就走路call会直接发包；玩家操作释放技能，释放技能call就会直接发送相关的包等等，相对比较直接的发包，这种直接往上返就可以找到公共call。


OD附加游戏后，

OD代码窗口中，Ctrl+G，然后搜索: ws2_32.send，然后在函数开头打断点，然后操作游戏角色走路，以及切换装备，都没有触发断点，说明 ws2_32.send 不是该游戏的发包函数。同样的方法试了 ws2_32.sendto，也不是发包函数。当 ws2_32.WSASend，发现一下断就断住了，老师通过堆栈窗口的函数参数，排除了心跳包，也没有发现有意义的内容，所以也不是发送函数。

那么上面三个函数都不是，加上该游戏又是腾讯系的游戏，很明显是游戏公司自己改写了发包函数，但是无论怎么改写，其和上面三大函数一样，底层都调用了 WSPSend 这个函数。那如何找到这个函数的代码呢？我们首先找到 ws2_32.send，然后进入 ws2_32.send 函数入口，然后往下找，如下图所示，能找到 FFD6 特征码或者 WEP 关键字，那么该处就是 WSPSend 函数调用点了，直接回车即可进入 WSPSend 实现处。

![[Pasted image 20260305111034.png]]



后续往上返，就基于这个 WSPSend 开始往上返，每操作角色一个动作(比如走路、换装备)，就会触发断点，然后往上返，尽量多返几层(8、9层)。注意：由于 call 寄存器，所以必须要打**断点执行EIP指向此处后，再回车才能进入到相应的函数里**，否则寄存器的值不确定，无法跳转到正确的函数。























## (DOING)天龙线程发包


![[Pasted image 20260306131439.png]]










## 理解游戏发包流程

这节课老师讲发包，发包是一个比较难以理解的一个点，所以老师这节课以简单的天龙为入手，先带领大家找天龙的发包，然后呢，那个理解透彻了，我们再来找DNF的，天龙的，其实也并不比DNF简单，只不过呢，这俩是两种不同的类型发包，你这两种类型都遇到了呢，你以后找发包就基本上每种情况都遇见过了。

在讲发包之前，老师要先给大家灌输一个概念，首先游戏分为服务端和客户端，客户端可能几万人同时在线，服务端要同时处理几万人的网络请求。

首先游戏客户端和服务端之间肯定有个通讯协议的，这个通讯协议可能是：send、sendto、WSASend，这三种是比较常见的，除了这三种，有些游戏厂商自己改写，像腾讯类的，基本上腾讯类的都是自己改写的，比如DNF就是调用自己改写的。但是呢，就算是厂商自己改写的，它也会调用底层的 WSPSend，前面三个底层也是调用了这个函数。所以呢，我们只要进入这个函数里面，然后往上返，就能返得到。

![[Pasted image 20251229143046.png]]


下面是通过AI咨询的WSPSend的使用示例代码，简单看看即可：

```cpp
#include <winsock2.h>
#include <ws2spi.h>
#include <stdio.h>

#pragma comment(lib, "ws2_32.lib")

int main() {
    WSADATA wsaData;
    SOCKET s;
    struct sockaddr_in server;
    WSABUF dataBuf;
    DWORD bytesSent;
    int err;
    
    // 初始化 Winsock
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        printf("WSAStartup 失败: %d\\n", WSAGetLastError());
        return 1;
    }
    
    // 创建套接字
    s = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, WSA_FLAG_OVERLAPPED);
    if (s == INVALID_SOCKET) {
        printf("套接字创建失败: %d\\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }
    
    // 设置服务器地址
    server.sin_family = AF_INET;
    server.sin_port = htons(80);
    server.sin_addr.s_addr = inet_addr("127.0.0.1");
    
    // 连接到服务器
    if (connect(s, (struct sockaddr*)&server, sizeof(server)) == SOCKET_ERROR) {
        printf("连接失败: %d\\n", WSAGetLastError());
        closesocket(s);
        WSACleanup();
        return 1;
    }
    
    // 准备要发送的数据
    const char* sendData = "Hello, server!";
    dataBuf.len = strlen(sendData) + 1;
    dataBuf.buf = (char*)sendData;
    
    // 发送数据
    if (WSPSend(s, &dataBuf, 1, &bytesSent, 0, NULL, NULL, NULL, &err) == SOCKET_ERROR) {
        printf("WSPSend 失败: %d\\n", err);
    } else {
        printf("成功发送 %d 字节\\n", bytesSent);
    }
    
    // 清理
    closesocket(s);
    WSACleanup();
    
    return 0;
}
```

接下来老师讲解，在游戏中，是怎么调用通讯协议的呢，流程是什么样的呢，

比如打怪，有很多跟网络相关的操作，比如技能操作，商品操作等。

![[Pasted image 20251229143106.png]]



如上图所示，还有很多跟游戏相关的call，不管什么call，所有和网络发送相关的call，都会进入到右边绿色的函数里，这个绿色方块就是公共call。

当我们找到这个公共call之后，我们就可以基于这个call往上返了，往上返就能返到相应的游戏技能了。当然这里的往上返，可能要返好多层。我们可以基于这个公共call，通过断点+往上返，可以找到对应技能操作的call，比如你是在鼠标点击打怪断下来的，你就返回到鼠标点击打怪call，如果你是释放技能断下来的，你就返回到释放技能call。而且我们在加密之前，是不是就可以看到它的明文信息呀。

当然还有一种发包方式，是线程发包，就是说它会单独的启动一个线程，往某个地方写入，往这个地址一直写入要发包的内容，然后用另外一个线程调用callsend，把这里的内容发出去。这种发包方式呢，也很常见。

1、先找到系统层 send 接口；

2、然后往上返，根据游戏相关操作往上返来定位出公共call；

## OD天龙寻找发包公共call


OD附加游戏后，

OD代码窗口中，Ctrl+G，然后搜索: ws2_32.send



打断点，任何相关的网络活动都会触发，
当然也可能是心跳包，
心跳包是游戏服务端用于检测游戏是否正常等等，
这时候可以在 OD 中通过 Shift+F2 来添加条件断点，
然后触发断点后，去堆栈窗口看它的包长、包内容来判断是否是心跳包，
把心跳包筛除掉，然后后面就好搞了，








OD代码窗口中，Ctrl+G，然后搜索: ws2_32.WSASend

```nasm
wspsend
	send
	sendto
	WSASend
	游戏厂商自己改写的send函数
```

OD附加游戏，然后在汇编窗口直接 Ctrl+G 查找 ws2_32.send，

找到该函数的函数体，然后在该函数的开头打断点(F2)，

然后游戏本身由于频繁的网络活动，会触发这个断点，

这些频繁的网络活动，要么就是其他网友发的喊话，或者是其他玩家的活动，

以及心跳包，等等，

这里我们新建一个队伍，然后我们通过往队伍里喊话，也就是往队伍里发消息，

从而触发网络活动，我们要抓取的就是这个网络活动，

只要能抓到，就可以往上层追，

接下来我们要在 ws2_32.send 函数开头F2设置断点，

在打断点之前，我们需要实现准备好我们要发送的内容，比如11111111111，

然后设置F2设置断点，然后立马发送上述准备好的内容，尽量防止被别的网络活动触发，

这节课，老师用天龙这个游戏来演示，

老师启动游戏后，通过OD附加，然后先找到send，通过 Ctrl+G 然后输入 ws2_32.send，

然后就会跳到函数入口点，然后我们在入口点下个断吧，直接按F2下断，然后让游戏运行，然后等待触发断点。

有的游戏呢，你一下断它马上就断，有可能是也有可能不是，有可能是心跳包。

遇到心跳包这种情况呢，可以用OD的条件断点来筛选掉心跳。

比如用 Shift+F2，然后在堆栈窗口看它的包长啊，包内容啊，来筛查一下，把心跳筛选掉。

游戏中不同的行为，会导致运行不同的发送执行流，

我们要能找到我们想要的执行流，

但我们首先需要找到公共call，

也就是不管玩家做什么操作，都会调用这个公共call把数据发送出去，

后续基于这个公共call，

我们就能往上返，追踪特定的动作，比如使用物品这个动作，

找到一个合适的动作比如喊话，然后send断点触发后，往上返多返几层，并且每层备注标记一下，

老师试了几个动作，都能往上返10层，并且每层都是一样的，

并且往上返超过10层，就会卡顿，然后需要点击开始，并且把所有线程恢复运行，

## 网络-天龙寻找发包公共call

```cpp
wspsend
	send
	sendto
	WSASend
	游戏厂商自己改写的send函数
```

首先老师用OD附加目标游戏，

附加执行完成后，OD窗口左上角会显示状态，如果是运行就表示正在运行状态，

如果是暂停状态，你要帮助它运行一下，

如果游戏还是卡着不动的话，那么OD的T(线程)窗口，

里面的线程都是挂起状态，

直接鼠标右键把它们 Resume All Threads，再点击运行按钮；

OD汇编窗口里，Ctrl+G 搜索 ws2_32.send 来查找，

找到之后，我们尝试直接在函数开始下个断，然后过一会可能就断下来了，

那这种基本就是了，

你看，我游戏角色一走路，它就马上断住了，那基本就是了，

有的游戏呢，你一下断它就马上断住了，它有可能是也有可能不是，

有可能它是因为心跳机制发的心跳包，

这种情况呢，

你可以在OD用 Shift+F2，来给 ws2_32.send 添加条件断点，

通过条件断点去看它的包长啊以及包内容啊，来判断一下，把心跳筛选掉，

当然也可能不是，

这时候你可能就要去找 sendto 啊，wspsend 之类的，这个我们后面再说了；

此时，老师触发了 ws2_32.send，

然后一直往外返，每次返都会在汇编窗口右边打上备注，

一直往上返，一直到不能返为止，

因为可能要返数个层才能找到真正的公共call，

上面是老师在游戏消息窗口喊话，即输入11111111发送出去，

视频中，老师往上返了10层，

然后让游戏角色走路，触发断点，然后继续往上返，

也是同样位置的10层返，

然后开宝箱，继续返，也是同样位置的10层，

但是老师每返到第10层时，游戏都会卡住，

需要 Resume All Threads，再点击运行按钮，才能让游戏恢复运行，

然后卡住时的位置是 Windows API 窗口函数处，

说明这不是正常的发包

## 网络-天龙线程发包的找法

一个游戏，你只要把它的公共call找到了，那你基本上70%的call都能找到了，

所以这个这个找公共call是非常重要的课，

你只要找到这个游戏的公共call，你就基本上对这个游戏把握住了，

剩下的就是一些细节方面的东西了。

发现右侧堆栈窗口，send函数里的data指向的地址一直有人在写入，因为里面的数据每次断点都会变，

如下图所示，就是先找到最底层的send，并验证send，然后往上返，之后对每个游戏动作进行断点验证，最终定位到公共call的代码块。

![[Pasted image 20251229143135.png]]





# DXF游戏内存找数据


## DXF遍历背包数组


1、比如只看4号背包，首先用CE查找，它是一个地址之类的，未知初始值，(32位)4字节；

2、未变动的值、变动的值、未变动的值，以此类推操作背包并不断缩小内存范围。

3、CE + OD 配合，找到内存对象基地址。


## 使用物品call

上一节我们找到了背包数组的基地址，这把我们就要用起来，

DXF进游戏打怪，并让怪打掉血，掉一点血之后，我们就可以使用背包里的加血物品。前面我们找到的公共call这时候就要派上用场了。然后在公共call的起始代码处下软件断点，然后在游戏里使用背包里的加血物品，然后就断下来了。这时候你要有一定判断，有可能是心跳断。 

然后【Ctrl+F9】往上返一层，然后下段，然后继续往上返一层，然后下断，直到确定是你使用物品触发的断。


通过堆栈窗口信息得知，使用物品call只需要一个参数；

下面是用老师提供的注入工具直接注入汇编代码：
```cpp
pushad             // 保护堆栈的必须操作,确保堆栈平衡从而不会让游戏崩溃
push 0x3           // OD追到的背包索引值
mov ecx, 0x1a5fb24
mov ecx, [ecx]     // 推荐别直接访问内存,而是借用寄存器间接访问内存
mov eax, 0x7b9130
call eax           // 推荐别直接call地址(虽然OD反汇编是这样)
popad
```


注入工具直接注入汇编代码只是在调试阶段快速验证，最终还是要用C++代码写出来。


## C++实现物品使用call


直接在对应的按钮回调函数里，使用内联汇编：

```cpp
void DXFDlg::OnBnClickedButton2()
{
	__asm
	{
		pushad
		push 0x3
		mov ecx, 0x1a5fb24
		mov ecx, [ecx]
		mov eax, 0x7b9130
		call eax
		popad
	}
}
```



## DXF喊话call


1、也是**从公共call往上返**，不直接用公共call是因为数据到公共call时已经加密了。

2、往上返几层，每一层的call语句都打上注释（比如 hh1、hh2、hh3、hh4)，再从外层向内层，逐层来打软件断点来找到这个喊话call。

3、触发断点的不一定是喊话call，虽然也是操作喊话触发断点，这时可以通过堆栈信息来看看它有没有参数传递，如果一个参数都没有传递，那么就可以直接排除这不是喊话call。


## DXF角色血量自我秒杀call


1、血量改不了，CE也改不了，CE改了立马又刷回来了，并且角色被怪物打掉血了，然后也会慢慢自动回血。**为什么会这样呢？** 表明当前血量的这个地址，是有别的地方对它进行写入的。从现象上看，没有看到一个原始变量。

```txt
明文血量(临时堆栈) --- 加密 --- 某个地址 --- 解密 --- 写入当前血量的地址B
```


我们直接在地址B下访问断，并往上返。

## DXF遍历怪物数组


1、本节课就是讲周围 object 遍历，各种对象；

2、通过前面的名字字段(0x258偏移)，来反推出其结构体对象。

## DXF找出周围类型

通过不同 object 里某个范围内，其某个字段的对比区分，来作为类型判断。


## DXF寻找吸怪坐标


1、怪物在脚底下不出来，我们可以通过坐标方式让它和我们在同一个坐标水平。


## DXF封包组包拼包详解


1、尽量选择干扰少的游戏内界面。

2、比如：
- 通过公共call触发【选择频道】call，并复制caller调用点以上的汇编代码，尽量赋值多点，存放到 选择频道.txt 文本里。
- 通过公共call触发【选择角色】call，同理，存放到 选择角色.txt 文件里。
- 通过公共call触发【喊话】call，同理，存放到 喊话.txt 文件里。


## VEHHOOK封包函数


【知识点】OD获取callee的传入参数，但参数代码被花指令混淆了，很简单，直接给callee调用处打断点，然后看堆栈信息。还有一个更简单的，就是hook，直接进目标函数的实现处的开始位置，然后下一个hook，然后我们把它的参数全部都提取出来，这样我们就不用拿OD一次次断点试了找参数了，就可以通过hook把它的包抓出来了。往上直接搜 veh hook 即可。


DXF秒进图
DXF图内顺图
DXF返回城镇
DXF获取房间坐标
DXF获取人物状态


# 天龙八部x64


## x86和x64区别


现在游戏市场，在2022年以后，基本上大多数都是64位了。

1、**寄存器**，64位兼容32位寄存器：
- EAX —— RAX
- EBX —— RBX
- EIP —— RIP
- 。。。
- 新增浮点寄存器: XMM8 ~ XMM15
- 新增8个新64位寄存器: R8 ~ R15


2、**调用约定**
- x86 使用至少3种: stdcall、cdecl、fastcall 等；
- x64 使用类似 fastcall 的调用约定；
- x64 使用 rcx,rdx,r8,r9 传递前4个参数，其余参数从右往左依次保存在栈上。


3、**栈的使用**
- 32位代码在函数中使用 push 和 pop 等指令改变栈的大小；
- 64位代码在函数中从不改变栈的大小，栈在函数的开始增长，期间一直保持不变，直到函数末尾。
- 当一个函数调用另一个函数时，caller会多申请32字节的预留栈空间，当 callee 寄存器不够用时，可以将4个参数寄存器中的值(rcx,rdx,r8,r9)保存在预留栈空间中。预留栈空间由 caller 提前申请，也由 caller 负责平衡回收。如果一个函数有其他参数(>4个)或者局部栈变量，函数会在 0x20 基础上增加预留栈空间的大小，有时增加大小后的值需要与16进行对齐。












---



C++代码实现锁血

DXF遍历怪物数组

DXF寻找周围遍历基地址

C++代码遍历周围

找出DXF遍历周围的类型（建筑、怪物、宠物和自己等等）

C++实现全图秒杀功能

DXF寻找吸怪坐标

C++实现吸怪功能

DXF完美实现全图秒怪

DXF封包组包拼包详解

DXF封包实现进入地图房间

VEHHOOK封包函数

封包抓取进图call

C++实现秒进图

DXF图内顺图

DXF返回城镇的实现

DXF获取房间坐标

DXF获取人物状态

DXF代码实现无限副本




## x64dbg的使用

x64dbg.rar —— 解压后，把里面的 x64dbg.exe 发送到桌面快捷方式，

x64dbg\x64\db —— 这个目录里的文件是附加的缓存文件,相当于附加的内容备份

前面我们用OD，但是OD只支持32位，不支持64位，因此我们就用了这个 x64dbg 工具。

以管理员方式运行，界面和OD类似，用法绝大多数用法和OD也一样，

然后需要做一些设置： （1）—》选项 —》选项 —》异常 —》添加区间 —》0~ffffffff

（2）—》选项 —》选项 —》反汇编 —》勾选一直启用高亮

## 动态模块地址

之前的靶场游戏，由于它不更新，它是固定的模块地址，

在编译的时候，可以设置它的模块地址是动态的还是固定的，

如果是动态的呢，你每一次重启游戏之后，它的模块地址都会发生变化，

模块地址发生变化呢，会导致我们前面找的那种基地址失效，

所以我们后面在写代码的时候，通过模块地址+偏移的方式，得到上述的基地址，

这样就不会有问题了，这样所有的电脑都可以用了，当然游戏只要不更新或者对应的变量偏移不更新。

接着上节课找坐标的课，我们不是找到了那个变量基地址吗，

然后在符号列表里，找到 Game.exe 那一行，其最左边就是模块地址，

x64dbg界面 —》符号 —》基址右键 —》复制 —》基址，

![[Pasted image 20251229143337.png]]



我们前面找到的【变量基地址】减去【模块基地址】就是变量在模块内部的偏移，

把模块基地址和变量基地址相减，得到一个偏移，因此后续我们可以得到：

变量基地址 = Game.exe + 基址偏移；

不管是动态模块还是静态的，都可以用上述的公式来访问变量。

```cpp
// 变量基地址 - 模块基地址 = 变量在模块内的偏移
// 0x7FF7893837F8 - 0x7FF788C40000 = 0x7437F8

// 主要模块名对大小写敏感
[[Game.exe+7437F8]+0x98]+0x5C  人物坐标 x
[[Game.exe+7437F8]+0x98]+0x60  人物坐标 z
[[Game.exe+7437F8]+0x98]+0x64  人物坐标 y
```

---

获取 Game.exe 在C++代码中可以通过 GetModuleHandle 函数来获取，

特征码定位，该技术用于应对游戏更新而导致【变量基地址】和【模块基地址】的偏移变动的问题，




## VSDLL-定时器实时刷新

影子注入器.exe

这是64位的注入器，也是和前面的注入工具一样，也是通过远线程方式注入，

我们需要实时扫描人物状态、血量、坐标等信息，

有两个办法，一个是使用线程，另一个是使用定时器，

老师用的MFC提供的定时器，

前提是要有界面对话框，比如 Dialog，

VS工程 —》顶部菜单 —》项目 —》类向导 —》消息 —》WM_TIMER —》确定；

```cpp
void 初始化部分(...)
{
	CString str1 = "读取角色";
	CString str2 = "停止读取";
	
	
	if (str2 == str1)
	{
		// 循环读取
		SetTimer(1, 1000, NULL);
		SetDlgItemText(IDC_BUTTON1, str2);
	} else
	{
		// 读取结束
		KillTimer(1);
		SetDlgItemText(IDC_BUTTON1, str1);
	}
}

void MyDialog::OnTimer(UINT_PTR nIDEvent)
{
	if (nIDEvent == 1)
	{
		// 刷新角色信息
		
		// 展示角色信息
		CString str;
		str.Format("角色名字: %s\\n角色等级: %d\\n角色状态: %d\\n角色血量: %d\\n", ...);
		SetDlgItemText(IDC_STATIC, str);
	}

	CDialogEx::OnTimer(nIDEvent);
}
```

人物属性的封装:

```cpp
xxx aaa::Update_Role(bool dbginfo)
{
	PlayerRole.clear(); //初始化玩家属性
	DWORD64 g_GameBase = (QWORD)GetModuleHandle(NULL);//模块基地址
	PlayerRole.m_ObjectAddr = ReadDword64(g_GameBase + 角色基地址) + 0x98);//角色对象
	DWORD64 addr = ReadDword64(ReadDword64(this->PlayerRole.m_ObjectAddr + 0x1b0) + 0x18);
	
	//角色状态
	PlayerRole.m_State = ReadDword(this->PlayerRole.m_ObjectAddr + 0x1b8);
	...
	... ReadFloat
	... ReadInt
	...
}
```

---

分析升级经验数组

天龙里面，随着经验值增加，升级难度也跟随着越来越大，体现在经验值上，

## VSDLL-远程调试

当我们注入的DLL运行崩溃，

首先我们可以通过 Dbgview.exe 结合调试打印语句来输出执行流程，

Dbgview.exe 记得要以管理员运行，

VS也能单步调试，

顶部菜单 —》调试 —》附加到进程 —》然后就可以在VS里下断调试了 —》注入DLL。

## 分析二叉树结构


反汇编中识别二叉树结构

因为二叉树比数组查找效率高，而且数量越大优势越大。

```cpp
7FF7914BC58A  int3
7FF7914BC58B  int3
7FF7914BC58C  int3
7FF7914BC58D  int3
7FF7914BC58E  int3
7FF7914BC58F  int3
7FF7914BC590  mov  r8, qword ptr ds:[rcx+80]
7FF7914BC597  mov  rcx, r8
7FF7914BC59A  mov  rax, qword ptr ds:[r8+8]
7FF7914BC59E  cmp  byte ptr ds:[rax+19],0    // 单字节比较
7FF7914BC5A2  jne  game.7FF7914BC5BB         // 如果不相等则不进入循环
7FF7914BC5A4  cmp  dword ptr ds:[rax+20],edx //循环开头
7FF7914BC5A7  jge  game.7FF7914BC5AF
7FF7914BC5A9  mov  rax, qword ptr ds:[rax+10]
7FF7914BC5AD  jmp  game.7FF7914BC5B5
7FF7914BC5AF  mov  rcx,rax 
7FF7914BC5B2  mov  rax, qword ptr ds:[rax+00]
7FF7914BC5B5  cmp  byte ptr ds:[rax+19],0
7FF7914BC5B9  je   game.7FF7914BC5A4         //循环尾巴
7FF7914BC5BB  cmp  rcx, r8 
7FF7914BC5BE  je   game.7FF7914BC5CA
7FF7914BC5C0  mov  qword ptr ss:[rsp+8],rcx
7FF7914BC5C5  cmp  edx, dword ptr ds:[rcx+20]
7FF7914BC5C8  jge  game.7FF7914BC5CF
7FF7914BC5CA  mov  qword ptr ss:[rsp+8],r8 
7FF7914BC5CF  lea  rax, qword ptr ss:[rsp+8]
7FF7914BC5D4  mov  rax, qword ptr ds:[rax]
7FF7914BC5D7  cmp  rax, r8
7FF7914BC5DA  jne  game.7FF7914BC5DF
7FF7914BC5DC  xor  eax, eax 
7FF7914BC5DE  ret 
7FF7914BC5DF  mov  rax, qword ptr ds:[rax+28]
7FF7914BC5E3  ret 
7FF7914BC5E4  int3
7FF7914BC5E5  int3
7FF7914BC5E6  int3
```

```cpp
struct 二叉树对象
{
	DWORD64 左子树;
	DWORD64 tmp1;
	DWORD64 右子树;
	BYTE    tmp2;
	BYTE    标志位;
	DWORD   tmp3;
	DWORD64 二叉树ID;
};
```



## 追二叉树基地址


前面首先定位到二叉树的循环头，然后在头部往上追。



## 网络-发包流程






## 网络-线程发包





## 网络-分析公共call





## x64游戏检测之分析游戏多开


```txt
## x64游戏检测之分析游戏多开

## x64游戏检测之关闭内核对象实现多开

## x64游戏检测之代码实现无限多
```


检测方法很多，比如：
遍历窗口、遍历进程、配置文件、注册表、互斥体、MAC地址,IP,公共文件、内存映射等等，方法很多。


其中用于检测的最多的是互斥体，其他的基本很少：
```cpp
HANDLE hMutex = CreateMutex(NULL, TRUE, "test");// 用于检测是否多开
if (hMutex)
{
	// ERROR_ALREADY_EXISTS == 183L
	if (ERROR_ALREADY_EXISTS == GetLastError())
	{
		// 游戏已在运行中
	}
}
```


方法1: 追到类似上述代码位置，然后把条件跳转改成jmp
方法2: YDArk关闭已开游戏进程的Mutex句柄；
方法3: 劫持注入方式，在游戏打开瞬间，通过注入修改jmp。



纯ring3代码也能关闭互斥体实例
如何获取未公开API函数的原型？比如 NtQueryInformationProcess
- 方法1: WRK（Windows Research Kernel）
- 方法2: 大家自己去x64dbg里去逆 ntdll.dll 里面去分析其参数和返回值。
NtQueryInformationProcess 可以获取游戏进程里有多少个句柄，
DuplicateHandle(..., DUPLICATE_CLOSE_SOURCE);
参考代码：
```txt
教程\02、课程和源码\第二阶段游戏实战(筑基)\2天龙X64\source\第82课代码过多开检测源码.rar
```


## x64游戏检测之数据检测


检测到的处理：
- 直接弹窗、报错、崩溃；
- （恶心不告诉你）比如通过权重：100分，-10分，-10分，当小于60分，放到重点监测区，人工

对方检测可能会有多种手段，不一定只是一种检测方法，
作为我们辅助，需要时间去验证的，
所以你处理了需要花时间观察，这是长周期的过程，可能你测试一周没问题了，
就表示处理好了。


**重点在于什么？**
你要改的内存地址，有某个东西一直在监测它，
用CE，把所有访问它的游戏代码，拷贝每个项里扫到的局部反汇编代码，
分别都复制下来贴到记事本里，以备后续使用，
另外需要**注意点**，需要等个10分钟再看看还有没有其他东西访问它，
因为有些游戏的监测很恶心，它不是马上监测，可能10分钟检测一次，
比如10分钟后，你没有任何操作，CE里突然多了一条访问者的这种，
这种情况你要尤为注意，它极大可能是检测的代码。

![[Pasted image 20260430161632.png]]



然后CE重新附加，解除CE的调试器附加，然后再用x64dbg附加游戏，
然后把上面的局部汇编中访问那个地址的机器码，
在 x64dbg 代码窗口里 Ctrl+G 把机器码贴上找到具体位置，
然后可以看它所在的模块名，如果模块是游戏主模块的名字，那它大概率不是检测代码，
为什么？
因为你不管是大公司还是小公司，
它们的游戏开发和安全团队肯定是分开的部门，是不同的部门，
安全部门可能会写一个 DLL 然后让游戏主模块去加载这个 DLL，比如腾讯的 TPSafe.dll、Protect.dll 等等非主模块，



直接数据检测，这种比较简单，找到检测者，直接jmp即可。
间接数据监测，可能有多个间接监测，可以在游戏一开始的时候就跳过监测，
别的某个安全模块，看看它是往某个地方去写，还是直接进行判断，
如果是往其他某个地方写，那么你还要往写这个地址继续追，


**call检测**
有时候，你调用某个call的时候，它会直接提示你数据异常之类的，
而有的时候，你调用call，它并不做任何提示，
但是它会过阵子过几天就来封你号，这种情况你就很懵不知道怎么导致的。
这时候你只能一点点排查，最终排查到调call调这个call有问题，

```cpp
void xunlufunc()
{
	int jiance1 = 1;

	// 设置它也写成检测call
	jiance_func1();
	
	xunlu1();// 比如我们只是调用里面这种子call，比如这个call

	// 我们并没有走完整的寻路call调用过程，
	// 这时候它就知道了你走的流程不完整
	// 你不知道它的判断比较在哪一层，你也不知道在哪里
	// 你只能调用外层call，
	// 但外层call也不一定有合适call给你用，
	// 你不一定有合适的参数
}
```


**过call检测思路**
在外层的时候，可能它有某个变量来做检测这种非法调用call，



















## x64游戏检测之数据检测代码分析

## x64游戏检测之变量检测和call检测

## x64游戏检测之过call检测思路



## x64游戏检测之分析call检测实现代码



## x64游戏检测之堆栈检测


## x64游戏检测之spoofcall过堆栈检测



## x64游戏检测之CRC检测



## x64游戏检测之过CRC检测思路和注意点



## x64游戏检测之行为检测

















# =====================

# =====================

# =====================

# =====================

# =====================
# =====================







# 练手游戏-OD追变量基地址





## DLL打印天龙人物名字

我们通过VS编写的DLL代码，注入到目标游戏之后，代码就成为游戏的一部分了，

因此人物名字可以直接通过指针读取，如下代码所示，下面是老师DXF读名字的示例代码：

```cpp
void DXFDlg::OnBnClickedButton1()
{
	wchar_t *name = (wchar_t *)(*(DWORD *)(*(DWORD *)0x1ab7cdc+0x258));
	OutputDebugString(name);
}
```


# DNF靶场（32位）






## 32位天龙人物状态

老师讲解演示中，使用天龙来演示，

首先为什么要找这个状态标志位，当你做一个辅助的时候，你得及时确定角色正在干什么，

正在打坐，正在释放技能，正在打怪，等等，

我们的辅助需要根据不同的状态，做不同的处理，

所以呢我们就需要找到这个标志位，找到这个数据所在的内存，

老师演示中，首先使用CE附加天龙游戏，然后数据类型是一个字节，未知初始值，

首次扫描，然后扫描出好几万个结果，

然后操作游戏角色走动起来，然后再次扫描变动的值，

然后操作游戏角色站着不动，然后再次扫描变动的值，

然后操作游戏角色走两步再停下，然后再次扫描未变动的值，如此循环，让CE扫描结果不断减少，

然后最后剩25个地址，然后也没法进一步扫描减少了，

那么我们首先观察，我们的标志位的值最好是0~10之间，然后从地址列表的值中，

只有一个唯一的地址，其值在10范围内，

上面的只是老师的爱好，因为老师喜欢10范围内的数值，因为老师认为状态标志位不需要大值，

我们学员也可以使用地址列表里其他的值，因为其他值如果满足状态变化的特征的话，也是能用的，


## OD找到名字基地址

首先启动游戏，然后通过 CE 找到玩家名字所在的**绝对地址**，

拿到这个绝对地址，

然后打开OD，并附加到游戏，

然后在OD数据窗口，Ctrl+G 把找到绝对地址所在内存，看到里面的数据确实是玩家名字，

然后在OD数据窗口，给这个绝对地址下断点，硬件断点且按字节，

然后让OD左上角处于运行状态，

然后过几秒之后，当有代码访问这个绝对地址就会触发断点，

每次触发的代码位置可能不一样，因为可能会有不同的执行流在访问这个地址的数据，

不断地下同一个断点，然后不断地触发断点，

找到一个容易反推到基地址的执行流代码，

下面是视频里比较好反推(返追)的触发断点的反汇编代码：

```cpp
...
push     ebp
mov      ebp, esp
push     ecx
mov      eax, dword ptr [ebp+8]  //3.这里给eax赋值,[ebp+8]就是caller传参的第1个参数
push     esi
push     edi
mov      edi, ecx
mov      dword ptr [ebp-4], edi
lea      edx, dword ptr [eax+2]
mov      cx, word ptr [eax]      //1.此处触发硬件访问断点(这里是最好追的一个)
add      eax, 2                  //2.EIP的位置(还没运行)
test     cx, cx
jnz      short  01198A41
sub      eax, edx
sar      eax, 1
jnz      short 01198A6F
mov      eax, dword ptr [1A32230]
push     eax
mov      esi, eax
...
```

如上OD代码窗口，视频里可以看到此时的EAX值就是字符串”11”，就是我们想要的值，

由上面步骤3给的注释，我们知道了该函数的caller的第1个参数，

紧接着视频里，老师按 Ctrl+F9(执行到返回)，

于是就执行完上述子函数代码，回到上一层的caller位置，如下代码所示：

```cpp
...
mov    esi, ecx
mov    eax, dword ptr [1AB7CDC]  //6.。。。
test   eax, eax
je     short 0069D025            //3.因为这里有个跳转,所以没有push别的参数了
mov    eax, dword ptr [eax+258]  //5.。。。
push   eax                       //4.那这里只有这一个push,那就只有这个参数了
lea    ecx, dword ptr [ebp-10]
call   01198A30                  //2.就是这个call
lea    eax, dword ptr [ebp-10]   //1.此时EIP所在位置
...
```

5.因为我们不知道这个eax来自哪，不一定是上面的6来原，也可能是别的地方跳过来的，于是视频里老师在5.那行汇编下个断点(F2)，然后让程序继续跑，然后触发断点了，于是进一步确定，push的那个eax是来自于5.这个位置的汇编指令。

再进一步验证，直接在OD数据窗口，Ctrl+G，然后输入 `eax+0x258` 找到这个内存地址，然后看看这个内存里是不是我们要的字符串 “11”，视频里确认了是我们要的字符串。

至此，视频中老师找到了基地址：

```cpp
mov    eax, dword ptr [1AB7CDC]
...
mov    eax, dword ptr [eax+258]
```

至此，视频老师把基地址计算公式推导出来：

```cpp
1. 0x49303738 --> CE追到的绝对地址
2. eax == 0x49303738
3. [eax+258] == 0x49303738
4. [[0x1AB7CDC] + 258] == 0x49303738
```

然后老师把上面推导的公式，放到OD底部命令行执行，查看内存内容确实是目标字符串：

OD命令行执行: `db [[0x1AB7CDC] + 0x258]` 即可看到数据窗口对应的地址和数据。OD左下角命令行输入框里，内存显示的命令格式为: `db [address]` 。

或者直接点击数据窗口，然后 Ctrl+G 直接输入寄存器名字比如eax里面存放了数值，这个数值就是某个内存地址，这样也能显示；或者寄存器加偏移值，这里的表达式不需要方括号。

## DLL-DNF过检测

DNF进程里很多地址都有保护，也就是有检测机制，

一旦我们在OD里下硬件断点，当触发断点时，就会导致游戏弹窗报错崩掉。

后续的课程中，当我们需要下硬件断点时，首先给它设置一下就好。

首先启动并登录DNF游戏并进入大厅，

然后OD附加它，然后CE附加它并随便找个地址，我们用这个地址来触发检测，

从CE那边拿到一个地址，

然后在OD地址窗口按 Ctrl+G 找到这个地址，

并直接给这个地址下断点，硬件访问断，字节，然后OD运行游戏，

之后就会触发游戏的检测机制，导致弹窗错误窗口，这时我们直接看 OD 的堆栈窗口，

因为像这种一般没法执行到返回，因为执行完就直接程序退出了，

所以我们没法用常规的方式往上返，这时候就只能看堆栈信息了，

根据堆栈信息来往上追出其可能的 caller，

这里的 caller 可能有很多个分支过来的，也可能是层层调用下来的，

我们要追的，也是因为导致它检测不过就跳转到这个分支来，

至少当前这个分支，以及上一个caller是错误处理的分支，那我们应该还要往上追一层，

## DLL-读取人物名字

下面是大流程：

1、首先使用CE找到目标地址；

2、然后使用OD追到基地址；

3、基于基地址+偏移，直接访问这个名字。

人物信息，包含名字、血量等信息。

我们先用CE把人物名字的内存地址找出来，CE找到：人物名字——0x62311760

地址找到了，但是没用哈，因为游戏重启或者电脑重启就没用了，所以我们还要找到它的基地址。

怎么找呢？我们使用OD找，打开OD并附加游戏，

然后先把上面找到的地址找到，并在OD数据窗口中能看到里面的值，也就是ASCII码，

接着我们直接对这个绝对地址下个访问断点，硬件字节访问断点，

这里注意，访问该地址的不一定是唯一的代码，可能还有其他函数代码会访问该地址，

我们多次断点，找到一个最好分析的函数代码，进行往上返，然后找到其基地址，

相当于断点触发之后，往上追，不断尝试，最终找到基地址，

下面是最好找基地址的一个函数代码截图：

![[Pasted image 20251229150038.png]]


至此我们直到这个 eax 的值是上层传下来的第一个参数，

然后我们取消硬件访问断点，然后【执行到返回——Ctrl+F9】，把视角定位到上一层caller代码，

![[Pasted image 20251229150052.png]]



那这里的这个eax值是哪里赋值过来的呢？

可能是上面那句执行下来的，也可能是别的地方跳转到这里来的，不确定，

于是我们在push eax 的位置下个断点（下图红色部分）：

![[Pasted image 20251229150112.png]]



经过在OD窗口查询下图这些地址，发现验证没问题，就是这个地址，

至此，人物名字的基地址我们找到了：

![[Pasted image 20251229150125.png]]

![[Pasted image 20251229150133.png]]


在DLL代码中，我们直接通过基地址加偏移来获取名字：

```cpp
// 首先基地址里还是一个地址
DWORD* addr1 = (DWORD*)(*(DWORD*)0x1AB7CDC);

// 然后拿到第二层地址
DWORD* addr2 = (DWORD*)((uintptr_t)addr1 + 0x258);

// 然后才是字符串
wchar_t* player_name = (wchar_t*)addr2;
```

这里需要注意的是，你的DLL工程字符编码配置，需要依赖你的目标游戏的字符编码，如果目标游戏是 Unicode 编码，那么你的工程配置也必须要一样。

```cpp
#ifdef UNICODE
#define TEXT(str) L##str
#else
#define TEXT(str) str
#endif //UNICODE
```

至此，我们就成功添加了相关控件代码，

```cpp
void DXFDlg::OnBnClickedButtonGetplayername()
{
	// 从游戏内存中,获取玩家名字,并显示到编辑框

	DWORD *addr1 = (DWORD *)0x1AB7CDC;
	DWORD *addr2 = (DWORD *)(*addr1 + 0x258);
	wchar_t *player_name = (wchar_t *)(*addr2);
	//wchar_t *player_name = (wchar_t*)(*(DWORD*)(*(DWORD*)0x1AB7CDC + 0x258));//OK

	// 设置编辑框文本
	SetDlgItemText(IDC_EDIT_PLAYERNAME, player_name);
}

void DXFDlg::OnBnClickedButtonSetplayername()
{
	// 获取编辑框文本
	CString strPlayerName;
	GetDlgItemText(IDC_EDIT_PLAYERNAME, strPlayerName);

	if (!strPlayerName.IsEmpty())
	{
		DWORD* addr1 = (DWORD*)0x1AB7CDC;
		DWORD* addr2 = (DWORD*)(*addr1 + 0x258);
		wchar_t* player_name = (wchar_t*)(*addr2);

		// 写入到目标内存
		wcscpy_s(player_name, strPlayerName.GetLength() + 1, strPlayerName);
		strPlayerName.ReleaseBuffer();
	}
}
```

下面是辅助运行的效果截图：

![[Pasted image 20251229150152.png]]



## DLL?-读取人物坐标

怎么找呢？

首先CE附加游戏，

然后先按照单浮点、未知的初始值，来找地址，然后找到好几万个地址，

我们游戏角色进入地图，然后不动，未变动的数值，

然后游戏角色在地图里走两步，变动的数值，表示只留变动的，然后地址数量少了很多，

前期就是找地址，然后找基地址，

只要找到基地址了，基本上就成功90%了，后面的代码编写轻轻松松。

目前通过CE至少已经确定是这4个范围内了，

我们可以通过 OD 下硬件断点，来一个个排查，

![[Pasted image 20251229150206.png]]


如果连触发都不触发的地址，就可以直接排除了，下面是硬件断点触发的代码，

xmm0寄存器我们不看，因为我们要定位大结构体的位置，所以这里只跟 ecx 寄存器，

发现 ecx 往上没有赋值语句了，于是直接【执行到返回——Ctrl+F9】，返到上一层，

![[Pasted image 20251229150217.png]]


返到上一层之后，如下图所示，ecx寄存器跟到6D6E那一行就结束了，因为上面的ecx已经无关了，且上面的汇编代码是混淆代码，也就是我们看不懂的非正常代码。于是我们把焦点继续转移到 edi 寄存器，即[edi+18C]，往上翻了代码，没有看到给edi赋值的语句，这时候我们顺便看一下右边寄存器窗口里 edi 寄存器里的值，为 0x0A927D00，加18C，得到 0x0A927E8C，刚好和CE那边的地址对应上。

![[Pasted image 20251229150239.png]]


疑问：在课程上，老师跟到这里就没有继续跟了，直接拿上一节课的基地址+18C 来作为x坐标的地址，以及上一节课的基地址+0x190作为y坐标的地址。视频中老师用 OD 追，老师追到 `[edi+18C]` 就没继续往上追了，


```cpp
void DXFDlg::OnBnClickedButtonGetplayername()
{
	// 从游戏内存中,获取玩家名字,并显示到编辑框
	wchar_t *player_name = (wchar_t*)(*(DWORD*)(*(DWORD*)0x1AB7CDC + 0x258));

	CString tmpmsg = TEXT("WCDXF ");
	tmpmsg.Append(player_name);
	OutputDebugString(tmpmsg);
}

void DXFDlg::OnBnClickedButtonGetplayerxy()
{
	FLOAT X = *(FLOAT*)(*(DWORD*)0x1AB7CDC + 0x18C);
	FLOAT Y = *(FLOAT*)(*(DWORD*)0x1AB7CDC + 0x190);

	CString tmpmsg = TEXT("WCDXF ");
	tmpmsg.AppendFormat(TEXT("X=%.2f, Y=%.2f"), X, Y);
	OutputDebugString(tmpmsg);
}
```



## DLL-获取人物血量

老师打开CE，老师把这些细节性的东西呢，通过不同的数据找法，给大家展现出来，

![[Pasted image 20251229150325.png]]


视频中，通过上图的找法，老师找到了唯一一个地址 0x4B30B6A0，然后地址相减 0x4B30B6A0-0x4B308000=0x36A0，因此这个地址就是偏移，于是我们找到了血量：

```cpp
DWORD blood = *(DWORD *)(*(DWORD*)0x1AB7CDC + 0x36A0);

{
	wchar_t *player_name = (wchar_t*)(*(DWORD*)(*(DWORD*)0x1AB7CDC + 0x258));
	FLOAT X = *(FLOAT*)(*(DWORD*)0x1AB7CDC + 0x18C);
	FLOAT Y = *(FLOAT*)(*(DWORD*)0x1AB7CDC + 0x190);
	DWORD Blood = *(DWORD *)(*(DWORD*)0x1AB7CDC + 0x36A0);

	CString tmpmsg = TEXT("WCDXF ");
	tmpmsg.Append(TEXT("名字:");
	tmpmsg.Append(player_name);
	tmpmsg.AppendFormat(TEXT("X=%.2f, Y=%.2f, 血量=%d"), X, Y, Blood);
	OutputDebugString(tmpmsg);
}
```

至此，老师找三个数据，都是通过三个不同的方法快速地找到，给大家传授各种能快速找到的经验，多添加各种各样的条件，这些很细微很细小的思路呢，可以帮助你去找别的游戏的时候，能够给你提供很多很多帮助，很多时候就是添加了这些小细节，你就能找到了。



## 初探DXF发包

ws2_32.send

ws2_32.sendto

ws2_32.WSASend

WSPSend 这个就是DNF厂商自己的发送，

如何识别 WSPSend 代码，在OD汇编窗口中，

在注释栏有 ws2_32.WEP 且紧接着下一行是 call edi 等寄存器，

基本上就确定寄存器里就是 WSPSend 函数内容了。

## 内存-OD找DNF人物坐标

首先用CE找地址，然鹅我们不知道坐标的宽度，我们搜x坐标吧，单浮点，

未知初始值，变动的数值，未变动的数值，，，筛下来十几个了，差不多了就可以了，

然后我们修改来排查，

# 网络游戏-网络发包基础


## 网络-DNF发包公共call寻找

你要分析一个游戏呢，首先你要对这个游戏的玩法有一定的了解，否则你分析很困难，

DNF是比较老的游戏了，因此它的检测什么东西呢都是特别多特别复杂的，

但是呢老师这个版本呢，也是有检测的，后面老师会讲，怎么去过掉一些检测。

ws2_32.WSPSend

关于花指令，它也只会在外层加花指令，

内层发包特别频繁的地方它是不敢加的，因为加了会影响游戏体验，所以呢它也有个度，

它在外层给我们干扰呢其实也不能彻底根治解决问题，

只要你基础掌握得扎实，都是有办法给它绕过去的，

PS: 一定要在这个模块里查看注释，不然查看不到该模块相关的注释；

如果三大基础send函数都没有，怎么办？ 那么老师随便打开一个游戏，比如老师打开天龙的登陆器，

然后找到send，然后进到里面，就能找到 WSPSend 代码了，可以顺便记录一下其特征码，


## OD找到游戏内WSPSend入口

1、首先 OD 附加别的网络程序，然后 Ctrl+G 找到 ws2_32.send，进入 ws2_32.send 函数内部，根据特征码找到 WSPSend 的调用点。



![[Pasted image 20260302125803.png]]


![[Pasted image 20260302130008.png]]


## CE遍历背包数组


通过在游戏内不断修改背包内容，然后用 CE 的【变动的数值、未变动的数值】的方式来定位内存地址。









## 网络-DNF队伍喊话call

DNF往队伍里喊话，

比如往队伍里发送字符串消息，这就是往队伍里喊话，

既然是队伍喊话，那别人肯定能看到，那这肯定是一个需要网络发包的过程，

我们准好要发送的文字11111111111，

然后在公共call的入口设置断点，然后开始发送，

触发了断点，然后我们往外返，每返一层就备注一下，层层往外返，

然后我们就可以在每个备注的层上，

打断点，在游戏里执行不同动作，来筛查出喊话的call，

然后根据堆栈信息把参数get到，

我们编写相应的汇编代码，用注入工具先注入调试一下：

```cpp
pushad
push   0x0
push   0x5ef
push   0x2
push   0x5bba7b80
mov    ecx, 0xd2c4380
mov    eax, 0x9592a0
call   eax
popad
```

注入代码后，游戏里成功喊话2222222222，

下节课老师将用代码封装喊话代码，并能指定喊话内容，

在我们MFC DLL界面里添加一个【喊话】按钮，然后实现代码：

```cpp
void Hanhua(const char *msg)
{
	DWORD talkECX = *(DWORD *)0x1AB950C;
	__asm
	{
		pushad
		push   0x0
		push   0x5ef
		push   0x2
		push   msg
		mov    ecx, talkECX
		mov    eax, 0x9592a0
		call   eax
		popad
	}
}
```


## 内存-遍历背包数组

通过CE找到背包地址，

然后通过OD去下硬件断点来往上追，追到背包基地址，

## 网络-DNF物品使用call

分析和实现物品使用call

直接把前面老师的汇编代码，

DLL新增一个【使用物品】按钮，内嵌到DLL工程代码里对应按钮回调函数里即可，

```cpp
__asm
{
	pushad
	push   0x3
	mov    ecx, 0x1a5fb24
	mov    ecx, [ecx]
	mov    eax, 0x7b9130
	call   eax
	popad
}
```

接下来，可以把上面的汇编代码进行封装，方便传参调用：

```cpp
void UseWupin(DWORD wupin)
{
	// wupin: from 0 ~ n
	wupin = wupin + 3;
	
	__asm
	{
		pushad
		push   wupin
		mov    ecx, 0x1a5fb24
		mov    ecx, [ecx]
		mov    eax, 0x7b9130
		call   eax
		popad
	}
}
```

视频中，老师使用注入工具，注入下面的汇编代码：

```cpp
pushad
push   0x3
mov    ecx, 0x1a5fb24
mov    ecx, [ecx]
mov    eax, 0x7b9130
call   eax
popad
```

老师使用工具注入汇编代码，这里使用注入工具，这只是帮助大家调试测试用，

最终我们要用 C++ 代码写出来，

## 网络-DNF自我秒杀call

把自己血量瞬间降低，

```cpp
明文血量 ---> 加密 ---》某个地址 --》解密 --》当前血量地址
```

```cpp
pushad
push   0
push   0
push   0
mov    ecx,0x46508000
push   0x000084D8        //血量值
mov    eax, 0x008174E0   //callee
call   eax
popad
```


## DNF遍历怪物数组

# 练手游戏-32位网络游戏

在前面漫长的基础知识的铺垫下，我们现在终于要开始逆向分析游戏了，

对应着微尘malloc老师的《第二阶段游戏实战(筑基)》课程，

学习新知识的最好的体验，就是能够得到及时的反馈，

我们这里在malloc老师教程的基础上，简单调整和新增了游戏的安装和登录环节，

目的就是能够让我们能够紧跟着malloc老师的课程，能够立马跟着动手验证和学习。

本章节主要分析两个经典的32位网络游戏，天龙八部和DNF靶场，

这两款游戏是非常典型的网络游戏代表，有助于让我们掌握分析的基本技能，

下面的对应小节有教大家如何安装和登录，

## 天龙安装与登录

malloc老师给的天龙下载链接: [[index.shtml]]

下面的安装包，也是从上述官网链接下载的，同学们可以直接使用，

《新天龙八部》经典怀旧正式服客户端——XTLBB-CZ-0.07.1808_GF.zip，

版本差距跟老师教程里使用的差距不大，都是零点零几的版本。

上淘宝上买一个账号，搜天龙八部账号，

联系商家说 5~15 级即可，怀旧区的就行，

级别无需太高，因为教程里老师用的9级号，

然后我买到一个：怀旧区，半城烟沙，51级，花了27.7元，商家是翔宇网络天龙八部代练，

账号: [[mailto:asw879@changyou.com]]

密码: a123456

人物角色服务区：怀旧一区——半城烟沙，51级，

如下图所示，下面就是登录后的效果：

![[Pasted image 20251229141826.png]]


![[Pasted image 20251229141835.png]]


找到游戏安装目录，安装目录里，有两个目录分别是 Bin 和 Bin64 两个目录，

分别代表着 32 位和 64 位，我们新手阶段是从32位开始，

先在32位游戏的环境下熟练掌握一些逆向的基本技能，再进阶到 64 位上，

首先你要熟悉这个游戏的基本玩法，

不多，就是熟悉装备，怎么找怪打怪，怎么回血，等等。

这样对你后续的逆向追数据有一定帮助，你做辅助开发对游戏操作一点都不了解也说不过去。




## CE查找字符串

比如查找人物名字，一边二分法批量修改一边缩小地址范围，直到找到为止。

## CE查找人物血量

登录天龙账号，然后找到我们自己人物角色的血量，

![[Pasted image 20251229141914.png]]


然后以管理员方式打开CE工具，并附加游戏进程，天龙的游戏进程是 Game.exe，

然后直接用 CE 搜索当前血量值，如下图所示，

![[Pasted image 20251229141938.png]]


然后在游戏中，操作一下道具装备，目的是让血量值有所变化，如下图所示：
![[Pasted image 20251229141955.png]]


通过CE不断查找筛选，最终找到唯一的一个血量值，

然后在CE中修改这个血量值，然后在游戏中重新打开角色信息，就能看到血量值变了，

![[Pasted image 20251229142016.png]]



然后我们再来到靶场DNF这边也试试找血量值，

首先，我们在游戏里，通过查看我的信息，即可看到HP血量值。

![[Pasted image 20251229142032.png]]


然后通过CE来查找，首次扫描出十几个，然后把装备卸掉一个，目的是为了游戏里血量值发生变化，
![[Pasted image 20251229142049.png]]



我们后续用CE最终扫到4个地址，

但是在实际修改数据体验中，发现靶场DNF并不能像天龙那样能够改变游戏内的数值，

视频中老师也讲了这个现象，

并不是所有游戏都可以这么简单让你找到内存并修改内存值的。

大家肯定不是第一次对逆向感兴趣，所以多多少少也接触过CE，

大家肯定也尝试过，也搜索过，

但是，大家会发现自己了解的那一套，时灵时不灵，有的游戏可以改有的就改不了，

有的游戏甚至你附加都附加不上，

那微尘malloc老师就是要教大家系统地学习逆向，搞定所有的游戏，

能够把所有东西的底层东西都能给它了解透彻，具体是怎么一回事。

课后作业，由于天龙32位这游戏能够找到内存并修改其值，

因此基于本节课演示的方法，

后续同学们自己去把人物属性的其他信息都找出来，一定要亲自体验一下CE使用。

## C++跨进程读血量

基于前面通过CE找到天龙血量值的地址，

我们通过使用C++的方式来访问这个地址，这里主要是跨进程读写血量值，

OpenProcess

ReadProcessMemory

WriteProcessMemory (目标内存必须是可访问的，否则会返回失败)，

我们这次演示的是跨进程读取目标进程对应内存地址的值，因此虽然上面有4个地址，但是我们随便选择一个地址，然后从C++代码的层面读取出来，从而建立一个基本的认识。

![[Pasted image 20251229142112.png]]



```cpp
#include <Windows.h>
#include <iostream>

int main(void)
{
	bool retok = false;

	// 拿到游戏的PID
	DWORD GamePid = 10816;

	// 拿到进程句柄
	HANDLE GameProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, GamePid);
	if (GameProcess == NULL)
	{
		printf("获取游戏进程句柄失败,错误码:%u\\n", GetLastError());
		return -1;
	}

	// 通过CE拿到目标的地址(比如血量)
	// 这个地址是游戏进程内的地址
	DWORD* address = (DWORD*)0x632ca6a0;

	DWORD nBuffer = 0;
	retok = ReadProcessMemory(GameProcess, address, &nBuffer, sizeof(DWORD), NULL);
	if (!retok)
	{
		printf("读取血量值失败,错误码:%u\\n", GetLastError());
		return -1;
	}

	printf("读取血量值: %u\\n", nBuffer);
	return 0;
}
```

下面是视频教程里的代码片段，目标游戏的PID，我们可以通过窗口类拿到，这里的核心函数有两个，两个函数使用示例如下代码所示，其他场景同理：

```cpp
	// 拿到游戏的PID
	DWORD GamePid = 10816;

	// 拿到游戏窗口句柄
	HWND hWnd = FindWindow(
		"TianLongBaBuHJ_WndClass", // 类名,可以通过 Spy++ 获取
		NULL  // 标题,可以通过 Spy++ 获取, 这里也能填NULL
	);

	// 通过窗口获取到进程ID
	GetWindowThreadProcessId(hWnd, &GamePid);

	// 跨进程读取人物血量值
	...
```

当然，在实际辅助中，目标游戏相关的内存是没有权限给你访问的，这时候会导致游戏图标不显示，

```cpp
hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, TargetPid);
```

比如我们通过 OpenProcess 获得到的句柄返回给 hProcess，

在攻防对战中呢，游戏公司经常就会干一件事情，就是会把这个句柄给你降权了，

把你这个句柄权限设为0，你不能读不能写，

所以呢你打开这个游戏的时候，就会出现无图标的情况，

当然我们也是可以提权的，我们后面的课程都会讲的哈，






## C++跳过游戏登陆器

进程从来不执行任何东西，真正完成代码执行的是线程，进程只是容器或者是线程的执行环境。

常规启动游戏：一般情况，游戏安装目录下，游戏都会有个登录器比如 launch.exe，而真正的游戏是game.exe，我们直接双击 game.exe 文件会弹窗让我用登陆器启动，这就是游戏官方给我们设置的小小限制。比如游戏本体通过命令行参数 lpCommandLine 来限制游戏启动。

我们如何获取其命令行呢？

首先我们通过登陆器来启动游戏，然后百度 “Windows下获取程序的命令行参数”，

下面是视频中老师以天龙为例，获取到的游戏启动参数，以及利用参数直接启动游戏的C++代码：

```cpp
// 首先要运行游戏,才能看到 Game.exe 这个进程,才能通过此命令获得参数
wmic process where caption="Game.exe" get caption,commandline /value

// 执行命令后,得到如下结果输出:
Caption=Game.exe
CommandLine=.\\Bin\\Game.exe -fl
```

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
    char szCmdLine[] = "D:\\SW\\GameTL\\Bin\\Game.exe -fl";

    // 程序运行的当前目录
    char szCurPath[] = "D:\\SW\\GameTL\\Bin";

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

下面是我们自己获取到的DNF靶场的启动参数，以及利用参数直接启动游戏的C++代码：：

```cpp
// 通过该命令先获取到 DNF.exe 进程的启动参数
wmic process where caption="DNF.exe" get caption,commandline /value

// 执行命令后,得到如下结果输出:
Caption=DNF.exe
CommandLine=DNF.exe DPLXG67FpFJYU7fGeesGGbfgAWVM0dNW42S1bjW19GxrvJ2Axk16Tz5DJ1VEV9fGy3aGYsxbKb8nElDgpCsjNI923MK9upI2ENCb1UcEG+gQgMDe9TpHcxaGKm+Y58KRW6iqKSpwEzAK1QfD+Iiqd+1jyjfNCqi7Q4SFY7jSwvA4sUDts+Kt0J2YL5IW3pY9OMzL+43AnwielGiDQnOTTpQbl8ZYWRYYhQ9SM70mfJC6XosMtoL9hsmHWmsd1yEN46PzQibCe5gIL22erAwLFaYUr/rp8xUYeailjBkTip62OrpJoMsk+T/QFRSqvsB6Y+JQBSB5KTkb8EaZPqnC3Q==
```

```cpp
#include <Windows.h>
#include <iostream>
#include <string>

static void demo_skip_launcher(void)
{
    bool bResult = true;

    /*
        如果项目字符集配置是 Unicode,
        则字符串类型变为 wchar_t,
        且字符串常量即左引号前要加上L, 比如 L"hello"
        且 std::cout 改为 std::wcout
    */

    // 要执行的命令行
    char szCmdLine[] = "E:\\\\SW\\\\Games\\\\DNF_CX_Client\\\\DNF.exe DPLXG67FpFJYU7fGeesGGbfgAWVM0dNW42S1bjW19GxrvJ2Axk16Tz5DJ1VEV9fGy3aGYsxbKb8nElDgpCsjNI923MK9upI2ENCb1UcEG+gQgMDe9TpHcxaGKm+Y58KRW6iqKSpwEzAK1QfD+Iiqd+1jyjfNCqi7Q4SFY7jSwvA4sUDts+Kt0J2YL5IW3pY9OMzL+43AnwielGiDQnOTTpQbl8ZYWRYYhQ9SM70mfJC6XosMtoL9hsmHWmsd1yEN46PzQibCe5gIL22erAwLFaYUr/rp8xUYeailjBkTip62OrpJoMsk+T/QFRSqvsB6Y+JQBSB5KTkb8EaZPqnC3Q==";

    // 程序运行的当前目录
    char szCurPath[] = "E:\\\\SW\\\\Games\\\\DNF_CX_Client";

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
}
```

下面是我们自己跳过登陆器直接启动DNF靶场游戏的运行效果：

![[Pasted image 20251229142143.png]]




下面是把上面程序代码做了一些封装，方便一次编译到处使用：

```cpp
#include <Windows.h>
#include <iostream>

/*
 
	目标游戏启动参数查询方法:

	首先通过cmd命令查看目标游戏进程启动参数:
	wmic process where caption="Game.exe" get caption,commandline /value

	执行命令后,得到如下结果输出:
	Caption=Game.exe
	CommandLine=.\\Bin\\Game.exe -fl

 */

int main(int argc, const char* argv[])
{
	if (argc != 3)
	{
		fprintf(stderr, "用法: %s  启动命令行  工作目录\\n", argv[0]);
		return -1;
	}

	/*
		如果项目字符集配置是 Unicode,
		则字符串类型变为 wchar_t,
		且字符串常量即左引号前要加上L, 比如 L"hello"
		且 std::cout 改为 std::wcout
	*/

	bool bResult = true;

	// 要执行的命令行
	// char szCmdLine[] = "D:\\\\SW\\\\GameTL\\\\Bin\\\\Game.exe -fl";
    char* szCmdLine = (char*)argv[1];

	// 程序运行的当前目录
	//  char szCurPath[] = "D:\\\\SW\\\\GameTL\\\\Bin";
    char* szCurPath = (char*)argv[2];

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
        std::cout << "进程启动成功!" << std::endl;
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

紧接着是上述封装程序的调用批处理脚本示例：

```cpp
@echo  off

cppConsoleSkipLauncher-x86.exe  "E:\\SW\\Games\\XTLBBCZ\\Bin\\Game.exe -fl"  E:\\SW\\Games\\XTLBBCZ\\Bin
```

## CS1.6找角色名字

用单机游戏来练习目标属性基地址追寻基本操作能力，

否则在网络游戏看汇编代码追地址时笨手笨脚的，

因为网络游戏可能对超时比较敏感，比如由于调试期间的暂停，服务端长时间没有得到心跳包而断开，

首先用CE找到名字确定地址，然后用调试器比如 x32dbg 找到名字基地址，

## 天龙-人物名字偏移

上一节课，我们通过CE找到了人物角色的名字的唯一地址，

这个地址没法复用，什么意思呢，

就是当下次重启游戏之后，这个地址就失效了，还得通过CE再次找地址，

因此本节课就是用OD找到它的偏移，

首先用OD或者x32dbg附加游戏进程，然后把上面拿到的绝对地址下硬件访问断点，

筛选出一个合适的触发点，（方便追的代码点），

然后往上追，

```cpp

0x4583CCDC == CE搜到的名字地址
ecx == 寄存器里面就是上面的地址

```

硬件访问断点触发处，然后一边追一边验证：

```cpp
0010595C | CC                       | int3                                    |
0010595D | CC                       | int3                                    |
0010595E | CC                       | int3                                    |
0010595F | CC                       | int3                                    |
00105960 | 55                       | push ebp                                |
00105961 | 8BEC                     | mov ebp,esp                             |
00105963 | 6A FF                    | push FFFFFFFF                           |
00105965 | 68 33A85900              | push game.59A833                        |
0010596A | 64:A1 00000000           | mov eax,dword ptr fs:[0]                |
00105970 | 50                       | push eax                                |
00105971 | 83EC 2C                  | sub esp,2C                              |
00105974 | A1 C8F87800              | mov eax,dword ptr ds:[78F8C8]           |
00105979 | 33C5                     | xor eax,ebp                             |
0010597B | 8945 F0                  | mov dword ptr ss:[ebp-10],eax           |
0010597E | 53                       | push ebx                                |
0010597F | 56                       | push esi                                |
00105980 | 57                       | push edi                                |
00105981 | 50                       | push eax                                |
00105982 | 8D45 F4                  | lea eax,dword ptr ss:[ebp-C]            |
00105985 | 64:A3 00000000           | mov dword ptr fs:[0],eax                | ecx来自上一层调用者caller
0010598B | 8BF9                     | mov edi,ecx                             | [[[ecx+0x148]+0x10]+0x2C] == 名字地址
0010598D | 8B87 48010000            | mov eax,dword ptr ds:[edi+148]          | [[[edi+0x148]+0x10]+0x2C] == 名字地址
00105993 | 8B5D 08                  | mov ebx,dword ptr ss:[ebp+8]            |
00105996 | 8B48 10                  | mov ecx,dword ptr ds:[eax+10]           | [[eax+0x10]+0x2C] == 名字地址
00105999 | 83C1 2C                  | add ecx,2C                              | [ecx+0x2C] == 名字地址
0010599C | 895D D4                  | mov dword ptr ss:[ebp-2C],ebx           |
0010599F | 8379 14 10               | cmp dword ptr ds:[ecx+14],10            |
001059A3 | C745 D0 00000000         | mov dword ptr ss:[ebp-30],0             |
001059AA | 72 02                    | jb game.1059AE                          |
001059AC | 8B09                     | mov ecx,dword ptr ds:[ecx]              | [ecx] == 名字地址
001059AE | 8D51 01                  | lea edx,dword ptr ds:[ecx+1]            |
001059B1 | 8A01                     | mov al,byte ptr ds:[ecx]                | ecx == 名字地址
001059B3 | 41                       | inc ecx                                 | 硬件访问断点 EIP 处（无法触发int3断点，不好追）
001059B4 | 84C0                     | test al,al                              |
```

```cpp
0011650F | 83EC 08                  | sub esp,8                               |
00116512 | F3:0F114424 04           | movss dword ptr ss:[esp+4],xmm0         |
00116518 | F3:0F111C24              | movss dword ptr ss:[esp],xmm3           |
0011651D | 8B8B 9C020000            | mov ecx,dword ptr ds:[ebx+29C]          |
00116523 | 8B01                     | mov eax,dword ptr ds:[ecx]              |
00116525 | FF50 04                  | call dword ptr ds:[eax+4]               |
00116528 | 8B8B 9C020000            | mov ecx,dword ptr ds:[ebx+29C]          |
0011652E | F3:0F1045 CC             | movss xmm0,dword ptr ss:[ebp-34]        |
00116533 | 8B01                     | mov eax,dword ptr ds:[ecx]              |
00116535 | 51                       | push ecx                                |
00116536 | F3:0F110424              | movss dword ptr ss:[esp],xmm0           |
0011653B | FF50 34                  | call dword ptr ds:[eax+34]              |
0011653E | 8D45 D8                  | lea eax,dword ptr ss:[ebp-28]           |
00116541 | 50                       | push eax                                |
00116542 | 8BCB                     | mov ecx,ebx                             | [[ebx+0x148]+0x10]+0x2C == 里面的值存放着名字地址
00116544 | E8 17F4FEFF              | call game.105960                        | caller调用点
00116549 | 8BD0                     | mov edx,eax                             |
```

49D103CC

[[ebx+0x148]+0x10]+0x2C 里面的值==49D103CC

## 内存-CE查找天龙人物名字

![[Pasted image 20251229142949.png]]


如上图所示，通过二分法批量修改名字，从而精确筛选出符合条件的地址。

最终通过CE找到一个确定的地址，比如: 0x4583CCDC

## 内存-OD查找天龙人物名字

# 实战64位天龙八部

## 分析坐标实现瞬移

1、判断数据宽度

2、通过在CE里面改变人物属性搜索出满足条件的内存地址

3、在目标内存地址上面，下访问或者写入，追溯代码段，追出地址的来源(基地址)

4、追溯过程 不断验证

5、CE 拼接出公式

坐标，普通的游戏都是float类型，在UE5里是double类型，

从这个位置开始，我们进入实战练习，

前面的DNF靶场是不更新的，是给大家掌握基础知识的，

而我们现在x64天龙部分，就是实战了，当你在看这个视频的时候，游戏已经更新很多版本了。

## 分析人物状态

为什么我们先找人物状态，因为它比较好找，

为什么我们要找人物状态，因为我们后面要做相关辅助的话，你需要去获知人物当前所处的状态，他是在打怪中，还是在站着不动，或者说在释放技能，还是在采药等等，

打开CE，状态的话，一般推荐先用字节找，如果说找不到或者不合适，那么再考虑用四字节或者别的。

字节搜到目标地址值： 站立 0 走路 2 使用技能 5 打坐 6 打怪 7 采药 8

用 x64dbg 打硬件访问断点触发一下，

```cpp
[rcx+0x1b8] —— 这个地址里面的值是0
[[rax+0x98]+0x1b8] —— 同一个地址，这个地址里面的值是0
[[[0x7ff7893837f8]+0x98]+0x1b8] —— 同一个地址，这个地址里面的值是0
```

于是，老师就把基地址+偏移就追出来了，

然后用CE把上面多重指针转换一下，练习一下CE指针转换的熟练度，

```cpp
[[Game.exe+7437F8]+0x98]+0x5C   人物坐标 x
[[Game.exe+7437F8]+0x98]+0x60   人物坐标 z
[[Game.exe+7437F8]+0x98]+0x64   人物坐标 y
[[Game.exe+7437F8]+0x98]+0x1b8  人物状态
```

## 分析人物升级经验数组

人物等级 和 升级经验 之间有一种联系，也就是等级越高，需要的升级经验越高，

需要把CE重新附加一下，或者附加别的，

这时候你就可以用 x64dbg 去追了，

## 分析人物的名字

## 周围-分析怪物的血量

遍历周围环境，为什么需要遍历周围，

比如我们要实现自动打怪，肯定得找到周围怪物的信息，然后我们去打周围的怪，

那这个周围怪物的信息呢，就包含怪物的对象，怪物的坐标，怪物的名字，怪物的血量等等，

这些都是我们需要找的，比如我们需要调一个打怪的call，就必须要怪物的一些信息，

再比如说，我们采矿采药，那也需要遍历周围药的信息，

那我们怎么去找呢？

因为游戏呢它本身需要显示这些东西的，

比如怪物在你视线范围内动，为什么我们能看到身边怪物在动呢，

因为我们一直在遍历周围的怪物信息，你遍历到它信息它坐标在动，

才会显示给你看，它在动的这么一个情况，

所以呢这个游戏本身啊，就是有一个一直在遍历的线程，

所以我们就找切入点去追这个线程，这条线索，

然后呢，会找到一个结构，一般来讲都是这种情况，会找到一个结构，

那这个结构里呢，就存放着怪物的各种信息，

所有的怪物信息，NPC的信息，包括地面的矿，草药，宝箱，包括你的宝宝等等信息，

都存在一个结构里面，

那这个结构呢，可能是一个链表，或者是二叉树，或者是链表套二叉树，或者是链表套数组等等，

所以呢我们可以追追看，追到这个结构，看看它到底是个啥结构，

然后呢我们自己通过代码，来把这个结构里面的数据给遍历出来，

这个就是我们最近这几节课的思路，后面几节课我们要做的东西，

那今天第一节课，我们来找找切入点，

我们怎么去找到这个遍历的数据结构，怎么去找到它，

那这个思路呢也有很多，比较常见的呢，我们可以在怪物的血量上面下个写入断，

比如说我去打它的时候，那怪物的血量会发生变化，

我们一去下写入呢，就能追到，它这个血量呢是往什么地方写的，

因为怪物血量一变化，

他就要显示给你看，它就会把这个变化后的血量存到我们的这个数据结构当中，

所以呢我们是不是可以通过下写入断，是不是就可以找到这个遍历周围的这段代码，

之后呢找到这个线程，

然后往上追呢，就有可能追到它的一个数据结构，

思路是这样的一个思路，

当然不仅仅是血量，不仅仅是人物对象，怪物对象，它相关的信息你都可以往上追，

那我们就从血量上来入手吧，

先用CE附加到游戏，这个游戏呢，你需要有点了解，

你升级升个七八级的，然后呢，这个怪物九级嘛，

然后呢，你把你身上的这些防御的装备给穿上，

攻击的装备你就空着，不然你很快就把它打死了，你穿了防御的装备呢，它也很难把你打死，

这样你俩就能形成一个僵持的局面，这样方便你去追数据，

否则你一下子把它打死了，或者它一下子把你打死了，都很难去追，对吧，时间不够，

那这个游戏怪物的这个血量呢，大概率是一个浮点数，单浮点，

这个游戏，怪物是没有具体血量值显示在游戏界面上的，

你鼠标移到怪物身上，看不到血量值，只看到一个红色血条，

那我们通过浮点找到的这个血量呢，大概率是个百分比的，

也就是说血量是零点几零点几这种的，1就是百分之百，这样的一个情况，

那我们首先扫描一下未知初始值，扫描出好多万条结果，

然后我们打一下这个怪物，再次扫描减少的数值，持续打怪，持续扫描减少的数值，

差不多地址列表里就100多个地址了，

然后我们不打怪物了，这个时候呢，搜未变动的数值，因为我一直没打它，

最后就剩6个地址了，然后根据实际怪物所剩血量，确定唯一地址，

然后我们把这个地址拉到下面，并修改它的值看看效果，从而进一步验证就是这个地址，

当然这个游戏你直接这么改是没用的哈，

这么改也只是本地看看效果，你一打回它，血量里面回归刚刚的血量了，

如果那种无需服务器验证的游戏，那么你本地改呢，就能实现修改血量的功能，

但大多数网络游戏，都是有服务器验证的，因此你改本地血量值就只能改本地值，

那我们接下来就下写入断呗，

老师使用 x64dbg 附加天龙这个游戏，然后用我们刚刚找到并验证的地址，

拿到 x64dbg 这边下个写入断看看，我们没打怪物，正常情况是不会断下来，

然后我们在游戏里打一下怪物，它这个血量发生变化，就会写入对不对，那么它就会断下来了，

```cpp
movss  dword ptr ds:[rax+8], xmm1
```

如上，我们看到是从 xmm1 写入到 [rax+0x8]，

那么我们进一步验证一下，在内存窗口看一下 [rax+0x8]，结果确实是，

然后我们就可以取消硬件断点了哈，

然继续往上追，`mov rax, qword ptr ds:[rcx+18]` ，

然后看到 rax 来自 [rcx+0x18]，放数据窗口验证一下，

`[[rcx+18]+0x8]` ，验证之后确实还是这个地址和值，

然后继续往上追，看看 rcx 的来源，往上追到函数头部了，并且没有看到给 rcx 赋值，

那么直接 Ctrl+F9 执行到返回，返回到上一层 caller 处，

```cpp

然后再往上就来自二叉树结点了,
[[[[rcx+0x28]+0x1B0]+0x18]+8] == 怪物血量值
[[[[[rsp+8]+0x28]+0x1B0]+0x18]+8] == 怪物血量值
[[[[[rax]+0x28]+0x1B0]+0x18]+8] == 怪物血量值
[[[[rax+0x28]+0x1B0]+0x18]+8] == 怪物血量值
[[[rax+0x1B0]+0x18]+8] == 怪物血量值
[[[rsi+0x1B0]+0x18]+8] == 怪物血量值
[[r14+0x18]+8] == 怪物血量值
[[rcx+0x18]+8] == 怪物血量值
[[rcx+0x18]+8] == 怪物血量值
[rax+8] == 怪物血量值
rax+8 是地址, [rax+8]是取数据, 拿到数据窗口, 查看该地址的值确实就是怪物的血量
```

反正一直追，而且64位的天龙和前面32位的靶场DNF相比，追数据相比更容易了，

因为之前的DNF靶场游戏，追数据会遇到很多看不懂的花指令，




# 练手游戏-天龙八部(64位)

## 本地数据分析(开头)

## 自己-人物属性

名字、坐标、血量、状态等信息；

```cpp
[[Game.exe+0x7437F8]+0x98]+0x5C 人物坐标x
[[Game.exe+0x7437F8]+0x98]+0x60 人物坐标z
[[Game.exe+0x7437F8]+0x98]+0x64 人物坐标y
[[Game.exe+0x7437F8]+0x98]+0x1B8 人物状态
[[[[Game.exe+0x7437F8]+0x98]+0x1B0]+0x18]+0x2960 人物当前血量

[[Game.exe+0x7437F8]+0x98] (暂时这么认为)人物对象基地址

人物的其他属性都在附近,直接可以通过CE查看内存区域的值来锁定
```

## 本地数据分析(结尾)

## 遍历周围(开头)

那我们怎么去找周围，

因为游戏它本身需要去显示周围怪物信息的，

你屏幕上能看到怪物在你附近跑动啥的，

说明游戏本身就有线程一直在遍历怪物等周围的一些信息的。

所以我们就找个切入点，去追这条线，

然后会找到一个结构，这个结构里呢就存放着怪物的信息、NPC信息、草药等信息；

这个结构呢，可能是链表、二叉树、或者链表套二叉树、或者是链表套数组等等；

所以呢我们可以追追看，

追到这个结构，看看这个机构到底是个啥，

然后呢，我们就通过代码把这个结构里的数据给遍历出来，这就是我们最近这几节课的思路。

## 分析怪物血量

比如我们在某怪物的血量上下个写入断，

当我们去打这个怪物的时候，它的血量也会发生相应的变化，

就能追到它这个血量是往什么地方写的，

因为怪物血量一变化，它就要显示给你看，它就会把变化后的血量存到数据结构中，

## 遍历周围(结尾)

# 诛仙x64

## x64的区别

寄存器的区别、函数的调用约定

## x64汇编模块

1、VS新建 C++ 工程，选为x64，

2、然后右键工程 —》生成依赖项 —》生成自定义 —》勾选两个(marmasm…, masm…) —》确定；

3、工程源文件里新增一个 .asm 的源文件，以后汇编相关代码就放到该文件里；

4、右键该 .asm 文件 —》属性 —》配置属性 —》常规 —》项类型 —》选择 Microsoft Macro Assembler。

删除 C 代码里的 main 函数，我们在汇编里实现这个main函数，

```cpp
extern getchar:far  //声明被调用的外部函数
.code
main proc
	sub  rsp, 100h   //x64宏汇编里,十六进制必须这样用h形式
	call getchar
	add  rsp, 100h
	ret
main endp
end
```

下面是C代码给汇编调用，以及汇编函数给C调用，两者相互访问对方的全局变量:

```cpp
#include <iostream>
extern "C" int cpp_add(int a, int b);
extern "C" int asm_add(int a, int b);

int cpp_add(int a, int b) { return a + b; }

int main(void)
{
	int a = asm_add(1, 2);
	printf("a = %d\\n", a);
	return 0;
}
```

```cpp
extern cpp_add:far      ;符号声明

.code                   ;代码段开始
asm_add proc
	sub rsp, 32h
	xor rax, rax
	mov rax, rcx
	add rax, rdx

	mov [rsp+00h], rax  ;保存rax
	call asm_test       ;call test
	mov rax, [rsp+00h]  ;恢复rax

	add rsp, 32h
	ret
asm_add endp

asm_test proc
	sub rsp, 32h
	mov rcx, 3          ;参数1
	mov rdx, 4          ;参数2
	call cpp_add
	mov rax, rax        ;返回值
	add rsp, 32h
	ret
asm_test endp

end                     ;代码段结尾
```

VS汇编这边有个BUG，比如汇编文件访问C那边的全局变量时，比如全局变量num，

汇编这边如果想要访问到变量里面的值，必须要多访问一层，如下:

```nasm
asm_test proc
	sub rsp, 32h
	mov rax, num   ;等同于 lea  rax, num --> rax = &num
	mov rax, [rax] ;这时才访问到num的值
	add rsp, 32h
	ret
asm_test endp


;为了防止混淆常规mov,我们直接用lea改写
asm_test proc
	sub rsp, 32h
	lea rax, num   ;等同于 lea  rax, num --> rax = &num
	mov rax, [rax] ;这时才访问到num的值
	add rsp, 32h
	ret
asm_test endp
```

## x64dll劫持注入

比如魔兽，你直接远线程注入的话，它是能检测到的，

因此这里教给大家一个新的注入方式，劫持系统dll来进行注入，

这种方式非常好用，麻烦是麻烦了点，但是能解决问题，

那它是一个什么样的原理呢？

游戏本身运行起来的时候，会先加载其安装目录下的dll文件，然后会加载system32里面的dll文件，

首先我们新建一个dll，且名字完全和系统某个dll完全相同，并且把这个dll放到游戏安装目录对应位置下，

这样游戏起来就会优先加载其目录下的对应系统dll，

也就是说我们伪造一个同名dll，实现它本该有的功能，然后把我们自己的功能注入进去，

拿到系统dll，我们首先要找出其导出函数，比如 version.dll ，这个是游戏常用到的，

而且它的导出函数很少，只有十几个，

然后我们要用到一个工具 Dependency Walker，它可以显示这个dll的导出函数列表，

然后全选导出函数，鼠标右键，Copy Function Names，放到临时的记事本里，

VS新建dll工程，Windows桌面 —》具有导出项的(DLL)动态链接库，名字为 version，和系统dll名字一样，

把汇编依赖项配置勾选上，然后新建一个汇编文件 call.asm，

```cpp
extern sysdll_funcs:far

.code
GetFileVersionInfoA proc
jmp qword ptr [sysdll_funcs + 8*1]
GetFileVersionInfoA endp
    
GetFileVersionInfoByHandle proc
jmp qword ptr [sysdll_funcs + 8*2]
GetFileVersionInfoByHandle endp
    
GetFileVersionInfoExA proc
jmp qword ptr [sysdll_funcs + 8*3]
GetFileVersionInfoExA endp
    
GetFileVersionInfoExW proc
jmp qword ptr [sysdll_funcs + 8*4]
GetFileVersionInfoExW endp
    
GetFileVersionInfoSizeA proc
jmp qword ptr [sysdll_funcs + 8*5]
GetFileVersionInfoSizeA endp
    
GetFileVersionInfoSizeExA proc
jmp qword ptr [sysdll_funcs + 8*6]
GetFileVersionInfoSizeExA endp
    
GetFileVersionInfoSizeExW proc
jmp qword ptr [sysdll_funcs + 8*7]
GetFileVersionInfoSizeExW endp
    
GetFileVersionInfoSizeW proc
jmp qword ptr [sysdll_funcs + 8*8]
GetFileVersionInfoSizeW endp
    
GetFileVersionInfoA proc
jmp qword ptr [sysdll_funcs + 8*9]
GetFileVersionInfoA endp
    
VerFindFileA proc
jmp qword ptr [sysdll_funcs + 8*10]
VerFindFileA endp
    
VerFindFileW proc
jmp qword ptr [sysdll_funcs + 8*11]
VerFindFileW endp
    
VerInstallFileA proc
jmp qword ptr [sysdll_funcs + 8*12]
VerInstallFileA endp
    
VerInstallFileW proc
jmp qword ptr [sysdll_funcs + 8*13]
VerInstallFileW endp
    
VerLanguageNameA proc
jmp qword ptr [sysdll_funcs + 8*14]
VerLanguageNameA endp
    
VerLanguageNameW proc
jmp qword ptr [sysdll_funcs + 8*15]
VerLanguageNameW endp
    
VerQueryValueA proc
jmp qword ptr [sysdll_funcs + 8*16]
VerQueryValueA endp
    
VerQueryValueW proc
jmp qword ptr [sysdll_funcs + 8*17]
VerQueryValueW endp

end
```

version.cpp

```cpp
#include "pch.h"

extern "C" UINT_PTR sysdll_funcs[24] = { 0 };
void GetAddr()
{
    HMODULE hModule = LoadLibraryA("sysversion.dll");
    if (hModule)
    {
        for (int i = 1; i <= 17; i++)
        {
            sysdll_funcs[i] = (UINT_PTR)GetProcAddress(hModule, (char*)i);
        }
    }
}
```

dllmain.cpp

```cpp
extern void GetAddr();

DWORD WINAPI LoadMyDll(LPVOID arg)
{
	LoadLibraryA("mydll.dll");
	return 1;
}

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    {
	    GetAddr(); // 这个位置调用
	    ::CreateThread(0,0,LoadMyDll,0,0,0);
    }
        
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
```

然后我们这个dll本身没有导出，因此我们需要新增模块定义文件，

右键源文件(目录) —》添加新建项 —》模块定义文件(.def) —》名字默认 —》添加；

```cpp
LIBRARY
EXPORTS
GetFileVersionInfoA @1
GetFileVersionInfoByHandle @2
GetFileVersionInfoExA @3
GetFileVersionInfoExW @4
GetFileVersionInfoSizeA @5
GetFileVersionInfoSizeExA @6
GetFileVersionInfoSizeExW @7
GetFileVersionInfoSizeW @8
GetFileVersionInfoA @9
VerFindFileA @10
VerFindFileW @11
VerInstallFileA @12
VerInstallFileW @13
VerLanguageNameA @14
VerLanguageNameW @15
VerQueryValueA @16
VerQueryValueW @17
```

## 特征码定位(代码定位)

```cpp
// 拿到游戏窗口句柄
HWND hGame = ::FindWindowA("窗口类名", NULL);

// 拿到游戏进程ID
::GetWindowThreadProcessId(hGame, &ProcessId);

// 拿到进程句柄
hProcess = GetProcessHandle(ProcessId);

// 获取模块基地址、模块大小
m_data = MyGetModule(ProcessId, "进程名");

```

```cpp
DWORD64 MySearchMemory()
{

	// VirtualQueryEx 一页一页地扫描,然后返回信息填充到mbi结构里
	while (VirtualQueryEx(hProcess,(LPVOID)StartAddress,&mbi,sizeof(mbi)) != 0)
	{
		// 获取 rw 或 rwx 属性的内存块
	}
}

DWORD64 MyGetAddress()
{
	MySearchMemory(进程句柄,特征码,模块地址,模块结束地址,容器容量,容器引用);
	
	// 容器中存放着代码地址
	
	// 把代码地址里面的值读取出来
	ReadProcessMemory(进程句柄,...,NULL);
}

MyGetModule(DWORD Pid, const wchar_t *Name)
{
	mymodule_data *data = NULL;
	
	// 拿到该进程所有模块的快照
	HANDLE hModuleSnap = CreateToolHelp32Snapshot(TH32CS_SNAPMODULE,Pid);
	
	MODULEENTRY32 me32;
	me32.dwSize = sizeof(MODULEENTRY32);
	
	// 拿到第一个模块的信息
	Module32First(hModuleSnap, &me32);
	
	// 然后继续遍历剩下的模块信息
	do {
		if (Pid == me32.th32ProcessID) {
			
			if (!wcscmp(Name, me32.szModule)) {
				data = new mymodule_data();
				data->MAddress = (DWORD64)me32.modBaseAddr;
				data->MSize = me32.modBaseSize;
			}
			
		}
	} while (Module32Next(hModuleSnap, &me32));
	
	CloseHandle(hModuleSnap);
	return data;
}
```







# bottom




