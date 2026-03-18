import os
import re
import shutil
from pathlib import Path
from typing import List, Union, Optional
import configparser

def get_all_md_files(
    root_dir: Union[str, Path] = ".",  # 默认遍历当前目录
    recursive: bool = True,            # 是否递归遍历子目录
    exclude_dirs: Optional[List[str]] = None  # 排除的目录（如.git、node_modules）
) -> List[Path]:
    """
    遍历指定目录下所有.md文件，返回完整路径列表
    
    Args:
        root_dir: 根目录路径（相对/绝对路径，默认当前目录）
        recursive: 是否递归遍历子目录（True=递归，False=仅当前目录）
        exclude_dirs: 需排除的目录名列表（如["resources", ".git"]）
    
    Returns:
        List[Path]: 所有.md文件的Path对象列表（含完整路径）
    
    Raises:
        FileNotFoundError: 指定的根目录不存在
        NotADirectoryError: 传入的root_dir不是目录
    """
    # 初始化排除目录列表（默认空）
    exclude_dirs = exclude_dirs or []
    # 统一路径处理为Path对象
    root_path = Path(root_dir).absolute()
    
    # 校验根目录合法性
    if not root_path.exists():
        raise FileNotFoundError(f"根目录不存在: {root_path}")
    if not root_path.is_dir():
        raise NotADirectoryError(f"传入的路径不是目录: {root_path}")
    
    # 存储所有.md文件的Path对象
    md_files = []
    
    # 遍历目录
    if recursive:
        # 递归遍历所有子目录
        for file_path in root_path.rglob("*.md"):
            # 跳过排除目录下的文件
            if any(excl_dir in file_path.parts for excl_dir in exclude_dirs):
                continue
            md_files.append(file_path)
    else:
        # 仅遍历当前目录，不递归
        for file_path in root_path.glob("*.md"):
            if any(excl_dir in file_path.parts for excl_dir in exclude_dirs):
                continue
            md_files.append(file_path)
    
    # 按路径排序，提升可读性
    md_files.sort()
    
    return md_files


def convert_markdown_refs_to_obsidian(md_files: List[Union[str, Path]], backup: bool = True) -> None:
    """
    将Markdown文件中的标准引用格式转换为Obsidian双括号格式
    转换规则：
    1. ![描述](路径/文件名) → ![[文件名]]
    2. [描述](路径/文件名) → [[文件名]]
    3. 自动剔除括号内的路径信息，仅保留文件名
    
    Args:
        md_files: .md文件路径列表（str/Path对象均可）
        backup: 是否备份原文件（备份文件后缀为 .bak）
    
    Raises:
        FileNotFoundError: 文件不存在
        PermissionError: 无文件读写权限
        Exception: 其他转换异常
    """
    # 正则表达式匹配规则（覆盖所有场景）
    # 匹配图片引用：![任意描述](路径/文件名)
    img_pattern = re.compile(r"!\[(.*?)\]\((.*?)\)", re.UNICODE)
    # 匹配链接引用：[任意描述](路径/文件名)
    link_pattern = re.compile(r"\[(.*?)\]\((.*?)\)", re.UNICODE)

    # 遍历每个MD文件
    for md_file in md_files:
        md_path = Path(md_file)
        print(f"开始处理文件：{md_path.absolute()}")

        # 校验文件合法性
        if not md_path.exists():
            print(f"❌ 跳过：文件不存在 - {md_path}")
            continue
        if md_path.suffix != ".md":
            print(f"❌ 跳过：非MD文件 - {md_path}")
            continue

        try:
            # 读取文件内容
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
            original_content = content  # 备份原始内容

            # ------------------- 第一步：转换图片引用 ![]() → ![]] -------------------
            def replace_img(match):
                # match.group(1) = 描述文本，match.group(2) = 带路径的文件名
                full_path = match.group(2).strip()
                # 剔除路径，仅保留文件名
                filename = Path(full_path).name
                return f"![[{filename}]]"
            content = img_pattern.sub(replace_img, content)

            # ------------------- 第二步：转换链接引用 []() → []] -------------------
            def replace_link(match):
                # match.group(1) = 描述文本，match.group(2) = 带路径的文件名
                full_path = match.group(2).strip()
                # 剔除路径，仅保留文件名
                filename = Path(full_path).name
                return f"[[{filename}]]"
            content = link_pattern.sub(replace_link, content)

            # ------------------- 第三步：写入文件（先备份） -------------------
            if content != original_content:
                # 备份原文件（可选）
                if backup:
                    backup_path = md_path.with_suffix(".md.bak")
                    with open(backup_path, "w", encoding="utf-8") as f:
                        f.write(original_content)
                    print(f"✅ 已备份原文件至：{backup_path}")

                # 写入转换后的内容
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ 转换完成：{md_path}")
            else:
                print(f"ℹ️ 无需转换：{md_path}（未发现标准引用格式）")

        except PermissionError:
            print(f"❌ 跳过：无读写权限 - {md_path}")
        except Exception as e:
            print(f"❌ 处理失败：{md_path} | 错误：{type(e).__name__} - {e}")




