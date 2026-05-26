#!/bin/bash
# RepoGuard - 代码审查管家 Linux/Mac 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/agent.py" "$@"
