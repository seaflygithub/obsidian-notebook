[TOC]

# linux udp主动广播自己IP

附件: [[udp_broadcast-v260107.zip]]

- 主动发送UDP广播包，字符串内容可自定义，发送时间间隔可自定义；
- 由 systemctl 管理；
- 如果中途断网，默认会尝试2分钟重置应用，2分钟后网络还是不通，则会重启系统。


# 通用96位ID转成合法MAC

```cpp
#include <stdint.h>
#include <stdio.h>

// ======================================================
// FNV-1a 64bit
// 96bit -> 唯一48bit, 这在数学上就不可能, 受到信息熵的约束限制,
// 理论上一定存在碰撞, 但 FNV-1a 分布非常均匀,
// 在实际工程里：MCU,FPGA,USB设备,虚拟网卡,Docker,Hyper-V,VMware 都在大量使用类似思路。
// 全96bit全部参与hash, 碰撞概率多大？
// 48bit MAC 空间：pow(2,48) ≈ 281万亿, 
// 如果你设备量是 100 万以内, 碰撞概率仍然极低, 工业上完全够用。
// 碰撞概率公式: P ≈ pow(k,2) / 2N, k=设备数量, N=MAC空间大小(2的48次方)
// 下面是碰撞概率数量级对照表:
//     设备数量	碰撞概率
//     1万	    0.000000018 %
//     10万	    0.0000018 %
//     100万	0.00018 %
//     1000万	0.018 %
//     3000万	0.16 %
//     1亿	    1.8 %
// ======================================================
static uint64_t fnv1a_64(const uint8_t* data, int len)
{

    uint64_t hash = 0xcbf29ce484222325ULL;

    for (int i = 0; i < len; i++)
    {
        hash ^= data[i];
        hash *= 0x100000001b3ULL;
    }

    return hash;
}

// ======================================================
// UID96 -> 合法MAC
// ======================================================
void uid96_to_umac(const uint8_t uid[12], uint8_t mac[6])
{
    uint64_t h;

    // 计算64bit hash
    h = fnv1a_64(uid, 12);

    // 取低48bit作为MAC
    mac[0] = (uint8_t)(h >> 40);
    mac[1] = (uint8_t)(h >> 32);
    mac[2] = (uint8_t)(h >> 24);
    mac[3] = (uint8_t)(h >> 16);
    mac[4] = (uint8_t)(h >> 8);
    mac[5] = (uint8_t)(h >> 0);

    // ==================================================
    // IEEE MAC规范
    //
    // bit0 = 0 : unicast
    // bit1 = 1 : locally administered
    //
    // 结果:
    // xxxxxx10
    // ==================================================
    mac[0] &= 0xFE;
    mac[0] |= 0x02;
}


int main(int argc, const char *argv[])
{
    // { 0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xAA,0xBB,0xCC } --> 16:c2:75:58:38:b5
    uint8_t origin_uid[12] = { 0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xAA,0xBB,0xCC };
    uint8_t out_mac[6];

    uid96_to_umac(origin_uid, out_mac);
    printf("out_mac = %02x:%02x:%02x:%02x:%02x:%02x\n",
        out_mac[0],
        out_mac[1],
        out_mac[2],
        out_mac[3],
        out_mac[4],
        out_mac[5]
        );

    return 0;
}
```





# Windows C++设备启用禁用


<font color=blue>Windows 10 不是有设备管理器嘛，然后设备管理器里，我们可以通过鼠标操作具体的设备，进行查看硬件信息等操作，也能启用设备 or 禁用设备，如果是先禁用设备然后再启用设备，等同于让设备重新初始化。给我提供一个能够方便后续自动化处理的操作，比如命令行方式启用设备/禁用设备，以及通过 VS C++ 封装一个函数，用来负责启用/禁用某个具体设备。
</font>

目标：**通过 设备实例 ID / 硬件 ID 精准定位设备 → 禁用 → 启用（等价重启初始化）**

---

一、先获取你的设备 ID（必须做）这是你设备的**唯一 ID**，后面全靠它定位。
1. 打开 **设备管理器**
2. 找到你的设备 → **右键 → 属性 → 详细信息**
3. 下拉选择 **设备实例路径**（英文：Device Instance Path）
4. 复制这串字符串，例如：

```cpp
PCI\VEN_8086&DEV_51E0&SUBSYS_11741D05&REV_01\3&11583659&0&B0
```

---

命令行方式（最简单，直接自动化脚本）
使用 Windows 自带工具：**pnputil**（Win10/Win11 原生自带，无需下载）

```bash
# 禁用设备
pnputil /disable-device "PCI\VEN_8086&DEV_51E0&SUBSYS_11741D05&REV_01\3&11583659&0&B0"

# 启用设备
pnputil /enable-device "PCI\VEN_8086&DEV_51E0&SUBSYS_11741D05&REV_01\3&11583659&0&B0"

# 重启设备（禁用 + 启用 一步完成）（3秒）
pnputil /disable-device "PCI\VEN_8086&DEV_51E0&SUBSYS_11741D05&REV_01\3&11583659&0&B0"
timeout /t 3 /nobreak
pnputil /enable-device "PCI\VEN_8086&DEV_51E0&SUBSYS_11741D05&REV_01\3&11583659&0&B0"
```

✅ **管理员权限运行** 即可！
✅ 完全等价于你在设备管理器手动操作。

---


<font color=blue>给我基于VS2022 C++封装一套接口，需要能够在Windows 7 和 以后的版本能够运行。主要是启用设备和禁用设备这两个功能。如果接口调用失败，接口能够返回错误码，并能精准解释错误码含义，方便使用者定位问题。接口源代码能够支持 Unicode 字符集或者多字节字符集。输入参数有两种，一种是基于设备实例Path来使能/禁用具体设备，另一种是通过GUID方式来使能/禁用具体设备。
</font>








VS C++ 封装函数（直接集成到你的 MFC 项目）
使用 Windows 原生 API：**SetupAPI / Cfgmgr32**，无第三方库，干净稳定，可直接用于工业软件。


一、头文件（比如 mydevicectrl.h）
```cpp
#pragma once

#include <Windows.h>
#include <SetupAPI.h>
#include <Cfgmgr32.h>
#include <initguid.h>
#include <atlstr.h>
#include <vector>
#include <iostream>

#pragma comment(lib, "Setupapi.lib")
#pragma comment(lib, "Cfgmgr32.lib")

class CDeviceControl
{
public:
    static CString GetErrorMessage(DWORD dwError);

    static BOOL EnumAllDeviceInstanceIds(
        std::vector<CString>& vecInstanceIds,
        DWORD& dwError);

    static BOOL EnableDeviceByInstanceId(
        LPCTSTR pszInstanceId,
        DWORD& dwError);

    static BOOL DisableDeviceByInstanceId(
        LPCTSTR pszInstanceId,
        DWORD& dwError);

    static BOOL EnableDeviceByGuid(
        const GUID& guid,
        DWORD& dwError);

    static BOOL DisableDeviceByGuid(
        const GUID& guid,
        DWORD& dwError);

private:

    static BOOL ChangeDeviceState(
        HDEVINFO hDevInfo,
        PSP_DEVINFO_DATA pDevInfoData,
        DWORD dwStateChange,
        DWORD& dwError);

    static BOOL FindDeviceByInstanceId(
        LPCTSTR pszInstanceId,
        HDEVINFO& hDevInfo,
        SP_DEVINFO_DATA& devInfoData,
        DWORD& dwError);

};
```


二、源文件（比如 mydevicectrl.cpp）
```cpp
#include "mydevicectrl.h"

CString CDeviceControl::GetErrorMessage(DWORD dwError)
{
    TCHAR szMsg[1024] = { 0 };

    FormatMessage(
        FORMAT_MESSAGE_FROM_SYSTEM |
        FORMAT_MESSAGE_IGNORE_INSERTS,
        NULL,
        dwError,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        szMsg,
        1024,
        NULL);

    return szMsg;
}

BOOL CDeviceControl::EnumAllDeviceInstanceIds(
    std::vector<CString>& vecInstanceIds,
    DWORD& dwError)
{
    vecInstanceIds.clear();

    dwError = ERROR_SUCCESS;

    HDEVINFO hDevInfo =
        SetupDiGetClassDevs(
            NULL,
            NULL,
            NULL,
            DIGCF_ALLCLASSES | DIGCF_PRESENT);

    if (hDevInfo == INVALID_HANDLE_VALUE)
    {
        dwError = GetLastError();
        return FALSE;
    }

    SP_DEVINFO_DATA devInfoData = { 0 };
    devInfoData.cbSize = sizeof(SP_DEVINFO_DATA);

    DWORD index = 0;

    while (SetupDiEnumDeviceInfo(
        hDevInfo,
        index,
        &devInfoData))
    {
        index++;

        TCHAR szInstanceId[MAX_DEVICE_ID_LEN] = { 0 };

        if (SetupDiGetDeviceInstanceId(
            hDevInfo,
            &devInfoData,
            szInstanceId,
            MAX_DEVICE_ID_LEN,
            NULL))
        {
            vecInstanceIds.push_back(szInstanceId);
        }
    }

    DWORD dwLastError = GetLastError();

    SetupDiDestroyDeviceInfoList(hDevInfo);

    // 正常结束
    if (dwLastError == ERROR_NO_MORE_ITEMS)
    {
        return TRUE;
    }

    dwError = dwLastError;

    return FALSE;
}

BOOL CDeviceControl::FindDeviceByInstanceId(
    LPCTSTR pszInstanceId,
    HDEVINFO& hDevInfo,
    SP_DEVINFO_DATA& devInfoData,
    DWORD& dwError)
{
    hDevInfo = SetupDiGetClassDevs(
        NULL,
        NULL,
        NULL,
        DIGCF_ALLCLASSES | DIGCF_PRESENT);

    if (hDevInfo == INVALID_HANDLE_VALUE)
    {
        dwError = GetLastError();
        return FALSE;
    }

    devInfoData.cbSize = sizeof(SP_DEVINFO_DATA);

    DWORD index = 0;

    while (SetupDiEnumDeviceInfo(hDevInfo, index, &devInfoData))
    {
        index++;

        TCHAR szInstanceId[MAX_DEVICE_ID_LEN] = { 0 };

        if (!SetupDiGetDeviceInstanceId(
            hDevInfo,
            &devInfoData,
            szInstanceId,
            MAX_DEVICE_ID_LEN,
            NULL))
        {
            continue;
        }

        if (_tcsicmp(szInstanceId, pszInstanceId) == 0)
        {
            return TRUE;
        }
    }

    dwError = ERROR_NOT_FOUND;
    SetupDiDestroyDeviceInfoList(hDevInfo);

    return FALSE;
}

BOOL CDeviceControl::ChangeDeviceState(
    HDEVINFO hDevInfo,
    PSP_DEVINFO_DATA pDevInfoData,
    DWORD dwStateChange,
    DWORD& dwError)
{
    SP_PROPCHANGE_PARAMS params = { 0 };

    params.ClassInstallHeader.cbSize =
        sizeof(SP_CLASSINSTALL_HEADER);

    params.ClassInstallHeader.InstallFunction =
        DIF_PROPERTYCHANGE;

    params.Scope = DICS_FLAG_GLOBAL;
    params.StateChange = dwStateChange;
    params.HwProfile = 0;

    if (!SetupDiSetClassInstallParams(
        hDevInfo,
        pDevInfoData,
        &params.ClassInstallHeader,
        sizeof(params)))
    {
        dwError = GetLastError();
        return FALSE;
    }

    if (!SetupDiCallClassInstaller(
        DIF_PROPERTYCHANGE,
        hDevInfo,
        pDevInfoData))
    {
        dwError = GetLastError();
        return FALSE;
    }

    return TRUE;
}

BOOL CDeviceControl::EnableDeviceByInstanceId(
    LPCTSTR pszInstanceId,
    DWORD& dwError)
{
    HDEVINFO hDevInfo = INVALID_HANDLE_VALUE;
    SP_DEVINFO_DATA devInfoData = { 0 };

    if (!FindDeviceByInstanceId(
        pszInstanceId,
        hDevInfo,
        devInfoData,
        dwError))
    {
        return FALSE;
    }

    BOOL bRet = ChangeDeviceState(
        hDevInfo,
        &devInfoData,
        DICS_ENABLE,
        dwError);

    SetupDiDestroyDeviceInfoList(hDevInfo);

    return bRet;
}

BOOL CDeviceControl::DisableDeviceByInstanceId(
    LPCTSTR pszInstanceId,
    DWORD& dwError)
{
    HDEVINFO hDevInfo = INVALID_HANDLE_VALUE;
    SP_DEVINFO_DATA devInfoData = { 0 };

    if (!FindDeviceByInstanceId(
        pszInstanceId,
        hDevInfo,
        devInfoData,
        dwError))
    {
        return FALSE;
    }

    BOOL bRet = ChangeDeviceState(
        hDevInfo,
        &devInfoData,
        DICS_DISABLE,
        dwError);

    SetupDiDestroyDeviceInfoList(hDevInfo);

    return bRet;
}

BOOL CDeviceControl::EnableDeviceByGuid(
    const GUID& guid,
    DWORD& dwError)
{
    HDEVINFO hDevInfo = SetupDiGetClassDevs(
        &guid,
        NULL,
        NULL,
        DIGCF_PRESENT);

    if (hDevInfo == INVALID_HANDLE_VALUE)
    {
        dwError = GetLastError();
        return FALSE;
    }

    SP_DEVINFO_DATA devInfoData = { 0 };
    devInfoData.cbSize = sizeof(SP_DEVINFO_DATA);

    DWORD index = 0;

    while (SetupDiEnumDeviceInfo(
        hDevInfo,
        index,
        &devInfoData))
    {
        index++;

        if (!ChangeDeviceState(
            hDevInfo,
            &devInfoData,
            DICS_ENABLE,
            dwError))
        {
            SetupDiDestroyDeviceInfoList(hDevInfo);
            return FALSE;
        }
    }

    SetupDiDestroyDeviceInfoList(hDevInfo);

    return TRUE;
}

BOOL CDeviceControl::DisableDeviceByGuid(
    const GUID& guid,
    DWORD& dwError)
{
    HDEVINFO hDevInfo = SetupDiGetClassDevs(
        &guid,
        NULL,
        NULL,
        DIGCF_PRESENT);

    if (hDevInfo == INVALID_HANDLE_VALUE)
    {
        dwError = GetLastError();
        return FALSE;
    }

    SP_DEVINFO_DATA devInfoData = { 0 };
    devInfoData.cbSize = sizeof(SP_DEVINFO_DATA);

    DWORD index = 0;

    while (SetupDiEnumDeviceInfo(
        hDevInfo,
        index,
        &devInfoData))
    {
        index++;

        if (!ChangeDeviceState(
            hDevInfo,
            &devInfoData,
            DICS_DISABLE,
            dwError))
        {
            SetupDiDestroyDeviceInfoList(hDevInfo);
            return FALSE;
        }
    }

    SetupDiDestroyDeviceInfoList(hDevInfo);

    return TRUE;
}
```


