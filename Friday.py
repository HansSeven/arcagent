from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph, START
import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.tools import tool
import functools
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode
from typing import Literal
from langchain_ollama import ChatOllama         # 必须用ChatOllama，因为只有ChatOllama更新了bind_tools功能，可以开启jason模式，非常非常好
import arcpy
import os
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

"""                      外置函数栏                                """

#使用函数

#函数1 生成缓冲区
def create_buffer(input_feature, output_folder, buffer_distance, buffer_name, dissolve_option="NONE"):
    """
    生成缓冲区，并将结果保存到指定文件夹中。

    参数：
    - input_feature (str)：输入要素的路径（如 shapefile 或要素类）。
    - output_folder (str)：用于存放生成的缓冲区结果的文件夹路径,如"C:/Users/90608/Desktop/b"。
    - buffer_distance (str)：缓冲距离，格式为 "<数值> <单位>"，例如 "100 Meters"。
    - buffer_name (str)：输出缓冲区文件的名称（包括扩展名，如 .shp）。
    - dissolve_option (str, 可选)：缓冲区溶解选项，默认为 "NONE"（不溶解），
      也可以设置为 "ALL"（所有缓冲区合并成一个）或其它字段名称。

    返回值：
    - str：生成的缓冲区文件的完整路径。
    """
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 构建完整的输出文件路径
    output_path = os.path.join(output_folder, buffer_name)

    # 设置允许覆盖已有输出
    arcpy.env.overwriteOutput = True

    # 调用缓冲区分析工具
    arcpy.Buffer_analysis(
        in_features=input_feature,
        out_feature_class=output_path,
        buffer_distance_or_field=buffer_distance,
        line_side="FULL",  # 对线要素，生成两侧缓冲区
        line_end_type="ROUND",  # 缓冲边缘为圆形
        dissolve_option=dissolve_option,  # 缓冲区溶解选项
        dissolve_field=None,  # 若不溶解则不指定字段
        method="PLANAR"  # 采用平面法计算缓冲区
    )

    return output_path
#2 裁剪函数
def simple_clip(input_fc, clip_fc, output_fc):
    """
    最简版裁剪函数，只需三个参数即可使用：

    参数：
    - input_fc (str)：要裁剪的要素路径（例如 "C:/data/landuse.shp"）。
    - clip_fc  (str)：裁剪范围要素路径（例如 "C:/data/clip_area.shp"）。
    - output_fc(str)：裁剪结果的输出路径（例如 "C:/data/landuse_clipped.shp"）。

    返回：
    - str：输出要素的路径。
    """
    # 允许覆盖已有结果
    arcpy.env.overwriteOutput = True

    # 调用最简裁剪工具：只需三个必选参数
    arcpy.Clip_analysis(input_fc, clip_fc, output_fc)

    return output_fc

# #3 图层类 创建图层（图层系操作）
# def create_layer(input_path, layer_name):
#     """
#     创建要素图层，用于后续选择操作。
#
#     参数：
#     - input_path (str)：输入要素类或 shapefile 的完整路径，例如 "C:/data/residents.shp"。
#     - layer_name (str)：创建的图层名称，用于后续引用，例如 "residents_lyr"。
#
#     返回值：
#     - str：图层名称（字符串），用于后续函数调用中的图层参数。
#     """
#     arcpy.MakeFeatureLayer_management(in_features=input_path, out_layer=layer_name)
#     return layer_name

#4 图层类 根据位置选择
def select_by_location_file(input_target, input_overlap, output_path, spatial_relation="INTERSECT"):
    """
    根据空间位置从输入文件中选择与另一个文件相交的要素，并输出为新文件。

    参数：
    - input_target (str)：目标要素类路径（如 C:/data/residents.shp）。
    - input_overlap (str)：用于进行空间判断的参考要素类路径（如:C:/data/greenspace_buffer.shp）。
    - output_path (str)：输出文件路径（包含如C:/data/residents_in_greenspace.shp）。
    - spatial_relation (str)：空间关系类型，默认是 "INTERSECT"，也可为 "WITHIN"、"CONTAINS" 等。

    返回值：
    - str：输出文件的完整路径。
    """
    # 创建临时图层
    arcpy.MakeFeatureLayer_management(input_target, "target_lyr")
    arcpy.MakeFeatureLayer_management(input_overlap, "overlap_lyr")

    # 执行空间选择
    arcpy.SelectLayerByLocation_management(
        in_layer="target_lyr",
        overlap_type=spatial_relation,
        select_features="overlap_lyr",
        selection_type="NEW_SELECTION"
    )

    # 将选中的要素导出为新文件
    arcpy.CopyFeatures_management("target_lyr", output_path)

    # 清理图层
    arcpy.Delete_management("target_lyr")
    arcpy.Delete_management("overlap_lyr")

    return output_path

# #5 图层类 导出图层中选择的要素
# def export_selected_features(layer_name, output_folder, output_name):
#     """
#     将当前图层中被选中的要素导出为新的要素类或 shapefile。
#
#     参数：
#     - layer_name (str)：图层名称，已进行选择的图层，例如 "residents_lyr"。
#     - output_folder (str)：输出文件夹路径，例如 "C:/output/"。
#     - output_name (str)：导出的文件名，例如 "selected_residents.shp"。
#
#     返回值：
#     - str：导出文件的完整路径。
#     """
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
#
#     output_path = os.path.join(output_folder, output_name)
#     arcpy.env.overwriteOutput = True
#
#     arcpy.FeatureClassToFeatureClass_conversion(
#         in_features=layer_name,
#         out_path=output_folder,
#         out_name=output_name
#     )
#     return output_path


#6图层类Select By Attributes功能
def select_by_field_value(layer_name, field_name, field_value):
    """
    通用字段筛选函数：根据指定字段及其值筛选图层中的要素。

    参数：
    - layer_name (str)：输入图层名称（如 "restaurant_layer"）。
    - field_name (str)：字段名称（如 "fclass"）。
    - field_value (str)：字段目标值（如 "restaurant"）。

    返回：
    - str：原图层名称，筛选状态已更新，可用于导出或分析。
    """
    expression = f"{field_name} = '{field_value}'"
    arcpy.SelectLayerByAttribute_management(layer_name, "NEW_SELECTION", expression)
    return layer_name

