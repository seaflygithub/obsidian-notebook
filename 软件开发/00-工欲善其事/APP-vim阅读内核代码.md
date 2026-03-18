
**为什么会有这个项目？** 因为在大项目中比如内核代码中，其他编辑器要么就是占用内存太高以及卡顿，要么就是几乎无法满足基本的代码跟踪阅读需求。而vim由于是底层语言开发，对资源方面的占用没那么高，于是催生了这种想法。

链接1: https://gitee.com/SeaflyGitee/vimkernel
链接2: https://github.com/seaflygithub/vimkernel

vimkernel 名字主要是由于作者主要用它来查看和修改 linux 内核代码，因此取了这个名字。

vimkernel主要还是依赖 vim + cscope + ctags 组合，尽量保证原汁原味的vim操作风格，网上提供的常规的部署，对于大型项目的使用，比较低效；相比于常规的组合使用，vimkernel有以下特点：

- 多线程生成索引数据库文件(对于代码量大的工程有显著优势)
- 启动 vim 时，自动加载索引数据库文件(在生成vimkernel所需目录时有效)
- 关闭 vim 时，自动保存会话文件(保留当前窗口布局)
- 执行 vim 写入文件时(:w,:wall)，自动重新生成索引数据库文件并自动导入到vim。

其他常规的 vim+cscope+ctags 组合具备的功能：

- 支持结构体成员引用提示补全(Omni插件)
- 支持cscope相关的查找操作；
- 支持ctags相关的查找操作；
- 支持全局文件查找（LookupFile插件）
- 支持高亮标记（mark插件）


C++语言版本(vim_project_update.cpp)：
- [x] ——结构体补全
- [x] ——SrcExpl预览能够正常使用
- [x] ——顶层查找文件
- [x] ——子目录层查找文件
- [x] ——启动其他窗口布局会破坏tags的pwd目录(会变成对应的子目录)
- [x] ——vim缺乏一个workspace机制导致pwd变更时tags索引无法正常工作
- [x] ——SrcExpl插件预览窗口一旦启动会导致pwd变更
- [x] ——把整个HOME/.vim拷贝出来全局搜索确实有chdir操作(尤其SrcExpl插件)
- [x] ——修复办法：通过chdir字符串全局查找，注释掉所有相关chdir的插件代码






