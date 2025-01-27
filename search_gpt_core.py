import os
import json
from openai import OpenAI
from duckduckgo_search import DDGS

# 从环境变量中获取 DeepSeek 的 API 密钥和地址
API_KEY = os.getenv("YOUR_DEEPSEEK_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")

# 初始化 OpenAI 客户端（实际调用的是 DeepSeek API）
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# 定义函数调用
FUNCTIONS = [
    {
        "name": "search_duckduckgo",
        "description": "使用DuckDuckGo搜索引擎查询信息。可以搜索最新新闻、文章、博客等内容。",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "搜索的关键词列表。例如：['Python', '机器学习', '最新进展']。"
                }
            },
            "required": ["keywords"]
        }
    }
]

# DuckDuckGo 搜索函数
def search_duckduckgo(keywords):
    search_term = " ".join(keywords)
    with DDGS() as ddgs:
        return list(ddgs.text(keywords=search_term, region="cn-zh", safesearch="on", max_results=5))

# 打印搜索结果
def print_search_results(results):
    for result in results:
        print(f"标题: {result['title']}\n链接: {result['href']}\n摘要: {result['body']}\n---")

# 调用 DeepSeek API 获取响应
def get_openai_response(messages, model="deepseek-chat", functions=None, function_call=None):
    try:
        response = client.chat.completions.create(
            model=model,  # 使用 deepseek-chat 模型
            messages=messages,
            functions=functions,
            function_call=function_call
        )
        return response.choices[0].message
    except Exception as e:
        print(f"调用 DeepSeek API 时出错: {str(e)}")
        return None

# 处理函数调用
def process_function_call(response_message):
    function_name = response_message.function_call.name
    function_args = json.loads(response_message.function_call.arguments)

    print(f"\n模型选择调用函数: {function_name}")

    if function_name == "search_duckduckgo":
        keywords = function_args.get('keywords', [])

        if not keywords:
            print("错误：模型没有提供搜索关键词")
            return None

        print(f"关键词: {', '.join(keywords)}")

        function_response = search_duckduckgo(keywords)
        print("\nDuckDuckGo搜索返回结果:")
        print_search_results(function_response)

        return function_response
    else:
        print(f"未知的函数名称: {function_name}")
        return None

# 主函数
def main(question):
    print(f"问题：{question}")

    messages = [{"role": "user", "content": question}]
    response_message = get_openai_response(
        messages, functions=FUNCTIONS, function_call="auto")

    if not response_message:
        return

    if response_message.function_call:
        if not response_message.content:
            response_message.content = ""
        function_response = process_function_call(response_message)
        if function_response:
            messages.extend([
                response_message.model_dump(),
                {
                    "role": "function",
                    "name": response_message.function_call.name,
                    "content": json.dumps(function_response, ensure_ascii=False)
                }
            ])

            final_response = get_openai_response(messages, model="deepseek-chat")
            if final_response:
                print("\n最终回答:")
                print(final_response.content)
    else:
        print("\n模型直接回答:")
        print(response_message.content)

# 程序入口
if __name__ == "__main__":
    main("植物大战僵尸杂交版的作者是谁？他是怎么想到做出来这个游戏的？")