#7 Project地理处理工具
def project_to_metric(input_fc, output_fc, epsg_code=3857):
    """
    将输入要素类投影为指定的米单位坐标系（默认 EPSG:3857，Web Mercator）。

    参数：
    - input_fc (str)：输入要素类路径（如 "C:/output/restaurant_selected.shp"）。
    - output_fc (str)：投影后的输出路径（如 "C:/output/restaurant_projected.shp"）。
    - epsg_code (int)：EPSG 投影代码（默认 3857，可设为如 32650 表示 UTM 区域）。

    返回：
    - str：投影后 shapefile 的路径。
    """
    arcpy.env.overwriteOutput = True
    spatial_ref = arcpy.SpatialReference(epsg_code)
    arcpy.Project_management(input_fc, output_fc, spatial_ref)
    return output_fc

#8 Spatial Analyst 工具箱里的 Kernel Density工具
def kernel_density(input_point_fc, population_field, output_raster_path, cell_size=10, search_radius="1000"):
    """
    对投影后的点要素执行核密度分析，输出栅格热力图。

    参数：
    - input_point_fc (str)：输入点要素类路径（如 "C:/output/restaurant_projected.shp"），必须为投影坐标系，单位为米。
    - population_field (str)：用于作为权重的字段名（如 "NONE" 表示均等权重）。
    - output_raster_path (str)：输出栅格路径（如 "C:/output/restaurant_density.img"）。
    - cell_size (int)：输出栅格像元大小（单位为米）。
    - search_radius (str)：核密度分析的搜索半径（单位为米，如 "1000"）。

    返回：
    - str：输出的核密度分析栅格路径。
    """
    arcpy.env.overwriteOutput = True
    arcpy.sa.KernelDensity(
        in_features=input_point_fc,
        population_field=population_field,
        cell_size=cell_size,
        search_radius=search_radius,
        area_unit_scale_factor="SQUARE_KILOMETERS"
    ).save(output_raster_path)
    return output_raster_path

#9spatial_join函数
def spatial_join(target_fc, join_fc, output_fc,
                 join_operation="JOIN_ONE_TO_MANY",
                 join_type="KEEP_COMMON",
                 match_option="INTERSECT"):
    """
    空间连接函数（通用版）：支持任意要素类型组合的空间聚合。

    参数：
    - target_fc (str)：目标要素路径，例如 "C:/data/roads_buffer.shp"。
    - join_fc (str)：连接要素路径，例如 "C:/data/restaurant_points.shp"。
    - output_fc (str)：输出要素路径，例如 "C:/output/buffer_join_result.shp"。
    - join_operation (str)：连接操作，默认 "JOIN_ONE_TO_MANY"。
    - join_type (str)：保留方式，默认 "KEEP_COMMON"（仅保留有匹配关系的要素）。
    - match_option (str)：空间匹配关系类型，默认 "INTERSECT"，还可设为 "CONTAINS"、"WITHIN"、"CLOSEST" 等。

    返回：
    - str：输出连接结果的路径。

    功能说明：该函数根据空间关系将连接图层的属性附加到目标图层上，
    支持任意组合：点对面、线对面、面对点、面对面、点对点等。
    输出图层会自动包含连接图层的所有属性字段，并附加 Join_Count(当前join要素命中了多少个target要素)、TARGET_FID, 等辅助字段，
    可直接用于后续的分组统计或类型分析。
    """
    arcpy.env.overwriteOutput = True
    arcpy.SpatialJoin_analysis(
        target_features=target_fc,
        join_features=join_fc,
        out_feature_class=output_fc,
        join_operation=join_operation,
        join_type=join_type,
        match_option=match_option
    )
    return output_fc

#10 summary_statistics函数
def summary_statistics(input_fc, statistics_field, output_table,case_field="TARGET_FID"):
    """
    对空间连接后的结果执行字段分组统计，输出每个区域中目标要素的数量或其他统计信息。

    参数：
    - input_fc (str)：输入要素类路径，例如 "C:/output/buffer_join_result.shp"。
    - statistics_field (str)：要统计的字段，例如 "osm_id"（唯一标识字段）。
    - output_table (str)：输出统计表路径，例如 "C:/output/statistics_result.dbf"。
    - case_field (str)：分组字段，例如 "TARGET_FID" 或区域 ID。
    返回：
    - str：输出统计表路径。

    功能说明：按 case_field 分组，对 statistics_field 执行 COUNT 统计，
    可用于计算每个区域内落入的点数、道路段数、面数量等。
    """
    arcpy.env.overwriteOutput = True
    arcpy.Statistics_analysis(
        in_table=input_fc,
        out_table=output_table,
        statistics_fields=[[statistics_field, "COUNT"]],
        case_field=case_field
    )
    return output_table

#11 文件层面的 select by field
def select_by_field_value_file(input_layer, field_name, field_value, output_fc):
    """
    按字段值选择要素，并导出结果。

    参数：
    - input_layer (str)：输入图层路径，例如 "C:/data/osm_points.shp"。
    - field_name (str)：字段名，例如 "fclass"。
    - field_value (str)：要筛选的字段值，例如 "hospital"。
    - output_fc (str)：输出筛选结果路径，例如 "C:/output/hospitals.shp"。

    返回：
    - str：输出路径。
    """
    arcpy.env.overwriteOutput = True
    where_clause = f"{field_name} = '{field_value}'"
    layer_name = "temp_layer"
    arcpy.MakeFeatureLayer_management(input_layer, layer_name)
    arcpy.SelectLayerByAttribute_management(layer_name, "NEW_SELECTION", where_clause)
    arcpy.CopyFeatures_management(layer_name, output_fc)
    return output_fc

#12最近点距离表
def generate_near_table(in_points, near_points, out_table, search_radius="1000 Meters", location="LOCATION", angle="NO_ANGLE"):
    """
    生成最近点距离表（如：每所学校到最近医院）。

    参数：
    - in_points (str)：输入起始点图层路径，例如 "C:/data/schools.shp"。
    - near_points (str)：目标点图层路径，例如 "C:/data/hospitals.shp"。
    - out_table (str)：输出表格路径，例如 "C:/output/school_nearest_hospital.dbf"。
    - search_radius (str, 可选)：搜索半径，例如 "1000 Meters"。
    - location (str, 可选)：是否输出坐标信息，默认 "LOCATION"。
    - angle (str, 可选)：是否输出方向角，默认 "NO_ANGLE"。

    返回：
    - str：输出最近距离表路径。
    """
    arcpy.env.overwriteOutput = True
    arcpy.analysis.GenerateNearTable(
        in_features=in_points,
        near_features=near_points,
        out_table=out_table,
        search_radius=search_radius,
        location=location,
        angle=angle,
        closest="CLOSEST",
        closest_count=1
    )
    return out_table

