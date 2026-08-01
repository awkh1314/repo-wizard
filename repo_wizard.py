#!/usr/bin/env python3
"""repo-wizard — 把任意目录一键变成「开源就绪」的 GitHub 仓库。

零依赖，仅使用 Python 标准库。支持两个子命令：
  init   交互式生成开源所需的一整套文件（README / LICENSE / .gitignore /
         CONTRIBUTING / CODE_OF_CONDUCT / GitHub 模板 / CI 工作流）
  check  审计现有仓库，给出「开源就绪度」评分与补齐建议

用法示例：
  python repo_wizard.py init
  python repo_wizard.py init ./my-project --yes
  python repo_wizard.py check
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# 颜色（Windows 下如果终端不支持则自动降级）
# --------------------------------------------------------------------------- #
_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(code: str, text: str) -> str:
    if not _USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


GREEN = lambda s: _c("32", s)
YELLOW = lambda s: _c("33", s)
RED = lambda s: _c("31", s)
BOLD = lambda s: _c("1", s)
CYAN = lambda s: _c("36", s)
DIM = lambda s: _c("2", s)

BANNER = r"""
   ___ ___  ___  ___  ___  ___  ___
  | _ \ _ \/ _ \| _ \/ _ \| __|| __|
  |   /   / (_) |   / (_) |__ \|__ \
  |_|_|_|_\\___/|_|_\\\\___/|___/|___/   repo-wizard
"""


# --------------------------------------------------------------------------- #
# 模板（使用 __TOKEN__ 占位符，渲染时用 .replace，避免与 YAML 的 ${{ }} 冲突）
# --------------------------------------------------------------------------- #
LICENSE_MIT = """MIT License

Copyright (c) __YEAR__ __AUTHOR__

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

APACHE_LICENSE = """                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   Copyright __YEAR__ __AUTHOR__

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

README_EN = """# __PROJECT_NAME__

> __DESCRIPTION__

<!-- 用一句话说明：它解决什么问题、为什么存在。 -->

## ✨ Features

- _（列出 2-4 个核心特性）_

## 🚀 Installation

```bash
# 贴出安装方式，例如：
pip install .
```

## 🛠 Usage

```bash
# 贴出最少可运行的示例
```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md)
and our [Code of Conduct](CODE_OF_CONDUCT.md) first.

## 📄 License

Released under the __LICENSE__ License. See [LICENSE](LICENSE).
"""

README_ZH = """# __PROJECT_NAME__

> __DESCRIPTION__

<!-- 用一句话说明：它解决什么问题、为什么存在。 -->

## ✨ 特性

- _（列出 2-4 个核心特性）_

## 🚀 安装

```bash
# 贴出安装方式，例如：
pip install .
```

## 🛠 用法

```bash
# 贴出最少可运行的示例
```

## 🤝 贡献

欢迎贡献！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与
[行为准则](CODE_OF_CONDUCT.md)。

## 📄 许可证

基于 __LICENSE__ 许可证开源，详见 [LICENSE](LICENSE)。
"""

CONTRIBUTING_EN = """# Contributing to __PROJECT_NAME__

Thanks for taking the time to contribute! 🎉

