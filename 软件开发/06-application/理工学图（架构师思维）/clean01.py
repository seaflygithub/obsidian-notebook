#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path


def is_chinese(char: str) -> bool:
    """判断是否为中文字符"""
    return '\u4e00' <= char <= '\u9fff'


def clean_text(text: str) -> str:
    """
    去掉中文之间的空格，但保留英文单词之间的空格
    """
    result = []
    prev_char = ""

    for ch in text:
        if ch == " ":
            # 如果前后都是中文 -> 去掉
            # 否则保留（比如英文之间）
            continue_flag = False
            if prev_char and result:
                # 看下一个字符
                # 这里只能先跳过，后面再处理
                continue_flag = True

            if continue_flag:
                # 先标记，后面统一处理
                result.append(ch)
            continue
        else:
            result.append(ch)
            prev_char = ch

    # 第二步：去掉“中文 + 空格 + 中文”
    text = "".join(result)
    text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)

    # 去掉“中文 + 空格 + 标点”
    text = re.sub(r'([\u4e00-\u9fff])\s+([，。！？、“”‘’：；（）])', r'\1\2', text)

    # 去掉“标点 + 空格 + 中文”
    text = re.sub(r'([，。！？、“”‘’：；（）])\s+([\u4e00-\u9fff])', r'\1\2', text)

    # 压缩多余空格（英文用）
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def process_file(input_file: str, output_file: str | None = None):
    path = Path(input_file)

    if not path.exists():
        print(f"文件不存在: {input_file}")
        return

    text = path.read_text(encoding="utf-8")
    cleaned = clean_text(text)

    if output_file:
        Path(output_file).write_text(cleaned, encoding="utf-8")
        print(f"处理完成，输出文件: {output_file}")
    else:
        print(cleaned)


if __name__ == "__main__":
    # 示例：处理 temp.txt -> output.txt
    process_file("temp.txt", "output.txt")