#13表格导出
def table_to_table(input_table, output_folder, output_name):
    """
    将表格导出为独立文件，适用于分析结果保存。

    参数：
    - input_table (str)：输入表格路径，例如 "C:/output/school_nearest_hospital.dbf"。
    - output_folder (str)：输出文件夹路径，例如 "C:/output"。
    - output_name (str)：输出表名称，例如 "near_table_result.csv"。

    返回：
    - str：导出表格的完整路径。

    功能说明：
    用于将分析工具（如 GenerateNearTable、SummaryStatistics）生成的结果表
    落地保存为独立的结构化表格文件，便于导出、查看和进一步分析。
    """
    arcpy.env.overwriteOutput = True
    output_path = os.path.join(output_folder, output_name)
    arcpy.conversion.TableToTable(
        in_rows=input_table,
        out_path=output_folder,
        out_name=output_name
    )
    return output_path

#14 多重缓冲区创建
def create_multiple_ring_buffers(input_fc, output_fc, distances, buffer_unit="Meters", dissolve_option="ALL"):
    """
    为点要素创建多个 concentric 缓冲区（多重服务圈）。

    参数：
    - input_fc (str)：输入点要素路径，例如 "C:/data/restaurant.shp"。
    - output_fc (str)：输出缓冲区路径，例如 "C:/output/restaurant_buffer.shp"。
    - distances (list[str])：缓冲距离列表，例如 ["500", "1000", "1500"]。
    - buffer_unit (str)：缓冲单位，默认 "Meters"。
    - dissolve_option (str)：缓冲合并方式，默认 "ALL"。

    返回：
    - str：输出文件路径。
    """
    arcpy.env.overwriteOutput = True
    distance_string = ";".join(distances)
    arcpy.analysis.MultipleRingBuffer(
        input_fc,
        output_fc,
        distance_string,
        buffer_unit,
        "Distance",
        dissolve_option
    )
    return output_fc

#15 erase
def erase_features(input_fc, erase_fc, output_fc):
    """
    用 erase_fc 图层对 input_fc 图层进行擦除，提取 input_fc 中不被 erase_fc 覆盖的部分。

    参数：
    - input_fc (str)：待擦除的输入要素类路径（如 "C:/data/residential.shp"）。
    - erase_fc (str)：用来擦除的要素类路径（如 "C:/data/park_buffer.shp"）。
    - output_fc (str)：输出要素类路径（如 "C:/output/residential_no_park.shp"）。

    返回：
    - str：输出要素类路径。
    """
    arcpy.analysis.Erase(in_features=input_fc,
                         erase_features=erase_fc,
                         out_feature_class=output_fc)
    return output_fc

#16 溶解
def dissolve_features(input_fc, output_fc, dissolve_field=None, multi_part="SINGLE_PART"):
    """
    将 input_fc 中按 dissolve_field 字段合并要素，或全图合并。

    参数：
    - input_fc (str)：输入要素类路径（如 "C:/data/park_buffer.shp"）。
    - output_fc (str)：输出要素类路径（如 "C:/output/park_merged.shp"）。
    - dissolve_field (list[str] or None)：按哪些字段合并，None 表示不按字段合并（如 ["CITY_NAME"]）。
    - multi_part (str)："SINGLE_PART" 或 "MULTI_PART"，合并后是否生成 multipart 要素。

    返回：
    - str：输出要素类路径。
    """
    arcpy.management.Dissolve(in_features=input_fc,
                              out_feature_class=output_fc,
                              dissolve_field=dissolve_field or [],
                              multi_part=multi_part)
    return output_fc

# 17Identity
def identity_features(input_fc, identity_fc, output_fc):
    """
    将 input_fc 与 identity_fc 执行 Identity 叠加，保留 input_fc 属性并继承 identity_fc 属性。

    参数：
    - input_fc (str)：要叠加的输入要素（如 "C:/data/residential.shp"）。
    - identity_fc (str)：用于叠加的要素（如 "C:/data/road_buffer.shp"）。
    - output_fc (str)：输出要素路径（如 "C:/output/resid_road_identity.shp"）。

    返回：
    - str：输出要素路径。
    """
    arcpy.analysis.Identity(in_features=input_fc,
                            identity_features=identity_fc,
                            out_feature_class=output_fc)
    return output_fc

#18 临近分析
def near_analysis(input_fc, near_fc, search_radius=None, location="NO_LOCATION", angle="NO_ANGLE", method="PLANAR"):
    """
    计算 input_fc 中每个要素到 near_fc 中最近要素的距离，可选半径限制。

    参数：
    - input_fc (str)：待测要素类（如 "C:/data/hospitals.shp"）。
    - near_fc (str)：参照要素类（如 "C:/data/road.shp"）。
    - search_radius (str or None)：搜索半径（如 "500 Meters"），None 表示不限制。
    - location (str)：是否将最近点坐标写入属性，"LOCATION" 或 "NO_LOCATION"。
    - angle (str)：是否写入角度，"ANGLE" 或 "NO_ANGLE"。
    - method (str)：距离计算方式，"PLANAR" 或 "GEODESIC"。

    返回：
    - str：input_fc 本身，属性表中新增 NEAR_DIST 等字段。
    """
    arcpy.analysis.Near(in_features=input_fc,
                        near_features=near_fc,
                        search_radius=search_radius or "",
                        location=location,
                        angle=angle,
                        method=method)
    return input_fc

