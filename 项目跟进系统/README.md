# 项目跟进系统

一个本地 Web 应用，用于管理工作事项跟进。

## 功能特性

- ✅ 看板视图（按状态分列展示）
- ✅ 统计面板（总事项数、进行中、已完成、完成率、超期数）
- ✅ 新增/编辑/删除事项
- ✅ 跟进记录（保留历史）
- ✅ 超期提醒（红色高亮）
- ✅ 优先级标识（紧急/高/中/低）
- ✅ 进度条可视化
- ✅ 响应式设计（手机端可用）

## 技术栈

- **后端**：Python FastAPI + SQLite
- **前端**：原生 HTML/CSS/JavaScript

## 快速启动

```bash
cd ~/.qclaw/workspace/项目跟进系统
./start.sh
```

启动后会自动：
1. 检查并安装依赖
2. 启动后端 API 服务（端口 8000）
3. 打开浏览器访问前端页面

## 项目结构

```
项目跟进系统/
├── backend/              # 后端
│   ├── main.py          # FastAPI 应用
│   ├── models.py        # 数据模型
│   ├── database.py      # 数据库操作
│   └── requirements.txt # 依赖
├── frontend/            # 前端
│   └── index.html       # 单页应用
├── data/                # 数据存储
│   └── workitems.db     # SQLite 数据库
└── start.sh             # 启动脚本
```

## 数据字段

### 工作事项

| 字段 | 类型 | 说明 |
|------|------|------|
| name | 文本 | 事项名称 |
| type | 单选 | 风控模型的搭建/智能客服/智能巡检 |
| owner | 单选 | 黄京/夏韵/孙培/赵园园 |
| status | 单选 | 未启动/进行中/遇阻/待验收/已完成/已取消 |
| priority | 单选 | 低/中/高/紧急 |
| create_time | 日期 | 创建时间（自动） |
| expected_time | 日期 | 预计完成时间 |
| actual_time | 日期 | 实际完成时间 |
| progress | 数字 | 进度百分比（0-100） |
| latest_update | 文本 | 最新进展 |

### 跟进记录

| 字段 | 类型 | 说明 |
|------|------|------|
| item_id | 数字 | 关联的工作事项 ID |
| time | 日期 | 跟进时间（自动） |
| person | 文本 | 跟进人 |
| content | 文本 | 跟进内容 |

## API 接口

### 工作事项

- `GET /api/items` - 获取所有事项
- `GET /api/items/{id}` - 获取单个事项
- `POST /api/items` - 创建事项
- `PUT /api/items/{id}` - 更新事项
- `DELETE /api/items/{id}` - 删除事项

### 跟进记录

- `GET /api/items/{id}/follow-ups` - 获取事项的跟进记录
- `POST /api/follow-ups` - 创建跟进记录

### 统计

- `GET /api/statistics` - 获取统计数据

### 元数据

- `GET /api/meta/types` - 获取事项类型列表
- `GET /api/meta/statuses` - 获取状态列表
- `GET /api/meta/priorities` - 获取优先级列表
- `GET /api/meta/owners` - 获取负责人列表

## 使用说明

1. **新增事项**：点击右上角「+ 新增事项」按钮
2. **查看详情**：点击卡片查看详情和跟进记录
3. **编辑事项**：在详情页点击「编辑」按钮
4. **删除事项**：在详情页点击「删除」按钮
5. **添加跟进**：在详情页底部输入跟进内容

## 数据存储

数据保存在 `~/.qclaw/workspace/项目跟进系统/data/workitems.db`（SQLite 文件）

## 停止服务

启动后会显示后端进程 PID，使用以下命令停止：

```bash
kill <PID>
```

或在启动终端按 `Ctrl+C`

## 开发者

由 QClaw（小糯米）开发，2026-05-18
