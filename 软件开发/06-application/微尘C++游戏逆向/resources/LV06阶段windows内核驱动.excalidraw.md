---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠== You can decompress Drawing data with the command palette: 'Decompress current Excalidraw file'. For more info check in plugin settings under 'Saving'


# Excalidraw Data

## Text Elements
windbg常用命令 ^HCYvMabm

bc* —— 清除所有断点
bl  —— 查看断点清单
bu funcname —— 打函数断点
bu —— 表示新增断点，比如 bu ntOpenProcess 表示在该函数处设置断点
bl —— 表示显示断点列表；

r   —— 查看寄存器表
u funcname [l行数] —— 查看反汇编代码
u 00007ff7`721d2f42 —— 查看此地址开始的反汇编代码
u 00007ff7`721d2f42 l20 —— 表示查看该地址20行反汇编代码
【地址高位以fff开头的就是内核空间的地址, 000开头的是用户空间】
r —— 显示当前时刻所有寄存器的值
kp —— 显示堆栈信息
X nt!Ps*cid*    —— 查找带Ps cid字样的函数
dq nt!PspCidTable    ——8字节方式显示其内存数据
dt _HANDLE_TABLE 上述表项里的8字节内容



dt —— 表示命令格式化显示变量的资料和结构
t —— 单步执行(step)



.reboot —— 重启目标系统
.reload —— 表示重新加载符号
.cls —— 表示清屏 ^EP84ZSjh

处理文件校验和系统引导 ^34Efqbeq

set ENTRY_GUID={46595952-454E-4F50-4747-554944FFFFFF}
bcdedit -create %ENTRY_GUID% -d "微尘网络安全" -application OSLOADER
bcdedit -set %ENTRY_GUID% device partition=%SYSTEMDRIVE%
bcdedit -set %ENTRY_GUID% osdevice partition=%SYSTEMDRIVE%
bcdedit -set %ENTRY_GUID% systemroot \Windows
bcdedit -set %ENTRY_GUID% path \Windows\system32\qq8132000_winload.exe
bcdedit -set %ENTRY_GUID% kernel qq8132000_ntoskrnl.exe
bcdedit -set %ENTRY_GUID% recoveryenabled 0
bcdedit -set %ENTRY_GUID% nx OptOut
bcdedit -set %ENTRY_GUID% nointegritychecks 1
bcdedit -displayorder %ENTRY_GUID% -addlast
bcdedit -default %ENTRY_GUID%
bcdedit -timeout 30 ^y8EUjdSP

如下代码是新增 Windows加载器，新手建议一行一行手动执行
(GUID随便改其中一个数值即可,不与你原系统一样即可) ^dVMqQoVW

执行完后，直接执行bcdedit查看，再通过msconfig查看加载器多了一项 ^kl419Gtw

处理内核签名校验 ^qacgYFR1

校验代码在: winload.exe or winload.efi ^82iFlI5o

OsIInitializeCodeIntegrity
ImgpValidateImageHash
操作: 让上面两个函数直接返回1即可, 类似如下

OsIInitializeCodeIntegrity:
        mov  al, 1
        retn ^KdHkFUDi

实现破图标 ^yD6XyaiX

ntoskrnl.exe

ObpReferenceObjectByHandleWithTag
特征码: bf 22 00 00 c0

把 jnz loc_1404DC614 用nop替换即可，即: 替换成 --> 90 90 90 90 90 90 ^y1EUaCys

Windows调试体系（过调试函数） ^hvt4DpX8

讲这个调试体系的目的，
我们是要做能够过ACE等的调试保护，
让我们能够正常CE、OD、xdbg、附加、打断点、读写内存等调试操作 ^vnR4QgEm

调试器 ^5ZNTbFTx

被调试进程 ^VePUeaj5

DebugActiveProcess: 其实就是动态调试器的附加操作
下面是网上抄的最简单的调试器代码，经过malloc老师改过的： ^IKpkFacH

结构体
_DEBUG_OBJECT ^RYhI9NfW

#include "stdio.h"
#include <windows.h>
#include <stdlib.h>

int main(int argc, char* argv[])
{
        bool isContinue = true;
        DEBUG_EVENT dbgEvent;
        int pid;

        puts("请输入调试进程的 PID：");
        scanf("%d", &pid);
        
        BOOL ret = DebugActiveProcess(pid);

        if (ret)
        {
                while (isContinue)
                {
                        ret = WaitForDebugEvent(&dbgEvent, INFINITE);
                        if (!ret)
                        {
                                printf("WaitForDebugEvent 出错：%d", GetLastError());
                                break;
                        }

                        switch (dbgEvent.dwDebugEventCode)
                        {
                        case EXCEPTION_DEBUG_EVENT:
                                puts("EXCEPTION_DEBUG_EVENT");
                                break;
                        case CREATE_THREAD_DEBUG_EVENT:
                                puts("CREATE_THREAD_DEBUG_EVENT");
                                break;
                        case CREATE_PROCESS_DEBUG_EVENT:
                                puts("CREATE_PROCESS_DEBUG_EVENT");
                                break;
                        case EXIT_THREAD_DEBUG_EVENT:
                                puts("EXIT_THREAD_DEBUG_EVENT");
                                break;
                        case EXIT_PROCESS_DEBUG_EVENT:
                                puts("EXIT_PROCESS_DEBUG_EVENT");
                                break;
                        case LOAD_DLL_DEBUG_EVENT:
                                puts("LOAD_DLL_DEBUG_EVENT");
                                break;
                        case UNLOAD_DLL_DEBUG_EVENT:
                                puts("UNLOAD_DLL_DEBUG_EVENT");
                                break;
                        case OUTPUT_DEBUG_STRING_EVENT:
                                puts("OUTPUT_DEBUG_STRING_EVENT");
                                break;
                        default:
                                break;
                        }

                        ret = ContinueDebugEvent(dbgEvent.dwProcessId, 
                                dbgEvent.dwThreadId, DBG_CONTINUE);

                }
        }
        else
        {
                printf("DebugActiveProcess 失败：%d\n", GetLastError());
        }

        system("pause");
        return 0;
} ^56Mipfot

(_EPROCESS)->DebugPort
ACE等各种保护它会检查 DebugPort 是否为空，如果不为空，则表示有调试器在调试目标游戏

0: kd> !process 0 0 notepad.exe
PROCESS ffffae0fd77e9080
    SessionId: 1  Cid: 1f40    Peb: 10020e000  ParentCid: 0884
    DirBase: 2395a000  ObjectTable: ffff9781ff1c0040  HandleCount: <Data Not Accessible>
    Image: notepad.exe

0: kd> dt _EPROCESS ffffae0fd77e9080
ntdll!_EPROCESS
   +0x000 Pcb              : _KPROCESS
   +0x2d8 ProcessLock      : _EX_PUSH_LOCK
   +0x2e0 RundownProtect   : _EX_RUNDOWN_REF
   +0x2e8 UniqueProcessId  : 0x00000000`00001f40 Void
   ...
   +0x420 DebugPort        : (null)     (如果非空, 则其存放了 _DEBUG_OBJECT 实例)

(1) windbg下个调试断点: ba r1 进程地址+0x420    (Access访问断点)
(2) 客户机里用CE附加目标进程，随便找个地址，并下硬件访问断，从而触发该断点

ACE 等 各种保护 他会检查这个地方DebugPort        如果这里是有值的话 ，那就说明 你在被调试
1. DbgkpSetProcessDebugObject: 设置指定进程的调试对象。调试对象可以是一个或多个调试器的句柄，用于监视和调试该进程。
2. KiDispatchException: 内部函数，用于处理异常并将其传递给异常处理程序。它负责分发异常到适当的处理程序或进行系统崩溃的处理。
3. DbgkForwardException: 将异常传递给调试器进行处理。此函数用于将异常信息发送到调试器，并等待调试器采取进一步的操作，如调试进程、记录异常信息等。
4. DbgkUnMapViewOfSection: 取消映射指定进程的区段。它用于从进程的虚拟地址空间中移除指定的区段映射，以释放内存资源。
5. DbgkExitProcess: 处理进程退出的调试相关操作。它在进程退出时触发，执行与进程调试相关的清理操作，如关闭调试器句柄、释放资源等。
6. DbgkExitThread: 处理线程退出的调试相关操作。它在线程退出时触发，执行与线程调试相关的清理操作，如关闭调试器句柄、释放资源等。
7. DbgkCreateThread: 创建具有调试相关属性的线程。它创建一个新的线程，并为其设置调试标志，以允许调试器监视和控制该线程的执行。
8. DbgkClearProcessDebugObject: 清除进程的调试对象。它用于清除进程的调试对象设置，即将进程的调试对象句柄设置为空。
9. DbgkMapViewOfSection: 将区段映射到指定进程的虚拟地址空间。它在指定进程的虚拟地址空间中创建一个新的区段映射，并将其填充为指定的数据。
10. DbgkpCloseObject: 内部函数，用于关闭调试对象。它用于关闭调试对象句柄，并执行与调试对象相关的清理操作。
11. PspExitThread: 线程退出的处理操作。它在线程退出时触发，执行与线程资源释放和退出相关的操作，如清理线程数据结构、释放资源等。
12. DbgkpQueueMessage: 将消息发送到调试器。它用于将消息发送给调试器处理，并等待调试器处理或回复。
13. PspTerminateAllThreads: 终止指定进程的所有线程。它用于强制终止指定进程的所有线程，无论线程的状态和执行位置如何。
14. PspProcessDelete: 删除指定进程的内部数据结构。它执行与指定进程相关的数据结构和资源的释放和清理操作。
15. DbgkCopyProcessDebugPort: 复制调试端口到目标进程。它用于将调试端口从源进程复制到目标进程，以便让目标进程与调试器建立连接。
16. DbgkCreateMinimalThread: 创建具有最小化线程环境的线程。它创建一个具有很少线程环境设置的新线程，用于执行最小化的线程上下文。
这些函数用于操作和控制调试器相关的行为与信息，与调试和异常处理机制密切相关。它们通常在操作系统的内核级别中使用，以支持调试器和异常处理的实现和功能。



0: kd> dt _EPROCESS ffffae0fd77e9080
ntdll!_EPROCESS
   +0x000 Pcb              : _KPROCESS
   +0x2d8 ProcessLock      : _EX_PUSH_LOCK
   +0x2e0 RundownProtect   : _EX_RUNDOWN_REF
   +0x2e8 UniqueProcessId  : 0x00000000`00001f40 Void
   ...
   +0x304 Flags            : 0x144d0c11
   +0x304 CreateReported   : 0y1
   +0x304 NoDebugInherit   : 0y0    (当该进程被调试时,内核该对象的该字段会被清空)

当进程被调试时其进程内核对象EPROCESS的NoDebugInherit字段会被置空，调用NtQueryInformationProcess可以检测此字段的值。 ^9BLpkggS

IDA常用操作 ^ZUW5rHCo

【载入文件】启动IDA后，直接把目标可执行文件拖拽到IDA界面；

【查找函数】左侧函数列表窗口，点中任意项，然后 Ctrl+F 搜索目标函数；

【代码转换】反汇编和C互相转换，按F5

反汇编窗口：
d —— 以数据的形式显示；
c —— 以反汇编代码形式显示；
a —— 以ASCII码方式显示；
u —— 以未定义方式显示(原始十六进制)




; —— 添加注释
: —— 添加注释(函数开头分号不好使, 可以用冒号)
Alt+b —— 搜索特征码(比如 F0 83 8E 04 03 00 00 03)
Alt+t —— 搜索反汇编中的字符串(比如 +420h])

Hex View 十六进制窗口: 
    (1) 打开子窗口: 左上View菜单 >> Open subviews >> Hex dump
    (2) 开启选中同步: 随便选中十六进制数据, 右键 >> 选择和比如 IDA View-A 反汇编窗口同步 
    (3) 修改数据: 鼠标选中对应字节 >> F2 >> 开始修改 >> F2 >> 修改完成


同步 Hex 视图
    (1) 菜单：View → Open subviews → Hex
    (2) 在 Hex 窗口右键，勾选 Synchronize with → Disassembly
    (3) 点击反汇编代码，Hex 窗口会自动跳转到对应机器码 ^hVVzoXOk

VMP加壳（VS自动编译、vmp加壳、签名、云下发） ^xWSbHp3A

【VMP加壳】就是把我们的代码加各种跳转，实现代码膨胀，让我们的特征被扰乱，这样干扰别人识别；
比如你驱动很多人用，容易被特征到，你重新加壳之后又可以重新蹦跶起来了。


定时VS自动编译、自动加壳、自动签名、自动下发安装，这样在攻防中能够有效防止被特征定位；
【VS自动编译】VS能够调用命令自动编译，从而可以根据需求实现自动化编译；
【VMP自动加壳】加壳工具也提供了控制台的命令 (VMProtect_Con.exe)，从而能够实现自动化加壳； ^nGY9Slxk

系统调用与SSDT(系统服务描述符表) ^sT3n409k

双机调试（虚拟机+windbg） ^Dx3639YC

之前我们在虚拟机上，运行我们的驱动，
双机调试的作用很大，我们在实际开发过程中会遇到各种蓝屏各种错误，
其实你学驱动还是学应用层软件开发，你把调试这块搞得很扎实，你去研究什么东西至少能解决70%的问题，
那我们怎么调试呢？怎么单步去运行虚拟机里面的代码呢？
前面我们安装完WDK之后呢，就会有个 windbg 工具，直接在左下角搜索栏里搜其名字。

1、虚拟机删除打印机，然后添加新硬件，添加串行端口；

2、使用命名的管道，填写内容  \\.\pipe\abc123

3、虚拟机开机，然后 msconfig >> 引导 >> 高级选项 >> 勾选调试，COM1，115200

4、找到 windbg.exe 所在位置，然后将其发送到桌面快捷方式，并在快捷方式里添加如下命令参数

-b -k com:pipe,port=\\\\.\\pipe\\abc123,resets=0,reconnect=y

完整的命令如下:
"D:\\Windows Kits\\10\\Debuggers\\x64\\windbg.exe" -b -k com:pipe,port=\\\\.\\pipe\\abc123,resets=0,reconnect=y ^17lA7OMu

虚拟机系统设置，即虚拟机内的系统设置，不是物理机系统设置。

上述设置好之后，先运行 windbg，然后虚拟机开机，就能看到 windbg 连上了虚拟机 Windows，

windbg 是否要以管理员方式运行，经过实验验证，无需管理员也能监控虚拟机，

下面是通过 windbg 来获取驱动的打印输出，驱动直接打印即可，

并且，DbgPrintEx 不区分调试还是Release，即使VS端是以Release编译，照样能通过 windbg 或者 dbgView 看到输出。 ^Ftv56dCH

// x64 debug

struct text {
    int a;
    int b;
};

void CMFCApplication2Dlg::OnBnClickedOk()
{
    CDialogEx::OnOK();
    __debugbreak(); // int 3 中断
    
    text t;
    t.a = 1;
    t.b = 2;
    OpenProcess(0x1234, 0, 0);
} ^B2Meus9w

添加如上代码，把MFC应用编译后拖拽到虚拟机里运行，
然后点击确定按钮，触发int 3软中断，此时 windbg 就捕捉到了

然后 windbg 可以执行 .reload ，该命令会花费一点时间，之后就能源码级调试(同步源码)； ^iY4W3ZMx

1. g
2. 输入要跳转的地址 ^X7wXrvko

x64dbg >> 附加MFC应用 >> 按钮里有 OpenProcess 调用

kernel32.dll
        OpenProcess

kernelbase.dll  (win10兼容层)
        OpenProcess >> 参数处理 >> 调用 ZwOpenProcess

ntdll.dll
        ZwOpenProcess >> 26h >> syscall >> ret ^IyQ05TvC

x64dbg >> 附加MFC应用 >> 按钮里有 ReadProcessMemory 调用

kernel32.dll
        ReadProcessMemory

kernelbase.dll  (win10兼容层)
        ReadProcessMemory >> 参数处理 >> 调用 NtReadVirtualMemory

ntdll.dll
        NtReadVirtualMemory >> 3Fh >> syscall >> ret ^gOtXLTbU

驱动级跨进程读写内存(突破TP、NP保护)
附加+内存拷贝
20~21课 ^RFNWMZag

void CHelloWord3Dlg::OnBnClickedButton8()
{
        UpdateData(1);

        //CString pid;
        //CString address;
        LONGLONG game_addr;
        StrToInt64ExW(address.GetString(), STIF_SUPPORT_HEX,&game_addr);
        LONGLONG game_pid;
        
        StrToInt64ExW(pid.GetString(), STIF_SUPPORT_HEX, &game_pid);
        UINT64 Mybuf[3] = { game_pid,game_addr ,8 };//读取8字节整型数据
         DWORD len = 0;
        UINT64 Outbuf=0;
        BOOL ret = DeviceIoControl(nDeviveHandle, 过保护读内存, &Mybuf, sizeof(Mybuf), 
                &Outbuf, sizeof(Outbuf), &len, NULL);

        // 把读取到的数据打印出来
        printf("Outbuf = %llx\n", Outbuf);
} ^EQuRHOsK

#include <ntifs.h>

void ReadProcessByAtt(IRP* Irp)
{
        UINT64 buf[3] = { 0 };
        //__debugbreak();

        // 拿到用户空间传进来的目标游戏PID、游戏内存地址等信息
        RtlCopyMemory(buf, Irp->AssociatedIrp.SystemBuffer, sizeof(buf));

        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer0=%llx\n", buf[0]);
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer1=%llx\n", buf[1]);
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer2=%llx\n", buf[2]);

        // 根据游戏PID拿到游戏的进程实例
        PEPROCESS pep = NULL;
        PsLookupProcessByProcessId(buf[0], &pep);

        // 申请驱动内存
        PVOID p = ExAllocatePool(NonPagedPool, 8);

        // 附加到游戏进程
        KAPC_STATE apc;
        KeStackAttachProcess(pep, &apc);

        // 附加之后，直接从游戏地址执行内存拷贝
        RtlCopyMemory(p, buf[1], 8);

        // 脱离游戏进程
        KeUnstackDetachProcess(&apc);

        // 把读取到的数据反馈给辅助工具
        RtlCopyMemory(Irp->AssociatedIrp.SystemBuffer, p, 8);

        // 释放驱动内存(用完后及时释放)
        ExFreePool(p);

        // 解除引用游戏游戏进程
        ObDereferenceObject(pep);
}

NTSTATUS
MyCrteate(
        _In_ struct _DEVICE_OBJECT *DeviceObject,
        _Inout_ struct _IRP *Irp
)
{
        
        DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "NTSTATUS coming in \n");
        PIO_STACK_LOCATION isl=IoGetCurrentIrpStackLocation(Irp);
        switch (isl->MajorFunction)
        {
        case IRP_MJ_DEVICE_CONTROL:
        {
                UINT32 控制码=isl->Parameters.DeviceIoControl.IoControlCode;

                if (控制码 == 过保护读内存)
                {
                        // 核心代码片段(读取目标游戏进程的内存数据)
                        ReadProcessByAtt(Irp);

                        Irp->IoStatus.Status = STATUS_SUCCESS;
                        Irp->IoStatus.Information = 8;
                        IoCompleteRequest(Irp, IO_NO_INCREMENT);
                        return STATUS_SUCCESS;
                }

                break;
        }
        
        default:
                break;
        }
        
        Irp->IoStatus.Status = STATUS_SUCCESS;
        Irp->IoStatus.Information = 4;
        IoCompleteRequest(Irp, IO_NO_INCREMENT);
        return STATUS_SUCCESS;
} ^48Ybge8u

驱动实现线程和进程的监控（保护进程） ^tAFe3ILM

微软未公开声明的函数: PsGetProcessImageFileName()
作用: 你把进程结构体传进去，就能得到进程的名字 ^vZxgTuVN

const char*PsGetProcessImageFileName(PEPROCESS arg1);

