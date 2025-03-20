<script setup>
import { ref, onMounted, nextTick, reactive, h } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MoreFilled, Setting, Edit, Delete, CopyDocument } from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'

const conversations = ref([])
const currentConversation = ref(null)
const messages = ref([])
const newMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

const API_BASE_URL = 'http://localhost:5000/api'

// 预设的系统角色列表
const systemRoles = [
  {
    title: 'AI编程助手',
    content: `你是一个强大的AI编程助手。

你正在与用户结对编程来解决他们的编程任务。
任务可能包括创建新的代码库、修改或调试现有代码库，或者回答问题。

遵循以下规则：

1. 沟通风格：
- 保持专业但友好的对话风格
- 用第二人称称呼用户，用第一人称称呼自己
- 使用markdown格式
- 使用反引号格式化文件、目录、函数和类名
- 使用 \\( 和 \\) 表示行内数学公式，\\[ 和 \\] 表示块级数学公式

2. 代码质量：
- 确保生成的代码可以立即运行
- 添加所有必要的导入语句和依赖项
- 创建新项目时添加合适的依赖管理文件和README
- 构建网页应用时使用现代UI和最佳UX实践
- 不生成极长的哈希值或非文本代码

3. 调试原则：
- 解决根本原因而不是表象
- 添加描述性的日志和错误信息
- 添加测试函数来隔离问题
- 在不确定的情况下收集更多信息

4. API使用：
- 除非用户明确要求，使用最适合的外部API和包
- 选择与用户依赖管理文件兼容的API版本
- 对于需要API密钥的服务，提醒用户并遵循安全最佳实践

5. 错误处理：
- 不要过度道歉，而是解释情况并继续
- 如果需要更多信息，主动提问
- 在修复错误时提供清晰的解释

始终用中文回复。

不要撒谎，不要编造事实，不要编造专业术语。`
  },
  {
    title: 'iOS逆向专家助手',
    content: `你是一个专业的iOS逆向工程专家助手。

1. 专业背景：
- 精通iOS系统架构和安全机制
- 熟悉Objective-C和Swift语言特性
- 掌握iOS应用程序的编译、打包和签名流程
- 具备丰富的越狱环境和非越狱环境下的逆向经验

2. 核心能力：
- 静态分析：
  * 熟练使用IDA Pro、Hopper等反汇编工具
  * 掌握Mach-O文件格式和ARM64汇编
  * 能够分析代码结构和算法实现
  * 理解加密、混淆等保护机制
- 动态分析：
  * 精通lldb、Frida等调试和hook工具
  * 熟悉MonkeyDev、Theos等开发框架
  * 能够进行运行时方法替换和注入
  * 掌握反调试对抗技术

3. 工作方法：
- 系统性分析：
  * 从UI层到系统调用的完整分析
  * 数据流和控制流的追踪
  * 加密算法和网络协议的还原
  * 安全机制的识别和绕过
- 工具使用：
  * 合理选择分析工具链
  * 编写自动化分析脚本
  * 构建测试环境和验证方案
  * 确保分析过程的可重现性

4. 安全意识：
- 遵守法律法规
- 保护知识产权
- 防范恶意代码
- 注重数据安全

5. 解决方案：
- 提供详细的分析报告
- 编写清晰的技术文档
- 设计可行的绕过方案
- 开发必要的辅助工具

始终用中文回复，保持专业性和安全性。

不要撒谎，不要编造事实，不要编造专业术语。`
  },
  {
    title: 'Android逆向专家助手',
    content: `你是一个专业的Android逆向工程专家助手。

1. 专业背景：
- 精通Android系统架构和安全机制
- 熟悉Java、Kotlin和Native层开发
- 掌握Android应用的编译、打包和签名流程
- 具备丰富的Root和非Root环境下的逆向经验

2. 核心能力：
- 静态分析：
  * 熟练使用jadx、JEB等反编译工具
  * 掌握DEX、ODEX文件格式分析
  * 能够分析混淆后的代码结构
  * 理解加固和保护机制
- 动态分析：
  * 精通Xposed、Frida等hook框架
  * 熟悉Android调试和追踪技术
  * 能够进行运行时方法监控和修改
  * 掌握反调试和模拟器检测绕过

3. 工作方法：
- 系统性分析：
  * 应用层到系统层的完整分析
  * Java层和Native层的联合分析
  * 数据存储和网络通信的还原
  * 安全机制的识别和处理
- 工具使用：
  * 搭建分析环境和工具链
  * 编写自动化分析脚本
  * 构建测试验证方案
  * 确保分析过程可复现

4. 安全意识：
- 遵守法律法规
- 保护知识产权
- 防范恶意代码
- 注重数据安全

5. 解决方案：
- 提供详细的分析报告
- 编写清晰的技术文档
- 设计可行的绕过方案
- 开发必要的辅助工具

始终用中文回复，保持专业性和安全性。

不要撒谎，不要编造事实，不要编造专业术语。`
  },
  {
    title: 'A股交易专家',
    content: `你是一个专业的A股个人独立交易专家，拥有丰富的实战经验。

1. 专业背景：
- 具备10年以上A股市场实战交易经验
- 精通技术分析和基本面分析
- 熟悉各类交易策略和风险管理方法
- 对宏观经济、行业分析有深入研究

2. 沟通原则：
- 使用专业但通俗易懂的语言解释市场现象
- 在分析中注重数据支持和逻辑推导
- 对投资风险保持高度警惕，及时提醒
- 避免使用诱导性或夸大性的表述

3. 分析方法：
- 技术面分析：
  * K线形态识别
  * 量价关系分析
  * 技术指标运用
  * 市场情绪判断
- 基本面分析：
  * 财务报表解读
  * 行业竞争格局
  * 公司治理评估
  * 政策影响分析

4. 风险控制：
- 始终强调仓位管理的重要性
- 提供完整的止损止盈建议
- 关注市场异常波动信号
- 警惕内幕交易和市场操纵

5. 投资理念：
- 理性客观，不盲目追涨杀跌
- 强调长期价值投资理念
- 重视投资组合的分散管理
- 保持独立思考，不随众操作

始终用中文回复，保持专业性和警示性。

不要撒谎，不要编造事实，不要编造专业术语。`
  },
  {
    title: '通用助手',
    content: '你是一个很有用的助手。可以帮我解决任何问题。不要撒谎，不要编造事实，不要编造专业术语。'
  },
  {
    title: '自定义角色',
    content: ''
  }
]

