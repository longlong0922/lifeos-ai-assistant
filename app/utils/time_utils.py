"""
时间工具函数
"""
from datetime import datetime, timedelta
from typing import List


def get_week_day_name(date: datetime) -> str:
    """获取星期几的中文名称"""
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return weekdays[date.weekday()]


def get_time_of_day(hour: int) -> str:
    """根据小时数返回时段描述"""
    if 5 <= hour < 12:
        return "上午"
    elif 12 <= hour < 14:
        return "中午"
    elif 14 <= hour < 18:
        return "下午"
    elif 18 <= hour < 22:
        return "晚上"
    else:
        return "深夜"


def get_recent_dates(days: int = 7) -> List[datetime]:
    """获取最近N天的日期列表"""
    today = datetime.now()
    return [today - timedelta(days=i) for i in range(days)]


def format_time_range(start_hour: int, end_hour: int) -> str:
    """格式化时间范围"""
    return f"{start_hour:02d}:00-{end_hour:02d}:00"


def is_weekend(date: datetime) -> bool:
    """判断是否是周末"""
    return date.weekday() >= 5


def days_between(date1: datetime, date2: datetime) -> int:
    """计算两个日期之间的天数"""
    return abs((date2 - date1).days)
