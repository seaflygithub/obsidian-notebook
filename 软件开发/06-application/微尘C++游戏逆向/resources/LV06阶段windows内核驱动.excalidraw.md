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

P0D75O53R8pXrwgA5xT5lNSXWDc35OvkhlT8IO0vQiD830f/EiCkilBnN/9QFNwAKGcnhBhnRIAoFPLU+iCS10Yght9RlJ603qtQALrXdt9RfxY0jTSfQMQ05tdcFL7fAhT6q07XeYhiFLcUiJ5pHgs4ZgJKFMvkjvtOtmHXSSDGFIy05hTgR1kgggD2FPFnThSl12Mg+gdeFI3XLSCBFMvXY99hFIPfMgcT10Mg8RShB2+049cxBzMg7gD1ihkU

42cSAFNnWyCdIJfLByD5FKcgzQd1FP0UtyDtFJgAtlS9FNcgl2CyBzv8IxSVAJMUxlStAMignQDooL0A6xSDAPiguxTpSwcU8wDgwOfkqwDz4gyg9JSSNyZ0lZJCgIBg6T9YlJhUhJTglNCUtmFDoNmUopSjlLiUhVSNe0ROdpSjNxGUtFS+q3iUiYdslNyUsJSClLNUwXSfN1iU+ZJCv37ASpTe/FQCWpSzR15AIXSmlI8/FpTMoC10ocgKVJtX

FXTkAj6UnFTEh0GUp4CJdKF01oDToImU/akwlJmU5FT/XwEKTcDFlP+UsoCZYFWUi3T3KFOA4tTtlKQIWdT9lJLOOdSmdKGIMpSzlIuUsFSIVMIQW5SxAhl0wLCNexgIJ5STxEoCQpS3lID063tPlKY/UEcEFN+UqFTAVNhU4FS49MkwBPT6lID06FSylNwAeFSpf3JUiJTKVKhU1oduvw17G+AcVOv8M3TjeEJUspSSVP2AslTu9Ob0nPTqVI0A

ohSo9LhkM2Cs31vkq1SGryxASW82VNQvDlT3VKe4z1TeVMlUv08/VO0vIVThFJcANfSeVJfuPlSt9JlUsi8Rfwjg4PSlVN2U6LdVVKLIdVTTb01U7VShB11U+g8V1zogxa9OL0tvbi9TVM6UiPTLVMgva1SdrztUva9xL3IlJ69dLxOvWS83VOG0j1TD9O9UqVSlLwDUkWAvtLf0m3IQ7xq0iRSI1PtHMKwSAi+AYdSyAh+vKy9/r2Mg6bT4L3Tv

Fmh01KzvTNTat3YXdGC61Kxg2gyG1JwMnAAp1NA0/Ay6IMRvJyghm2rUtgda1Pxg2b9C1OLOCPT2DPbU6u9pAFrveu8e1JEU029W70CAdu8g1Mb7IdTYUlHU/u9aBxlyS/SZ1Oq2bdSiYMhAy9TqQIr7N9T+YM3Um9T3v3Vgp9TolyvUgwzBF1e/DdTBQJ3U7cc91L/Uywy11OsM5kCPFzVgm79HDIsM/QyXDLZAqH9P1Je3QH92YIcM39TvDO7H

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

UgASpCPCmfct6FPC5IKJCmEsc4B1wo3C2fxfYyfCmcK8glyCHWF1ew1Ckl4QF3DQd4ArwpewbYBbwrBgecL6oDfC3hc5wriKRYAjwu6/GUCCh1yCEYAIIqCsuIpBgCPClzSJwvGkdgAfADkWfj14RDnAT0LCADBIE2A1ZDdgMEgfJ3xgM1oQlmrHbkhqIqwnCCxqIp4ABFJwgA7CpiK5e2oixsBTYFjyViLNQOosIcg+kXMCTaobQswAFTyTQqLC

h0KSAv3C8sK3QvFC1YQbvDbC2sKZApaC+QLsAEwAFeA3QGQAOXg0Ck9A6R5vQJ1hFCdTNyawYMKw1xzMtocFgF0iqX8WtO/ktrTf5OBkf+S9+0AU0DkYrOzXCGdhTKog0UyaIPFMhiDYFIjg5YdXHmAAqAC5TLm02jBfIs6M6UDG51VM/Gc1PPbXbUzttMQA5Yc5mH7XRZTaEwdA+hTR1xqM/EzTAgdAq0zIPyEHW0ySANXfFSCHTJ4Up0y+FNdM

30zD31KMpgDwzJ+01gC/tJ9MmHTKov9Mu98LIPB0uRTH/DDMwHTSAlUHD99ozMR0laAgbM0UkGzuosTMoDcMdKNAlHTeqxx05QCbByzMmkzNAPMUhD8CzOjnIsy4oPQ/RKCyB1MA7D8adIZMqsz4wP1LcTTBCk/8/ALFQuBC1AKP/PXeJYRgArO6ZgB8e3ACoNcnQugCvUKRgNvOeALjECQC1gKSQr/8lEyswqesLAKbUBwCzkL1grOi/JkSws04

MgKbflqHbAAqAu2EGgKJAvZAagAGAplyFELRgt88y4KVQswAbgLJIv4C0wKhAuhUmYDlgo9CmwKmgvrC5SL/QugIJQLzgBUCt0JjgpRi7kK0YtJC0ELMYoMC7GKTAsEC8wLBpC0sD4KdhHagGUKaYoJCumLTop5CkEKPApICLwLWYr8ChYLAguWCxELVgrCCs4KAiRBi5UKyQswAOILsQpKCvcKqtBSC5sLd8E5ChWKfPPGCvIKmYqKCiWLygr3/

Dvt3gDTAW7tagua5BoKpAqUiv0L2gp3eLoKEgpdXXoLmwGOQAYLaYvli4GLhYvRilWLpgoli+YLPIEqHBELppDli04LfYoZi5WKmYp2C12KcQs8gQ4KdYvlC/WLXAomCjGKbgtZih4K2mHPgaGK+HiOPd4LHcU+CxgImgxNOLo1jIpTiqOLDYr5CsELsADBi06YYQoWCsPsw4qRC3n0fYtRCpWL04pVi3Y51YtmC3EK/4WTivWKq4t5Cq4LyQp4A