OB_PREOP_CALLBACK_STATUS PobPreOperationCallback(
        PVOID RegistrationContext,
        POB_PRE_OPERATION_INFORMATION OperationInformation
)
{
        PEPROCESS pep = IoGetCurrentProcess();
        char* nName = PsGetProcessImageFileName(pep);
        char* nName = PsGetProcessImageFileName(OperationInformation->Object);
        // Q?: 以上两种方式获取的进程，有什么区别？

        /*
        A@: 当 A 进程通过 OpenProcess 打开 B 进程时：
                IoGetCurrentProcess() → A（发起者）
                OperationInformation->Object → B（目标）
        */


        // 防守方: 如果可执行程序文件名是 8132000.exe
        if (_strnicmp(nName, "8132000.exe", strlen("8132000.exe")) == 0)
        {
                // 关闭所有权限: 表现为你在任务管理器里无法结束该进程, 即使管理员也不行
                DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, " 进入nName=%s \n", nName);
                OperationInformation->Parameters->CreateHandleInformation.DesiredAccess = 0;
                OperationInformation->Parameters->DuplicateHandleInformation.DesiredAccess = 0;
        }

        // 破解方: 如果可执行程序文件名是 8132000.exe
        if (_strnicmp(nName, "8132000.exe", strlen("8132000.exe")) == 0)
        {
                // 开放所有权限
                // 如果是进程A，则需要给A自己提权

                DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, " 进入nName=%s \n", nName);
                OperationInformation->Parameters->CreateHandleInformation.DesiredAccess = 0x1fffff;
                OperationInformation->Parameters->DuplicateHandleInformation.DesiredAccess = 0x1fffff;

                // DesiredAccess/OriginalDesiredAccess 相关字段: PROCESS_TERMINATE, PROCESS_ALL_ACCESS;
        }
}


void ObRegisterCallbacksInit()
{

        OB_CALLBACK_REGISTRATION ocr;

        OB_OPERATION_REGISTRATION oor;
        UNICODE_STRING us= RTL_CONSTANT_STRING(L"8132000");
        ocr.Version = OB_FLT_REGISTRATION_VERSION;
        ocr.OperationRegistrationCount = 1;
        ocr.Altitude = us;
        ocr.RegistrationContext = NULL;
        ocr.OperationRegistration = &oor;
        oor.ObjectType = PsProcessType;
        oor.Operations = OB_OPERATION_HANDLE_CREATE | OB_OPERATION_HANDLE_DUPLICATE;
        oor.PreOperation = PobPreOperationCallback;
        oor.PostOperation = NULL;

        NTSTATUS ns=ObRegisterCallbacks(&ocr,&rh);
        DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, " ns=%x \n", ns);
}

NTSTATUS DriverEntry(
        PDRIVER_OBJECT  DriverObject,
        PUNICODE_STRING RegistryPath
) {
        // ...

        DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, " 即将进入ObRegisterCallbacksInit \n");

        // 验证签名的结构体: _LDR_DATA_TABLE_ENTRY
        _LDR_DATA_TABLE_ENTRY* pLdrData = (_LDR_DATA_TABLE_ENTRY*)DriverObject->DriverSection;
        pLdrData->Flags = pLdrData->Flags | 0x20; // 先绕过签名检查

        ObRegisterCallbacksInit();

        return STATUS_SUCCESS;

} ^VKyqd0oA

签名生成工具: signtools-v3.2.zip

签名需要的证书文件: xxx.pfx
老师提供的过期证书文件: 蓝洞签名密码1.pfx

使用signtools导入证书，密码随你便设置
        (1) 证书管理 >> 导入 >> 选择你要导入的pfx文件
        (2) 签名规则 >> 命名用非中文
        (3) 数字签名 >> 添加文件(.sys文件) >> 数字签名 >> 驱动模式

开始日期——截止日期：
        (1) 我们在安装驱动之前临时把系统日期改在日期范围内；
        (2) 安装驱动之后把系统日期改回来即可。 ^RVlfviIG

Windows 10 过签名方法 ^lvU5uby7

MDL实现驱动读写
37~38课 ^8O7pHYv9

开关读写保护（CR3寄存器WP字段） ^P5K3GNbE

MDL 内存描述符列表
某个物理页，可以对应多个虚拟地址，MDL就能实现这样的效果

比如当我们要对一块内核内存进行修改时，
我们要先为这块内存创建MDL，其会建立一个新的虚拟内存空间，与目标内存的物理地址建立映射关系。
 ^JuSb6Alc

全局句柄表和私有句柄表(28~33课)

Windows调试体系(43~47课)

Windows系统引导和内核(47课) ^mBamUY9p

驱动基础 ^BhDeywpV

NTSTATUS DriverEntry(
         PDRIVER_OBJECT  DriverObject,
         PUNICODE_STRING RegistryPath
) {
        DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "helloword  RegistryPath=%wZ\n", RegistryPath);
        DbgPrintEx(DPFLTR_IHVDRIVER_ID,0,"hellowordDriverObject->DriverName=%wZ\n", DriverObject->DriverName);
        return STATUS_SUCCESS;
} ^3L1c9IrV

打印Unicode字符串的格式: %wZ ^aODLqXaT

NTSTATUS MyCrteate(
        _In_ struct _DEVICE_OBJECT *DeviceObject,
        _Inout_ struct _IRP *Irp)
{
    PIO_STACK_LOCATION isl=IoGetCurrentIrpStackLocation(Irp);
    
    switch (isl->MajorFunction)
    {
        // ...
        case IRP_MJ_READ:
        {
                DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, " IRP_MJ_READ  \n");
                char aa[] = "weichen777微尘";
                RtlCopyMemory(Irp->UserBuffer,aa,sizeof(aa));
                break;
        }
        case IRP_MJ_DEVICE_CONTROL:
        {
                // 用户空间的数据
                int *buf = Irp->AssociatedIrp.SystemBuffer;
                DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, "SystemBuffer0=%d\n", buf[0]);
                DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, "SystemBuffer1=%d\n", buf[1]);
                DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, "SystemBuffer2=%d\n", buf[2]);

                // 数据写入用户空间
                char aa[] = "weichen777微尘读";
                RtlCopyMemory(Irp->AssociatedIrp.SystemBuffer, aa, sizeof(aa));

                // 请求完成
                Irp->IoStatus.Status = STATUS_SUCCESS;
                Irp->IoStatus.Information = sizeof(aa);
                IoCompleteRequest(Irp, IO_NO_INCREMENT);
                return STATUS_SUCCESS;
                break;
        }
        
            default:
            {
                        break;
            }
        
        }

        Irp->IoStatus.Status = STATUS_SUCCESS;
        Irp->IoStatus.Information = 4; // outbuf字节数
        IoCompleteRequest(Irp, IO_NO_INCREMENT);
        return STATUS_SUCCESS;

} ^wuBNwCqq

从用户空间到内核空间读写基本框架代码 ^r6lFti7W

#define 三环符号 L"\\??\\myhelloWord"

void CHelloWord3Dlg::OnBnClickedButton1()
{
         nDeviveHandle=CreateFile(三环符号, 
            GENERIC_READ| GENERIC_WRITE, 
            FILE_SHARE_READ, NULL, 
            OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL,NULL);
}

void CHelloWord3Dlg::OnBnClickedButton2()
{
        CloseHandle(nDeviveHandle);
}

void CHelloWord3Dlg::OnBnClickedButton3()
{
        char* buf = "weichen666微尘";
        DWORD len = 0;
        BOOL ret=WriteFile(nDeviveHandle, buf,sizeof(buf),&len, NULL);
}

void CHelloWord3Dlg::OnBnClickedButton4()
{
        char buf[256] = {0};
        DWORD len = 0;
        BOOL ret = ReadFile(nDeviveHandle, buf, sizeof(buf), &len, NULL);
}

void CHelloWord3Dlg::OnBnClickedButton5()
{
        char buf[256] = {"weichen567" };
        MyStruct Mybuf = {1,2,3};
        DWORD len = 0;
        char Outbuf[256];
        BOOL ret = DeviceIoControl(nDeviveHandle, 读写text, 
                &Mybuf, sizeof(Mybuf), Outbuf,sizeof(Outbuf),&len, NULL);
} ^R9UlzkBS

其他进程1 ^lrL7u0C7

其他进程2 ^kYzTEvvQ

某游戏进程 ^Ushu8tJb

（1）驱动附加游戏进程
（2）内存拷贝到驱动内存 ^XsREuoix

驱动内存 ^pBGVYzJe

原理：驱动附加+内存拷贝 ^ZIIPW9om

驱动实现进程和线程监控（保护进程、过图标）
22~26课 ^YJ5rRo0U

全局句柄表和私有句柄表
28~33 ^PqbtcwAp

自动编译+驱动签名+加壳
34~36课 ^i6U7Catt

驱动注入（过代码段写保护）
40 ~ 42课 ^RUDrzgYh

32位系统上还能通过hook方式来监控系统线程和进程，
但到了64位平台上，就不能了，因为特别容易PG，即内核保护级蓝屏。

ObRegisterCallbacks()
ObUnRegisterCallbacks()

ObRegisterCallbacks 给你提供了回调的函数空壳，你需要在壳里写你自己的功能代码。



验证签名的结构体: _LDR_DATA_TABLE_ENTRY
下面是我们用 windbg 查看的目标版本Windows系统的Flags偏移，我们甚至不关心完整结构体什么样，
我们只关心我们要修改的 Flags 在结构体内部的偏移，拿到偏移就方便修改。

0: kd> dt _LDR_DATA_TABLE_ENTRY
ntdll!_LDR_DATA_TABLE_ENTRY
   +0x000 InLoadOrderLinks : _LIST_ENTRY
   +0x010 InMemoryOrderLinks : _LIST_ENTRY
   +0x020 InInitializationOrderLinks : _LIST_ENTRY
   +0x030 DllBase          : Ptr64 Void
   +0x038 EntryPoint       : Ptr64 Void
   +0x040 SizeOfImage      : Uint4B
   +0x048 FullDllName      : _UNICODE_STRING
   +0x058 BaseDllName      : _UNICODE_STRING
   +0x068 FlagGroup        : [4] UChar
   +0x068 Flags            : Uint4B
 ^q4zqFDfo

Windows不同版本里, _LDR_DATA_TABLE_ENTRY 内部成员偏移不一样, 
需要根据你目标机的系统版本来确定结构体定义,
下面是专门查询获取各个版本 Windows 内部结构体定义的网站: 
https://www.vergiliusproject.com/ ^xX4i9PIr

过图标破图标原理分析 ^g9PM8yk5

其中 OriginalDesiredAccess 管理着最初始的权限:
OperationInformation->Parameters->CreateHandleInformation.OriginalDesiredAccess;
OperationInformation->Parameters->DuplicateHandleInformation.OriginalDesiredAccess;

通过字段可以精确控制权限: PROCESS_TERMINATE, PROCESS_ALL_ACCESS, etc;


防守方有个类似定时器，会定时给你降权处理。后续会通过句柄表相关的知识来解决这个问题。 ^gLzroKSM

1、句柄本质来讲，就是一个索引号；
2、【全局句柄表】只有进程和线程有ID，内核其他对象都只有名字；
3、【私有句柄表】OpenProcess等函数通过PID拿到进程对象， ^qIWtEvA1

// MFCApplication1.exe —— PID=2648

0: kd> X nt!Ps*Cid*
fffff800`cb43e2dc nt!PsLookupProcessThreadByCid (PsLookupProcessThreadByCid)
fffff800`cb4d0670 nt!PspReferenceCidTableEntry (PspReferenceCidTableEntry)
fffff800`cb3ab340 nt!PspCidTable = <no type information>
fffff800`cb4bdfd4 nt!PspClearProcessThreadCidRefs (PspClearProcessThreadCidRefs)


0: kd> dq nt!PspCidTable
fffff801`789ac340  ffffdf0f`89c19040 fffff801`789ac348
fffff801`789ac350  fffff801`789ac348 ffffcf0e`61eb7570
fffff801`789ac360  00000000`00000000 00001000`00010000
fffff801`789ac370  00009a03`00000000 fffff801`78e24000
fffff801`789ac380  fffff801`78e99000 00000000`00000002
fffff801`789ac390  00000000`00000000 00000000`00000000
fffff801`789ac3a0  00000000`00000000 ffffcf0e`61fa93d0
fffff801`789ac3b0  00000000`0002625a fffff801`789ac838


0: kd> dt _HANDLE_TABLE ffffdf0f`89c19040
ntdll!_HANDLE_TABLE
   +0x000 NextHandleNeedingPool : 0x2800
   +0x004 ExtraInfoPages   : 0n0
   +0x008 TableCode        : 0xffffdf0f`9302e001
   +0x010 QuotaProcess     : (null) 
   +0x018 HandleTableList  : _LIST_ENTRY [ 0xffffdf0f`89c19058 - 0xffffdf0f`89c19058 ]
   +0x028 UniqueProcessId  : 0
   +0x02c Flags            : 1
   +0x02c StrictFIFO       : 0y1
   +0x02c EnableHandleExceptions : 0y0
   +0x02c Rundown          : 0y0
   +0x02c Duplicated       : 0y0
   +0x02c RaiseUMExceptionOnInvalidHandleClose : 0y0
   +0x030 HandleContentionEvent : _EX_PUSH_LOCK
   +0x038 HandleTableLock  : _EX_PUSH_LOCK
   +0x040 FreeLists        : [1] _HANDLE_TABLE_FREE_LIST
   +0x040 ActualEntry      : [32]  ""
   +0x060 DebugInfo        : (null) 



0: kd> dq 0xffffdf0f`9302e000
ffffdf0f`9302e000  ffffdf0f`89c1a000 ffffdf0f`9302f000
ffffdf0f`9302e010  ffffdf0f`9340b000 ffffdf0f`93e80000
ffffdf0f`9302e020  ffffdf0f`958ce000 ffffdf0f`95dcb000
ffffdf0f`9302e030  ffffdf0f`96e6b000 ffffdf0f`98899000
ffffdf0f`9302e040  ffffdf0f`98b52000 ffffdf0f`963ac000
ffffdf0f`9302e050  00000000`00000000 00000000`00000000
ffffdf0f`9302e060  00000000`00000000 00000000`00000000
ffffdf0f`9302e070  00000000`00000000 00000000`00000000


0: kd> dq ffffdf0f`963ac000+4*14c
ffffdf0f`963ac530  cf0e627c`b800f321 00000000`00000000
ffffdf0f`963ac540  00000000`00000000 ffffdf0f`98899fa0
ffffdf0f`963ac550  00000000`00000000 ffffdf0f`963ac2e0
ffffdf0f`963ac560  cf0e6240`3080f495 00000000`00000000
ffffdf0f`963ac570  00000000`00000000 ffffdf0f`9302f110
ffffdf0f`963ac580  00000000`00000000 ffffdf0f`988998a0
ffffdf0f`963ac590  00000000`00000000 ffffdf0f`963ac750
ffffdf0f`963ac5a0  00000000`00000000 ffffdf0f`963ac340


cf0e627c`b800f321
1100111100001110011000100111110010111000000000001111001100100001
1100 1111 0000 1110 0110 0010 0111 1100 1011 1000 0000 0000 1111 001100100001
1100 1111 0000 1110 0110 0010 0111 1100 1011 1000 0000    0000 1111 001100100001
1100 1111 0000 1110 0110 0010 0111 1100 1011 1000 0000
0000 0000 0000 0000 0000 1100 1111 0000 1110 0110 0010 0111 1100 1011 1000 0000 
0000 0000 0000 0000 1100 1111 0000 1110 0110 0010 0111 1100 1011 1000 0000 0000 
1111 1111 1111 1111 1100 1111 0000 1110 0110 0010 0111 1100 1011 1000 0000 0000 
ffffcf0e`627cb800


0: kd> dt _EPROCESS ffffcf0e`627cb800
ntdll!_EPROCESS
   +0x000 Pcb              : _KPROCESS
   +0x2d8 ProcessLock      : _EX_PUSH_LOCK
   +0x2e0 RundownProtect   : _EX_RUNDOWN_REF
   +0x2e8 UniqueProcessId  : 0x00000000`0000254c Void
   ...
   +0x418 ObjectTable      : 0xffffdf0f`9d4b58c0 _HANDLE_TABLE
   +0x420 DebugPort        : (null) 
   ...
   +0x450 ImageFileName    : [15]  "MFCApplication" ^sUZibHTD

0表示只有1级,1表示有2级页表
最后一级每个表项占16字节(_HANDLE_TABLE_ENTRY) ^MY58eBoI

---> 0x0c + 4 = 0x10 = 16字节 ^m1DC0A02

0: kd> dt _HANDLE_TABLE_ENTRY
ntdll!_HANDLE_TABLE_ENTRY
   +0x000 VolatileLowValue : Int8B
   +0x000 LowValue         : Int8B
   +0x000 InfoTable        : Ptr64 _HANDLE_TABLE_ENTRY_INFO
   +0x008 HighValue        : Int8B
   +0x008 NextFreeHandleEntry : Ptr64 _HANDLE_TABLE_ENTRY
   +0x008 LeafHandleValue  : _EXHANDLE
   +0x000 RefCountField    : Int8B
   +0x000 Unlocked         : Pos 0, 1 Bit
   +0x000 RefCnt           : Pos 1, 16 Bits
   +0x000 Attributes       : Pos 17, 3 Bits
   +0x000 ObjectPointerBits : Pos 20, 44 Bits
   +0x008 GrantedAccessBits : Pos 0, 25 Bits
   +0x008 NoRightsUpgrade  : Pos 25, 1 Bit
   +0x008 Spare1           : Pos 26, 6 Bits
   +0x00c Spare2           : Uint4B ^Mc8TRmOQ

pid / 1024 = 9548 / 1024 = 9 (余332)
pid % 1024 = 9548 % 1024 = 332 = 0x14c ^rfxBcr6s

// TIM.exe —— PID=2648

0: kd> X nt!Ps*Cid*
fffff800`cb43e2dc nt!PsLookupProcessThreadByCid (PsLookupProcessThreadByCid)
fffff800`cb4d0670 nt!PspReferenceCidTableEntry (PspReferenceCidTableEntry)
fffff800`cb3ab340 nt!PspCidTable = <no type information>
fffff800`cb4bdfd4 nt!PspClearProcessThreadCidRefs (PspClearProcessThreadCidRefs)


0: kd> dq nt!PspCidTable
fffff801`789ac340  ffffdf0f`89c19040 fffff801`789ac348
fffff801`789ac350  fffff801`789ac348 ffffcf0e`61eb7570
fffff801`789ac360  00000000`00000000 00001000`00010000
fffff801`789ac370  00009a03`00000000 fffff801`78e24000
fffff801`789ac380  fffff801`78e99000 00000000`00000002
fffff801`789ac390  00000000`00000000 00000000`00000000
fffff801`789ac3a0  00000000`00000000 ffffcf0e`61fa93d0
fffff801`789ac3b0  00000000`0002625a fffff801`789ac838


0: kd> dt _HANDLE_TABLE ffffdf0f`89c19040
ntdll!_HANDLE_TABLE
   +0x000 NextHandleNeedingPool : 0x2800
   +0x004 ExtraInfoPages   : 0n0
   +0x008 TableCode        : 0xffffdf0f`9302e001
   +0x010 QuotaProcess     : (null) 
   +0x018 HandleTableList  : _LIST_ENTRY [ 0xffffdf0f`89c19058 - 0xffffdf0f`89c19058 ]
   +0x028 UniqueProcessId  : 0
   +0x02c Flags            : 1
   +0x02c StrictFIFO       : 0y1
   +0x02c EnableHandleExceptions : 0y0
   +0x02c Rundown          : 0y0
   +0x02c Duplicated       : 0y0
   +0x02c RaiseUMExceptionOnInvalidHandleClose : 0y0
   +0x030 HandleContentionEvent : _EX_PUSH_LOCK
   +0x038 HandleTableLock  : _EX_PUSH_LOCK
   +0x040 FreeLists        : [1] _HANDLE_TABLE_FREE_LIST
   +0x040 ActualEntry      : [32]  ""
   +0x060 DebugInfo        : (null) 



0: kd> dq 0xffffdf0f`9302e000
ffffdf0f`9302e000  ffffdf0f`89c1a000 ffffdf0f`9302f000
ffffdf0f`9302e010  ffffdf0f`9340b000 ffffdf0f`93e80000
ffffdf0f`9302e020  ffffdf0f`958ce000 ffffdf0f`95dcb000
ffffdf0f`9302e030  ffffdf0f`96e6b000 ffffdf0f`98899000
ffffdf0f`9302e040  ffffdf0f`98b52000 ffffdf0f`963ac000
ffffdf0f`9302e050  00000000`00000000 00000000`00000000
ffffdf0f`9302e060  00000000`00000000 00000000`00000000
ffffdf0f`9302e070  00000000`00000000 00000000`00000000


