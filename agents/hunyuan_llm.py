"""
腾讯混元 LLM 封装
使用腾讯云 SDK 正确调用混元 API
"""

import json
import os
from typing import List, Dict, Any, Optional
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models


class HunyuanLLM:
    """腾讯混元大模型封装"""
    
    def __init__(
        self,
        secret_id: str,
        secret_key: str,
        model: str = "hunyuan-large",
        region: str = "ap-guangzhou"
    ):
        """
        初始化混元客户端
        
        Args:
            secret_id: 腾讯云 SecretId
            secret_key: 腾讯云 SecretKey
            model: 模型名称
            region: 服务地域
        """
        self.model = model
        
        # 创建认证凭证
        cred = credential.Credential(secret_id, secret_key)
        
        # 配置 HTTP 请求
        httpProfile = HttpProfile()
        httpProfile.endpoint = "hunyuan.tencentcloudapi.com"
        
        # 创建客户端配置
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        
        # 创建混元客户端
        self.client = hunyuan_client.HunyuanClient(cred, region, clientProfile)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0
    ) -> str:
        """
        调用混元对话接口
        
        Args:
            messages: 对话消息列表 [{"role": "user", "content": "..."}] 或 LangChain Message 对象
            temperature: 温度参数
            max_tokens: 最大输出 token 数
            top_p: 核采样参数
        
        Returns:
            模型回复内容
        """
        try:
            # 转换消息格式：处理字典或 LangChain 消息对象
            formatted_messages = []
            for msg in messages:
                # 检查是否是 LangChain 消息对象
                if hasattr(msg, 'type') and hasattr(msg, 'content'):
                    # LangChain 消息对象
                    role_mapping = {
                        'system': 'system',
                        'human': 'user',
                        'ai': 'assistant',
                        'user': 'user',
                        'assistant': 'assistant'
                    }
                    role = role_mapping.get(msg.type, 'user')
                    content = msg.content
                else:
                    # 字典格式
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                
                formatted_msg = {
                    "Role": role,
                    "Content": content
                }
                formatted_messages.append(formatted_msg)
            
            # 创建请求
            req = models.ChatCompletionsRequest()
            params = {
                "Model": self.model,
                "Messages": formatted_messages,
                "Temperature": temperature,
                "TopP": top_p
            }
            req.from_json_string(json.dumps(params))
            
            # 发送请求
            resp = self.client.ChatCompletions(req)
            
            # 解析响应
            response_dict = json.loads(resp.to_json_string())
            
            # 提取回复内容
            if "Choices" in response_dict and len(response_dict["Choices"]) > 0:
                return response_dict["Choices"][0]["Message"]["Content"]
            else:
                return "抱歉，我暂时无法回答。"
                
        except Exception as e:
            print(f"❌ 混元 API 调用失败: {str(e)}")
            return f"抱歉，服务暂时不可用：{str(e)}"
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        """
        LangChain 兼容接口
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
        
        Returns:
            包含 content 的响应对象
        """
        content = self.chat(
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000),
            top_p=kwargs.get("top_p", 1.0)
        )
        
        # 返回类似 LangChain 的响应格式
        class Response:
            def __init__(self, content):
                self.content = content
        
        return Response(content)


def create_hunyuan_llm(
    secret_id: Optional[str] = None,
    secret_key: Optional[str] = None,
    model: Optional[str] = None
) -> HunyuanLLM:
    """
    创建混元 LLM 实例（从环境变量读取配置）
    
    Args:
        secret_id: SecretId（可选，默认从环境变量读取）
        secret_key: SecretKey（可选，默认从环境变量读取）
        model: 模型名称（可选，默认 hunyuan-large）
    
    Returns:
        混元 LLM 实例
    """
    secret_id = secret_id or os.getenv("TENCENT_SECRET_ID")
    secret_key = secret_key or os.getenv("TENCENT_SECRET_KEY")
    model = model or os.getenv("HUNYUAN_MODEL", "hunyuan-large")
    
    if not secret_id or not secret_key:
        raise ValueError("请设置 TENCENT_SECRET_ID 和 TENCENT_SECRET_KEY 环境变量")
    
    return HunyuanLLM(
        secret_id=secret_id,
        secret_key=secret_key,
        model=model
    )


if __name__ == "__main__":
    # 测试代码
    from dotenv import load_dotenv
    load_dotenv()
    
    llm = create_hunyuan_llm()
    
    messages = [
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
    
    response = llm.chat(messages)
    print(f"回复: {response}")