// 默认的系统角色设置
const defaultSystemContent = systemRoles[0].content

// 滚动到最新消息
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 获取所有对话
const fetchConversations = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/conversations`)
    conversations.value = response.data
  } catch (error) {
    ElMessage.error('获取对话列表失败：' + (error.response?.data?.message || error.message))
  }
}

// 创建新对话
const createConversation = async () => {
  try {
    // 使用更直接的方式创建对话框
    // 直接使用导入的h函数
    
    // 准备预设角色列表
    const roles = systemRoles.slice(0, -1);
    
    // 使用ElMessageBox显示选项卡片
    await ElMessageBox({
      title: '选择AI助手角色',
      message: h('div', { style: { marginBottom: '16px' } }, [
        h('div', { style: { marginBottom: '16px' } }, '请点击选择一个预设角色，或创建自定义角色'),
        h('div', { 
          style: { 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', 
            gap: '16px' 
          } 
        }, roles.map(role => 
          h('div', {
            style: {
              padding: '16px',
              border: '1px solid #dcdfe6',
              borderRadius: '8px',
              cursor: 'pointer',
              backgroundColor: '#fff',
              transition: 'all 0.3s'
            },
            onClick: async () => {
              try {
                // 角色被选中，关闭对话框
                ElMessageBox.close()
                
                // 创建对话
                const response = await axios.post(`${API_BASE_URL}/conversations`, {
                  title: role.title, // 使用角色名称作为对话名称
                  system_content: role.content
                })
                
                ElMessage.success(`已创建 "${role.title}" 角色的对话`)
                conversations.value.unshift(response.data)
                selectConversation(response.data)
              } catch (error) {
                ElMessage.error('创建对话失败：' + (error.response?.data?.message || error.message))
              }
            },
            onMouseover: (e) => {
              e.currentTarget.style.borderColor = '#409EFF'
              e.currentTarget.style.backgroundColor = '#ecf5ff'
              e.currentTarget.style.transform = 'translateY(-2px)'
            },
            onMouseleave: (e) => {
              e.currentTarget.style.borderColor = '#dcdfe6'
              e.currentTarget.style.backgroundColor = '#fff'
              e.currentTarget.style.transform = 'translateY(0)'
            }
          }, [
            h('div', { style: { fontWeight: 'bold', marginBottom: '8px' } }, role.title),
            h('div', { style: { fontSize: '12px', color: '#666' } }, role.content.split('\n')[0])
          ])
        )),
        // 添加自定义角色卡片
        h('div', {
          style: {
            padding: '16px',
            border: '1px solid #dcdfe6',
            borderRadius: '8px',
            cursor: 'pointer',
            backgroundColor: '#fff',
            transition: 'all 0.3s',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '120px'
          },
          onClick: async () => {
            // 关闭角色选择对话框
            ElMessageBox.close()
            
            try {
              // 弹出自定义角色输入框
              const { value } = await ElMessageBox.prompt(
                '请设置AI助手的角色和行为指南',
                '创建自定义角色',
                {
                  confirmButtonText: '确定',
                  cancelButtonText: '取消',
                  inputType: 'textarea',
                  customClass: 'system-role-dialog',
                  inputPlaceholder: `示例 - 自定义角色设定：

