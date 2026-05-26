#!/usr/bin/env python3
"""
RepoGuard - 私人仓库的代码审查管家
通过接入外部 AI API，对仓库代码进行自动审查
兼容 OpenAI 接口协议，支持任意兼容的 AI API 服务
"""

import json
import os
import sys
import argparse
import requests
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config():
    if not CONFIG_PATH.exists():
        print(f"错误: 配置文件不存在 ({CONFIG_PATH})")
        print("请先复制配置模板: cp config.example.json config.json")
        print("然后编辑 config.json 填入你的 API 信息")
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_api_key():
    config = load_config()

    api_key = config.get("api_key", "").strip()
    if api_key:
        return api_key

    api_key = os.environ.get(config["api_key_env"], "").strip()
    if api_key:
        return api_key

    print(f"错误: 请在 config.json 中设置 api_key")
    print(f"或者设置环境变量 {config['api_key_env']}")
    sys.exit(1)


def call_ai(prompt, system_prompt=None, temperature=None, max_tokens=None):
    config = load_config()
    api_key = get_api_key()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": config["model"],
        "messages": messages,
        "temperature": temperature or config["default_temperature"],
        "max_tokens": max_tokens or config["default_max_tokens"]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            config["api_endpoint"],
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"API 调用失败: {e}")
        sys.exit(1)
    except (KeyError, IndexError) as e:
        print(f"响应解析失败: {e}")
        sys.exit(1)


def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"读取文件失败: {e}")
        sys.exit(1)


def cmd_review(args):
    if not args.file:
        print("错误: 请指定要审查的文件")
        sys.exit(1)

    code = read_file(args.file)
    system_prompt = """你是一个专业的代码审查专家。请审查以下代码，用中文回答，重点关注：
1. 代码质量和最佳实践
2. 潜在的bug和安全问题
3. 性能优化建议
4. 代码风格和可读性

请用简洁的 Markdown 格式输出审查结果。"""

    prompt = f"请审查以下代码文件 {args.file}：\n\n```\n{code}\n```"
    result = call_ai(prompt, system_prompt)
    print(result)


def cmd_explain(args):
    if not args.file:
        print("错误: 请指定要解释的文件")
        sys.exit(1)

    code = read_file(args.file)
    system_prompt = """你是一个编程教师。请用简单易懂的中文解释代码的作用，包括：
1. 整体功能概述
2. 主要函数/类的作用
3. 关键逻辑解释
4. 使用的技术点"""

    prompt = f"请解释以下代码文件 {args.file}：\n\n```\n{code}\n```"
    result = call_ai(prompt, system_prompt)
    print(result)


def cmd_generate(args):
    if not args.description:
        print("错误: 请描述要生成的代码功能")
        sys.exit(1)

    system_prompt = """你是一个高级程序员。请根据描述生成高质量的代码，要求：
1. 代码简洁、可读
2. 添加必要的注释
3. 遵循最佳实践
4. 包含错误处理
5. 使用中文注释"""

    prompt = f"请生成以下功能的代码：\n\n{args.description}"
    result = call_ai(prompt, system_prompt)
    print(result)


def cmd_test(args):
    if not args.file:
        print("错误: 请指定要生成测试的文件")
        sys.exit(1)

    code = read_file(args.file)
    system_prompt = """你是一个测试专家。请为代码生成单元测试，要求：
1. 覆盖主要功能和边界情况
2. 使用常见的测试框架（如 pytest、unittest）
3. 测试文件命名规范
4. 添加中文注释说明测试目的
5. 只输出测试代码"""

    prompt = f"请为以下代码文件 {args.file} 生成单元测试：\n\n```\n{code}\n```"
    result = call_ai(prompt, system_prompt)
    print(result)


def cmd_refactor(args):
    if not args.file:
        print("错误: 请指定要重构的文件")
        sys.exit(1)

    code = read_file(args.file)
    system_prompt = """你是一个代码重构专家。请提供重构建议，包括：
1. 可以提取的函数/类
2. 可以简化的逻辑
3. 可以优化的性能点
4. 重构后的代码示例
5. 重构的好处说明"""

    prompt = f"请为以下代码文件 {args.file} 提供重构建议：\n\n```\n{code}\n```"
    result = call_ai(prompt, system_prompt)
    print(result)


def cmd_chat(args):
    system_prompt = """你是一个 AI 编程助手。你可以帮助用户：
1. 解答编程问题
2. 提供代码示例
3. 讨论技术方案
4. 调试代码问题

请用友好、专业的中文回答。"""

    if args.message:
        prompt = args.message
    else:
        print("欢迎使用 RepoGuard 代码审查管家！输入 'exit' 退出。")
        while True:
            try:
                user_input = input("\n你: ")
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break
            try:
                if user_input.lower() in ["exit", "quit", "退出"]:
                    print("再见！")
                    break
                if not user_input.strip():
                    continue
                result = call_ai(user_input, system_prompt)
                print(f"\nAI: {result}")
            except KeyboardInterrupt:
                print("\n再见！")
                break
        return

    result = call_ai(prompt, system_prompt)
    print(result)


def main():
    parser = argparse.ArgumentParser(
        description="RepoGuard - 私人仓库代码审查管家",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python agent.py review src/main.py          # 代码审查
  python agent.py explain src/main.py         # 代码解释
  python agent.py generate "创建一个排序函数"   # 代码生成
  python agent.py test src/main.py            # 生成测试
  python agent.py refactor src/main.py        # 重构建议
  python agent.py chat                        # 自由对话
  python agent.py chat "如何学习Python?"       # 单次提问
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    review_parser = subparsers.add_parser("review", help="代码审查")
    review_parser.add_argument("file", nargs="?", help="要审查的文件路径")

    explain_parser = subparsers.add_parser("explain", help="代码解释")
    explain_parser.add_argument("file", nargs="?", help="要解释的文件路径")

    generate_parser = subparsers.add_parser("generate", help="代码生成")
    generate_parser.add_argument("description", nargs="?", help="代码功能描述")

    test_parser = subparsers.add_parser("test", help="生成测试")
    test_parser.add_argument("file", nargs="?", help="要生成测试的文件路径")

    refactor_parser = subparsers.add_parser("refactor", help="重构建议")
    refactor_parser.add_argument("file", nargs="?", help="要重构的文件路径")

    chat_parser = subparsers.add_parser("chat", help="自由对话")
    chat_parser.add_argument("message", nargs="?", help="要问的问题")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "review": cmd_review,
        "explain": cmd_explain,
        "generate": cmd_generate,
        "test": cmd_test,
        "refactor": cmd_refactor,
        "chat": cmd_chat
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
