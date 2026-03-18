---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠== You can decompress Drawing data with the command palette: 'Decompress current Excalidraw file'. For more info check in plugin settings under 'Saving'


# Excalidraw Data

## Text Elements
imgui ^bn46Pb6r

https://github.com/ocornut/imgui

平台选择: E:\project\vsproject\imgui-master\backends\imgui_impl_dx11.cpp
工程入口: E:\project\vsproject\imgui-master\examples\imgui_examples.sln ^snjuqyjj

012. 外部绘制独立的界面窗体(只保留 ImGui 窗体) ^f8QUkNhS

011. 加载字体和中文 ^JZw25rQI

步骤1: 把控制台换成窗口 ^97084xSc

步骤2: 修改main函数头 ^27fQAySo

【不显示控制台窗口】 ^jVJwxvJp

1. 选择 docking 分支 ^rlJ5zwkf

2. 修改这两个参数为图中值 ^gtoJbQo6

3. 然后就只显示 ImGui 窗口了 ^PrNxLPgj

AddFontFromFileTTF 函数缺陷: 
        (1) 不方便程序简洁发布;
        (2) 加载字体文件期间会有一段时间的白屏.


AddFontFromMemoryTTF 函数用法
vsproject\imgui-master\misc\fonts\binary_to_compressed_c.cpp
    (1) 新建空工程;
    (2) 把 master 分支的 binary_to_compressed_c.cpp 原封不动拷贝到工程里;
    (3) 直接编译生成小工具(比如叫 font2array.exe)
    (4) 把目标字体 .ttf 文件拷贝到同目录;
    (5) 在命令行执行:
          font2array.exe  -nocompress  testfont.ttf  myfont_data  > myfont.h

    (6) 把头文件拷贝到你目标工程里, 在你的 docking 工程里调用加载字体数据：
          ImFontConfig ifc;
          ifc.FontDataOwnedByAtlas = false;
          io.Fonts->AddFontFromMemoryTTF(myfont_data, myfont_data_size, 18.0f, &ifc, io.Fonts->GetGlyphRangesChineseFull());
          //ImGui::Begin(u8"Hello你好"); // 带中文字符串的都要加u8修饰(utf-8) ^h483HQ9a

014. 搭建内部绘制的 ImGui 项目框架 ^0jZVdvIx

CSGO ^FkywJ1xF

PUGB ^k6tIGacH

(1) 内部绘制, 就和我们前面的DLL一样, 需要依赖目标进程才能运行;
(2) 我们需要利用 dx11 的绘制把 ImGui 界面绘制在游戏窗口内部, 让其成为游戏的一部分;


(1) VS以动态链接库方式创建工程;
(2) 把 ImGui 相关代码拷贝到工程目录; ^hKCekc3V

vsproject\imgui-docking\顶层所有cpp源文件  -->  mydll.src\
    imconfig.h
    imgui.cpp
    imgui.h
    imgui_demo.cpp
    imgui_draw.cpp
    imgui_internal.h
    imgui_tables.cpp
    imgui_widgets.cpp
    imstb_rectpack.h
    imstb_textedit.h
    imstb_truetype.h


vsproject\imgui-docking\backends --> mydll.src\ImGui\
    imgui_impl_dx11.cpp
    imgui_impl_dx11.h
    imgui_impl_win32.cpp
    imgui_impl_win32.h ^vH0Sehcq

(3) 新增头文件: main.h






(4) 显式添加系统的DX11依赖: d3d11.lib

(5) 不使用预编译头: 工程配置 >> C/C++ >> 预编译头 >> 选择不使用

(6) 编写主程序: dllmain.cpp --> DLL_PROCESS_ATTACH 分支















(7) 参考代码: 第七阶段UE专题\imgui\source\第14课代码.rar ^FhR15G2B

第七阶段UE专题\imgui\source\第14课代码.rar ^8ue4hj4d

013. 实现登陆界面 ^wF21I3oS

#pragma once
#include <d3d11.h>
#include "ImGui/imgui_impl_dx11.h"
#include "ImGui/imgui_impl_win32.h"
#include <windows.h> ^lsNqavDk

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    {
        // 创建线程, 线程函数在其他文件实现(模块化)
        ::CreateThread(0,0,(LPTHREAD_START_ROUTINE)Go,0,0,0);
    }
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
} ^JSwozh1Q

(1) 内部绘制, 无需创建窗体: 没有 CreateWindowW() 的调用了

(2) CreateDeviceD3D();

(3) 没创建窗体, 自然不需要显示窗体: 无需调用 ShowWindow() ^NraHtHpg

001. Start ^OLOxTXQ4

015. DX11虚表HOOK ^i0N6BWyP

(1) 之前 D3D HOOK 是直接 hook api 的, 那种方式还是需要更新;

