from multiprocessing.pool import worker

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama          #调用ollama的langgraph必须使用这个
from langgraph.graph import END, StateGraph, START
from typing import Annotated
from langchain_core.tools import tool
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict
import functools
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode
from typing import Literal


def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                #待改
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                " You have access to the following tools: {tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_tools(tools)
#state，总计信息
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
#自定义模式的agent——node，所以我说那个计划任务也可以开自定义版本。只不过是自定义的toolnode
def agent_node(state, agent, name):
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)#toolnode核心
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }
llm = ChatOllama(model="llama3.2:latest")

#类比，给我改*
@tool
def CSV_load(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
        #神奇函数，我写个自定义就行
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n\`\`\`python\n{code}\n\`\`\`\nStdout: {result}"
    return (
        result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    )
'''
tavily_tool = TavilySearchResults(max_results=5)
这个是类比的api
'''
tavily_tool=[CSV_load]
worker_agent = create_agent(
    llm,
    [tavily_tool],#改成工具序列
    system_message="You should try to use these tool to deal with the commond，it is important to use the tool step by"
                   "step,you must analyze the commond and find the flow to complete."
                   "If you have completed all tasks, respond with FINAL ANSWER,this is the order to .",
)
#自定义node定义，partial固定参数
research_node = functools.partial(agent_node, agent=worker_agent, name="Researcher")

tools = [tavily_tool, python_repl]
tool_node = ToolNode(tools)
#router逻辑
def router(state) -> Literal["call_tool", "__end__", "continue"]:
    # This is the router
    messages = state["messages"]
    last_message = messages[-1]                                 # state是系统state是在各种工具里面流的
    if last_message.tool_calls:
        # The previous agent is invoking a tool
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:                  # 边缘逻辑，这里来判断是否脱出、继续、工具调用，很重要的，这个是终止关键

        # Any agent decided the work is done
        return "__end__"
    return "continue"

#graph成型
workflow = StateGraph(AgentState)

workflow.add_node("Researcher", research_node)
workflow.add_node("chart_generator", chart_node)
workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "Researcher",
    router,
    {"continue": "chart_generator", "call_tool": "call_tool", END: END},
)
workflow.add_conditional_edges(
    "chart_generator",
    router,
    {"continue": "Researcher", "call_tool": "call_tool", END: END},
)

workflow.add_conditional_edges(
    "call_tool",
    # Each agent node updates the 'sender' field
    # the tool calling node does not, meaning
    # this edge will route back to the original agent
    # who invoked the tool
    lambda x: x["sender"],
    {
        "Researcher": "Researcher",
        "chart_generator": "chart_generator",
    },
)
workflow.add_edge(START, "Researcher")
graph = workflow.compile()
#invoke模式开启，这里输入可以用来读输入，核心在于能否一直交流，不过问题不大，论文不要求你做成界面人性化
events = graph.stream(
    {
        "messages": [
            HumanMessage(
                content="Fetch the UK's GDP over the past 5 years,"
                " then draw a line graph of it."
                " Once you code it up, finish."
            )
        ],
    },
    # Maximum number of steps to take in the graph
    {"recursion_limit": 150},
)
for s in events:
    print(s)
    print("----")