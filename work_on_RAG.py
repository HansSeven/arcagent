import os
import arcpy

def build_shapefile_context_from_folder(folder: str) -> str:
    """扫描文件夹，生成适用于LLM的地理数据上下文描述（含完整路径）"""

    def list_shapefiles_with_path(folder: str) -> list:
        return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".shp")]

    def get_fields(input_fc: str) -> list:
        return [f.name for f in arcpy.ListFields(input_fc) if f.type not in ('OID', 'Geometry')]

    def get_unique_values(input_fc: str, field: str) -> list:
        with arcpy.da.SearchCursor(input_fc, [field]) as cursor:
            return list(set([row[0] for row in cursor if row[0] is not None]))

    def analyze_shapefile_metadata_with_path(shp_path: str) -> dict:
        meta = {}
        fields = get_fields(shp_path)
        for field in fields:
            try:
                values = get_unique_values(shp_path, field)
                meta[field] = values
            except:
                meta[field] = ["<无法读取>"]
        return meta

    # 开始生成 context 文本
    shapefiles = list_shapefiles_with_path(folder)
    context_lines = ["当前文件夹包含以下图层数据（包含完整路径、字段及其可能值）：", ""]

    for shp in shapefiles:
        try:
            metadata = analyze_shapefile_metadata_with_path(shp)
            context_lines.append(f"图层路径：{shp}")
            for field, values in metadata.items():
                value_list = "、".join(str(v) for v in values[:10])  # 最多展示10个
                context_lines.append(f"  - 字段：{field}，可能值包括：{value_list}")
            context_lines.append("")  # 空行分隔
        except Exception as e:
            context_lines.append(f"图层路径：{shp}（读取失败：{e}）\n")

    return "\n".join(context_lines)
print(build_shapefile_context_from_folder("D:/迅雷下载/beijing-latest-free.shp"))
"""
上面部分为感知生成context的代码
你拥有如下图层信息：

（这里就是刚刚那段自动生成的 context）

用户提问：请帮我分析居民点到最近医院的服务范围

请输出：
- 应该使用哪些图层？
- 是否需要字段筛选（如 type = 医院）？
- 应该执行哪些分析步骤（如 Buffer → SelectLayerByLocation → Export）

"""