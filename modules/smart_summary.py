"""
智能摘要模块 (Smart Summary Module)
用于处理信息过载：接收用户的杂乱任务/想法，返回结构化摘要

核心功能：
1. 一句话总结
2. 自动分类
3. 提取重点
4. 优先级判断（重要性 + 紧急性）
5. 生成下一步建议
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PriorityItem:
    """优先级项"""
    item: str
    importance: int  # 0-10
    urgency: int     # 0-10
    reason: str = ""


@dataclass
class QuickAction:
    """快速行动"""
    desc: str
    est_minutes: int
    next_step: str
    type: str = "immediate"  # immediate | prep | calendar


@dataclass
class SummaryResult:
    """摘要结果"""
    one_line_summary: str
    categories: List[str]
    highlights: List[str]
    priority_assessment: List[PriorityItem]
    skip_candidates: List[str]
    one_hour_actions: List[QuickAction]
    suggested_next_action: QuickAction
    confidence: float
    raw_input: str
    created_at: str


# ============================================================================
# System Prompt（可直接用于 LLM API）
# ============================================================================

SMART_SUMMARY_SYSTEM_PROMPT = """你是 LifeOS 的智能摘要助手，专门帮助用户处理信息过载。

## 你的任务
接收用户输入的杂乱任务、想法或计划，输出一个结构化的 JSON 摘要。

## 输出格式（严格遵守 JSON Schema）
{
  "one_line_summary": "用一句话概括用户的整体情况（20字以内）",
  "categories": ["work", "personal", "urgent", "health", ...],
  "highlights": ["最重要的点1", "最重要的点2", ...],
  "priority_assessment": [
    {"item": "任务名", "importance": 0-10, "urgency": 0-10, "reason": "简短原因"}
  ],
  "skip_candidates": ["可以跳过或推迟的事项"],
  "one_hour_actions": [
    {"desc": "1小时内可做的动作", "est_minutes": X, "next_step": "具体下一步", "type": "immediate"}
  ],
  "suggested_next_action": {
    "desc": "最推荐的第一步",
    "est_minutes": X,
    "next_step": "具体操作",
    "type": "immediate"
  },
  "confidence": 0.0-1.0
}

## 核心原则
1. **优先级判断**：重要性(importance) > 紧急性(urgency)
2. **低摩擦启动**：优先推荐能在 1-5 分钟内完成的动作
3. **心理减负**：当用户表达疲惫时，推荐能快速完成且显著降低焦虑的动作
4. **具体可执行**：每个 next_step 必须是明确的、可立即执行的动作

## 分类标准
- work: 工作相关
- personal: 个人生活
- urgent: 有明确截止时间
- health: 健康相关
- finance: 财务相关
- social: 社交相关
- learning: 学习成长

## 时间估算标准
- 1分钟：支付、发送简短消息、确认信息
- 5分钟：列要点、整理清单、快速回复
- 15分钟：准备材料、初步研究
- 30分钟以上：深度工作、会议

