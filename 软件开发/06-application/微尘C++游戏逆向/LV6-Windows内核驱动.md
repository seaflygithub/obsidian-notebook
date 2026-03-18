
草稿：[[微尘网络游戏逆向C++.excalidraw]]

malloc推荐书籍: 潘爱民的《Windows内核原理与实现》

# 驱动编译环境搭建

比如前面的天龙游戏，其进程空间为4GB，我们之前探究的都是低2G的空间，

那我们这一系列的课就探究高2GB的内容了，并且了解它与低2G的关系，

比如低2G应用层为3环，高2G为0环，Windows只有0环和3环，

比如我们游戏依赖的各种dll文件，都是加载在3环区域内，而驱动.sys文件加载在0环区域内，

低2G空间是各个进程独有的空间，而高2G是所有进程共用的，

---

驱动开发环境搭建，首先要确认自己电脑操作系统版本，通过CMD运行 winver 查看，

比如老师电脑显示的是 “版本 1803 …”，则表示版本是1803，

然后百度搜索WDK，去微软官网下载对应的WDK，

嫌麻烦的，可以使用老师提供的版本来部署驱动开发环境，

cn_windows_10_business_editions_version_1803_updated_march_2018_x64_dvd_12063730.iso

---

# Win10驱动开发环境

驱动安装步骤官网参考链接(win10 22H2): bing 搜索 vs2022 wdk

https://learn.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk


1、安装必要的组件，如下图所示：

![[Pasted image 20251229144115.png]]


2、下载以及安装SDK、WDK安装包，如下图所示：

![[Pasted image 20251229144137.png]]




# 驱动调试环境搭建

调试环境老师推荐用虚拟机，即使用虚拟机Windows 10，

然后进入把Windows设置成测试模式，cmd管理员运行如下命令，然后重启虚拟机，

```cpp
// 开启测试模式
bcdedit /set testsigning on

// 关闭测试模式
bcdedit /set testsigning off
```

关闭系统防火墙之类的，以及更新服务也关了。

---

然后我们开始编写第一个驱动，helloworld驱动，使用 KMDF 空项目 模板来创建，并做一些必要的配置x64 Debug。

![[Pasted image 20251229144158.png]]


---

新建源文件 main.c，然后编写如下代码，

上面的C++警告视为错误，可能需要创建源文件之后才能看到配置项，

```cpp
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
}
```

编写之后，编译驱动，并用老师提供的 DriverMonitor 工具加载到系统里。

老师推荐，不用 KdPrint 打印信息，因为它要在 DbgView 里勾选详细输出，这会使其卡顿，因为系统很多信息也要输出，

所以这里老师推荐使用 DbgPrintEx 这个打印函数。

![[Pasted image 20251229144219.png]]



# DbgPrintEx详解

通过官网查看 DbgPrintEx 的参数，其函数声明如下：

```cpp
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
**/
```

---

```cpp
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
}
```

下面是代码运行效果：

![[Pasted image 20251229144239.png]]




# 创建驱动设备对象

由于我们的三环用户程序需要和驱动进行交互，这里交互的方式之一就是通过设备对象来进行交互，因此本节围绕着设备对象进行编程探究。

```cpp
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
}
```

如上代码所示，我们创建了 MyIRPCreate 函数，我们想要触发它执行，因此我们需要创建设备对象，

继续添加代码，顺便让驱动支持卸载，即在卸载的操作中释放相关资源，完整代码如下：

```cpp
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
}
```

然后在用户空间打开这个三环文件，以建立和零环驱动之间的通信，

```cpp
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
}
```

# 驱动IRP通讯

前面的设备对象，我们只是触发了其打开、关闭、读取、写入的函数调用，

并没有产生实质性的数据交互，

我们应用层辅助一般会通过: ReadProcessMemory，WriteProcessMemory 来访问游戏内存，

但是很多有保护的游戏会把这两个函数 Hook 了，或者加了检测，

那最好的办法呢，是我们自己建立这样的函数，完整的来实现这个读写内存的功能，

下面是对设备对象加了读写请求的处理，完整代码如下：

```cpp
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
}
```

下面是对应的用户程序的测试代码：

```cpp
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
}
```

# 驱动设备控制

设备的控制接口，相比于读写分开的好处是，可以读写同时，适合小批量数据的读写，

下面是完整的设备对象控制代码，包含驱动代码和应用程序代码。

```cpp
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
}
```

```cpp

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
}
```

控制码是一个 32 位整数，由以下四部分组成： `| 设备类型(16位) | 访问权限(2位) | 功能码(12位) | 方法(2位) |`

设备类型：标识设备所属的类别（如文件系统、磁盘设备等），通常使用预定义的常量（如 `FILE_DEVICE_UNKNOWN`）。 访问权限：指定访问要求（如 `FILE_ANY_ACCESS`、`FILE_READ_ACCESS`）。 功能码：驱动自定义的功能编号，用于区分不同的控制命令。