euLP7mIeFYc0/wZCuSKmQulC+qBB4sJChULPoqVCruKmYoFC1mKRQqSgaWBOYqrCueLJQtUi2wK51IrioeKO4r9ixmLRYp2UNUKt4q1C06iZ1L1C5xADQtNgI0KRIvs88SKzPnjijWKnQotC/EKOQvzCt+L4vN7fUP9iwuxissLXQsrCtUQD4s9ChSK6wv+QMmKmws6snWLrxz/iMMLsFKaM0+TvjM1veML8IM5XZMLAErEi4BKHJ3TCripfosxs

f6LUAEBigBLRIrtCj+L5hDASl0KKwussasLYEodixsLVIq9iiftSAFbC6cLOwsTyDAoyvwvC/sK05MHC7cAmv1HC8cKLIsnC5kLkIqBAqCKFwoS0jciVwr5oQgBZEo5SAb8twqPCwvtNYrLCugLAIpPCqhytOHnCy8K9ewMSt4BTR0WEUgBHwufClZJXwpsSwRLZgC0S5SYfwtYkP8Lcgn9hUxKbwqoc0CK4ilzhDcKPgFhHaCLYIsRg02DEIrUS

qb9UIvQi5/tzIsl/aNdsIoEivCKXmRUQYEBiIoBgOaQyIskSAGBrtOwAOiLZ/ATADsL6IrdAHiLTYBYirSL2Io7CziLdAUYi3iKb7F5AASKDIu2AYSKaEtTCuhL64vASphL3QugSmsK4EobClSK1IoYizSK4oG0i3UdMIqfC4vlOrOMii+JGtMkS2JLOLITCn+S83x5MzrTHIqqlZyKhTIG04gzIFNog2t8wRElM3Uz/IpYgwKLkFOCiomSFtLCi

vWDIou4gjUz8FK1MzbTBIMWUmT5bSQNM5KLO1VSik0z5ZzNM8ndEJ2yim7S2FOEU/KLzAEKi7hTN31Ki17T1ijdM3SCPTOBS3dcxFIai3tS/TKkU1qK+AMh0gQDodPhSiMzlFI/XNRSBopTM+Mz2UgA3IhLdFOTMjRTf3yUAwKDMzLASaD8CdMWi7QCkN10A/QCoP1sU0syqdPLMxxTadL2igPz8T06kvTD2b0pksLz7vN6kx7zMwOUfZ80P/Kdg

D6Lzgs7ioMgLoqACz0Kborui9TIIAqpC8GKYAtL7Uqy3orwC4eLrklDXMhLlEBzCgGK8ws1S8+Lo4uICgf9SAoxLSGLKAuYCagKtAFoChGKkYs6swWLV4qlSmuLMYpvis1KoQqwnQQLNAGECgmKVkiJixoK2EvkCimKhl2pi0+Ll4tTir6L14qvilTgJ4rU4XGKOYssCouKeYoBAPmLw0qdSyVKL4pjiq+LxYo9Sn3dhpCli9hIZYvDi0ILI4uNS

6uLR4tVipoBe4ruCpILtYv5i/+KM0sVirNLo0qmC91LzQp6jG3AKgoti6oLrYs5i22LPgvti30LWgqdizoK0dJrS7vt3Yv6CpeKm0oNikeKMYsDivNLqPyPgBYLQ4uLS1uLDQvbi1GKK0oxiuOLzQoOCltSZ0q3S+mKd0pVizOKl0uzip4K84teC5YLuYslCr4LS4t+ChtLrQojSrVL/YqZi8EKs4sbitOR4QvXSiOKiQudSltKjYqvinuKv4r7i

zyA8QqPSstLt0vnSlWKKQq3iqBBaQpni/eL4RAkC5kLWQqgygDLM0pNS4DKCgs3ipdLt4pWHMULZ4tQynYQj4rTS72LoMpPS2DKN4vbSvYKVvM9C++LdQqS9Z+LjEALCtMLqvjAy2tLf4qgy9jLWkoYSwxoOktki0jKSktYS4dK+ksDCiZLWLJyXNBLbYIwSyMKm5MwiCkzrby1vb+S8EqdgPjLCUvU8khLBCl1SihKqEtfi5pLCwq0yp402ksYS

mSKSMqWEbpKg0v9CjhKdYu4S8NA2wtkSrsKBEo/CvsLgkui/URLhwuEsVSKokpQCGJK9It7gGRL/EvkS1gAPMtWgpRLU+xUS8JLzAg0SjUwnEpbAH+LdEsPCzxLgIsMS88KTEvT7MxK7wqH8KxKYss/nYSw5gHyykYDPwoSy6rQzCFcS8aR3Ev0SrxK3gB8S3II/EvfC+RLoCHCy8KKnxzCS+xKPwobAPzL9jkwiphxzQASS6ixE8SSSwiLUktIi

j/xMksoi/GBcktNgfJLP6NNgIpKyks9C6pLykqQPVNoqkuKS6yx+IrfCoSLqEvfikzLQErzS9pKLMpQyqzKxMtJiv0KAwoGSrSLkAB0i2ZKxksMij+ZWLOmS/kcAsssi6fT5kpsixZK7It5MlZLxktLfHNc3IvAU6iCtkq8i8bSfIrOS9LcDkubfIKK23xCiyHLbxzx/E2DLu0uS9Uzoov4gu5KiFPii4edEopEgtxSUorO0hhT0tMyiyhIfkqnX

W7T/kvu0u0yyAMCsx0zt3xdM2gDtIPRS2qKqov0g1Wd6ouhSpqLEUsZytqKQzI6itFKaovxSyMyVFNEA7FK50FxS4aLNdGuSsaLiUuR0rHT2Ummi8lK8dLmi6lK8zKWiulKSdIZS8egmUuMAzaLqdJ8nSsyohy5k5DDOHPsbDFUDABWkFaZUSHZsqVzl3WkfUcjjnyJ6SYAaGO3dTdhmyJ93dRiYDDMuc+9j2D681wj4sNMUEgofDUMck88iXIZ8

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

vuAV6Rc9SwbzLCUAexB34BaGmblf7A7sawbeQH7pHgbyg3tOewaieqF65OkEIAFAd+D/kCMQNMU8Bvb6tjxtrTAGsgajBvEGkwaOrSkgSobBmRqGjuwhw3EgPiwhyBxAKwcQgEYAGIab7AsG5J1R7TuGh4bR4F/sE6R94meG9EE3ht56swMSrU+GtYaHBp+GnwI0QFQAIEbx2Se5Hwa/AD8GuXqzBqAhetohBnVgC9DAJiWG5gaUetWGjgBGBr2Q

