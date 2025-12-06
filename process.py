import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import sqlite3
import asyncio
from parse import parse
from llm.google import invoke_llm
from prompt.prompt import build_prompt
from typing import Optional
import time
import pymysql
from dotenv import load_dotenv
load_dotenv()
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='process.log',
    format='%(asctime)s - %(filename)s-%(funcName)s-%(message)s',
    level=logging.INFO
)
logger.setLevel(logging.INFO)



async def generate_processed_data(huchenfeng) -> Optional[tuple[str, str]]:
    """生成处理后的数据：调用 LLM 并解析响应"""
    prompt = build_prompt(huchenfeng)
    llm_response = await invoke_llm(prompt)
    if llm_response is None:
        return None
    
    model_version = llm_response['model_version']
    json_str = parse(llm_response['content'])
    return (json_str, model_version)


async def process_train_dialogues():
    """批量处理训练数据：读取 train_dialogues，调用 LLM，更新数据库"""
    conn_local = sqlite3.connect("dataset/database/raw_dialogues.db") 
    # conn_local = pymysql.connect(
    #     host=os.getenv("MYSQL_HOST"),
    #     user=os.getenv("MYSQL_USER"),
    #     password=os.getenv("MYSQL_PASSWORD"),
    #     database="raw_dialogues",
    #     charset="utf8mb4",
    #     cursorclass=pymysql.cursors.DictCursor
    # )  
    try:
        conn_read = conn_local.cursor()
        conn_write = conn_local.cursor()

        conn_read.execute("SELECT id, huchenfeng, status FROM train_dialogues")
        rows_count = 0
        
        while True and rows_count < 10000:
            # 计时开始
            start_time = time.time()
            rows = conn_read.fetchmany(50)
            if not rows:
                break
            
            valid_rows = [row for row in rows if row[2] == 0]
            print(f"处理的有效id是:{[row[0] for row in valid_rows]}")
            logger.info(f"处理的有效id是:{[row[0] for row in valid_rows]}")
            if not valid_rows:
                continue
            
            results = await asyncio.gather(*(generate_processed_data(row[1]) for row in valid_rows))
            
            if len(results) == len(valid_rows):
                for i, result in enumerate(results):
                    if result is not None:
                        conn_write.execute(
                            "UPDATE train_dialogues SET processed_data = ?, model_version = ?, status = 1, processed_at = datetime('now') WHERE id = ?",
                            (result[0], result[1], valid_rows[i][0])
                        )
                        conn_local.commit()
                        rows_count += 1
                        logger.info(f"处理完成 ID: {valid_rows[i][0]}")
            # 计时结束
            end_time = time.time()
            logger.info(f"处理 {len(valid_rows)} 条记录耗时: {end_time - start_time:.2f} 秒")
            print(f"处理 {len(valid_rows)} 条记录耗时: {end_time - start_time:.2f} 秒")
        
        logger.info(f"[执行历史标记]Total rows count: {rows_count}")
    
    except Exception as e:
        logger.error(f"批量处理失败: {e}")
        raise
    finally:
        conn_local.close()
        logger.info("数据库连接已关闭")


if __name__ == "__main__":
    logger.info("开始批量处理训练数据")
    asyncio.run(process_train_dialogues())
    logger.info("批量处理完成")