(2) 本节课我们通过交换链, 从交换链里找到它的虚表, 然后直接修改虚表的地址, 这种方式叫虚表hook, 其优点是不用更新;

(3) 什么是虚表: 
一个类, 其首位置会存放一个地址, 这个地址里存放的是一张表, 这张表就是把它每一个虚函数都罗列在里面; ^vfYHxeh4

typedef HRESULT(STDMETHODCALLTYPE* Present)(
    IDXGISwapChain* This,
    /* [in] */ UINT SyncInterval,
    /* [in] */ UINT Flags);
Present origPresent;

HRESULT MyPresent(
    IDXGISwapChain* This,
    /* [in] */ UINT SyncInterval,
    /* [in] */ UINT Flags)
{
    // 执行我们的代码
    printf("HOOK SUCCESS");// 形式化打印

    // 最后执行它原先的代码
    return origPresent(This,SyncInterval,Flags);
 }

DWORD MyThread(LPVOID lpThreadParameter)
{
    // 其他代码 ...

    printf("g_pSwapChain=%p", g_pSwapChain);      // 拿到交换链首地址

    DWORD64 addr64 = (*(DWORD64 *)g_pSwapChain); // 拿到虚表地址
    DWORD64 *VirtualTable = (DWORD64 *)addr64;   // 把虚表转换成数组
    origPresent =(Present)VirtualTable[8];       // 拿到原函数地址(渲染函数,会被高频调用)
    DWORD oldp, tmpp;
    VirtualProtect(VirtualTable,4096, PAGE_EXECUTE_READWRITE, &oldp);// 解除保护
    VirtualTable[8]=(DWORD64)MyPresent;
    VirtualProtect(VirtualTable, 4096, oldp, &tmpp); // 恢复保护

    // 其他代码 ...
} ^olPG1jmr

子类首地址 ^uGGuPFOl

虚表地址 ^sXq6jQI1

父类成员变量 ^nfb6DZx1

子类成员变量 ^sfwt1f0F

前面虚表首地址, 后面紧跟成员变量
(先父后子) ^sLTUM4uV

#include <iostream>

class Object {
public:
    int blood = 0x20;
    virtual void move() { }
    virtual void jump() { }
};

class BOSS : public Object {
public:
    int MP = 0x10;
    virtual void skill() { }
};

int main()
{
    BOSS boss;
    boss.jump();
    boss.move();
    boss.skill();
    return 0;
} ^Qhnlv90s

Object::move() ^j5w6OvuJ

Object::jump() ^rVVvpStJ

BOSS::skill() ^5j2ga6x2

(先父后子) ^gegiyGpa

016. ImGui内部绘制窗体的实现 ^2D1Dzmgp

(1) 游戏窗口它会自动调整分辨率, 如果你hook那个函数去释放它的话,
      当你去调整分辨率的时候, 它会崩溃的。 ^k7oWyne8

017. ImGui内部绘制hook窗口消息机制 ^PiCN3NTw

上一节课, 内部 ImGui 窗口绘制出来了, 然后鼠标无法拖动, 因为它接不到鼠标消息; ^WFRNKgN1

018. ImGui内部绘制解决游戏分辨率切换崩溃问题 ^iB3Ug2z6

其实就是资源释放放在合理的位置就行;

第七阶段UE专题\imgui\source\第18课代码.rar
下面是基于课堂代码梳理出来的核心代码，具体细节看相关代码。 ^lf5Id8B7

// 通过游戏窗口类名拿到窗口句柄
HWND hWndGame = FindWindowA("UnrealWindow",NULL);