def is_header_ref(ref: str) -> bool:
    """
    判断单个引用是否为Obsidian的标题引用（格式：[[#标题]]）
    
    Args:
        ref: 提取出的[[内的原始内容（已去首尾空格）
        
    Returns:
        bool: True=标题引用，False=非标题引用
    """
    # 标题引用特征：去空格后首字符是 #
    stripped_ref = ref.strip()
    return len(stripped_ref) > 0 and stripped_ref[0] == "#"

def is_footnote_ref(ref: str) -> bool:
    """
    判断单个引用是否为Obsidian的文本块/脚注引用（格式：[[^文本块]]）
    
    Args:
        ref: 提取出的[[内的原始内容（已去首尾空格）
        
    Returns:
        bool: True=文本块引用，False=非文本块引用
    """
    # 文本块引用特征：去空格后首字符是 ^
    stripped_ref = ref.strip()
    return len(stripped_ref) > 0 and stripped_ref[0] == "^"


def get_filerefs_from_md(mdfile: Union[str, Path]) -> List[str]:
    """
    读取Markdown文件，提取所有Obsidian格式的文件引用（[[文件名]]）中的文件名
    过滤掉标题引用（[[#标题]]）和文本块引用（[[^文本块]]）
    
    Args:
        mdfile: Markdown文件的路径（相对路径/绝对路径，str或Path对象）
        
    Returns:
        List[str]: 提取出的所有文件引用列表（去重、空值过滤）
        
    Raises:
        FileNotFoundError: 指定的MD文件不存在
        PermissionError: 无权限读取MD文件
        IsADirectoryError: 传入的路径是目录而非文件
    """
    # 统一路径处理为Path对象，兼容str/Path输入
    md_path = Path(mdfile)
    
    # 校验文件合法性
    if not md_path.exists():
        raise FileNotFoundError(f"MD文件不存在: {md_path.absolute()}")
    if md_path.is_dir():
        raise IsADirectoryError(f"传入的路径是目录，不是文件: {md_path.absolute()}")
    
    # 正则表达式匹配Obsidian引用格式 [[xxx]]
    ref_pattern = re.compile(r"\[\[([^\]]+)\]\]", re.UNICODE)
    
    # 读取MD文件内容（UTF-8编码，兼容中文）
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
    except PermissionError as e:
        raise PermissionError(f"无权限读取文件: {md_path.absolute()}") from e
    
    # 提取所有匹配的引用内容
    raw_refs = ref_pattern.findall(md_content)
    
    # 数据清洗：过滤标题/文本块引用 + 去重 + 空值过滤 + 去首尾空格
    cleaned_refs = []
    for ref in raw_refs:
        stripped_ref = ref.strip()
        # 新增：跳过空引用、标题引用、文本块引用
        if not stripped_ref:
            continue
        if is_header_ref(stripped_ref) or is_footnote_ref(stripped_ref):
            continue
        # 去重后加入结果列表
        if stripped_ref not in cleaned_refs:
            cleaned_refs.append(stripped_ref)
    
    return cleaned_refs
    