0: kd> dq ffffdf0f`9340b000+4*258
ffffdf0f`9340b960  cf0e655e`e800ed23 00000000`00000000
ffffdf0f`9340b970  cf0e6543`8080ed3d 00000000`00000000
ffffdf0f`9340b980  cf0e6243`70800001 00000000`00000000
ffffdf0f`9340b990  cf0e63c9`8040fffd 00000000`00000000
ffffdf0f`9340b9a0  cf0e63a3`e5c0fffd 00000000`00000000
ffffdf0f`9340b9b0  cf0e647f`f3400001 00000000`00000000
ffffdf0f`9340b9c0  00000000`00000000 ffffdf0f`98b52db0
ffffdf0f`9340b9d0  cf0e63a3`7580ffef 00000000`00000000


cf0e655e`e800ed23
1100111100001110011001010101111011101000000000001110110100100011
1100 1111 0000 1110 0110 0101 0101 1110 1110 1000 0000 00001110110100100011
1100 1111 0000 1110 0110 0101 0101 1110 1110 1000 0000    00001110110100100011
1100 1111 0000 1110 0110 0101 0101 1110 1110 1000 0000
0000 0000 0000 0000 0000 1100 1111 0000 1110 0110 0101 0101 1110 1110 1000 0000
0000 0000 0000 0000 1100 1111 0000 1110 0110 0101 0101 1110 1110 1000 0000 0000
1111 1111 1111 1111 1100 1111 0000 1110 0110 0101 0101 1110 1110 1000 0000 0000
ffffcf0e`655ee800


0: kd> dt _EPROCESS ffffcf0e`655ee800
ntdll!_EPROCESS
   +0x000 Pcb              : _KPROCESS
   +0x2d8 ProcessLock      : _EX_PUSH_LOCK
   +0x2e0 RundownProtect   : _EX_RUNDOWN_REF
   +0x2e8 UniqueProcessId  : 0x00000000`00000a58 Void
   ...
   +0x418 ObjectTable      : 0xffffdf0f`97f5c740 _HANDLE_TABLE
   +0x420 DebugPort        : (null) 
   ...
   +0x450 ImageFileName    : [15]  "TIM.exe"
 ^SdwzO9lQ

pid / 1024 = 2648 / 1024 = 2 (余600)
pid % 1024 = 2648 % 1024 = 600 = 0x258 ^ohRUtoUD

验证全局句柄表（从全局句柄表中找到指定PID对应的进程 _EPROCESS） ^tzNg3HWb

私有句柄表 ^pnNfGpVZ

当我们用CE附加游戏进程时,就相当于OpenProcess游戏进程句柄;

打开 YDark, 右键查看CE 的进程句柄, 找到里面的 Process 类型的句柄, 就有CE附加的游戏进程, 如下图: ^hcv2hXkY

这就是私有句柄表 ^2QmEWDhI

windbg 附加到指定进程:
!process  0  0  ce.exe ^tBLSzCqF

0: kd> !process 0 0 cheatengine-x86_64-SSE4-AVX2.exe
PROCESS ffffcf0e65268440
    SessionId: 1  Cid: 02fc    Peb: 003e6000  ParentCid: 1ec8
    DirBase: 806fb000  ObjectTable: ffffdf0f9e759800  HandleCount: <Data Not Accessible>
    Image: cheatengine-x86_64-SSE4-AVX2.exe


0: kd> dt _EPROCESS ffffcf0e65268440
ntdll!_EPROCESS
   ...
   +0x2e8 UniqueProcessId  : 0x00000000`000002fc Void
   ...
   +0x418 ObjectTable      : 0xffffdf0f`9e759800 _HANDLE_TABLE
   +0x420 DebugPort        : (null) 


0: kd> dt _HANDLE_TABLE 0xffffdf0f`9e759800
ntdll!_HANDLE_TABLE
   +0x000 NextHandleNeedingPool : 0x400
   +0x004 ExtraInfoPages   : 0n0
   +0x008 TableCode        : 0xffffdf0f`961ae000
   +0x010 QuotaProcess     : 0xffffcf0e`65268440 _EPROCESS
   +0x018 HandleTableList  : _LIST_ENTRY [ 0xffffdf0f`98cf59d8 - 0xffffdf0f`9e3dc658 ]
   +0x028 UniqueProcessId  : 0x2fc
   +0x02c Flags            : 0
   +0x02c StrictFIFO       : 0y0
   +0x02c EnableHandleExceptions : 0y0
   +0x02c Rundown          : 0y0
   +0x02c Duplicated       : 0y0
   +0x02c RaiseUMExceptionOnInvalidHandleClose : 0y0
   +0x030 HandleContentionEvent : _EX_PUSH_LOCK
   +0x038 HandleTableLock  : _EX_PUSH_LOCK
   +0x040 FreeLists        : [1] _HANDLE_TABLE_FREE_LIST
   +0x040 ActualEntry      : [32]  ""
   +0x060 DebugInfo        : (null) 


0: kd> dq 0xffffdf0f`961ae000
ffffdf0f`961ae000  00000000`00000000 00000000`00000000
ffffdf0f`961ae010  cf0e646b`5480ffed 00000000`001f0003
ffffdf0f`961ae020  cf0e6471`0390ffef 00000000`00000001
ffffdf0f`961ae030  cf0e6688`dc50ffe5 00000000`001f0003
ffffdf0f`961ae040  cf0e64fa`68e0ffd7 00000000`000f00ff
ffffdf0f`961ae050  cf0e656a`56e0ffef 00000000`00100002
ffffdf0f`961ae060  cf0e660f`9cb0ffef 00000000`00000001
ffffdf0f`961ae070  cf0e6245`0860ffe3 00000000`00100002
0: kd> dq 0xffffdf0f`961ae000+4*330
ffffdf0f`961aecc0  cf0e647d`e05000c5 00000000`00112345
ffffdf0f`961aecd0  cf0e64e3`1050fff7 00000000`001fffff
ffffdf0f`961aece0  cf0e6521`30c0e76b 00000000`001f0003
ffffdf0f`961aecf0  00000000`00000000 ffffdf0f`961aef30
ffffdf0f`961aed00  cf0e6406`1050fff7 00000000`001fffff
ffffdf0f`961aed10  cf0e64a7`9740fff1 00000000`00100003
ffffdf0f`961aed20  cf0e6551`1d60fff1 00000000`00100003
ffffdf0f`961aed30  cf0e649f`f030fff1 00000000`00100003
0: kd> dt _HANDLE_TABLE_ENTRY ffffdf0f`961aecc0
ntdll!_HANDLE_TABLE_ENTRY
   +0x000 VolatileLowValue : 0n-3526770966387490619
   +0x000 LowValue         : 0n-3526770966387490619
   +0x000 InfoTable        : 0xcf0e647d`e05000c5 _HANDLE_TABLE_ENTRY_INFO
   +0x008 HighValue        : 0n1123141
   +0x008 NextFreeHandleEntry : 0x00000000`00112345 _HANDLE_TABLE_ENTRY
   +0x008 LeafHandleValue  : _EXHANDLE
   +0x000 RefCountField    : 0n-3526770966387490619
   +0x000 Unlocked         : 0y1
   +0x000 RefCnt           : 0y0000000001100010 (0x62)
   +0x000 Attributes       : 0y000
   +0x000 ObjectPointerBits : 0y11001111000011100110010001111101111000000101 (0xcf0e647de05)
   +0x008 GrantedAccessBits : 0y0000100010010001101000101 (0x112345)
   +0x008 NoRightsUpgrade  : 0y0
   +0x008 Spare1           : 0y000000 (0)
   +0x00c Spare2           : 0



cf0e647d`e05000c5
1100 1111 0000 1110 0110 0100 0111 1101 1110 0000 0101 0000 0000 0000 1100 0101
1100 1111 0000 1110 0110 0100 0111 1101 1110 0000 0101
0000 0000 0000 0000 0000 1100 1111 0000 1110 0110 0100 0111 1101 1110 0000 0101
0000 0000 0000 0000 1100 1111 0000 1110 0110 0100 0111 1101 1110 0000 0101 0000
1111 1111 1111 1111 1100 1111 0000 1110 0110 0100 0111 1101 1110 0000 0101 0000
ffffcf0e`647de050



0: kd> dt _EPROCESS ffffcf0e`647de050+30
ntdll!_EPROCESS
   +0x000 Pcb              : _KPROCESS
   +0x2d8 ProcessLock      : _EX_PUSH_LOCK
   +0x2e0 RundownProtect   : _EX_RUNDOWN_REF
   +0x2e8 UniqueProcessId  : 0x00000000`00000da8 Void
   ...
   +0x448 ImageFilePointer : 0xffffcf0e`654fe840 _FILE_OBJECT
   +0x450 ImageFileName    : [15]  "MFCApplication" ^k6ATM3sB

0x330 (816) ^1pJdJjgq

IDA分析遍历句柄表函数 ^TreLFAUS

未导出函数:
ExpLookupHandleTableEntry

导出函数:
ObReferenceObjectByHandle
ObReferenceObjectByHandleWithTag ^6cPz8puR

权限 ^4WinVrFv

0: kd> bu ObReferenceObjectByHandle
0: kd> bl
     0 e Disable Clear  fffff801`78ad7f30     0001 (0001) nt!ObReferenceObjectByHandle

