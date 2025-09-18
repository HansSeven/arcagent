from langchain_core.messages import (BaseMessage,HumanMessage,ToolMessage,AIMessage)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Annotated, Sequence, TypedDict
import operator
"""                    代码prebuilt部分                                    """
def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " After you complete all tasks, another assistant with different tools will continue the flow."
                " Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop,only use it when try to stop."
                " You have access to the following tools: {tool_names}.\n{system_message}"
                ,
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    #   system message 可以是路由和描述？
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    #   不对应该是分级，预处理agent，处理agent，和输出agent partial固定参数
    return prompt | llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
    analyzer_agent: None


def agent_node(state, agent, name):
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so that we know who to pass to next.
        "sender": name,
    }

def Executor_node(state):
    agent = state.get("analyzer_agent")
    if agent is None:
        raise ValueError("No analyzer_agent found in state.")
    print(f"[Executor] ✅ Analyzer agent found. Running agent_node with {len(state['messages'])} messages.")
    return agent_node(state, agent=agent, name="Executor")