DWORD MyThread(LPVOID lpThreadParameter) {

    DXGI_SWAP_CHAIN_DESC sd;
    ZeroMemory(&sd, sizeof(sd));
    sd.BufferCount = 2;
    sd.BufferDesc.Width = 0;
    sd.BufferDesc.Height = 0;
    sd.BufferDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
    sd.BufferDesc.RefreshRate.Numerator = 60;
    sd.BufferDesc.RefreshRate.Denominator = 1;
    sd.Flags = DXGI_SWAP_CHAIN_FLAG_ALLOW_MODE_SWITCH;
    sd.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
    sd.OutputWindow = hWndGame;
    sd.SampleDesc.Count = 1;
    sd.SampleDesc.Quality = 0;
    sd.Windowed = TRUE;
    sd.SwapEffect = DXGI_SWAP_EFFECT_DISCARD;

    UINT createDeviceFlags = 0;
    //createDeviceFlags |= D3D11_CREATE_DEVICE_DEBUG;
    D3D_FEATURE_LEVEL featureLevel;
    const D3D_FEATURE_LEVEL featureLevelArray[2] = { D3D_FEATURE_LEVEL_11_0, D3D_FEATURE_LEVEL_10_0, };
    HRESULT res = D3D11CreateDeviceAndSwapChain(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, 
        createDeviceFlags, featureLevelArray, 2, D3D11_SDK_VERSION, &sd, 
        &g_pSwapChain, &g_pd3dDevice, &featureLevel, &g_pd3dDeviceContext);
    if (res == DXGI_ERROR_UNSUPPORTED) // Try high-performance WARP software driver if hardware is not available.
        res = D3D11CreateDeviceAndSwapChain(nullptr, D3D_DRIVER_TYPE_WARP, nullptr, 
            createDeviceFlags, featureLevelArray, 2, D3D11_SDK_VERSION, &sd, 
            &g_pSwapChain, &g_pd3dDevice, &featureLevel, &g_pd3dDeviceContext);
    if (res != S_OK)
        return false;

    // 创建交换链: D3D11CreateDeviceAndSwapChain()

    // 拿到交换链
    printf("g_pSwapChain=%p", g_pSwapChain);

    // 通过交换链拿到虚表
    VirtualTable = *(DWORD64**)g_pSwapChain;
    origPresent =(Present)VirtualTable[8];
    DWORD oldvp, tmpvp;
    VirtualProtect(VirtualTable,4096, PAGE_EXECUTE_READWRITE, &oldvp);
    VirtualTable[8]=(DWORD64)MyInitFunc; // 首次执行需要初始化一些东西
    origResizeBuffers = (ResizeBuffers)VirtualTable[13];
    VirtualTable[13]=(DWORD64)MyResizeBuffers;
    VirtualProtect(VirtualTable, 4096, oldvp, &tmpvp); // 恢复权限

    return 0;
} ^lfwWE9tk

extern IMGUI_IMPL_API LRESULT ImGui_ImplWin32_WndProcHandler(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);
WNDPROC myWNDPROC;
LRESULT WINAPI WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    if (ImGui_ImplWin32_WndProcHandler(hWnd, msg, wParam, lParam))
        return true;

    return ::CallWindowProc(myWNDPROC,hWnd, msg, wParam, lParam);
}
HRESULT MyInitFunc(
    IDXGISwapChain* This,
    /* [in] */ UINT SyncInterval,
    /* [in] */ UINT Flags)
{
    This->GetDevice(__uuidof(g_pd3dDevice),(void**) &g_pd3dDevice);
    g_pd3dDevice->GetImmediateContext((ID3D11DeviceContext**)&g_pd3dDeviceContext);
    //printf("g_pSwapChain=%p,g_pd3dDevice=%p ,g_pd3dDeviceContext=%p This=%p", g_pSwapChain, g_pd3dDevice, g_pd3dDeviceContext, This);
    ID3D11Texture2D* pBackBuffer;
    This->GetBuffer(0, IID_PPV_ARGS(&pBackBuffer));

    g_pd3dDevice->CreateRenderTargetView(pBackBuffer, nullptr, &g_mainRenderTargetView);
    pBackBuffer->Release();


    // 只执行一次
    static bool isDone = false;
    if (!isDone)
    {
        // 设置回调(能够接收鼠标点击等消息)
        myWNDPROC = (WNDPROC)SetWindowLongPtrA(hWndGame, GWLP_WNDPROC, (LONG_PTR)WndProc);

        ImGui::CreateContext();
        ImGui::StyleColorsDark();
        ImGui_ImplWin32_Init(hWndGame);

        isDone = true;
    }

    // 由于修改分辨率时给它释放了, 所以要多次初始化
    ImGui_ImplDX11_Init(g_pd3dDevice, g_pd3dDeviceContext);

    // 第二次以后的虚函数执行就跳到 MyPresent
    VirtualTable[8] = (DWORD64)MyPresent;

    // 别忘了调用系统原来的函数
    return origPresent(This, SyncInterval, Flags);
} ^aO6Bl8Mn

HRESULT MyPresent(
    IDXGISwapChain* This,
    /* [in] */ UINT SyncInterval,
    /* [in] */ UINT Flags)
{
    // 开始正式绘制 ImGui 窗口

    // Start the Dear ImGui frame
    ImGui_ImplDX11_NewFrame();
    ImGui_ImplWin32_NewFrame();
    ImGui::NewFrame();

    ImGui::Begin("Hello, world!");
    ImGui::End();
    ImGui::Render();
    g_pd3dDeviceContext->OMSetRenderTargets(1, &g_mainRenderTargetView, nullptr);
    ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());
 
    // 别忘了调用系统原来的函数
    return origPresent(This,SyncInterval,Flags);
 } ^nfsxiwD7