c4bWEEKGoRDb+uhaMYabPWOGsmxoMSCG9AaehsuGy31rhpH6hQAeRuwYPka30MAmJ4bdPBeGika+wQ+GtAa7qF+GhiA5LyYsJkbgRtX63QavBuzpNkb8fEgG/wbtcThG0SwqhsRG3TxkRp8nMpA0RrLczEaEAGxG7YRpBpycMkaHvGNGwvrUvXMDGkbRRoAG5OlGRuZGwBxwRqdGjkb3gXSGmulAAB0FDGIBhrVCdPwM/GzG3+w44BQ7QFBe6kAA

WSNelFVYWgxQUBRCOkkBGSMQKH0z+vFGoUbEBDv683qOnUEsW+EoaTYsSYbX2SiAeqwNRpgcckaMLEpGkp1gbWQARsb4xp8CP4arRsBGkBk7Rs8GsEbvBtkAcAbfBpdGzkb2bQjsUMascXXpLUb34F5Gi9CDRvisI0aRxpNGqkbxxsnG9AaExqxSIxAWRqr6lcbIRrXG4wbXRs3GmulaDEAAD2UQUFzG6gA+YkAmOsaURSMQfeQmxqiGrPqEhsGt

BQBPxqPG7qxhxveG88bMgGQAICbAgHNG6cbLRoBGpkb5xuY8e0alxsdGh8axBs6gCQbXxpxGu+w8Ru6dT8aSRvDG5+xIxrHpMcb4JpdwdXqmAGQAYYhb6CFAJCbySGvG9CbkxuXG7fqnxuhGl8ahbTFcd0afzAKIU+xYLD9GqJIMRtwARgBnnCUADBF34FEQWCJ62jaG9xwzhpbGsCbrLCSG9AaUhuCGrPrgxvgsFSaABviGwcaAvVd9CIbqwWbG

gyaaQF+8YV1wfAqGwn1ITzOhGdxZqEfhSQAtupG6vtxEZMFWVybHJp0WRbr1+GW6tya1uuvADbqtusNgHbqX2T26o7qMA0O6yoAMAxO6xWxzuvCmy7rrupfZUek7uqMAB7qig1O9AH0XuoiDaHreLE+6myAfuvdgUnr0psB6rLhqABB6sHqj/VmGgzEoeuDBaIM4gQ6GtLAuhqP6pob2hrqG84b8eq+GjYanBq2GuPqyeuhaKnr9hsOG+nqskkvc

fSaGhssmoybthHkGgVDYJv5674aSeqAGoQJK+ol63CaoRvwmmEbGrBAm4/qxEj9iMUatetSG3XqjepSmtrkTpr2NM6b4Bv968gV9PR9603q5RpoCB3rRwCd65xl4+uisa6bBTE96tpErevum9sapBQkgIPrdbSc9N6bgrAj6+AbE+s5sCGawbChm+6wYZoOsFPrdPDT6iabuhvf63TxZBpmml4bFBogAYvr0BrL6oQaaXAhGvCbCDC2m7jwO7DDc

FvqCGEwmxcbk6RXpLvqikQ+m/vr2BvRmycFZpqxmnGaNetUG9QbF+rcGkEa1+uwm+AalAEJmjabiZpfGw6btJt2ms0bySCYGiybhEQaNSk02uVlGv6bvpqFdeAblRpRmxAR2BqBRRVxWZvmm0/qBBuWm8Xr7rCFmnibNpr4msGxG+risbcaDrGZm6ywdZspGyWaZ+swGtQbsBp5mhcbCBvatRVxjZvZG9cb0xppcSkkhbVGtZSxlBoEG8yaVRsbm

VgbLfSZm3PrMZtgm4ObcZpuIFaaQBqWEL2bnRufGjcaKSTJm3EaZBujm7nrY5u33FQanZq5mzQbqnCpm92ak5pIG9aaTZpFm9ObSZtp5AW0rZumsDuw7ZpbBOwbaRsWmpwbOZpdm3Aa3Zr0GnCbuJu9mtObfZs3GwIbkZqP6tSarLA0mu6gtJrDmjWbdJvCQNWbWeqmmkibgrEnm8khp5p169nr0hvGZMc4wfWyG4gBchpytAoaihpKGzKb+4HzB

CoaPRoRG0cBahrh6zqbP+WaG3s5WhpGGxqaOppbG3oaFAH6G7BhBhuGG4kJRhqVmiYaphqiAGYaIermGrcAFhvzxNJw75oledYbHBtqsAaaBpvwaPYaaevKRUaaThvGmsKw75s/5ceabhoUAAkbH5seGn+wKJuSsKiboxupGhaaeprY8aPJUJpmIQEbbRtLm3ubWRsrmgebeJprm6KwL5p/MT0br5qRG65BfRv9GiSasRq5GpvriJq1m/Eb7hvwW

okaf7HImw0aYJtHGxf1YxpgW+kbiSBvG/yU+5tXG5hbTZtYWmAbuRv3GnUb+RoAmQUbxZohZPWbcZtDmjebJRuPm06bHRUVmz7FUFsVGjFEF5qV64UasFummycFtRt1GoYaAJigm6KwTxtgmmiaNigdmijkUJv+GmhabRowmnQbqZo9muKwU5rTG3u1BJujyK+aKUR9G1EbxJodvARbCJpDGrOawxukWiMbTxqjG00bjFuQmpRbQls4m1RbHxvUW

6uah5oDmoCFsxtzG/MbCxp/sYsbNYFLG7BgKxqrGmgwaxv/G60VlLAbGp5FhQHjGnaa2xuPtb7EuxrcgHsbAFp7tFxbwkB8W2RaYxsvGwpaZxrQm28aPvB7mh0bGFv7m1OaWFsqWrh0hFvDcLJbdxrcWw8bCFuyWyibcluomuRa5lrYmhkabxrvGqJbUxp9mqyagIQ/Gr8av5rVCH8bVYD/G7gN55u6WoCb+ltUm7BbNRsgmo5bjxpkWs8a/FoQm

qmAWJuSJC0bglutGpZbF8RWW/mb7xvWWmJa55v7gBuac+pJ5MibSRuOW4hbTltIW8ca6Jux6hiamJtpYSFbClsTGm5bQBruWweaHloEmuxxhJq4Wsc4+FtSW4AJzCVkm+SaYIkUm5+bYhtUmyZb+4FXmsQB15rHm1FalHFHmq/ql5pEWxIaTJuSGsybzhtpWmER/UVsmxYMuUpZNLqTQCtTAzBDocMbynBDoCoCmpybxuv8m7yaPJqXMQ1bVutmo