#19分割要素
def split_features(input_fc, split_fc, output_folder, split_field=""):
    """
    按 split_fc 或 split_field 自动切割 input_fc，要么按边界图层批量输出，要么按属性字段分割。

    参数：
    - input_fc (str)：待切割要素类路径（如 "C:/data/roads.shp"）。
    - split_fc (str): 用于切割的要素类路径（如行政区边界 "C:/data/counties.shp"）。
    - output_folder (str)：输出文件夹（如 "C:/output/roads_by_county/"）。
    - split_field (str)：如果不使用 split_fc，可按 input_fc 中的字段分割（如 "CITY_NAME"），否则置空。

    返回：
    - None：将在 output_folder 中生成多个要素类文件。
    """
    arcpy.management.Split(in_features=input_fc,
                           split_features=split_fc,
                           output_workspace=output_folder,
                           split_field=split_field)
    # 无返回，文件已生成

#20要素转点
def feature_to_point(input_fc, output_fc, point_location="CENTROID"):
    """
    将多边形要素类 input_fc 转为代表点 output_fc，可选质心或内部点。

    参数：
    - input_fc (str)：输入面要素类（如 "C:/data/service_area.shp"）。
    - output_fc (str)：输出点要素类（如 "C:/output/service_area_centroids.shp"）。
    - point_location (str)："CENTROID"（几何质心）或 "INSIDE"（保证点落面内）。

    返回：
    - str：输出点要素类路径。
    """
    arcpy.management.FeatureToPoint(in_features=input_fc,
                                    out_feature_class=output_fc,
                                    point_location=point_location)
    return output_fc

#21 定点转为点
def feature_vertices_to_points(input_fc, output_fc, point_type="ALL"):
    """
    将线/面要素的顶点或端点导出为点。

    参数：
    - input_fc (str)：输入要素类（线或面），如 "C:/data/roads.shp"。
    - output_fc (str)：输出点要素类（如 "C:/output/road_vertices.shp"）。
    - point_type (str)："ALL"（所有顶点）、"START"（起点）、"END"（终点）、"MID"（中点）。

    返回：
    - str：输出点要素类路径。
    """
    arcpy.management.FeatureVerticesToPoints(in_features=input_fc,
                                             out_feature_class=output_fc,
                                             point_type=point_type)
    return output_fc

#22 边界要素转点
def feature_to_line(input_fc, output_fc):
    """
    将多边形要素边界或多要素集转成线要素。

    参数：
    - input_fc (str)：输入面要素类（如 "C:/data/park.shp"）。
    - output_fc (str)：输出线要素类（如 "C:/output/park_boundaries.shp"）。

    返回：
    - str：输出线要素类路径。
    """
    arcpy.management.FeatureToLine(in_features=input_fc,
                                   out_feature_class=output_fc)
    return output_fc

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
                "when use tool,you can only use the above tools,don't try to make up a tool."
                "When adding string parameters (e.g., file paths), make sure to escape special characters properly—\n"
                "especially backslashes in file addresses, such as Windows-style paths.\n"
                "When writing file paths, use forward slashes (/) instead of backslashes (\)ps,you can ask for the parameters from user\n"
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


"""                     工具定义部分                         """
"""1. Buffer"""
@tool
def Buffer_analysis(
        input_feature: Annotated[str, "The path to the input features to buffer (e.g., C:/data/roads.shp)"],
        output_folder: Annotated[str, "The folder where the buffer output will be saved (e.g., C:/Users/90608/Desktop/b)"],
        buffer_distance: Annotated[str, "The buffer distance, in the format '<value> <unit>' (e.g., '100 Meters')"],
        buffer_name: Annotated[str, "The filename for the buffer output, including extension (e.g., 'roads_buffer.shp')"],
        dissolve_option: Annotated[str, "Dissolve option: 'NONE' (default, no dissolve), 'ALL' (merge all buffers), or a field name"]
):
    """Buffer\n
    Creates buffer zones around input features at the specified distance.
    Output: a new feature class saved at the specified path (e.g., C:/Users/90608/Desktop/b/roads_buffer.shp)."""
    try:
        output_path = create_buffer(input_feature, output_folder, buffer_distance, buffer_name, dissolve_option)
    except BaseException as e:
        return f"Failed to execute Buffer. Error: {repr(e)}"
    return f"the output path is {output_path}."

"""2. Clip"""
@tool
def Clip_analysis(
        input_fc: Annotated[str, "The path to the input features to be clipped (e.g., C:/data/landuse.shp)"],
        clip_fc: Annotated[str, "The path to the clip feature that defines the clipping extent (e.g., C:/data/clip_area.shp)"],
        output_fc: Annotated[str, "The path to save the clipped output features (e.g., C:/data/landuse_clipped.shp)"]
):
    """Clip\n
    Extracts the portions of the input features that overlap the clip features and writes them to a new feature class.
    Output: a feature class saved at output_fc containing only the clipped features (e.g., C:/data/landuse_clipped.shp)."""
    try:
        output_path = simple_clip(input_fc, clip_fc, output_fc)
    except BaseException as e:
        return f"Failed to execute Clip. Error: {repr(e)}"
    return f"the output path is {output_path}."