调用例程：
```cpp
#include <Windows.h>
#include <Initguid.h>
#include <guiddef.h>
#include <devguid.h> // 我们拿以太网来试验 (GUID_DEVCLASS_NET)
#include <iostream>
#include "mydevicectrl.h"

DEFINE_GUID(GUID_DEVCLASS_MYETHERNET, 0x4d36e972L, 0xe325, 0x11ce, 0xbf, 0xc1, 0x08, 0x00, 0x2b, 0xe1, 0x03, 0x18);

// 万能：把 TCHAR 字符串 转成 char*，给 printf 使用
const char* TStrToANSI(LPCTSTR tstr)
{
    static char buf[1024] = { 0 };

#ifdef UNICODE
    WideCharToMultiByte(CP_ACP, 0, tstr, -1, buf, sizeof(buf), NULL, NULL);
#else
    strncpy_s(buf, sizeof(buf), tstr, _TRUNCATE);
#endif

    return buf;
}

int main(int argc, const char* argv[])
{
    if (argc != 3)
    {
        printf("USAGE: %s  <0|1> <设备实例ID>    --0:Disable, 1:Enable\n", argv[0]);
        printf("  e.g: %s  0  \"PCI\\VEN_10EC&DEV_8125&SUBSYS_11741D05&REV_05\\01000000684CE00000\"\n", argv[0]);
        return -1;
    }
    int bEnable = atoi(argv[1]);
    CString devInstanceId = argv[2];

    BOOL bRet;
    DWORD dwError = 0;
    CString errstr;

    // 控制台切换 UTF8
    SetConsoleOutputCP(CP_ACP);

    if (bEnable)
    {
        bRet = CDeviceControl::EnableDeviceByInstanceId(devInstanceId, dwError);
        if (!bRet)
        {
            errstr = CDeviceControl::GetErrorMessage(dwError);
            printf("启用设备失败 %d %s\n", dwError, TStrToANSI(errstr.GetString()));
            return 1;
        }
    }
    else
    {
        bRet = CDeviceControl::DisableDeviceByInstanceId(devInstanceId, dwError);
        if (!bRet)
        {
            errstr = CDeviceControl::GetErrorMessage(dwError);
            printf("禁用设备失败 %d %s\n", dwError, TStrToANSI(errstr.GetString()));
            return 1;
        }
    }

    printf("[%s]设备成功: %s\n", bEnable ? "启用" : "禁用", TStrToANSI(devInstanceId.GetString()));


    //通过GUID方式控制设备
    //CDeviceControl::EnableDeviceByGuid(GUID_DEVCLASS_MYETHERNET, dwError);
	return 0;
}
```




# Windows C++应用编程



## 键盘闲置超时检测

- 电脑按键检测应用：长时间没按按键，意味着长时间无人操作，比如超时时间为1小时，在1小时时间里没有任何按键被按下，则表示1小时内无人操作，将会执行超时之后的处理。


附件: [[keyboardIdleDetect-260113.zip]]

电脑按键检测应用：
长时间没按按键，意味着长时间无人操作，比如超时时间为1小时，
在1小时时间里没有任何按键被按下，则表示1小时内无人操作，将会执行超时之后的处理。

```cpp
Step 01. You can set environment variable:
    keyboardNoPressTimeOutSec

Step 02. then you can run the program, 
    the system will reboot after keyboardNoPressTimeOutSec
    (env vars: keyboardNoPressTimeOutSec, keyboardNoPressTimeStepLenSec)

Step 03. Set it to start automatically when you boot up.
    First create the shortcut, 
    then Ctrl+r, 
    then type shell:common startup, 
    and copy the shortcut to this directory.

How to build program (WinMain):
    1. Create Win32 console project
    2. linker --> system --> subsystem --> WINDOWS
    3. C/C++  --> preprocessor --> preprocessor define --> _CONSOLE --> _WINDOWS
```


配置文件参考内容: keyboardIdleDetect.ini
```ini
[GenericSettings]
;超时时间,超过这么多秒后没有按任何按键,就会执行超时脚本 idleTimeoutPostScript
keyboardNoPressTimeOutSec=7200

;日志配置,日志文件最大行数,超过这个阈值,会删掉最早的日志记录,通常删除10%的行数
logMaxLines=10000
logFileName=keyboardIdleDetect.log

;超时检测间隔(步长),比如这里3秒检测一次,顺带会执行一次 idleCheckStepScript
keyboardNoPressTimeStepLenSec=3

;超时后执行的脚本,一般是重启系统,脚本内也能添加其他自定义操作
idleTimeoutPostScript=idleTimeoutPostScript.bat

;该脚本可以作为额外定时任务执行,比如定时检测流氓进程,定时kill这些进程
idleCheckStepScript=idleCheckStepScript.bat
```


参考 idleCheckStepScript.bat :
```bat
@echo off

::下面是常见的流氓进程
::taskkill /f /im wps.exe /t
taskkill /f /im wpscloudsvr.exe /t
taskkill /f /im wpscenter.exe /t
taskkill /f /im BackgroundDownload.exe  /t
```


参考 idleTimeoutPostScript.bat:
```bat
@echo off

shutdown  /r  /f  /t  30
```


源文件清单:
```txt
-a----         2026/1/11     20:13           3017 ini_config_manager.cpp
-a----         2026/1/11     13:02           1146 ini_config_manager.h
-a----         2026/1/11     20:51          16240 keyboardIdleDetect.cpp
-a----         2026/1/11     20:38           3572 string_methods_manager.cpp
-a----         2026/1/11     20:38            617 string_methods_manager.h
```





# Windows C++中文字符编码问题


完整 C++11 代码（VS2022 可直接编译）


Windows C++ 程序开发，有些函数接口只能接收 wstring 这种宽字符类型，或者只能返回这种宽字符类型的字符串变量，这时候为了能够在程序中正确打印or显示中文字符串，以及能够正确在配置文件中写入中文字符串信息，则需要把宽字符的字符串转换成本地ANSI类型，经过实测是可用的。

如下图所示，VS C++工程配置可以配置成 Unicode 字符集 和 多字节字符集(ANSI)：


在 VS C++ 编程开发中，**Unicode、ANSI、UTF-8、UTF-16** 关系如下：
1、正确区分上述的关系，以及在什么情况使用哪个才不会导致乱码，这至关重要；
2、Unicode 是必须要宽字节字符串的情况下使用，UTF-16是其标配编码；Unicode 是字符集合，不是编码，Unicode **不规定如何存储**，只规定编号。Windows API 使用 UTF-16，而不是指 Unicode=UTF-16；Unicode 可以是 UTF-8、UTF-16、UTF-32 等等。
3、ANSI 是在控制台打印or界面显示文字的情况下使用；ANSI 是 Windows 特有概念，跨平台容易乱码。
4、UTF-8 是在跨平台(比如网络)情况下使用；UTF-8 ASCII兼容、跨平台、网络协议标准；
![[Pasted image 20260316092057.png]]








实测工程字符编码配置：由于代码里有些必须要用到宽字符参数，所以工程字符集配置成 **Unicode** 字符集。ANSI的字符串变量，直接用 printf 即可打印，无需宽字符L修饰。


windows_cpp_utils.h 完整内容如下:

```cpp
#ifndef WINDOWS_CPP_UTILS_H
#define WINDOWS_CPP_UTILS_H

#include <Windows.h>
#include <iostream>
#include <vector>
#include <string>

void SetConsoleANSI();// 初始化控制台 ANSI 编码（确保中文正常显示）

// Note: Windows C++ 中文不要用utf8，文本类型的文件保存为 ANSI 即可

void WriteStringToFile(const std::string& filePath, const std::string& content);
std::string ReadStringFromFile(const std::string& filePath);
void WriteStringToFileBinary(const std::string& filePath, const std::string& content);


// 字符集转换接口
std::string WStringToANSI(const std::wstring& wstr);
std::wstring ANSIToWString(const std::string& ansiStr);

// 字符编码转换接口
std::string UTF8ToANSI(const std::string& utf8Str);
std::string ANSIToUTF8(const std::string& ansiStr);

#if 0 // 使用示例
std::string str1 = "中文123";
std::wstring str2 = L"这是中文字符串2222222";
std::string str3 = WStringToANSI(str2);


// 2. 定义文件路径（支持中文路径）
std::string filePath = "D:\\备份测试文件.txt";
std::string filePathUtf8 = "D:\\备份测试文件UTF8.txt";

//// 3. 写入文件（文本模式）
//WriteStringToFile(filePath, str1);

// 4. 读取文件并打印
str1 = ReadStringFromFile(filePath);
printf("str1(ANSI) = %s\n", str1.c_str());

// 4. 读取文件并打印
str1 = UTF8ToANSI(ReadStringFromFile(filePathUtf8));
printf("str1(UTF8) = %s\n", str1.c_str());

printf("str3(WSTR) = %s\n", str3.c_str());

#endif // if 0

#endif // WINDOWS_CPP_UTILS_H
```


