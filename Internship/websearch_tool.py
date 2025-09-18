from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from langchain.schema import HumanMessage, SystemMessage
from openai import OpenAI

""""""


client = OpenAI(
    api_key="sk-3a717e8295f5420081aee2be05b35d1c",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def qwen_chat(messages, model="qwen-max"):
    return client.chat.completions.create(
        model=model,
        messages=messages
    ).choices[0].message.content

"""判断联网"""
def should_use_search(state):
    user_input = state["question"]
    keywords = ["最近", "现在", "今年", "最新", "多少", "哪里可以买", "排名", "官网", "GitHub"]
    if any(k in user_input for k in keywords):
        return "search"
    return "skip"
"""构造检索query"""
def build_search_query(state):
    question = state["question"]
    return {**state, "query": question}  # 暂时直接用问题做 query

"""搜索引擎"""
def search_web(state):
    query = state["query"]
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))
    urls = [r["href"] for r in results if "href" in r]
    return {**state, "search_results": urls}
"""抓取网页，提取正文"""
def fetch_webpage_text(state):
    texts = []
    for url in state["search_results"]:
        try:
            r = requests.get(url, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            body = soup.get_text(separator="\n").strip()
            texts.append(body[:2000])  # 只取前2000字
        except:
            continue
    return {**state, "web_contents": texts}

"""模型总结网页内容"""

def summarize_web(state):
    summaries = []
    for content in state["web_contents"]:
        resp = qwen_chat([
            {"role": "system", "content": "请总结这段网页内容"},
            {"role": "user", "content": content}
        ])
        summaries.append(resp)
    return {**state, "summaries": summaries}

"""生成最终回答"""
def generate_answer(state):
    question = state["question"]
    summary_context = "\n\n".join(state["summaries"])
    resp = qwen_chat([
        {"role": "system", "content": "请根据以下资料回答用户问题："},
        {"role": "user", "content": f"{summary_context}\n\n问题：{question}"}
    ])
    return {"final_answer": resp}