"""3. Create Layer (Layer-level)"""
# @tool
# def arc_gis_pro_create_layer_layer_level(
#         input_path: Annotated[str, "The path to the input feature class or shapefile (e.g., C:/data/residents.shp)"],
#         layer_name: Annotated[str, "The name to assign to the created in-memory layer (e.g., 'residents_lyr')"]
# ):
#     """Create Layer (Layer-level)\n
#     A layer-level tool that loads a dataset into memory as a feature layer.
#     This allows subsequent tools (e.g., SelectLayerByAttribute, SelectLayerByLocation, CalculateField) to operate on the layer without immediately writing to disk.\n
#     Output: the name of the in-memory layer (e.g., 'residents_lyr'), which can be passed to other layer-level tools."""
#     try:
#         result = create_layer(input_path, layer_name)
#     except BaseException as e:
#         return f"Failed to execute Create Layer. Error: {repr(e)}"
#     return result
"""4. Select Layer By Location (Layer-level)"""
#@tool
# def arc_gis_pro_select_by_location_layer_level(
#         target_layer: Annotated[str, "The name of the layer to apply spatial selection on (e.g., 'residents_lyr')"],
#         overlap_layer: Annotated[str, "The name of the layer defining the spatial reference (e.g., 'greenspace_buffer')"],
#         spatial_relation: Annotated[str, "The spatial relationship type: 'INTERSECT' (default), 'WITHIN', 'CONTAINS', etc."]
# ):
#     """Select Layer By Location (Layer-level)\n
#     Selects features in the target layer based on their spatial relationship to features in another layer.\n
#     Output: the same layer (target_layer) with a new selection applied according to spatial_relation."""
#     try:
#         result = select_by_location(target_layer, overlap_layer, spatial_relation)
#     except BaseException as e:
#         return f"Failed to execute Select Layer By Location. Error: {repr(e)}"
#     return result
"""5. Export Selected Features (Layer-level)"""
# @tool
# def arc_gis_pro_export_selected_features_layer_level(
#         layer_name: Annotated[str, "The name of the feature layer with a selection applied (e.g., 'residents_lyr')"],
#         output_folder: Annotated[str, "The folder where the exported features will be saved (e.g., C:/output/)"],
#         output_name: Annotated[str, "The name of the output feature class or shapefile (e.g., 'selected_residents.shp')"]
# ):
#     """Export Selected Features (Layer-level)\n
#     Exports the currently selected features from an in-memory layer to a new feature class or shapefile.\n
#     Output: a new feature class saved at output_folder/output_name containing only the selected features."""
#     try:
#         result = export_selected_features(layer_name, output_folder, output_name)
#     except BaseException as e:
#         return f"Failed to execute Export Selected Features. Error: {repr(e)}"
#     return result
# """6. Select By Attribute (Layer-level)"""
# @tool
# def arc_gis_pro_select_by_field_value_layer_level(
#         layer_name: Annotated[str, "The name of the feature layer to query (e.g., 'restaurant_layer')"],
#         field_name: Annotated[str, "The attribute field to use in the query (e.g., 'fclass')"],
#         field_value: Annotated[str, "The value to match for selection (e.g., 'restaurant')"]
# ):
#     """Select By Attribute (Layer-level)\n
#     A layer-level tool that applies an attribute filter to an in-memory feature layer.
#     It updates the layer’s selection based on the given field_name = field_value expression.\n
#     Output: the same layer_name with the new selection applied."""
#     try:
#         result = select_by_field_value(layer_name, field_name, field_value)
#     except BaseException as e:
#         return f"Failed to execute Select By Attribute. Error: {repr(e)}"
#     return result
"""7. Project"""
@tool
def Project_management(
        input_fc: Annotated[str, "The path to the input feature class to be projected (e.g., C:/output/restaurant_selected.shp)"],
        output_fc: Annotated[str, "The path to save the projected feature class (e.g., C:/output/restaurant_projected.shp)"],
        epsg_code: Annotated[int, "The EPSG code of the target coordinate system (default 3857 for Web Mercator)"]
):
    """Project\n
    Reprojects the input feature class to a specified metric coordinate system.\n
    Output: a new feature class saved at output_fc in the given spatial reference (e.g., C:/output/restaurant_projected.shp)."""
    try:
        output_path = project_to_metric(input_fc, output_fc, epsg_code)
    except BaseException as e:
        return f"Failed to execute Project. Error: {repr(e)}"
    return f"the output path is {output_path}."

"""8. Kernel Density"""
@tool
def Kernel_Density(
        input_point_fc: Annotated[str, "The path to the input point feature class (projected in a metric coordinate system, e.g., C:/output/restaurant_projected.shp)"],
        population_field: Annotated[str, "The field used as weight for density calculation (e.g., 'NONE' for equal weight)"],
        output_raster_path: Annotated[str, "The path to save the output density raster (e.g., C:/output/restaurant_density.tif)"],
        cell_size: Annotated[int, "The cell size (in map units, e.g., meters) for the output raster"],
        search_radius: Annotated[str, "The search radius (in map units, e.g., '1000') for the kernel density calculation"]
):
    """Kernel Density\n
    Calculates a smoothly tapered density surface from point features using a kernel function.\n
    Output: a raster file saved at output_raster_path (e.g., C:/output/restaurant_density.tif)."""
    try:
        output_path = kernel_density(input_point_fc, population_field, output_raster_path, cell_size, search_radius)
    except BaseException as e:
        return f"Failed to execute Kernel Density. Error: {repr(e)}"
    return f"the output path is {output_path}."

"""9. 空间连接"""
@tool
def SpatialJoin_analysis(
        target_fc: Annotated[str, "The path to the feature class receiving joined attributes (e.g., C:/data/roads_buffer.shp)"],
        join_fc: Annotated[str, "The path to the feature class providing attributes to join (e.g., C:/data/restaurant_points.shp)"],
        output_fc: Annotated[str, "The path to save the spatial join result (e.g., C:/output/buffer_join_result.shp)"],
        join_operation: Annotated[str, "JOIN operation: 'JOIN_ONE_TO_ONE' or 'JOIN_ONE_TO_MANY' (default)."],
        join_type: Annotated[str, "Keep options: 'KEEP_ALL' or 'KEEP_COMMON' (default) for matched features."],
        match_option: Annotated[str, "Spatial relationship: 'INTERSECT' (default), 'CONTAINS', 'WITHIN', 'CLOSEST', etc."]
):
    """Spatial Join\n
    Appends attributes from join_fc to target_fc based on spatial relationships.\n
    Output: a new feature class saved at output_fc containing all target_fc features,
    joined with matching join_fc attributes and added fields like Join_Count and TARGET_FID."""
    try:
        result = spatial_join(target_fc, join_fc, output_fc, join_operation, join_type, match_option)
    except BaseException as e:
        return f"Failed to execute Spatial Join. Error: {repr(e)}"
    return f"the output path is {result}."

"""10. Summary Statistics"""
@tool
def SummaryStatistics(
        input_fc: Annotated[str, "The path to the input table or feature class to be summarized (e.g., C:/output/buffer_join_result.shp)"],
        statistics_field: Annotated[str, "The field to be counted (e.g., 'osm_id')"],
        output_table: Annotated[str, "The path to save the summary statistics table (e.g., C:/output/statistics_result.dbf)"],
        case_field: Annotated[str, "The field used to group records (e.g., 'TARGET_FID')"]
):
    """Summary Statistics\n
    Calculates summary statistics for a specified field, grouping by case_field.\n
    Output: a standalone table saved at output_table containing COUNT(statistics_field) per unique case_field (e.g., C:/output/statistics_result.dbf)."""
    try:
        result = summary_statistics(input_fc, statistics_field, output_table, case_field)
    except BaseException as e:
        return f"Failed to execute Summary Statistics. Error: {repr(e)}"
    return f"the output path is {result}."
