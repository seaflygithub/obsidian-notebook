from pathlib import Path

text = Path("temp.txt").read_text(encoding="utf-8")
text = text.replace(" ", "")

Path("output.txt").write_text(text, encoding="utf-8")