HRESULT MyResizeBuffers(
    IDXGISwapChain* This,
    /* [in] */ UINT BufferCount,
    /* [in] */ UINT Width,
    /* [in] */ UINT Height,
    /* [in] */ DXGI_FORMAT NewFormat,
    /* [in] */ UINT SwapChainFlags)
{

    if (g_pd3dDevice)
    {
        // 当游戏换分辨率时,需要释放相关资源

        g_pd3dDevice->Release();
        g_pd3dDevice = nullptr;
        //g_pd3dDeviceContext->Release();
        g_mainRenderTargetView->Release();
        ImGui_ImplDX11_Shutdown();
        VirtualTable[8] = (DWORD64)MyInitFunc;
    }

    // 别忘了调用系统原来的函数
    return origResizeBuffers(This, BufferCount, Width, Height, NewFormat,SwapChainFlags);
} ^AhEWqsjT

为什么要释放相关资源？不释放不行吗？ ^xUa6ZHcs

// Setup Dear ImGui context
IMGUI_CHECKVERSION();
ImGui::CreateContext();


// Setup Dear ImGui style
ImGui::StyleColorsDark();


// Setup Platform/Renderer backends
ImGui_ImplWin32_Init(hwnd);
ImGui_ImplDX11_Init(g_pd3dDevice, g_pd3dDeviceContext);


// 上面是进入高频循环之前做的事
while (!done)
{
    // 高频主循环体


    // Handle window resize (we don't resize directly in the WM_SIZE handler)
    if (g_ResizeWidth != 0 && g_ResizeHeight != 0)
    {
        CleanupRenderTarget();
        g_pSwapChain->ResizeBuffers(0, g_ResizeWidth, g_ResizeHeight, DXGI_FORMAT_UNKNOWN, 0);
        g_ResizeWidth = g_ResizeHeight = 0;
        CreateRenderTarget();
    }


    // Start the Dear ImGui frame
    ImGui_ImplDX11_NewFrame();
    ImGui_ImplWin32_NewFrame();
    ImGui::NewFrame();


    // ImGui 窗体
    ImGui::Begin("Hello, world!");                          // Create a window called "Hello, world!" and append into it.
    ImGui::End();


    // (必备)Rendering
    ImGui::Render();
    g_pd3dDeviceContext->OMSetRenderTargets(1, &g_mainRenderTargetView, nullptr);
    ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());

    // Present
    HRESULT hr = g_pSwapChain->Present(1, 0);   // Present with vsync

} ^Na0LdXH9

修改窗口大小 ^WBS1Z2Ws

开始构建窗体 ^Icpmb7UN

启动ImGui模块 ^r65RCROY

执行自定义渲染 ^CsK6jl9T

执行系统渲染 ^s6MmKyqx

HWND = 画布的窗框
D3D11 = 画笔 + 画板
ImGui = 在画板上画画的人

(1) HWND 对 ImGui 的作用：只处理输入（鼠标 / 键盘），不负责画图。
(2) D3D11 对 ImGui 的作用：只负责渲染（把 UI 画出来）。
(3) 注入为什么不用创建窗口：因为游戏已经提供了窗口 + D3D画笔，你只需要偷过来给 ImGui 使用。 ^4MQoOJMz

（用官方独立例程代码去理解上面拆散的流程） ^ELzWBDKy

(1) FPS游戏和之前的游戏找法优点区别：
      (1) FPS是及时性要求比较高, 所有很多数据必须在本地处理, 比如骨骼渲染等;
      (2) 但是它对此反调试也很变态, 所以大部分无法通过OD来找数据, 所以我们基本纯靠CE找数据; ^3Eq7UNgI

sv_cheats  1    ——开启作弊模式
mp_roundtime_defuse  60    ——设置一局时长60分钟(方便长时间追数据)
bot_kill    ——杀死全部
bot_stop  1    ——全体定住
bot_add    ——随机增加一个bot
B键    ——买枪
hurtme  10    ——给自己掉10滴血 ^JxDwGwOA

FPS人物结构分析——FPS通过血量入手 ^IcnfuIYs

注意(踩坑经验): 中文显示问号, 说明带中文字符串的源码文件必须要是utf-8编码 ^wET0SOgY

## Embedded Files
fec5679b01539f6aed04cbe2eedb50d2def1bd91: [[Pasted Image 20260521222631_332.png]]

1765f6d8d331384796cef58cc773779de9598266: [[Pasted Image 20260521223605_313.png]]

59ea2c66c073fbef60d5754e1ced8ad1d3ddcbd9: [[Pasted Image 20260522111525_043.png]]

cd1c87eea3fcde1c0fa14c468ea99b7874be8bac: [[Pasted Image 20260522111542_824.png]]

51b53df42236b0191918edca655072627b97b233: [[Pasted Image 20260523220304_708.png]]

%%
## Drawing
```compressed-json
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=
```
%%