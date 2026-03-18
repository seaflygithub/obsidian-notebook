#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path


# =========================
# 1. 基础工具
# =========================

def is_chinese(char: str) -> bool:
    return '\u4e00' <= char <= '\u9fff'


def normalize_text(text: str) -> str:
    """
    统一全角/半角、奇怪符号
    """
    replacements = {
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'",
        '．': '.',
        '，': '，',
        '。': '。',
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text


# =========================
# 2. 核心：空格修复
# =========================

def fix_spaces(text: str) -> str:
    """
    修复 OCR 产生的“字间空格”
    """

    # ① 中文之间去空格
    text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)

    # ② 中文 + 标点
    text = re.sub(r'([\u4e00-\u9fff])\s+([，。！？：；])', r'\1\2', text)

    # ③ 标点 + 中文
    text = re.sub(r'([，。！？：；])\s+([\u4e00-\u9fff])', r'\1\2', text)

    # ④ 中文 + 英文（去掉空格）
    text = re.sub(r'([\u4e00-\u9fff])\s+([A-Za-z0-9])', r'\1\2', text)

    # ⑤ 英文 + 中文（去掉空格）
    text = re.sub(r'([A-Za-z0-9])\s+([\u4e00-\u9fff])', r'\1\2', text)

    # ⑥ 多余空格压缩（英文用）
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# =========================
# 3. 段落修复（重要）
# =========================

def fix_newlines(text: str) -> str:
    """
    OCR 常见问题：一行一句被乱切
    """

    lines = text.splitlines()
    new_lines = []

    buffer = ""

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # 如果上一行没结束（没有句号），拼接
        if buffer and not buffer.endswith(('。', '！', '？', '.', '!', '?')):
            buffer += line
        else:
            if buffer:
                new_lines.append(buffer)
            buffer = line

    if buffer:
        new_lines.append(buffer)

    return "\n".join(new_lines)


# =========================
# 4. 主流程
# =========================

def clean_ocr_text(text: str) -> str:
    text = normalize_text(text)
    text = fix_spaces(text)
    text = fix_newlines(text)
    return text


def process_file(input_file: str, output_file: str):
    text = Path(input_file).read_text(encoding="utf-8")
    cleaned = clean_ocr_text(text)
    Path(output_file).write_text(cleaned, encoding="utf-8")
    print(f"完成: {output_file}")


# =========================
# 5. 入口
# =========================

if __name__ == "__main__":
    process_file("temp.txt", "output.txt")