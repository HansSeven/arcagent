from langchain_ollama import ChatOllama
from agent_builder import create_agent,agent_node,AgentState,Executor_node
from tools_definition import Union_analysis,CopyFeatures_management,Intersect_analysis, Buffer_analysis, Clip_analysis, Project_management, Kernel_Density, SpatialJoin_analysis,SummaryStatistics, SelectLayerByAttribute, GenerateNearTable_analysis, TableToTable_conversion,MultipleRingBuffer_analysis, Erase_analysis, Dissolve_management, Identity_analysis, Near_analysis,Split_analysis, FeatureToPoint_management, FeatureVerticesToPoints_management, FeatureToLine_management
import functools
from langgraph.prebuilt import ToolNode
from typing import Literal
from langgraph.graph import END, StateGraph, START
from langchain_core.messages import HumanMessage
from RAGtest import MatchToolName
from langchain_openai import ChatOpenAI
from tool_bind_node_norag import  tool_select_bind_node
tools = [Union_analysis,CopyFeatures_management,Intersect_analysis,Buffer_analysis, Clip_analysis, Project_management, Kernel_Density, SpatialJoin_analysis,SummaryStatistics, SelectLayerByAttribute, GenerateNearTable_analysis, TableToTable_conversion,MultipleRingBuffer_analysis, Erase_analysis, Dissolve_management, Identity_analysis, Near_analysis,Split_analysis, FeatureToPoint_management, FeatureVerticesToPoints_management, FeatureToLine_management]
"""                    框架主体                                       """
# tool_rag_node=functools.partial(tool_rag_bind_node,llm=llm,tool_pool=tools,system_message="when use tool,you can only use the above tools,don't try to make up a tool."
#                 "When adding string parameters (e.g., file paths), make sure to escape special characters properly—\n"
#                 "especially backslashes in file addresses, such as Windows-style paths.\n"
#                 "When writing file paths, use forward slashes (/) instead of backslashes (\)ps,you can ask for the parameters from user\n",)
#
llm = ChatOpenAI(model="qwen-turbo-latest",openai_api_key="sk-3a717e8295f5420081aee2be05b35d1c",openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1")

Planner_agent = create_agent(llm,[MatchToolName],system_message="""You are a GIS task reviser working in a restricted tool environment.

Your task is to revise a structured GIS task **based on the actual local tool names** available in your runtime.

You MUST follow the steps below in strict order:

1. Tool Matching:
   - For each tool listed in the original "tools" field, **call the tool MatchToolName** to get the actual local tool name.
   - Replace the original tool name with the matched result.
   - If a tool has no match (returns None), treat it as unavailable.

2. Step Filtering:
   - Remove any step that uses an unavailable tool (i.e., tools that failed to match).
   - If a removed step was producing an intermediate result used in later steps, you must either revise those later steps or remove them too.

3. Field Updating:
   - The "tools" field must be updated to include only the matched and available tools used in the final steps.
   - You may modify "instruction", "task_type", "key_layers", or "parameters" **only if needed** to preserve task consistency.

4. Output:
   - You must output a single **valid JSON object** in this exact field order: "instruction", "task_type", "steps", "tools", "key_layers", "parameters".
   - Do NOT include explanation, commentary, or any extra text. Only output the JSON.

IMPORTANT: 
- You are NOT allowed to guess tool names.
- You are NOT allowed to use tools that were not returned by MatchToolName.
- You MUST call MatchToolName on every original tool name before deciding which tools are usable.

Please revise the following structured GIS task by matching tool names with MatchToolName and filtering invalid steps accordingly. Output the final revised JSON only.
You are the pre-planner, and the executor is behind you.you should not write FINAL ANSWER.


""")
Planner_node = functools.partial(agent_node, agent=Planner_agent, name="Planner")
tool_node = ToolNode([MatchToolName] +tools)
tool_rag_node=functools.partial(tool_select_bind_node,llm=llm,tool_pool=tools,system_message="when use tool,you can only use the above tools,don't try to make up a tool."
                "When adding string parameters (e.g., file paths), make sure to escape special characters properly—\n"
                "especially backslashes in file addresses, such as Windows-style paths.\n"
                "When writing file paths, use forward slashes (/) instead of backslashes (\)ps,you can ask for the parameters from user\n"
                                "you can generate your file in  D:/output")
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

workflow = StateGraph(AgentState)
workflow.add_node("Planner", Planner_node)
workflow.add_node("tool_rag",tool_rag_node)
workflow.add_node("Executor", Executor_node)
workflow.add_node("call_tool", tool_node)
workflow.add_conditional_edges(
    "Planner",
    router,
    {"continue": "tool_rag","call_tool": "call_tool", "__end__": END},
)
workflow.add_conditional_edges(
    "tool_rag",
    router,
    {"continue": "Executor", "call_tool": "call_tool", "__end__": END},
)
workflow.add_conditional_edges(
    "Executor",
    router,
    {"continue": "Executor", "call_tool": "call_tool", "__end__": END},
)


workflow.add_conditional_edges(                                      # 这个边是无向边，数据可在两侧流动
    "call_tool",
    # Each agent node updates the 'sender' field
    # the tool calling node does not, meaning
    # this edge will route back to the original agent
    # who invoked the tool
    lambda x: x["sender"],                                              # 数据流向router函数
    {                                     # 根据收到的message判断数据流向
        "Planner": "Planner",
        "Executor":"Executor"
    },
)
workflow.add_edge(START, "Planner")
graph = workflow.compile()
#
#
# 调用该图
events = graph.stream(
    {
        "messages": [
            HumanMessage(
                content="""
{
  "instruction": "我觉得有些商场或者大市场离公交站特别远，去一趟不方便，能不能帮我找出这种没有公交覆盖的商业点？",
  "task_type": "Transit Accessibility Filtering for Commercial POIs",
  "steps": [
    "1. Use SelectLayerByAttribute to extract POIs where fclass = 'mall', output = commercial_pois.",
    "2. Use SelectLayerByAttribute to extract Transport where fclass = 'bus_stop', output = bus_pois.",
    "3. Run Buffer_analysis on bus_pois with buffer_distance = 500 meters, output = bus_buffer.",
    "4. Run Erase_analysis to subtract bus_buffer from commercial_pois, output = isolated_commercial.",
    "5. Run Dissolve_management on isolated_commercial to merge overlapping or close facilities, output = commercial_gap_zone.",
    "6. Run FeatureToPoint_management on commercial_gap_zone, output = center_points.",
    "7. Export commercial_gap_zone and center_points using CopyFeatures_management."
  ],
  "tools": [
    "SelectLayerByAttribute",
    "Buffer_analysis",
    "Erase_analysis",
    "Dissolve_management",
    "FeatureToPoint_management",
    "CopyFeatures_management"
  ],
  "key_layers": [
    "POIs=C:/Users/90608/Desktop/input/gis_osm_pois_free_1.shp",
    "Transport=C:/Users/90608/Desktop/input/gis_osm_transport_free_1.shp"
  ],
  "parameters": {
    "buffer_distance": "500 meters"
  }
}

"""

            )
        ],
    },
    # Maximum number of steps to take in the graph
    {"recursion_limit": 150},
)
for s in events:
    print(s)
    print("----")