0: kd> g
Breakpoint 0 hit
nt!ObReferenceObjectByHandle:
fffff801`78ad7f30 4883ec48        sub     rsp,48h



nt!ObpReferenceObjectByHandleWithTag+0xa8:
fffff801`78ad8018 4d8bbd18040000  mov     r15,qword ptr [r13+418h]
3: kd> t
nt!ObpReferenceObjectByHandleWithTag+0xaf:
fffff801`78ad801f 4d85ff          test    r15,r15
3: kd> t
nt!ObpReferenceObjectByHandleWithTag+0xb2:
fffff801`78ad8022 0f84f3040000    je      nt!ObpReferenceObjectByHandleWithTag+0x5ab (fffff801`78ad851b)
3: kd> t
nt!ObpReferenceObjectByHandleWithTag+0xb8:
fffff801`78ad8028 4c3b3d11ede2ff  cmp     r15,qword ptr [nt!ObpKernelHandleTable (fffff801`78906d40)]
3: kd> t
nt!ObpReferenceObjectByHandleWithTag+0xbf:
fffff801`78ad802f 0f84b0040000    je      nt!ObpReferenceObjectByHandleWithTag+0x575 (fffff801`78ad84e5)
3: kd> t
nt!ObpReferenceObjectByHandleWithTag+0xc5:
fffff801`78ad8035 41f7c4fc030000  test    r12d,3FCh
3: kd> t
nt!ObpReferenceObjectByHandleWithTag+0xcc:
fffff801`78ad803c 0f849a040000    je      nt!ObpReferenceObjectByHandleWithTag+0x56c (fffff801`78ad84dc)
3: kd> t
nt!ObpReferenceObjectByHandleWithTag+0xd2:
fffff801`78ad8042 498bd4          mov     rdx,r12
3: kd> t
nt!ObpReferenceObjectByHandleWithTag+0xd5:
fffff801`78ad8045 498bcf          mov     rcx,r15
3: kd> t
nt!ObpReferenceObjectByHandleWithTag+0xd8:
fffff801`78ad8048 e833050000      call    nt!ExpLookupHandleTableEntry (fffff801`78ad8580)
3: kd> t
nt!ExpLookupHandleTableEntry:
fffff801`78ad8580 8b01            mov     eax,dword ptr [rcx]




3: kd> dt _EPROCESS
ntdll!_EPROCESS
   ...
   +0x418 ObjectTable      : Ptr64 _HANDLE_TABLE



0: kd> bu ExpLookupHandleTableEntry
0: kd> g
Breakpoint 0 hit
nt!ExpLookupHandleTableEntry:
fffff801`78ad8580 8b01            mov     eax,dword ptr [rcx]
3: kd> r
rax=00000000944d0e01 rbx=ffffcf0e61ea82d0 rcx=ffffdf0f97f5c740
rdx=00000000000019b8 rsi=ffffcf0e65706080 rdi=0000000000000003
rip=fffff80178ad8580 rsp=ffff80816ff017e8 rbp=ffff80816ff01b80
 r8=0000000000000000  r9=0000000000000001 r10=fffff80178a914e0
r11=ffff80816ff01a18 r12=00000000000019b8 r13=ffffcf0e655ee800
r14=0000000000000001 r15=ffffdf0f97f5c740
iopl=0         nv up ei pl nz na po nc
cs=0010  ss=0018  ds=002b  es=002b  fs=0053  gs=002b             efl=00000206
nt!ExpLookupHandleTableEntry:
fffff801`78ad8580 8b01            mov     eax,dword ptr [rcx] ds:002b:ffffdf0f`97f5c740=00002000



3: kd> dt _HANDLE_TABLE ffffdf0f97f5c740
ntdll!_HANDLE_TABLE
   +0x000 NextHandleNeedingPool : 0x2000
   +0x004 ExtraInfoPages   : 0n0
   +0x008 TableCode        : 0xffffdf0f`98490001
   +0x010 QuotaProcess     : 0xffffcf0e`655ee800 _EPROCESS
   +0x018 HandleTableList  : _LIST_ENTRY [ 0xffffdf0f`98183058 - 0xffffdf0f`97812a58 ]
   +0x028 UniqueProcessId  : 0xa58
   +0x02c Flags            : 0
   +0x02c StrictFIFO       : 0y0
   +0x02c EnableHandleExceptions : 0y0
   +0x02c Rundown          : 0y0
   +0x02c Duplicated       : 0y0
   +0x02c RaiseUMExceptionOnInvalidHandleClose : 0y0
   +0x030 HandleContentionEvent : _EX_PUSH_LOCK
   +0x038 HandleTableLock  : _EX_PUSH_LOCK
   +0x040 FreeLists        : [1] _HANDLE_TABLE_FREE_LIST
   +0x040 ActualEntry      : [32]  ""
   +0x060 DebugInfo        : (null) 
 ^Y65KJYGV

下断调试 ^omDC7OVG

单步至此 ^nKcrkh8j

ObpKernelHandleTable ^4g2lfBoR

至此得知:
rcx = ObpKernelHandleTable
rdx = handle ^I5gkIrVz

#include "pch.h"
#include "windows.h"
#include "Driverload.h"
#include "winsvc.h"

// DriverLoad("HelloWord","HelloWord.sys");
void DriverLoad(char* DriverName,char* NzPath)
{
        char nbuf[256] = {0};
        GetFullPathNameA(NzPath,256,nbuf,NULL);
        char buf[1024] = {0};
        SC_HANDLE hServiceDDK = NULL;
        SC_HANDLE hServiceMgr =OpenSCManagerA(NULL,NULL, SC_MANAGER_ALL_ACCESS);
        if (hServiceMgr)
        {
                wsprintfA(buf, "OpenSCManagerA 打开OK");
                OutputDebugStringA(buf);
                 hServiceDDK = CreateServiceA(
                        hServiceMgr,
                        DriverName,
                        DriverName,
                        SERVICE_START,
                        SERVICE_KERNEL_DRIVER,
                        SERVICE_DEMAND_START,
                        SERVICE_ERROR_NORMAL,
                        nbuf,
                        NULL,
                        NULL,
                        NULL,
                        NULL,
                        NULL
                );
                if (hServiceDDK)
                {
                        wsprintfA(buf, "CreateServiceA 打开OK");
                        OutputDebugStringA(buf);
                }
                else if(GetLastError() == ERROR_SERVICE_EXISTS)
                {
                        //wsprintfA(buf, "CreateServiceA 打开失败cuowu=%d", GetLastError());
                        //OutputDebugStringA(buf);

                        hServiceDDK = OpenServiceA(hServiceMgr, DriverName, SERVICE_START);
                        if (hServiceDDK)
                        {
                                wsprintfA(buf, "OpenServiceA 打开OK");
                                OutputDebugStringA(buf);
                        }
                        else
                        {
                                wsprintfA(buf, "OpenServiceA 打开失败cuowu=%d", GetLastError());
                                OutputDebugStringA(buf);
                        }

                }

                if (StartServiceA(hServiceDDK, NULL, NULL))
                {
                        wsprintfA(buf, "StartServiceA OK");
                        OutputDebugStringA(buf);
                }
                else
                {
                        wsprintfA(buf, "StartServiceA 打开失败cuowu=%d", GetLastError());
                        OutputDebugStringA(buf);
                }

        }
        else
        {
                wsprintfA(buf,"OpenSCManagerA 打开失败cuowu=%d", GetLastError());
                OutputDebugStringA(buf);
        }

        if (hServiceDDK)
        {
                CloseServiceHandle(hServiceDDK);
        }
        if (hServiceMgr)
        {
                CloseServiceHandle(hServiceMgr);
        }

}


BOOL UnloadDriver(char * lpszDriverName)
{
        BOOL bRet = FALSE;
        SC_HANDLE hServiceMgr = NULL;//SCM管理器的句柄
        SC_HANDLE hServiceDDK = NULL;//NT驱动程序的服务句柄
        SERVICE_STATUS SvrSta;
        char buf[2048] = { 0 };
        hServiceMgr = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
        if (hServiceMgr == NULL)
        {
                //带开SCM管理器失败
                sprintf_s(buf, "weichen:OpenSCManager() Faild %d ! \n", GetLastError());
                OutputDebugStringA(buf);
                bRet = FALSE;
                goto BeforeLeave;
        }
        else
        {
                //带开SCM管理器失败成功
                sprintf_s(buf, "weichen:OpenSCManager() ok ! \n");
                OutputDebugStringA(buf);
        }
        //打开驱动所对应的服务
        hServiceDDK = OpenServiceA(hServiceMgr, lpszDriverName, SERVICE_ALL_ACCESS);

        if (hServiceDDK == NULL)
        {
                //打开驱动所对应的服务失败
                sprintf_s(buf, "weichen:OpenService() Faild %d ! \n", GetLastError());
                OutputDebugStringA(buf);
                bRet = FALSE;
                goto BeforeLeave;
        }
        else
        {
                sprintf_s(buf, "weichen:OpenService() ok ! \n");
                OutputDebugStringA(buf);
        }

        //停止驱动程序，如果停止失败，只有重新启动才能，再动态加载。  
        if (!ControlService(hServiceDDK, SERVICE_CONTROL_STOP, &SvrSta))
        {
                sprintf_s(buf, "weichen:ControlService() Faild %d !\n", GetLastError());
                OutputDebugStringA(buf);
        }
        else
        {
                //打开驱动所对应的失败
                sprintf_s(buf, "weichen:ControlService() ok !\n");
                OutputDebugStringA(buf);
        }
        //动态卸载驱动程序,删除服务  
        if (!DeleteService(hServiceDDK))
        {
                //卸载失败
                sprintf_s(buf, "weichen:DeleteSrevice() Faild %d !\n", GetLastError());
                OutputDebugStringA(buf);
        }
        else
        {
                //卸载成功
                sprintf_s(buf, "weichen:DelServer:deleteSrevice() ok !\n");
                OutputDebugStringA(buf);
        }
        bRet = TRUE;
BeforeLeave:
        //离开前关闭打开的句柄
        if (hServiceDDK)
        {
                CloseServiceHandle(hServiceDDK);
        }
        if (hServiceMgr)
        {
                CloseServiceHandle(hServiceMgr);
        }
        return bRet;
} ^neAfOy2t

驱动&服务加载/卸载代码 ^NjaOWmw9

VS自动编译工程 ^T7q8wj7i

（0）通过快捷方式找到对应的 .com 文件：
D:\SW\VS\2022\Community\Common7\IDE\devenv.exe  —— 可视化的
D:\SW\VS\2022\Community\Common7\IDE\devenv.com  —— 命令行

（1）新建VS工程 —— 选择Windows桌面应用程序
（2）删掉所有界面代码
（3）只写如下代码：

#include "framework.h"
#include "WindowsProject2.h"

int APIENTRY wWinMain(_In_ HINSTANCE hInstance,
                     _In_opt_ HINSTANCE hPrevInstance,
                     _In_ LPWSTR    lpCmdLine,
                     _In_ int       nCmdShow)
{
        SetCurrentDirectoryA("C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\Community\\Common7\\IDE");
        while (true)
        {
                WinExec("Devenv.com C:\\Users\\Administrator\\source\\repos\\HelloWord\\HelloWord.sln /rebuild", SW_HIDE);
                Sleep(2*1000*60);
        }
        
        
    return 0;
}

/*
下面是cmd命令:
"C:\Program Files (x86)\Microsoft Visual Studio 14.0\Common7\IDE\devenv.com" "C:\Users\seafly\Desktop\源码\第33课代码\HelloWord\HelloWord.sln" /rebuild
**/ ^5tK275QT

VMP加壳 ^XHGFjJUP

helloWorld.sys
helloWorld.sys.vmp
（手动加壳后，会生成该文件，其实就是个xml文件, 自动化加壳就很需要这个文件）
.vmp 内容如下:

<?xml version="1.0" encoding="UTF-8" ?>
<Document Version="2">
    <Protection InputFileName="HelloWord.sys" Options="328648" VMCodeSectionName=".???">
        <Messages />
        <Folders />
        <Procedures>
            <Procedure MapAddress="Myunload" Options="0" CompilationType="1" />
            <Procedure MapAddress="MyCrteate" Options="0" CompilationType="1" />
            <Procedure MapAddress="DriverEntry" Options="0" CompilationType="1" />
        </Procedures>
        <Objects />
    </Protection>
    <DLLBox>
        <Folders />
    </DLLBox>
    <Script />
    <LicenseManager />
</Document>


IDA一般驱动和分析内核用得比较多，游戏找数据上用得不多； ^7AoDT4xw

下面是批处理（vmp.bat）：自动加壳、自动签名 ^6zdT1NRw

@echo off

set "projectpath=%cd%"
cd ../

set "preProjectpath=%cd%"
cd /d %projectpath%

set "vmpath=%preProjectpath%/x64/Debug/HelloWorld.sys.vmp"
set "oldDate=%date:~0,10%"
set "path=%path%;D:\sw\VMProtect_Ultimate_v3.6.0_Build_1406_Retail_Licensed"
set "signFullPath=%preProjectpath%/x64/Debug/HelloWorld.vmp.sys"

VMProtect_Con.exe  %vmpath%
date 2013/8/15
CSignTool.exe  sign /r landong111 /f %signFullPath% /ac
date %oldDate%
copy "%signFullPath%" "D:\HelloWorld.sys" ^VHRtogAE

#include"ntifs.h"

// 关闭CR0控制寄存器内的WP位
KIRQL WriteProtectOff()
{
        KIRQL OldIrql = 0;
        ULONG_PTR cr0 = 0;
        // 提升IRQL等级到Dispatch Level
        OldIrql = KeRaiseIrqlToDpcLevel()
                ;
        // 读取读cr0控制寄存器内容
        cr0 = __readcr0();
        // 关闭WP位
#ifdef _X86_
        cr0 &= 0xfffeffff;
#else 
        cr0 &= 0xfffffffffffeffff;
#endif 
        // 关闭中断
        _disable();
        // 写回cr0寄存器
        __writecr0(cr0);
        return(OldIrql);
}

// 打开CR0控制寄存器内的WP位
VOID WriteProtectOn(KIRQL irql)
{
        KIRQL OldIrql = 0;
        ULONG_PTR cr0 = 0;
        // 读取读cr0控制寄存器内容
        cr0 = __readcr0();
        // 打开WP位
#ifdef _X86_
        cr0 |= 0x00010000;
#else 
        cr0 |= 0x0000000000010000;
#endif 
        // 写回cr0寄存器
        __writecr0(cr0);
        // 打开中断
        _enable();
        // 恢复IRQL等级
        KeLowerIrql(irql);
} ^eJN8qhqp

#include"ntifs.h"

// 过保护读内存
void ReadProcessByAtt(IRP* Irp)
{
        UINT64 buf[3] = { 0 };
        //__debugbreak();

        RtlCopyMemory(buf, Irp->AssociatedIrp.SystemBuffer, sizeof(buf));
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer0=%llx\n", buf[0]);
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer1=%llx\n", buf[1]);
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer2=%llx\n", buf[2]);
        PEPROCESS pep = NULL;
        PsLookupProcessByProcessId(buf[0], &pep);
        PVOID kbuf = ExAllocatePool(NonPagedPool, 8);
        KAPC_STATE apc;
        KeStackAttachProcess(pep, &apc);
        // 把游戏内存数据拷贝到驱动内存(8字节)
        RtlCopyMemory(kbuf, buf[1], 8);
        KeUnstackDetachProcess(&apc);

        RtlCopyMemory(Irp->AssociatedIrp.SystemBuffer, kbuf, 8);
        ExFreePool(kbuf);
        ObDereferenceObject(pep); // 游戏进程引用减1
}

// MDL驱动读写
void ReadProcessByMDL(IRP* Irp)
{
        UINT64 buf[3] = { 0 };
        //__debugbreak();

        RtlCopyMemory(buf, Irp->AssociatedIrp.SystemBuffer, sizeof(buf));
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer0=%llx\n", buf[0]);
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer1=%llx\n", buf[1]);
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer2=%llx\n", buf[2]);

        // 拿到游戏进程实例
        PEPROCESS pep = NULL;
        PsLookupProcessByProcessId(buf[0], &pep);

        // 根据虚拟地址buf申请mdl
        PMDL  g_mdl=IoAllocateMdl(buf,8, FALSE, FALSE, NULL);
        MmBuildMdlForNonPagedPool(g_mdl);

        // 映射mdl到另一个虚拟地址address
        PVOID address=MmMapLockedPages(g_mdl, KernelMode);
        //PVOID p = ExAllocatePool(NonPagedPool, 8);
        KAPC_STATE apc;
        KeStackAttachProcess(pep, &apc);
        RtlCopyMemory(address, buf[1], 8);// 把游戏地址的数据拷贝到mdl虚拟地址
        KeUnstackDetachProcess(&apc);

        // 把mdl虚拟地址的数据通过拷贝反馈给irp请求
        RtlCopyMemory(Irp->AssociatedIrp.SystemBuffer, address, 8);
        //ExFreePool(p);
        MmUnmapLockedPages(address, g_mdl);
        IoFreeMdl(g_mdl);
        ObDereferenceObject(pep);
}

// MDL驱动写
void ReadProcessByMDWrite(IRP* Irp)
{
        UINT64 buf[3] = { 0 };
        //__debugbreak();

        RtlCopyMemory(buf, Irp->AssociatedIrp.SystemBuffer, sizeof(buf));
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer0=%llx\n", buf[0]);
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer1=%llx\n", buf[1]);
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer2=%llx\n", buf[2]);
        PEPROCESS pep = NULL;
        PsLookupProcessByProcessId(buf[0], &pep);

        // 把用户空间传进来的地址申请mdl
        PMDL  g_mdl = IoAllocateMdl(buf[2], 8, FALSE, FALSE, NULL);
        MmBuildMdlForNonPagedPool(g_mdl);

        // 把这个用户空间地址映射成 address
        PVOID address = MmMapLockedPages(g_mdl, KernelMode);
        //PVOID p = ExAllocatePool(NonPagedPool, 8);
        KAPC_STATE apc;
        KeStackAttachProcess(pep, &apc);
        // 把 address 数据拷贝到游戏内存里
        RtlCopyMemory(buf[1], address, 8);
        KeUnstackDetachProcess(&apc);

        RtlCopyMemory(Irp->AssociatedIrp.SystemBuffer, address, 8);
        //ExFreePool(p);
        MmUnmapLockedPages(address, g_mdl);
        IoFreeMdl(g_mdl);
        ObDereferenceObject(pep);
}

// 只读写保护
void ReadProcessByOnlyRead(IRP* Irp)
{
        UINT64 buf[3] = { 0 };
        //__debugbreak();

        RtlCopyMemory(buf, Irp->AssociatedIrp.SystemBuffer, sizeof(buf));
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer0=%llx\n", buf[0]);
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer1=%llx\n", buf[1]);
        DbgPrintEx(IRP_MJ_DEVICE_CONTROL, 0, " Irp->AssociatedIrp.SystemBuffer2=%llx\n", buf[2]);
        PEPROCESS pep = NULL;
        PsLookupProcessByProcessId(buf[0], &pep);
        KAPC_STATE apc;
        KeStackAttachProcess(pep, &apc);
        PMDL  g_mdl = IoAllocateMdl(buf[1], 8, FALSE, FALSE, NULL);
        MmBuildMdlForNonPagedPool(g_mdl);
        PVOID address = MmMapLockedPages(g_mdl, KernelMode);
        //PVOID p = ExAllocatePool(NonPagedPool, 8);
        KeUnstackDetachProcess(&apc);
        KIRQL irql=WriteProtectOff();
        RtlCopyMemory(address, buf[2], 8);
        WriteProtectOn( irql);


        RtlCopyMemory(Irp->AssociatedIrp.SystemBuffer, address, 8);
        //ExFreePool(p);
        MmUnmapLockedPages(address, g_mdl);
        IoFreeMdl(g_mdl);
        ObDereferenceObject(pep);
} ^ZhjqncLo

LONGLONG game_addr;
StrToInt64ExW(address.GetString(), STIF_SUPPORT_HEX,&game_addr);
LONGLONG game_pid;
StrToInt64ExW(pid.GetString(), STIF_SUPPORT_HEX, &game_pid);
UINT64 Mybuf[3] = { game_pid,game_addr ,8 };
DWORD len = 0;
UINT64 Outbuf=NULL;
BOOL ret = DeviceIoControl(nDeviveHandle, 过保护读内存, 
    &Mybuf, sizeof(Mybuf), &Outbuf, sizeof(Outbuf), &len, NULL);
















LONGLONG game_addr;
StrToInt64ExW(address.GetString(), STIF_SUPPORT_HEX, &game_addr);
LONGLONG game_pid;
StrToInt64ExW(pid.GetString(), STIF_SUPPORT_HEX, &game_pid);
UINT64 Mybuf[3] = { game_pid,game_addr ,8 };
DWORD len = 0;
UINT64 Outbuf = 0;
BOOL ret = DeviceIoControl(nDeviveHandle, MDL驱动读写, 
    &Mybuf, sizeof(Mybuf), &Outbuf, sizeof(Outbuf), &len, NULL);

























LONGLONG game_addr;
StrToInt64ExW(address.GetString(), STIF_SUPPORT_HEX, &game_addr);
LONGLONG game_pid;
StrToInt64ExW(pid.GetString(), STIF_SUPPORT_HEX, &game_pid);
LONGLONG userbuf;
StrToInt64ExW(TextBuf.GetString(), STIF_SUPPORT_HEX, &userbuf);
UINT64 Mybuf[3] = { game_pid,game_addr ,(UINT64)(&userbuf) };
DWORD len = 0;
UINT64 Outbuf = NULL;
BOOL ret = DeviceIoControl(nDeviveHandle, MDL驱动写, 
    &Mybuf, sizeof(Mybuf), &Outbuf, sizeof(Outbuf), &len, NULL);























LONGLONG game_addr;
StrToInt64ExW(address.GetString(), STIF_SUPPORT_HEX, &game_addr);
LONGLONG game_pid;
StrToInt64ExW(pid.GetString(), STIF_SUPPORT_HEX, &game_pid);
LONGLONG userbuf;
StrToInt64ExW(TextBuf.GetString(), STIF_SUPPORT_HEX, &userbuf);
UINT64 Mybuf[3] = { game_pid,game_addr ,(UINT64)(&userbuf) };
DWORD len = 0;
UINT64 Outbuf = NULL;
BOOL ret = DeviceIoControl(nDeviveHandle, 只读写保护, 
    &Mybuf, sizeof(Mybuf), &Outbuf, sizeof(Outbuf), &len, NULL); ^0Rw6IyjU

(1) 游戏PID >> 游戏进程
(2) 辅助DLL


// 驱动: 把我们要注入的 mymfc.dll 通过驱动注入到目标游戏进程里
AttachAndInjectProcess(irp); ^0JPYcXVD

AttachAndInjectProcess(irp)
{
// 01. 拿到游戏进程的 EPROCESS: PsLookupProcessByProcessId
        // 01. 附加到游戏进程: KeStackAttachProcess
                // 01. 拿到游戏内 ntdll.dll 模块基地址: NtdllAddress = GetUserModule(EProcess, ...);
                // 02. 拿到模块内的加载器函数: LdrLoadDll = GetModuleExport(NtdllAddress, "LdrLoadDll", EProcess);
                // 03. 用加载器函数直接加载辅助dll: InjectBuffer = GetNativeCode(LdrLoadDll, ...);
                // 04. 远线程执行辅助dll: ExecuteInNewThread(InjectBuffer, ...);
        // 02. 脱离游戏进程: KeUnstackDetachProcess
// 02. 游戏进程 EPROCESS 减1: ObDereferenceObject
} ^GxLwsKy1

0: kd> dt _PEB
ntdll!_PEB
   ...
   +0x010 ImageBaseAddress : Ptr64 Void
   +0x018 Ldr              : Ptr64 _PEB_LDR_DATA
   +0x020 ProcessParameters : Ptr64 _RTL_USER_PROCESS_PARAMETERS


0: kd> dt _PEB_LDR_DATA
ntdll!_PEB_LDR_DATA
   +0x000 Length           : Uint4B
   +0x004 Initialized      : UChar
   +0x008 SsHandle         : Ptr64 Void
   +0x010 InLoadOrderModuleList : _LIST_ENTRY
   +0x020 InMemoryOrderModuleList : _LIST_ENTRY
   +0x030 InInitializationOrderModuleList : _LIST_ENTRY
   +0x040 EntryInProgress  : Ptr64 Void
   +0x048 ShutdownInProgress : UChar
   +0x050 ShutdownThreadId : Ptr64 Void ^jIGYs8jA

typedef struct _DEBUG_OBJECT
{
    KEVENT EventsPresent; // offset: 0x00
    FAST_MUTEX Mutex; // offset: 0x10
    LIST_ENTRY StateEventListEntry; // offset: 0x30
    ULONG Flags; // offset: 0x38
}DEBUG_OBJECT, *PDEBUG_OBJECT; ^ROD8RBaM

typedef NTSTATUS(NTAPI  *pfnNtQueryInformationProcess)(                                                                
        _In_      HANDLE           ProcessHandle,
    _In_      UINT             ProcessInformationClass,
    _Out_     PVOID            ProcessInformation,
    _In_      ULONG            ProcessInformationLength,
    _Out_opt_ PULONG           ReturnLength
);

UINT ProcessDebugFlags = 0x1F;

int main(int argc, char* argv[])
{
        ULONG                DebugFlags; 
        NTSTATUS        stNtstatus;
        pfnNtQueryInformationProcess NtQueryInformationProcess;

        NtQueryInformationProcess = 
                (pfnNtQueryInformationProcess)GetProcAddress(
                LoadLibrary(TEXT("ntdll.dll")), 
                TEXT("NtQueryInformationProcess"));

        stNtstatus = NtQueryInformationProcess(
                GetCurrentProcess(),
                ProcessDebugFlags,
                &DebugFlags, sizeof(ULONG), NULL);

        if(0x00000000 == stNtstatus && NULL == DebugFlags)
        {
                MessageBox(NULL, TEXT("已检测到调试器！"),NULL, MB_OK);
                ExitProcess(NULL);
        }

        MessageBox(NULL, TEXT("程序正常运行！"), NULL, MB_OK);
        return 0;
} ^4w5wL6gS

ThreadHideFromDebugger。这是Windows提供的第一个反调试技术之一，用于微软搜索如何防止逆向，它非常强大。
如果为线程设置了此标志，则该线程将停止发送有关调试事件的通知。
这些事件包括断点和程序完成通知。此标志的值存储在_ETHREAD结构的HideFromDebugger字段中

0: kd> dt _ETHREAD
ntdll!_ETHREAD
   +0x000 Tcb              : _KTHREAD
   +0x5e0 CreateTime       : _LARGE_INTEGER
   +0x5e8 ExitTime         : _LARGE_INTEGER
   ...
   +0x6c0 CrossThreadFlags : Uint4B
   +0x6c0 Terminated       : Pos 0, 1 Bit
   +0x6c0 ThreadInserted   : Pos 1, 1 Bit
   +0x6c0 HideFromDebugger : Pos 2, 1 Bit    （置1则会让调试器收不到调试信息） ^GQRwoD0r

#include <stdio.h> 
#include <windows.h>
#include <tchar.h>

typedef DWORD (WINAPI *ZW_SET_INFORMATION_THREAD)(HANDLE, DWORD, PVOID, ULONG);
#define ThreadHideFromDebugger 17
VOID DisableDebugEvent(VOID)
{
    HINSTANCE hModule;
    ZW_SET_INFORMATION_THREAD ZwSetInformationThread;

    hModule = GetModuleHandleA("Ntdll");
    ZwSetInformationThread = 
        (ZW_SET_INFORMATION_THREAD)GetProcAddress(hModule, "ZwSetInformationThread");
    ZwSetInformationThread(GetCurrentThread(), ThreadHideFromDebugger, NULL, NULL);
}

int WINAPI WinMain (HINSTANCE hInstance, HINSTANCE hPrevInstance,
                    PSTR szCmdLine, int iCmdShow)
{
DisableDebugEvent();
     return 0 ;
} ^TVm5oWPw

Alt+t 搜索字符串: +420h] ^JPovGkwu

把所有420h改成408h, 因为
(_EPROCESS)+408h  AweInfo 这个很少用 ^OmyHQZDF

(1) 按F2修改
(2) 20改成08
(3) 然后按F2保存 ^RZXR2RJA

修改 ntoskrnl.exe/ntoskrnl.efi 处理掉一些反调试策略 ^Dw43ZI2a

(_EPROCESS)->DebugPort 指针(结构体: _DEBUG_OBJECT) ^tkLsyFKL

Windows 10 驱动开发环境 ^DLx5SxdM

malloc推荐书籍: 潘爱民的《Windows内核原理与实现》

驱动开发环境搭建，首先要确认自己电脑操作系统版本，通过CMD运行 winver 查看，
比如老师电脑显示的是 “版本 1803 …”，则表示版本是1803，
然后百度搜索WDK，去微软官网下载对应的WDK，
嫌麻烦的，可以使用老师提供的版本来部署驱动开发环境，
cn_windows_10_business_editions_version_1803_updated_march_2018_x64_dvd_12063730.iso


驱动安装步骤官网参考链接(win10 22H2): bing 搜索 vs2022 wdk
https://learn.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk

1、安装必要的组件，如下图所示： ^Mf5vtCTC

2、下载以及安装SDK、WDK安装包，如下图所示： ^ky0hths3

调试环境老师推荐用虚拟机，即使用虚拟机里的 Windows 10 作为驱动调试客户机，
然后进入把Windows设置成测试模式，cmd管理员运行如下命令，然后重启虚拟机，

// 开启测试模式
bcdedit /set testsigning on

// 关闭测试模式
bcdedit /set testsigning off

关闭系统防火墙之类的，以及更新服务也关了。 ^R8nAb2SD

新建源文件 main.c，然后编写如下代码，
上面的C++警告视为错误，可能需要创建源文件之后才能看到配置项， ^KUf1EgMX

#include <ntifs.h>

NTSTATUS
DriverEntry(
    IN PDRIVER_OBJECT  DriverObject,
    IN PUNICODE_STRING  RegistryPath
)
{
    NTSTATUS status = STATUS_SUCCESS;
    KdPrint(("seafly: Hello world!\\n"));
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "seafly: Hello world Ex!\\n");
    return status;
} ^VJCvOvc8

编写之后，编译驱动，并用老师提供的 DriverMonitor 工具加载到系统里。
老师推荐，不用 KdPrint 打印信息，因为它要在 DbgView 里勾选详细输出，这会使其卡顿，因为系统很多信息也要输出，
所以这里老师推荐使用 DbgPrintEx 这个打印函数。 ^PcgiD8Vj

通过官网查看 DbgPrintEx 的参数，其函数声明如下：

NTSYSAPI ULONG DbgPrintEx(
  [in] ULONG ComponentId,
  [in] ULONG Level,
  [in] PCSTR Format,
       ...   
);

/*
ComponentId: 为了避免将驱动程序的输出与 Windows 组件的输出混合, 需以下值选一,
        DPFLTR_IHVVIDEO_ID
        DPFLTR_IHVAUDIO_ID
        DPFLTR_IHVNETWORK_ID
        DPFLTR_IHVSTREAMING_ID
        DPFLTR_IHVBUS_ID
        DPFLTR_IHVDRIVER_ID

Format: 不支持任何浮点格式的输出
**/ ^QFwJywcr

#include <ntifs.h>

VOID
MyDriverUnload(
    _In_ struct _DRIVER_OBJECT* DriverObject
)
{
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "ByeByeWorld,DriverName=%wZ\\n", DriverObject->DriverName);
}

