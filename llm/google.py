from google import genai
from google.genai import types
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from .views import LLMResponse
import logging
# Load .env file if it exists, otherwise use environment variables
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
logger = logging.getLogger(__name__)

client = genai.Client(api_key = os.getenv("GOOGLE_API_KEY"))

async def invoke_llm(text, model="gemini-2.5-flash",try_count=10):
    try:
        count = 0
        response = None
        while count < try_count:
            try:
                response = await client.aio.models.generate_content(
                    model=model,
                    contents=text,
                    config=types.GenerateContentConfig(temperature=0.7),
                )
                break
            except Exception as e:
                count += 1
                if count >= try_count:
                    logger.error(f"重试{try_count}次后失败: {e}")
                    return None
                await asyncio.sleep(5)
        
        # Extract content from the response
        if response:
            content = response.candidates[0].content.parts[0].text if response.candidates else ""
        
            # Extract token usage information
            token_usage =  {
                "prompt_token_count": response.usage_metadata.prompt_token_count,
                "candidates_token_count": response.usage_metadata.candidates_token_count,
                "total_token_count": response.usage_metadata.total_token_count,
            }
            # Assemble the response using the defined data structure
            return LLMResponse(content=content, token_usage=token_usage, model_version=model)
        return response
    except Exception as e:
        logger.error(f"调用LLM失败: {e}")
        return None
if __name__ == "__main__":
    import sys
    # 嘛，你这合一学说实话你也不挣钱呢，你得找挣钱呢，因为这市场太小了，没办法，这就是你的命运，选择大于努力，记住了。
    # 聊呗，你老管弹幕干嘛？弹幕都是一群很可爱的笔友们在开玩笑，网络世界不就是这样吗？我相信我从你的面相上来看，也是个经历过大风大浪的人，怎么这两把刷子就把你给唬住了呢？是不是？你是螺丝数码是码拉出来溜溜是吧？也是在社会上摸爬滚打这么多年了是吧？我们重新开始好吗？好不好？好不好？我重新问，你重新答，就像一切没有发生过一样，OK。
    # 我今天我说我喜欢吃苏州面，然后我说我个人我不喜欢吃兰州拉面，这怎么？我怎么还就这有什么问题吗？每个人口感口味它是不一样的，对不对？这怎么我说这个话也有毛病了？我确实喜欢吃苏州面。就是对于我来讲就是更加的怎么讲呢？就是这个酥酥面就吃起来很就是口感很丰富，就更鲜，会非常鲜。就我说这个都不行了？我说了就仅代表个人观点，个人的口味无关乎地域啊，怎么老有人拿地域说这个事啊？我一直在讲只是我个人，我个人我喜欢粤菜排第一，江浙菜第二，其他的往后稍一稍，这怎么？这有毛病啊？这这这这这也有毛病啊？
    # 这个叫忧郁的说，户子我爱你，哎呀，我也爱你，感谢忧郁啊，我也爱你，我也我也爱你啊。好，户子你看茶馆吗？推荐给你，我看啊，茶馆我都看完了，你看过那个茶馆吗？
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from prompt.prompt import build_prompt
    
    result = asyncio.run(invoke_llm(build_prompt('''这个叫忧郁的说，户子我爱你，哎呀，我也爱你，感谢忧郁啊，我也爱你，我也我也爱你啊。好，户子你看茶馆吗？推荐给你，我看啊，茶馆我都看完了，你看过那个茶馆吗？''')))
    print(result)