PQUluqZ9PVbpusWgegBNuuW60KbqmUSmv5B9uqimmgBIptkDOKazusNOC7qXVuSmi6bHRTSmjKaeaXB6gGBSg3qm97rTYAKmwUAipoyAEqbOjSB6tCBKpoWDFYlwg3IfPKaX5tvmt+b75vamrNaZZq6mtuaKFtJ6inqEFqGm5Ba6eoVGgfr0FtMWxeb2er5W02Bm5ryWiAByFtgWvGbE5q4mtRaNlo0WrZa4rB2m1Xqp+pDmsWbJpuERc6bLTUN6

+Abb+t+mz7FvepBm6ywPpvt6iSBHepRMZ3qp1vd6xEhUsGVm2darLAZmgGbu+pD62WEaXDBmyGaY+vBmk9bj1rj62PqD1tPWt2xU+opRBxa3+o1mjuwbZv7gRtbJ+v2m/WbRevbWgmbqVs2WhvrM5oWsJSxKZvCW92aHiTpmnvqlZsZmp9a3iXDrGObKRvZmqWbO5tcG7ub6FtWWzmxBZp/W7tb9+ussPtaRRrFGiUa5ZsdNBWaPpu968ub+4HvW

kIaP+uIGl9bYNrPGgJa21sNmg6xolvuW/QbWSXgG9Fb2rGfW8yxX1r/6gpaENsLmruatBt5mrCaiBvgG6iwmNppWljb/Zq4dQOawrDjmjXqa1scW1sadhs29KOb4Bu42pQb85v1m/Gb4BvE239b5UX/W3ZborE42xfgaNqbWuTa+NvfgFwbuZuQ24DaGFs5sXTbMNv02uubzBuEWvZa4rFfW1ubRRrpGpab+NqQ2wTaEVpE2pFbO1pRWrkaR5owW

3lbl5vUm6VbNJtlW1SaRVpb68LaZZv+W6iwBVvUDOVat5qHQLIbP+ByGl9k8hoB9I+bpRssW0yxT5tNgc+a4ls4Wm+bMeqgWyAklAEJGpSb0etfmwxb75r6Gz8Bcxo8W7laYRGI25bFexumG2YUQFsgxeYagYQgWgxbh1qMWwtbYFr6mr9FS1qQWg4aUFsrW04bEttG2tUaoQXrWzc48FvqAM+kvFuCsaZbQVrkWltbFFoWWkJakxvhWlDbEVtuW

phau1oqW2Ja7HAq27haURrEm9EaWVvi29jaOBussW4axFo22ghapFuBWnJbfFr227qaJtquW4pasrVKWomaCJv4mqpkDlr1G/RaI7Bw26BaQ5vw2qUbihqK2wZagkVsWqtbQsXI2pxbNvVW2pQAodo8WrbbrLB22ptawVoCW6FbZxuB2kubbNtQ287bkVuY2t0abtoSWu7beFpSWwMbntsyWncboJt+2mZayFt42sQB2JuO2hjaK5rp2iTbQtuqW

nMaXlrqWjGIixpLGyOByxsrGlVhqxpBQWsbPlrI27paLlv52gZbrFvWdT9ERlrGWvsaJlsi2qyxidrOW2ZbelqbGoJaKdrhWqnaPBrLmjtaylsu28HbtlqImwzbXiRJ5fHbCduN2kFaSdvOW83apxqKW63bVpq19DDartvi2pQAnlu/G38aAJk6WvSawrEAmiFbflvFmgcajdpwWwFaiFujcEhaPhsQmqFbLdsWWsJbbdrs22nbgtvp29JarMo52

t3bdxqxW9PbXhrxWrPaggHom0gBGJohW1ib+dqB2wPaUxou2kLbS9rDsOJaGVtEm5lbAxukmhQB2VoUm9+B6tpf6iLbJVpXm6Lap5ti2pPb4tvvWwyaU9q0sVLahVvFWzebBFoVW5R0lVqADN7yivKQwjvKvvLNyyZ9KwF8gYM1ZQH0ACgBZkKHPO3LqcwR6ZpUrfl9otaUmlX2o+c8HdWk4w6T2KO1DC/5eNSYLQIr/SQp88pyFs2gNf4q9ytd8

ip89KqbspjyTyujyiErvSoOzHgAiUIvy1IqcODfuARq1vO2PXKg+vIfyiSYmxgf8+Pz3KuDc3fMmsJKKvvghBlYsQCZQUAgmkFAB3T1/cg7KDpBQag7aDo6k79CeUt/Q1isFjLJPC1snvOrPXBD6DoAmKg7PxuYOkaTe0yw1YDyTCqP2xArJn0/ACYADSAoAXyAJgBWPW3KOMyzqapVlpXBwHlhGqSzqP4MMZh1IoA8bs1MPUE5MCEoKh0TqCrCk

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

XknWcZfxgUnOcaFJoAmT8eiJkZHBcdxpCAnTkbSJhsDlCcyJpZ1sifUJQLHUYTfgELH00d45cLGyMYNxsPHYsZeteLHaiaSxy3H+/VSxxoniAHtxx01WicbR+En1CXyxkNBCseHCYrHxPtKx5bH9RWGJ73GJ0dqxiYmXSADxprH+ORax1Am2sfmJ50nusZwJlYmCbDWJwbGNibuJkFGtcfPRsrlJsfE+1ABzidmxmgnlUaOJv0nmAEYJ02BmCY/R

1gn7icTx/Mn9CXpJtpGiyZLJzc4QSZQxy7GqdWuxyEnsMY7xvDGSiYRJtgAkSfaJ7vGKMdyxdEmrsUxJ37GL81xJ5jGJcZBxmAAwceTRFfGkofKRkkntCbhx2VHVzlqR6snRCRMJ2UmnCf+Jywn+8XPxyzHL8fsJ7wnfiblJufEv8aXxNwmgiY8J1km/8Y5xgAmOSZ5xk60LyavtFkmjybZJmzHACZ3J+UmXyYtJ8AnkiYjRkAko0dUnDzHNSeQJ

