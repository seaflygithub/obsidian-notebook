[TOC]


# shell-内置字符串处理

参考文章：
shell脚本中的字符串处理（长度，读取，替换，截取，分割）
https://blog.csdn.net/m0_51971452/article/details/115263995

---

## 字串长度

```bash
str="123456"
echo ${#str}   #6
```

---

## 按下标截取字符串

```bash
${string:${index}}
${string:${index}:${length}}

str_var1="123456789abcdef"
echo ${str_var1:3} #456789abcdef
echo ${str_var1:3:6} #456789
```

---

## 删除字串

- 下面一个井号表示从左往右开始匹配，匹配到第一个，就执行删除操作，所过之处，寸草不生。
- 下面两个井号表示从左往右开始匹配，匹配到最后一个，就执行删除操作，所过之处，寸草不生。
![[image_20240925080956.png]]

- 下面一个百分号表示从右往左开始匹配，匹配到第一个，就执行删除操作，所过之处，寸草不生。
- 下面两个百分号表示从右往左开始匹配，匹配到最后一个，就执行删除操作，所过之处，寸草不生。
![[image_20240925100940.png]]

---

## 替换字串

- <font size=4>${var_str3</font><font size=5 color=red>/</font><font size=4>str111/str222}</font>
- 从左往右匹配，匹配到第一个，则执行替换。
```bash
var_str3="hello_world_shell_great_linux_tool"
echo ${var_str3/shell/clang}
echo ${var_str3/"shell"/"clang"}
#hello_world_clang_great_linux_tool
```


- <font size=4>${var_str3</font><font size=5 color=red>//</font><font size=4>str111/str222}</font>
- 从左往右匹配，替换所有匹配到的项。
```bash
var_str3="hello_world_shell_great_linux_tool"
echo ${var_str3//"_"/"@@@@@@"}
#hello_world_shell_great@@@@@@linux_tool
```



# TCL






# bottom



