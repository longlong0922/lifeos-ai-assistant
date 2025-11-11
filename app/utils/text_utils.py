"""
文本处理工具函数
"""
from typing import List, Dict
import re


def extract_keywords(text: str, keywords: List[str]) -> List[str]:
    """从文本中提取关键词"""
    found = []
    text_lower = text.lower()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found.append(keyword)
    return found


def count_word_frequency(texts: List[str]) -> Dict[str, int]:
    """统计词频"""
    word_count = {}
    for text in texts:
        # 简单分词（中文）
        words = re.findall(r'[\u4e00-\u9fff]+', text)
        for word in words:
            if len(word) >= 2:  # 只统计2个字以上的词
                word_count[word] = word_count.get(word, 0) + 1
    return word_count


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_emotions(text: str) -> List[str]:
    """提取情绪词汇"""
    emotion_keywords = {
        '正面': ['开心', '高兴', '满足', '愉快', '兴奋', '期待', '放松', '平静'],
        '负面': ['累', '烦', '焦虑', '压力', '无力', '失落', '难过', '沮丧', '生气', '愤怒']
    }
    
    found_emotions = []
    text_lower = text.lower()
    
    for category, words in emotion_keywords.items():
        for word in words:
            if word in text_lower:
                found_emotions.append(f"{category}:{word}")
    
    return found_emotions


def format_bullet_list(items: List[str], symbol: str = "•") -> str:
    """格式化为列表"""
    return "\n".join([f"{symbol} {item}" for item in items])


def clean_text(text: str) -> str:
    """清理文本（去除多余空格、换行等）"""
    # 去除多余空格
    text = re.sub(r'\s+', ' ', text)
    # 去除首尾空格
    text = text.strip()
    return text