def unify_path_separator(path_str: Union[str, Path]) -> str:
    # """
    # 统一路径分隔符为正斜杠（/），适配Windows/macOS/Linux
    # 处理场景：
    # 1. Windows反斜杠（\）→ 正斜杠（/）
    # 2. 混合分隔符（如 D:/test\subdir\file.md）→ 统一为 D:/test/subdir/file.md
    # 3. 兼容Path对象/字符串输入
    # 4. 保留Windows盘符（如 C:\ → C:/）、网络路径（\\server\share → //server/share）
    # 
    # Args:
    #     path_str: 路径字符串或Path对象（支持绝对/相对路径）
    # 
    # Returns:
    #     str: 分隔符统一为正斜杠的路径字符串
    # """
    
    
    # 1. 统一转换为字符串（兼容Path对象输入）
    if isinstance(path_str, Path):
        path_str = str(path_str)
    
    # 2. 处理Windows反斜杠（注意：字符串中\需要转义为\\）
    # 先替换双反斜杠（网络路径如\\server\share）为双正斜杠
    unified_path = path_str.replace("\\\\", "//")
    # 再替换单个反斜杠为正斜杠
    unified_path = unified_path.replace("\\", "/")
    
    # 3. 特殊处理：避免Windows盘符后出现双斜杠（如 C://test → C:/test）
    if len(unified_path) >= 2 and unified_path[1] == ":":
        # 匹配 C:/、D:/ 等盘符格式
        unified_path = f"{unified_path[0]}:/{unified_path[3:]}" if len(unified_path) > 3 and unified_path[2] == "/" else unified_path
    
    return unified_path
    
def add_path_to_refs(refs: List[str], base_path: str = "resources/") -> List[str]:
    """
    给提取出的引用文件名统一添加路径前缀
    
    Args:
        refs: get_filerefs_from_md返回的引用列表
        base_path: 要添加的路径前缀（默认 resources/）
        
    Returns:
        List[str]: 带路径的文件名列表
    """
    # 确保路径前缀以/结尾（避免拼接错误，如resourceabc.png）
    normalized_path = base_path.rstrip("/") + "/" if base_path else ""
    
    # 拼接路径
    ref_with_path = []
    for ref in refs:
        # 避免重复添加路径（如原引用已带resources/）
        if not ref.startswith(normalized_path):
            ref_with_path.append(f"{normalized_path}{ref}")
        else:
            ref_with_path.append(ref)
    
    return ref_with_path
    

