from flask import Flask, request, jsonify, Response, stream_with_context, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import duckdb
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import uuid

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app)

# 初始化数据库
def init_db():
    conn = duckdb.connect('chats.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP,
            title VARCHAR,
            system_content TEXT,
            is_deleted BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id VARCHAR PRIMARY KEY,
            conversation_id VARCHAR,
            role VARCHAR,
            content TEXT,
            reasoning_content TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    ''')
    conn.close()

init_db()

# 添加根路由
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# OpenAI客户端初始化
client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url=os.getenv('DEEPSEEK_BASE_URL')
)

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    conn = duckdb.connect('chats.db')
    conversations = conn.execute('''
        SELECT id, created_at, title, system_content 
        FROM conversations 
        WHERE is_deleted = FALSE
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    return jsonify([{
        'id': conv[0],
        'created_at': conv[1].isoformat(),
        'title': conv[2],
        'system_content': conv[3]
    } for conv in conversations])

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    title = request.json.get('title', '新对话')
    system_content = request.json.get('system_content', '你是一个有帮助的AI助手。')
    conversation_id = str(uuid.uuid4())
    
    conn = duckdb.connect('chats.db')
    result = conn.execute('''
        INSERT INTO conversations (id, created_at, title, system_content, is_deleted)
        VALUES (?, ?, ?, ?, FALSE)
        RETURNING id, created_at, title, system_content
    ''', (conversation_id, datetime.now(), title, system_content)).fetchone()
    conn.close()
    
    return jsonify({
        'id': result[0],
        'created_at': result[1].isoformat(),
        'title': result[2],
        'system_content': result[3]
    })

@app.route('/api/conversations/<conversation_id>/messages', methods=['GET'])
def get_messages(conversation_id):
    # 检查是否是流式请求
    if request.args.get('message') is not None:
        return stream_message(conversation_id, request.args.get('message'))
        
    # 普通的消息获取请求
    conn = duckdb.connect('chats.db')
    messages = conn.execute('''
        SELECT * FROM messages 
        WHERE conversation_id = ? 
        ORDER BY created_at
    ''', (conversation_id,)).fetchall()
    conn.close()
    return jsonify([{
        'id': msg[0],
        'conversation_id': msg[1],
        'role': msg[2],
        'content': msg[3],
        'reasoning_content': msg[4],
        'created_at': msg[5].isoformat()
    } for msg in messages])

@app.route('/api/conversations/<conversation_id>/messages', methods=['POST'])
def create_message(conversation_id):
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400

    conn = duckdb.connect('chats.db')
    save_message(conn, conversation_id, 'user', user_message)
    conn.close()
    return jsonify({'status': 'success'})

def save_message(conn, conversation_id, role, content, reasoning_content=None):
    message_id = str(uuid.uuid4())
    conn.execute('''
        INSERT INTO messages (id, conversation_id, role, content, reasoning_content, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (message_id, conversation_id, role, content, reasoning_content, datetime.now()))

def stream_message(conversation_id, user_message):
    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400

    conn = duckdb.connect('chats.db')
    
    # 获取系统角色设置
    conversation = conn.execute('''
        SELECT system_content FROM conversations 
        WHERE id = ? AND is_deleted = FALSE
    ''', (conversation_id,)).fetchone()
    
    if not conversation:
        conn.close()
        return jsonify({'error': '对话不存在'}), 404
    
    system_content = conversation[0]
    
    # 保存用户消息
    save_message(conn, conversation_id, 'user', user_message)
    
    # 获取对话历史
    messages = conn.execute('''
        SELECT role, content FROM messages 
        WHERE conversation_id = ? 
        ORDER BY created_at
    ''', (conversation_id,)).fetchall()
    
    # 构造API请求消息
    api_messages = [{"role": "system", "content": system_content}] + \
                  [{"role": msg[0], "content": msg[1]} for msg in messages]
    print(api_messages)
    def generate():
        full_response = ""
        full_reasoning = ""
        try:
            # 发送初始化事件
            yield 'data: {"type": "start", "content": ""}\n\n'
            
            # 调用API获取流式回复
            response = client.chat.completions.create(
                model=os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner'),
                messages=api_messages,
                stream=True
            )
            
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'reasoning_content'):
                    if chunk.choices[0].delta.reasoning_content:
                        content = chunk.choices[0].delta.reasoning_content
                        full_reasoning += content
                        yield f'data: {json.dumps({"type": "reasoning", "content": content})}\n\n'
                
                if hasattr(chunk.choices[0].delta, 'content'):
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield f'data: {json.dumps({"type": "content", "content": content})}\n\n'
            
            # 保存完整的回复消息
            save_message(conn, conversation_id, 'assistant', full_response, full_reasoning)
            conn.close()
            
            # 发送完成标记
            yield f'data: {json.dumps({"type": "done", "done": True})}\n\n'
            
        except Exception as e:
            error_msg = str(e)
            yield f'data: {json.dumps({"error": error_msg})}\n\n'
            conn.close()

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Content-Type': 'text/event-stream',
            'Access-Control-Allow-Origin': '*'
        }
    )

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    conn = duckdb.connect('chats.db')
    try:
        # 软删除对话
        conn.execute('''
            UPDATE conversations 
            SET is_deleted = TRUE 
            WHERE id = ?
        ''', (conversation_id,))
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['PUT'])
def update_conversation(conversation_id):
    try:
        title = request.json.get('title')
        system_content = request.json.get('system_content')
        
        if not title and not system_content:
            return jsonify({'error': '标题和系统角色设置不能同时为空'}), 400
            
        conn = duckdb.connect('chats.db')
        try:
            # 开始事务
            conn.execute('BEGIN TRANSACTION')
            
            # 先检查对话是否存在且未删除
            conversation = conn.execute('''
                SELECT id, created_at, title, system_content
                FROM conversations 
                WHERE id = ? AND is_deleted = FALSE
            ''', (conversation_id,)).fetchone()
            
            if not conversation:
                conn.execute('ROLLBACK')
                conn.close()
                return jsonify({'error': '对话不存在'}), 404
            
            # 构建更新语句
            update_fields = []
            params = []
            if title is not None:
                update_fields.append('title = ?')
                params.append(title.strip())
            if system_content is not None:
                update_fields.append('system_content = ?')
                params.append(system_content.strip())
            
            if not update_fields:
                conn.execute('ROLLBACK')
                conn.close()
                return jsonify({'error': '没有需要更新的字段'}), 400
                
            params.append(conversation_id)
            
            # 更新对话
            conn.execute(f'''
                UPDATE conversations 
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', params)
            
            # 获取更新后的数据
            updated = conn.execute('''
                SELECT id, created_at, title, system_content
                FROM conversations 
                WHERE id = ?
            ''', (conversation_id,)).fetchone()
            
            # 提交事务
            conn.execute('COMMIT')
            
            response_data = {
                'id': updated[0],
                'created_at': updated[1].isoformat() if updated[1] else None,
                'title': updated[2],
                'system_content': updated[3]
            }
            
            conn.close()
            return jsonify(response_data)
            
        except Exception as db_error:
            print(f"数据库错误: {str(db_error)}")
            try:
                conn.execute('ROLLBACK')
            except:
                pass
            conn.close()
            return jsonify({'error': f'数据库操作失败: {str(db_error)}'}), 500
            
    except Exception as e:
        print(f"服务器错误: {str(e)}")
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/conversations/<conversation_id>/messages/<message_id>', methods=['DELETE'])
def delete_message(conversation_id, message_id):
    conn = duckdb.connect('chats.db')
    try:
        # 检查消息是否存在且属于该对话
        message = conn.execute('''
            SELECT id FROM messages 
            WHERE id = ? AND conversation_id = ?
        ''', (message_id, conversation_id)).fetchone()
        
        if not message:
            conn.close()
            return jsonify({'error': '消息不存在或不属于该对话'}), 404
        
        # 删除消息
        conn.execute('''
            DELETE FROM messages 
            WHERE id = ? AND conversation_id = ?
        ''', (message_id, conversation_id))
        
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 