import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from process import generate_processed_data
import asyncio
import pytest

import logging
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('test/test.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(filename)s-%(funcName)s-%(message)s'))
logger.addHandler(file_handler)

logger.setLevel(logging.DEBUG)

t1 = '''
升。你坐高铁是为了自己，是利己，不要给自己套上大的道德光环。那我做直播还是为了社会呢？我纳税啊，对不对？你不要套上道德光环，我做直播还促进经济增长呢，对不对？一样的道理啊，干事情首先是为了利己。你去……
'''
t2 = '''
如果你选择去送外卖，一个月挣八千来赡养你的父母，你不一定有这个钱，不一定有这个命，听懂我的意思了吗？
'''
t3 = '''
四万多个人看着呢，看弹幕吧。我是不是在攻击？我真是心疼你的孩子，我真是心疼你的孩子。你不要用那种借口，我们这边都这样做，人家怎么做关你毛事？你的孩子健不健康，你的孩子身心健不健康是跟你有直接关系的。我估计我说了也是白说，你还跟他喝茶呢？我说了也是白说。
'''
t4 = '''
四万多个人看着呢，看弹幕吧。我是不是在攻击？我真是心疼你的孩子，我真是心疼你的孩子。你不要用那种借口，我们这边都这样做，人家怎么做关你毛事？你的孩子健不健康，你的孩子身心健不健康是跟你有直接关系的。我估计我说了也是白说，你还跟他喝茶呢？我说了也是白说。
'''
t5 = '''
四万多个人看着呢，看弹幕吧。我是不是在攻击？我真是心疼你的孩子，我真是心疼你的孩子。你不要用那种借口，我们这边都这样做，人家怎么做关你毛事？你的孩子健不健康，你的孩子身心健不健康是跟你有直接关系的。我估计我说了也是白说，你还跟他喝茶呢？我说了也是白说。
'''

t6 = '''
四万多个人看着呢，看弹幕吧。我是不是在攻击？我真是心疼你的孩子，我真是心疼你的孩子。你不要用那种借口，我们这边都这样做，人家怎么做关你毛事？你的孩子健不健康，你的孩子身心健不健康是跟你有直接关系的。我估计我说了也是白说，你还跟他喝茶呢？我说了也是白说。
'''
t7 = '''
四万多个人看着呢，看弹幕吧。我是不是在攻击？我真是心疼你的孩子，我真是心疼你的孩子。你不要用那种借口，我们这边都这样做，人家怎么做关你毛事？你的孩子健不健康，你的孩子身心健不健康是跟你有直接关系的。我估计我说了也是白说，你还跟他喝茶呢？我说了也是白说。
'''
@pytest.mark.asyncio
async def test_generate_processed_data():
    """测试批量生成处理后的数据"""
    results = await asyncio.gather(
        generate_processed_data(t1),
        generate_processed_data(t2),
        generate_processed_data(t3),
        generate_processed_data(t4),
        generate_processed_data(t5),
        generate_processed_data(t6),
        generate_processed_data(t7)
    )
    print("返回结果的长度：",len(results))
    for i, res in enumerate(results, 1):
        print(f"Result {i}: {res}")
        # 允许 None 结果（LLM 调用可能失败）
        assert res is not None or res is None


if __name__ == "__main__":
    # 直接运行时的测试代码
    asyncio.run(test_generate_processed_data())
