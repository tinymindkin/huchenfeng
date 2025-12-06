import sqlite3
import json
from pathlib import Path
from dotenv import load_dotenv
from llm.google import invoke_llm
from parse import parse
from typing import Optional
import asyncio
import logging
import time
from prompt.prompt import build_custom_prompt
logging.basicConfig(
    filename='generate_answer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
DB_PATH = 'dataset/database/raw_dialogues.db'
CONCURRENCY_LIMIT = 200  # 并发限制
BATCH_LIMIT = 1000
batch_size = 40
semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

class singleQuestion(dict):
    train_id: int
    answer: str
    question_list: list[str]
    model_version: str



async def generate_question(answer) -> tuple[list[str], str] | None:
    """生成问题：调用 LLM 并解析响应"""
    prompt = build_custom_prompt(answer,"generate_question.md")
    llm_response = await invoke_llm(prompt)
    if llm_response is None:
        return None
    model_version = llm_response['model_version']
    question_json_str = parse(llm_response['content'])
    if question_json_str is None:
        logging.warning(f"解析 LLM 响应失败，answer: {answer[:50]}...")
        return None
    return question_json_str, model_version


async def process_single_answer(answer: str, train_id: int) -> singleQuestion | None:
    """处理单个 answer，返回结果字典用于后续数据库写入"""
    async with semaphore:
        result = await generate_question(answer)
        if result is None:
            return None
        question_list, model_version = result
        if not isinstance(question_list, list):
            logging.warning(f"question_list 不是列表格式，id={train_id}")
            return None
        return singleQuestion({
            'train_id': train_id,
            'answer': answer,
            'question_list': question_list,
            'model_version': model_version
        })


async def main():
    """轮询 train_dialogues 表，生成问题并插入 question_answer_table"""
    conn = sqlite3.connect(DB_PATH)
    read_cursor = conn.cursor()
    write_cursor = conn.cursor()
    
    try:
        # 读取 status=1 且 processed_data 不为空的记录
        read_cursor.execute('''
            SELECT id, processed_data FROM train_dialogues 
            WHERE status = 1 AND processed_data IS NOT NULL
            ORDER BY id
        ''')
        
        batch_num = 0
        while True and batch_num < BATCH_LIMIT:  
            start_time = time.time()
            train_items = read_cursor.fetchmany(batch_size)
            if not train_items:
                logging.info("没有更多数据需要处理")
                break
            batch_num += 1
            logging.info(f"正在处理第 {batch_num} 批，数量={len(train_items)}")
            
            # 收集本批次所有需要处理的任务
            tasks = []
            for train_id, processed_data in train_items:
                # 提取answer_list
                try:
                    answer_list = json.loads(processed_data)
                except json.JSONDecodeError as e:
                    logging.warning(f"解析 processed_data 失败，id={train_id} : {e}")
                    logging.warning(f"processed_data: {processed_data}")
                    continue
                if not isinstance(answer_list, list):
                    logging.warning(f"processed_data 不是列表格式，id={train_id}")
                    continue

                # 为每个 answer 创建并发任务
                for answer in answer_list:
                    tasks.append(process_single_answer(answer, train_id))
            
            # 并发执行所有任务
            logging.info(f"第 {batch_num} 批共 {len(tasks)} 个任务开始并发执行")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 顺序写入数据库（避免并发写入导致数据错乱）
            for result in results:
                if isinstance(result, Exception):
                    logging.error(f"任务执行异常: {result}")
                    continue
                if result is None:
                    continue
                
                train_id = result['train_id']
                answer = result['answer']
                question_list = result['question_list']
                model_version = result['model_version']
                
                # 插入每个问题
                for question in question_list:
                    write_cursor.execute('''
                        INSERT INTO question_answer_table 
                        (answer_id, answer, question, model_version, status)
                        VALUES (?, ?, ?, ?, 1)
                    ''', (train_id, answer, question, model_version))
                    write_cursor.execute('''
                    UPDATE train_dialogues 
                    SET status = 3 
                    WHERE id = ?
                ''', (train_id,))
                
                logging.info(f"已处理 answer，train_id={train_id}，问题数量={len(question_list)}")
            
            # 每批次提交一次
            conn.commit()
            end_time = time.time()
            logging.info(f"第 {batch_num} 批已提交，耗时: {end_time - start_time:.2f}秒")
            time.sleep(5)
        logging.info(f"总共处理了 {batch_num} 批数据！")   
    except Exception as e:
        conn.rollback()
        logging.error(f"错误: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # async def test_main():
    #     answer_1 = '''学员？你早说嘛，飞行学员嘛，对不对嘛？以后跟航空公司签订合同啦？对啊，哎呀，你这些废话。他是什么？我给他讲一下，他是飞行学员，之后已经和航空公司签了卖身契了，比如说和什么航空，就是大的航空公司开飞机的，以后那肯定给你签证，他怕你跑。'''
    #     answer_2 = '''说实话我会去，为什么？我来讲一下这个目睹中学，它的氛围是非常宽松的。虽然我上的是国际部，但普通高中那边我也有朋友，氛围很宽松，就是跟类似于衡水中学这种学校的模式完全不一样。在这么宽松的一个环境下，升学率还这么高，我觉得是很了不起的，非常了不起。然后，就让我想起了有一些高中学生，看一眼窗外都得请家长，拿安检设备去学生宿舍看学生带没带手机，毫不尊重学生，这就是差距。虽然我个人来讲，我在目睹中学绝对不是一个优秀的学生，就是一个差生，但是我很感恩这个学校给我带来的时光，没有禁锢我。这相比较而言，我还是比较感恩的。有一些高中我是受不了的，看一眼窗外找家长，宿舍里面这不能带那不能带，各种严苛的死规矩，比如早上跑步前面跟后面挨得特别近，早上跑步还得拿个书边背边跑，这种环境下，我说实话我是真受不了。还有，一个月只能回家一回。目睹中学在我当年上学的时候每周都放假。我如果没记错的话，普通高中是放假一天，甚至可以走读的，很多人走读。我记不大清了，学生很自由，学校后门拿外卖随便拿，学校是很放得开学生的，所以我很喜欢，这就是江苏教育的不同吧。'''
    #     answer_3 = '''这个我确实不太清楚，这个不知道啊，你讲一讲吧，讲一讲了说不定对吧？我这个觉得有趣，我就是给你上个舰长。'''
    #     results = await asyncio.gather(
    #         generate_question(answer_1), 
    #         generate_question(answer_2), 
    #         generate_question(answer_3)
    #     )
    #     print("Results:", results)
    # asyncio.run(test_main())

    asyncio.run(main())