windows_cpp_utils.cpp 完整内容如下:

```cpp

#include "windows_cpp_utils.h"
#include <fstream>


// ========== 辅助函数：设置控制台 ANSI 编码（中文显示） ==========
void SetConsoleANSI()
{
    SetConsoleOutputCP(GetACP()); // 恢复默认 ANSI 编码（中文=GBK）
    SetConsoleCP(GetACP());
    setlocale(LC_CTYPE, "");
}


// ========== 核心函数：写入字符串到文件（文本模式） ==========
// filePath: 文件路径（支持中文、长路径）
// content: 要写入的字符串（UTF-8 编码）
void WriteStringToFile(const std::string& filePath, const std::string& content)
{
    // 打开文件：std::ios::out 覆盖写入，std::ios::app 追加写入
    std::ofstream file(filePath, std::ios::out | std::ios::trunc);
    if (!file.is_open())
    {
        throw std::runtime_error("文件打开失败：" + filePath);
    }

    // 写入内容
    file << content;
    if (file.fail())
    {
        throw std::runtime_error("文件写入失败：" + filePath);
    }

    // 关闭文件（析构会自动关闭，手动关闭更严谨）
    file.close();
    std::cout << "字符串已成功写入文件：" << filePath << std::endl;
}

// ========== 核心函数：从文件读取字符串（一次性读取全部内容） ==========
std::string ReadStringFromFile(const std::string& filePath)
{
    std::ifstream file(filePath, std::ios::in);
    if (!file.is_open())
    {
        throw std::runtime_error("文件打开失败：" + filePath);
    }

    // 读取全部内容（C++11 简洁写法）
    std::string content((std::istreambuf_iterator<char>(file)),
        std::istreambuf_iterator<char>());

    file.close();
    std::cout << "已成功读取文件：" << filePath << std::endl;
    return content;
}

// ========== 扩展函数：二进制模式写入（备份时推荐，无格式转换） ==========
void WriteStringToFileBinary(const std::string& filePath, const std::string& content)
{
    std::ofstream file(filePath, std::ios::out | std::ios::binary | std::ios::trunc);
    if (!file.is_open())
    {
        throw std::runtime_error("二进制模式打开文件失败：" + filePath);
    }

    // 写入字节流（适合备份二进制数据、可执行文件等）
    file.write(content.c_str(), content.size());
    if (file.fail())
    {
        throw std::runtime_error("二进制模式写入失败：" + filePath);
    }

    file.close();
    std::cout << "二进制模式写入成功：" << filePath << std::endl;
}



// 万能：把 TCHAR 字符串 转成 char*，给 printf 使用
const char* TStrToANSI(LPCTSTR tstr)
{
    static char buf[1024] = { 0 };

#ifdef UNICODE
    WideCharToMultiByte(CP_ACP, 0, tstr, -1, buf, sizeof(buf), NULL, NULL);
#else
    strncpy_s(buf, sizeof(buf), tstr, _TRUNCATE);
#endif

    return buf;
}


// ========== 核心工具函数：UTF-16 wstring 转 ANSI(GBK) string ==========
// 输入：UTF-16 编码的 std::wstring（含中文）
// 输出：ANSI(GBK) 编码的 std::string（中文环境下可直接打印）
std::string WStringToANSI(const std::wstring& wstr)
{
    // 获取当前系统的 ANSI 代码页（中文环境下为 936，对应 GBK）
    UINT ansiCodePage = GetACP(); // GetACP() = 936 (GBK) 中文简体系统

    // 第一步：计算转换所需的字节数（不含结束符）
    int ansiLen = WideCharToMultiByte(
        ansiCodePage,             // 目标编码：ANSI 代码页（GBK）
        0,                        // 无特殊标志（不转换换行符、保留所有字符）
        wstr.c_str(),             // 源 UTF-16 宽字符串
        static_cast<int>(wstr.size()), // 源字符串长度（-1 自动处理 \0，这里手动指定长度）
        nullptr,                  // 临时缓冲区（先计算长度）
        0,                        // 缓冲区大小（0 仅计算长度）
        nullptr,                  // 无效字符替换符（默认用 ?）
        nullptr                   // 是否替换了无效字符（无需关注）
    );

    // 检查转换长度是否有效
    if (ansiLen <= 0)
    {
        throw std::runtime_error("WString 转 ANSI 失败，错误码：" + std::to_string(GetLastError()));
    }

    // 第二步：分配内存并执行转换
    std::string ansiStr(ansiLen, 0); // 初始化指定长度的字符串
    int ret = WideCharToMultiByte(
        ansiCodePage,
        0,
        wstr.c_str(),
        static_cast<int>(wstr.size()),
        &ansiStr[0],              // 目标缓冲区
        ansiLen,                  // 缓冲区大小
        nullptr,
        nullptr
    );

    if (ret != ansiLen)
    {
        throw std::runtime_error(
            "WString 转 ANSI 不完整，预期转换 " + 
            std::to_string(ansiLen) + " 字节，实际转换 " + 
            std::to_string(ret) + " 字节");
    }

    return ansiStr;
}

// ========== 反向转换：ANSI(GBK) string 转 wstring（可选） ==========
std::wstring ANSIToWString(const std::string& ansiStr)
{
    UINT ansiCodePage = GetACP();

    // 计算转换所需的宽字符数
    int wstrLen = MultiByteToWideChar(
        ansiCodePage,
        0,
        ansiStr.c_str(),
        static_cast<int>(ansiStr.size()),
        nullptr,
        0
    );

    if (wstrLen <= 0)
    {
        throw std::runtime_error("ANSI 转 WString 失败，错误码：" + std::to_string(GetLastError()));
    }

    // 执行转换
    std::wstring wstr(wstrLen, 0);
    int ret = MultiByteToWideChar(
        ansiCodePage,
        0,
        ansiStr.c_str(),
        static_cast<int>(ansiStr.size()),
        &wstr[0],
        wstrLen
    );

    if (ret != wstrLen)
    {
        throw std::runtime_error("ANSI 转 WString 不完整");
    }

    return wstr;
}







// ========== 核心函数1：UTF-8 string → ANSI(GBK) string ==========
// 输入：UTF-8 编码的 std::string（含中文）
// 输出：ANSI(GBK，中文环境) 编码的 std::string
std::string UTF8ToANSI(const std::string& utf8Str)
{
    if (utf8Str.empty())
    {
        return "";
    }

    // 步骤1：UTF-8 → UTF-16 (wstring)
    int utf16Len = MultiByteToWideChar(
        CP_UTF8,                // 源编码：UTF-8
        MB_ERR_INVALID_CHARS,   // 遇到无效字符抛错（保证转换准确性）
        utf8Str.c_str(),        // 源 UTF-8 字符串
        static_cast<int>(utf8Str.size()), // 源字符串长度
        nullptr,                // 临时缓冲区（先计算长度）
        0                       // 缓冲区大小（0 仅计算长度）
    );

    if (utf16Len <= 0)
    {
        throw std::runtime_error("UTF-8 转 UTF-16 失败，错误码：" + std::to_string(GetLastError()));
    }

    std::wstring utf16Str(utf16Len, 0);
    MultiByteToWideChar(
        CP_UTF8,
        MB_ERR_INVALID_CHARS,
        utf8Str.c_str(),
        static_cast<int>(utf8Str.size()),
        &utf16Str[0],
        utf16Len
    );

    // 步骤2：UTF-16 → ANSI(GBK)
    UINT ansiCodePage = GetACP(); // 获取系统ANSI代码页（中文=936=GBK）
    int ansiLen = WideCharToMultiByte(
        ansiCodePage,           // 目标编码：ANSI(GBK)
        0,                      // 无特殊标志
        utf16Str.c_str(),       // 源 UTF-16 字符串
        utf16Len,               // 源字符串长度
        nullptr,                // 临时缓冲区
        0,                      // 缓冲区大小
        nullptr,                // 无效字符替换符（默认?）
        nullptr                 // 是否替换了无效字符
    );

    if (ansiLen <= 0)
    {
        throw std::runtime_error("UTF-16 转 ANSI 失败，错误码：" + std::to_string(GetLastError()));
    }

    std::string ansiStr(ansiLen, 0);
    WideCharToMultiByte(
        ansiCodePage,
        0,
        utf16Str.c_str(),
        utf16Len,
        &ansiStr[0],
        ansiLen,
        nullptr,
        nullptr
    );

    return ansiStr;
}

// ========== 核心函数2：ANSI(GBK) string → UTF-8 string ==========
// 输入：ANSI(GBK，中文环境) 编码的 std::string
// 输出：UTF-8 编码的 std::string
std::string ANSIToUTF8(const std::string& ansiStr)
{
    if (ansiStr.empty())
    {
        return "";
    }

    // 步骤1：ANSI(GBK) → UTF-16 (wstring)
    UINT ansiCodePage = GetACP();
    int utf16Len = MultiByteToWideChar(
        ansiCodePage,           // 源编码：ANSI(GBK)
        MB_ERR_INVALID_CHARS,   // 遇到无效字符抛错
        ansiStr.c_str(),        // 源 ANSI 字符串
        static_cast<int>(ansiStr.size()), // 源长度
        nullptr,
        0
    );

    if (utf16Len <= 0)
    {
        throw std::runtime_error("ANSI 转 UTF-16 失败，错误码：" + std::to_string(GetLastError()));
    }

    std::wstring utf16Str(utf16Len, 0);
    MultiByteToWideChar(
        ansiCodePage,
        MB_ERR_INVALID_CHARS,
        ansiStr.c_str(),
        static_cast<int>(ansiStr.size()),
        &utf16Str[0],
        utf16Len
    );

    // 步骤2：UTF-16 → UTF-8
    int utf8Len = WideCharToMultiByte(
        CP_UTF8,                // 目标编码：UTF-8
        0,                      // 无特殊标志
        utf16Str.c_str(),       // 源 UTF-16 字符串
        utf16Len,               // 源长度
        nullptr,
        0,
        nullptr,
        nullptr
    );

    if (utf8Len <= 0)
    {
        throw std::runtime_error("UTF-16 转 UTF-8 失败，错误码：" + std::to_string(GetLastError()));
    }

    std::string utf8Str(utf8Len, 0);
    WideCharToMultiByte(
        CP_UTF8,
        0,
        utf16Str.c_str(),
        utf16Len,
        &utf8Str[0],
        utf8Len,
        nullptr,
        nullptr
    );

    return utf8Str;
}
```


使用示例:
```cpp
printf("类型名 = %s\n", WStringToANSI(part.name).c_str());

// 控制台程序实际打印:
// 类型名 = 系统分区
```


---


```cpp

#ifdef MYTEST_USE_WCHAR

// 项目配置里使用的 Unicode 字符集，但是调用 printf 函数打印中文字符串变量时，打印出来是乱码？
// 方案 1：使用宽字符专用函数（最推荐，无转码开销）

#include <wchar.h>
#include <locale.h>

int main() {
    // 关键：设置 C 运行时区域为本地（支持中文）
    setlocale(LC_ALL, "");
    const wchar_t* wstr = L"正确的中文";
    // 用 wprintf 打印宽字符，格式符用 %ls
    wprintf(L"%ls\n", wstr);
    return 0;
}

#endif // MYTEST_USE_WCHAR


#ifdef MYTEST_USE_UTF8

// 项目配置里使用的 Unicode 字符集，但是调用 printf 函数打印中文字符串变量时，打印出来是乱码？
// 方案 2：转换为 UTF-8，配合控制台 UTF-8 模式（现代开发首选）

#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <windows.h>
#include <locale.h>

// 辅助函数：UTF-16(wchar_t) 转 UTF-8(char*)
int WCharToUtf8(const wchar_t* wstr, char* utf8, int utf8Len) {
    return WideCharToMultiByte(CP_UTF8, 0, wstr, -1, utf8, utf8Len, NULL, NULL);
}

int main() {
    setlocale(LC_ALL, ".UTF8");
    // 控制台切换为 UTF-8 代码页（65001）
    SetConsoleOutputCP(65001);

    const wchar_t* wstr = L"正确的中文";
    char utf8[1024] = { 0 };
    WCharToUtf8(wstr, utf8, 1023);
    // 用 printf 打印 UTF-8 字符串
    printf("%s\n", utf8);

    // 按 UTF-8 写入到文本文件
    // 然后创建的文本文件就是 UTF-8 编码
    FILE* fp = fopen("test.txt", "wb+");
    if (fp) {
        fprintf(fp, "%s\n", utf8);
        fflush(fp);
        fclose(fp);
    }
    return 0;
}

#endif // MYTEST_USE_UTF8
```