bUmd0YVxxMmBscPRlMn2CTTJkgmMyYzR3XGIsdNJo3HzSYvxJBFrSbLRmon6ibX9e0nHSYWJnLHXSd9J93GqgRHR9snRiaDJ33GQyaCAMMnpiYjJ2YnyiZjJ95Gusajx/gmVcffRzbHUyZ2xpCmY8eTx1CHU8aghwvHu4dM8PfGqjUOJg5GGyYLx6KHFGGLx+RHSuW2EcSms2Urxhkm4Ma7JoEnx4SbJ5LE7SYwxyinx0ehJh7GSKbNxXsnnsb7x

4ymB8fexoWLrEU+xjR0v0LLh5m7Mjo1WquGpisgK5x6+bzfBxuHLoc/B3JH0cQnJpQmLkaXxj6F5ychxzKG18cDBDfH4cYpJ4vEd8b2xmknNyYPxx8meCY1Rs/HycZCJoe1ekYcJ08nvyfPJ/wnScYlJ4Inn8f5JjZ0Tye3J3wnq8dFJ0AnlkYPJ2wm2cbvJ9knsqfKpn8m8qYFxpzHlOSVyfmlVSaAp8XGUUUlx0yppcYQJ5pFkCcGdZjEoycIJ

FinMCcWJ+Mnd0dWJmCmVcaGx+CncUZ2J9gmyCdrxRLBKCcwJKNzokARR+KmW7T4J03GcCYxRlgmeKY+FUgmNyYOxr8mmqd4JylHTPG0p+lHTPB8JIcnrKdZRiQmicU5R7lHvrtox7En5Cf8phfHlCeFRucnOMd+hYkmIqdJJzfG1yapJ86nUcbEx2smtnXaR/cm0qaKpjKn8cZlJlpGrqa5J38mlnTfJuwmPyaypsqnOSefJlqnxSexpuqmwidRp

+1GCacetZ1Gl8UDRuInT4SJxYAllSYAp1zHuqfSJ0CnECXgJ3zGcibSQZNG3gQNJoomuIrIx3NH0KZNxlsFqieSxq0nbSetxginmiYdx1imnceRJ4ynXCTbRvshO0e7RvomfSYGJsrHxPqHRiimRiYMp8IB+ycREWdGpifMJYPGl4VGpsPGJqc3R9inNKaYJhMnRMX+R9Ym34U2J4gmuCRWpvYnvickpgOdjianBB9Gn0dLTJ4nribjxisnv0YeJ

/zGnicAxjVhgMYYRUDHPic9pyB1Gqcpp9SnYSY4pmGFtKbBJ/uAISf1pu7HDKc7xlEn0SVMpuGAXsYsp1EmrKcAymymMSc+prEmcSbnxvEn2McBpiHHgab9BXjGwaaipiGnYqY4J3anoabpJy6nk6dPxpkmZMdsZSUniqcyp0qm0af7p7kmlkavJq/FCqc8J6UmHyaTpp8mtYUqpr/FAidnpm8n3yfqpz8mkqbUp5+0iabix/8mwCRFxrqncaWAp

8Fd2abgJrInBqZ1JivEgsf1JgonQsbQxY0n9cf6FMom2sYwpy50sKclp83G8KfBJmWna0adJ+Wm2iZdxibH3ScYQT0nvSZY+0insyY9xvWnAyehJ4MmTacaxhiml0ctpuYn10eAZqanvkZmp6CmnaeTJl2mTqe2J9MndiczJosmcyYoJmbG1qbmxr4mCycwp+sm06Zjxo6nyyaIZiSVw6YTpmsm+6eXplOmVscYZrSmG8dpR0EmWyb0pnOmcMaMp

jomnseLp8ymJGbexp6mK6eHx0cm/sbrpycneqenJ2cnl8aBpzPEW6a0JvPEVyd0J6Kn1ydoZ2knRUd3pusnUqfcJ91HbybJpxen8ae4Z+Z0D6cfxmqn0qemdMenBSYnpuxnV6bMxgqnN6Zxp7em8afcZ5KngMQVJxzGj6aBpTqnUidZp9UmMiY5p6+muaZwZqCnHaeVxtbHVcaIJjglEKdIZ5CniidQpt+mzSdFp+hnxaZtJ3+mU1rQxgBmWiawZ

4imZGa1p8hm4GaqxjsnEGZop5BnA8bNpmYn0GeYpzBnJqbjJ8TEuKduJxanTqb4p8JADYZTxmSm6pA+hsSnOCYOJzvHc8b4Z/uBhmf+kIvHDYdLxjhmiUaXpwJnyUdrxtaGM6eEZtsnRGc7J1OmC6b1xIumKiaNph6m0Seep2ynmwaLg0h6OJhIqxIAJIAoAbYBTnl8gB9jlDtgtO7MeqUROZjVVeLWlTcB6mP/JBI5TxPF+GsiYGvrzRgtzw1kk

VtUV/PufcY71/KYKoEqbfsY8u365jpZ8/cH4DpCR3YjFHpyk4xpeTlfYup7q1FN0BGoLs23ARIi93IIOpJHIjql8tJHfGAiBEiEIwVUBWCxLQWoha0EYSdQhFUEHQUYhTUFsIVYhQIFhIUIhQ2BqWfT5UiF6WcohRCFkgVtBNCEMgSdBTCFcgRYhd0FPQVNBeSxVIQDBQGEc0VIhcMEDQVUBKMEVye+9HL07A1gsVSFMQQqIVUmW/X6DfYFr/XLB

dwNKvUeJBsFkfRf9NINGnUmDIoFP/U1RtyF//Stx71okEo9ZodB+WZ0BHlmyACFZ0gAEIStBJCFe0fohNlnJWaYhaVm3QVwhOVn1WbIAeSxvWYEhQCEGWZohFIFQ2fQhcNmOWZlZ6Nn2IXlZvVmeMaVZqVHE2bDBX1m+4FEhAvFtWd+9QHl9WZChR7ljWcv9U1nBgwtZ+H0+UfkJm1nxg3tZjsEQQUchO1nv/RdZnwNJA3dZwdnPWeHZmXIE2ZLZ

/1nA2cZZ4NnxPrTZiVnnASlZ10EcIUKBfCEpQXjZ40EaWdaBPkFk2aZZsVnWWfTZ+dmI2cXZrlmc2c3ZzixYLATZhBwLwreBCdmqIRTZ/SBWYVnZxwEM2eYhKNnl2cvZl8bFWZ4hQtnVWZLZnoE9kC4hY5A3LHfZ4EEtWdsDX6Hq2aB9CNG62fscBtnelqGDS1mW2fOUNtnX/U1Rh1nu2echRp0+2fmDAdmR2dw5odnR2fXZgVnaWb9Zw2Bt2enZ

