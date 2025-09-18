# tools/gis.py
from .base import register_tool

@register_tool(
    name="gis.buffer",
    description="Buffer a vector layer (plug your arcpy here)",
    input_schema={
        "type": "object",
        "properties": {
            "input_layer": {"type": "string"},
            "distance": {"type": "string"},
            "dissolve": {"type": "boolean", "default": False}
        },
        "required": ["input_layer", "distance"]
    }
)
def gis_buffer(args):
    input_layer = args["input_layer"]
    distance = args["distance"]
    dissolve = bool(args.get("dissolve", False))

    # —— 这里接入 arcpy.Buffer_analysis —— #
    # import arcpy
    # out_fc = f"{input_layer.rsplit('.',1)[0]}_buffer.shp"
    # dissolve_opt = "ALL" if dissolve else "NONE"
    # arcpy.Buffer_analysis(input_layer, out_fc, distance, dissolve_option=dissolve_opt)
    # return {
    #   "content": [
    #     {"type":"text","text":f"Buffered {input_layer} by {distance}, dissolve={dissolve_opt}"},
    #     {"type":"text","text":f"output: {out_fc}"}
    #   ],
    #   "is_error": False
    # }

    # 先返回假结果，跑通联调
    out_fc = f"{input_layer.rsplit('.',1)[0]}_buffer.shp"
    return {
        "content": [
            {"type": "text", "text": f"[FAKE] Buffered {input_layer} by {distance}, dissolve={dissolve}"},
            {"type": "text", "text": f"output: {out_fc}"}
        ],
        "is_error": False
    }