方法：指定数据传输的方式（如 `METHOD_BUFFERED`、`METHOD_DIRECT`）。

**驱动和应用程序需保持一致：**

```c
// 定义设备类型（自定义值，需避免与系统冲突）
#define FILE_DEVICE_MYDEVICE 0x8000// 定义功能码（0x800 ~ 0xFFF 为自定义范围）
#define MY_FUNCTION_READ  0x800#define MY_FUNCTION_WRITE 0x801// 生成控制码
#define CTRL_RWDEVICE CTL_CODE(FILE_DEVICE_MYDEVICE, MY_FUNCTION_READ, METHOD_BUFFERED, FILE_ANY_ACCESS)
```

在驱动对应的Irp请求处理函数中，可以通过以下方式获取：

```cpp
    PIO_STACK_LOCATION stack = IoGetCurrentIrpStackLocation(Irp);
    ULONG controlCode = stack->Parameters.DeviceIoControl.IoControlCode;//控制码
    ULONG inputBufferLength = stack->Parameters.DeviceIoControl.InputBufferLength;
    ULONG outputBufferLength = stack->Parameters.DeviceIoControl.OutputBufferLength;
    PVOID inputBuffer = Irp->AssociatedIrp.SystemBuffer;
    PVOID outputBuffer = Irp->AssociatedIrp.SystemBuffer;
```

# 双机调试

之前我们在虚拟机上，运行我们的驱动，

双机调试的作用很大，我们在实际开发过程中会遇到各种蓝屏各种错误，

其实你学驱动还是学应用层软件开发，你把调试这块搞得很扎实，你去研究什么东西至少能解决70%的问题，

那我们怎么调试呢？怎么单步去运行虚拟机里面的代码呢？

前面我们安装完WDK之后呢，就会有个 windbg 工具，直接在左下角搜索栏里搜其名字，

1、虚拟机删除打印机，然后添加新硬件，添加串行端口；

2、使用命名的管道，\\.\pipe\abc123

3、虚拟机开机，msconfig —》引导 —》高级选项 —》勾选调试，COM1，115200

4、找到 windbg.exe 所在位置，然后将其发送到桌面快捷方式，并在快捷方式里添加如下命令参数

`-b -k com:pipe,port=\\\\.\\pipe\\abc123,resets=0,reconnect=y`

完整的命令如下:

`"D:\\Windows Kits\\10\\Debuggers\\x64\\windbg.exe" -b -k com:pipe,port=\\\\.\\pipe\\abc123,resets=0,reconnect=y`


![[Pasted image 20251229144315.png]]



上述设置好之后，先运行 windbg，然后虚拟机开机，就能看到 windbg 连上了虚拟机 Windows，

windbg 是否要以管理员方式运行，经过实验验证，无需管理员也能监控虚拟机，

下面是通过 windbg 来获取驱动的打印输出，驱动直接打印即可，

并且，DbgPrintEx 不区分调试还是Release，即使VS端是以Release编译，照样能通过 windbg 或者 dbgView 看到输出。

![[Pasted image 20251229144410.png]]



# windbg命令

bu —— 表示新增断点，比如 bu ntOpenProcess 表示在该函数处设置断点

bl —— 表示显示断点列表；

bc 0 —— 表示清掉断点列表中的第0号断点；

bc * —— 表示清掉断点列表中所有断点；

ba —— 这是内存访问断点

---

.reload —— 表示重新加载符号

.cls —— 表示清屏

u 表示查看汇编代码

dt —— 表示命令格式化显示变量的资料和结构

t —— 单步执行(step)

r —— 显示当前时刻所有寄存器的值

kp —— 显示堆栈信息

---

u 00007ff7`721d2f42 —— 查看此地址开始的汇编代码

u 00007ff7`721d2f42 l20 —— 表示查看该地址20行汇编代码



# IDA入门

IDA是一种静态调试工具，它不像我们之前的OD、CE那样下断调试，

但是它的功能也是特别特别强大，而且强大到远超乎我们想象，我们甚至只需要用它10%的功能，

我们在内核驱动阶段，是有必要掌握它的使用了。

老师提供的IDA安装包：Hex-Rays.IDA.Pro.v7.5.SP3.rar

---

常用操作：

```cpp
N —— 重命名，给函数重命名
; —— 注释
Alt + t —— 搜索
G —— 跳转
Ctrl+F —— 左边符号列表窗口搜索我们想要找的函数名
F5 —— 自动翻译
```

inherit

# 技能-VT无痕HOOK

学员A —— 感觉最难的是对抗反作弊，游戏攻防。

学员B —— 那就学内核，把需要 HOOK 的位置都 HOOK 了，然后学VT无痕HOOK。
















# bottom