lj7H2cdBA9nM2dfZtiEV2cNBc9nCOZ9Z00Eb2ZFZ2iFUgT3ZudmsgUPZzlnZWZPZzoFvQQvZ+q1agVY5oNnkgXvZt4FKOfZZl9ml2bo54Dmh5s/ZnRmQwVNBNVmCIW6BagB/2YzRQDnWLHk5nwJy2bA5x7kIOZS9I1nHA12BAYM4OabZ4IBWEDHJmZRkOZ7ZlG00OadZmYMgfS7Z/tnGvT/MABQx2eI5w5kyOYVBGdnxWafZ6jmZOa5Z+jneWeXL

Jjmi2bIhXzn2Oak559nI2dk5mNmBOdKBDgBFOaXJ/iEf2e85zVn9OdiDXVnDYCM5t4FDWdSJ6DnIfQs5tP1TIRnxuzmMOe/9Rzn1IQQdLDmAAxTW/Dm8OaawLznY2Z854VmxOasBENmAuao57jmaOYS5/jnV2cY5yCEiOdPZ0Tmp2dFZuiEeuek5+Lnj2ZXZ70FUudBplVmVOd/ZstnYLArZtoM82YlRlcFa2dM50fkSuehxaH0yueGDFtmLlEq5

qMaJg07ZtiwnOcw52YNMgylpprnHuea5r1mIufHZ0jmOuYm5rrn/Oc45wLm+ueC5vjnQubjZ4bniIVG5pLmouY+5lNnd2ftBfdm/udm5gHmOIWB5yIF5OfG5u9megAfZ6bm4uaPZgHndOa25lumC2YWGjLm2ub/ZgDmgOeE5kDnsudaDOIM8uZ4xnbnICZ3mhIN9ufM5w7n4OebZuQmkOe4DW1mquYc5q7nHWdq551m7uddZh7nnueF5odnWubU5

9rmA2dvZplnuuZ+53rnnQTh57NnAeY328LmRueY5sbn3ucl5tjnU2Yx5oLmFeeXZhHm+WYi55HmNecnZ1HmLwHR52XmZuax5xXmceep5iVH8eaBhQnnxeeJ5rTnSeaYAOyFQOZy58DmaeZrZunniuaZ5uHEWeas5n7Gv1XO5t/0eefQ5i7nbuZc59b0GufHBYkHrvIyOwv7yQeL+9m7ljM5uqlnXue85lHnpee+56HmuOfl563m9QRLZtdnVeci5

nPmkISh5hiFMed45xXmDeZS5/Nmv2YJ5lbnMubW5pE6DOarZn3mgfUK5wSV/edg55nnLOZrBCrmOefbZ6rmI+Zu53tmBebc5gNwnuaa5sXmpQQr5vzmKOZ152Hmi+bo5kvnEeY3ZsHnF+Zi5lfnC+dr5/Xnc2bt5vHmm+cd5lvmiebb5gT0O+dzBfLmsQUB5PvnySDOJc1njuYQ5uQmzuZH5lDnLuZ79SPm6uan57Dn3Odn5kXnhefn52CETeal5

8jm1AVi53Xm1+cS5obnDebL5wVmwBa15qvmw2egFg/n1+aP5lXmQeZ0BY3nRRoh5plmJOd5AKAXV+fQFtixbeYb5+3nT+eW509nVOalBF3ms8W053TnPecp53LmKBZbp2nmTOYZ5k1nH+bNZo7mO/VMhRDmw+dQ58fm+eec57/np+dLxwAWpBZa5rPm2uZ355lmlQT35hdnSBcG5hjn4BewF8vmkBc657XnLeZr5rNnD+dPZ0vmNBdwF6Lm9kEIF

4gX9+f0FuTmyeYU5xvmlOci52gWRIU05hgW3eavZ94FmBZ1Z73ntud95zgW+g3rZngXG2Zf5+H0bOemUIQWv+cx9H/n+eZj5+7mCfQuZjx6divKOiw5EgGnkNyAagGwAfRBSkToelKi93URTPFhQkNXTJZqQZWtqXFhKmL2lHql+6qoKk37CY3I8wA63Ecye6FmIis3BuFnIDoRZgyrdwaMqmPLgkZ4tRySnz3kLQhy32Jqe0I5C92N8RxqDpkuI

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

peYFq6Wr1KulunSryppsq9yr/Kuiq9Kr/wtyq8NYSqvqq+d2Wqv6q8aQRqvw3nOrmpRLq/rbTiuxDuKOlsGwPPMK1sqRoB4APttQklezkqN1C5uD8Suti+EtCu4KXb0Lp0l3mrN8KLDzWJJlwVqizSsL3qOVwd4DwrOdK7Nzjf6Zi7kzuYuNQ6tL+I0MeyQOu0veY3S4a6ZN1VMR6yvbD1No5fivc+vd7jhDi7Mz6+Dac9SLwKOJAEASRmqopH/A

Ve4EoCcAxdDqezU2f8AFgH/AcqRdlOg8youLveb8gLPYPbqLymOKvK4QigBp5Af1CYg2i+5zZmuXTE14LQ7KxlXPDUid2Loo9mP0s/qjtdNRjGJgKSQRY8Z0UYvt23o99F3Ro/ZVs0u0c4tL8yObc78Lu3OvDoVr6dCi0ICkDg9VVQo6oI6B9WYET3PPS6qkpVWSE99z1yuW1fQATVggk6tgZqv+YWmw5hZ8tX9gASlQGHduhxE4SGD19DXn0VVE

XIAwwBVLSIEhXs4AE7FNvHHryeuInaghNGHyaQnrjgAV4GvhD06YnBnyF3qWEhVRANwfrtglEppZ66yAeApk/GNYQAB/BMAAWUUpQja2p3Y2GGwL1ABvk+/gJ3ZAAHfbQAAIFVYQJIY8EBAYeRBKmjQYX3r0nXFhJ4hBUQ7AcOEkrVRIStyOwE2xcohwG8vL68kEzbkhDpFYG8yRCBvy7C+sIcUMTBQb7dEIG7RMcmxsG95hCBuPJS6QbevFwDQA

