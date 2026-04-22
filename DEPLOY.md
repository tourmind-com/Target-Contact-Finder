# CRM Skill 完整部署指南

## 架构说明

```
钉钉用户 ──► OpenClaw (ECS) ──► CRM Skill HTTP Server (:9059) ──► Apollo API ──► CRM 数据库
                │                                                   (Search + Enrich)
                └── 加载 SKILL.md
```

**需要部署的组件：**
1. ✅ CRM Skill HTTP Server（独立进程，端口 9059）
2. ✅ Apollo API Key 配置
3. ✅ 安装 SKILL.md 到 OpenClaw（无需配置 MCP）

---

## 第一步：部署 CRM Skill HTTP Server

### 1.1 拉取代码

```bash
cd /path/to/your/workspace
git clone <crm-repo-url>
cd crm
```

### 1.2 编译 Skill Server

```bash
go build -o crm-skill ./mcp/cmd/
```

### 1.3 配置环境变量

```bash
# Apollo API Key（必须是 Master Key）
export APOLLO_API_KEY="your-apollo-api-key-here"

# AgentAuth 配置（用于 user_key 鉴权）
export AGENTAUTH_BASE_URL="https://aauth-170125614655.asia-northeast1.run.app"
export AGENTAUTH_APP_KEY="your-agentauth-app-key-here"

# 建议写入系统环境持久化
cat >> /etc/profile.d/crm-skill.sh << 'EOF'
export APOLLO_API_KEY="your-apollo-api-key-here"
export AGENTAUTH_BASE_URL="https://aauth-170125614655.asia-northeast1.run.app"
export AGENTAUTH_APP_KEY="your-agentauth-app-key-here"
EOF
source /etc/profile.d/crm-skill.sh
```

### 1.4 启动服务

```bash
# 前台启动
./crm-skill -port :9059

# nohup 后台运行
nohup ./crm-skill -port :9059 > crm-skill.log 2>&1 &
```

**端口说明：**
| 端口 | 服务 | 说明 |
|------|------|------|
| 9059 | CRM Skill HTTP API | 供 OpenClaw skill 直接调用 |

**环境变量：**
| 变量 | 必填 | 说明 |
|------|------|------|
| APOLLO_API_KEY | 是 | Apollo API Key（Master Key） |
| AGENTAUTH_BASE_URL | 是 | AgentAuth 服务地址，用于验证 user_key |
| AGENTAUTH_APP_KEY | 是 | AgentAuth App Key |

### 1.5 验证服务

```bash
# 检查端口
curl -s -X POST http://127.0.0.1:9059/skill/search_customer_profile \
  -H "Content-Type: application/json" \
  -d '{"user_key": "test"}' | jq .
# 期望返回 {"ok":false,"error":"unauthorized: ..."}
```

---

## 第二步：安装 SKILL.md

### 2.1 创建 Skill 目录

```bash
mkdir -p ~/.openclaw/skills/crm-customer-import
```

### 2.2 复制 SKILL.md

**方式 A：直接复制（如果能访问 CRM 代码）**
```bash
cp /path/to/crm/skill/SKILL.md ~/.openclaw/skills/crm-customer-import/
```

**方式 B：手动创建**

直接从源码仓库 `skill/SKILL.md` 复制完整内容，请勿裁剪。

---

## 第三步：重启 OpenClaw

```bash
openclaw gateway restart
```

---

## 第四步：验证

### 4.1 在钉钉中测试

发送消息给 OpenClaw 机器人：

```
帮我找一批日本地区的酒店B2B客户
```

期望响应：
- 机器人将自然语言解析为结构化参数
- 通过 `curl` 调用 `http://39.108.114.224:9059/skill/search_customer_profile`
- 展示客户列表（公司名称、联系人、邮箱、电话、地址）
- 询问是否录入 CRM

然后回复：
```
好的，录入
```

期望响应：
- 机器人调用 `/skill/batch_import_customer`
- 返回「成功 X 条，失败 Y 条」

---

## 常见问题

### Q1: 接口调用返回 unauthorized

删除 `{baseDir}/user_key.txt`，重新获取 user_key：https://aauth-170125614655.asia-northeast1.run.app/dashboard

### Q2: 导入失败「联系邮箱已存在」

这是正常的去重逻辑。CRM 按邮箱去重，已存在的邮箱会跳过。

### Q3: 搜索报错 "APOLLO_API_KEY 环境变量未配置"

确认 `APOLLO_API_KEY` 环境变量已设置：
```bash
echo $APOLLO_API_KEY
```

### Q4: Apollo API 返回 403 "API_INACCESSIBLE"

Apollo People Search API 需要 **Master API Key**。参考 [Apollo 文档](https://docs.apollo.io/docs/create-api-key) 创建 Master Key。

### Q5: 搜索无结果或全部无邮箱

尝试放宽搜索条件（减少过滤项），Apollo 数据覆盖有区域差异。

### Q6: Skill 不触发

1. 确认 SKILL.md 路径正确
2. 重启 OpenClaw：`openclaw gateway restart`

---

## 快速检查清单

- [ ] `APOLLO_API_KEY` 环境变量已配置（Master Key）
- [ ] `AGENTAUTH_BASE_URL` 和 `AGENTAUTH_APP_KEY` 环境变量已配置
- [ ] CRM Skill HTTP Server 已启动（端口 9059）
- [ ] 服务器能访问 `api.apollo.io`（外网）
- [ ] 服务器能访问 AgentAuth 服务（外网）
- [ ] SKILL.md 已复制到 `~/.openclaw/skills/crm-customer-import/`
- [ ] OpenClaw 已重启
- [ ] 钉钉测试通过（首次使用时会提示获取 user_key）