ANSI：不是具体编码，是 “本地编码集” 的统称；随系统区域变化：
- 简中 Windows：ANSI = GBK；
- 繁体 Windows：ANSI = Big5；
- 英文 Windows：ANSI = ASCII；。。。


ANSI（GBK）：汉字 2 字节，英文 1 字节，地域锁定，跨系统易乱码；
UTF-8：汉字 3 字节，英文 1 字节，全球通用，是现代开发的首选。

Windows 工程配置成 Unicode 字符集，其实就是配置成 UTF-16 宽字符集。


下面是 Unicode(wchar) 转换成 utf-8 编码的字符串，以及反向转换，用 C++11 实现的两个函数和用例：

```cpp
#include <string>
#include <stdexcept>
#include <windows.h>  // 仅Windows平台需要，包含转换API

// C++11 实现：UTF-16(wchar_t) 转 UTF-8
std::string utf16_to_utf8(const std::wstring& utf16_str)
{
    // 空字符串直接返回
    if (utf16_str.empty())
    {
        //return "";
        return std::string();
    }

    // 第一步：获取转换所需的缓冲区大小（-1 表示包含字符串结束符）
    int required_size = WideCharToMultiByte(
        CP_UTF8,               // 目标编码：UTF-8
        0,                     // 转换标志：无特殊处理
        utf16_str.c_str(),     // 源UTF-16字符串
        static_cast<int>(utf16_str.length()),  // 源字符串长度（不含结束符）
        nullptr,               // 临时缓冲区：先不分配
        0,                     // 缓冲区大小：先获取所需大小
        nullptr,               // 默认替换字符：不需要
        nullptr                // 是否使用默认替换字符：不需要
    );

    // 检查转换大小是否有效
    if (required_size == 0)
    {
        //throw std::runtime_error("WideCharToMultiByte failed: " + std::to_string(GetLastError()));
        return std::string();
    }

    // 第二步：分配缓冲区并执行转换
    std::string utf8_str(required_size, '\0');
    int result = WideCharToMultiByte(
        CP_UTF8,
        0,
        utf16_str.c_str(),
        static_cast<int>(utf16_str.length()),
        &utf8_str[0],          // C++11 保证std::string的内部存储是连续的
        required_size,
        nullptr,
        nullptr
    );

    if (result == 0)
    {
        //throw std::runtime_error("WideCharToMultiByte conversion failed: " + std::to_string(GetLastError()));
        return std::string();
    }

    // 移除末尾的空字符（std::string不需要手动加结束符）
    utf8_str.resize(result);
    return utf8_str;
}

// C++11 实现：UTF-8 转 UTF-16(wchar_t)
std::wstring utf8_to_utf16(const std::string& utf8_str)
{
    // 空字符串直接返回
    if (utf8_str.empty())
    {
        //return L"";
        return std::wstring();
    }

    // 第一步：获取转换所需的缓冲区大小
    int required_size = MultiByteToWideChar(
        CP_UTF8,               // 源编码：UTF-8
        MB_ERR_INVALID_CHARS,  // 转换标志：遇到无效字符抛错（C++11风格的严格校验）
        utf8_str.c_str(),      // 源UTF-8字符串
        static_cast<int>(utf8_str.length()),
        nullptr,
        0
    );

    if (required_size == 0)
    {
        //throw std::runtime_error("MultiByteToWideChar failed: " + std::to_string(GetLastError()));
        return std::wstring();
    }

    // 第二步：分配缓冲区并执行转换
    std::wstring utf16_str(required_size, L'\0');
    int result = MultiByteToWideChar(
        CP_UTF8,
        MB_ERR_INVALID_CHARS,
        utf8_str.c_str(),
        static_cast<int>(utf8_str.length()),
        &utf16_str[0],         // C++11 保证std::wstring内部连续
        required_size
    );

    if (result == 0)
    {
        // throw std::runtime_error("MultiByteToWideChar conversion failed: " + std::to_string(GetLastError()));
        return std::wstring();
    }

    // 移除末尾的空字符
    utf16_str.resize(result);
    return utf16_str;
}

// 测试用例（C++11）
#include <iostream>
#include <locale.h>
int main()
{
    // 设置控制台区域以支持中文输出
    setlocale(LC_ALL, ".UTF8");
    SetConsoleOutputCP(65001);  // Windows控制台切换为UTF-8编码

    // 测试UTF-16转UTF-8
    std::wstring utf16_src = L"Hello 世界！C++11 编码转换";
    std::string utf8_dst = utf16_to_utf8(utf16_src);
    std::cout << "UTF-8字符串：" << utf8_dst << std::endl;

    // 测试UTF-8转UTF-16
    std::wstring utf16_dst = utf8_to_utf16(utf8_dst);
    std::wcout << L"还原后的UTF-16字符串：" << utf16_dst << std::endl;

    // 验证转换是否可逆
    if (utf16_src == utf16_dst)
    {
        std::wcout << L"\n转换可逆，结果正确！" << std::endl;
    }
    return 0;
}
```




# Windows C++高性能计时器


HighPrecisionTimer.h
HighPrecisionTimer.cpp

```cpp
//#pragma once
#ifndef _CPP_HIGH_PRECISION_TIMER_H
#define _CPP_HIGH_PRECISION_TIMER_H

//#include <afxwin.h>
#include "stdafx.h"
#include <windows.h>
#include <cstdint>

// 高精度时间戳类型（64位整型，核心数据）
typedef int64_t TimeStamp;

void InitHighPrecisionTimer();

/// <summary>
/// 【高性能】获取当前高精度时间戳（纳秒级精度，64位整型）
/// 循环高频调用无性能损耗，线程安全
/// </summary>
/// <returns>64位时间戳（单位：100纳秒，Windows标准间隔）</returns>
TimeStamp GetHighPrecisionTimeStamp();

/// <summary>
/// 时间戳 → 人类可读的日期时间字符串（YYYY-MM-DD HH:MM:SS.ffffff）
/// 支持微秒级显示，兼容MFC
/// </summary>
/// <param name="timestamp">GetHighPrecisionTimeStamp()获取的时间戳</param>
/// <returns>MFC CString 格式化时间</returns>
CString TimeStampToDateTimeString(TimeStamp timestamp);

/// <summary>
/// 时间戳 → 原生SYSTEMTIME结构体（可自定义格式化）
/// </summary>
/// <param name="timestamp">高精度时间戳</param>
/// <param name="st">输出SYSTEMTIME</param>
void TimeStampToSystemTime(TimeStamp timestamp, SYSTEMTIME& st);

#endif // _CPP_HIGH_PRECISION_TIMER_H
```


---

```cpp
#include "stdafx.h"
#include "HighPrecisionTimer.h"

// 静态全局变量（仅初始化一次，无性能开销）
static LARGE_INTEGER g_qpcFrequency = { 0 };
static LARGE_INTEGER g_qpcBaseTime = { 0 };
static TimeStamp g_fileTimeBase = 0;

// 初始化高精度计时器（仅第一次调用执行）
void InitHighPrecisionTimer()
{
	if (g_qpcFrequency.QuadPart == 0)
	{
		// 获取QPC频率（系统启动后固定不变）
		QueryPerformanceFrequency(&g_qpcFrequency);
		// 获取基准QPC计数
		QueryPerformanceCounter(&g_qpcBaseTime);

		// 获取当前系统FILETIME（1601年以来的100纳秒数）
		FILETIME ft;
		GetSystemTimeAsFileTime(&ft);
		ULARGE_INTEGER fileTime;
		fileTime.LowPart = ft.dwLowDateTime;
		fileTime.HighPart = ft.dwHighDateTime;
		g_fileTimeBase = fileTime.QuadPart;
	}
}

/// <summary>
/// 【高性能】获取当前高精度时间戳（纳秒级精度，64位整型）
/// 循环高频调用无性能损耗，线程安全
/// </summary>
/// <returns>64位时间戳（单位：100纳秒，Windows标准间隔）</returns>
TimeStamp GetHighPrecisionTimeStamp()
{
	// 仅第一次调用初始化，后续无分支开销
	if (g_qpcFrequency.QuadPart == 0)
	{
		InitHighPrecisionTimer();
	}

	// 核心：仅2个Windows API调用，无浮点、无内存、无锁，极致高性能
	LARGE_INTEGER qpcNow;
	QueryPerformanceCounter(&qpcNow);

	// 计算高精度偏移（100纳秒为单位）
	const int64_t qpcDelta = qpcNow.QuadPart - g_qpcBaseTime.QuadPart;
	const int64_t delta100ns = (qpcDelta * 10000000) / g_qpcFrequency.QuadPart;

	// 返回64位高精度时间戳（标准Windows时间戳）
	return g_fileTimeBase + delta100ns;
}

/// <summary>
/// 时间戳 → 原生SYSTEMTIME结构体（可自定义格式化）
/// </summary>
/// <param name="timestamp">高精度时间戳</param>
/// <param name="st">输出SYSTEMTIME</param>
void TimeStampToSystemTime(TimeStamp timestamp, SYSTEMTIME& st)
{
	// 64位时间戳 → FILETIME → SYSTEMTIME
	ULARGE_INTEGER fileTime;
	fileTime.QuadPart = timestamp;
	FILETIME ft;
	ft.dwLowDateTime = fileTime.LowPart;
	ft.dwHighDateTime = fileTime.HighPart;

	// 转换成本地时间（需要UTC时间去掉LOCALFLAGS）
	FileTimeToLocalFileTime(&ft, &ft);
	FileTimeToSystemTime(&ft, &st);
}

/// <summary>
/// 时间戳 → 人类可读的日期时间字符串（YYYY-MM-DD HH:MM:SS.ffffff）
/// 支持微秒级显示，兼容MFC
/// </summary>
/// <param name="timestamp">GetHighPrecisionTimeStamp()获取的时间戳</param>
/// <returns>MFC CString 格式化时间</returns>
CString TimeStampToDateTimeString(TimeStamp timestamp)
{
	SYSTEMTIME st{};
	TimeStampToSystemTime(timestamp, st);

	// 格式化输出：年-月-日 时:分:秒.微秒
	CString strTime;
	strTime.Format(_T("%04d-%02d-%02d %02d:%02d:%02d.%06u"),
		st.wYear,
		st.wMonth,
		st.wDay,
		st.wHour,
		st.wMinute,
		st.wSecond,
		st.wMilliseconds * 1000); // 转微秒

	return strTime;
}
```



# Windows C++文件名解析


GetSizeFromFilename 通过 MFC 程序本身的文件名拿到必要的参数信息。