def migrate_obsidian_note(
    mdfile: Union[str, Path],
    srcdir: Union[str, Path],
    dstdir: Union[str, Path],
    backup: bool = True
) -> None:
    """
    迁移Obsidian笔记及关联资源文件
    适配Obsidian特性：自动补全.md后缀、确保笔记文件和资源都被迁移
    :param mdfile: 要迁移的MD文件名（支持无.md后缀，如"笔记1"或"笔记1.md"）
    :param srcdir: 源目录（MD文件所在目录）
    :param dstdir: 目标目录（迁移后的目录）
    :param backup: 是否备份目标目录下已存在的同名文件
    """
    # 1. 路径标准化处理
    srcdir = Path(srcdir).absolute()
    dstdir = Path(dstdir).absolute()

    # ========== 核心新增：自动补全.md后缀逻辑 ==========
    # 处理输入的mdfile，优先尝试原名称，不存在则补.md后缀
    mdfile_str = str(mdfile)
    src_md_path = srcdir / mdfile_str  # 原始路径
    # 检查是否存在，不存在则补.md后缀
    if not src_md_path.exists():
        # 避免重复加.md（如输入"笔记1.md.md"）
        if not mdfile_str.endswith(".md"):
            src_md_path = srcdir / f"{mdfile_str}.md"
            print(f"⚠️  原始文件 {srcdir/mdfile_str} 不存在，尝试补全.md后缀：{src_md_path}")
        else:
            raise FileNotFoundError(f"源笔记文件不存在：{srcdir/mdfile_str}")
    
    # 确认最终的笔记文件名（带.md）
    final_md_filename = src_md_path.name
    dst_md_path = dstdir / final_md_filename  # 目标MD文件完整路径

    # ========== 资源目录定义 ==========
    src_res_dir = srcdir / "resources"    # 源资源目录
    dst_res_dir = dstdir / "resources"    # 目标资源目录

    # 2. 前置校验
    # 最终校验源MD文件是否存在且为MD文件
    if not src_md_path.exists():
        raise FileNotFoundError(f"补全.md后缀后，源笔记文件仍不存在：{src_md_path}")
    if src_md_path.suffix != ".md":
        raise TypeError(f"文件不是MD格式：{src_md_path}")
    
    # 校验源资源目录（不存在则跳过资源迁移）
    src_res_exists = src_res_dir.exists() and src_res_dir.is_dir()

    # 3. 创建目标目录（含resources）
    dstdir.mkdir(parents=True, exist_ok=True)
    dst_res_dir.mkdir(exist_ok=True)

    # 4. 提取MD文件中的引用资源列表
    print(f"🔍 解析 {final_md_filename} 中的资源引用...")
    ref_files = get_filerefs_from_md(src_md_path)
    if not ref_files and src_res_exists:
        print(f"⚠️  {final_md_filename} 中未发现有效资源引用，仅迁移笔记文件")
    elif not ref_files and not src_res_exists:
        print(f"⚠️  {final_md_filename} 中无资源引用，且源目录无resources目录，仅迁移笔记文件")

    # 5. 迁移关联资源文件
    migrated_res = []
    if ref_files and src_res_exists:
        print(f"📦 开始迁移 {len(ref_files)} 个关联资源...")
        for ref_file in ref_files:
            src_res_file = src_res_dir / ref_file
            dst_res_file = dst_res_dir / ref_file
            
            # 跳过不存在的资源文件
            if not src_res_file.exists():
                print(f"❌ 资源文件不存在，跳过：{src_res_file}")
                continue
            
            # 备份目标目录已存在的同名文件
            if dst_res_file.exists() and backup:
                backup_suffix = 1
                while True:
                    backup_file = dst_res_file.with_suffix(f"{dst_res_file.suffix}.bak{backup_suffix}")
                    if not backup_file.exists():
                        shutil.copy2(dst_res_file, backup_file)
                        print(f"📋 备份已存在的资源文件：{backup_file}")
                        break
                    backup_suffix += 1
            
            # 移动资源文件（覆盖已存在文件）
            shutil.move(str(src_res_file), str(dst_res_file))
            migrated_res.append(ref_file)
            print(f"✅ 迁移资源：{src_res_file} → {dst_res_file}")

    # 6. 迁移MD笔记文件（强化逻辑，确保笔记文件必迁移）
    print(f"📄 迁移笔记文件 {final_md_filename}...")
    # 备份目标目录已存在的同名笔记
    if dst_md_path.exists() and backup:
        # 避免备份文件重复（如.md.bak1、.md.bak2）
        backup_suffix = 1
        while True:
            backup_md = dst_md_path.with_suffix(f".md.bak{backup_suffix}")
            if not backup_md.exists():
                shutil.copy2(dst_md_path, backup_md)
                print(f"📋 备份已存在的笔记文件：{backup_md}")
                break
            backup_suffix += 1
    
    # 移动笔记文件（核心：确保笔记文件本身被搬运）
    shutil.move(str(src_md_path), str(dst_md_path))
    print(f"✅ 迁移笔记：{src_md_path} → {dst_md_path}")

    # 7. 清理空的源resources目录（可选）
    if src_res_exists and not os.listdir(src_res_dir):
        src_res_dir.rmdir()
        print(f"🧹 源resources目录已空，删除：{src_res_dir}")

    # 8. 输出迁移总结
    print("\n🎉 迁移完成！")
    print(f"📝 笔记文件：{final_md_filename}")
    print(f"📂 源目录：{srcdir} → 目标目录：{dstdir}")
    if migrated_res:
        print(f"📦 迁移资源数：{len(migrated_res)} | 资源列表：{migrated_res}")
    else:
        print(f"📦 迁移资源数：0")