NTSTATUS
DriverEntry(
    IN PDRIVER_OBJECT  DriverObject,
    IN PUNICODE_STRING  RegistryPath
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "HelloWorld,DriverName=%wZ\\n", DriverObject->DriverName);
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "HelloWorld,RegistryPath=%wZ\\n", RegistryPath);

    DriverObject->DriverUnload = MyDriverUnload;
    return status;
} ^VCSK3Lfg

下面是字符串打印格式的示例代码： ^3oNZHss1

然后我们开始编写第一个驱动，helloworld驱动，使用 KMDF 空项目 模板来创建，并做一些必要的配置x64 Debug。 ^aTBrgyNf

创建驱动设备对象 ^n2tD06PM

由于我们的三环用户程序需要和驱动进行交互，这里交互的方式之一就是通过设备对象来进行交互，因此本节围绕着设备对象进行编程探究。 ^jIocjuGY

#include <ntifs.h>

VOID
MyDriverUnload(
    _In_ struct _DRIVER_OBJECT* DriverObject
)
{
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "ByeByeWorld,DriverName=%wZ\\n", DriverObject->DriverName);
}

NTSTATUS
MyIRPCreate(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "calling %wZ\\n", __FUNCTION__);
    return status;
}

NTSTATUS
DriverEntry(
    IN PDRIVER_OBJECT  DriverObject,
    IN PUNICODE_STRING  RegistryPath
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "HelloWorld,DriverName=%wZ\\n", DriverObject->DriverName);
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "HelloWorld,RegistryPath=%wZ\\n", RegistryPath);

    DriverObject->DriverUnload = MyDriverUnload;
    DriverObject->MajorFunction[IRP_MJ_CREATE] = MyIRPCreate;
    return status;
} ^xK7QHCyr

如上代码所示，我们创建了 MyIRPCreate 函数，我们想要触发它执行，因此我们需要创建设备对象，
继续添加代码，顺便让驱动支持卸载，即在卸载的操作中释放相关资源，完整代码如下： ^Sm3Nx3S0

#include <ntifs.h>

UNICODE_STRING g_myDeviceSymName;

VOID MyDriverUnload(
    _In_ struct _DRIVER_OBJECT* DriverObject
)
{
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);

    // 驱动卸载时, 需要释放相关资源, 方便下次能够正常加载
    if (g_myDeviceSymName.Length != 0)
    {
        IoDeleteSymbolicLink(&g_myDeviceSymName);
        RtlInitUnicodeString(&g_myDeviceSymName, L"");
    }

    if (DriverObject->DeviceObject != NULL)
    {
        IoDeleteDevice(DriverObject->DeviceObject);
        DriverObject->DeviceObject = NULL;
    }
}

NTSTATUS MyIRPCreate(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);
    return status;
}

NTSTATUS MyIRPClose(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);
    return status;
}

NTSTATUS MyIRPRead(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);
    return status;
}

NTSTATUS MyIRWrite(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);
    return status;
}

NTSTATUS
DriverEntry(
    IN PDRIVER_OBJECT  DriverObject,
    IN PUNICODE_STRING  RegistryPath
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "驱动名称=%wZ\\n", DriverObject->DriverName);
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "注册路径=%wZ\\n", RegistryPath);

    DriverObject->DriverUnload = MyDriverUnload;
    DriverObject->MajorFunction[IRP_MJ_CREATE] = MyIRPCreate;
    DriverObject->MajorFunction[IRP_MJ_CLOSE] = MyIRPClose;
    DriverObject->MajorFunction[IRP_MJ_READ] = MyIRPRead;
    DriverObject->MajorFunction[IRP_MJ_WRITE] = MyIRWrite;

    // 创建设备对象(用于和三环通信)
    UNICODE_STRING myDeviceName;

    // 驱动层的名字
    RtlInitUnicodeString(&myDeviceName, L"\\\\Device\\\\myhello");
    status = IoCreateDevice(
        DriverObject,
        sizeof(DriverObject->DriverExtension),
        &myDeviceName,
        FILE_DEVICE_UNKNOWN,
        FILE_DEVICE_SECURE_OPEN,
        FALSE,
        &DriverObject->DeviceObject
    );

    if (status != STATUS_SUCCESS)
    {
        DbgPrintEx(77, 0, "IoCreateDevice Failed,status=%d\\n", status);

        if (DriverObject->DeviceObject != NULL)
        {
            IoDeleteDevice(DriverObject->DeviceObject);
            DriverObject->DeviceObject = NULL;
        }
        return status;
    }

    // 创建3环别名(用户程序可见的名字)
    RtlInitUnicodeString(&g_myDeviceSymName, L"\\\\??\\\\myhello");
    status = IoCreateSymbolicLink(&g_myDeviceSymName, &myDeviceName);
    if (status != STATUS_SUCCESS)
    {
        DbgPrintEx(77, 0, "IoCreateSymbolicLink Failed,status=%d\\n", status);

        if (g_myDeviceSymName.Length != 0)
        {
            IoDeleteSymbolicLink(&g_myDeviceSymName);
            RtlInitUnicodeString(&g_myDeviceSymName, L"");
        }
        return status;
    }

    return status;
} ^YtTHyck0

然后在用户空间打开这个三环文件，以建立和零环驱动之间的通信， ^dkC87ChH

#include <Windows.h>
#include <iostream>

int main()
{
    HANDLE hFile;
    hFile = CreateFile(
        L"\\\\??\\\\myhello",
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
    if (hFile == INVALID_HANDLE_VALUE)
    {
        std::cout << "CreateFile Failed,Status=" << GetLastError() << std::endl;
        return -1;
    }
    std::cout << "已打开设备文件\\n";
    std::cout << "已关闭设备文件\\n";
    CloseHandle(hFile);
    return 0;
} ^yBIYQ241

驱动IRP通讯 ^3PXMpxBC

前面的设备对象，我们只是触发了其打开、关闭、读取、写入的函数调用，
并没有产生实质性的数据交互，
我们应用层辅助一般会通过: ReadProcessMemory，WriteProcessMemory 来访问游戏内存，
但是很多有保护的游戏会把这两个函数 Hook 了，或者加了检测，
那最好的办法呢，是我们自己建立这样的函数，完整的来实现这个读写内存的功能，
下面是对设备对象加了读写请求的处理，完整代码如下： ^fTKKlzv3

#include <ntifs.h>

UNICODE_STRING g_myDeviceSymName;

VOID MyDriverUnload(
    _In_ struct _DRIVER_OBJECT* DriverObject
)
{
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);

    // 驱动卸载时, 需要释放相关资源, 方便下次能够正常加载
    if (g_myDeviceSymName.Length != 0)
    {
        IoDeleteSymbolicLink(&g_myDeviceSymName);
        RtlInitUnicodeString(&g_myDeviceSymName, L"");
    }

    if (DriverObject->DeviceObject != NULL)
    {
        IoDeleteDevice(DriverObject->DeviceObject);
        DriverObject->DeviceObject = NULL;
    }
}

NTSTATUS MyIRPCreate(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);

    PIO_STACK_LOCATION ios = IoGetCurrentIrpStackLocation(Irp);
    switch (ios->MajorFunction)
    {
    case IRP_MJ_CREATE:
    {
        DbgPrintEx(77, 0, "%s:IRP_MJ_CREATE\\n",__FUNCTION__);
        break;
    }
    }

    // 请求结束后,上报必要的状态
    Irp->IoStatus.Status = STATUS_SUCCESS;
    Irp->IoStatus.Information = 4;
    IoCompleteRequest(Irp, IO_NO_INCREMENT);

    return status;
}

NTSTATUS MyIRPClose(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);

    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = sizeof(status); //实际传输的字节数
    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    return status;
}

NTSTATUS MyIRPRead(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);

    // 用户请求: 读取设备
    char mybuf[32] = "这是驱动层数据";
    RtlCopyMemory(Irp->UserBuffer, mybuf, sizeof(mybuf));

    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = sizeof(mybuf); //实际传输的字节数
    IoCompleteRequest(Irp, IO_NO_INCREMENT);

    return status;
}

NTSTATUS MyIRWrite(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);

    // 用户写入请求
    char* UserMsg = (char*)Irp->UserBuffer;
    DWORD32 UserLen = strlen(UserMsg);
    DbgPrintEx(77, 0, "%s:用户写入=%s\\n", __FUNCTION__, UserMsg);

    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = UserLen; //实际传输的字节数
    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    return status;
}

NTSTATUS
DriverEntry(
    IN PDRIVER_OBJECT  DriverObject,
    IN PUNICODE_STRING  RegistryPath
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "驱动名称=%wZ\\n", DriverObject->DriverName);
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "注册路径=%wZ\\n", RegistryPath);

    DriverObject->DriverUnload = MyDriverUnload;
    DriverObject->MajorFunction[IRP_MJ_CREATE] = MyIRPCreate;
    DriverObject->MajorFunction[IRP_MJ_CLOSE] = MyIRPClose;
    DriverObject->MajorFunction[IRP_MJ_READ] = MyIRPRead;
    DriverObject->MajorFunction[IRP_MJ_WRITE] = MyIRWrite;

    // 创建设备对象(用于和三环通信)
    UNICODE_STRING myDeviceName;

    // 驱动层的名字
    RtlInitUnicodeString(&myDeviceName, L"\\\\Device\\\\myhello");
    status = IoCreateDevice(
        DriverObject,
        sizeof(DriverObject->DriverExtension),
        &myDeviceName,
        FILE_DEVICE_UNKNOWN,
        FILE_DEVICE_SECURE_OPEN,
        FALSE,
        &DriverObject->DeviceObject
    );

    if (status != STATUS_SUCCESS)
    {
        DbgPrintEx(77, 0, "IoCreateDevice Failed,status=%d\\n", status);

        if (DriverObject->DeviceObject != NULL)
        {
            IoDeleteDevice(DriverObject->DeviceObject);
            DriverObject->DeviceObject = NULL;
        }
        return status;
    }

    // 创建3环别名(用户程序可见的名字)
    RtlInitUnicodeString(&g_myDeviceSymName, L"\\\\??\\\\myhello");
    status = IoCreateSymbolicLink(&g_myDeviceSymName, &myDeviceName);
    if (status != STATUS_SUCCESS)
    {
        DbgPrintEx(77, 0, "IoCreateSymbolicLink Failed,status=%d\\n", status);

        if (g_myDeviceSymName.Length != 0)
        {
            IoDeleteSymbolicLink(&g_myDeviceSymName);
            RtlInitUnicodeString(&g_myDeviceSymName, L"");
        }
        return status;
    }

    return status;
} ^NXDN58Ct

下面是对应的用户程序的测试代码： ^nPZwsFVP

#include <Windows.h>
#include <iostream>

int main()
{
    HANDLE hFile;
    hFile = CreateFile(
        L"\\\\??\\\\myhello",
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
    if (hFile == INVALID_HANDLE_VALUE)
    {
        std::cout << "CreateFile Failed,Status=" << GetLastError() << std::endl;
        return -1;
    }
    std::cout << "已打开设备文件\\n";

    char Buffer[64] = "weichen666微尘";
    DWORD rdLen = 0;
    DWORD wrLen = 0;

    // 往设备写入数据
    if (!WriteFile(hFile, Buffer, sizeof(Buffer), &wrLen, NULL))
    {
        std::cout << "写入设备失败,LastError=" << GetLastError() << std::endl;
        return -1;
    }
    std::cout << "已写入设备文件,Buf=" << Buffer << std::endl;

    // 从设备读取数据
    memset(Buffer, 0, sizeof(Buffer));
    if (!ReadFile(hFile, Buffer, sizeof(Buffer), &rdLen, NULL))
    {
        std::cout << "读取设备失败,LastError=" << GetLastError() << std::endl;
        return -1;
    }
    std::cout << "已读取设备文件,Buf=" << Buffer << std::endl;

    std::cout << "已关闭设备文件\\n";
    CloseHandle(hFile);

    system("pause");
    return 0;
} ^aYp8OpBp

驱动设备控制 ^L2WYCnoB

设备的控制接口，相比于读写分开的好处是，可以读写同时，适合小批量数据的读写，
下面是完整的设备对象控制代码，包含驱动代码和应用程序代码。 ^0nNEBO4g

#include <ntifs.h>

UNICODE_STRING g_myDeviceSymName;

VOID MyDriverUnload(
    _In_ struct _DRIVER_OBJECT* DriverObject
)
{
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);

    // 驱动卸载时, 需要释放相关资源, 方便下次能够正常加载
    if (g_myDeviceSymName.Length != 0)
    {
        IoDeleteSymbolicLink(&g_myDeviceSymName);
        RtlInitUnicodeString(&g_myDeviceSymName, L"");
    }

    if (DriverObject->DeviceObject != NULL)
    {
        IoDeleteDevice(DriverObject->DeviceObject);
        DriverObject->DeviceObject = NULL;
    }
}

NTSTATUS MyIRPCreate(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);

    PIO_STACK_LOCATION ios = IoGetCurrentIrpStackLocation(Irp);
    switch (ios->MajorFunction)
    {
    case IRP_MJ_CREATE:
    {
        DbgPrintEx(77, 0, "%s:IRP_MJ_CREATE\\n",__FUNCTION__);
        break;
    }
    }

    // 请求结束后,上报必要的状态
    Irp->IoStatus.Status = STATUS_SUCCESS;
    Irp->IoStatus.Information = 4;
    IoCompleteRequest(Irp, IO_NO_INCREMENT);

    return status;
}

NTSTATUS MyIRPClose(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);

    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = sizeof(status); //实际传输的字节数
    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    return status;
}

NTSTATUS MyIRPRead(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);

    // 用户请求: 读取设备
    char mybuf[32] = "这是驱动层数据";
    RtlCopyMemory(Irp->UserBuffer, mybuf, sizeof(mybuf));

    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = sizeof(mybuf); //实际传输的字节数
    IoCompleteRequest(Irp, IO_NO_INCREMENT);

    return status;
}

NTSTATUS MyIRWrite(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);

    // 用户写入请求
    char* UserMsg = (char*)Irp->UserBuffer;
    DWORD32 UserLen = strlen(UserMsg);
    DbgPrintEx(77, 0, "%s:用户写入=%s\\n", __FUNCTION__, UserMsg);

    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = UserLen; //实际传输的字节数
    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    return status;
}

NTSTATUS MyIRPDeviceCtrl(
    _In_ struct _DEVICE_OBJECT* DeviceObject,
    _Inout_ struct _IRP* Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "called %s\\n", __FUNCTION__);

    // 用户控制请求
    char drvBuf[64] = "驱动的控制数据";
    RtlCopyMemory(Irp->AssociatedIrp.SystemBuffer, drvBuf, strlen(drvBuf));

    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = strlen(drvBuf); //实际传输的字节数
    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    return status;
}

NTSTATUS
DriverEntry(
    IN PDRIVER_OBJECT  DriverObject,
    IN PUNICODE_STRING  RegistryPath
)
{
    NTSTATUS status = STATUS_SUCCESS;
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "驱动名称=%wZ\\n", DriverObject->DriverName);
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, 0, "注册路径=%wZ\\n", RegistryPath);

    DriverObject->DriverUnload = MyDriverUnload;
    DriverObject->MajorFunction[IRP_MJ_CREATE] = MyIRPCreate;
    DriverObject->MajorFunction[IRP_MJ_CLOSE] = MyIRPClose;
    DriverObject->MajorFunction[IRP_MJ_READ] = MyIRPRead;
    DriverObject->MajorFunction[IRP_MJ_WRITE] = MyIRWrite;
    DriverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL] = MyIRPDeviceCtrl;

    // 创建设备对象(用于和三环通信)
    UNICODE_STRING myDeviceName;

    // 驱动层的名字
    RtlInitUnicodeString(&myDeviceName, L"\\\\Device\\\\myhello");
    status = IoCreateDevice(
        DriverObject,
        sizeof(DriverObject->DriverExtension),
        &myDeviceName,
        FILE_DEVICE_UNKNOWN,
        FILE_DEVICE_SECURE_OPEN,
        FALSE,
        &DriverObject->DeviceObject
    );

    if (status != STATUS_SUCCESS)
    {
        DbgPrintEx(77, 0, "IoCreateDevice Failed,status=%d\\n", status);

        if (DriverObject->DeviceObject != NULL)
        {
            IoDeleteDevice(DriverObject->DeviceObject);
            DriverObject->DeviceObject = NULL;
        }
        return status;
    }

    // 创建3环别名(用户程序可见的名字)
    RtlInitUnicodeString(&g_myDeviceSymName, L"\\\\??\\\\myhello");
    status = IoCreateSymbolicLink(&g_myDeviceSymName, &myDeviceName);
    if (status != STATUS_SUCCESS)
    {
        DbgPrintEx(77, 0, "IoCreateSymbolicLink Failed,status=%d\\n", status);

        if (g_myDeviceSymName.Length != 0)
        {
            IoDeleteSymbolicLink(&g_myDeviceSymName);
            RtlInitUnicodeString(&g_myDeviceSymName, L"");
        }
        return status;
    }

    return status;
} ^4bHiuJS1

#include <Windows.h>
#include <iostream>

#define CTRL_RWDEVICE CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)

