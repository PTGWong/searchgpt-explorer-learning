# searchgpt-explorer-learning

## 简介

`searchgpt-explorer-learning` 是一个基于 `SearchGPT-Explorer` 项目的**学习项目**，旨在深入理解和掌握 `SearchGPT-Explorer` 的工作原理和实现细节。本项目通过实践、分析和实验性修改，帮助学习者更好地理解如何将搜索 API 功能与大型语言模型集成，实现类似 New Bing 的实时网络信息访问能力。

**注意：** 本项目并非 `SearchGPT-Explorer` 的官方版本，而是一个个人学习和实验性质的项目。

## 快速开始 (基于 `SearchGPT-Explorer` 的设置)

### 前提条件

*   Python 3.7+
*   DeepSeek API 密钥
*   DuckDuckGo 搜索 API（无需密钥）

### 安装

1.  克隆本仓库：

    ```bash
    git clone https://github.com/PTGWong/searchgpt-explorer-learning.git
    cd searchgpt-explorer-learning
    ```

2.  安装所需包： (与 `SearchGPT-Explorer` 相同)

    ```bash
    pip install -r requirements.txt
    ```

3.  设置 DeepSeek API 密钥为环境变量： (与 `SearchGPT-Explorer` 相同，只需替换内容为DeepSeek的API即可，**`OPENAI_KEY_KEY`**和**`OPENAI_BASE_URL`** 变量名称无需更改)

    ```bash
    export OPENAI_API_KEY="YOUR-DEEPSEEK-API-KEY"
    export OPENAI_BASE_URL="https://api.deepseek.com"
    ```

### 使用

本项目主要用于学习和实验，你可以：

*   **运行 `search_gpt_core.py`：** 运行主脚本，观察 `SearchGPT-Explorer` 的基本功能。
    ```bash
    python search_gpt_core.py
    ```
*   **修改代码：** 在主目录下修改代码，例如尝试不同的搜索策略、修改 GPT 模型调用方式等。
*   **分析代码：** 阅读代码，理解其实现逻辑，并记录你的学习笔记。

## 项目结构

searchgpt-explorer-learning/

├── LICENSE             # 项目许可证文件

├── README.md           # 项目说明文档

├── requirements.txt    # 项目依赖包列表

├── search_gpt_core.py  # 主脚本文件，集成搜索 API 和 DeepSeek 模型调用