"""11. Select By Field (File)"""
@tool
def SelectLayerByAttribute(
        input_layer: Annotated[str, "The path to the input feature class or shapefile (e.g., C:/data/osm_points.shp)"],
        field_name: Annotated[str, "The attribute field to query (e.g., 'fclass')"],
        field_value: Annotated[str, "The value to select in the field (e.g., 'hospital')"],
        output_fc: Annotated[str, "The path to save the selected features (e.g., C:/output/hospitals.shp)"]
):
    """Select By Field\n
    Extracts features from the input layer matching a specific attribute value and writes them to a new feature class.\n
    Output: a feature class saved at output_fc containing only features where field_name = field_value."""
    try:
        result = select_by_field_value_file(input_layer, field_name, field_value, output_fc)
    except BaseException as e:
        return f"Failed to execute Select By Field. Error: {repr(e)}"
    return f"the output path is {result}."
"""12. Generate Near Table"""
@tool
def GenerateNearTable_analysis(
        in_points: Annotated[str, "The path to the input point features (e.g., C:/data/schools.shp)"],
        near_points: Annotated[str, "The path to the point features to search against (e.g., C:/data/hospitals.shp)"],
        out_table: Annotated[str, "The path to save the near table (e.g., C:/output/school_nearest_hospital.dbf)"],
        search_radius: Annotated[str, "Maximum search radius (e.g., '1000 Meters'); leave empty for no limit"],
        location: Annotated[str, "Specify 'LOCATION' to add nearest point coordinates or 'NO_LOCATION' (default)"],
        angle: Annotated[str, "Specify 'ANGLE' to add direction angle or 'NO_ANGLE' (default)"]
):
    """Generate Near Table\n
    Creates a table of the nearest distances between in_points and near_points.\n
    Output: a table saved at out_table containing NEAR_DIST, NEAR_FID, and optional NEAR_X/NEAR_Y and NEAR_ANGLE fields."""
    try:
        result = generate_near_table(in_points, near_points, out_table, search_radius, location, angle)
    except BaseException as e:
        return f"Failed to execute Generate Near Table. Error: {repr(e)}"
    return f"the output path is {result}."
"""13. Table To Table"""
@tool
def TableToTable_conversion(
        input_table: Annotated[str, "The path to the input table to be exported (e.g., C:/output/school_nearest_hospital.dbf)"],
        output_folder: Annotated[str, "The folder where the output table will be saved (e.g., C:/output)"],
        output_name: Annotated[str, "The name of the exported table file (including extension, e.g., near_table_result.csv)"]
):
    """Table To Table\n
    Exports an input table or table view to a new standalone table in the specified workspace.\n
    Output: a table saved at the combined path output_folder/output_name (e.g., C:/output/near_table_result.csv)."""
    try:
        result = table_to_table(input_table, output_folder, output_name)
    except BaseException as e:
        return f"Failed to execute Table To Table. Error: {repr(e)}"
    return f"the output path is {result}."
"""14. Multiple Ring Buffer"""
@tool
def MultipleRingBuffer_analysis(
        input_fc: Annotated[str, "The path to the input point features (e.g., C:/data/restaurant.shp)"],
        output_fc: Annotated[str, "The path to save the multiple ring buffer output (e.g., C:/output/restaurant_buffer.shp)"],
        distances: Annotated[str, "Semicolon-separated list of distances for rings (e.g., '500;1000;1500')"],
        buffer_unit: Annotated[str, "The unit for buffer distances (e.g., 'Meters')"],
        dissolve_option: Annotated[str, "Dissolve option: 'ALL' to merge rings or 'NONE' to keep separate"]
):
    """Multiple Ring Buffer\n
    Creates concentric buffer rings around input points for the specified distances.\n
    Output: a feature class saved at output_fc containing the buffer rings (e.g., C:/output/restaurant_buffer.shp)."""
    try:
        dist_list = distances.split(";")
        result = create_multiple_ring_buffers(input_fc, output_fc, dist_list, buffer_unit, dissolve_option)
    except BaseException as e:
        return f"Failed to execute Multiple Ring Buffer. Error: {repr(e)}"
    return f"the output path is {result}."
"""15. Erase"""
@tool
def Erase_analysis(
        input_fc: Annotated[str, "The path to the input features to be erased (e.g., C:/data/residential.shp)"],
        erase_fc: Annotated[str, "The path to the features defining areas to remove (e.g., C:/data/park_buffer.shp)"],
        output_fc: Annotated[str, "The path to save the erased output features (e.g., C:/output/residential_no_park.shp)"]
):
    """Erase\n
    Calculates the geometric difference between input_fc and erase_fc, preserving only the portions of input_fc that fall outside erase_fc.\n
    Output: a feature class saved at output_fc containing only the non-overlapping areas (e.g., C:/output/residential_no_park.shp)."""
    try:
        result = erase_features(input_fc, erase_fc, output_fc)
    except BaseException as e:
        return f"Failed to execute Erase. Error: {repr(e)}"
    return f"the output path is {result}."
"""16. Dissolve"""
@tool
def Dissolve_management(
        input_fc: Annotated[str, "The path to the input features to be dissolved (e.g., C:/data/park_buffer.shp)"],
        output_fc: Annotated[str, "The path to save the dissolved output features (e.g., C:/output/park_merged.shp)"],
        dissolve_field: Annotated[str, "Comma-separated field names to dissolve by (e.g., 'CITY_NAME'); leave empty for full dissolve."],
        multi_part: Annotated[str, "'SINGLE_PART' or 'MULTI_PART' to specify output feature type (default 'SINGLE_PART')."]
):
    """Dissolve\n
    Merges features based on common attribute values or combines all features when no fields are specified.\n
    Output: a feature class saved at output_fc containing the dissolved results (e.g., C:/output/park_merged.shp)."""
    try:
        fields = dissolve_field.split(",") if dissolve_field else []
        result = dissolve_features(input_fc, output_fc, fields, multi_part)
    except BaseException as e:
        return f"Failed to execute Dissolve. Error: {repr(e)}"
    return f"the output path is {result}."