Fhh14gPqFmJAADtbXWAhkBfr3KxDYEIepI6JADbr7YgO6/Or7+Ae68SQPuv3ggHrtAVh67K10evYxQXr9eul6/T5GeuDQFPr+evoRDXrqevl67Xh1evF683r7K7SG68sbiw967pJA+uQuUkbueu0AHPr6+vb65eWhhuH64MWZ+u368/r1ABv69/r/+vAG4gb4BvIaQqROBv4xSgbmBuwG9Qb+BuVPU/AJBunG48b+MV0G/tluVwCG6+9XBuSUWCb

2xkiG/6NEhuRSXIbyhuaG7obuJAGG6Ybui68S5u8jNO4C+yOx6vPPaQL1Ng2G44b+nlu656iHhu/YH7rkBhB69KxQRvvHeEbwqnRG/kbiRu9XpPrzB2ZG9NgORvxG50BFevam5IsaQFVG5FJXevHAn3rtxxD690b6Rv9G8vrm+u769ysUxuF4/Mb3KwP66/rn+u/64Ab5xuORQcb0Bvlm6Z5Vxu1m78bjkUvG58b8JugLDQbgogMG6Cb9xucG/gb

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

2l55/PMo9BsX8scroPy6e/AHhnu+zGAr99uTbZQb6oFxO7NIHNvLHWfV7DvC28XbqxFQO7tb8Dv4G/XbntkK26lb2DuXW4DW2gG+O/rboTuUO6+x5tujUQqxc2EJSi6HnrEnvWsdAtuYOddtOcvS7oyJC07HHQ0Z/IkiO8wrkjvsy6hdfF04LFLb0Yex6V9eZQEEO4+8MM50BG9RGVlskFtsS9viWVQ7sMuIK7HL540O275buMvcO81b/DuTW8E5

VcvTh/CQYdvGdZwr7DlhW+GH0Vvp26dbzdu528RNRDvdW/JNYTunTUo7tE0Rh5o72ahA2547t1vd2/BHh7qD2/mHo9vwbjE7yke/kEoroTuInWTtDgBcgDStbZw+IWqBVYe+Ikk7o213y5HxhLumh5jxECvJ8fTb9luv246Hy7q/27zbt41th8FbyEecR91NREfIO7GH6DuJh96eqYex1pmHtEfbTQpH6YfNJXAr9kf3oTWHiUeeh/iJYIoBW+SJ

N20PbUOH59XG6f7aIdvzh83L8ju4R7lHydu8R6RHu4eJDAeH2YeVa00A6Ow8TFk8d4euR9LcHkfVW5+H9Vv/h8w7mCvAO6BHotue24XLo1uUy8I7u0fWOQuH2EefW4RHh1u3R4JHlEf6O81Hxjv+h8xHhYf4R7Y710fFR9o7zdvt29zH/jvSR7YoQTv8x89b4TvRO+e9MUfaR638ekfZiUexRYlCwGZHha1WR5jbjke/YkDH8Hxgx4y78HD949/L

6fvkpZPj19uo0TTbtlu2h+/bqNvs26NH2oMAO6lHoDuZR5Lb31v87RStMelxh4OgSYfUR5DbuYe6x/tNLEfvW++Hltuv2/7H7S19h+6HlceDLVNHnYfm0vUb5PWDh42HvrEbR8GH4Q3kx4dHgR16XRuH/Ee1iHuHnkFHh8XxZ4ffR7eHj4epO6Tbi8flh9+HttuMO4+SLDvAR67bmMe8O+TL340Vy7NbpMflsRTHx0e0x+LHhUeOO+RHrjvDx7rb

m/rtR/VH1jvcR6Inncesx647isejx9YQMNvyR5PHh01Gx/aHmkeyISAsNseQrUZH7se1iV7Hk9vrx+6AQcfMmmk7mQv3rbkL+Qj9AEWAdAOHEzr89Tuv938HnfugM1S1pUvxePAjwqAq7iEY7rP84wJ6UYS6lWjY43QRi4v75HvoQ7SHmzuCI4Nskvupa53DhWOK+/2jQIvIagr4QqBjiKjoSMqmxmikQhPstZAHoAx6h8pzxofgGFKuPeA/k7SW

ESJIgn1H6+E+IlQAYUJ2lEAAZ4NOlCWCI8pp9mIH9pR0S8X7uZRAAHO/SFseGmEMQAAvDLtiIQZ14k/Gw6Qi4E/Gs9IKGEPCD8JTwjjgdRZ94AHrgBQk4BCnsKf2lAin570RJ49gOKe2lESn5KfdkBEH9Ke2S6QYTKfDYBynvKeSbkKn2oRip7XiUqf6GHKnkFBKp+qn98Jap/qnveBGp9SbpPn0m6n7mL7IvIEN3xhmp/3gVqe2lHanqKeJSlin

nqIEp6SnxYIUp4GntpQMp/MH7Kfcp6BQAqeip+wYEqeQUDKniqfqhCqnsIIap5PCOqe1FganspvnB+kn+zCagEwiCoAYACpARSffB+UnoKid+901DTSZK4WMEfpNmG+wZGozLlzIs8S1uJa0BHuiuDw4RIeMW5SHhUOhu+NLpd3Mh8tz7IeUE8Jb5/vFgC5jA8P+4/hOf2ha+/1zyPyL2rwItruHK5iLuof2+4aHzvvhurZtloeUuYwn55kp0adE

ZIkYWn0ANWk3HG1hziez26XH18e7x82H3ofgO4GH2Uehh8InjMfSx9moX15pEn5FJifKoZeHv0eLrADHjkEvhc/GgxIrG86UJafTwlYQI4sQGEAAQmsAVFBQVs5lLDFn8JFJZ7VpbQBXDaZG4kVonSkdICaAReHAL8gDaDcsd2eJZ4BF7EelKcJhOUQ1zVm+tlmggWzR8We7qE9nhWayPSJcHNwPHAbb80ei6SMQZxb/Z5Mp/eRwkVyReYec56sR

J9FS55MtIukWaat1kMfWOVOnviJ1h//bh8fpR7LnxCvFZ4cda0fjh9tHooNoR/FtMduKO41nmietZ+In90fBQD1nnDYwJ59H14f/R6gn7kf2K7QFZbFTp9d9JuemNc+xR8fbHT1btQ3O55XHz8f1Z+/H3Cffx9zL/8etx4bL0eedZ4kMCeeDZ/AnmeeTZ7nnoMeF55CJEjuop7Bx5cflZ5NH1ueq563njufPbS7n4KmhsRwnkSU8J7/H8duAJ8zH