# 递归向上查找资源
def find_resource_upwards(
    filename: str,
    start_dir: Union[str, Path],
    vault_root: Union[str, Path]
) -> Optional[Path]:
    """
    从 start_dir 开始，逐层向上查找 resources/filename
    
    查找规则：
    start_dir/resources/
    ↑
    parent/resources/
    ↑
    ...
    ↑
    vault_root/resources/
    """

    current_dir = Path(start_dir).absolute()
    vault_root = Path(vault_root).absolute()

    while True:
        candidate = current_dir / "resources" / filename
        if candidate.exists():
            return candidate

        # 到顶层就停止
        if current_dir == vault_root:
            break

        # 防止越界（安全保护）
        if vault_root not in current_dir.parents and current_dir != vault_root:
            break

        current_dir = current_dir.parent

    return None


# 复制 Obsidian 笔记，包括其引用的本地笔记资源文件
def copy_obsidian_note(
    mdfile: Union[str, Path],
    srcdir: Union[str, Path],
    dstdir: Union[str, Path],
    vault_root: Union[str, Path],
    backup: bool = True
) -> None:
    """
    拷贝 Obsidian 笔记及其引用的资源文件（不会删除源文件）

    主要用于：
    - 笔记分享（导出单篇或部分笔记）
    - 避免暴露整个 Obsidian 仓库（vault）
    - 自动收集并复制该笔记依赖的资源文件（图片、附件、Excalidraw等）

    支持特性：
    - 自动补全 .md 后缀（兼容 Obsidian 无后缀引用）
    - 向上递归查找资源文件（resources 目录逐层向上搜索）
    - Windows / Linux 路径兼容（建议配合 unify_path_separator 使用）
    - fallback 机制（如 xxx → xxx.md）

    Args:
        mdfile (Union[str, Path]):
            要拷贝的笔记文件名或路径。
            支持：
            - "笔记A"
            - "笔记A.md"
            - 相对路径或绝对路径（建议配合 srcdir 使用）

        srcdir (Union[str, Path]):
            源目录（笔记所在目录）。
            通常为笔记所在的文件夹路径。

        dstdir (Union[str, Path]):
            目标目录（拷贝输出目录）。
            函数会在该目录下：
            - 创建目标 MD 文件
            - 创建 resources 子目录（用于存放引用资源）

        vault_root (Union[str, Path]):
            Obsidian 仓库（vault）顶层目录（⚠️ 非常关键参数）。

            用于限制资源查找范围，防止无限向上搜索。

            资源查找路径规则：
                srcdir/resources/
                → 上一级/resources/
                → 再上一级/resources/
                → ...
                → vault_root/resources/

            一旦超过该目录，停止查找。

        backup (bool, optional):
            是否对目标目录中已存在的同名文件进行备份（默认 True）。

            备份规则：
            - 资源文件：xxx.png → xxx.png.bak1 / .bak2 ...
            - 笔记文件：xxx.md → xxx.md.bak1 / .bak2 ...

    Raises:
        FileNotFoundError:
            当源 MD 文件不存在（含补全 .md 后仍不存在）

        TypeError:
            当目标文件不是 .md 文件

        PermissionError:
            文件读写权限不足时

    Notes:
        - 本函数不会修改源文件（仅 copy，不 move）
        - 不会修改 Markdown 内容（不会重写引用路径）
        - 仅复制当前 MD 的“直接引用资源”，不会递归复制子笔记（[[xxx]]）

    Example:
        >>> copy_obsidian_note(
        >>>     mdfile="zynq-axi-dma",
        >>>     srcdir="E:/obsidian/驱动-zynq系列",
        >>>     dstdir="E:/share/zynq-note",
        >>>     vault_root="E:/obsidian",
        >>>     backup=False
        >>> )
    """

    srcdir = Path(srcdir).absolute()
    dstdir = Path(dstdir).absolute()
    vault_root = Path(vault_root).absolute()

    # ========= 1. 处理 md 文件 =========
    mdfile_str = str(mdfile)
    src_md_path = srcdir / mdfile_str

    if not src_md_path.exists():
        if not mdfile_str.endswith(".md"):
            src_md_path = srcdir / f"{mdfile_str}.md"
            print(f"⚠️ 自动补全.md → {src_md_path}")
        else:
            raise FileNotFoundError(f"文件不存在: {src_md_path}")

    if not src_md_path.exists():
        raise FileNotFoundError(f"最终仍不存在: {src_md_path}")

    final_name = src_md_path.name
    dst_md_path = dstdir / final_name

    # ========= 2. 创建目录 =========
    dstdir.mkdir(parents=True, exist_ok=True)
    dst_res_dir = dstdir / "resources"
    dst_res_dir.mkdir(exist_ok=True)

    # ========= 3. 解析引用 =========
    print(f"🔍 解析引用: {final_name}")
    refs = get_filerefs_from_md(src_md_path)

    # ========= 4. 拷贝资源 =========
    copied = []

    # for ref in refs:
    #     src_res = find_resource_upwards(ref, srcdir, vault_root)

    #     if not src_res:
    #         print(f"❌ 未找到资源: {ref}")
    #         continue

    #     dst_res = dst_res_dir / ref

    #     # 备份
    #     if dst_res.exists() and backup:
    #         i = 1
    #         while True:
    #             bak = dst_res.with_suffix(f"{dst_res.suffix}.bak{i}")
    #             if not bak.exists():
    #                 shutil.copy2(dst_res, bak)
    #                 print(f"📋 备份: {bak}")
    #                 break
    #             i += 1

    #     shutil.copy2(src_res, dst_res)
    #     copied.append(ref)
    #     print(f"✅ 拷贝资源: {src_res} → {dst_res}")


    for ref in refs:
        fallback_used = False

        # ========= 1. 正常查找 =========
        src_res = find_resource_upwards(ref, srcdir, vault_root)

        # ========= 2. fallback 查找 =========
        if not src_res:

            # Obsidian 的“弱引用模型”，Obsidian 允许 [[xxx.excalidraw]]，但真实文件是 xxx.excalidraw.md
            alt_ref = f"{ref}.md"
            src_res = find_resource_upwards(alt_ref, srcdir, vault_root)
            
            if src_res:
                fallback_used = True
                print(f"⚠️ 使用 fallback：{ref} → {alt_ref}")

        # ========= 3. 未找到 =========
        if not src_res:
            print(f"❌ 未找到资源（含 fallback）：{ref}")
            continue

        # ========= 4. 目标路径 =========
        dst_res = dst_res_dir / src_res.name  # 推荐：保留真实文件名

        # ========= 5. 备份 =========
        if dst_res.exists() and backup:
            i = 1
            while True:
                bak = dst_res.with_suffix(f"{dst_res.suffix}.bak{i}")
                if not bak.exists():
                    shutil.copy2(dst_res, bak)
                    print(f"📋 备份: {bak}")
                    break
                i += 1

        # ========= 6. 拷贝 =========
        shutil.copy2(src_res, dst_res)

        if fallback_used:
            print(f"✅ 拷贝资源（fallback）：{src_res} → {dst_res}")
        else:
            print(f"✅ 拷贝资源：{src_res} → {dst_res}")




    # ========= 5. 拷贝 MD =========
    if dst_md_path.exists() and backup:
        i = 1
        while True:
            bak = dst_md_path.with_suffix(f".md.bak{i}")
            if not bak.exists():
                shutil.copy2(dst_md_path, bak)
                print(f"📋 备份MD: {bak}")
                break
            i += 1

    shutil.copy2(src_md_path, dst_md_path)
    print(f"📄 拷贝MD: {src_md_path} → {dst_md_path}")

    # ========= 6. 总结 =========
    print("\n🎉 拷贝完成")
    print(f"📦 资源数: {len(copied)}")