"""17. Identity"""
@tool
def Identity_analysis(
        input_fc: Annotated[str, "The path to the input features to overlay (e.g., C:/data/residential.shp)"],
        identity_fc: Annotated[str, "The path to the features whose attributes will be joined (e.g., C:/data/road_buffer.shp)"],
        output_fc: Annotated[str, "The path to save the identity result features (e.g., C:/output/resid_road_identity.shp)"]
):
    """Identity\n
    Overlays input_fc with identity_fc, preserving input_fc’s attributes and appending identity_fc’s attributes where they overlap.\n
    Output: a new feature class saved at output_fc containing the combined geometries and attributes (e.g., C:/output/resid_road_identity.shp)."""
    try:
        result = identity_features(input_fc, identity_fc, output_fc)
    except BaseException as e:
        return f"Failed to execute Identity. Error: {repr(e)}"
    return f"the output path is {result}."

"""18. Near"""
@tool
def Near_analysis(
        input_fc: Annotated[str, "The path to the features for which nearest distances will be calculated (e.g., C:/data/hospitals.shp)"],
        near_fc: Annotated[str, "The path to the features to search for nearest neighbors (e.g., C:/data/roads.shp)"],
        search_radius: Annotated[str, "Optional maximum search radius (e.g., '500 Meters'); leave empty for no limit"],
        location: Annotated[str, "Specify 'LOCATION' to add nearest point coordinates or 'NO_LOCATION' (default)"],
        angle: Annotated[str, "Specify 'ANGLE' to add direction angle or 'NO_ANGLE' (default)"],
        method: Annotated[str, "Distance calculation method: 'PLANAR' (flat earth) or 'GEODESIC' (earth curvature)"]
):
    """Near\n
    Calculates the distance from each feature in input_fc to the nearest feature in near_fc and writes the results into input_fc’s attribute table.\n
    Output: input_fc is updated with fields NEAR_DIST, NEAR_FID, and optionally NEAR_X/NEAR_Y and NEAR_ANGLE."""
    try:
        result = near_analysis(
            input_fc=input_fc,
            near_fc=near_fc,
            search_radius=search_radius,
            location=location,
            angle=angle,
            method=method
        )
    except BaseException as e:
        return f"Failed to execute Near. Error: {repr(e)}"
    return f"The feature class '{result}' has been updated with nearest-distance fields."
"""19. Split"""
@tool
def Split_analysis(
        input_fc: Annotated[str, "The path to the input feature class to split (e.g., C:/data/roads.shp)"],
        split_fc: Annotated[str, "The path to the feature class defining split boundaries (e.g., C:/data/counties.shp)"],
        output_folder: Annotated[str, "The folder where the split feature classes will be saved (e.g., C:/output/roads_by_county/)"],
        split_field: Annotated[str, "The attribute field to split by if split_fc is empty (e.g., 'CITY_NAME'); leave empty to use split_fc"]
):
    """Split\n
    Splits input_fc into multiple feature classes based on split_fc boundaries or split_field values.\n
    Output: multiple feature class files created in output_folder."""
    try:
        split_features(input_fc, split_fc, output_folder, split_field)
    except BaseException as e:
        return f"Failed to execute Split. Error: {repr(e)}"
    return f"Features have been split into {output_folder}."
"""20. Feature To Point"""
@tool
def FeatureToPoint_management(
        input_fc: Annotated[str, "The path to the input polygon feature class (e.g., C:/data/service_area.shp)"],
        output_fc: Annotated[str, "The path to save the output point feature class (e.g., C:/output/service_area_centroids.shp)"],
        point_location: Annotated[str, "Specifies point placement: 'CENTROID' for geometric center or 'INSIDE' to ensure point falls within the polygon (default 'CENTROID')"]
):
    """Feature To Point\n
    Converts polygon features into point features by placing a point at each polygon’s centroid or inside position.\n
    Output: a new point feature class saved at output_fc (e.g., C:/output/service_area_centroids.shp)."""
    try:
        result = feature_to_point(input_fc, output_fc, point_location)
    except BaseException as e:
        return f"Failed to execute Feature To Point. Error: {repr(e)}"
    return f"the output path is {result}."
"""21. Feature Vertices To Points"""
@tool
def FeatureVerticesToPoints_management(
        input_fc: Annotated[str, "The path to the input line or polygon feature class (e.g., C:/data/roads.shp)"],
        output_fc: Annotated[str, "The path to save the output point feature class (e.g., C:/output/road_vertices.shp)"],
        point_type: Annotated[str, "The type of vertices to export: 'ALL' (all vertices), 'START', 'END', or 'MID'"]
):
    """Feature Vertices To Points\n
    Converts each specified vertex of line or polygon features into point features.\n
    Output: a point feature class saved at output_fc containing the requested vertices."""
    try:
        result = feature_vertices_to_points(input_fc, output_fc, point_type)
    except BaseException as e:
        return f"Failed to execute Feature Vertices To Points. Error: {repr(e)}"
    return f"the output path is {result}."
"""22. Feature To Line"""
@tool
def FeatureToLine_management(
        input_fc: Annotated[str, "The path to the input polygon feature class (e.g., C:/data/park.shp)"],
        output_fc: Annotated[str, "The path to save the output line feature class (e.g., C:/output/park_boundaries.shp)"]
):
    """Feature To Line\n
    Converts polygon boundaries or multipart features into line features.\n
    Output: a line feature class saved at output_fc (e.g., C:/output/park_boundaries.shp)."""
    try:
        result = feature_to_line(input_fc, output_fc)
    except BaseException as e:
        return f"Failed to execute Feature To Line. Error: {repr(e)}"
    return f"the output path is {result}."

tools = ["Buffer_analysis", "Clip_analysis", "Project_management", "Kernel_Density", "SpatialJoin_analysis",
             "SummaryStatistics", "SelectLayerByAttribute", "GenerateNearTable_analysis", "TableToTable_conversion",
             "MultipleRingBuffer_analysis", "Erase_analysis", "Dissolve_management", "Identity_analysis", "Near_analysis",
             "Split_analysis", "FeatureToPoint_management", "FeatureVerticesToPoints_management", "FeatureToLine_management"]
"""                                      提取代码tool                                          """