```cpp
#ifdef SZSY_PERF_CODE

#include <afx.h>
#include <string.h>
#include <errno.h>

// 单位换算常量（字节）
#define SIZE_1KB     1024ULL
#define SIZE_1MB     (SIZE_1KB * 1024ULL)
#define SIZE_1GB     (SIZE_1MB * 1024ULL)
#define SPEED_REFRESH_MS 2000
//unsigned char tmpBuffer[4 * SIZE_1MB];

// 自适应字符集：多字节/Unicode 通用
// 文件名格式: pktsz512kB_totalsz1mb.exe ，文件名大小写不敏感
BOOL GetSizeFromFilename(OUT ULONGLONG& outPktSize, OUT ULONGLONG& outTotalSize)
{
	// 初始化输出
	outPktSize = 0;
	outTotalSize = 0;

	// 1. 获取自身 EXE 路径（自适应字符集）
	TCHAR szPath[MAX_PATH] = { 0 };
	if (::GetModuleFileName(NULL, szPath, MAX_PATH) == 0)
		return FALSE;

	CString strFullPath = szPath;

	// 2. 提取文件名（去掉路径）
	int nPathPos = strFullPath.ReverseFind(_T('\\'));
	if (nPathPos != -1)
		strFullPath = strFullPath.Mid(nPathPos + 1);

	// 3. 去掉 .exe 后缀
	int nExePos = strFullPath.ReverseFind(_T('.'));
	if (nExePos > 0)
		strFullPath = strFullPath.Left(nExePos);

	// 4. 统一转大写，大小写不敏感
	CString strFileName = strFullPath;
	strFileName.MakeUpper();

	// 固定关键字（自适应）
	const CString KEY_PKT = _T("PKTSZ");
	const CString KEY_TOTAL = _T("TOTALSZ");

	// 内部解析工具（通用）
	auto ParseValue = [&](const CString& key) -> ULONGLONG
	{
		int index = strFileName.Find(key);
		if (index == -1)
			return 0;

		// 跳过关键字
		index += key.GetLength();
		CString strNum;

		// 提取连续数字
		while (index < strFileName.GetLength() && _istdigit(strFileName[index]))
		{
			strNum += strFileName[index++];
		}

		if (strNum.IsEmpty())
			return 0;

		// 字符串转 64位整数（自适应 Unicode / 多字节）
#if defined(UNICODE) || defined(_UNICODE)
		ULONGLONG num = _wtoull(strNum);
#else
		ULONGLONG num = _atoi64(CT2A(strNum));
#endif

		// 识别单位 K/M/G
		if (index >= strFileName.GetLength())
			return 0;

		TCHAR unit = strFileName[index];
		switch (unit)
		{
		case _T('K'): return num * SIZE_1KB;
		case _T('M'): return num * SIZE_1MB;
		case _T('G'): return num * SIZE_1GB;
		default:      return 0;
		}
	};

	// 解析两个值
	outPktSize = ParseValue(KEY_PKT);
	outTotalSize = ParseValue(KEY_TOTAL);

	// 必须都解析成功
	return (outPktSize > 0 && outTotalSize > 0);
}

#endif // SZSY_PERF_CODE
```


# Windows C++线程绑定CPU核



```cpp
#include <Windows.h>

//绑定CPU核心的使用方法
//CUIntArray arUintCoreRange;
//arUintCoreRange.Add(7);
//CWinThread *pThread = AfxBeginThread(ThreadStartRecv, (void*)this);
//::SetThreadAffinityMask(pThread->m_hThread, ConvertCPUNumber(arUintCoreRange));
DWORD ConvertCPUNumber(CUIntArray &arUIntCPUNumber)
{
	DWORD dwCPUMask = 0;
	for (int i = 0; i < arUIntCPUNumber.GetSize(); i++)
	{
		DWORD dwCPUMaskTmp = 0x1;
		for (int j = 0; j < arUIntCPUNumber.GetAt(i); j++)
		{
			dwCPUMaskTmp = dwCPUMaskTmp << 1;
		}
		dwCPUMask |= dwCPUMaskTmp;

	}
	return dwCPUMask;
}

void CPcieTestDlg::OnBnClickedButtonSaveCsv()
{
	int cpuCoreIndex = max(GetCPULogicalCoreCount() - 1, 0);

	CUIntArray arUintCoreRange;
	arUintCoreRange.Add(cpuCoreIndex);

	m_pTestCSVThread = AfxBeginThread(ThreadTestSaveCSV, (void*)this);

	// 用 Windows 标准API 来绑定CPU核心
	DWORD_PTR mask = ::SetThreadAffinityMask(m_pTestCSVThread->m_hThread, ConvertCPUNumber(arUintCoreRange));
	if (mask == 0)
	{
		char message[128] = { 0 };
		snprintf(message, sizeof(message), "%s 线程绑定核心 %d 失败 %s", __func__, cpuCoreIndex, strerror(errno));
		this->ShowMessage(message, 1);
	}
	else
	{
		char message[128] = { 0 };
		snprintf(message, sizeof(message), "%s 线程绑定核心 %d 完成", __func__, cpuCoreIndex);
		this->ShowMessage(message, 0);
	}
}
```



# Windows C++性能耗时波动统计

---

1、时间戳数组

```cpp
static TimeStamp *g_buffer_timestamps = NULL; // 存放时间戳,用来记录延时波动
g_buffer_timestamps = (TimeStamp *)malloc(pkt_cnt * sizeof(TimeStamp));
```

---

2、时间戳记录点

```cpp
// 要记录的起点
cur_ts = GetHighPrecisionTimeStamp();

// 接收到一帧数据后
if (g_buffer_length < (dma_total_size - dma_pkt_size))
{
	// 存放时间戳(仅存放 g_buffer 范围内的时间戳信息)
	g_buffer_timestamps[tsIndex] = cur_ts;
	tsIndex += 1;
}
```


---

3、存储延时波动
- 记录时间戳之间的差值（延时值），转换成微秒
- 把差值存放写入到 CSV 文件中。

```cpp
void CPcieTestDlg::SaveDelayWaveToCSV(SYSTEMTIME *in_time)
{
	SYSTEMTIME time_now;

	if (in_time)
	{
		time_now = *in_time;
	}
	else
	{
		GetLocalTime(&time_now);
	}

	// 实际有效包数（不是总容量！）
	ULONGLONG valid_pkt_count = dma_total_size / dma_pkt_size - 1;

	char filename[128] = { 0 };
	snprintf(filename, sizeof(filename), "DELAYUS%d_%04d%02d%02d%02d%02d%02d.csv",
		m_device_index,
		time_now.wYear, time_now.wMonth, time_now.wDay,
		time_now.wHour, time_now.wMinute, time_now.wSecond);

	FILE* fp = fopen(filename, "w+t");
	if (fp == NULL)
	{
		ShowMessage("CSV文件创建失败！", 2);
		return;
	}

	ShowMessage("保存CSV文件...", 0);

	// 启用缓冲，避免疯狂IO卡死
	char write_buf[4096];
	setvbuf(fp, write_buf, _IOFBF, sizeof(write_buf));

	// 只写【有效数据】，不越界！
	for (ULONGLONG i = 1; i < valid_pkt_count; i++)
	{
		TimeStamp prev = g_buffer_timestamps[i - 1];
		TimeStamp curr = g_buffer_timestamps[i];

		int64_t delta = curr - prev;
		int64_t delay_us = delta / 10;  // 100ns → 微秒

		fprintf(fp, "%lld\n", delay_us);
	}

	fflush(fp);
	fclose(fp);

	ShowMessage("保存CSV文件完成！", 0);
}
```


---

4、生成测试时间戳

```cpp
UINT ThreadTestSaveCSV(LPVOID pParam)
{
	CPcieTestDlg* dlg = (CPcieTestDlg*)pParam;

#if 1
	// 测试时间波动存盘功能
	{
		ULONGLONG index_all = dma_total_size / dma_pkt_size;

		// 生成模拟时间戳
		dlg->ShowMessage("生成CSV数据...", 0);
		for (ULONGLONG index_cur = 0; index_cur < index_all; index_cur++)
		{
			g_buffer_timestamps[index_cur] = GetHighPrecisionTimeStamp();
			Sleep(10);
		}
		dlg->ShowMessage("生成CSV数据完成", 0);

		// 测试时间戳存盘
		dlg->SaveDelayWaveToCSV(NULL);
	}
#endif // if 0

	return 0;
}

void CPcieTestDlg::OnBnClickedButtonSaveCsv()
{
	int cpuCoreIndex = max(GetCPULogicalCoreCount() - 1, 0);

	CUIntArray arUintCoreRange;
	arUintCoreRange.Add(cpuCoreIndex);
	m_pTestCSVThread = AfxBeginThread(ThreadTestSaveCSV, (void*)this);
	DWORD_PTR mask = ::SetThreadAffinityMask(m_pTestCSVThread->m_hThread, ConvertCPUNumber(arUintCoreRange));
	if (mask == 0)
	{
		char message[128] = { 0 };
		snprintf(message, sizeof(message), "%s 线程绑定核心 %d 失败 %s", __func__, cpuCoreIndex, strerror(errno));
		this->ShowMessage(message, 1);
	}
	else
	{
		char message[128] = { 0 };
		snprintf(message, sizeof(message), "%s 线程绑定核心 %d 完成", __func__, cpuCoreIndex);
		this->ShowMessage(message, 0);
	}
}
```



# Windows C++性能计数器


1、性能计数器实现

```cpp
// 全局/类成员 计数器
static ULONGLONG g_CounterRecvPkt = 0;

// 【写线程】高频频繁累加
static inline void CounterRecvPktIncrement()
{
	// 原子+1，线程安全，无需锁
	InterlockedIncrement(&g_CounterRecvPkt);
}

// 【读线程】2秒读一次
static inline ULONGLONG CounterRecvPktRead()
{
	// 原子读取，线程安全
	return InterlockedCompareExchange(&g_CounterRecvPkt, 0, 0);
}

// 计算 64位无符号计数器 安全差值（自动处理溢出回环）
// curr_count：当前计数值
// prev_count：上一次计数值
// 返回：正确的增量（永远 >= 0，溢出自动回环计算）
static inline ULONGLONG GetCounterDelta(ULONGLONG curr_count, ULONGLONG prev_count)
{
	return (curr_count >= prev_count) ? (curr_count - prev_count) : (ULLONG_MAX - prev_count + curr_count + 1);
}
```


---

2、通过性能计数器来检测速度
相当于 t1, t2 两个时刻的计数值，两个时刻的绝对差值就是当前瞬时速度。

```cpp
UINT ThreadRecvSpeed(LPVOID pParam)
{
	CPcieTestDlg* dlg = (CPcieTestDlg*)pParam;
	ULONGLONG prev_count = 0;
	ULONGLONG curr_count = 0;
	ULONGLONG delta_count = 0;
	double speed_MB;

	while (dlg->m_bSpeedThreadRunning)
	{
		curr_count = CounterRecvPktRead();

		// 获取两次计数之间的差值
		//delta_count = GetCounterDelta(curr_count, prev_count);
		delta_count = curr_count - prev_count;
		if (delta_count > 0)
		{
			// 只有差值不为0的时候才会计算速度并显示

			speed_MB = (double)(delta_count * dma_pkt_size) / 1024.0 / 1024.0;
			speed_MB = speed_MB / (SPEED_REFRESH_MS / 1000);

			CString str;
			str.Format("%.0lfMB/S", speed_MB);
			//str.Format("%lld pkts", curr_count);
			dlg->GetDlgItem(IDC_EDIT_SPEED)->SetWindowText(str);

			// 更新历史记录
			prev_count = curr_count;
		}
		else
		{
			// 如果没有变动，说明接收停止了，此时不应该继续显示速度来迷惑用户
			CString str;
			str.Format("0MB/S");
			dlg->GetDlgItem(IDC_EDIT_SPEED)->SetWindowText(str);
		}

		Sleep(SPEED_REFRESH_MS); // 每2秒刷新一次
	}

	return 0;
}
```



# Windows C++ UDP高性能客户端



