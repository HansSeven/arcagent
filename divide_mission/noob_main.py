from agent_builder import create_agent,agent_node,AgentState
from tools_definition import Union_analysis,CopyFeatures_management,Intersect_analysis, Buffer_analysis, Clip_analysis, Project_management, Kernel_Density, SpatialJoin_analysis,SummaryStatistics, SelectLayerByAttribute, GenerateNearTable_analysis, TableToTable_conversion,MultipleRingBuffer_analysis, Erase_analysis, Dissolve_management, Identity_analysis, Near_analysis,Split_analysis, FeatureToPoint_management, FeatureVerticesToPoints_management, FeatureToLine_management
import functools
from langgraph.prebuilt import ToolNode
from typing import Literal
from langgraph.graph import END, StateGraph, START
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from tool_addition import DeleteField_management,AddField_management,CalculateField_management,Merge_management,Delete_management,RepairGeometry_management,MultipartToSinglepart_management,AddGeometryAttributes_management,MakeFeatureLayer_management,AddJoin_management,RemoveJoin_management,PolygonToRaster_conversion,RasterToPolygon_conversion,FeatureClassToShapefile_conversion,MultipartToSinglepart_analysis,SelectLayerByLocation_management,FeatureClassToFeatureClass_conversion
tools = [Union_analysis,CopyFeatures_management,Intersect_analysis,Buffer_analysis, Clip_analysis, Project_management, Kernel_Density, SpatialJoin_analysis,SummaryStatistics, SelectLayerByAttribute, GenerateNearTable_analysis, TableToTable_conversion,MultipleRingBuffer_analysis, Erase_analysis, Dissolve_management, Identity_analysis, Near_analysis,Split_analysis, FeatureToPoint_management, FeatureVerticesToPoints_management, FeatureToLine_management]
ADtools=[DeleteField_management,AddField_management,CalculateField_management,Merge_management,Delete_management,RepairGeometry_management,MultipartToSinglepart_management,AddGeometryAttributes_management,MakeFeatureLayer_management,AddJoin_management,RemoveJoin_management,PolygonToRaster_conversion,RasterToPolygon_conversion,FeatureClassToShapefile_conversion,MultipartToSinglepart_analysis,SelectLayerByLocation_management,FeatureClassToFeatureClass_conversion]
"""                    框架主体                                       """
llm = ChatOpenAI(model="qwen-plus",openai_api_key="sk-3a717e8295f5420081aee2be05b35d1c",openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1")
Executor_agent=create_agent(llm,tools+ADtools,system_message="when use tool,you can only use the above tools,don't try to make up a tool."
                "When adding string parameters (e.g., file paths), make sure to escape special characters properly—\n"
                "especially backslashes in file addresses, such as Windows-style paths.\n"
                "When writing file paths, use forward slashes (/) instead of backslashes (\)ps,you can ask for the parameters from user\n"
                                "you can generate your file in  D:/output")
Executor_node = functools.partial(agent_node, agent=Executor_agent, name="Executor")
tool_node = ToolNode(tools+ADtools)
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
workflow.add_node("Executor", Executor_node)
workflow.add_node("call_tool", tool_node)
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
        "Executor":"Executor"
    },
)
workflow.add_edge(START, "Executor")
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
  "instruction": "现在很多医院周围都有公交站、加油站，还有球场这种人多噪声大的地方，可能会影响病人休息，麻烦你帮我把这些干扰重叠的区域提出来，用于做医院周边控制区。",
  "task_type": "Hospital Surrounding Conflict Control Extraction",
  "steps": [
    "1. Start by selecting POIs where fclass is 'hospital' and save the result as hospital_pois.",
    "2. Then go to the Traffic layer and extract features where fclass = 'fuel', and call it fuel_pois.",
    "3. In the POIs layer, select features where fclass is 'stadium' and save them as stadium_pois.",
    "4. From the Transport layer, extract bus stops by selecting features with fclass = 'bus_stop'; store them as bus_pois.",
    "5. Create a 250-meter buffer around fuel_pois and name it fuel_buffer.",
    "6. Buffer the stadium_pois by 300 meters and save the output as stadium_buffer.",
    "7. Do the same for bus_pois with a 300-meter buffer to get bus_buffer.",
    "8. Merge fuel_buffer and stadium_buffer into a single layer called union_fs.",
    "9. Combine union_fs with bus_buffer to create the total_conflict_zone.",
    "10. Now buffer hospital_pois by 600 meters to define the hospital_zone.",
    "11. Clip the hospital_zone using total_conflict_zone to isolate overlapping areas—name the result hospital_conflict_clip.",
    "12. Finally, export hospital_conflict_clip for further analysis or mapping."
  ],
  "tools": [
    "SelectLayerByAttribute",
    "Buffer_analysis",
    "Union_analysis",
    "Clip_analysis",
    "CopyFeatures_management"
  ],
  "key_layers": [
    "POIs=C:/Users/90608/Desktop/input/gis_osm_pois_free_1.shp",
    "Transport=C:/Users/90608/Desktop/input/gis_osm_transport_free_1.shp",
    "Traffic=C:/Users/90608/Desktop/input/gis_osm_traffic_free_1.shp"
  ],
  "parameters": {
    "fuel_buffer_distance": "250 meters",
    "stadium_buffer_distance": "300 meters",
    "bus_buffer_distance": "300 meters",
    "hospital_buffer_distance": "600 meters"
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

