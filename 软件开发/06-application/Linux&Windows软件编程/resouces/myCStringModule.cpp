#include "stdafx.h"
#include <vector>
#include <stack>
#include <algorithm>

// 辅助函数：检查字符串是否包含子串（不区分大小写）
static BOOL ContainsIgnoreCase(const CString& str, const CString& subStr)
{
	if (subStr.IsEmpty()) return TRUE;
	CString strLower = str;
	CString subLower = subStr;
	strLower.MakeLower();
	subLower.MakeLower();
	return strLower.Find(subLower) != -1;
}

// 辅助函数：将过滤字符串转换为逆波兰表达式（RPN）
static BOOL ParseToRPN(const CString& filterStr, std::vector<CString>& rpn, CString& errorMsg)
{
	std::stack<CString> opStack;
	int len = filterStr.GetLength();
	errorMsg.Empty();

	for (int i = 0; i < len; i++)
	{
		TCHAR ch = filterStr[i];

		// 跳过空格
		if (ch == _T(' ')) continue;

		// 处理左括号
		if (ch == _T('('))
		{
			opStack.push(_T("("));
		}
		// 处理右括号
		else if (ch == _T(')'))
		{
			while (!opStack.empty() && opStack.top() != _T("("))
			{
				rpn.push_back(opStack.top());
				opStack.pop();
			}
			if (opStack.empty())
			{
				errorMsg = _T("括号不匹配：缺少左括号");
				return FALSE;
			}
			opStack.pop(); // 弹出左括号
		}
		// 处理操作符 && 和 ||
		else if (ch == _T('&') && i + 1 < len && filterStr[i + 1] == _T('&'))
		{
			while (!opStack.empty() && opStack.top() != _T("("))
			{
				CString top = opStack.top();
				// && 优先级高于 ||，所以遇到 && 时，只能弹出栈顶的 &&
				if (top == _T("&&"))
				{
					rpn.push_back(top);
					opStack.pop();
				}
				else break;
			}
			opStack.push(_T("&&"));
			i++; // 跳过第二个 &
		}
		else if (ch == _T('|') && i + 1 < len && filterStr[i + 1] == _T('|'))
		{
			while (!opStack.empty() && opStack.top() != _T("("))
			{
				CString top = opStack.top();
				// || 优先级最低，弹出所有栈顶操作符
				if (top == _T("&&") || top == _T("||"))
				{
					rpn.push_back(top);
					opStack.pop();
				}
				else break;
			}
			opStack.push(_T("||"));
			i++; // 跳过第二个 |
		}
		// 处理操作数（关键词）
		else
		{
			CString keyword;
			while (i < len && filterStr[i] != _T(' ') && filterStr[i] != _T('&') &&
				filterStr[i] != _T('|') && filterStr[i] != _T('(') && filterStr[i] != _T(')'))
			{
				keyword += filterStr[i];
				i++;
			}
			i--; // 回退一个位置，因为外层循环会自增
			rpn.push_back(keyword);
		}
	}

	// 弹出剩余的操作符
	while (!opStack.empty())
	{
		CString top = opStack.top();
		if (top == _T("("))
		{
			errorMsg = _T("括号不匹配：缺少右括号");
			return FALSE;
		}
		rpn.push_back(top);
		opStack.pop();
	}

	return TRUE;
}

// 辅助函数：计算逆波兰表达式的值
static BOOL EvaluateRPN(const std::vector<CString>& rpn, const CString& deviceId)
{
	std::stack<BOOL> valueStack;

	for (size_t i = 0; i < rpn.size(); i++)
	{
		const CString& token = rpn[i];

		if (token == _T("&&"))
		{
			if (valueStack.size() < 2) return FALSE;
			BOOL right = valueStack.top(); valueStack.pop();
			BOOL left = valueStack.top(); valueStack.pop();
			valueStack.push(left && right);
		}
		else if (token == _T("||"))
		{
			if (valueStack.size() < 2) return FALSE;
			BOOL right = valueStack.top(); valueStack.pop();
			BOOL left = valueStack.top(); valueStack.pop();
			valueStack.push(left || right);
		}
		else
		{
			// 操作数：检查设备ID是否包含该关键词
			valueStack.push(ContainsIgnoreCase(deviceId, token));
		}
	}

	if (valueStack.size() != 1) return FALSE;
	return valueStack.top();
}

// 主函数：根据过滤字符串筛选设备实例ID
BOOL GetFilterItems(const CString& filterStr,
	const std::vector<CString>& vecInstanceIds,
	std::vector<CString>& outItems)
{
	// 清空输出容器
	outItems.clear();

	// 如果过滤字符串为空，返回所有设备
	if (filterStr.IsEmpty() || filterStr.Find(_T(" ")) == -1 && filterStr.GetLength() == 0)
	{
		outItems = vecInstanceIds;
		return TRUE;
	}

	// 解析过滤表达式为逆波兰表达式
	std::vector<CString> rpn;
	CString errorMsg;
	if (!ParseToRPN(filterStr, rpn, errorMsg))
	{
		// 解析失败，可以选择返回所有设备或者返回FALSE
		TRACE(_T("过滤表达式解析失败: %s\n"), errorMsg);
		outItems = vecInstanceIds;  // 失败时返回所有设备
		return FALSE;
	}

	// 对每个设备ID进行筛选
	for (size_t i = 0; i < vecInstanceIds.size(); i++)
	{
		if (EvaluateRPN(rpn, vecInstanceIds[i]))
		{
			outItems.push_back(vecInstanceIds[i]);
		}
	}

	return TRUE;
}