from langgraph.graph import StateGraph
from websearch_tool import should_use_search,build_search_query,search_web,fetch_webpage_text,summarize_web,generate_answer
from typing import TypedDict, List
class WebSearchState(TypedDict):
    question: str
    query: str
    search_results: List[str]
    web_contents: List[str]
    summaries: List[str]
    final_answer: str  # 可选字段也加上

# 然后传这个类型定义给 StateGraph
workflow = StateGraph(WebSearchState)

workflow.add_node("query_builder", build_search_query)
workflow.add_node("search_web", search_web)
workflow.add_node("fetch_web", fetch_webpage_text)
workflow.add_node("summarize", summarize_web)
workflow.add_node("answer", generate_answer)

# 条件跳转
workflow.add_conditional_edges("query_builder", should_use_search, {
    "search": "search_web",
    "skip": "answer"
})
workflow.add_edge("search_web", "fetch_web")
workflow.add_edge("fetch_web", "summarize")
workflow.add_edge("summarize", "answer")

workflow.set_entry_point("query_builder")
app = workflow.compile()

result=app.invoke({"question":"苹果手机最新型号"})
print(result["final_answer"])