import sqlite3
from datetime import datetime
import os


def create_train_dialogues_table(db_path='database/raw_dialogues.db'):
    """
    生成用于训练的数据库
    1. 读取 filtered_dialogues 表(id,wangyou,huchenfeng,source) 
    2. 创建一个新的表 train_dialogues(id,huchenfeng,processed_data,status,source,created_at,processed_at)
    """
    
    # Check if database exists at the expected path
    if not os.path.exists(db_path):
        # Try alternative path used in notebook
        if os.path.exists('../database/raw_dialogues.db'):
            db_path = '../database/raw_dialogues.db'
        else:
            raise FileNotFoundError(f"Database not found at {db_path}")
    
    print(f"Using database at: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor_write = conn.cursor()
    cursor_read = conn.cursor()
    
    try:
        # Drop and create the train_dialogues table
        cursor_write.execute('DROP TABLE IF EXISTS train_dialogues')
        
        cursor_write.execute('''
        CREATE TABLE train_dialogues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            huchenfeng VARCHAR NOT NULL,
            processed_data TEXT,
            status INTEGER DEFAULT 0,
            source TEXT(100),
            created_at TIMESTAMP NOT NULL,
            processed_at TIMESTAMP
        )
        ''')
        
        print("Created train_dialogues table")
        
        # Get current timestamp
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Read from filtered_dialogues
        cursor_read.execute('SELECT id, huchenfeng, source FROM filtered_dialogues')
        
        inserted_count = 0
        batch_size = 1000
        
        while True:
            rows = cursor_read.fetchmany(batch_size)
            if not rows:
                break
            
            # Prepare data for insertion
            data_to_insert = [
                (row[1], None, 0, row[2], created_at, None) 
                for row in rows
            ]
            
            # Insert into train_dialogues
            cursor_write.executemany('''
            INSERT INTO train_dialogues (huchenfeng, processed_data, status, source, created_at, processed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', data_to_insert)
            
            inserted_count += len(data_to_insert)
            print(f"已插入 {inserted_count} 条记录...")
        
        # Commit changes
        conn.commit()
        
        print(f"\n完成！共插入 {inserted_count} 条记录到 train_dialogues 表")
        
        # Verify the data
        cursor_read.execute('SELECT COUNT(*) FROM train_dialogues')
        count = cursor_read.fetchone()[0]
        print(f"验证：train_dialogues 表中共有 {count} 条记录")
        
        # Show sample data
        cursor_read.execute('SELECT * FROM train_dialogues LIMIT 3')
        samples = cursor_read.fetchall()
        print("\n示例数据：")
        for sample in samples:
            print(f"  ID: {sample[0]}, 户晨风: {sample[1][:50]}..., 状态: {sample[3]}, 来源: {sample[4]}, 创建时间: {sample[5]}")
        
    except Exception as e:
        conn.rollback()
        print(f"错误: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    create_train_dialogues_table()
