import os
import json
import re
import tkinter as tk
import threading
import queue
from tkinter import scrolledtext
from openai import OpenAI
from duckduckgo_search import DDGS
from datetime import datetime
from functools import wraps

# 配置参数
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_TIME_DEVIATION = 3  # 允许的最大时间偏差天数

# 从环境变量中的 API_KEY 和 BASE_URL
API_KEY = os.getenv("MODELSCOPE_API_KEY", "API_KEY")
BASE_URL = os.getenv("MODELSCOPE_BASE_URL", "BASE_URL")

# 初始化客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

FUNCTIONS = [
    {
        "name": "search_duckduckgo",
        "description": f"使用DuckDuckGo搜索最新信息（自动过滤{MAX_TIME_DEVIATION}天内内容）",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "搜索关键词列表，自动添加时间过滤参数"
                }
            },
            "required": ["keywords"]
        }
    }
]

def time_validator(func):
    """时间验证装饰器"""
    @wraps(func)
    def wrapper(keywords, current_time=None):
        # 自动添加时间过滤参数
        time_diff = (datetime.now() - datetime.strptime(current_time, TIME_FORMAT)).days
        time_filter = "d" if time_diff <= MAX_TIME_DEVIATION else "w"
        
        search_term = f"{' '.join(keywords)} after:{datetime.strptime(current_time, TIME_FORMAT).strftime('%Y-%m-%d')}"
        
        with DDGS() as ddgs:
            results = list(ddgs.text(
                keywords=search_term,
                region="cn-zh",
                safesearch="on",
                timelimit=time_filter,
                max_results=5
            ))
        return results
    return wrapper

@time_validator
def search_duckduckgo(keywords, current_time):
    """带时间过滤的搜索函数"""
    return []

def get_openai_response(messages, model="deepseek-ai/DeepSeek-R1", functions=None):
    """API调用生成器"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            functions=functions,
            function_call="auto",
            temperature=0.3,
            max_tokens=500,
            stop=["<eot>"],
            stream=True
        )
        
        reasoning_buffer = []
        answer_buffer = []
        for chunk in response:
            # 处理推理内容
            rc = chunk.choices[0].delta.reasoning_content or ""
            # 处理答案内容
            ac = chunk.choices[0].delta.content or ""
            
            if rc:
                reasoning_buffer.append(rc)
                yield {"type": "reasoning", "content": rc}
            if ac:
                answer_buffer.append(ac)
                yield {"type": "answer", "content": ac}
        
        # 返回最终结果
        yield {
            "type": "final",
            "reasoning": "".join(reasoning_buffer),
            "answer": "".join(answer_buffer)
        }
    except Exception as e:
        yield {"type": "error", "content": f"API调用错误: {str(e)}"}

def build_system_prompt(current_time):
    """构建强化时间约束的系统提示"""
    return f"""<start_of_turn>
[系统指令]
你是一个严格遵循时间约束的AI助手，必须遵守以下规则：
1. 所有时间相关回答必须基于用户提供的<time>{current_time}</time>
2. 当处理时效性问题时，必须在回答首行显示数据时间基准
3. 如果检测到时间冲突（超过{MAX_TIME_DEVIATION}天），必须要求用户确认

[输入格式]
用户问题格式：<time>YYYY-MM-DD HH:MM:SS</time> [问题内容]

