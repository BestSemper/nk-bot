from sentence_transformers import SentenceTransformer, util
import sqlite3
from datetime import datetime

db_path = 'db/chat_history.db'
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print('Database created')

def insert_chat_history(member_id, role, content):
    if content == '':
        content = 'No content'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    created_at = datetime.now().strftime('%Y%m%d')
    cursor.execute('''
        INSERT INTO chat_history (member_id, created_at, role, content)
        VALUES (?, ?, ?, ?)
    ''', (member_id, created_at, role, content))
    conn.commit()
    conn.close()
    print(f'Chat history inserted: {member_id}, {role}, {content}')

def get_chat_history(member_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT member_id, created_at, role, content
        FROM chat_history
        WHERE member_id = ?
        ORDER BY created_at
    ''', (member_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_today_chat_history(member_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    created_at = datetime.now().strftime('%Y%m%d')
    cursor.execute('''
        SELECT member_id, created_at, role, content
        FROM chat_history
        WHERE member_id = ? AND created_at = ?
        ORDER BY created_at
    ''', (member_id, created_at))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_related_chat_history(member_id, sentence, k=5):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT content
        FROM chat_history
        WHERE member_id = ?
    ''', (member_id,))
    rows = cursor.fetchall()
    conn.close()
    
    chat_history = [row[0] for row in rows]
    
    sentence_embedding = model.encode(sentence, convert_to_tensor=True)
    chat_history_embeddings = model.encode(chat_history, convert_to_tensor=True)
    
    cos_scores = util.pytorch_cos_sim(sentence_embedding, chat_history_embeddings)[0]
    
    top_k_indices = cos_scores.topk(min(k, len(rows))).indices
    
    related_chat_history = [chat_history[idx] for idx in top_k_indices]
    
    return related_chat_history
    
# Test
# create_db()

# insert_chat_history('user123', 'user', 'Hello, how can I help you?')
# insert_chat_history('user123', 'ai', 'I need assistance with my account.')

# history = get_chat_history('user123')
# for record in history:
#     print(record)