def demo_copy_obsidian_note():
    md = "DDR3"
    src = r"E:\project\notebook\obsidian-notebook\软件开发\05-drivers\方向：高速接口\ZYNQPL快速学习"
    dst = r"E:\project\testshare"
    root = r"E:\project\notebook\obsidian-notebook"   # 🔥 vault顶层

    copy_obsidian_note(
        mdfile=md,
        srcdir=unify_path_separator(src),
        dstdir=unify_path_separator(dst),
        vault_root=unify_path_separator(root),
        backup=False
    )


def demo_unify_path_separator():
    # 测试不同场景的路径
    test_paths = [
        # Windows绝对路径（反斜杠）
        r"C:\Users\test\笔记1.md",
        # Windows混合分隔符
        r"D:/Obsidian\驱动-zynq系列\zynq-axi-dma.md",
        # Windows网络路径
        r"\\192.168.1.100\共享目录\resources\test.png",
        # 相对路径（反斜杠）
        r"软件开发\驱动-zynq系列",
        # Path对象输入
        Path(r"E:\files\test.zip"),
        # Linux/macOS路径（正斜杠，无需处理）
        "/home/user/obsidian/笔记.md"
    ]
    
    print("路径转换测试结果：")
    print("-" * 80)
    for raw_path in test_paths:
        converted_path = unify_path_separator(raw_path)
        print(f"原始路径：{raw_path}")
        print(f"转换后：{converted_path}")
        print("-" * 80)