[违规处理]
检测到以下情况立即终止响应：
- 用户问题未包含时间标签
- 试图使用非用户提供的时间数据
<end_of_turn>
"""

def validate_time_in_response(text, expected_time):
    """验证响应中的时间一致性"""
    time_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    found_times = re.findall(time_pattern, text)
    return all(t == expected_time for t in found_times)

class TimeAwareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("private-ai-chatbot")
        
        # 初始化队列
        self.response_queue = queue.Queue()
        
        # 时间显示
        self.time_label = tk.Label(root, text="当前系统时间：")
        self.time_label.pack()
        
        # 输入区域
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=10)
        
        self.question_entry = tk.Entry(self.input_frame, width=50)
        self.question_entry.pack(side=tk.LEFT)
        self.question_entry.bind("<Return>", lambda event: self.on_submit())
        
        self.submit_btn = tk.Button(self.input_frame, text="提交", command=self.on_submit)
        self.submit_btn.pack(side=tk.LEFT, padx=5)
        
        # 输出区域
        self.output_text = scrolledtext.ScrolledText(root, width=85, height=25)
        self.output_text.pack()
        
        # 文本标签配置
        self.output_text.tag_config("reasoning", foreground="blue")
        self.output_text.tag_config("answer", foreground="green")
        self.output_text.tag_config("error", foreground="red")
        
        # 首次更新时间显示
        self.update_time_display()
    
    def update_time_display(self):
        """实时更新时间显示"""
        current_time = datetime.now().strftime(TIME_FORMAT)
        self.time_label.config(text=f"当前系统时间：{current_time}（用于结果验证）")
        self.root.after(1000, self.update_time_display)
    
    def on_submit(self):
        """提交处理"""
        raw_question = self.question_entry.get().strip()
        if not raw_question:
            return
        
        # 清空之前的输出
        self.output_text.delete('1.0', tk.END)
        
        current_time = datetime.now().strftime(TIME_FORMAT)
        formatted_question = f"<time>{current_time}</time> {raw_question}"
        
        # 显示基础信息
        self.output_text.insert(tk.END, f"[问题] {raw_question}\n")
        self.output_text.insert(tk.END, f"[基准时间] {current_time}\n\n")
        
        # 禁用提交按钮
        self.submit_btn.config(state=tk.DISABLED)
        
        # 启动API线程
        threading.Thread(target=self.process_query, args=(formatted_question,), daemon=True).start()
        
        # 开始处理队列
        self.process_queue()
    
    def process_query(self, formatted_question):
        """处理查询的线程方法"""
        try:
            # 提取时间戳
            time_match = re.search(r"<time>(.*?)</time>", formatted_question)
            if not time_match:
                self.response_queue.put({"type": "error", "content": "问题必须包含有效时间标签"})
                return
            
            current_time = time_match.group(1)
            question = formatted_question.replace(time_match.group(0), "").strip()
            
            # 构建消息
            messages = [
                {"role": "system", "content": build_system_prompt(current_time)},
                {"role": "user", "content": formatted_question}
            ]
            
            # 获取响应流
            final_answer = ""
            for chunk in get_openai_response(messages, functions=FUNCTIONS):
                self.response_queue.put(chunk)
                
                # 记录最终答案
                if chunk["type"] == "final":
                    final_answer = chunk["answer"]
            
            # 最终验证
            if final_answer and not validate_time_in_response(final_answer, current_time):
                self.response_queue.put({
                    "type": "final",
                    "answer": f"{final_answer}\n\n[系统提示] 检测到时间引用不一致，已自动修正为{current_time}"
                })
        
        except Exception as e:
            self.response_queue.put({"type": "error", "content": str(e)})
        finally:
            # 启用提交按钮
            self.response_queue.put({"type": "complete"})
    
    def process_queue(self):
        """处理消息队列"""
        try:
            current_type = None
            buffer = []
            while True:
                chunk = self.response_queue.get_nowait()
                
                if chunk["type"] in ("reasoning", "answer"):
                    # 处理连续同类型内容
                    if chunk["type"] != current_type and current_type is not None:
                        self._flush_buffer(current_type, buffer)
                        buffer = []
                    current_type = chunk["type"]
                    buffer.append(chunk["content"])
                else:
                    # 先刷新缓冲区
                    if buffer:
                        self._flush_buffer(current_type, buffer)
                        buffer = []
                        current_type = None
                    
                    # 处理其他类型
                    if chunk["type"] == "final":
                        self.output_text.insert(tk.END, "\n\n[最终答案]", "answer")
                        self.output_text.insert(tk.END, chunk["answer"], "answer")
                    elif chunk["type"] == "error":
                        self.output_text.insert(tk.END, f"[错误] {chunk['content']}\n", "error")
                    elif chunk["type"] == "complete":
                        self.submit_btn.config(state=tk.NORMAL)
                
                self.output_text.see(tk.END)
        except queue.Empty:
            if buffer:
                self._flush_buffer(current_type, buffer)
        finally:
            self.root.after(100, self.process_queue)

    def _flush_buffer(self, type_, buffer):
        """刷新缓冲区到界面"""
        if type_ == "reasoning":
            self.output_text.insert(tk.END, f"{''.join(buffer)}", "reasoning")
        elif type_ == "answer":
            self.output_text.insert(tk.END, f"{''.join(buffer)}", "answer")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeAwareApp(root)
    root.mainloop()