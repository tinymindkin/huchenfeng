import sqlite3
import json
import logging
import os

# 获取脚本所在目录的父目录（项目根目录）
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(ROOT_DIR, "dataset/database/raw_dialogues.db")
SFT_PATH = os.path.join(ROOT_DIR, "question_answer.jsonl")



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_dataset():
    """从 question_answer_table 读取数据，过滤后生成 JSONL 文件"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, question, answer FROM question_answer_table
            WHERE LENGTH(question) > 2 AND status = 1
        ''')
        
        count = 0
        with open(SFT_PATH, 'w', encoding='utf-8') as f:
            for row in cursor:
                _, question, answer = row
                data = {
                    "messages": [
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": answer}
                    ]
                }
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
                count += 1
                # 测试
                # if count >= 10:  
                #     break
        
        logging.info(f"成功生成 {count} 条数据到 {SFT_PATH}")
        
    except Exception as e:
        logging.error(f"错误: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    generate_dataset()