int main()
{
    HANDLE hFile;
    hFile = CreateFile(
        L"\\\\??\\\\myhello",
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
    if (hFile == INVALID_HANDLE_VALUE)
    {
        std::cout << "CreateFile Failed,Status=" << GetLastError() << std::endl;
        return -1;
    }
    std::cout << "已打开设备文件\\n";

    char Buffer[64] = "weichen666微尘";
    DWORD rdLen = 0;
    DWORD wrLen = 0;

    // 往设备写入数据
    if (!WriteFile(hFile, Buffer, sizeof(Buffer), &wrLen, NULL))
    {
        std::cout << "写入设备失败,LastError=" << GetLastError() << std::endl;
        return -1;
    }
    std::cout << "已写入设备文件,Buf=" << Buffer << std::endl;

    // 从设备读取数据
    memset(Buffer, 0, sizeof(Buffer));
    if (!ReadFile(hFile, Buffer, sizeof(Buffer), &rdLen, NULL))
    {
        std::cout << "读取设备失败,LastError=" << GetLastError() << std::endl;
        return -1;
    }
    std::cout << "已读取设备文件,Buf=" << Buffer << std::endl;

    // 设备控制
    char ibuf[64] = "weichen666微尘";
    char obuf[64] = { 0 };
    DeviceIoControl(hFile, CTRL_RWDEVICE, 
        ibuf, sizeof(ibuf), 
        obuf, sizeof(obuf),
        &rdLen,
        NULL
    );
    printf("obuf = %s\\n", obuf);

    std::cout << "已关闭设备文件\\n";
    CloseHandle(hFile);

    system("pause");
    return 0;
} ^qreT5XAf

控制码是一个 32 位整数，由以下四部分组成：
| 设备类型(16位) | 访问权限(2位) | 功能码(12位) | 方法(2位) |
设备类型：标识设备所属的类别（如文件系统、磁盘设备等），通常使用预定义的常量（如 FILE_DEVICE_UNKNOWN）。 
访问权限：指定访问要求（如 FILE_ANY_ACCESS、FILE_READ_ACCESS）。 功能码：驱动自定义的功能编号，用于区分不同的控制命令。
方法：指定数据传输的方式（如 METHOD_BUFFERED、METHOD_DIRECT）。


// 驱动和应用程序需保持一致
// 定义设备类型（自定义值，需避免与系统冲突）
#define FILE_DEVICE_MYDEVICE 0x8000// 定义功能码（0x800 ~ 0xFFF 为自定义范围）
#define MY_FUNCTION_READ  0x800
#define MY_FUNCTION_WRITE 0x801// 生成控制码
#define CTRL_RWDEVICE CTL_CODE(FILE_DEVICE_MYDEVICE, MY_FUNCTION_READ, METHOD_BUFFERED, FILE_ANY_ACCESS)


在驱动对应的Irp请求处理函数中，可以通过以下方式获取：
PIO_STACK_LOCATION stack = IoGetCurrentIrpStackLocation(Irp);
ULONG controlCode = stack->Parameters.DeviceIoControl.IoControlCode;//控制码
ULONG inputBufferLength = stack->Parameters.DeviceIoControl.InputBufferLength;
ULONG outputBufferLength = stack->Parameters.DeviceIoControl.OutputBufferLength;
PVOID inputBuffer = Irp->AssociatedIrp.SystemBuffer;
PVOID outputBuffer = Irp->AssociatedIrp.SystemBuffer; ^o2uYleSI

C++Win764x下做掉PatchGuard教程: https://blog.csdn.net/kingswb/article/details/64934007
附件: C++Win764x下做掉PatchGuard教程_win7.html ^nUF0JL47

// 加载驱动
DriverLoad("HelloWord","HelloWord.sys");

// 卸载驱动
UnloadDriver("HelloWord");

// 打开驱动
#define 三环符号 L"\\??\\myhelloWord"
DeviveHandle=CreateFile(三环符号, 
        GENERIC_READ| GENERIC_WRITE, 
        FILE_SHARE_READ, NULL, 
        OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL,NULL); ^UGeRiE9z

#include "pch.h"
#include "windows.h"
#include "winsvc.h"

void DriverLoad(char* DriverName,char* NzPath)
{
        char nbuf[256] = {0};
        GetFullPathNameA(NzPath,256,nbuf,NULL);
        char buf[1024] = {0};
        SC_HANDLE hServiceDDK = NULL;
        SC_HANDLE hServiceMgr =OpenSCManagerA(NULL,NULL, SC_MANAGER_ALL_ACCESS);
        if (hServiceMgr)
        {
                wsprintfA(buf, "OpenSCManagerA 打开OK");
                OutputDebugStringA(buf);
                 hServiceDDK = CreateServiceA(
                        hServiceMgr,
                        DriverName,
                        DriverName,
                        SERVICE_START,
                        SERVICE_KERNEL_DRIVER,
                        SERVICE_DEMAND_START,
                        SERVICE_ERROR_NORMAL,
                        nbuf,
                        NULL,
                        NULL,
                        NULL,
                        NULL,
                        NULL
                );
                if (hServiceDDK)
                {
                        wsprintfA(buf, "CreateServiceA 打开OK");
                        OutputDebugStringA(buf);


        
                }
                else if(GetLastError() == ERROR_SERVICE_EXISTS)
                {


                        //wsprintfA(buf, "CreateServiceA 打开失败cuowu=%d", GetLastError());
                        //OutputDebugStringA(buf);

                        hServiceDDK = OpenServiceA(hServiceMgr, DriverName, SERVICE_START);


                        if (hServiceDDK)
                        {
                                wsprintfA(buf, "OpenServiceA 打开OK");
                                OutputDebugStringA(buf);




                        }
                        else
                        {
                                wsprintfA(buf, "OpenServiceA 打开失败cuowu=%d", GetLastError());
                                OutputDebugStringA(buf);
                        }

                }


                if (StartServiceA(hServiceDDK, NULL, NULL))
                {
                        wsprintfA(buf, "StartServiceA OK");
                        OutputDebugStringA(buf);
                }
                else
                {
                        wsprintfA(buf, "StartServiceA 打开失败cuowu=%d", GetLastError());
                        OutputDebugStringA(buf);
                }


        }
        else
        {
                wsprintfA(buf,"OpenSCManagerA 打开失败cuowu=%d", GetLastError());
                OutputDebugStringA(buf);
        }

        if (hServiceDDK)
        {
                CloseServiceHandle(hServiceDDK);
        }
        if (hServiceMgr)
        {
                CloseServiceHandle(hServiceMgr);
        }

}


BOOL UnloadDriver(char * lpszDriverName)
{
        BOOL bRet = FALSE;
        SC_HANDLE hServiceMgr = NULL;//SCM管理器的句柄
        SC_HANDLE hServiceDDK = NULL;//NT驱动程序的服务句柄
        SERVICE_STATUS SvrSta;
        char buf[2048] = { 0 };
        hServiceMgr = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
        if (hServiceMgr == NULL)
        {
                //带开SCM管理器失败
                sprintf_s(buf, "weichen:OpenSCManager() Faild %d ! \n", GetLastError());
                OutputDebugStringA(buf);
                bRet = FALSE;
                goto BeforeLeave;
        }
        else
        {
                //带开SCM管理器失败成功
                sprintf_s(buf, "weichen:OpenSCManager() ok ! \n");
                OutputDebugStringA(buf);
        }
        //打开驱动所对应的服务
        hServiceDDK = OpenServiceA(hServiceMgr, lpszDriverName, SERVICE_ALL_ACCESS);

        if (hServiceDDK == NULL)
        {
                //打开驱动所对应的服务失败
                sprintf_s(buf, "weichen:OpenService() Faild %d ! \n", GetLastError());
                OutputDebugStringA(buf);
                bRet = FALSE;
                goto BeforeLeave;
        }
        else
        {
                sprintf_s(buf, "weichen:OpenService() ok ! \n");
                OutputDebugStringA(buf);
        }

        //停止驱动程序，如果停止失败，只有重新启动才能，再动态加载。  
        if (!ControlService(hServiceDDK, SERVICE_CONTROL_STOP, &SvrSta))
        {
                sprintf_s(buf, "weichen:ControlService() Faild %d !\n", GetLastError());
                OutputDebugStringA(buf);
        }
        else
        {
                //打开驱动所对应的失败
                sprintf_s(buf, "weichen:ControlService() ok !\n");
                OutputDebugStringA(buf);
        }
        //动态卸载驱动程序,删除服务  
        if (!DeleteService(hServiceDDK))
        {
                //卸载失败
                sprintf_s(buf, "weichen:DeleteSrevice() Faild %d !\n", GetLastError());
                OutputDebugStringA(buf);
        }
        else
        {
                //卸载成功
                sprintf_s(buf, "weichen:DelServer:deleteSrevice() ok !\n");
                OutputDebugStringA(buf);
        }
        bRet = TRUE;
BeforeLeave:
        //离开前关闭打开的句柄
        if (hServiceDDK)
        {
                CloseServiceHandle(hServiceDDK);
        }
        if (hServiceMgr)
        {
                CloseServiceHandle(hServiceMgr);
        }
        return bRet;
} ^msait8Vz

代码实现驱动自动加载/卸载 ^dLHJuS9B

## Element Links
nUF0JL47: [[C++Win764x下做掉PatchGuard教程_win7.html]]

## Embedded Files
36e001afa1f0d7e846214744c049e45f4d7889df: [[Pasted Image 20260510215422_568.png]]

a415a51c5807a072580bf223ca25f8f679c6a3f6: [[Pasted Image 20260511111101_597.png]]

befe91de9453895a23b216d326eb56cf9cec7a40: [[Pasted Image 20260511111314_518.png]]

0038a65cfebc97a6dccd71805acc39262c3aeaa8: [[Pasted Image 20260511144126_045.png]]

cffcd7d0cd7893924948f248709758f5b24f4d23: [[Pasted Image 20260511144403_053.png]]

f49354f64dab08cce5e49e9148c0df4ad06caa5e: [[Pasted Image 20260514232153_256.png]]

de6189e76d20607d7bc9a03f01367f30148b1ffb: [[Pasted Image 20260515001038_938.png]]

802de29337af12bdd7e660aa353c3e5a85041c20: [[Pasted Image 20260515094227_551.png]]

006bdb83f8a8eec9f86deb51213fc057d8874312: [[Pasted Image 20260517225347_273.png]]

c33bc10e87df51e55050ee9eaa338e93c59e00e6: [[Pasted Image 20260517225821_613.png]]

4bc13f677adff19e4b90c03de4a84714cb60a68c: [[Pasted Image 20260517230815_399.png]]

0d60a20580e90663acf16e878f8ea5d2745c3ff5: [[Pasted Image 20260518005315_112.png]]

3a95789a4d98bcb1ff7168506501e6bd5a05379a: [[Pasted Image 20260518092950_867.png]]

96ffce03147fe434856deddc43f8b7ea9c1ed166: [[Pasted Image 20260518093030_924.png]]

9caf5a1037e25e21605c640d3d63913cb569b745: [[Pasted Image 20260518093303_887.png]]

2d82472223dba875c1a133bd923db97dbfe00c6c: [[Pasted Image 20260518093536_374.png]]

90302facd2ea182a055d061ff7b04a3b862f1a3e: [[Pasted Image 20260518093756_498.png]]

%%
## Drawing
```compressed-json
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

2kaSkCV6ySAVeqxMNXrxpszGjflYSHSwUab9evmm/PrJIFN68XEDPT6m0yxretd6l3qWbAOmwGwjpqusE6btrG7hd3rivCZGlfq0BpIFK6xxBuqmqvqueoamogaABo2EC4bCfFamoEFBBqisFPrZLBIYJsbPxqz6jaac+pGmgvrbpowGzLkHpvHGp6biSHkGz/rv+pOGv/rFRtxxbXksJpamzsa2pp6m7ia2eqJGkkb+Ju/tafqoeUhaCaaVprem

iJBrpsH61ibb+o36tSwqpvHGsUa4ZpemynqrrA+mq4bvprAG6/qfhpI8WmaB4GhmiEbGZvD68Jo6+oUGxGaPxtUG3mb3XnRmz6bMZo5m13qqSQAmhq05LCYG/frUxuZG5AQUBuV9CGbaBtx68caVZtf6wgaWZr8sNmavpomtTF0exu5myKxIZsOEfmbbxv1m56a62hFmhGalBoY8FQb/+sv67xlpZvZms2a7CWEGy2accRE8W2aO0SkG4kaYRvqm

x2b3+tFml2afvGbGr8bABq9m02avhssG5iaCRp96wSbVLGEm4khRJvVmlwbk5rVm9HryptEGuwauAxMG1sF85rEAGwak5voDEdAqwU8G4gBvBvCtPwaAhqCG9yaIkBCGgiaPzC1G8cAohoe6gmbshsSG2c5khqKG+Kbe5tTm3GaGJRyGr8A/RoKGsCZh5udBUmbKOXzGyobNOSimhDFahshhUvE5HD7mvGaw5qYADobHeq6GvKaehrh68pEippfy

ZHqU5rKmtKbWRvTmqul/hsHm+YaP7HAm++xIJpC9J31bRtDmuqa95ufGqUaJiBlG44bxZvdmzOkE5tlm6u0O5oESe4bu5seGm5A9RoNG8ibPhpNGi2azRqLm9kbphtmGh+bARo/sMCb+RuvG8cboJtFGjKa2hu/m/EhHRsRGzCa2xrdGogx/xv9cTEbBxq5G3EawJnxGnGaAWRH61/ry5sn6wmbKRsCGpybiZpGms+atEUpmpAbcZpvmiqaphs5G

7kaZ5svGsKwxxvLG0L0P5pTGn+b6xoRGxsbXZtjml0aKFt/GqhbcJoRdcBau5uK8XUaXhrImhq8EFu7Gi+x/ZveJK8aIJpvG60a7xsFmozkwgnhGp0bQrWAWjRbsJq0WtqbsXSrpH0a/RoDGoMaP7BDGrWAwxvwYSMboxtoMWMa9xrhFIKwpxvFGliaMxtWdJWEcxvcgPMaKhsLG08ajLBkW28b8FqrGx5ERQBrG3Ybf5oOG9Cb3xsBmiWb5xpVG

jGalxo8WvCazFuQW4CbwbXEW4can5pwWqxa8FrkW6JbUJocWx0aMJu/G1xaKlpwmqpaaFtXG2gwNxq3GncawJgiWkrlExsPG+0aWJqLG0RbUFovGppbRxtwW2Rb35ofG9IkJRpfGv+a3xvXxQBaUZrKW9sa+lvcWuWaVxsOEXsaA5rR5UCaQRuaWl+brFqgmuRbYJt+6+CbEJofoZCaNls6WnZajZpAZEBbKlpOW6pbDhFCGwibdAigWtc44FuMW

mAI1hRomuibkIgYmuebIltmW2+b7PRLmhway5tmWiSbJlsvmsSa0lozm5FbOJtRW1Kbc5pEdaHxpJskdAlLA2AbrChMtvIpknzymivjcvqSMUzEw3SbZqEUmnSaNJsHcWNEcfSZWhrqz2Sa6zla2VvDAAybuuuMm685Juv+QAbq//UsmyoBrJvVIWybHTlFW6jFHJtWNObqtOUO69QAlus8mhIN1uscDAeAtutsgQKaMgGCmwgVjuqhwcKbjA0mF

VebI4RimrVae5u+6jqaJ5uSm0ear5sB6whbthuymx3rcptwaY+a+htPmwYbipovm9habBsRWm2b6ZoFml1aspuZm4gadRBNm0BbGerHm9nquptVm7GaxJp2moywhppZsNNbAbBGmvXqU1tUsEaapppmmuokc1vnmhaaRTB16laai1qREMGaQZrN6mgMK1vJ9b4EHeuVhRta61o2EM6aJrDbW0awLppE8D3rSprTGtOaRPGtmzfqQ1tvG2GahZvJ6

16aPZqlm3paZZt+Wn2aRPD+mtPqSlsz6hels+qKRMGaVbGhIQvqB1tRmoObK+oTWg2aI5tYGxQahuqRmt2b9lo+JaNbZ1uedUyw7VrsW/bqCZrYQakaSZpLWvXryZoHgQRaDBo5cQdazLF3W5/rWFodmyPqJ1slm1oNmppnW/pa/lqusc2bIrHOW7axv1tMsX9aQ5uYG4WbI5udmk9a9lpbG6VxL1vA2t9bmbR2df1wlZsCse2a4ZvYW9MbD5tQG

mgbXeoQ2iAAiNqFmxqaeBp+W7Dafpug28xbgnB1mwPq9Zob3JDbD1qjmtDal1vPWwGwsNuOWudbEFpqWoCaLlux64dbg5pqmsNbw5o/gJ2a2Bt421RbPxvUW0DbvZqrmviax5uxWnURM5rEAbOabpvRW6Cxe1r56zHqg1o2EHTbuAwJmwlaTAzDCjwav+C8Gq9kfBoSdJuaqRp4WjIBgho69QFbO5sgWm1b0hu3mieaB5vqAIebaQgdW21a41pAl

Sebp5sKG4LasgQXmsoaUltwAKoaU/XXmkvFFISYWsSaWFpaGr+aKrFymj1b8ppPmhHrfVvPmvObt5pEWlBazxrQWgEapFr8sDJabFqyW2qaiFp2GusbXxqcWipw+Now2npbVNsTmjUa7hoiGkFaorAMW0ia3hvBWgzaIkBg2v3rwbXvmwLbH5uwW5ZaWltWW+K15Ft3mnYbHFrIWjrbylrA2oTaRtrLRBpaeRsYWzOxb1v/W4jaH1pgQZubXNrbB

PhbCtoEWozaV+vkZCYb5lvK2nbbJFqWWyxbbltaW9+a7Fs2Wgpb/5pUWmOblNqam9ba1Nu62gSw9FugW54bBtsNGiibjRtMWs5aWNoHgO/qatvuW97bDtrEANCbVtvjm6dbAds9GrxbfRvwYQ0JfFrxiYMbQxqjgCMaoxo1YGMbQUDjG+oN31sTG9paUdtiW59b4luzG6EhcxrqBJebUltM2720VlsyWtpacloUW/JalFqKW3Za2trjm42aGNs22

kTaYdtqW8Tbm7QUAR7aqtpLGrnbatp522HFclunGj5bBdq+Wz2aMdq626HblwXXGzcbcdoNCbca1YF3GqnaoBqmW93Ajxs02rTbMuUWW5+a4rFfmm0b1lqfG/nbmtp+204b2tvR2zraY1ol2u7xYdvQGkCbQUBm2l7aHdruWt+aFtseWrx5nlst2lCaUdvV27pavdoB2nXbTlo2ETzaI32BWkiawVqNGqiaFAChW+iaP4EYmjTacZpt2w4RzNr02

qmbCVqL2rFaOds4DJLJS5se5ANbnBq22k8KTTRJWvoNjvNiVR9CzvMM6i7zeZK70asBfIBdNOUB9AAoAKpD0zy1y2rRI2JH6agSUTh0K+ETIal1E1jqSs2apRA1+qraIRM123JsK7jVCczHKoXCIuqnKqLrDXNnKzAqJ8vEqh4rzXOlgHgBAULo8zVC/pMmlShqsJIdch/Dd71IpBsB9anPooErjyr9808rzUI0qgrqt8Kng+cl8GAYscCYwUAUA

DcbG3Qakjg1gDtAO0FBwDtBQSA7WpI3Qjjs4b0zy/BV3jzpW3PK78rEGEA6wJjAOiA6C3S1jB3NRpLfzJ/Li8tfQtaYf8y/AKYAdSAoAXyApgGKPTXKkMxGlQpVxpUN1FV1/nLu0C4M8ZjZDAGMGEKzgtnwMTnDwRLYVfj6EptUt9pqzJNDd9q7wi4rS7InTcuyXcrnK63z3csNK2ZUeACwqm/b58r2pCZj5ZIJmWDCPfOggcPMFw30Or/aQSqkz

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

A6GEIeOh96beYf5Cc6HmZ0uhxwFroewASuG7obCsUWGvIZ8h2KGPzFlhve5goe+h36GdIeVhgGHooaoh9WG6gRhhpYCuId1h7Bwx4dBhmN9YYfhhrKGkYZyhoaG0YfvOBrFMYeqhyzkLYathwx0bYecoO2HNruZde0hyYcuhlSHrzjUh+OGXofphnSG9If3B1OHqpDZh5OHfYa5h/kJM4Zrhl8GB4AFh5yHhYZzh0gVPIeehiWHXofa8d6HAoc+h

vuGFYaVh2Sxh4aBh/WGtYZIXLKGoYbHhg2H0fwyhk+Al4dNhleHUAB3hgqGCYaKhomHD4e+h8qH14cMdF2HsYYkRd2GS4aah8TExVNah68H2oeUh6H04TzJsng0EcNjBgQ0qfr727HQvIEkAXyBfEHxgAQJUHt3TPeMGoU0+Y5gm8PfQPMG36Or4UMQIkJXYJZqOoTzkGwjNn386kvgIaxRci+zSxHrB/fazfON3BX6mHtbBrAq+/vqOgf6SYw1+

0byDqn2peAwopke0ShtCpNqE8cHv9snBjJ6ISp3AQTyz0ylgOcGIAAXBwy7BoYchF4lCCVMDAFAQSTBJXPFrbUsdJER9IRzROobN5rWFCvES0TdpLJ128RMJTvF37XMJf61bnSG9UdEQTVntbe1h7WmdaJ1rnSXxQZ1V8TDhBZ1RnQ3tJwNB7TntV/ECkaAFVq02nQ6tDp1l7X/xcpH17TlNSdFJnVqRtZ16kaKRz+1BnT/xNfFVrQQxSpG1/A6F

OAlSWWIxaMDs8XQJOGcaMToxJixbEWxpW0hgvVIJcy11EQoJXOAqCSPhWwkWCUkxdgln4QDbazE5MTRABTENCS78UrFBCW+h0aQ60QyQcv4s0xixNpB5vlftNtE0QAhBOQkaCWOR1QkSEWGB85GuUEcsZzE7CSSRou1vrQaRm51BnTYQN5GJwTERJLE3CRSxDREoUYg296aCsTMRe9LwiTylPBF9EUAAecV9hGnO2rsikADVBgMQSX1VKdE00U0t

PSFQYWzRCOFc0SkhWJHy8XTOXi4q8WExYFGaYVSRswk/rV7tPvFrCSyRuEEOkZ3xGpGsxsPxG9EwUeKR2Z1Skd3RI60Kkb5R3JGVnW6Rga1ekbSRjlH2nS5Ry/E4MTaRr9Fv+W6dLpHBUffxPpGMkYGRtVHhkcAJE+0UYfQxZuFMglbhcZGkppwxVicGJw+hWZHUf3mR+QlFkZwJbUVUhnKiDoE54Q1OquGVJQs1SwEckG9Ro7FN4WVFeoAuyB36

m4AIFt62jT1IFuCDNINn0SlG0NHhXVxAPjED4U8JZQAA0a7IdTFZwm9Rm0JAADPlBhhyoh1BXS8SaT0hotHSiHqAfQBewkJSdMAfV32QdNHvUbYQUor6gFnNGqHihSZhkgk6d24xcyTeMUoJVNGdkZhRvZG2CUfhDgkX4VkxMYkzkaUxC5GVMTqBQFGjCWydb60i0bXtMzExEQxBKBE34BxBe5HvUfKiFQk+TrUJX5HJ0f+RrQkhCS+5UaQt0fAy

HEFdWHL+DzFqCjgASG0fMXnRpSURUf6R2Z0f7Slez5HMuWSxDwkNERwJHUQK0YsCYUQpPN+4WtHF0f9R71H+XGuBYQdE0brRjNHKYeMRIIkT0vRR7e78UYMgMQZA1SCRrwMgvgoxamFVgWS9UlG88VsDKJHqUZiR1Lb6UbPOBJH70eSR7602Ud+tHu1lUasJIdEeUaBBaVHprT3xOVH5rWFRvVHOUfoxrdFDUclR2jFRkfHRGe0WMd6dOa0hUbnx

dlHaMaaRlVGWkaGRvjGNUZyR4TGKrR2tQpHFUckxgG0X0UGRspGjUe2ddoU8MU6Fe1abUemR+1GR4SwJejElkbdpDEFa8Wxhf1AvUa7IVuE/UfrRrsgWrXKpLtHw4jDR8uF5CQjRrubo0ajRiv1M7ArR6UHiAETRyJwU0ZrRjRFHMdgxizGVwSaUDGF34FnCY6Qi0eWRotGBLArRqtGgGFrRiLHG0fveZtH+iFbRvSGO0eDR8gl7gVCxgTF0RAHR

6zFWCSkxEdGjkaREd+Fx0d4JP5GE6WnRo9HrkcQhaN47kczTOtEmkAoxkFGlJQ+RtrHEwHfRw4QbMV3Rn5GyEScxbQkgUZeRnJ1VMcaR9THuUZAx8rGP0bhRr9HGwR/Rvb19AH/Ro4hq0aC+I6c8ISA+thAIsfAxtgBIMbDRo7G5HECJQrE0UYmFPFHUAE6LV9UiUazxe1GR2DfQQL48MfCRkGEs0SLxGlG+gTpRqul4kaZRqbHLnRSRicEn0f1R

l9HGMZF2qpGhMZ6dJTHd7Q4x2bHwUbFR3jG17TGdBTHYcZ3tOpG6eTBxrjGC4SvxWTGl0YExya0JnQFRvp15UexxzjG6MYLhTTGJUbXtHTGSaStR8LapkfjArvxKMQwJJ1HsCX5cCTEh0exsQ5Gx0bsxCdHf4QEJGdHJsZwxBzGYMecxwrG8cncxta1j4R8x3TT5cZpbCKbDhACx/oGgsa7IELHe0bCxxsFzsaSxqV6UscrR7bH0sb2xzLHa4Ym+

HLGDLALRNtHiCXXhTtGyCW7RzZHB+1KxobGNhBGx4hF7MX3RibHj0fExZ+GYId99aaHDwdmh/lwWUbbREDGPMZdxiJB74cMh1Rh5HA6hlls50coxx9HKcakx7jHCZsWxmqHP0Y2RtLF+XD/RjgAAMZ2x4DG30dAxzNHHcVOx+4FdcfyxeDHrsfMx/E1ZJpTxHqHvEb6hmOHukD1OP5FF4XQxkJHUUT+hMlGCMcpR77HiMe1WiLEAcdusGDkE8d6x

pNlqMdPxJHHmkcJmgIMocYHgZZ1WMZ1RlTGJMbmxr+1xUZGdfjHmMYxx/JGekYpxxHHRUZnx/HGtMbkxonHF8ZEx5TGFUdXx6fHpMdgxVpHtMaJxhIV9cnE5SZHDMZZxmZGTMbHhZ1GJhSgJPSHEUdtxqXGs8YO6rXHncd2RirH9keHRvnGuCQFxhrGD0aax4XGWscs5G5H6/BbQdJB7kekRQNyYkGeR4HHvrURRwnGI8cshwhFRsY9x8bHNCVnR

nrG37Wvxw/Hb8chRiEElscOETPHPCURR/lxLsdRR3lLrEXlpbRFMUcfAHFGkMcZeglHbVTQxzPE3PiwxklGwkYsdT7HC8WiRjeaSMf+xhlH4YRHxrREQ8ZBx4Pqccapx/vE58e3x7VGycfYx8TGaMbXxkpGUcY3xM/HqkbyRxnaxMePxKgnn0aPxowm5CS0J0nHRMd1Rg/HrCdvxmnHN8e2dbUUzUawxC1HROT0xiZGLWTfxn58sMc/xipHOceAJ

d1HwMk9RtCxvUfsxy7Vi8d6Ra4FACagx74EvMZjRyNGFcb8x39H40ZVjYLHk0ZAJtNGYMazRmcIc0fzRlrVwMkSxnDFS0ale8tHDccAx4WAMsZgxrLHzcZbRq3H8sYAJ1zHPCRKx6gkwCdqxyrGDkc4JGhH6sdIJqdGECdnRyQkvrSUlMPHZcYUJVdGdMXXRjrGbQjPR9+Ad0fdx9Qk4CfEsRAmT0aWJ+Yn0kEvRsv5r0aBhO9Gx8coJ/Qmb8dTx

19GDsZ6J5GFGCe/RnPHNsbzxo3GgMb2xkDGK8bFtMvHoMbAxi7GUUfDSxDHq5qwnAQmhCYTRJ7HkUWwx++H3sYkJgvEwYSIxmQnB8avOYfGUbFHx8YmH0Ynx0HHk8fmxhjHNCc1RknGzCbYxiwm88SsJ8HGZ8Y3xgAk0cfKJUwnZUeXxq/HTieoJ1PHj8dpxovF5MbJJmHHtCccJlfHqSZcJ1PG3Ca2dR/HGcYMxqAlbUf2XYzGqMQ5xszHXUZRh

0aQrMZxhd+BbMZ9Rtfxxce9RyXHXMeSJ4+05cfSJmltvMcyJjbHAsdyJw018ifCxwomdCRix0NA4sZnCBLGpXr1xoD6DcbSxp4mV/w+JrsgmiYdIC3G8sfbR9on7caAJron+0a5xvonICYGJ45Ghib4JEYmkEU2J8UmBse5QBYmusYoJjvFpifTx2TFvkZIJgMnD0fIJ44mrnWcJwkmaCdDJggmIsRuJtbG7ia2xuoma0eeJovHXiZZRE7G1ESgx

4smRfW+JhDGbsZbx6857sanzR7GRCdZxmAAXsZgAN7HxCfJRyJG+8ekJlLbYSdhheQni0UBxxJHpsaox1EnUydxxjQmEHWyRpkmtUYcJy/H98YJJicmYMWJJtpHSSaDFZkm5yfhxvQmp8ZpJvHHbCcWdLEmckRZJ+cmEccXJ9Qnf8X3JkZHmkV5J1/H+SaMxkEmQif4xsInr4W9J3nHfSdqxk5HBcf4JIMmxiZJpeUmnMa6FJImZcbvxVUmNSY1J

5XG+/WyJ9XGk0d1JrZG+0Z1xg0mLSaMBK0nHifqJk3HGibNxx0mWibWFa3H2MVdJ9ZHOib1JwTEriddxognVic9xsgnRcesxX3Hrwf9xlmG04aDxuRxlCYXRovHw8ZIpyPGDIcPBmPHfYfjxpEnE8aTZNQmU8cBtGMm1hWzJ7PG40bzJgvHCycuJismsSVLJuGByycQpyvGrsfYJ34n8TXXQgOG0bozyhor0DthBsP6Wis8RyOHG8ejhgaHW8cxx

RsnMMebJ0JHu8fwx1+HCMZjBAfGC0XhJpi4lCZHJvrGxybPJoSnJyey9XlHDyc6RzcmscdPJ9km0ydTxlcmjUbXJyxlZyZxJykmFyeCppcnVUfvx0/H7CeipnQm8ScEp9EmD7UvJ41Hryb8J61G7yffxoUn2cdMxl1HmkT/x1ZG7cYIpntG4Ke1xsrGvSYgJt8nR0egJz+FYCaFxn8mqKdIFZAnUCfQJgglMCeiQbAmJiaTZPAmGSc8xrnGyKbsx

NYmvcdcpnAmk8fHJ88mGMaGp+gmNhDEp/ZBmCa+JqvHVKc4JvU5uCd4Jv4nkMcJRjvHgSaTRbDGDIHBJzsmjkW7J6EneyacpgcnK8UUJ5lG3KZRJ1Qm0ScyRzEn0cePJrcnLCbipuameMcSp1HGTCY3JlKnWSapJncmOSb3J36nhqeSpiknUqacJzymMqbvxgnGU/RNRitkvCcgJBnHcqaZxwIm2J2CJ4UniqYmFN1H0kA9RwEEZSdiJ3ix4iaDR

pUngKYmBRXHqac1JlXGoKZ1Jj0mEKc+Jr7ls0a7IPNGC0fKJ80nKiaZhstHUsdQpgsnbSdNxptHsKdghXCm14U4xCqnlRUIp6qnQCcWpiJBucaqxqAnBiZgJ4Yn/keax38nDhGYpyYnWKemJldGVwTXRjdHM022JlYnxqYopi5Hgye1FU9GuyHKiC9GdWCvRphEb0aOJvinx8Z+tEGmQqeEpovG5abLRZan1sbppySnjcdtJl4mlKbeJssmzseDp

gIkqyerxnAlbsf1VVDGLKbQJOEgwSY7J3vGvsZ7J2lHZCcy5ZynESZh+B6mGBvSpl6mpyd8pt6mAqb3xoKm3afipn6mEaantYunAaZPJ7cmP7Xdpl9E6Sc3xxkn1yaipqGmgadip8unvqfhpk/G6cZ5J9Gm+SZJpAUm0CUfJhZG8afFJyUmbMeiJuzGxcbiJiLHFSbdJ5UmRkdAptInwKbNWrIntSY1xvImZaYKJ5mmosdQAUaQjSaYQE0mzSaA+

pCmVeT5p/MndscFpjCnhadyx1omXSYlpwAnpaadx7omvae5h18npMUap5WnmqdVp+Am2qe9xitlxpGSx8MmUCZHgbrHkyZUJ9e0LiaMBTMna4bjJianKKe9xyMmZsdhpzJGRKdghH2ncyYeJ6+nC8Zkp8On+cXkptzHy8cIZ5FH1qa7Sjgma8drJu7GHsYOppsmZkdbJ9smbKY+xyEmqUYcpmEnrqbIxocnUGdHJp6nZqa8p7lHXqZnJ7EmO6brp

z6nu6cEZ8e0sqYipsnkAabEZj6n8Sa+pqRmZMb7piGm/Kf5R2unFGfzpg1HwaY8xnKmYCRfxgIn8qaCJ5smx6e/x8zHwCZ5x7+maseGxz8mWqe/Jq5He4X/JuyHEiYpp+4F+sdSJ3zH16boDTem1cYZpoinSGf3p3/Geaf1xj8wr6akp2+mG0cwpoIAnScfpm3Hn6Y6Jqqm36c9J2MniCaQZ82mNaddxminekSjxwPHjwaYp3OmpiZXp9imB4DyZ

1mHuKbjxjLlNadzpnRmIccwZqulsGYkp3BnImfCAfbG4GfiJ47H3idkpkBlI6Y2pmvGYwa5+ZHCKDpceRIBJIAoAHYB/nl8gC9jYjtz+8V5SPjKombyYa3MTC6RtmOHaoWzgATCPOB5swHtwDDyEnIJeW2Sm/o6jYZ9tEdl+yLqGHv0R3UrmHo8K4xHwnsS6/oil/NfdGnUJFFSo3HZyXIMOiEB0Tl+wEKTgSvSehf7t8v/2m1DWa3KAFIF6IWTB

QwFILBdBNiE3QXaZgiF9QW9BHiETQTIhASFYgTkhGiEjYFBZ+PkGIUhZliEcIXyBD0FCIRKBX0ESIUqBfiEgwRDBB0EpLH0haMFi8SkhBiEkwWtBQwFUwRIx5wNovWUDSCx9IRJBUohX8Y8DGsFF/UqDHgNWwReBTHFfvUaDXyFmgyHBeEFvISaDIF0AoW6DWNGvWiYypVnNckxZiwE0WbIAHFnSAGwhV0FcISLRriEEWeJZ3iFSWcDBCiEKWcZZ

sgApLFVZ6SEYIShZ9iECgX1ZoiFDWaRZslnTWaEhSlmOWb7xmlmfsetZxMF1Wf7gBSEy8VZZif0pRU5ZuKEPuV5Zj8wKgxyWwVmMvX4JlDHBCdFZgH18rRaDaVnxWdlZzoMRvR6DM1bFWZzZ5Vm82ZVZu0EwWfNZ7ZlbWZhZvVnCWd8BJ1m+IRNZ2oEqIVVBS1nC2axZh0FNWe1Z6FncIQJZ+FnHWf8BElmAwXIhWtnhIUgsK1nYHA3CwEEW2dYh

O1n9IG5hB1miWe7Zo1ne2ZRZuoFh2a7G6lnxIW9Z+lm/WfGBfZBRIROQRywl2bhBFlmlAza9UNm2g2tRiNnbHBe9AVnqgyFZuNnUMcTZ3f1AfUlZxiwQfSG9OVmT/ToDXNmP2fzZpVmrWb9Zsdm8WbcBctnO2ZnZsoE52eRZ8lm3WeLZhtmUISbZgYFJQVLZ9tnOIQrZn0FZ2edZmtnBITrZsMEh2aytDoE/2Z1Z/IFJ2cBBadnK2ZQ56tm+2fQ5

vdm5ZpXZtOn4wQdBBlnqITGBagAt2cpRndmGLAo5sIJA2cPZj7lj2eC9Hlm1Az5Zi9no2avZ2Nn6ycWUO9mZWcHxFNnn2Y6DNoMpWbfZgyBSLGeUH9nwWY1Zo2B4Oe1BKV6iOeQ5kDnUObI51FnlOfEmjFnG2bVZ5tnVOdxZvDmOIUKBIDniOe050jmF2Yw5xoEOACo5y6m6Wdo5jdmA2cgsINnXAw9Zr7GuWd45+f1yg35ZwTnIA2vZtvHuwQID

MVng+uTZx9m6gSk5hB1X2aMDd9mv2c/Z7pAlOeLZ3Dm22fU5oD7NOcRZ2znwObrZm0FB2aM5n1nGITU5iznsuarZ41ndOYg5kYEwwSc5jhm80XXZ/TnmWY45vIN2WaNgbjn7fSlFM9mo2ZV2mNmBvRvZhNnwuaTZiVmcvRi5wyES/Xi5rNnEueS5pLnZuZS5ornf2dM5rVnx2bLZjTmkOZy5yrm7Ob9ZqDm6IRg5mrm4ObM5jLmyufW5irn52by5

gdnDOeg5iwEKOfS5idmegCnZk7mSOc25vLm2Oe85wvEvWbqGxrni2c3Z7dnd2ew5/dmWuZcDfIN2ub7xvcEMae65wLneuaE5/rnY6fwYG5QxObTZiTnoudTZyLm4uYzZoIM/MZm5rHmv2dS5+jmS2cO5u1nAOa9BLtmbOee511n8ufRZ1ssFuZM54kaCeZhZjtnieeA5v0Eyef7Z91nLud2567n/uYRh2nnluf/Z/ZACOb5AcrmnubO58nnXuZB5

r7GPuchhL7m8eZ+55jm/uaYADyED2da5o9nQebDZgzGIeYE5qHngueE519UEedR5oF1JOfG5l9n0eflZsb1wQY28qz7UDp0pxG990Kxu8OGk3Nx51UFbudW5rLnHudJ5kXnLQW25wrmrueK553mEOcs5xnnrOeZ5j3n0OYu5xznPWdXZz7nXOaa59zn7js45kNnVebaDblmAiY154khLiWX9bXn+udC5vXm9/WR52Ln02Zk5zNmFWbm5kvnHeYwh

JbnW2cJ5tbmrOa054PmwOfJ5r3n2eftBWDmSubp5/3mhefd5+vnWeZb5qlmI+eo54rm6OdVBZrmPOfj5isEOudJBLrm+OcjZyHmEcT65tf0BuduUHPmH2dG5lHmJuZN5uTnvXGx5rfm82bL5iFmK+ZW53Vnq+cD52vme2a750Pn9OZ255vn9udb53nnzOftZt3m6+ZdZ7vnr+cv51CEbuf35vnmBeY75x/m0OcYsMXnw+Yl5yPmpeej577nGOd+5

1jmuefY5kfnlea45xPmeOZT5qfnz2bT5pf0qg0z5+fnYefh5obn72ai5lfn8+bB9dfmEufk5+PHt+ZIFqnmfecW5nnnK+Zd5owFv+dP5p/nz+cg573mOed95j/m7+YZ57iFTubP5s1mX+aYF1IF3+coFg/n8Ofu5wjmH+boF3/nF2cgFt7nWgSAFhrmQBZl5sAW5eYgFhXmAeegFoHm2uYAFwvEwefV5xAWeudn56Hn5+ZE5hZQl+ZwFgwMxubaD

NfnC+Yx5qH1BmYQQ2QqdLgdQxIAZ5HcgGoBsAAMQUpFUHqDzWd1C+Jp8QV4ycL9q4fitlRU1RkTPOpwYuzYYCrEO7tM5gCOZ4o7TmbH8xsGB3MYeq5nDEdP2+LqTEenVeyTxz3YLb81JXKf21vyNNRGY3I4V7L6O8xD/mb/2qw6gWY3PdAAwmgbxbZoxMRzlVAA2EUjsYdA9TjEGNAB8Bni1UfN8LEw9fQB1HnreXVgxBlHzJ2I8EUgZidGsIAZA

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

wQ3nuRT1uPXQxgT1iPWYfmT17WXU9ZHQdPXTykIMMbWvKgm17pAptaYcGbXF3Hm11dxFtZL159X6tZW1tQ3X1fW11R1yLHv1+vXtwUb1g7Wh9ejeJfXt9a5QTvX7DeX1lXlj7H71pw2KDfLF97WpXs+1pEQJ9d+16fXoDeosWfW56Xn1jYRF9fINmHWtvDh1tfXrDYNRTfW3DecNhOld9fju3oVsdaP11Q2/ADx1ryEz9eJ18wEkDcS5lHEKdZ6H

O/W69dp1+nXu4UZ11bX9BVf1s2AIDbFhKA2DEBgN7/Xf9a11//XBWUANkTxgDf+R0A3cNrl13soP9c6GlXW1dfvADXXhdcPmlA2FbTQNphHU2wM60g7pCpT+mB6XHgKIO2hxmZnyRIA7q2elgkWSdHJ8YYxV5AXDdPjAG3Kay0x11V3jLT5E7Lf2i4Ml6PgMFjUxfsx6cGWnVchlpzDkCroewSqPVedyr1XrmbEq1IXhRfSFo2zHmaVw0rNeJB7u

bu5O8spV8ghi6Mhk4oW6CtJlyw7AtYqFwA6JAHEiDm9+iFURFXKinHsWPEIGlEoQJ+Q6ZR/Ohhh14DfkQAAAo0AAenNVBiwYOUJWKQfqbmIghkAAMATAAEQVeOAY/EiCe8BSYjFmf0JC/Gz8MiJa4HNYJ+BlMlL8TTIVQh9GnMItYD/CN+RAAGi5dPAf4C1YZ5t2chlNwABQZUAAG6N9YAWQQ0IzmnlNlMITIkUQEeBAAAqFYuB1rE08LsBVkB/g

dE2RKVRAfQAyNjsSGhglZfHAE03cNIdN05wZKi/AAjTNqzYCR02yEjpDW1BS8iijIasvywMgWT0uPS9RGEh4etkCOkM9y1pKf02pLJHZYM2SkD2BccBwzflA2QJ/3N9N3c6L8AQqT9kTZaEVnSo0zYjfNbJuIG4g0ktNL1Gvay8yEnzNwuWYfqCqSvJ/bxmvD686LzzNgL8LTcxN603sTe8of28+ABjvBqsv5BrgMYBS/Dj8ZoRFNEAANlMOGD+i

PRBJ0M2PNE2SAEtNrE3CDBxNvE2CTY4VIk36GBJN1+QKTapNmk2bZjpNrmJGTZZNtk2OTa5No2AeTb5NmuABTaFNkU2xTezCCU3pTdlN7U2iKgbiZU21Tb1gDU2DQi1NhU3BTeMiPU3DTeNN05wzTZbNq02bTaXCO03x5d/N3mwnTa9Nym83Tfoij03kBEgtnSofTdkSMOIYzZBLSQJ4zdDNpM3NqG9NihJ6MhloWM3uBXQtxM3kzarlis2AvxEi

AkhMzbXsbM2tq3BvVM2Av1nKIs2xFJ4y1i9r0QbNui3bUCrNrK1izbrNss3Y7yLyfM2ALbnNvwB7FitvLs2GzYiQXs3+zcHNkc2xzbfkCc3EFfOwkDXg4ZpW6/L9KfhB+qhpzYxNwC32zdIAXE38TeiYQk3iTbJNyk3qTaZCWk376npNvGJmTdZN9k3OTe5NgvxeTaD0fk3PzbL8S828YnFNyU3X5BlNuU2FTYfNp831Tc1Nw6RtTc/N782jTedN

3mx/zZnN1s2gLZAtjEz4Ei9Ns7d4LZNvaC2rtyStjwKFAj9NvC3ULaDNySAQzaItrC2i8kjNj1cCIiyt2VI0LdythM2ciEwtv8gSLf4tsi2MzfEiai3s715vJxZ6LcLN1GImLcEvFi3eLcbN5ctKzdgV6s3uLddvNi9uzfYt0C8tLaEtgnwOzeGtsS3RLwktvs2BzaHNgwxRzfHN3RA70JGksn62EaGZmTD7BcF8r8BESBC0Ij13ICZ+6CM9jbJ8

OTXKfDH6DntoCyQEos8sdjsIxwRAVbdUaU8siNN7U3h6/tURzzSjNci7EzW2/t1kj43zNa+NsfKe/puZ/42/VYH++uzHNbLQ03hODzhDBJ78pL3K6x63mOHguE2/Nd/2+NWv2Kbo6giTn3rx1S7VzHHcPBxNzEmaJlbSHDUmuNEVLv7cKcwePC5AF6EjdaDZ/ZA5QA6ZSLXZYC8gea7dNPFsBoUGaRFZE02d2fX5R9aovS6ZEoU2EBJ1xKHX/Qjf

BCpBLbbN+c3vKFWAI2A9IaZSkewinAtcIMY2MTJ9Fy6vbqlO6qX2bFZt3PqObY8sfjlubdOcf14KAFhCcJlxIiXBSQBqpb4l6qWnkmtO30WQde1tk23MiDNthCporTXlHW32bfNUg22pPB5tvw2gPvH66qWj8QDeU228mXEifFxg7edt0O2Fxcx15aBlJfhBTS3Zzalt4S3eYTI2s1be7B3MRm2uxUi1sy6GkX2QdW3Hbpsu3dH5To9u1y7pTo8u

ou2/bomsdyAVTuIQg07grpvObJBCABjuqK7SiQVt01xQHEnO1AAZJqnQkm3cHCHMIm2iTpXMdlbh3BJt6m3yWXJt9ZA51Yeg+m3M7bN1lm22bYdNr23GhUNt3mxebYIlfm31gUFttjFhbaKN0W2f+AR9BO3orZ0trmA5baZhtu2lbZcsFW2SiDVth27JTpFSrW2ELA9txe3ObYOZE03jbZDt57lzbeFBS23j5ett4+Xbbch1kD5w7adtky0o7bXs

N23s5SftvW26aWXtn23TnBH19WkPtZ/trRWg7ZAdl2217GAdj+3ExWUlmO2sgDjt5XWJbait7S3pbcJmnLa07a0N+dBZ7eztm27x8ECsfO277d5OuU6BTpLtjW23LsfG3277LtGsau3/LtrtsO7DQDYQHcwm7Y1OyK7jTtbtiDpa0Hbtm2xO7bP9Qk1aiqA1iNMlLceFlS3Q4aGXdBXW3FTxfG2u3AHtim37oWHt8m3R7aXcWm2p7b6kGe2mbZdA

FJEoHaXtrm24HdXtvO317cEsAW2CLCFtyhJd7bHMMW3D7eId5O3+4FltxmHV4XPt6jwHLBKFG+3PboLt++3j5e1the3oHe9t46w37Yjt0B3P7YQqC22rbcqlm23WwTttoB283Did9B2jvAgdsOVLHZftle3obAQd2jAkHcDt2agsnbAdo7xMHcjthJ217ABmjI28HYXF+O3CHYmtpO2prdIdzobeg3Ttyh2zHZV2W266Hdvtp26K7bbBeh3vbvYd

4Z2W1u4dlyHeHc1O8O6G7fkcZu3RHZE5fx2/AGVtju2TTVtQeY370JIO3R6Kfo4RtEWuEcPJME5R2UbIPkBIbcpQuezSfCUYsMQd2Dpc+cQVmZ3YLwXexJEcn906cNV834TGSNGlYyYdfM5w/I4z7PSQvp93jeoehwr/rY7+z42u/oVQ343BReRlySqOHvwbKG2Jej40RAsbSvDV9p9KGz/NZE52kOGVlxH3Sq0qoLXoHPnuS3C4yuXuE7B941B7

c4dxti6jOGBt7n62S44bjmTEcbZ9OBOAHgJcjlV6Kx49Ks+OchyHHgjwq5WHUKcFnSgCiDRAB80ZNY3IHn7kHnrQmhsA0IaffKAntCjoMNCdgp9oaMNwzTxecQ7njcRVv63i7LBdwG2IXYwK5IXe/rBtuzXCHOBNhjy21GvoUGM72N1HIqSLuDkkGnwT4DjVsmXGCopl8oAVGlC6B+ooujQAWLpPGmeUF13skDdd5xoPXY8aL0A3DswN5BWVHtt5

tBXRCrEwn13BOnddpSpA3YCV87ygldGKw8kd7AqAegB4ADFO8XyA7lNUZeQbnZYkXFqsWL53D/i9uFoEQvjESIEOrnV3nZioz52kC0MNH52T7L+dozWgXdKV7diAnrkO2e9vjct86zXalZhdypy0UAAHLh6Dqkic+dyNJMRtvejPsFVc+13ETdN+n9ipHtD82By69xJd8oAz7lT7SRJiCk4ECzhiYHs/JAhiCkICEIAxtlTkQgJjPySgbfx8h3Zd

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

sDuNW5AxU9v9oHPbituATRvb1QU728vby3GTA0LLtoEbYVLyXIetHUSRPq1Yimxb/R0uW4HgIx0VLVTVjsnSh+N1yjl82/bLutvyh6Pb0tum2UTefQFoO/XxNM5MBG9REVkckAtsYdvsWVaH08uiy6fb441uW+tLzFv1JV3b420P2/Tbko1M24IFN8v3Jv/b/lkC247L8Vv624qHqVum28KBi9uETSvb1DvFW9g7+9uZh8Pb0ZvwO6PxZDv0O91b

tDvGy8W6ztvih7pb7tve28Ze1duTW/w74/wu258dQO0OAFyAcq1jnEkhdoe/oVLyAjvofCI72vGe7bSHxduMh6Rbldvsh6m6jdv8h+vLnducW5zb+DuXh7mH4EfZqGqH0NvPh4xNRE0fh5pbmEf9TW7bhlvIiVWxarEOh9EiLofN296H+keBh/OH5g2ciRGHhdWxh8ZHqCx7h8A78R1CXRA7inkWR8qHhYfJDCWHnke/7FWHsOwSTCk8TYeCR8Lc

IkehR8DRM8vZXpZbo4ery/KRG8vGh+rLl9vay6fL+svrh/KNB413y7zbtsvlbWA7/1v1W7eHiDutW7qHyNvH1r+H5ofRy+ZHoEftR5BH5tuwR+WH9tv0O9PhLDuB24m+s1uqR/+QcCvUR4WJZ7EViSLATEfArWxHs1vRR7DiM0f0mlXLxzvQ3ZhBrT2G+/c79R3DS8db0+2b66yH7DvqR9lHvIfPW5OH2kwih6dHyyWlR4Pb+U0Yx6DHk9uoyBDb

2oeoO/1H8Me+R5rblofq5raH+JI8R7FHmkfPW9mtPoekBbHShhuOx/NtUYeWGeKJAce/259Hz8vHh4BHocfxy/mHo/FFh/FBRMeDR8vXI0eNh62H61vVy8tH61lrR/SNW0eAUlfb7sfmTR9b+0u027dHjNv+W+9HyYffR9Fb/0eEO9jL+o0D3tye8t7OR8NNbkf6h5g7mceBR5VbpkfZh+HHwNu4x4+HlDvEJ5lNZMfoR77H/kfMx4BQXDu2x6zH

lEfkJ7RH/MfOAELHzYlix77b0seQ8HLHvxFUK7Ol32PNrYE1xN3Aa4TB8YN9ACWAKAPlEx4qpjvyDzMHofuemLReeF5CpORrtAsTC6et5fp1uNqE4sloc3CK4ovsu5rBl42Xm80LiTv/B91dkruva737gBPJoyFjpeRSxgbVCHPl1QMfGGPp6oyorTuYfcz7pIfsnuTgbq594EuTvJZpImSCXEe74VEiVABZQh6UQABngz6UHYJryg32KAeelDeL

lvvllEAAc79bmy4aEQxAAC8Mt2IxBn3iDca9pGLgDca70hoYK8J/wjvCeOA9FgPgTOvnlCcng+BXJ56UdyeER8Ynq8hfJ+6UAKegp72Qagewp9RLtBgIp6NgaKfYp55uBKfmhCSnveIUp+YYNKfQUAynrKe/whynvKf94AKnuxvq+5njxxvw0+/TfcuQmCKnlyeI4DcntBgPJ8XHryew4h8nwaJ/J8Cn7YJgp/qn7pRwp9kHqKeYp+BQeKfEp/wY

ZKfQUFSn9KfGhEynhIJsp9vCXKfdFnyngJvNB+wrm6XBfJqAVaIKgBgAakAhJ5MH2fdRJ+/DKvgSRa8zwxQTyJo+fmBD9NC9y6P0Fn0w1KiLcEN9ptVcOEebzBznm7N91wPHcp0nrCO9J6j7gyfks7MRkSuy0NmqAOgk+9CwjzWMlDgMawubC+Zr0EqEc/Hg5IeFM49khdv+oePLz9v60c9EdIkoWn0AZWkXHD0h1se0x5yHlcekiS3bukfCh7OH

koeDx7KHwEfzx9ZHpYhE3iUSRnkwx4ChtYfjR+OsU0fhQQBFjcbzEmEbvpRBp7vCNhApiwgYQABCa3BUMFBRzjksdmfwkS5n5WltABT1w4anRX8dEUlDxt2F0cB3yCvwRyxLZ85n3YWjTRzp0XhZhEPNfohuITiBANGOZ7uoa2fiZuQ9fFxOPDccaNvpR+sKYxBStrh2p2f3cHCRXJFYO7jnv6Rv0XTnu6hfIjypsA3GW8sNzyfOh6Fn7R0KrXXH

o21nR9NtOUfuh4KJf6E88XGHlUeRW6A79UeAx8Q7qCeiOkkMBWeiNhWHu8f1h5NHx8fCO+fHqAVKOSLnrgNxR7g1tcepR5znwYezYGGHmufTHTJRhuejx+Fbr8uxW6lns8eCW9jH2ah5Z6vg7uf8rENHvue1Z4Hnwkeh55klQufVp7exkueeh8nnsWeK59ZNbcfjHQVHvce+2mAnrIUph79HlueIJ+Pb7efO593npWeD59Vnlax1Z4nOp8fWJ/nH

8+ffoTBJq+f9bRSJKefiSBTbuefN28VH1+fmiXfnsCfP5+jHmWet57ln3+engf/n3ufAF7TOY+fzR9Pnk8uoiWZb59u7R7fb38eLh4Anq4egJ7uH5eeAO6bntUfC2+eH9CesF5HH2agxBlB4QAAHz3BH34fkJ7g7vFvMF83nrheliG4aQAAYxUAAe9jAABD9ARekx8hH3o0CJ8zZOKViJ4zHsifGIScDHMeHLXRH2iftkXon8qelx7LHiifCJ4WR

XMeA7WonjEesR+uIXTScR9Wnhz1sx8onixffHQLHmJ1obHsXm2FAvicXsxf7LTzHjEp9F8ThdAMYSE8XySB74aXBPU5pIhb72LFGQgWQeD0tWG0QTxxP28w9cJEeZ41n9YX8GCtmH+AF5gQsVK12RADn8QgiIQYsFJf0iSq5SOfYNnCRVjZMfRFNfFwPS/rBUSJU55jhGhfM7HytVMf42UvAFT7XsTl64pfQ5+JIIelWrF59Pq0w7GQEflFDAjl6

wZfZrV00qoAv8Dk9ZT1xl5jR1qwCdezn+Be926gsU+E3HCR1hOfV58KSBCw+TRhx8AYQMXqXsOJwkX529MA8rTxRYZ0227/sUPyrtsCsWOfp58S5LZe7trK2ohmj5FTn+5eVl6sRWXEPl83HvOfBlqxEUBeR24QsTjxIl7QYJYBk4lXiUHhYsUEHg0JWGEAAQcjsl9cQTxw8l/9nmc1A54RZ4OeSl7Dn72eI59R9QJZv/Vg2ape7DFqXz50jl5Dw

LmfXZ/MAd2fMV96XsQBw5+F6uoEsV76X1CfcLjksTZeWF7cFYO0RGZyRA5em2TJX7oAKV9ZwZuHjIFOXnbxQ/MuXgBkbl8ZGi2eQ56tnnFeMgFtnxQ37Z9xFOpazLGuBZ2e0WiFX6lfPZ+xX7meWV7MsFFe1AAKXoOedV+JIele2wUjn4gbMXW2H1vkoLE48G1ecy4bHh1v0h7T1y4ebmVNXulf5V6h25seNgX5ntdu3W+gXlIJvx6/AXsfVF6sR

cYfW58gnt2Ed57wXq5eeawIXh8eIl4yXrWfl691nu6ehp9vCA2fyGGNn02fQUHNnwKwPV/VAL1fFV5a15VeOrPG2sW0NV8pX4VerIA9n2VevZ71X2tvOEXyXtFfCl5KBGle5V8bXi1eTZwtsaOe5LB+X1TzlV+eXpOeqXTeXjZaB19WFcolll9+XjGmr+oLnkeeHF+XHjsf557LnuBfNx+ENncen57rnkbEUF5gFNBfm57YX9efnjS1H8ReO56FA

Luf8F5VnxNeh28BXnYfwF4XXjoex58DX1dfb54znrceq5+UtFdfkF8YXkCfjx+mHtCfpZ7EXzCef5/PXv+e41+Vn+8f+5+Yni0fh56yFTyfL5+XXiUeb557HjcfVPI3Xx+fhZ+/XwVumF4eH/9eRF44XoDf47TPX4IAwN4AZABfr15AXweewF/nXuDfFx6gXxDeJ54NtNde0N9d1zdfMN+fnpeff15Xnk8eAN43ngNuiN5jXxWfwN/I3qDeb16o3

oFf71+FH/YebR8oXz8fjh4KHnI1325dHx8vsBXdHhhfsN6435hftl4wXgjf+N7jLnhf+F5vH6cffF+EXwcfj14wnojepF7kXhRe/7A7b4UE2l6RHnDuER+Innxew17RNPxfLF4CXrEeHnFCXtaemJ9MXtzfYR6onrzeix9sX8cBfN8cXgLfpjXc34LfQSECX6WFebF837xeot+WNWLe3F8CtYJfwt5LHsJfkvSTXmOImp9kHmJe4l+TiBJekl7dX

+uwdhdSXj2A8t7EGLJecl6gsQ1eoAGNXjFemV7EAMpe8V8kWSpfCV9/9Yle83DqXm4EGl42Wppe+R7l61peIx/aX4gCcYEP1zOwel6q34XqBl8xsoZfqwBGXohJxl8W3yZfiTBmX2oVsiHmXqNHFl4nX1ZeIkHWXtlfTcS2Xx4euV7bpqbFeV6PxflfFbbuoUVfzl8q2CVevvClXuwkY5+nXwdenl+V9Uzb1V5Tn8dePt8nX/qaAd4LpWdf/lvzc

W9fbV9l1qCxQV/BXyFfoV8NCeFfEV+RXimEW1/MABr6MV8LX81e2EHKX/Ff0fUCWIlecQBJXz8vbt8FXt2fjIDrX1rei167XxixKd59n83bArHZX7Tfipt2X9HHrt9moEneXZ61XkVe6xrOX8VfPvElXvFFbl4+J2leqd5tnu2etl/LX1VfTLF+3pCbOd7J32teO14bXunfVLEa35reil8x3r1fsd57Xra6HV+BX4UFdd+I7+0Dx283Lsv3FHamn

8DXnG/UengeDy9JHlmfw3rZn+tfdV7SXp1umYb9Xxzf2x4/XldevW/Fn/se/W6/ni8eQN5I32NeyN4TX0Teq4U1n0FBtZ/0ZPWfM19QAQ2eTZ5GUTZQzZ9ZXgtfHd7NX4tfxd4dniteSyarXrneFd413rtfg8ZR31Fe0d/RX9Xe0989X6neP/Sjn4UF3t6EXt9eh1++3x2fR17+38UaDt6+Xg9xgd8S5UHfcNpo35oki56XXz3ekN6Y319eHl8rn

oYfq56QXjjfJZ4mHt+fQJ4PXp4ej19BNE9fgN5wX0Dfg96+8ETej5+g30heNbUfXpLJx59XHkfeUN7vn99eJ98/Xqfft1/3H3dfakX3X1hfF941HkMVOF9X34jeL1+E30Pft97E3k+fqN5fH2pF4N6O8Q/fhZ8lH0ffPl/H32efJ993Hq/eX55/Xufe/14/nw9fH94bb7BfX99I3zfeP96AX4heKx5/32Df+97o33DHn1+APk/e31/Q3+Uf2N6gP

zjfYD+43vDezN+X3ize4y8E3vefbx6vXsPeTgoh32Nu9h4oXw4e5N/tHopFHR8C3s/f7y9dH1TfAJ/Q7ig/UF/n3+/fTx/M35/eiN4M3mzfjN/4P2ceox903wMeX96s3+RejN49H7k0Ux/G393fD0FIngWe4aFc36Legt5cXvRfvN/BsLLeGJ+MX/zeDkh0X/xe4t5sXy4grD6MXu+EuA2MP1LezD6sX+Le+PSS3o7wPD7ilNLeaJ/KtTLfQl/CX

9Jf8t+iXpkJit9K3hCxkl5F353eELABFurfXEFyX4vejV9bXoOfad9xXz/1Ot/SJKpeet8J3vrfSV4G345eht6nXkbfpiQQdBzfSAD77Tpeg7W6X7I/5t8zsCZfvsWGX0ZfqwDW3rtA+rSmXrbfZWU6PgZeFl5m39veJZ6O3pcENl9O3jlfuSQu3yKmrt7WvPlfSj5DwE5eed7FXi5f+d5e3wXfpV7uXrvf458Tn6XbVLBl3h+h3l52PzOeCPBGP

jQIe942Ea1e2D7138PfrzmkiWHeoV9wHxHeF5mR3v2eMj9L3ttffAUV3p3ecj9Y2Alf8d8KP0pPij+J3xY+BV7l3qlfyd5+P9Peq99m30pf9V+p2hnfJj6Z3rdbs97kZ7p02d6WIDnfNV/l3olIVj8e3jY5nt/XxV7e3aTccAvexd6VXiXfkzsOP8E+cT8hP/PeK99F3hE+etfSPprfMj4x3xk+sd+r3q1fj4awPiTeod9YP8Te71/xNc6XO9rI7

hgv2+92t/wj+k6qATgQwKy+84SfDpne2ExsyBDX6VkPdA/WVfPC5VRj/RTh6NRUEUGN1XIUch72Jc5E7t42i4/X7sJNN+4+7hGXAh9qLvGeQh/xjjcOYnumY+JR53McEGGPSNUo+aaPWu6jr+IOGZ85rzswz6mLgDGE62iaUeD06nvwQH2IFkEAAN7Tk4ijlZhAEl+xLgt6JACDPkM+P4DDP5OIIz6jP2M/4z7lN7RAkz6N3yXup4+l7gQq6++Z9

useFe5CYVM/Q0FDP+hhwz9uWSM/vYhjPuM/85QTP/M/Xp4o77Qef8xgACLQagDtoN9Q8T2VPzE5NqhNMaVyNT+Qannc1IxYEbYr6xgTgpJ5DNiSQilXPraLGb62ou1xrzV2tJ8K7q0+Oo5tP6Tugh/tPmUuXuzt7/7vRK5V6CAsOe3MLqSvbtGgIcEiRA+kzuwuYe5v7uFvDS6fkEe2NHfYAGUAQgH0AcN7tDdUYNW3bVoipdmxJAAipeNaYA1S9

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
```
%%