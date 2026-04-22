# CRM Skill 测试用例与触发率验证

## 测试用例说明

`evals.json` 包含 7 个测试用例，覆盖以下场景：

| ID | 名称 | 场景 | 期望触发工具 |
|----|------|------|--------------|
| 1 | basic-search-japan | 基础搜索：日本地区客户 | search_customer_profile |
| 2 | search-with-criteria | 带条件搜索：年采购额+地区+行业 | search_customer_profile |
| 3 | confirm-import | 确认导入（上下文依赖） | batch_import_customer |
| 4 | implicit-search | 隐式搜索：「有没有 xx 客户」 | search_customer_profile |
| 5 | import-confirmation-yes | 简短确认：「是的，导入」 | batch_import_customer |
| 6 | search-europe-business | 搜索欧洲商务客户 | search_customer_profile |
| 7 | negative-not-import | 拒绝导入 | 不触发 batch_import |

## 触发率验证方法

### 方法 1：使用 skill-creator（推荐）

如果你已安装 skill-creator，可以在 OpenClaw/Claude 中运行：

```
用 skill-creator 验证一下 crm-customer-import skill 的触发率
```

skill-creator 会自动：
1. 加载 `evals/evals.json` 中的测试用例
2. 分别运行 with-skill 和 without-skill 版本
3. 对比结果并计算触发率

### 方法 2：手动测试

在钉钉中对 OpenClaw 机器人发送以下测试消息，观察是否正确触发 skill：

**应该触发 search_customer_profile 的消息：**
- ✅ 「帮我找一批日本地区的客户」
- ✅ 「有没有做酒店的潜在客户」
- ✅ 「找年采购额超过100万的东南亚客户」
- ✅ 「搜索欧洲的旅游公司」

**应该触发 batch_import_customer 的消息（在搜索结果展示后）：**
- ✅ 「好的，录入」
- ✅ 「是的，导入CRM」
- ✅ 「确认」

**不应该触发的消息：**
- ❌ 「不用了，先不录入」
- ❌ 「让我再想想」

### 方法 3：API 直接测试

直接调用 MCP Server 的工具：

```bash
# 测试搜索
curl -X POST http://localhost:9026/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "search_customer_profile",
      "arguments": {
        "profile_description": "日本地区的酒店客户",
        "limit": 5
      }
    },
    "id": 1
  }'
```

## 触发率指标

目标触发率：
- **搜索场景**：> 95%（用户说找客户相关的话应该触发）
- **导入场景**：> 90%（用户确认导入时应该触发）
- **误触发率**：< 5%（不相关的对话不应该触发）

## 优化触发率

如果触发率不理想，可以：

1. **扩展 description 中的触发词**
   - 在 SKILL.md 的 `description` 中添加更多同义词
   - 例如：「客户资源」「商机」「线索」等

2. **添加更多示例对话**
   - 在 SKILL.md 中添加更多 `## 示例对话` 部分

3. **运行 skill-creator 的 description optimizer**
   ```
   用 skill-creator 优化 crm-customer-import skill 的 description
   ```
