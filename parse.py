from llm_output_parser import parse_json
import json
from typing import Optional
import logging
logger = logging.getLogger(__name__)

def is_valid_list(data:list) -> bool:
    return type(data) == list and len(data) > 0 and data[0] != ''

def is_valid_dict(data:dict) -> bool:
    return isinstance(data, dict) and len(data) == 1


def parse(text) -> Optional[list]:
    try:
        data = parse_json(text)
    except ValueError:
        print("解析 JSON 失败: " ,text)
        logger.error("解析 JSON 失败: %s", text)
        return None
    if is_valid_list(data):

        return json.dumps(data)
    elif is_valid_dict(data):
        first_value = next(iter(data.values()))
        if is_valid_list(first_value):
            return json.dumps(first_value)
        else:
            print("解析 JSON 失败: " ,text)
            logger.error("解析 JSON 失败: %s", text) 
            return None
    else:
        return None
if __name__ == "__main__":
        # Parse JSON from an LLM response
    llm_response = """
    ent': '```json\n[\n    "聊呗，你老管弹幕干嘛？弹幕都是一群很可爱的笔友们在开玩笑，网络世界不就是这样吗？我相信我从你的面相上来看，也是个经历过大风大浪的人，怎么这两把刷子就把你给唬住了呢？是不是？你是螺丝数码是码拉出来溜溜是吧？也是在社会上摸爬滚打这么多年了是吧？我们重新开始好吗？好不好？我重新问，你重新答，就像一切没有发生过一样，OK。"\n]\n```', 'token_
    """

    llm_response_1 = """
    这个呀
    ```json
    {
        "xixxi": ["xxx","xxx","xxxx"]`
    }
    ```
    """

    llm_response_2 = """
    这个呀
    ```json
    {
        "xixxi": ["xxx","xxx","xxxx"],
        "xixx2i" : false
    }
    ```
    """
    print(parse(llm_response_2))