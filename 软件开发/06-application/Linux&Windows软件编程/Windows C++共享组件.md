[TOC]

# linux udp主动广播自己IP

附件: [[udp_broadcast-v260107.zip]]

- 主动发送UDP广播包，字符串内容可自定义，发送时间间隔可自定义；
- 由 systemctl 管理；
- 如果中途断网，默认会尝试2分钟重置应用，2分钟后网络还是不通，则会重启系统。



# Windows 应用编程



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







# Bottom

