输出必须是可解析的 JSON，不要包含任何额外的文字说明。
"""


# ============================================================================
# Few-Shot Examples（供 LLM 学习）
# ============================================================================

FEW_SHOT_EXAMPLES = [
    {
        "user_input": "今天要做7件事：写报告A、答复邮件、准备明天会议、付房租、买菜、洗衣服、打电话给妈妈。我累了，不知道先做哪个。",
        "assistant_output": {
            "one_line_summary": "用户有7件任务，感到疲惫且无法优先排序",
            "categories": ["work", "personal", "urgent", "finance"],
            "highlights": [
                "报告A需要高集中度时间",
                "付房租有截止时间（今天）",
                "用户表达疲惫，需要低摩擦启动"
            ],
            "priority_assessment": [
                {"item": "付房租", "importance": 9, "urgency": 9, "reason": "截止时间今天，避免滞纳金"},
                {"item": "写报告A", "importance": 10, "urgency": 7, "reason": "明天截止，需深度工作"},
                {"item": "准备明天会议", "importance": 8, "urgency": 8, "reason": "明天就要用"},
                {"item": "打电话给妈妈", "importance": 7, "urgency": 3, "reason": "情感维系重要但不紧急"},
                {"item": "答复邮件", "importance": 6, "urgency": 5, "reason": "取决于邮件内容"},
                {"item": "买菜", "importance": 5, "urgency": 4, "reason": "可推迟到晚上或明天"},
                {"item": "洗衣服", "importance": 4, "urgency": 3, "reason": "可推迟"}
            ],
            "skip_candidates": ["洗衣服（可推到明天）", "买菜（可简化为外卖）"],
            "one_hour_actions": [
                {
                    "desc": "付房租",
                    "est_minutes": 2,
                    "next_step": "打开银行APP，选择房租转账",
                    "type": "immediate"
                },
                {
                    "desc": "列出报告A的3个核心要点",
                    "est_minutes": 5,
                    "next_step": "打开文档，用5分钟列出框架",
                    "type": "prep"
                }
            ],
            "suggested_next_action": {
                "desc": "先付房租（1分钟完成）",
                "est_minutes": 2,
                "next_step": "打开手机银行APP，完成转账",
                "type": "immediate"
            },
            "confidence": 0.95
        }
    },
    {
        "user_input": "感觉压力好大，明天要面试，今天还要准备材料，下午还有个会。",
        "assistant_output": {
            "one_line_summary": "用户面临面试压力，当天任务较多",
            "categories": ["work", "urgent"],
            "highlights": [
                "明天面试是核心压力源",
                "准备材料是当天最重要任务",
                "下午有会议，时间紧张"
            ],
            "priority_assessment": [
                {"item": "准备面试材料", "importance": 10, "urgency": 10, "reason": "明天面试，今天必须完成"},
                {"item": "下午会议", "importance": 7, "urgency": 8, "reason": "已定时间，必须参加"}
            ],
            "skip_candidates": [],
            "one_hour_actions": [
                {
                    "desc": "列出面试可能被问到的3个问题",
                    "est_minutes": 10,
                    "next_step": "打开笔记本，回忆岗位需求，写下3个核心问题",
                    "type": "prep"
                },
                {
                    "desc": "准备自我介绍（1分钟版本）",
                    "est_minutes": 15,
                    "next_step": "对着镜子练习3遍，计时确保在1分钟内",
                    "type": "immediate"
                }
            ],
            "suggested_next_action": {
                "desc": "先用5分钟深呼吸放松，然后列出面试3个问题",
                "est_minutes": 5,
                "next_step": "设置5分钟计时器，专注深呼吸",
                "type": "immediate"
            },
            "confidence": 0.92
        }
    },
    {
        "user_input": "今天就想休息，但还有点杂事：回个消息、整理桌面、可能要买点东西。",
        "assistant_output": {
            "one_line_summary": "用户想休息，只有少量低优先级任务",
            "categories": ["personal"],
            "highlights": [
                "用户明确表达想休息",
                "任务都是可推迟的杂事"
            ],
            "priority_assessment": [
                {"item": "回消息", "importance": 5, "urgency": 4, "reason": "取决于消息内容，大多可推迟"},
                {"item": "整理桌面", "importance": 3, "urgency": 2, "reason": "可随时做"},
                {"item": "买东西", "importance": 4, "urgency": 3, "reason": "不紧急，可明天"}
            ],
            "skip_candidates": ["整理桌面（可以明天）", "买东西（可以明天或网购）"],
            "one_hour_actions": [
                {
                    "desc": "快速浏览消息，只回复紧急的",
                    "est_minutes": 3,
                    "next_step": "打开手机，设置3分钟计时，只回复标记为紧急的",
                    "type": "immediate"
                }
            ],
            "suggested_next_action": {
                "desc": "用1分钟快速回复最重要的消息，然后去休息",
                "est_minutes": 1,
                "next_step": "打开消息列表，只回复第一条，其他明天再说",
                "type": "immediate"
            },
            "confidence": 0.88
        }
    }
]


# ============================================================================
# 解析器与辅助函数
# ============================================================================

class SmartSummaryParser:
    """智能摘要解析器"""
    
    @staticmethod
    def parse_llm_response(response_text: str, user_input: str) -> Optional[SummaryResult]:
        """
        解析 LLM 返回的 JSON 响应
        
        Args:
            response_text: LLM 返回的文本
            user_input: 用户原始输入
            
        Returns:
            SummaryResult 对象，或 None（如果解析失败）
        """
        try:
            # 尝试提取 JSON（处理可能包含 markdown 代码块的情况）
            json_text = response_text.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            json_text = json_text.strip()
            
            data = json.loads(json_text)
            
            # 构建 PriorityItem 列表
            priority_items = [
                PriorityItem(
                    item=p.get("item", ""),
                    importance=p.get("importance", 5),
                    urgency=p.get("urgency", 5),
                    reason=p.get("reason", "")
                )
                for p in data.get("priority_assessment", [])
            ]
            
            # 构建 QuickAction 列表
            one_hour_actions = [
                QuickAction(
                    desc=a.get("desc", ""),
                    est_minutes=a.get("est_minutes", 5),
                    next_step=a.get("next_step", ""),
                    type=a.get("type", "immediate")
                )
                for a in data.get("one_hour_actions", [])
            ]
            
            # 构建推荐动作
            suggested = data.get("suggested_next_action", {})
            suggested_action = QuickAction(
                desc=suggested.get("desc", ""),
                est_minutes=suggested.get("est_minutes", 5),
                next_step=suggested.get("next_step", ""),
                type=suggested.get("type", "immediate")
            )
            
            return SummaryResult(
                one_line_summary=data.get("one_line_summary", ""),
                categories=data.get("categories", []),
                highlights=data.get("highlights", []),
                priority_assessment=priority_items,
                skip_candidates=data.get("skip_candidates", []),
                one_hour_actions=one_hour_actions,
                suggested_next_action=suggested_action,
                confidence=data.get("confidence", 0.8),
                raw_input=user_input,
                created_at=datetime.now().isoformat()
            )
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"解析错误: {e}")
            return None
    
    @staticmethod
    def to_json(summary: SummaryResult) -> str:
        """将 SummaryResult 转换为 JSON 字符串"""
        def convert(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return obj
        
        return json.dumps(asdict(summary), ensure_ascii=False, indent=2)
    
    @staticmethod
    def format_for_display(summary: SummaryResult) -> str:
        """格式化为人类可读的显示文本"""
        lines = [
            f"📋 {summary.one_line_summary}",
            "",
            f"🏷️ 分类: {', '.join(summary.categories)}",
            "",
            "✨ 重点:",
        ]
        for h in summary.highlights:
            lines.append(f"  • {h}")
        
        lines.append("")
        lines.append("⚡ 优先级排序:")
        for p in sorted(summary.priority_assessment, 
                       key=lambda x: (x.importance + x.urgency), 
                       reverse=True)[:5]:
            lines.append(f"  {p.item} [重要:{p.importance} 紧急:{p.urgency}]")
            if p.reason:
                lines.append(f"    → {p.reason}")
        
        if summary.skip_candidates:
            lines.append("")
            lines.append("⏸️ 可推迟:")
            for s in summary.skip_candidates:
                lines.append(f"  • {s}")
        
        lines.append("")
        lines.append(f"🎯 建议下一步: {summary.suggested_next_action.desc}")
        lines.append(f"   预计时间: {summary.suggested_next_action.est_minutes}分钟")
        lines.append(f"   具体操作: {summary.suggested_next_action.next_step}")
        
        return "\n".join(lines)


# ============================================================================
# 构建完整 Prompt 的辅助函数
# ============================================================================

def build_smart_summary_prompt(user_input: str, include_examples: bool = True) -> List[Dict[str, str]]:
    """
    构建完整的 LLM prompt（messages 格式）
    
    Args:
        user_input: 用户输入
        include_examples: 是否包含 few-shot 示例
        
    Returns:
        messages 列表（适用于 OpenAI API 等）
    """
    messages = [
        {"role": "system", "content": SMART_SUMMARY_SYSTEM_PROMPT}
    ]
    
    if include_examples:
        for example in FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["user_input"]})
            messages.append({
                "role": "assistant", 
                "content": json.dumps(example["assistant_output"], ensure_ascii=False, indent=2)
            })
    
    messages.append({"role": "user", "content": user_input})
    
    return messages


# ============================================================================
# 测试与示例
# ============================================================================

if __name__ == "__main__":
    # 示例：模拟 LLM 响应
    test_input = "今天要处理项目文档、开会、还要去取快递，感觉有点乱。"
    
    # 模拟的 LLM 响应（实际应该调用 LLM API）
    mock_response = """```json
{
  "one_line_summary": "用户有3件事待办，感觉混乱",
  "categories": ["work", "personal"],
  "highlights": [
    "项目文档可能需要集中时间",
    "取快递是低摩擦任务"
  ],
  "priority_assessment": [
    {"item": "项目文档", "importance": 8, "urgency": 7, "reason": "工作相关，需要完成"},
    {"item": "开会", "importance": 7, "urgency": 8, "reason": "已定时间"},
    {"item": "取快递", "importance": 4, "urgency": 5, "reason": "可随时取"}
  ],
  "skip_candidates": [],
  "one_hour_actions": [
    {
      "desc": "先去取快递（10分钟）",
      "est_minutes": 10,
      "next_step": "下楼到快递柜取件",
      "type": "immediate"
    },
    {
      "desc": "列出项目文档的3个章节",
      "est_minutes": 5,
      "next_step": "打开文档，写下大纲",
      "type": "prep"
    }
  ],
  "suggested_next_action": {
    "desc": "先取快递（10分钟轻松完成）",
    "est_minutes": 10,
    "next_step": "下楼到快递柜，顺便活动一下",
    "type": "immediate"
  },
  "confidence": 0.85
}
```"""
    
    # 解析
    parser = SmartSummaryParser()
    result = parser.parse_llm_response(mock_response, test_input)
    
    if result:
        print("✅ 解析成功！\n")
        print(parser.format_for_display(result))
        print("\n" + "="*50)
        print("\n📄 JSON 输出:")
        print(parser.to_json(result))
    else:
        print("❌ 解析失败")
    
    # 显示如何构建 prompt
    print("\n" + "="*50)
    print("\n📝 构建的 Prompt Messages:")
    messages = build_smart_summary_prompt(test_input, include_examples=False)
    for i, msg in enumerate(messages):
        print(f"\n[{i}] {msg['role'].upper()}:")
        print(msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content'])