def extract_tool_names_from_json_message(messages):
    for msg in reversed(messages):
        if hasattr(msg, "content") and isinstance(msg.content, str):
            try:
                data = json.loads(msg.content)
                if isinstance(data, dict) and "tools" in data:
                    return data["tools"]
            except json.JSONDecodeError:
                continue
    return []

"""                                                           向量数据库构建                                                    """

# 你的 tool_docs 格式
tool_docs = [
    ("Buffer_analysis", "Create buffer polygons around input features at a specified distance."),
    ("Clip_analysis", "Extract input features that fall within the boundary of clip features."),
    ("Project_management", "Transform spatial data from one coordinate system to another."),
    ("Kernel_Density", "Generate a raster surface showing the density of features in a neighborhood."),
    ("SpatialJoin_analysis", "Join attributes from one feature layer to another based on spatial relationship."),
    ("SummaryStatistics", "Summarize field values by group, producing a standalone table."),
    ("SelectLayerByAttribute", "Select features from a layer based on attribute query expressions."),
    ("GenerateNearTable_analysis", "Create a table recording the distance to nearest features."),
    ("TableToTable_conversion", "Export a table from one format or location to another."),
    ("MultipleRingBuffer_analysis", "Create multiple concentric buffer rings around features."),
    ("Erase_analysis", "Remove areas of input features that overlap with erase features."),
    ("Dissolve_management", "Aggregate features based on a common attribute to form larger units."),
    ("Identity_analysis", "Overlay two layers and append attributes of identity features to input features."),
    ("Near_analysis", "Calculate distance from each feature to the nearest feature in another layer."),
    ("Split_analysis", "Split input features into multiple outputs based on boundaries or attribute values."),
    ("FeatureToPoint_management", "Create points at the centroid or inside location of polygon features."),
    ("FeatureVerticesToPoints_management", "Convert feature vertices into individual point features."),
    ("FeatureToLine_management", "Convert input polygons or multipart features into line features.")
]

# 1. 将每个工具包装成 Document（含描述和元数据）
documents = [Document(page_content=desc, metadata={"tool_name": name}) for name, desc in tool_docs]

# 2. 加载 embedding 模型（可替换为 HuggingFaceEmbeddings 等）
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")

# 3. 构建向量库
vectorstore = FAISS.from_documents(documents, embedding_model)

"""                                          匹配代码                                           """
def match_tool_names_with_rag(model_tool_names, vectorstore, k=1):
    matched_tool_names = []
    for query in model_tool_names:
        results = vectorstore.similarity_search(query, k=k)
        if results:
            matched_tool_names.append(results[0].metadata["tool_name"])
        else:
            print(f"[WARN] No match found for '{query}'")
    return matched_tool_names


"""                                         Tool_RAG_Node                                       """

def tool_rag_bind_node(state, llm, vectorstore, tool_pool, system_message, name="tool_binder"):
    """
    Node: 提取工具名 → 向量匹配 → 构建绑定 agent → 写入 state 供 analyzer 使用
    """
    # Step 1: 提取工具名
    model_tools = extract_tool_names_from_json_message(state["messages"])
    if not model_tools:
        print("[WARN] No tool names extracted from messages.")
        return {
            "messages": [AIMessage(content=json.dumps({"matched_tools": []}), name=name)],
            "sender": name,
            "analyzer_agent": None
        }

    # Step 2: RAG 匹配真实工具名
    matched_names = match_tool_names_with_rag(model_tools, vectorstore)
    if not matched_names:
        print(f"[WARN] No matches found for extracted tools: {model_tools}")

    # Step 3: 从工具池中选取定义
    selected_tools = [tool for tool in tool_pool if tool.name in matched_names]

    # Step 4: 创建绑定后的 agent
    analyzer_agent = create_agent(llm, selected_tools, system_message)

    # Step 5: 返回新的状态，供 analyzer 节点使用
    return {
        "messages": [AIMessage(content=json.dumps({"matched_tools": matched_names}), name=name)],
        "sender": name,
        "analyzer_agent": analyzer_agent
    }


"""                    框架主体                                       """

llm = ChatOllama(model="llama3.2")
analyze_agent = create_agent(                                              #因为是json不会有finish
    llm,
    tools,
    system_message=("Use the provided tools to complete the assigned task.\n"
    "You are the tool caller. All you can do is invoke the tool,you should not code or make up anything."
    "From now on, your workflows must depend heavily on these tools. Pay careful attention to \n"
    "pass the file paths provided by the user, those generated during the workflow, or those you design as parameters to these tools."
                    ),
)

analyze_node = functools.partial(agent_node, agent=analyze_agent, name="analyzer")

chart_agent = create_agent(
    llm,
    tools,
    system_message="when you are called ,the work is finished ,just speak FINAL ANSWER to stop",
)
chart_node = functools.partial(agent_node, agent=chart_agent, name="chart_generator")
tool_node = ToolNode(tools)

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

workflow.add_node("analyzer", analyze_node)
workflow.add_node("chart_generator", chart_node)
workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "analyzer",
    router,
    {"continue": "chart_generator", "call_tool": "call_tool", "__end__": END},
)
workflow.add_conditional_edges(
    "chart_generator",
    router,
    {"continue": "analyzer", "call_tool": "call_tool", "__end__": END},
)

workflow.add_conditional_edges(                                      # 这个边是无向边，数据可在两侧流动
    "call_tool",
    # Each agent node updates the 'sender' field
    # the tool calling node does not, meaning
    # this edge will route back to the original agent
    # who invoked the tool
    lambda x: x["sender"],                                              # 数据流向router函数
    {
        "analyzer": "analyzer",                                      # 根据收到的message判断数据流向
        "chart_generator": "chart_generator",
    },
)
workflow.add_edge(START, "analyzer")                      # 本次示范只有一个流程，也就是开始会连接第几个流程，这里只连接一个
graph = workflow.compile()


# 调用该图
events = graph.stream(
    {
        "messages": [
            HumanMessage(
                content="can you help me,i have input shapefile path is C:/Users/90608/Desktop/b/hospital.shp"
                        "i need you to create a multiple_ring_buffer,output folder is C:/Users/90608/Desktop/b/"

            )
        ],
    },
    # Maximum number of steps to take in the graph
    {"recursion_limit": 150},
)
for s in events:
    print(s)
    print("----")