# searchgpt-explorer-learning

## 简介

`searchgpt-explorer-learning` 是一个基于 `SearchGPT-Explorer` 项目的**学习项目**，旨在深入理解和掌握 `SearchGPT-Explorer` 的工作原理和实现细节。本项目通过实践、分析和实验性修改，帮助学习者更好地理解如何将搜索 API 功能与大型语言模型集成，实现类似 New Bing 的实时网络信息访问能力。

**注意：** 本项目并非 `SearchGPT-Explorer` 的官方版本，而是一个个人学习和实验性质的项目。

## 学习目标

*   **深入理解:** 理解 `SearchGPT-Explorer` 的核心架构和设计思想。
*   **代码分析:** 详细分析 `SearchGPT-Explorer` 的关键代码模块，例如搜索 API 的集成、GPT 模型的调用、以及动态函数调用等。
*   **实验性修改:** 对 `SearchGPT-Explorer` 的代码进行实验性修改，验证理解，并探索不同的实现方式。
*   **分享心得:** 记录学习过程中的心得体会，并与其他学习者交流。

## 基于 `SearchGPT-Explorer` 的特性

`searchgpt-explorer-learning` 基于 `SearchGPT-Explorer` 项目，继承了以下特性：

*   集成搜索 API 和 GPT 模型
*   实时网络信息检索
*   动态函数调用，实现灵活的搜索操作
*   错误处理和稳健的 API 交互
*   复用`function calling`功能，接口易用，增强 AI 对话能力

## 快速开始 (基于 `SearchGPT-Explorer` 的设置)

### 前提条件

*   Python 3.7+
*   OpenAI API 密钥
*   DuckDuckGo 搜索 API（无需密钥）

### 安装

1.  克隆本仓库：

    ```bash
    git clone [你的仓库地址]
    cd searchgpt-explorer-learning
    ```

2.  安装所需包： (与 `SearchGPT-Explorer` 相同)

    ```bash
    pip install -r requirements.txt
    ```

3.  设置 OpenAI API 密钥为环境变量： (与 `SearchGPT-Explorer` 相同)

    ```bash
    export OPENAI_API_KEY='your-api-key-here'
    ```

### 使用

本项目主要用于学习和实验，你可以：

*   **运行 `search_gpt_core.py`：** 运行主脚本，观察 `SearchGPT-Explorer` 的基本功能。
    ```bash
    python search_gpt_core.py
    ```
*   **修改代码：** 在 `src/` 目录下修改代码，例如尝试不同的搜索策略、修改 GPT 模型调用方式等。
*   **分析代码：** 阅读代码，理解其实现逻辑，并记录你的学习笔记。

## 项目结构