def demo_convert_markdown_refs_to_obsidian():
    # 当前目录，可替换为绝对路径如"D:/Obsidian/笔记"
    TARGET_DIR = "."
    # 排除无需处理的目录
    EXCLUDE_DIRS = [
        ".obsidian", ".git", 
        "__pycache__", ".trash", "Excalidraw"]
    
    # 调用函数获取所有.md文件
    md_files = get_all_md_files(
        root_dir=TARGET_DIR,
        recursive=True,
        exclude_dirs=EXCLUDE_DIRS
    )
    print(f"找到 {len(md_files)} 个MD文件，开始转换...\n")
    
    # 2. 执行格式转换（开启备份）
    convert_markdown_refs_to_obsidian(md_files, backup=False)

    print("\n🎉 所有文件处理完成！")
    
def demo_migrate_obsidian_note():
    # 配置迁移参数
    # 要迁移的笔记文件名
    mdf = r"zynq-axi-dma.md"
    src = r"E:\project\notebook\obsidian-notebook\软件开发\驱动-zynq系列"
    dst = r"E:\project\notebook\obsidian-notebook\软件开发\05-drivers\驱动-zynq-axi-dma"
    
    unify_srcdir = unify_path_separator(src)
    unify_dstdir = unify_path_separator(dst)
    
    print(f"unify_srcdir={unify_srcdir}\n")
    try:
        migrate_obsidian_note(
            mdfile=mdf,
            srcdir=unify_srcdir,
            dstdir=unify_dstdir,
            backup=False
        )
    except Exception as e:
        print(f"❌ 迁移失败：{type(e).__name__} - {e}")


