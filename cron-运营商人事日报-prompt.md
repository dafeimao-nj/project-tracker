# 定时任务：运营商人事日报 Prompt

## 触发条件
每天早上 08:00 (Asia/Shanghai)

## ⚠️ 搜索规则：元宝搜索（ProSearch）+ 其他搜索方式并行

**元宝搜索必须包含**，同时可配合其他搜索方式（multi-search-engine 等）交叉验证。

元宝搜索脚本：/Users/zengjun-dafeimao/Library/Application Support/QClaw/openclaw/config/skills/online-search/scripts/prosearch.cjs

注意：内置 web_search 工具未配置API Key会报错，请使用元宝搜索脚本替代：
```
node '/Users/zengjun-dafeimao/Library/Application Support/QClaw/openclaw/config/skills/online-search/scripts/prosearch.cjs' --keyword="搜索词" --freshness=7d
```
返回 JSON，取 `data.docs` 中的搜索结果，`message` 字段为格式化摘要。

## 任务 Message（cron payload）

```
你是通信行业人事分析助手。请完成以下任务：

## 第一步：精准源搜索（优先）

用 --site 参数定向搜索以下头部信源，获取最近7天人员变动（--freshness=7d）：

1. --keyword="运营商 人事 任免" --freshness=7d（全网泛搜）
2. --keyword="运营商 人事变动 2026" --site=yunyingshang.com --freshness=7d（运营商财经网）
3. --keyword="运营商 总经理 董事长 任命" --site=yicai.com --freshness=7d（第一财经）
4. --keyword="运营商 人事调整" --site=thepaper.cn --freshness=7d（澎湃新闻）
5. --keyword="央企 人事 任免 运营商" --site=people.com.cn --freshness=7d（人民网）
6. --keyword="运营商 高管 变动" --site=finance.sina.com.cn --freshness=7d（新浪财经）
7. --keyword="三大运营商 人事" --site=caixin.com --freshness=7d（财新网）
8. --keyword="中国移动 人事 任免" --freshness=7d
9. --keyword="中国联通 人事 任免" --freshness=7d
10. --keyword="中国电信 人事 任免" --freshness=7d
11. --keyword="中国广电 铁塔 邮政 人事" --freshness=7d

注意：--site 和 --freshness 可以同时使用。搜索命令格式：
node '/Users/zengjun-dafeimao/Library/Application Support/QClaw/openclaw/config/skills/online-search/scripts/prosearch.cjs' --keyword="xxx" --site=xxx --freshness=7d

## 第二步：整理报告

按以下格式整理，只保留有实质变动的内容，无变动则写"暂无"：

📅 {日期} 运营商人事日报

【中国移动】
• **{姓名}** → {新职务}（{日期}）
  原任：{原职务}

【中国联通】
• ...

【中国电信】
• ...

【中国广电/铁塔/邮政】
• ...

📎 核心信源：运营商财经网 / 第一财经 / 澎湃新闻 / 人民网

## 第三步：保存与输出

1. 将完整报告保存到 ~/.qclaw/workspace/运营商人事日报_{YYYY-MM-DD}.md
2. 使用 feishu_doc 工具将当日报告追加写入飞书文档：
   - doc_token: QHRHdIihxojcLOxwB1Jc8zn2ndf
   - action: append
   - 内容格式（Markdown）：
     ```
     ## 📅 {YYYY年MM月DD日} 运营商人事日报
     
     【中国移动】
     • ...
     
     【中国联通】
     • ...
     
     【中国电信】
     • ...
     
     【中国广电/铁塔/邮政】
     • ...
     
     📎 核心信源：...
     ```
3. 直接输出报告文字（手机阅读友好，控制在300字以内，超过则只输出集团层面变动摘要）

## 注意事项
- 信源优先级：运营商财经网 > 第一财经/澎湃 > 人民网 > 新浪财经 > 其他
- 去重：同一人同一变动只列一次
- 时效：只保留最近7天内的变动
- 准确：不确定的信息标注"[待核实]"
- 交叉验证：同一事件有两个以上信源确认方可列入
- 如果所有运营商均无新变动，输出"📰 {日期} 运营商人事日报：近7天无重大人员变动。"

要求：(1) 不要回复 HEARTBEAT_OK (2) 不要调用 message 工具 (3) 直接输出报告文字
```

## Cron 创建命令（待授权恢复后执行）

```bash
openclaw cron add \
  --name "运营商人事日报" \
  --cron "0 8 * * *" \
  --session isolated \
  --agent main \
  --message "..." \
  --announce --channel wechat-access --to "agent:main:wechat-access:direct:611799966"
```

## 重点信源清单

| 优先级 | 信源 | 站点 | 说明 |
|--------|------|------|------|
| ⭐⭐⭐ | 运营商财经网 | yunyingshang.com | 最专业、最全的运营商人事报道 |
| ⭐⭐⭐ | 第一财经 | yicai.com | 权威财经媒体 |
| ⭐⭐ | 澎湃新闻 | thepaper.cn | 国企人事报道及时 |
| ⭐⭐ | 人民网 | people.com.cn | 官方人事任免公告 |
| ⭐⭐ | 新浪财经 | finance.sina.com.cn | 覆盖面广 |
| ⭐ | 财新网 | caixin.com | 深度报道 |