```cpp
#include <stdio.h>
#include <stdint.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

typedef struct
{
    SOCKET sock_fd;
    struct sockaddr_in remote_addr;
    int is_init_ok;
} UdpClient_t;

/**
 * @brief 初始化UDP客户端
 * @param cli 客户端句柄结构体
 * @param remote_ip 远端IP字符串，例如 "192.168.1.100"
 * @param remote_port 远端端口
 * @return 0成功，非0失败
 */
int udp_client_init(UdpClient_t* cli, const char* remote_ip, uint16_t remote_port)
{
    if (!cli || !remote_ip)
        return -1;

    memset(cli, 0, sizeof(UdpClient_t));

    // 1. 初始化Winsock
    WSADATA wsa_data;
    int ret = WSAStartup(MAKEWORD(2, 2), &wsa_data);
    if (ret != 0)
    {
        printf("WSAStartup fail, ret:%d\n", ret);
        return -2;
    }

    // 2. 创建UDP socket
    cli->sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (cli->sock_fd == INVALID_SOCKET)
    {
        printf("socket create fail, err:%d\n", WSAGetLastError());
        WSACleanup();
        return -3;
    }

    // 3. 设置远端地址
    cli->remote_addr.sin_family = AF_INET;
    cli->remote_addr.sin_port = htons(remote_port);
    inet_pton(AF_INET, remote_ip, &cli->remote_addr.sin_addr);

    cli->is_init_ok = 1;
    return 0;
}

/**
 * @brief UDP发送数据
 * @param cli 客户端
 * @param buf 发送缓冲区
 * @param len 要发送字节长度
 * @return 返回实际发送字节；SOCKET_ERROR表示失败
 */
int udp_client_send(UdpClient_t* cli, const uint8_t* buf, int len)
{
    if (!cli || !cli->is_init_ok || !buf || len <= 0)
        return SOCKET_ERROR;

    int sent = sendto(cli->sock_fd,
        (const char*)buf,
        len,
        0,
        (struct sockaddr*)&cli->remote_addr,
        sizeof(struct sockaddr_in));

    if (sent == SOCKET_ERROR)
    {
        printf("sendto err:%d\n", WSAGetLastError());
    }
    return sent;
}

/**
 * @brief 阻塞接收UDP报文
 * @param cli 客户端
 * @param recv_buf 接收缓存
 * @param buf_max_len 缓存最大字节
 * @param out_remote_len 输出：对端地址结构体长度，可传NULL
 * @param out_remote_addr 输出：对端地址，可传NULL
 * @return >0:收到字节数；0关闭；SOCKET_ERROR出错
 */
int udp_client_recv(UdpClient_t* cli,
    uint8_t* recv_buf,
    int buf_max_len,
    struct sockaddr_in* out_remote_addr,
    int* out_remote_len)
{
    if (!cli || !cli->is_init_ok || !recv_buf || buf_max_len <= 0)
        return SOCKET_ERROR;

    struct sockaddr_in from_addr;
    int from_len = sizeof(struct sockaddr_in);

    int rlen = recvfrom(cli->sock_fd,
        (char*)recv_buf,
        buf_max_len,
        0,
        (struct sockaddr*)&from_addr,
        &from_len);

    if (out_remote_addr)
        *out_remote_addr = from_addr;
    if (out_remote_len)
        *out_remote_len = from_len;

    //if (rlen == SOCKET_ERROR)
    //{
    //    printf("recvfrom err:%d\n", WSAGetLastError());
    //}
    return rlen;
}

/**
 * @brief 释放UDP客户端资源
 */
void udp_client_deinit(UdpClient_t* cli)
{
    if (!cli)
        return;
    if (cli->is_init_ok)
    {
        closesocket(cli->sock_fd);
        WSACleanup();
    }
    memset(cli, 0, sizeof(UdpClient_t));
}


/**
 * @brief 设置socket为非阻塞模式
 */
int udp_client_set_nonblock(UdpClient_t* cli)
{
    if (!cli || !cli->is_init_ok)
        return -1;

    u_long enable_nonblock = 1;
    int ret = ioctlsocket(cli->sock_fd, FIONBIO, &enable_nonblock);
    if (ret != 0)
    {
        printf("ioctlsocket nonblock fail, err=%d\n", WSAGetLastError());
        return -2;
    }
    return 0;
}

/**
 * @brief 设置UDP内核接收缓冲区，万兆建议 256KB~1MB，降低内核丢包
 */
int udp_client_set_rcvbuf(UdpClient_t* cli, int buf_size)
{
    if (!cli || !cli->is_init_ok)
        return -1;

    int ret = setsockopt(cli->sock_fd, SOL_SOCKET, SO_RCVBUF, (char*)&buf_size, sizeof(int));
    if (ret != 0)
    {
        printf("setsockopt SO_RCVBUF fail err=%d\n", WSAGetLastError());
        return -2;
    }

    // 读取真实生效缓冲区大小
    int actual = 0;
    int opt_len = sizeof(int);
    getsockopt(cli->sock_fd, SOL_SOCKET, SO_RCVBUF, (char*)&actual, &opt_len);
    printf("SO_RCVBUF: request=%d, actual=%d\n", buf_size, actual);

    /*
    通过
    路径：HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\AFD\Parameters
    新建DWORD: DefaultReceiveWindow = 2097152 (2MB)
    重启电脑生效。


    缓冲区太大（>8MB）会占用内核非分页内存，不建议无脑拉满。
    setsockopt 传入的是期望大小，Windows 不会一定完全按你给的值分配，会受 AFD 驱动注册表上限约束，不会返回错误，静默截断。
    必须用 getsockopt 读取实际生效大小，做校验。
    缓冲区只能缓解突发报文峰值；应用层循环读取不及时，照样丢包。


    分档位建议
        开发调试 / 千兆网          1MB (1048576)   默认稳妥起点，绝大多数测试够用
        万兆光口 FPGA              2MB (2097152)   优先选用，应对 FPGA 瞬间爆发大批 UDP 包，内核可以扛住短时脉冲，内存开销可控
        高压力万兆，偶发内核丢包   4MB (4194304)   上限，一般不要超过 4MB
        不建议                     8MB 及以上      占用大量内核非分页内存，Windows 稳定性下降，收益边际递减
    不要设置几十 MB。Windows UDP 性能提升很小，但是内核内存开销急剧上涨。


    **/

    return 0;
}


/**
 * @brief buffer_dump 十六进制打印缓冲区
 * @param buf     输入缓冲区
 * @param len     有效字节长度
 * @param prefix  每行打印的前缀字符串，传NULL则无前缀
 * 格式：
 * [prefix] 偏移(0x0000)  16字节十六进制        | ASCII(不可见用.)
 */
void buffer_dump(const void* buf, size_t len, const char* prefix)
{
    const uint8_t* p = (const uint8_t*)buf;
    size_t offset = 0;

    while (offset < len)
    {
        // 打印行前缀
        if (prefix != NULL)
        {
            printf("%s", prefix);
        }

        // 打印相对偏移（相对于入参buf起始）
        printf("%04zx:  ", offset);

        // 打印最多16字节hex
        size_t i;
        for (i = 0; i < 16; i++)
        {
            if (offset + i < len)
            {
                printf("%02x ", p[offset + i]);
            }
            else
            {
                printf("   "); // 不足16字节填充空格对齐
            }
            // 第8字节后增加空格视觉分割
            if (i == 7)
            {
                printf(" ");
            }
        }

        printf(" | ");

        // 打印右侧ASCII
        for (i = 0; i < 16; i++)
        {
            if (offset + i < len)
            {
                uint8_t ch = p[offset + i];
                // 可见字符 0x20 ~ 0x7E，其余输出 '.'
                if (ch >= 0x20 && ch <= 0x7E)
                {
                    printf("%c", ch);
                }
                else
                {
                    printf(".");
                }
            }
            else
            {
                printf(" ");
            }
        }

        printf("\n");
        offset += 16;
    }
}
```



```cpp

// 接收线程工作函数，运行在独立线程，可设置CPU亲和性绑定指定核心
// 接收线程函数原型：unsigned __stdcall udp_recv_thread(void* param)
unsigned __stdcall udp_recv_thread(void* param)
{
    UdpClient_t* cli = (UdpClient_t*)param;
    uint8_t recv_buf[4096];

    for (;;)
    {
        // ========= 内层循环：吸干内核所有UDP报文 =========
        for (;;)
        {
            int rlen = udp_client_recv(cli, recv_buf, sizeof(recv_buf), NULL, NULL);
            if (rlen > 0)
            {
                // 收到UDP报文
                // 注意：这里不要做重、慢业务处理！
                // 建议：把原始报文拷贝，投递到线程安全队列，交给业务线程去解析会话
                // on_udp_packet(recv_buf, rlen);

                buffer_dump(recv_buf, rlen, "[recv_buf]");
            }
            else
            {
                if (rlen == SOCKET_ERROR)
                {
                    int err = WSAGetLastError();
                    if (err == WSAEWOULDBLOCK)
                    {
                        // 内核缓冲区已空，退出内循环，回到外层忙轮询
                        break;
                    }
                    else
                    {
                        // 真正底层错误，线程退出
                        printf("udp socket fatal error %d\n", err);
                        return 0;
                    }
                }
                else if (rlen == 0)
                {
                    // 0-byte udp，丢弃
                    break;
                }
            }
        }

        // ========= 这里只做：读取时间戳，判断超时标记，不Sleep =========
        // 注意：**不要在这里执行重量级会话处理**
        // 仅做极简的“是否需要退出线程”标志检测
        // session和看门狗超时逻辑建议放到另一个业务线程，不要占用接收线程
    }

    return 0;
}

// ------------------- 简单使用示例 main (非阻塞式) -------------------
int main_noblock(void)
{
    UdpClient_t udp_cli;
    // 修改为你的FPGA板子IP、端口
    const char* target_ip = "127.0.0.1";
    uint16_t target_port = 8080;

    int ret = udp_client_init(&udp_cli, target_ip, target_port);
    if (ret != 0)
    {
        printf("udp client init failed!\n");
        return -1;
    }
    printf("udp client init ok, target: %s:%d\n", target_ip, target_port);


    udp_client_set_nonblock(&udp_cli);         // 设置非阻塞！
    udp_client_set_rcvbuf(&udp_cli, 1024 * 1024);


    //uint8_t send_buf[1400] = { 0x11,0x22,0x33 };
    uint8_t send_buf[1400] = { "Hello World" };
    uint8_t recv_buf[1400] = { 0 };

    // 发送测试
    int sent = udp_client_send(&udp_cli, send_buf, strlen(send_buf));
    printf("send bytes:%d\n", sent);


    /*
    Win+X → 设备管理器 → 网络适配器，找到你的万兆网卡, 右键【属性】→【高级】选项卡
        1. 关闭 EEE、绿色以太网，消除 PHY 层延迟抖动；
        2. 切换到【电源管理】标签：取消勾选「允许计算机关闭此设备以节约电源」
        3. 关闭网卡设备电源管理；系统电源计划设置为高性能；PCIe 链接状态电源管理关闭。
    

    Windows 万兆网卡 RSS 开启、关闭 EEE（节能以太网）

    EEE 会在低流量时切换物理层节能状态，带来延迟抖动、瞬时丢包；
    RSS 把网卡中断分散到多个 CPU 核心，避免单核心被网络中断打满；

    先获取网卡名称：管理员 PowerShell执行
    Get-NetAdapter | Where-Object MediaType -eq "802.3"

    # 开启RSS缩放 Receive-Side Scaling(RSS)
    Enable-NetAdapterRss -Name "Ethernet"

    # 查看RSS状态，确认Enabled:True
    # 如果网卡支持 RSS，显示Enabled: True；老旧网卡不支持会报错。
    Get-NetAdapterRss -Name "Ethernet"

    如果你后面接收线程绑定单独 CPU 核，RSS 不要把中断也压到同一个核，避免该核同时扛硬件中断 + 用户态忙轮询，性能反降。
    可以用Set-NetAdapterRss指定 RSS 使用别的逻辑核心。
        举例：
        1) 你机器 CPU 逻辑核：0,1,2,3,4,5,6,7
        2) 比如你的 UDP 接收线程绑定到 逻辑核 3；那 RSS 中断就避开 3。

    RSS 绑定单个核心（Base=N,Max=N，仅 1 个 RSS 队列）
    所有网卡硬件中断、DMA 完成中断全部落在同一个逻辑核；网卡描述符、接收缓冲区全部热在该核的 L2 Cache。
    不会发生跨核的 Cache 颠簸；硬件中断侧内存访问高度局部性。

    # RSS中断绑定逻辑核2
    Set-NetAdapterRss -Name "Ethernet" -BaseProcessorNumber 2 -MaxProcessorNumber 2
    Set-NetAdapterRss -Name "以太网" -BaseProcessorNumber 2 -MaxProcessorNumber 2

    恢复系统自动管理 RSS
    Set-NetAdapterRss -Name "以太网" -BaseProcessorNumber -1 -MaxProcessorNumber -1
    **/

	
	// ========= 创建线程 =========
	HANDLE h_recv_thread = NULL;
	unsigned int thread_id = 0;
	
	h_recv_thread = (HANDLE)_beginthreadex(
	    NULL,
	    0,
	    udp_recv_thread,
	    &udp_cli,
	    0,
	    &thread_id
	);
	
	if (h_recv_thread == NULL)
	{
	    printf("_beginthreadex udp_recv_thread failed err:%d\n", GetLastError());
	    return -1;
	}
	
	// ---- 设置CPU亲和性：绑定逻辑核3（1ULL << 3）
	DWORD_PTR affinity_mask = 1ULL << 3;
	DWORD_PTR ret_aff = SetThreadAffinityMask(h_recv_thread, affinity_mask);
	if(ret_aff == 0)
	{
	    printf("SetThreadAffinityMask failed %d\n", GetLastError());
	}
	
	// ---- 提升线程优先级，减少被系统抢占
	BOOL ret_prio = SetThreadPriority(h_recv_thread, THREAD_PRIORITY_HIGHEST);
	if(!ret_prio)
	{
	    printf("SetThreadPriority failed %d\n", GetLastError());
	}


    for (;;) Sleep(2000);

    udp_client_deinit(&udp_cli);
    return 0;
}
```


