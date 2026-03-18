

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






