def demo_show_obsidian_note():
    # 1. 配置测试文件路径（替换为你的实际路径）
    test_md = "软件开发/驱动-zynq系列/zynq-axi-dma.md"
    
    # 2. 打印测试信息，提升可读性
    print("=" * 60)
    print(f"开始解析MD文件：{test_md}")
    print("=" * 60)
    
    try:
        # 3. 调用解析函数
        all_refs = get_filerefs_from_md(test_md)
        
        # 4. 分场景输出结果，清晰展示过滤效果
        if not all_refs:
            print("✅ 解析完成：未提取到任何有效文件引用（已过滤标题/文本块/空引用）")
        else:
            print(f"✅ 解析完成：共提取到 {len(all_refs)} 个有效文件引用：")
            print("-" * 40)
            for idx, ref in enumerate(all_refs, 1):
                print(f"{idx:2d}. {ref}")
        
        # 【可选扩展】如果需要验证过滤逻辑，可额外解析所有原始引用（含标题/文本块）
        # 注：仅用于调试，正式使用可注释
        print("\n" + "-" * 60)
        print("调试信息：文件中所有原始引用（含标题/文本块/空引用）：")
        md_path = Path(test_md)
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        raw_refs = re.findall(r"\[\[([^\]]+)\]\]", md_content, re.UNICODE)
        if raw_refs:
            for idx, ref in enumerate(raw_refs, 1):
                stripped_ref = ref.strip()
                # 标注引用类型
                ref_type = ""
                if not stripped_ref:
                    ref_type = "【空引用】"
                elif is_header_ref(stripped_ref):
                    ref_type = "【标题引用】"
                elif is_footnote_ref(stripped_ref):
                    ref_type = "【文本块引用】"
                else:
                    ref_type = "【文件引用】"
                print(f"{idx:2d}. {ref_type} {ref}")
        else:
            print("   无任何原始引用")
            
    # 5. 细化异常处理，给出更友好的提示
    except FileNotFoundError as e:
        print(f"❌ 错误：{e}")
        print("   请检查文件路径是否正确，或文件是否存在")
    except IsADirectoryError as e:
        print(f"❌ 错误：{e}")
        print("   请确保传入的是MD文件路径，而非目录路径")
    except PermissionError as e:
        print(f"❌ 错误：{e}")
        print("   请检查文件的读取权限，或是否被其他程序占用")
    except UnicodeDecodeError as e:
        print(f"❌ 错误：文件编码异常 - {e}")
        print("   建议检查文件是否为UTF-8编码，或修改读取编码")
    except Exception as e:
        print(f"❌ 未知错误：{type(e).__name__} - {e}")
        print("   请检查文件路径格式、文件完整性或函数逻辑")
    finally:
        print("\n" + "=" * 60)
        print("解析流程结束")
        print("=" * 60)


def run_from_ini(config_path: str):
    # 🔥 关键：禁用插值，避免路径被污染
    config = configparser.ConfigParser(interpolation=None)
    
    config.read(config_path, encoding="utf-8")

    # 函数注册表（🔥核心）
    func_map = {
        "copy_obsidian_note": copy_obsidian_note,
        "migrate_obsidian_note": migrate_obsidian_note,
        "convert_markdown_refs_to_obsidian": convert_markdown_refs_to_obsidian,
    }

    for section in config.sections():
        print(f"\n🚀 执行任务: {section}")

        if section not in func_map:
            print(f"❌ 未知函数: {section}")
            continue

        func = func_map[section]

        # 读取参数
        kwargs = {}
        for key, value in config.items(section):

            # 去掉引号
            if (value.startswith('"') and value.endswith('"')) or \
            (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]

            # 🔥 类型自动转换
            if value.lower() in ["true", "false"]:
                kwargs[key] = value.lower() == "true"
            else:
                kwargs[key] = value

        try:
            func(**kwargs)
        except Exception as e:
            print(f"❌ 执行失败: {section} | {e}")

# Python version: Anaconda + Python 3.10+
# if __name__ == "__main__":
#     # demo_migrate_obsidian_note()
#     demo_copy_obsidian_note()

if __name__ == "__main__":
    run_from_ini("notebook-tool-args.ini")

