# RepoGuard

> 三步，给你的私人仓库配上 AI 代码审查。

每次 `git push`，AI 自动审查你的代码变更。无需第三方平台，无需复杂配置，接入你自己的 AI API 即可运行。

---
1. 下载项目 → 配置 config.json
2. 推到自己的 GitHub 仓库 → 设置api密钥
3. 之后每次 git push，上传新代码 AI 将自动审查

## 三步开始

### 第一步：下载配置

```bash
git clone <你的仓库地址>
cd repoguard
cp config.example.json config.json
pip install -r requirements.txt
```

编辑 `config.json` 填入 API 信息（支持任何兼容 OpenAI 接口的服务）：

```json
{
  "api_endpoint": "https://api.openai.com/v1/chat/completions",
  "model": "gpt-4o-mini",
  "api_key": "",
  "api_key_env": "AI_API_KEY"
}
```

> `api_key` 留空则从环境变量读取，推荐用环境变量避免密钥泄露。

### 第二步：推到你的仓库

```bash
git init
git add .
git commit -m "init: RepoGuard"
git remote add origin <你的私有仓库地址>
git push -u origin main
```

然后进入仓库 **Settings → Secrets and variables → Actions**，添加三个 Secrets：

| Secret | 值 |
|------|------|
| `API_KEY` | 你的 AI API 密钥 |
| `API_ENDPOINT` | API 地址，如 `https://api.openai.com/v1/chat/completions` |
| `API_MODEL` | 模型名，如 `gpt-4o-mini` |

### 第三步：正常写代码，自动审查

```bash
git add .
git commit -m "feat: 新功能"
git push
```

之后每次 push 或提交 PR，GitHub Actions 自动获取 diff、调用 AI 审查。PR 事件下审查结果自动评论，push 事件下记录在 Actions 日志。

---

## 工作流程

```
git push ──→ GitHub Actions 触发 ──→ 获取 diff ──→ 调用 AI API
                                                      │
                                          ┌───────────┴───────────┐
                                          ↓                       ↓
                                      PR 事件                 push 事件
                                  自动评论到 PR          记录在 Actions 日志
```

---

## 本地模式

除了自动审查，RepoGuard 也能在本地命令行使用：

| 命令 | 功能 | 示例 |
|------|------|------|
| `review` | 代码审查 | `python agent.py review src/main.py` |
| `explain` | 代码解释 | `python agent.py explain src/main.py` |
| `generate` | 代码生成 | `python agent.py generate "描述"` |
| `test` | 生成测试 | `python agent.py test src/main.py` |
| `refactor` | 重构建议 | `python agent.py refactor src/main.py` |
| `chat` | 自由对话 | `python agent.py chat` |

---

## 支持的 API

兼容 OpenAI Chat Completions 接口的服务均可：OpenAI、DeepSeek、通义千问、Ollama、小米 Mimo 等。

---

## License

MIT
