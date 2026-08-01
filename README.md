# repo-wizard

> Turn any directory into an open-source-ready GitHub repo in seconds.

**repo-wizard** is a zero-dependency CLI that scaffolds everything a GitHub
open-source project needs: `README`, `LICENSE`, `.gitignore`, `CONTRIBUTING`,
`CODE_OF_CONDUCT`, issue/PR templates, and a CI workflow. It also ships a
`check` command that scores how "open-source ready" an existing repo is.

<details>
<summary>中文</summary>

**repo-wizard** 是一个零依赖的命令行工具，一键为你的 GitHub 开源项目生成全部标准文件：`README`、`LICENSE`、`.gitignore`、`CONTRIBUTING`、`CODE_OF_CONDUCT`、Issue/PR 模板以及 CI 工作流。还自带 `check` 命令，给现有仓库打分，告诉你还缺什么。

</details>

## ✨ Features

- **`init`** — interactive scaffolding of a full open-source file set
- **`check`** — audit an existing repo and get an "open-source readiness" score (0–100)
- **Zero dependencies** — pure Python standard library, runs anywhere Python 3.8+ runs
- **Language-aware** — picks a sensible `.gitignore` for Python / Node / Go / Rust
- **Bilingual README** — generate `README` & `CONTRIBUTING` in English or Chinese
- **Non-destructive** — never overwrites existing files unless you pass `--force`

## 🚀 Installation

No install needed — just download `repo_wizard.py` and run it:

```bash
python repo_wizard.py init
```

Or install as a command:

```bash
pip install .
# then: repo-wizard init
```

## 🛠 Usage

```bash
# Interactive: answer a few prompts, files are written to ./my-project
python repo_wizard.py init ./my-project

# Non-interactive: use sensible defaults
python repo_wizard.py init ./my-project --yes

# Generate a Chinese README for a Node project
python repo_wizard.py init . --yes --language node --readme-lang zh

# Audit an existing repo
python repo_wizard.py check .
```

### Output of `init`

```
   ___ ___  ___  ___  ___  ___  ___
  | _ \ _ \/ _ \| _ \/ _ \| __|| __|
  |   /   / (_) |   / (_) |__ \|__ \
  |_|_|_|_\\___/|_|_\\\\___/|___/|___/   repo-wizard

  ✅ 已生成:
    + README.md
    + LICENSE
    + .gitignore
    + CONTRIBUTING.md
    + CODE_OF_CONDUCT.md
    + .github/ISSUE_TEMPLATE/bug_report.yml
    + .github/ISSUE_TEMPLATE/feature_request.yml
    + .github/PULL_REQUEST_TEMPLATE.md
    + .github/workflows/ci.yml
```

### Options

| flag | meaning |
| --- | --- |
| `--name` | project name |
| `--description` | one-line description |
| `--author` | author / maintainer name |
| `--license` | `mit` (default) / `apache-2.0` / `none` |
| `--language` | `python` / `node` / `go` / `rust` / `generic` |
| `--readme-lang` | `en` (default) / `zh` |
| `--ci` / `--no-ci` | generate a CI workflow |
| `--templates` / `--no-templates` | generate issue/PR templates |
| `--yes` | skip prompts, use defaults |
| `--force` | overwrite existing files |

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and our
[Code of Conduct](CODE_OF_CONDUCT.md) first.

## 📄 License

Released under the MIT License. See [LICENSE](LICENSE).
