#pragma once
#include "stdafx.h"
#include <afxstr.h>
#include <vector>
BOOL GetFilterItems(const CString& filterStr,
	const std::vector<CString>& vecInstanceIds,
	std::vector<CString>& outItems);

