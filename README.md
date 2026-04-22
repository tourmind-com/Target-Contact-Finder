# CRM OpenClaw Skill 使用指南

## 概述

本技能为 CRM 系统提供客户画像搜索与批量导入功能，可通过 OpenClaw 钉钉助手机器人使用。

## 功能

1. **搜索客户画像**：根据自然语言描述搜索匹配的潜在客户
2. **批量导入客户**：将搜索结果批量导入 CRM 作为潜在客户

## 目录结构

```
skill/
├── SKILL.md              # Skill 主文件（OpenClaw 加载）
├── README.md             # 本文档
└── evals/
    ├── evals.json        # 测试用例
    └── README.md         # 测试说明
```

## 部署步骤

### 1. 启动 CRM MCP Server

CRM 服务已集成 MCP Server，有两种启动方式：

#### 方式 A：与主服务一起启动（推荐）

MCP Server 默认在主服务启动时一并启动，监听 `:9026` 端口。

需通过环境变量配置 AgentAuth：

```bash
export AGENTAUTH_BASE_URL=https://aauth-170125614655.asia-northeast1.run.app
export AGENTAUTH_APP_KEY=YOUR_AGENTAUTH_APP_KEY
```

#### 方式 B：独立启动

```bash
cd /path/to/crm
AGENTAUTH_BASE_URL=https://aauth-170125614655.asia-northeast1.run.app \
AGENTAUTH_APP_KEY=YOUR_AGENTAUTH_APP_KEY \
go run cmd/mcp/main.go -p 9026
```

### 2. 配置 OpenClaw

在 OpenClaw 的 `~/.openclaw/openclaw.json` 中添加 MCP Server 配置（无需请求头鉴权，鉴权通过工具参数 `user_key` 完成）：

```json
{
  "mcpServers": {
    "crm": {
      "url": "http://your-crm-server:9026/mcp",
      "transport": "streamable-http"
    }
  }
}
```

如果 OpenClaw 和 CRM 在同一台 ECS：
```json
{
  "mcpServers": {
    "crm": {
      "url": "http://127.0.0.1:9026/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### 3. 安装 Skill

将 `skill/SKILL.md` 文件复制到 OpenClaw 的技能目录：

```bash
# 方式 A：直接复制
cp skill/SKILL.md ~/.openclaw/skills/crm-customer-import/SKILL.md

# 方式 B：通过 ClawHub（如果已发布）
clawhub install crm-customer-import
```

### 4. 重启 OpenClaw 网关

```bash
openclaw gateway restart
```

### 5. 验证

```bash
# 检查 MCP Server 是否正常
openclaw mcp list

# 应该看到：
# SERVER    STATUS    TOOLS   TRANSPORT
# crm       running   2       streamable-http
```

## 使用方式

在钉钉中与 OpenClaw 机器人对话：

```
用户：帮我找一批日本地区的客户

机器人：好的，我来帮您搜索日本地区的客户。
       
       根据您的画像「日本地区」，找到以下 10 位匹配客户：
       
       1. 东京旅游株式会社 (相似度: 95%)
          联系人：田中太郎
          邮箱：tanaka@tokyo-travel.jp
          ...
       
       请问是否要将这些客户录入 CRM 系统？

用户：好的，录入

机器人：导入完成！成功 10 条，失败 0 条。
```

## MCP Tools

| Tool | 描述 |
|------|------|
| `search_customer_profile` | 根据画像描述搜索匹配的客户 |
| `batch_import_customer` | 将客户批量导入 CRM 作为潜在客户 |

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `AGENTAUTH_BASE_URL` | AgentAuth 服务地址 | 无，必填 |
| `AGENTAUTH_APP_KEY` | AgentAuth App Key | 无，必填 |
| `MCP_PORT` | MCP Server 端口 | 9026 |

### 端口

| 端口 | 服务 |
|------|------|
| 9025 | CRM 主服务（HTTP API） |
| 9026 | CRM MCP Server |

## 注意事项

1. **网络配置**：确保 OpenClaw 所在机器能访问 CRM 的 MCP 端口
2. **邮箱去重**：系统按联系邮箱去重，重复邮箱会导入失败
3. **必填字段**：客户名称、联系人、联系邮箱、联系电话为必填
4. **Mock 数据**：当前搜索接口返回 Mock 数据，待接入真实画像 API 后替换

## 后续扩展

- [ ] 接入真实的客户画像搜索 API
- [ ] 支持登录态，记录商务联系人
- [ ] 支持从搜索结果中勾选部分客户导入
- [ ] 支持更多客户字段（标签、区域等）

## 故障排查

### MCP Server 无法连接

1. 检查 CRM 服务是否启动
2. 检查端口是否被占用：`lsof -i :9026`
3. 检查防火墙规则

### 导入失败

1. 检查必填字段是否完整
2. 检查邮箱是否已存在
3. 查看 CRM 服务日志

### OpenClaw 无法识别 Skill

1. 确认 SKILL.md 文件路径正确
2. 重启 OpenClaw 网关：`openclaw gateway restart`
3. 检查 OpenClaw 日志

## 触发率验证

### 使用 skill-creator 验证

在 OpenClaw/Claude 中发送：

```
用 skill-creator 验证一下 crm-customer-import skill 的触发率
```

### 手动测试触发率

发送以下测试消息，观察是否正确触发：

| 测试消息 | 期望触发 |
|----------|----------|
| 帮我找一批日本地区的客户 | ✅ search_customer_profile |
| 有没有做酒店的潜在客户 | ✅ search_customer_profile |
| 好的，录入 | ✅ batch_import_customer |
| 不用了 | ❌ 不触发 |

详细测试用例见 `evals/evals.json`。

### 优化触发率

如果触发率不理想：

```
用 skill-creator 优化 crm-customer-import skill 的 description
```
