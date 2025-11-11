"""
每日简报生成节点
"""
from typing import Dict
from datetime import datetime, timedelta
from app.models import GraphState, ChatMessage
from app.database import Database
from app.llm_provider import BaseLLMProvider, DAILY_BRIEF_PROMPT


def plan_node(state: GraphState, db: Database, llm: BaseLLMProvider) -> Dict:
    """
    每日简报节点：生成个性化的每日计划和建议
    """
    user_id = state.user_id
    today = datetime.now()
    
    # 检查今天是否已生成简报
    existing_brief = db.get_daily_brief(user_id, today)
    if existing_brief:
        # 从数据库获取已保存的简报数据
        key_focuses = existing_brief.get('key_focuses', [])
        risk_alerts = existing_brief.get('risk_alerts', [])
        encouragement = existing_brief.get('encouragement', '加油！')
        energy = existing_brief.get('energy_prediction', 75)
        
        response = f"""📋 今日简报 - {today.strftime('%Y年%m月%d日')}

⚡ 能量预测：{energy:.0f}%

🎯 今日重点：
"""
        if key_focuses:
            for i, focus in enumerate(key_focuses, 1):
                task = focus.get('task', '')
                time = focus.get('time', '')
                reason = focus.get('reason', '')
                response += f"{i}. {time}: {task}\n   原因：{reason}\n\n"
        else:
            response += "- 暂无今日重点，可以聊聊你今天想做什么～\n\n"
        
        if risk_alerts:
            response += "⚠️ 提示：\n"
            for alert in risk_alerts:
                response += f"- {alert}\n"
            response += "\n"
        
        response += f"💬 {encouragement}"
        
        state.messages.append(ChatMessage(role="assistant", content=response))
        return {"messages": state.messages, "next_node": None}
    
    # 收集数据生成新简报
    habits = db.get_user_habits(user_id)
    habit_records = []
    for habit in habits:
        records = db.get_habit_records(habit['id'], limit=14)
        habit_records.extend(records)
    
    # 计算能量预测（简化版：基于最近完成率）
    recent_7_days = [r for r in habit_records if (today - datetime.fromisoformat(r['date'])).days <= 7]
    if recent_7_days:
        completed = len([r for r in recent_7_days if r['status'] == 'completed'])
        energy_prediction = 50 + (completed / len(recent_7_days) * 50)
    else:
        energy_prediction = 75.0  # 默认值
    
    # 获取最近的反思，了解用户状态
    recent_reflections = db.get_recent_reflections(user_id, limit=3)
    
    # ===== 基于用户的实际习惯生成重点任务 =====
    key_focuses = []
    if habits:
        # 为每个活跃的习惯生成今日提醒
        for habit in habits[:5]:  # 最多显示5个习惯
            # 检查今天是否已完成
            today_records = [r for r in habit_records if r['habit_id'] == habit['id'] and 
                           datetime.fromisoformat(r['date']).date() == today.date()]
            
            status_text = "✅ 已完成" if today_records and today_records[0]['status'] == 'completed' else "⏳ 待完成"
            
            key_focuses.append({
                "time": "全天",
                "task": f"{habit['name']} [{status_text}]",
                "reason": habit.get('description') or f"你设定的 {habit['target_frequency']} 习惯"
            })
    
    # 如果没有习惯，给出建议
    if not key_focuses:
        key_focuses.append({
            "time": "今天",
            "task": "创建第一个习惯",
            "reason": "可以从简单的目标开始，比如：每天喝8杯水、阅读10分钟、早睡早起等"
        })
    
    # ===== 根据完成率生成风险提示 =====
    risk_alerts = []
    if energy_prediction < 50:
        risk_alerts.append("最近完成率较低，建议适当调整目标难度")
    elif energy_prediction < 70:
        risk_alerts.append("继续保持，可以尝试增加一点挑战")
    
    if not habits:
        risk_alerts.append("还没有创建习惯，点击右上角'习惯管理'开始设定目标")
    
    # 检查是否有长期未完成的习惯
    for habit in habits:
        recent_habit_records = [r for r in habit_records if r['habit_id'] == habit['id'] and 
                               (today - datetime.fromisoformat(r['date'])).days <= 7]
        if recent_habit_records:
            completed_count = len([r for r in recent_habit_records if r['status'] == 'completed'])
            if completed_count == 0:
                risk_alerts.append(f"习惯'{habit['name']}'已经7天未完成，需要调整吗？")
    
    # ===== 根据能量预测生成鼓励语 =====
    if energy_prediction >= 80:
        encouragement = "🌟 状态非常好！你正在养成优秀的习惯，继续保持！"
    elif energy_prediction >= 60:
        encouragement = "💪 进展不错！每一天的坚持都在积累改变的力量。"
    elif energy_prediction >= 40:
        encouragement = "🌱 不要气馁，习惯养成需要时间，给自己多一点耐心。"
    else:
        encouragement = "� 每一天都是新的开始，从最简单的一个习惯开始重新出发吧！"
    
    # 保存简报到数据库
    db.save_daily_brief(
        user_id=user_id,
        date=today,
        energy_prediction=energy_prediction,
        key_focuses=key_focuses,
        risk_alerts=risk_alerts if risk_alerts else ["目前一切顺利！"],
        encouragement=encouragement
    )
    
    # ===== 生成简报文本 =====
    response = f"""📋 今日简报 - {today.strftime('%Y年%m月%d日 %A')}

⚡ 能量预测：{energy_prediction:.0f}%
{f"（基于最近7天完成 {len([r for r in recent_7_days if r['status'] == 'completed'])}/{len(recent_7_days)} 次习惯）" if recent_7_days else "（暂无历史数据）"}

🎯 今日习惯清单：
"""
    
    for i, focus in enumerate(key_focuses, 1):
        task = focus.get('task', '')
        reason = focus.get('reason', '')
        response += f"{i}. {task}\n   💡 {reason}\n\n"
    
    if risk_alerts:
        response += "⚠️ 提示：\n"
        for alert in risk_alerts:
            response += f"• {alert}\n"
        response += "\n"
    
    response += f"💬 {encouragement}\n\n"
    response += "---\n💭 你可以告诉我：\n• 完成了某个习惯\n• 今天遇到了什么困难\n• 想调整习惯目标"
    
    state.messages.append(ChatMessage(role="assistant", content=response))
    return {"messages": state.messages, "next_node": None}
