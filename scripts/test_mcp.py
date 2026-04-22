#!/usr/bin/env python3
"""
CRM MCP Server 测试脚本
用于验证 MCP Server 是否正常工作
支持 MCP SSE 协议
"""

import json
import sys
import time
import requests

class MCPClient:
    """MCP 客户端，支持 SSE 协议"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session_id = None
        self.request_id = 0
    
    def _next_id(self):
        self.request_id += 1
        return self.request_id
    
    def _parse_sse(self, text: str) -> dict:
        """解析 SSE 响应"""
        result = None
        for line in text.strip().split('\n'):
            if line.startswith('data: '):
                data = line[6:]
                if data:
                    result = json.loads(data)
        return result
    
    def _post(self, payload: dict) -> dict:
        """发送请求并解析 SSE 响应"""
        headers = {"Content-Type": "application/json"}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        
        resp = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
        
        # 保存 session id
        if "Mcp-Session-Id" in resp.headers:
            self.session_id = resp.headers["Mcp-Session-Id"]
        
        # 解析 SSE 响应
        content_type = resp.headers.get("Content-Type", "")
        if "text/event-stream" in content_type:
            return self._parse_sse(resp.text)
        else:
            return resp.json() if resp.text else None
    
    def initialize(self) -> dict:
        """初始化 MCP 会话"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"}
            }
        }
        return self._post(payload)
    
    def list_tools(self) -> dict:
        """列出可用工具"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {}
        }
        return self._post(payload)
    
    def call_tool(self, name: str, arguments: dict) -> dict:
        """调用工具"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }
        return self._post(payload)


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:9099"
    user_key = sys.argv[2] if len(sys.argv) > 2 else ""

    if not user_key:
        print("Usage: python3 test_mcp.py <url> <user_key>")
        print("  user_key: 从 AgentAuth Dashboard 获取（格式: uk_xxxxxxxx）")
        sys.exit(1)

    print(f"测试 CRM MCP Server: {url}")

    client = MCPClient(url)

    # Step 1: 初始化会话
    print("\n=== 初始化 MCP 会话 ===")
    init_result = client.initialize()
    print(f"初始化结果: {json.dumps(init_result, indent=2, ensure_ascii=False)}")

    if not init_result or "error" in init_result:
        print("初始化失败，退出")
        return

    # Step 2: 列出工具
    print("\n=== 列出可用工具 ===")
    tools_result = client.list_tools()
    print(f"工具列表: {json.dumps(tools_result, indent=2, ensure_ascii=False)}")

    # Step 3: 测试搜索
    print(f"\n=== 测试 search_customer_profile ===")
    print(f"画像: 日本地区的酒店客户")
    try:
        result = client.call_tool("search_customer_profile", {
            "user_key": user_key,
            "q_keywords": "hotel hospitality B2B",
            "organization_locations": ["Japan"],
            "per_page": 5
        })
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {e}")

    # Step 4: 测试导入（使用测试数据，注意邮箱唯一性）
    test_customers = [
        {
            "name": "测试公司",
            "contact_name": "张三",
            "contact_email": f"test_{int(time.time())}@example.com",
            "contact_phone": "13800138000",
            "contact_phone_prefix": "+86",
            "country_code": "CN",
            "address": "北京市朝阳区",
            "remark": "测试导入"
        }
    ]
    print(f"\n=== 测试 batch_import_customer ===")
    print(f"客户数: {len(test_customers)}")
    try:
        result = client.call_tool("batch_import_customer", {
            "user_key": user_key,
            "customers": test_customers
        })
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
