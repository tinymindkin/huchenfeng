"""
数据处理和 LLM 调用工具函数。

提供文本清洗、分段、以及通过 LLM 提取特定说话人内容等功能。
"""
import os
from typing import List

import google.generativeai as genai

def build_filter_prompt(text: str, speaker_name: str = "户晨风") -> str:
    """
    构造过滤提示，用于提取特定说话人的发言。
    
    Args:
        text: 多说话人转写文本
        speaker_name: 要提取的说话人姓名
    
    Returns:
        构造好的提示词
    """
    return (
        f"阅读下面的多说话人中文转写，只保留说话人\"{speaker_name}\"的发言，保持原话顺序，"
        "删除其他人的内容，不做任何总结或改写，直接输出拼接后的文本。"
        "\n\n原始转写：\n"
        f"{text}\n\n仅输出过滤结果："
    )


def generate_sample_conversation(speaker_name: str = "户晨风") -> str:
    """
    使用 Google Gemini API 生成一段包含指定说话人的多人对话示例。
    
    用于测试和演示目的，便于验证处理链路。
    
    Args:
        speaker_name: 要包含的说话人姓名
    
    Returns:
        生成的对话文本
    """
    try:
        # 1. 从环境变量中获取 API Key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY 环境变量未设置")

        # 2. 配置 SDK
        genai.configure(api_key=api_key)

        # 3. 创建模型实例
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 4. 构造 Prompt
        prompt = (
            f"生成一段包含三位说话人的简短中文对话（30-60字），其中一位名叫\"{speaker_name}\"。"
            "格式不限，保证能区分说话人。"
        )
        
        # 5. 调用 API
        response = model.generate_content(prompt)

        return response.text
        
    except Exception as e:
        print(f"调用 Google Gemini API 失败: {e}")
        # 在 API 失败时返回一个固定的示例文本，确保程序不会中断
        return f"{speaker_name}：大家好，我是户晨风。\\n小明：你好！\\n小红：欢迎欢迎！"


def extract_speaker_content(text: str, speaker_name: str = "户晨风") -> List[str]:
    """
    使用 Google Gemini API 提取特定说话人的发言内容。
    
    利用 LLM 过滤出指定说话人的发言。
    如果结果包含多个自然段落，会自动分割成列表。
    
    Args:
        text: 原始多说话人文本
        speaker_name: 要提取的说话人姓名
    
    Returns:
        提取出的文本片段列表（可能包含多个段落）
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY 环境变量未设置")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = build_filter_prompt(text, speaker_name)
        response = model.generate_content(prompt)

        # Enhanced error handling for Gemini API responses
        if response.candidates:
            if response.candidates[0].content.parts:
                result = response.text
            else:
                print(f"[Gemini API Error] No parts in candidate content. Finish reason: {response.candidates[0].finish_reason}")
                print(f"[Gemini API Error] Safety ratings: {response.candidates[0].safety_ratings}")
                result = ""
        else:
            print(f"[Gemini API Error] No candidates found. Prompt feedback: {response.prompt_feedback}")
            result = ""
        
        # 尝试按段落分割（用两个换行符分隔）
        # 如果有多个自然段落则拆分，否则返回单个结果
        paragraphs = [p.strip() for p in result.split("\n\n") if p.strip()]
        return paragraphs if len(paragraphs) > 1 else [result.strip()]
        
    except Exception as e:
        print(f"调用 Google Gemini API 失败: {e}")
        # 在 API 失败时返回一个固定的示例文本，确保程序不会中断
        return [f"（未能从文本中提取 {speaker_name} 的发言）"]


# TODO:规整化 + 去噪 + 分段
def denoise_and_split_text(text: str) -> List[str]:
    """
    对文本进行去噪和分段处理。
    
    Args:
        text: 待处理的文本
    
    Returns:
        处理后的文本片段列表
    """
    pass