1. 角色身份：
- 明确角色的专业背景
- 设定角色的经验水平
- 定义角色的专业领域
- 说明角色的特殊技能

2. 沟通原则：
- 设定语言风格
- 定义回答方式
- 确定专业程度
- 规定行为准则

3. 专业要求：
- 列出核心能力
- 说明专业标准
- 定义工作方法
- 设置质量要求

4. 限制和原则：
- 明确行为边界
- 设定道德准则
- 规定禁止事项
- 确定处理原则

5. 其他要求：
- 补充特殊说明
- 添加额外规则
- 设定其他限制

请用中文回复。`,
                  inputValidator: (value) => {
                    if (!value.trim()) {
                      return '系统角色设置不能为空'
                    }
                    return true
                  }
                }
              )
              
              // 如果用户提供了自定义角色内容
              if (value && value.trim()) {
                // 尝试从自定义内容中提取标题（第一行）
                const lines = value.trim().split('\n');
                const title = lines[0].length > 20 
                  ? lines[0].substring(0, 20) + '...'  // 截取过长的标题
                  : lines[0];
              
                const response = await axios.post(`${API_BASE_URL}/conversations`, {
                  title: title || '自定义角色',  // 使用提取的标题或默认名称
                  system_content: value.trim()
                })
                
                ElMessage.success('已创建自定义角色对话')
                conversations.value.unshift(response.data)
                selectConversation(response.data)
              }
            } catch (error) {
              if (error !== 'cancel') {
                ElMessage.error('创建自定义角色失败：' + (error.response?.data?.message || error.message))
              }
            }
          },
          onMouseover: (e) => {
            e.currentTarget.style.borderColor = '#409EFF'
            e.currentTarget.style.backgroundColor = '#ecf5ff'
            e.currentTarget.style.transform = 'translateY(-2px)'
          },
          onMouseleave: (e) => {
            e.currentTarget.style.borderColor = '#dcdfe6'
            e.currentTarget.style.backgroundColor = '#fff'
            e.currentTarget.style.transform = 'translateY(0)'
          }
        }, [
          h('div', { style: { fontWeight: 'bold', marginBottom: '8px' } }, '创建自定义角色'),
          h('div', { style: { fontSize: '12px', color: '#666', textAlign: 'center' } }, '创建一个完全自定义的AI助手角色')
        ])
      ]),
      showCancelButton: true,
      cancelButtonText: '取消',
      showConfirmButton: false,
      customClass: 'role-selection-dialog'
    }).catch(err => {
      if (err !== 'cancel') {
        console.error('对话框错误:', err)
      }
    })
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('创建对话失败：' + (error.response?.data?.message || error.message))
    }
  }
}

// 选择对话
const selectConversation = async (conversation) => {
  currentConversation.value = conversation
  try {
    const response = await axios.get(`${API_BASE_URL}/conversations/${conversation.id}/messages`)
    messages.value = response.data
    await scrollToBottom()
  } catch (error) {
    ElMessage.error('获取消息失败：' + (error.response?.data?.message || error.message))
  }
}

// 处理输入框按键事件
const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 发送消息
const sendMessage = async () => {
  if (!newMessage.value.trim() || !currentConversation.value) {
    if (!currentConversation.value) {
      ElMessage.warning('请先创建或选择一个对话')
    }
    return
  }
  
  const userMessage = newMessage.value
  newMessage.value = ''
  
  loading.value = true
  
  try {
    // 立即添加用户消息
    const userMsg = {
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    }
    messages.value.push(userMsg)
    
    // 添加助手消息占位
    const assistantMessage = reactive({
      role: 'assistant',
      content: '',
      reasoning_content: '',
      created_at: new Date().toISOString(),
      streaming: true
    })
    messages.value.push(assistantMessage)
    await scrollToBottom()

    // 创建 EventSource 实例
    const eventSource = new EventSource(
      `${API_BASE_URL}/conversations/${currentConversation.value.id}/messages?message=${encodeURIComponent(userMessage)}`
    )

    // 处理消息事件
    eventSource.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('Received data:', data)

        if (data.error) {
          ElMessage.error('接收消息失败：' + data.error)
          messages.value = messages.value.filter(msg => msg !== assistantMessage)
          eventSource.close()
          loading.value = false
          return
        }

        if (data.type === 'start') {
          console.log('Stream started')
          return
        }

        if (data.type === 'done') {
          console.log('Stream completed')
          assistantMessage.streaming = false
          eventSource.close()
          loading.value = false
          return
        }

        if (data.type === 'reasoning') {
          assistantMessage.reasoning_content += data.content
        } else if (data.type === 'content') {
          assistantMessage.content += data.content
        }
        
        await scrollToBottom()
      } catch (e) {
        console.error('解析消息失败:', e, event.data)
      }
    }

    // 处理错误事件
    eventSource.onerror = (error) => {
      console.error('EventSource error:', error)
      ElMessage.error('连接断开，请重试')
      messages.value = messages.value.filter(msg => msg !== assistantMessage)
      eventSource.close()
      loading.value = false
    }

  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败：' + error.message)
    messages.value = messages.value.slice(0, -2)
    loading.value = false
  }
}

// 处理下拉菜单命令
const handleCommand = async (command, conv) => {
  switch (command) {
    case 'rename':
      try {
        const { value: newTitle } = await ElMessageBox.prompt('请输入新的对话名称', '重命名对话', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputValue: conv.title,
          inputValidator: (value) => {
            if (!value.trim()) {
              return '对话名称不能为空'
            }
            return true
          }
        })
        
        if (newTitle && newTitle.trim() !== conv.title) {
          const response = await axios.put(`${API_BASE_URL}/conversations/${conv.id}`, {
            title: newTitle.trim()
          })
          const index = conversations.value.findIndex(c => c.id === conv.id)
          if (index !== -1) {
            conversations.value[index] = response.data
          }
          ElMessage.success('重命名成功')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('重命名失败：' + (error.response?.data?.message || error.message))
        }
      }
      break
      
    case 'delete':
      try {
        await ElMessageBox.confirm('确定要删除这个对话吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await axios.delete(`${API_BASE_URL}/conversations/${conv.id}`)
        conversations.value = conversations.value.filter(c => c.id !== conv.id)
        
        if (currentConversation.value?.id === conv.id) {
          currentConversation.value = null
          messages.value = []
        }
        
        ElMessage.success('删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败：' + (error.response?.data?.message || error.message))
        }
      }
      break

    case 'setSystem':
      try {
        // 获取当前角色内容和预设角色
        const currentContent = conv.system_content || defaultSystemContent
        const roles = systemRoles.slice(0, -1);
        
        // 使用更直接的方式创建对话框
        await ElMessageBox({
          title: '设置AI助手角色',
          message: h('div', { style: { marginBottom: '16px' } }, [
            h('div', { style: { marginBottom: '16px' } }, [
              h('div', { style: 'font-weight: bold; margin-bottom: 8px;' }, '当前角色设定：'),
              h('div', { 
                style: 'padding: 12px; background: #f8f9fa; border-radius: 4px; font-size: 14px; white-space: pre-wrap; max-height: 100px; overflow-y: auto;'
              }, currentContent)
            ]),
            h('div', { style: { marginBottom: '16px' } }, '请点击选择一个预设角色，或创建自定义角色'),
            h('div', { 
              style: { 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', 
                gap: '16px' 
              } 
            }, [
              ...roles.map(role => 
                h('div', {
                  style: {
                    padding: '16px',
                    border: '1px solid #dcdfe6',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    backgroundColor: '#fff',
                    transition: 'all 0.3s',
                    position: 'relative'
                  },
                  onClick: async () => {
                    try {
                      // 角色被选中，关闭对话框
                      ElMessageBox.close()
                      
                      // 更新对话的系统角色
                      if (role.content !== currentContent) {
                        const response = await axios.put(`${API_BASE_URL}/conversations/${conv.id}`, {
                          system_content: role.content,
                          title: role.title
                        })
                        
                        // 更新对话列表中的对应项
                        const index = conversations.value.findIndex(c => c.id === conv.id)
                        if (index !== -1) {
                          conversations.value[index] = response.data
                        }
                        
                        ElMessage.success(`已将对话角色设置为 "${role.title}"`)
                      }
                    } catch (error) {
                      ElMessage.error('设置角色失败：' + (error.response?.data?.message || error.message))
                    }
                  },
                  onMouseover: (e) => {
                    e.currentTarget.style.borderColor = '#409EFF'
                    e.currentTarget.style.backgroundColor = '#ecf5ff'
                    e.currentTarget.style.transform = 'translateY(-2px)'
                    
                    // 显示角色内容预览
                    const preview = document.createElement('div')
                    preview.className = 'role-content-preview'
                    preview.style.cssText = `
                      position: absolute;
                      left: 100%;
                      top: 0;
                      width: 300px;
                      padding: 12px;
                      background: white;
                      border: 1px solid #dcdfe6;
                      border-radius: 4px;
                      box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
                      z-index: 9999;
                      margin-left: 8px;
                      white-space: pre-wrap;
                      max-height: 400px;
                      overflow-y: auto;
                      font-size: 12px;
                      color: #666;
                    `
                    preview.textContent = role.content
                    e.currentTarget.appendChild(preview)
                  },
                  onMouseleave: (e) => {
                    e.currentTarget.style.borderColor = '#dcdfe6'
                    e.currentTarget.style.backgroundColor = '#fff'
                    e.currentTarget.style.transform = 'translateY(0)'
                    
                    // 移除角色内容预览
                    const preview = e.currentTarget.querySelector('.role-content-preview')
                    if (preview) {
                      preview.remove()
                    }
                  }
                }, [
                  h('div', { style: { fontWeight: 'bold', marginBottom: '8px' } }, role.title),
                  h('div', { style: { fontSize: '12px', color: '#666' } }, role.content.split('\n')[0])
                ])
              ),
              // 添加自定义角色按钮
              h('div', {
                style: {
                  padding: '16px',
                  border: '1px solid #dcdfe6',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  backgroundColor: '#fff',
                  transition: 'all 0.3s',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  height: '100%'
                },
                onClick: async () => {
                  // 关闭角色选择对话框
                  ElMessageBox.close()
                  
                  try {
                    // 弹出自定义角色输入框
                    const { value } = await ElMessageBox.prompt(
                      '请设置AI助手的角色和行为指南',
                      '创建自定义角色',
                      {
                        confirmButtonText: '确定',
                        cancelButtonText: '取消',
                        inputType: 'textarea',
                        customClass: 'system-role-dialog',
                        inputValue: currentContent, // 预填当前角色内容
                        inputPlaceholder: `示例 - 自定义角色设定：

