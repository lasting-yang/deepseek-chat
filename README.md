# DeepSeek Chat

一个使用 Flask 和 Vue.js 构建的 AI 聊天应用，支持与 DeepSeek API 进行交互。

## 特性

- 创建多个对话
- 支持系统角色设置
- 流式聊天响应
- 思考过程显示
- 消息复制和删除
- 对话重命名和删除
- 自动保存聊天历史

## 快速启动

一行命令启动应用（自动构建前端并启动服务）:

```bash
# 运行启动脚本
python run.py
```

这个脚本会自动检查并构建前端，然后启动后端服务，使应用可通过 http://localhost:5000 访问。

## 手动部署

如果需要手动部署，可以按以下步骤操作:

```bash
# 1. 运行构建脚本，编译前端并集成到后端
python build.py

# 2. 进入后端目录
cd backend

# 3. 安装后端依赖
pip install -r requirements.txt

# 4. 配置环境变量（需要在 .env 文件中设置 DEEPSEEK_API_KEY 和 DEEPSEEK_BASE_URL）

# 5. 启动应用
python app.py
```

完成上述步骤后，在浏览器访问 http://localhost:5000 即可使用应用。

## 开发模式

如果需要分别运行前端和后端进行开发:

### 后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 配置

在 `backend/.env` 文件中配置必要的环境变量:

```
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-reasoner
``` 