# Windows 注册表编辑

  

## 通过注册表限制 SMB 版本


网盘附件: smb2-server-260804.zip


SMB 2.0.2 或 2.1 到底哪个更好？我给定Windows版本范围：Windows 7 到更高版本这个系统版本范围，低于 Windows 7 的版本我先明确不支持。经过AI的回答，2.1更好。

1、按下 Win + R，输入 regedit 并回车，打开“注册表编辑器”。

2、在地址栏复制并粘贴以下路径，然后回车：

`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters`

3、在右侧空白处右键，选择 新建 > DWORD (32位) 值。将新建的值命名为 MaxSmb2Dialect

4、双击 MaxSmb2Dialect，将“数值数据”修改为 0x00000210 （即 SMB 2.1 对应的值），并确保“基数”选择的是“十六进制”。

5、点击“确定”并关闭注册表编辑器，重启电脑使修改生效。

下面是通过命令自动操作(管理员权限):
```bash
# cmd 命令, 最通用，兼容性最好。
reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters" /v MaxSmb2Dialect /t REG_DWORD /d 0x00000210 /f

# powershell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters" -Name "MaxSmb2Dialect" -Value 0x00000210 -Type DWord -Force

# 两种方法都会立即生效，无需重启, 但需要重新登录Windows系统, WIN+L锁定后，再解锁即可, 或重启服务程序也行。
```

---

Windows客户端开放 Guest 访问（内网测试专用，不建议公网）

有些 Windows 系统可能会访问失败，即使匿名访问也失败，

错误 1272

这是因为 Windows 10/11 默认安全策略禁用匿名/Guest访问共享, 从而触发了系统安全拦截报错 1272。

两种方案: 一种是通过samba用户名密码访问，另一种是修改 Windows 注册表允许匿名访问。

```bash
# 修改注册表, 允许Windows匿名访问 Samba 服务端
reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters" /v AllowInsecureGuestAuth /t REG_DWORD /d 0x00000001 /f
```

















# MFC实时波形


附件: [[MFCAppWaveDrawDemo260521（实时延迟波动波形）.rar]]

效果图:
![[Pasted image 20260521123358.png]]

需求背景: 可用于数据传输时的延迟波动实时监测。




# MFC日志输出窗口IDC_EDIT

适用：**只读日志、自动滚动、换行、追加不刷屏、禁止编辑**

## 一、前期准备

1. 对话框资源拖入一个 **Edit Control**
2. 控件 ID 改为：`IDC_EDIT_MSGLOG`
3. 编辑控件属性必须勾选：
    - ✅ `ReadOnly`：只读，不让用户改
    - ✅ `Multiline`：多行
    - ✅ `Vertical Scroll`：垂直滚动条
    - 可选：`Horizontal Scroll`
    - 取消：`Auto HScroll`


## 二、封装日志输出函数

在你的对话框头文件添加函数声明：
```cpp
// XXXDlg.h
	void logClear();
	void logPrintArgs(LPCTSTR lpszLevel, LPCTSTR lpszFormat, va_list args);
	void logMsgInfo(LPCTSTR lpszFormat, ...);
	void logMsgWarn(LPCTSTR lpszFormat, ...);
	void logMsgError(LPCTSTR lpszFormat, ...);
	/*
		互联网日志格式：[时间] [级别] [模块] [线程] 内容
		[2026-04-25 14:22:30.156] INFO  MainService 系统初始化完成
		[2026-04-25 14:22:30.891] WARN  NetManager 网络延迟偏高
		[2026-04-25 14:22:31.023] ERROR HttpServer 接口请求失败,code=503
		[2026-04-25 14:22:31.105] FATAL AppEntry 核心服务崩溃，程序退出
	**/
```


实现文件：
```cpp
// XXXDlg.cpp


// 清空日志窗口
void cppHookInjectDlg::logClear()
{
    // 获取日志编辑框控件
    CEdit* pEdit = (CEdit*)GetDlgItem(IDC_EDIT_MSGLOG);
    if (pEdit == nullptr)
        return;

    // 清空所有内容
    pEdit->SetWindowText(_T(""));
}

// 内部通用日志输出
void cppHookInjectDlg::logPrintArgs(LPCTSTR lpszLevel, LPCTSTR lpszFormat, va_list args)
{
    // 获取时间
    SYSTEMTIME st;
    GetLocalTime(&st);

    // 拼接 [时间] [级别]
    CString strPrefix;
    strPrefix.Format(_T("[%04d-%02d-%02d %02d:%02d:%02d] %s "),
        st.wYear,
        st.wMonth,
        st.wDay,
        st.wHour,
        st.wMinute,
        st.wSecond,
        lpszLevel);

    // 格式化内容
    CString strContent;
    strContent.FormatV(lpszFormat, args);

    // 最终日志
    CString strLog = strPrefix + strContent;

    // 输出到 Edit
    CEdit* pEdit = (CEdit*)GetDlgItem(IDC_EDIT_MSGLOG);
    if (pEdit == nullptr) return;


    // 1. 当前已占用字符数
    int nUsedChs = pEdit->GetWindowTextLength();
    int nMaxChs = pEdit->GetLimitText(); // 获取最大字符数
    if (nMaxChs == 10000000)
    {
        if ((nUsedChs + 32) >= nMaxChs)
        {
            logClear();
        }

        pEdit->SetSel(-1, -1);
        pEdit->ReplaceSel(strLog);
        pEdit->ReplaceSel(_T("\r\n"));
        pEdit->LineScroll(pEdit->GetLineCount());
    }
    else
    {
        // 设置最大支持 1,000,000 字符（≈1MB），足够大量日志
        pEdit->SetLimitText(10000000);
    }
}

// INFO 级别
void cppHookInjectDlg::logMsgInfo(LPCTSTR lpszFormat, ...)
{
    va_list args;
    va_start(args, lpszFormat);
    logPrintArgs(_T("INFO"), lpszFormat, args);
    va_end(args);
}

// WARN 级别
void cppHookInjectDlg::logMsgWarn(LPCTSTR lpszFormat, ...)
{
    va_list args;
    va_start(args, lpszFormat);
    logPrintArgs(_T("WARN"), lpszFormat, args);
    va_end(args);
}

// ERROR 级别
void cppHookInjectDlg::logMsgError(LPCTSTR lpszFormat, ...)
{
    va_list args;
    va_start(args, lpszFormat);
    logPrintArgs(_T("ERROR"), lpszFormat, args);
    va_end(args);
}
```


## 三、调用示例

```cpp
void cppHookInjectDlg::OnBnClickedButtonCallasm()
{
    // TODO: 在此添加控件通知处理程序代码

    int data1 = 6;
    int data2 = 0;
    data2 = asm_add(data1);
    
    //logMsgPrint("INFO", "num = %d", data2);
    logMsgInfo(_T("num = %d (0x%x)"), data2, data2);
}
```




# MFC表格实现（CListCtrl 报表视图）

<font color=blue>2022 VC++ MFC，我需要一个表格，该表格用来显示抓包的信息，共3列，第一列显示套接字sockfd，第二列显示包大小，第三列显示包内容(16进制)，没抓到包就往表格里追加信息行。
</font>

## 一、界面准备（1 分钟完成）

1. 打开你的 MFC 对话框 / 窗口，从工具箱拖一个 **List Control** 控件到界面
2. 右键控件 → **属性**：
    - `View(视图)` 设为 `Report`（报表模式）
    - 始终现实选定内容(True)
    - 自动排列(True)
    - 控件 ID 默认`IDC_LIST_NETPACK`即可
    
3. 为控件添加**控件变量**：右键控件 → 添加变量 → 变量名：`m_listNetPacket`
	- 然后会在 XXXDlg 类里新增一个实例成员: `CListCtrl m_listNetPacket;`
	- 后续可以用这个成员往列表里塞东西。


## 二、封装接口


```cpp
// XXXDlg 类里的 public 添加接口声明:

	// 初始化表格
	void InitNetPacketList();

	// 抓包信息追加函数
	void AddNetPacketRow(UINT sockfd, int nPacketSize, const BYTE* pPacketData);
```


```cpp
// XXXDlg.cpp 文件里添加接口实现

// ===================== 新增：初始化网络包列表 =====================
void cppHookInjectDlg::InitNetPacketList()
{
	//0——表示移除原先样式
	//LVS_REPORT 报告模式,即每项显示多列
	//LVS_SINGLESEL 设置列表只允许单选
	//LVS_SHOWSELALWAYS 即使列表失去焦点,也显示选中项
	//LVS_ALIGNLEFT 设置列表项的文本左对齐
	//WS_VSCROLL 添加垂直滚动条
	//WS_BORDER 添加边框
	m_listNetPacket.ModifyStyle(0, 
				LVS_REPORT | 
				LVS_SINGLESEL | 
				LVS_SHOWSELALWAYS | 
				LVS_ALIGNLEFT | 
				WS_VSCROLL | WS_BORDER);

    // 设置列表样式：整行选中 + 网格线
	//LVS_EX_FULLROWSELECT 全行选择模式,即选中项时整行都会被高亮显示
	//LVS_EX_GRIDLINES 显示网格线
	//LVS_EX_DOUBLEBUFFER 启用双缓冲,减少闪烁
    m_listNetPacket.SetExtendedStyle(
        m_listNetPacket.GetExtendedStyle()
        | LVS_EX_DOUBLEBUFFER
        | LVS_EX_FULLROWSELECT
        | LVS_EX_GRIDLINES
    );

    // 插入3列表头（你要的格式）
    m_listNetPacket.InsertColumn(0, _T("套接字 sockfd"), LVCFMT_LEFT, 120);
    m_listNetPacket.InsertColumn(1, _T("包大小 (字节)"), LVCFMT_LEFT, 120);
    m_listNetPacket.InsertColumn(2, _T("包内容 (16进制)"), LVCFMT_LEFT, 700);
}

// ===================== 新增：追加一行抓包数据 =====================
void cppHookInjectDlg::AddNetPacketRow(UINT sockfd, int nPacketSize, const BYTE* pPacketData)
{
    if (nPacketSize <= 0 || pPacketData == nullptr)
        return;

    // 新行索引
    int nRow = m_listNetPacket.GetItemCount();

    // 第1列：sockfd
    CString strSock;
    strSock.Format(_T("%d(0x%x)"), sockfd, sockfd);
    m_listNetPacket.InsertItem(nRow, strSock);

    // 第2列：包大小
    CString strSize;
    strSize.Format(_T("%d(0x%x)"), nPacketSize, nPacketSize);
    m_listNetPacket.SetItemText(nRow, 1, strSize);

    // 第3列：16进制格式
    CString strHex;
    for (int i = 0; i < nPacketSize; i++)
    {
        CString tmp;
        tmp.Format(_T("%02X "), pPacketData[i]);
        strHex += tmp;
    }
    m_listNetPacket.SetItemText(nRow, 2, strHex);

    // 自动滚动到底部
    m_listNetPacket.EnsureVisible(nRow, FALSE);
}
```


