import os
import pandas as pd
import time
from openai import OpenAI

# 初始化 Qwen API
client = OpenAI(
    api_key="sk-3a717e8295f5420081aee2be05b35d1c",  # 替换为你的 key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 读取验证集CSV
df = pd.read_csv("C:/Users/90608/Desktop/LittlePaper/不公平对决数据集.csv")

# 初始化输出字段
df["deepseek_model_output"] = ""

# ✅ 保留原prompt，一字不动
def build_prompt(instruction):
    return f"""
You are a GIS task parser. Your job is to convert vague or oral-style natural language instructions into a structured geospatial task format.

Each instruction describes a real-world issue that requires spatial analysis (e.g., service gaps, environmental risk, access equity, zoning violations, etc.). Your job is to extract and structure the spatial thinking process needed to solve the problem.

For each instruction, generate the following fields:

1. task_type: Concise name of the GIS analytical goal (e.g., "Resilience Gap Evaluation", "Route Disruption Detection", etc.).
2. steps: A numbered list of GIS operations needed to solve the problem. Each step must specify the input layer, the tool or method used, any filters applied, and the output result name.
3. tools: A list of GIS tool names used in the steps (must be valid ArcGIS Pro tools if possible).
4. key_layers: A list of key data layers used (must include source data used in the analysis).
5. parameters: A dictionary of important analysis parameters (e.g., buffer_distance, time_threshold, zoning_category, etc.).

Constraints:
- Use only the layers and entities implied or logically required by the instruction.
- Do not fabricate layers unless they are necessary to fulfill the intent.
- Your logic should prioritize precise spatial reasoning, not just linguistic matching.
- Ensure the final structure can be used for actual geospatial processing.

Format your output in the following structure:
{{
  "task_type": "...",
  "steps": [
    "1. ...",
    "2. ...",
    ...
  ],
  "tools": ["...", "..."],
  "key_layers": ["...", "..."],
  "parameters": {{
    "..." : "..."
  }}
}}

### EXAMPLES

Instruction: Compare zoning data from 2014 and 2021 to locate reclassified land areas.

{{
  "task_type": "Change Detection Analysis",
  "steps": [
    "1. Use SelectLayerByAttribute to extract land polygons from zoning_2014.",
    "2. Use SelectLayerByAttribute to extract land polygons from zoning_2021.",
    "3. Run Intersect_analysis on the two layers to find overlapping zones.",
    "4. Run SelectLayerByAttribute on intersect result to filter reclassified parcels, output = changed_zones."
  ],
  "tools": ["SelectLayerByAttribute", "Intersect_analysis"],
  "key_layers": ["zoning_2014", "zoning_2021"],
  "parameters": {{}}
}}

Instruction: Evaluate whether low-income housing and high-end apartments are equally covered by nearby refueling services within 5 minutes of drive time.

{{
  "task_type": "Public Service Equity Evaluation",
  "steps": [
    "1. Use SelectLayerByAttribute to extract refill_station, output = stations.",
    "2. Use ServiceArea_analysis on stations with time_cutoff = 5 minutes, output = service_zone.",
    "3. Use SelectLayerByAttribute to extract low_income_housing, output = low_housing.",
    "4. Use SelectLayerByAttribute to extract high_end_apartments, output = high_apartments.",
    "5. Run Intersect_analysis between low_housing and service_zone, output = low_served.",
    "6. Run Intersect_analysis between high_apartments and service_zone, output = high_served.",
    "7. Run SummaryStatistics_analysis on low_served and high_served to compare coverage."
  ],
  "tools": [
    "SelectLayerByAttribute",
    "ServiceArea_analysis",
    "Intersect_analysis",
    "SummaryStatistics_analysis"
  ],
  "key_layers": [
    "refill_station",
    "low_income_housing",
    "high_end_apartment"
  ],
  "parameters": {{
    "time_cutoff": "5 minutes"
  }}
}}

### END OF EXAMPLES

Now parse the following instruction:
{instruction}
"""


# 遍历每条instruction调用Qwen并写入模型原始输出
for i, row in df.iterrows():
    try:
        prompt = build_prompt(row["instruction"])
        response = client.chat.completions.create(
            model="deepseek-r1",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content.strip()
        df.at[i, "deepseek_model_output"] = content

        print(f"Row {i} done.")
        time.sleep(1.2)
    except Exception as e:
        print(f"Row {i} failed: {e}")
        continue

# 保存结果到CSV
df.to_csv("C:/Users/90608/Desktop/LittlePaper/不公平对决数据集_deepseek输出_few-shot.csv", index=False, encoding="utf-8-sig")
