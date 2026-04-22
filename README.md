# Target Contact Finder — OpenClaw Skill

通过结构化条件搜索酒旅行业 B2B 潜在客户，确认后批量导入 CRM。

## 功能

- **搜索客户画像**：按行业、地区、岗位、层级等条件搜索匹配的潜在联系人
- **批量导入客户**：将搜索结果批量导入 CRM 作为潜在客户

## 目录结构

```
skill/
├── SKILL.md          # Skill 主文件（OpenClaw 加载）
├── DEPLOY.md         # 详细部署指南
├── README.md         # 本文档
├── evals/
│   ├── evals.json    # 测试用例
│   └── README.md     # 测试说明
└── scripts/
    └── test_mcp.py   # 接口测试脚本
```

## 快速部署

### 1. 启动 Skill HTTP Server

```bash
go build -o crm-skill ./mcp/cmd/
nohup ./crm-skill -port :9059 > crm-skill.log 2>&1 &
```

所需环境变量：

```bash
export APOLLO_API_KEY="your-apollo-master-api-key"
export AGENTAUTH_BASE_URL="https://aauth-170125614655.asia-northeast1.run.app"
export AGENTAUTH_APP_KEY="your-agentauth-app-key"
```

### 2. 安装 Skill

将 `SKILL.md` 复制到 OpenClaw 技能目录，重启网关：

```bash
mkdir -p ~/.openclaw/skills/crm-customer-import
cp skill/SKILL.md ~/.openclaw/skills/crm-customer-import/
openclaw gateway restart
```

无需在 `openclaw.json` 中配置任何 MCP server，Skill 直接通过 HTTP 调用接口。

## API

**Base URL:** `http://39.108.114.224:9059`

| 接口 | 说明 |
|------|------|
| `POST /skill/search_customer_profile` | 搜索客户画像 |
| `POST /skill/batch_import_customer` | 批量导入客户 |

所有请求体需包含 `user_key` 字段（从 AgentAuth Dashboard 获取）。

## 使用示例

```
用户：帮我找一批日本地区的酒店客户

机器人：根据您的需求，搜索条件如下：
       - 关键词：hotel hospitality resort
       - 公司地区：Japan
       - 联系人层级：manager, director, head

       共找到 120 条记录，本次获取 10 条：
       1. Hilton Tokyo — 联系人：田中太郎 ...
       ...
       是否录入 CRM？

用户：好的，录入

机器人：导入完成！成功 10 条，失败 0 条。
```

## 详细部署说明

见 [DEPLOY.md](DEPLOY.md)。