## 三、调用示例


在合适的位置初始化并显示表头：
```cpp
// 在 XXXDlg 合适的位置初始化表头, DoDataExchange 里是没问题的
void cppHookInjectDlg::DoDataExchange(CDataExchange* pDX)
{
    CDialogEx::DoDataExchange(pDX);
    DDX_Control(pDX, IDC_LIST_NETPACK, m_listNetPacket);
    InitNetPacketList();
}

// 后续在其他函数中就可以往表里塞东西
// 插入表内容(测试内容)
BYTE testPacket[] = { 0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88 };
for(int i=0; i<64; i++)
AddNetPacketRow(1001, 8, testPacket);
```


鼠标右键表中的某一项，则会触发自动复制表项里的内容：
```cpp
// XXXDlg.h --> 在Dlg类里public里, 添加函数声明
	// 每一列的每一项鼠标右键可复制
	afx_msg void OnRClickList(NMHDR* pNMHDR, LRESULT* pResult);


// XXXDlg.cpp

	// 添加这一项: OnRClickList
	BEGIN_MESSAGE_MAP(cppHookInjectDlg, CDialogEx)
	    ON_BN_CLICKED(IDC_BUTTON_CALLASM, &cppHookInjectDlg::OnBnClickedButtonCallasm)
	    ON_NOTIFY(NM_RCLICK, IDC_LIST_NETPACK, &cppHookInjectDlg::OnRClickList)
	    ON_BN_CLICKED(IDC_BUTTON_HOOK, &cppHookInjectDlg::OnBnClickedButtonHook)
	    ON_BN_CLICKED(IDC_BUTTON_MSGLOGCLEAR, &cppHookInjectDlg::OnBnClickedButtonMsglogclear)
	END_MESSAGE_MAP()

	// 实现这个 OnRClickList
	void cppHookInjectDlg::OnRClickList(NMHDR* pNMHDR, LRESULT* pResult)
	{
	    LPNMITEMACTIVATE pNMIA = reinterpret_cast<LPNMITEMACTIVATE>(pNMHDR);
	    *pResult = 0;
	
	    // 获取点击的行和列
	    int nRow = pNMIA->iItem;
	    int nCol = pNMIA->iSubItem;
	
	    if (nRow < 0 || nCol < 0)
	        return;
	
	    // 获取单元格文本
	    CString strText = m_listNetPacket.GetItemText(nRow, nCol);
	    if (strText.IsEmpty())
	        return;
	
	    // 复制到剪贴板
	    if (OpenClipboard())
	    {
	        EmptyClipboard();
	        HGLOBAL hGlobal = GlobalAlloc(GMEM_MOVEABLE, (strText.GetLength() + 1) * sizeof(TCHAR));
	        if (hGlobal)
	        {
	            LPTSTR lpBuffer = (LPTSTR)GlobalLock(hGlobal);
	            if (lpBuffer) _tcscpy_s(lpBuffer, strText.GetLength() + 1, strText);
	            GlobalUnlock(hGlobal);
	            SetClipboardData(CF_UNICODETEXT, hGlobal);
	        }
	        CloseClipboard();
	    }
	
	    // 提示（可选）
	    logMsgInfo(_T("已复制：%s"), strText);
	}
```



# MFC字符串过滤表达式

一、字符串过滤模块

[[myCStringModule.cpp]]
[[myCStringModule.h]]

```cpp
// 功能: 根据表达式, 从列表中选出匹配项
// filterStr 字符串过滤表达式
// vecInstanceIds 待过滤的字符串列表
// outItems 过滤得到的字符串项
// @details 支持小括号、&&、||
BOOL GetFilterItems(const CString& filterStr,
	const std::vector<CString>& vecInstanceIds,
	std::vector<CString>& outItems);
```


---


二、使用方法

![[Pasted image 20260706094952.png]]

```cpp
BOOL CPcieTestDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();
	...

	// 设置默认过滤字符串
	SetDlgItemText(IDC_EDIT_DEVFILTER, _T("PCI && (10EE && 7038)"));
}


// 点击【复位设备】按钮
void CPcieTestDlg::OnBnClickedButtonResetdev()
{
	DWORD dwError;
	std::vector<CString>& vecInstanceIds = std::vector<CString>();
	CString filterStr;
	std::vector<CString> filteredItems;

	// 首先拿到所有设备的实例ID
	CDeviceControl::EnumAllDeviceInstanceIds(vecInstanceIds, dwError);

	// 1. 获取界面的过滤字符串
	GetDlgItemText(IDC_EDIT_DEVFILTER, filterStr);
	if (filterStr.IsEmpty())
	{
		CString msg;
		msg.Format(_T("请输入设备筛选信息关键字(支持: ()、&&、|| 这3种组合逻辑)"));
		AfxMessageBox(msg);
		return;
	}

	// 从输入框获取过滤信息
	/*
	PCI\VEN_10EE&DEV_7038&SUBSYS_000710EE&REV_00\6&19CD2FE4&0&00880008
	PCI\VEN_10EE&DEV_7038&SUBSYS_000810EE&REV_00\6&4AD812E&0&00800008
	PCI\VEN_10EE&DEV_7038&SUBSYS_000910EE&REV_00\6&120227&0&00280008
	*/
	GetFilterItems(filterStr, vecInstanceIds, filteredItems);

	{
		char message[128] = { 0 };
		snprintf(message, sizeof(message), "系统共 %d 个设备，筛选出 %d 个", 
			vecInstanceIds.size(), filteredItems.size());
		this->ShowMessage(message, 0);
	}

	if (filteredItems.size() > 0)
	{
		BOOL bRet;
		CString errStr;
		for (int i = 0; i < filteredItems.size(); i++)
		{
			snprintf(message, sizeof(message), "复位[%d] %s ...", i, filteredItems[i].GetString());
			this->ShowMessage(message, 0);

			// 后续设备相关操作
		}
	}
}
```



# MFC拿到本程序文件名


功能函数：

```cpp

#define SZSY_PERF_CODE 1

#ifdef SZSY_PERF_CODE

#include <afx.h>
#include <string.h>
#include <errno.h>

// 单位换算常量（字节）
#define SIZE_1KB     1024ULL
#define SIZE_1MB     (SIZE_1KB * 1024ULL)
#define SIZE_1GB     (SIZE_1MB * 1024ULL)
#define SPEED_REFRESH_MS 1000
//unsigned char tmpBuffer[4 * SIZE_1MB];

// 自适应字符集：多字节/Unicode 通用
// 文件名格式: pktsz512kB_totalsz1mb.exe ，文件名大小写不敏感
BOOL GetSizeFromFilename(OUT ULONGLONG& outPktSize, OUT ULONGLONG& outTotalSize)
{
	// 初始化输出
	outPktSize = 0;
	outTotalSize = 0;

	// 1. 获取自身 EXE 路径（自适应字符集）
	TCHAR szPath[MAX_PATH] = { 0 };
	if (::GetModuleFileName(NULL, szPath, MAX_PATH) == 0)
		return FALSE;

	CString strFullPath = szPath;

	// 2. 提取文件名（去掉路径）
	int nPathPos = strFullPath.ReverseFind(_T('\\'));
	if (nPathPos != -1)
		strFullPath = strFullPath.Mid(nPathPos + 1);

	// 3. 去掉 .exe 后缀
	int nExePos = strFullPath.ReverseFind(_T('.'));
	if (nExePos > 0)
		strFullPath = strFullPath.Left(nExePos);

	// 4. 统一转大写，大小写不敏感
	CString strFileName = strFullPath;
	strFileName.MakeUpper();

	// 固定关键字（自适应）
	const CString KEY_PKT = _T("PKTSZ");
	const CString KEY_TOTAL = _T("TOTALSZ");

	// 内部解析工具（通用）
	auto ParseValue = [&](const CString& key) -> ULONGLONG
	{
		int index = strFileName.Find(key);
		if (index == -1)
			return 0;

		// 跳过关键字
		index += key.GetLength();
		CString strNum;

		// 提取连续数字
		while (index < strFileName.GetLength() && _istdigit(strFileName[index]))
		{
			strNum += strFileName[index++];
		}

		if (strNum.IsEmpty())
			return 0;

		// 字符串转 64位整数（自适应 Unicode / 多字节）
#if defined(UNICODE) || defined(_UNICODE)
		ULONGLONG num = _wtoull(strNum);
#else
		ULONGLONG num = _atoi64(CT2A(strNum));
#endif

		// 识别单位 K/M/G
		if (index >= strFileName.GetLength())
			return 0;

		TCHAR unit = strFileName[index];
		switch (unit)
		{
		case _T('K'): return num * SIZE_1KB;
		case _T('M'): return num * SIZE_1MB;
		case _T('G'): return num * SIZE_1GB;
		default:      return 0;
		}
	};

	// 解析两个值
	outPktSize = ParseValue(KEY_PKT);
	outTotalSize = ParseValue(KEY_TOTAL);

	// 必须都解析成功
	return (outPktSize > 0 && outTotalSize > 0);
}

#endif // SZSY_PERF_CODE
```


---

使用示例：

```cpp
	if (GetSizeFromFilename(dma_pkt_size, dma_total_size))
	{
		//CString msg;
		//msg.Format(_T("包大小：%llu 字节\n总大小：%llu 字节"), dma_pkt_size, dma_total_size);
		//AfxMessageBox(msg);
		char message[256] = { 0 };
		sprintf(message, "文件名解析到包大小：%llu 字节  总大小：%llu 字节", dma_pkt_size, dma_total_size);
		this->ShowMessage(message, 0);
	}
	else
	{
		//AfxMessageBox(_T("解析文件名失败！"));
		dma_pkt_size = 512 * SIZE_1KB;
		dma_total_size = 100 * SIZE_1MB;

		char message[256] = { 0 };
		sprintf(message, "解析文件名失败，使用默认包大小：%llu 字节  总大小：%llu 字节", dma_pkt_size, dma_total_size);
		this->ShowMessage(message, 1);
	}
```







# Unicode环境下CString和buf之间相互转换


## CString_to_Buf使用示例


```cpp
// 从编辑框拿到字符串内容存入strSend
CString strSend;
{
	// 1. 获取编辑框控件指针
	CEdit* pEdit = (CEdit*)GetDlgItem(IDC_EDIT_TCPDATA);
	if (pEdit == nullptr)
		return;

	// 2. 获取文本框字符串
	pEdit->GetWindowText(strSend);

	// 3. 去除前后空白（可选，防止用户只输入空格/换行）
	strSend.Trim();

	// 4. 如果为空，直接返回，不发送
	if (strSend.IsEmpty())
	{
		logMsgWarn(_T("请填充发送内容(字符串)"));
		WSACleanup();
		return;
	}
}

// 转换成网络能发送的字节内容
CStringA strSendA = CW2A(strSend);
const char* pSendBuf = strSendA;
int nSendLen = strSendA.GetLength(); // 等价 strlen

// 网络发送出去
send(sock, pSendBuf, nSendLen, 0);
```



## Buf_to_CString使用示例

```cpp
// 字符编码相关头文件
#include <atlstr.h>
#include <atlconv.h>

void c_netpack_dump(int sockfd, void *buf, long len)
{
    if (mainDlg != nullptr)
    {
        // 支持中文内容展示(打印Unicode字符集编码的字符串)
        CString cstr = CA2W((char *)buf);
        mainDlg->logMsgInfo(_T("sockfd=0x%lx, buf=0x%lx, len=%ld, cstr=%ws"), sockfd, buf, len, cstr);

        // 不打印数据内容
        //mainDlg->logMsgInfo(_T("sockfd=0x%lx, buf=0x%lx, len=%ld"), sockfd, buf, len);
    }
}
```
















# Bottom

