oCfL5/fgyeeSrBvn42fNrFNn18v555gnxYerbTehdjG35/0tD+f1x7bn0U0f56tH3efu56/HvufR2+hda4fT5+oriE0IF/HnqBfr5+nnuBewznvnocfH59DLy8ewx545A1vsO/grk8fYx8NbqyVMJ8TH3uf7R7I7kBfB54nbtJ12O7ontYghBhB4QAAHz2JHvMekO4LH5duCJ+Hnv1vtZ7WIXhpAABjFQAB72MAAEP15F6rH/40yR45BQ9v5Z+Pb

pseuJ7pHtifgrQ7HuEoBJ52RISeOp4NHzkfWx+sXhkfOx84AexeY4SqAe4hItLZHyfIDR9d9KxfFF/rH9xe7F8SdBGx/F/NhEL5gl4xH0Jf2x6TtDxemR7StJgMESCiXiSBIoYnBOU4RIkX7qLFyQnmQIj01WC0QbxxQR5o9cJFpZ7Nn0kXsGBNmb+Ap5ifMKq1Y56PNYYgGIVYsMpfkiWR5dOfwNnCRejZ6fR29IlwLh9LBPiJi5/DhNCfrsUad

Uxf02QvAJz7nsV961pfk5/JIUeleLGV9Ay1o7EQEAVF1Al965Zf4iUi0qoAv8Ak5Uz1Nl8Sx3iw+dcrn3Ye1Z/CQf+EPHDf1vOfLh/pNVO0LGYmxXaVv0UGXv2JwkSoWvSxNvAZ1l+0QGQZ1pUblLGznr+fDChuXq4aZ7o+SXKpb6GLngFezl7qkWXEoV+fHwCnnduLcB+fkF+oGuCxsl6QYRYBo4lniEHgosW0HtUJGGEAAQcjal5cQbxwGl/GE

OOfml4Tn8OeU58jntOfqfS8WVANwNl6X2wx+l8hdF5fA8Eln4OfzAFDnxOe2l5pXqWeFZrmX8pfzx8guZSxrl5IXrDl7l+vJ4Nknl57ZdlfugE5X+nBUYeMgd5fggE+Xi1Fvl4+8X5f7FrdnpOePZ9pXjIBvZ8MVm5eWrLc28ywDgUDnjFolV55X6lfySFTnljuiPDJXtQAKV9kIdCFeV/mXsQB7V5rBdOe8nQFtT4eA21RXiQLoJ6vb2CWBy8Fn

2cfh0FBH21fPV4NXoMa5x9mBOWef24Vn28f3x4CRFCfPwD6HkJfi26KDMBf1F7bcSBfcwdoXo2fIJ6yXqpeLZ6/r62ffp+Wnk8I7Z+IYR2fnZ5BQV2ewrGjXtUBY16NX2w3fZ69FRubC54hWoOfrV+MgMOe9V4jngVeHV/YRRpe3zUpXt1eW169X1hAfV9tsTOf/l9OX+FfgV/VGgue1bSLnqFa4V588iufrF83nwwoa5/INuuel54CX6KfqsQwX

uIl158/n6FfcF9vHnefNh73nwBedJWAX4+fQF/IXstvKF/zX6hfC1/Inw2eIJ9nnsSfSO5DXlBfn55PXtQNV5+NHy9fsF8BXm9f+4EtH1NfvbUIX/efiF9uXvMuxF9clEsfz56oXtVfv15AZWBeS14vb4Nevh+A3+ueT19fnxWf4N62HqDfr15fH29ff54IX/+eTh8fX2pFn15tb0Rfc18w3z9fsN/1nn9e8N//XgjekF6A3o9eRJX1H9BfyN+bn

rBfyTDNH6DeaN9g3t8f/24fXwRefx+EXl9e2N7fX24eL56/X7jfcN7oX/DfEF+RXwTfF57CJeCemACeNdhfkJ6jH1CfuF/QnlCvjW6wnwdvFN8Pn5TfWN6dHoef5R5HnyReIAGkXuRfQJ8Vbyif5ZtHXshf0x7UXjjetF70XgxegHBYnkxe/N5E7k76Y2+bH7ifZHF4n2xfISC8X0WFHF4bngcfXF6zXxZEEl8idLseWR98X0cB0l+vhIJest7iX

08ewl5S3iJfHiGK3mJeyt/0Fc01Kt/y3ha1Ul6K3vseMl5K9UteQ4mGn8we8l4KX6OIil5KXkWfJTT5XhZf3YC63oQYal7qXuCwnV6gAF1eWl9G3sQAOl/pX4RZul6ZX9AMWV5U8AZfDgSGXqFaRl6s3sZfv/QmXkzepl8WgGZfjl8W3tX9Nl9xslZfKwDWXrBJrt87QAy0dl72X6mk8iEOX5LHjl63XjyInzEuXsVfISRuX2EepV43pmVegbzlX

nbfXl+SJVVe0wGatDVf3vB+Xi1E/l7Csb7fc5/znqfb116pgSFel1+3XojwUd6BFA9etFtYNgTeiN8DXktERIkxX7FfcV/VCQlfiV9JXmOfyV6aX11eMgXdX/VeR1+9XlbehFkZXrxZmV+xAVlfmjflX1terV5DngdeWd+HX5HkhV/aXkVevlrCscVeUN6ySJ8xgTUKp2Vex6QF3xVfhd5cwaHf1V4K2TVfF8W1XzHbdV8u3r1f217219igTV+QN

i1fe16F37leRd+nX2NfZcVm3+beqV6HX/lflt8CHJ+6g1+J3gNerdf43/TeiN7spq3vbq879gt37e6l959vAK+nHjcwhZ6jX53e7V9jXmWf+OUTXxcfOh/PXqIJ018zX8revx/Y3jzfdZ5oXnjedN7430uFzZ5BQS2fjGRtnmtfUAHtnp2f+lBWUF2fRV+bXmPeY17Z343flSDN3hXeA58t3rlflV5cwQdfDd7t3zPH6d+dXxneWl9t3tnfZ14Tn

edeOQSzn7HePIk7XkFfu14x3iFfN1+n3wYod1+y3nJIcF9H5U+nD18M3nSUMt5vH2TelZ8wXyDfJN6fHnzzi9bvXj8fEN6Y33ioWN4Hnlze0N4Z5CRfry843q+e89+LXgvePd993gNshN9330DeV55T3yjeT973XmDfTYDg3+Ter94c3oBej5+c3lRe3N+C37PeC1603p4f897vngDfgx5332pEX56GdgA+W56o358fz97o3+9eID8zLoRerW7l3

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
```
%%