## How to contribute

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. Ensure the test suite passes.
4. Make sure your commit messages follow
   [Conventional Commits](https://www.conventionalcommits.org).
5. Open a pull request and describe your change clearly.

## Reporting bugs

Open an issue using the bug report template and include reproduction steps.
"""

CONTRIBUTING_ZH = """# 为 __PROJECT_NAME__ 做贡献

感谢你抽出时间参与贡献！🎉

## 如何贡献

1. Fork 本仓库，并从 `main` 创建你的分支。
2. 如果新增了需要测试的代码，请补充测试。
3. 确保测试套件通过。
4. 提交信息请遵循
   [Conventional Commits](https://www.conventionalcommits.org) 规范。
5. 发起 Pull Request，并清晰描述你的改动。

## 报告问题

请使用 Bug 报告模板提交 Issue，并附上复现步骤。
"""

CODE_OF_CONDUCT = """# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity and
orientation.

## Our Standards

Examples of behavior that contributes to a positive environment:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback

Examples of unacceptable behavior:

* The use of sexualized language or imagery, and unwelcome sexual attention
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the project maintainers. All complaints will be reviewed and
investigated promptly and fairly.

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.1, available at
https://www.contributor-covenant.org/version/2/1/code_of_conduct.html.

[homepage]: https://www.contributor-covenant.org
"""

ISSUE_BUG = """name: 🐛 Bug report
description: Report a bug to help us improve
title: "[Bug] "
labels: ["bug"]
body:
  - type: textarea
    id: what-happened
    attributes:
      label: What happened?
      description: A clear and concise description of the bug.
    validations:
      required: true
  - type: textarea
    id: reproduce
    attributes:
      label: Steps to reproduce
      description: How can we reproduce the issue?
      placeholder: |
        1. Run '...'
        2. See error '...'
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
    validations:
      required: false
  - type: textarea
    id: env
    attributes:
      label: Environment
      description: OS / version / runtime
    validations:
      required: false
"""

ISSUE_FEATURE = """name: 💡 Feature request
description: Suggest a new idea for this project
title: "[Feature] "
labels: ["enhancement"]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem
      description: What problem would this feature solve?
    validations:
      required: true
  - type: textarea
    id: solution
    attributes:
      label: Proposed solution
    validations:
      required: true
  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives considered
    validations:
      required: false
"""

PR_TEMPLATE = """## 📝 Description

<!-- 描述你的改动以及动机。 -->

## ✅ Checklist

- [ ] 我的改动遵循 [Conventional Commits](https://www.conventionalcommits.org)
- [ ] 我已更新相关文档 / 测试
- [ ] 本地测试通过

## 🔗 Related issues

<!-- 例如: Closes #12 -->
"""

CI_PYTHON = """name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install
        run: pip install -e .
      - name: Test
        run: pytest || echo "no tests yet"
"""

CI_NODE = """name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install
        run: npm install
      - name: Test
        run: npm test || echo "no tests yet"
"""

CI_GENERIC = """name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint / build placeholder
        run: echo "Add your build & test steps here"
"""

GITIGNORE = {
    "python": """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
.venv/
venv/
env/

# Distribution / packaging
build/
dist/
*.egg-info/
.eggs/

# Testing / coverage
.pytest_cache/
.coverage
htmlcov/

# IDE
.idea/
.vscode/

# OS
.DS_Store
""",
    "node": """# Dependencies
node_modules/

# Build output
dist/
build/

# Logs
*.log
npm-debug.log*

# Env
.env
.env.local

# IDE
.idea/
.vscode/

# OS
.DS_Store
""",
    "go": """# Binaries
*.exe
*.test
*.out

# Vendor (if not using modules)
vendor/

# IDE
.idea/
.vscode/

# OS
.DS_Store
""",
    "rust": """/target/
**/*.rs.bk
Cargo.lock

# IDE
.idea/
.vscode/

# OS
.DS_Store
""",
    "generic": """# Editor / OS
.idea/
.vscode/
.DS_Store
*.log

# Python
__pycache__/
.venv/

# Node
node_modules/
""",
}

LICENSE_FILES = {
    "mit": ("MIT", LICENSE_MIT),
    "apache-2.0": ("Apache-2.0", None),  # 占位：下方单独处理
}


# --------------------------------------------------------------------------- #
# 工具函数
# --------------------------------------------------------------------------- #
def prompt(label: str, default: str, hint: str = "") -> str:
    suffix = f" [{hint}]" if hint else ""
    val = input(f"  {CYAN(label)}{suffix} {DIM('(默认: ' + default + ')')}: ").strip()
    return val or default


def prompt_choice(label: str, options: list[str], default_idx: int = 0) -> str:
    opts = " / ".join(
        (BOLD(o) if i == default_idx else o) for i, o in enumerate(options)
    )
    raw = input(f"  {CYAN(label)} [{opts}]: ").strip().lower()
    if not raw:
        return options[default_idx]
    for o in options:
        if o.lower().startswith(raw) or o.lower() == raw:
            return o
    return options[default_idx]


def get_git_author() -> str:
    try:
        name = subprocess.check_output(
            ["git", "config", "user.name"], stderr=subprocess.DEVNULL
        ).decode().strip()
        if name:
            return name
    except Exception:
        pass
    return os.environ.get("USER") or os.environ.get("USERNAME") or "Anonymous"


def render(text: str, **tokens) -> str:
    for k, v in tokens.items():
        text = text.replace(f"__{k.upper()}__", str(v))
    return text


# --------------------------------------------------------------------------- #
# init 命令
# --------------------------------------------------------------------------- #
def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.path).resolve()
    target.mkdir(parents=True, exist_ok=True)

    print(BANNER)
    print(BOLD("  repo-wizard · 初始化开源仓库\n"))

    # ---- 收集信息 ----
    if args.yes:
        name = args.name or target.name
        description = args.description or "A new open-source project."
        author = args.author or get_git_author()
        license_key = args.license or "mit"
        lang = args.language or "generic"
        readme_lang = args.readme_lang or "en"
        ci = args.ci if args.ci is not None else True
        templates = args.templates if args.templates is not None else True
    else:
        name = prompt("项目名称", args.name or target.name)
        description = prompt("一句话描述", args.description or "A new open-source project.")
        author = prompt("作者 / 维护者", args.author or get_git_author())
        license_key = prompt_choice(
            "许可证", ["mit", "apache-2.0", "none"], 0
        )
        lang = prompt_choice(
            "主语言", ["python", "node", "go", "rust", "generic"], 4
        )
        readme_lang = prompt_choice("README 语言", ["en", "zh"], 0)
        ci = prompt_choice("生成 CI 工作流?", ["yes", "no"], 0) == "yes"
        templates = (
            prompt_choice("生成 Issue/PR 模板?", ["yes", "no"], 0) == "yes"
        )

    year = str(__import__("datetime").date.today().year)

    # ---- 组装文件清单 ----
    files: dict[Path, str] = {}

    # README
    readme_tpl = README_ZH if readme_lang == "zh" else README_EN
    files[target / "README.md"] = render(
        readme_tpl,
        project_name=name,
        description=description,
        license=license_key.upper(),
    )

    # LICENSE
    if license_key == "mit":
        files[target / "LICENSE"] = render(
            LICENSE_MIT, author=author, year=year
        )
    elif license_key == "apache-2.0":
        files[target / "LICENSE"] = render(
            APACHE_LICENSE, author=author, year=year
        )
    # none -> 不生成

    # .gitignore
    files[target / ".gitignore"] = GITIGNORE.get(lang, GITIGNORE["generic"])

    # CONTRIBUTING
    contrib_tpl = CONTRIBUTING_ZH if readme_lang == "zh" else CONTRIBUTING_EN
    files[target / "CONTRIBUTING.md"] = render(contrib_tpl, project_name=name)

    # CODE_OF_CONDUCT
    files[target / "CODE_OF_CONDUCT.md"] = CODE_OF_CONDUCT

    # GitHub 模板
    if templates:
        files[target / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml"] = ISSUE_BUG
        files[target / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml"] = ISSUE_FEATURE
        files[target / ".github" / "PULL_REQUEST_TEMPLATE.md"] = PR_TEMPLATE

    # CI
    if ci:
        ci_tpl = {
            "python": CI_PYTHON,
            "node": CI_NODE,
        }.get(lang, CI_GENERIC)
        files[target / ".github" / "workflows" / "ci.yml"] = ci_tpl

    # ---- 写入（避免覆盖已有文件） ----
    written, skipped = [], []
    for path, content in files.items():
        if path.exists() and not args.force:
            skipped.append(path.name)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(target)))

    # ---- 汇总 ----
    print()
    print(BOLD("  ✅ 已生成:"))
    for f in written:
        print(f"    {GREEN('+')} {f}")
    if skipped:
        print()
        print(DIM("  已存在、已跳过（用 --force 覆盖）:"))
        for f in skipped:
            print(f"    {YELLOW('~')} {f}")

    if written:
        print()
        print(BOLD("  下一步:"))
        print(f"    cd {target}")
        print("    git init && git add . && git commit -m 'chore: open-source scaffolding'")
        print("    gh repo create && git push -u origin main")

    return 0


# --------------------------------------------------------------------------- #
# check 命令
# --------------------------------------------------------------------------- #
ESSENTIALS = [
    ("README.md", 20, "项目门面，说明它解决什么问题"),
    ("LICENSE", 25, "没有许可证，别人不敢使用"),
    (".gitignore", 10, "避免把依赖 / 密钥提交进仓库"),
    ("CONTRIBUTING.md", 15, "告诉别人如何参与"),
    ("CODE_OF_CONDUCT.md", 10, "社区行为准则"),
    (".github/ISSUE_TEMPLATE", 10, "规范的问题反馈模板"),
    (".github/PULL_REQUEST_TEMPLATE.md", 5, "PR 模板"),
    (".github/workflows", 5, "CI 自动测试，提升可信度"),
]


def cmd_check(args: argparse.Namespace) -> int:
    target = Path(args.path).resolve()
    print(BANNER)
    print(BOLD("  repo-wizard · 开源就绪度检查\n"))

    if not target.exists():
        print(RED(f"  目录不存在: {target}"))
        return 1

    score = 0
    print(f"  扫描: {target}\n")
    for rel, weight, tip in ESSENTIALS:
        p = target / rel
        exists = p.exists()
        if exists:
            score += weight
            print(f"    {GREEN('✔')} {rel:<38} {DIM('+' + str(weight))}")
        else:
            print(f"    {RED('✘')} {rel:<38} {DIM('+' + str(weight))}  {DIM(tip)}")

    print()
    color = GREEN if score >= 80 else (YELLOW if score >= 50 else RED)
    print(f"  开源就绪度: {color(str(score) + '/100')}")

    if score < 100:
        missing = [rel for rel, _, _ in ESSENTIALS if not (target / rel).exists()]
        print(f"  缺失 {len(missing)} 项。运行以下命令补齐:")
        print(f"    {CYAN('python repo_wizard.py init ' + str(target) + ' --yes')}")
    else:
        print(GREEN("  完美，仓库已开源就绪！🚀"))

    return 0


# --------------------------------------------------------------------------- #
# 入口
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="repo-wizard",
        description="把任意目录一键变成开源就绪的 GitHub 仓库。",
    )
    p.add_argument("--version", action="version", version="repo-wizard 0.1.1")
    sub = p.add_subparsers(dest="command", required=True)

    pi = sub.add_parser("init", help="生成开源所需的一整套文件")
    pi.add_argument("path", nargs="?", default=".", help="目标目录 (默认当前目录)")
    pi.add_argument("--name")
    pi.add_argument("--description")
    pi.add_argument("--author")
    pi.add_argument("--license", choices=["mit", "apache-2.0", "none"], default="mit")
    pi.add_argument("--language", choices=["python", "node", "go", "rust", "generic"], default="generic")
    pi.add_argument("--readme-lang", choices=["en", "zh"], default="en")
    pi.add_argument("--ci", dest="ci", action="store_true", default=None)
    pi.add_argument("--no-ci", dest="ci", action="store_false")
    pi.add_argument("--templates", dest="templates", action="store_true", default=None)
    pi.add_argument("--no-templates", dest="templates", action="store_false")
    pi.add_argument("--yes", action="store_true", help="跳过交互，使用默认值")
    pi.add_argument("--force", action="store_true", help="覆盖已存在的文件")
    pi.set_defaults(func=cmd_init)

    pc = sub.add_parser("check", help="审计现有仓库的开源就绪度")
    pc.add_argument("path", nargs="?", default=".", help="目标目录 (默认当前目录)")
    pc.set_defaults(func=cmd_check)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
