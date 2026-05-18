#!/bin/bash

# 项目跟进系统 - 启动脚本

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "======================================"
echo "  项目跟进系统 - 启动中..."
echo "======================================"
echo ""

# 检查 Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 python3"
    echo "请先安装 Python 3"
    exit 1
fi

# 检查并安装依赖
echo "📦 检查依赖..."
cd "$BACKEND_DIR"

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "正在安装 FastAPI..."
    pip3 install -r requirements.txt
fi

# 启动后端
echo ""
echo "🚀 启动后端服务（端口 8000）..."
python3 main.py &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 检查后端是否启动成功
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ 后端启动失败"
    exit 1
fi

echo "✅ 后端已启动（PID: $BACKEND_PID）"

# 打开前端
echo ""
echo "🌐 打开前端页面..."
open "$FRONTEND_DIR/index.html"

echo ""
echo "======================================"
echo "  ✅ 系统已启动！"
echo "======================================"
echo ""
echo "📍 后端 API: http://localhost:8000"
echo "📍 前端页面: 已在浏览器中打开"
echo ""
echo "💡 使用提示："
echo "   - 点击卡片查看详情、跟进记录"
echo "   - 点击右上角「+ 新增事项」添加新事项"
echo "   - 数据保存在: $PROJECT_DIR/data/workitems.db"
echo ""
echo "🛑 停止服务：kill $BACKEND_PID"
echo ""

# 等待用户按 Ctrl+C
trap "echo ''; echo '正在停止...'; kill $BACKEND_PID; echo '✅ 已停止'; exit 0" INT TERM

wait $BACKEND_PID
