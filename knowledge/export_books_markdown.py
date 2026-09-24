#!/usr/bin/env python3
"""
export_books_markdown.py
Exports 24 classic copywriting books into structured markdown files in knowledge/books/
"""

import sys
import os
import re
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def export_books_md():
    json_path = PROJECT_ROOT / "knowledge" / "master_copywriting_books.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    books = data.get("books", [])

    books_dir = PROJECT_ROOT / "knowledge" / "books"
    books_dir.mkdir(parents=True, exist_ok=True)

    for i, b in enumerate(books, 1):
        clean_author = re.sub(r'[/\\:\*?"<>|]', '_', b['author'])[:30].strip()
        filename = f"{i:02d}_{b['book_id']}_{clean_author}.md"
        filepath = books_dir / filename

        cases_md = ""
        for c in b.get("classic_golden_cases", []):
            cases_md += f"""- **【{c.get('case_name')}】**  
  *金句*: `{c.get('slogan')}`  
  *深度拆解*: {c.get('insight')}  
"""

        methods_md = "\n".join([f"- {m}" for m in b.get("writing_methods", [])])
        strat = b.get("strategy_framework", {})
        strat_md = json.dumps(strat, ensure_ascii=False, indent=2)

        md_content = f"""# 《{b['title']}》— 文案写作与广告策略核心心法

> **作者**: {b['author']} | **学派归属**: {b['school']}
> **核心理论**: {b['core_theory']}
> **思考方式**: {b['thinking_paradigm']}

---

## 🏛️ 战略策略框架
```json
{strat_md}
```

---

## ✍️ 具体写作技法与修辞模型
{methods_md}

---

## 🏆 传世经典金句案例与深度解构
{cases_md}

---

## ⚙️ 算法启发与工程指标
- **目标指标**: {b.get('algorithmic_heuristics', {}).get('target_metric', '')}
- **判定规则**: {b.get('algorithmic_heuristics', {}).get('rule', '')}
"""
        filepath.write_text(md_content, encoding="utf-8")
        print(f"Generated {filename}")

    print(f"✅ Successfully exported {len(books)} book markdowns to {books_dir}")

if __name__ == "__main__":
    export_books_md()