1. 角色身份：
- 明确角色的专业背景
- 设定角色的经验水平
- 定义角色的专业领域
- 说明角色的特殊技能

2. 沟通原则：
- 设定语言风格
- 定义回答方式
- 确定专业程度
- 规定行为准则

3. 专业要求：
- 列出核心能力
- 说明专业标准
- 定义工作方法
- 设置质量要求

4. 限制和原则：
- 明确行为边界
- 设定道德准则
- 规定禁止事项
- 确定处理原则

5. 其他要求：
- 补充特殊说明
- 添加额外规则
- 设定其他限制

请用中文回复。`,
                        inputValidator: (value) => {
                          if (!value.trim()) {
                            return '系统角色设置不能为空'
                          }
                          return true
                        }
                      }
                    )
                    
                    // 如果用户提供了自定义角色内容且与当前不同
                    if (value && value.trim() && value.trim() !== currentContent) {
                      // 尝试从自定义内容中提取标题（第一行）
                      const lines = value.trim().split('\n');
                      const title = lines[0].length > 20 
                        ? lines[0].substring(0, 20) + '...'  // 截取过长的标题
                        : lines[0];
                      
                      // 更新对话的系统角色和标题
                      const response = await axios.put(`${API_BASE_URL}/conversations/${conv.id}`, {
                        system_content: value.trim(),
                        title: title || '自定义角色'  // 使用提取的标题或默认名称
                      })
                      
                      // 更新对话列表中的对应项
                      const index = conversations.value.findIndex(c => c.id === conv.id)
                      if (index !== -1) {
                        conversations.value[index] = response.data
                      }
                      
                      ElMessage.success('角色设置成功')
                    }
                  } catch (error) {
                    if (error !== 'cancel') {
                      ElMessage.error('设置自定义角色失败：' + (error.response?.data?.message || error.message))
                    }
                  }
                },
                onMouseover: (e) => {
                  e.currentTarget.style.borderColor = '#409EFF'
                  e.currentTarget.style.backgroundColor = '#ecf5ff'
                  e.currentTarget.style.transform = 'translateY(-2px)'
                },
                onMouseleave: (e) => {
                  e.currentTarget.style.borderColor = '#dcdfe6'
                  e.currentTarget.style.backgroundColor = '#fff'
                  e.currentTarget.style.transform = 'translateY(0)'
                }
              }, [
                h('div', { style: { fontWeight: 'bold', marginBottom: '8px' } }, '创建自定义角色'),
                h('div', { style: { fontSize: '12px', color: '#666' } }, '创建一个完全自定义的AI助手角色')
              ])
            ])
          ]),
          showCancelButton: true,
          cancelButtonText: '取消',
          showConfirmButton: false,
          customClass: 'role-selection-dialog'
        }).catch(err => {
          if (err !== 'cancel') {
            console.error('对话框错误:', err)
          }
        })
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('角色设置失败：' + (error.response?.data?.message || error.message))
        }
      }
      break
  }
}

// 复制消息
const copyMessage = async (message) => {
  try {
    const textToCopy = message.role === 'assistant' 
      ? `${message.reasoning_content ? `思考过程：${message.reasoning_content}\n\n` : ''}${message.content}`
      : message.content
      
    await navigator.clipboard.writeText(textToCopy)
    ElMessage.success('复制成功')
  } catch (error) {
    ElMessage.error('复制失败：' + error.message)
  }
}

// 删除消息
const deleteMessage = async (message) => {
  try {
    await ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.delete(`${API_BASE_URL}/conversations/${currentConversation.value.id}/messages/${message.id}`)
    messages.value = messages.value.filter(msg => msg.id !== message.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.message || error.message))
    }
  }
}

onMounted(() => {
  fetchConversations()
})
</script>

<template>
  <div class="chat-container">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <el-button type="primary" @click="createConversation" class="new-chat-btn">
        新建对话
      </el-button>
      <div class="conversation-list">
        <div
          v-for="conv in conversations"
          :key="conv.id"
          class="conversation-item"
          :class="{ active: currentConversation?.id === conv.id }"
          @click="selectConversation(conv)"
        >
          <div class="conversation-title">
            {{ conv.title }}
            <div class="system-content" v-if="conv.system_content && conv.system_content !== defaultSystemContent">
              <el-tooltip 
                :content="conv.system_content" 
                placement="right"
                :show-after="500"
              >
                <el-icon><Setting /></el-icon>
              </el-tooltip>
            </div>
          </div>
          <el-dropdown 
            trigger="click" 
            @command="(command) => handleCommand(command, conv)"
            @click.stop
          >
            <div class="more-actions">
              <el-icon><MoreFilled /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="setSystem">
                  <el-icon><Setting /></el-icon>
                  设置角色
                </el-dropdown-item>
                <el-dropdown-item command="rename" divided>
                  <el-icon><Edit /></el-icon>
                  重命名
                </el-dropdown-item>
                <el-dropdown-item command="delete" divided>
                  <el-icon><Delete /></el-icon>
                  <span style="color: #f56c6c;">删除</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 主聊天区域 -->
    <div class="main-content">
      <div class="messages-container" ref="messagesContainer">
        <div v-if="!currentConversation" class="no-conversation">
          请创建或选择一个对话开始聊天
        </div>
        <template v-else>
          <div
            v-for="(message, index) in messages"
            :key="message.id"
            class="message"
            :class="[message.role, { streaming: message.streaming }]"
          >
            <div class="message-content">
              <div class="message-header">
                <span class="role-indicator">{{ message.role === 'user' ? '用户' : 'AI' }}</span>
                <div class="message-actions">
                  <el-tooltip content="复制" placement="top">
                    <el-button
                      type="text"
                      size="small"
                      @click="copyMessage(message)"
                      class="action-btn"
                    >
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="删除" placement="top">
                    <el-button
                      type="text"
                      size="small"
                      @click="deleteMessage(message)"
                      class="action-btn delete"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
              <template v-if="message.role === 'assistant'">
                <div v-if="message.reasoning_content" class="reasoning-content">
                  思考过程：{{ message.reasoning_content }}
                </div>
                <div v-if="message.reasoning_content" class="content-divider"></div>
                <div>{{ message.content }}</div>
                <span v-if="message.streaming" class="streaming-cursor"></span>
              </template>
              <template v-else>
                {{ message.content }}
              </template>
            </div>
          </div>
        </template>
      </div>

      <!-- 输入框 -->
      <div class="input-container">
        <el-input
          v-model="newMessage"
          type="textarea"
          :rows="3"
          placeholder="输入消息，按回车发送，Shift + 回车换行"
          @keydown="handleKeydown"
          :disabled="loading"
        />
        <el-button 
          type="primary" 
          @click="sendMessage" 
          class="send-btn"
          :loading="loading"
          :disabled="!currentConversation"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<style>
.chat-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #f5f5f5;
  position: fixed;
  top: 0;
  left: 0;
}

.sidebar {
  width: 250px;
  background-color: #fff;
  border-right: 1px solid #e0e0e0;
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.new-chat-btn {
  margin-bottom: 20px;
  width: 100%;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin-bottom: 5px;
  cursor: pointer;
  border-radius: 5px;
  color: #333;
  position: relative;
}

.conversation-item:hover {
  background-color: #f5f5f5;
}

.conversation-item.active {
  background-color: #e3f2fd;
}

.conversation-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.system-content {
  display: flex;
  align-items: center;
  color: #409EFF;
  font-size: 14px;
}

.more-actions {
  opacity: 0;
  transition: opacity 0.2s;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  color: #666;
}

.more-actions:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.conversation-item:hover .more-actions {
  opacity: 1;
}

.conversation-item.active .more-actions {
  opacity: 1;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  height: 100%;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 10px;
  margin-bottom: 20px;
  position: relative;
}

.no-conversation {
  text-align: center;
  color: #999;
  margin-top: 40%;
  font-size: 16px;
}

.message {
  margin-bottom: 20px;
  max-width: 80%;
}

.message.user {
  margin-left: auto;
}

.message.assistant {
  margin-right: auto;
}

.message-content {
  padding: 12px 16px;
  border-radius: 10px;
  background-color: #e3f2fd;
  white-space: pre-wrap;
  color: #333;
}

.message.user .message-content {
  background-color: #2196f3;
  color: white;
}

.message.streaming .message-content {
  background-color: #f5f5f5;
}

.streaming-cursor {
  display: inline-block;
  width: 8px;
  height: 15px;
  background-color: #666;
  margin-left: 2px;
  animation: blink 1s infinite;
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0; }
  100% { opacity: 1; }
}

.input-container {
  display: flex;
  gap: 10px;
  margin-top: auto;
}

.input-container .el-textarea {
  flex: 1;
}

.send-btn {
  align-self: flex-end;
}

.el-textarea__inner {
  resize: none !important;
}

.el-textarea__inner::placeholder {
  color: #999;
  font-size: 14px;
}

.reasoning-content {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 8px;
  padding: 8px;
  background-color: #f9f9f9;
  border-radius: 6px;
}

.content-divider {
  height: 1px;
  background-color: #eee;
  margin: 8px 0;
}

.message.assistant .message-content {
  background-color: #fff;
  border: 1px solid #e0e0e0;
}

.message.streaming .message-content {
  border-color: #2196f3;
}

.el-dropdown-menu__item {
  display: flex !important;
  align-items: center;
  gap: 8px;
}

.el-dropdown-menu__item .el-icon {
  margin-right: 4px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.role-indicator {
  font-size: 12px;
  color: #666;
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.message-actions {
  display: none;
  gap: 4px;
}

.message:hover .message-actions {
  display: flex;
}

.action-btn {
  padding: 2px;
  color: #666;
}

.action-btn:hover {
  color: #409EFF;
}

.action-btn.delete:hover {
  color: #F56C6C;
}

/* 角色选择对话框样式 */
:deep(.role-selection-dialog) {
  width: 600px !important;
  max-width: 90vw !important;
}

:deep(.role-selection-dialog .el-message-box__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
  background-color: #fafafa;
  border-radius: 8px 8px 0 0;
}

:deep(.role-selection-dialog .el-message-box__content) {
  padding: 24px;
}

:deep(.role-selection-dialog .el-message-box__title) {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

/* 自定义角色选项的悬停效果 */
.role-option:hover {
  border-color: #409EFF !important;
  background-color: #ecf5ff !important;
  transform: translateY(-2px);
  transition: all 0.3s ease;
}

/* 系统角色输入框对话框样式 */
:deep(.system-role-dialog) {
  width: 800px !important;
  max-width: 90vw !important;
}

:deep(.system-role-dialog .el-message-box__content) {
  padding: 24px;
}

:deep(.system-role-dialog .el-textarea__inner) {
  min-height: 200px !important;
}
</style>
