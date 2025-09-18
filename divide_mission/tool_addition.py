import os
import arcpy
from langchain_core.tools import tool
from typing import Annotated,List

@tool
def DeleteField_management(
    input_shp: Annotated[str, "Full path to the input shapefile (e.g., 'C:/data/features.shp')"],
    fields_to_delete: Annotated[List[str], "List of field names to delete (e.g., ['field1', 'field2'])"]
) -> str:
    """DeleteField_tool
    Deletes specified attribute fields from a shapefile using arcpy.DeleteField_management.
    Output: The input shapefile will be modified in place."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.DeleteField_management(in_table=input_shp, drop_field=fields_to_delete)
        return f"Fields {fields_to_delete} successfully deleted from {input_shp}"
    except Exception as e:
        return f"Delete field failed. Error: {repr(e)}"

@tool
def AddField_management(
    input_shp: Annotated[str, "Full path to the input shapefile (e.g., 'C:/data/features.shp')"],
    field_name: Annotated[str, "The name of the new field to add (e.g., 'area_sqkm')"],
    field_type: Annotated[str, "Type of field (e.g., 'TEXT', 'DOUBLE', 'LONG')"]
) -> str:
    """AddField_tool
    Adds a new field to the attribute table of a shapefile using arcpy.AddField_management.
    Output: The input shapefile will be modified in place with the new field added."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.AddField_management(
            in_table=input_shp,
            field_name=field_name,
            field_type=field_type
        )
        return f"Field '{field_name}' of type '{field_type}' added to {input_shp}"
    except Exception as e:
        return f"Add field failed. Error: {repr(e)}"

@tool
def CalculateField_management(
    input_shp: Annotated[str, "Full path to the input shapefile (e.g., 'C:/data/features.shp')"],
    field_name: Annotated[str, "Name of the field to calculate (e.g., 'area')"],
    expression: Annotated[str, "Python expression for calculating the field (e.g., '!shape.area@SQMETERS!')"]
) -> str:
    """CalculateField_tool
    Calculates values for an existing field in a shapefile using a Python expression."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.CalculateField_management(
            in_table=input_shp,
            field=field_name,
            expression=expression,
            expression_type="PYTHON3"
        )
        return f"Field '{field_name}' calculated using expression: {expression}"
    except Exception as e:
        return f"Calculate field failed. Error: {repr(e)}"

@tool
def Merge_management(
    input_features: Annotated[List[str], "A list of full paths to shapefiles to merge (e.g., ['C:/a.shp', 'C:/b.shp'])"],
    output_shp: Annotated[str, "Full path to the output merged shapefile (e.g., 'C:/output/merged.shp')"]
) -> str:
    """Merge_tool
    Merges multiple shapefiles into a single output using arcpy.Merge_management."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.Merge_management(inputs=input_features, output=output_shp)
        return f"Merged {len(input_features)} shapefiles into: {output_shp}"
    except Exception as e:
        return f"Merge failed. Error: {repr(e)}"

@tool
def Append_management(
    input_features: Annotated[List[str], "List of full paths to input shapefiles to append (e.g., ['C:/data/new1.shp', 'C:/data/new2.shp'])"],
    target_feature: Annotated[str, "Full path to the target shapefile that will receive new features (e.g., 'C:/data/master.shp')"],
    schema_type: Annotated[str, "Schema type for append: 'TEST' (fields must match) or 'NO_TEST' (fields can differ)"]
) -> str:
    """Append_tool
    Appends multiple input shapefiles into an existing target shapefile using arcpy.Append_management."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.Append_management(inputs=input_features, target=target_feature, schema_type=schema_type)
        return f"Appended {len(input_features)} layers into {target_feature} using schema_type = {schema_type}"
    except Exception as e:
        return f"Append failed. Error: {repr(e)}"

@tool
def Delete_management(
    input_path: Annotated[str, "Full path to the feature class or shapefile to delete (e.g., 'C:/data/temp.shp')"]
) -> str:
    """Delete_tool
    Deletes the specified shapefile or feature class from disk using arcpy.Delete_management."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.Delete_management(in_data=input_path)
        return f"Deleted: {input_path}"
    except Exception as e:
        return f"Delete failed. Error: {repr(e)}"

@tool
def RepairGeometry_management(
    input_shp: Annotated[str, "Full path to the shapefile with geometry issues (e.g., 'C:/data/broken.shp')"]
) -> str:
    """RepairGeometry_tool
    Checks and fixes geometry errors in the input shapefile using arcpy.RepairGeometry_management."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.RepairGeometry_management(in_features=input_shp)
        return f"Geometry repaired for: {input_shp}"
    except Exception as e:
        return f"Repair geometry failed. Error: {repr(e)}"

@tool
def MultipartToSinglepart_management(
    input_shp: Annotated[str, "Full path to the multipart shapefile (e.g., 'C:/data/multipart.shp')"],
    output_shp: Annotated[str, "Full path to the output singlepart shapefile (e.g., 'C:/data/singlepart.shp')"]
) -> str:
    """MultipartToSinglepart_tool
    Converts multipart features into singlepart features using arcpy.MultipartToSinglepart_management."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.MultipartToSinglepart_management(in_features=input_shp, out_feature_class=output_shp)
        return f"Converted to singlepart features: {output_shp}"
    except Exception as e:
        return f"Multipart to singlepart failed. Error: {repr(e)}"

@tool
def AddGeometryAttributes_management(
    input_shp: Annotated[str, "Full path to the input shapefile (e.g., 'C:/data/features.shp')"],
    geometry_properties: Annotated[List[str], "List of geometry attributes to add (e.g., ['AREA', 'CENTROID_X', 'CENTROID_Y'])"]
) -> str:
    """AddGeometryAttributes_tool
    Adds geometric properties like area, length, or centroid coordinates to the input shapefile."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.AddGeometryAttributes_management(
            Input_Feature_Class=input_shp,
            Geometry_Properties=";".join(geometry_properties)
        )
        return f"Geometry attributes {geometry_properties} added to: {input_shp}"
    except Exception as e:
        return f"Add geometry attributes failed. Error: {repr(e)}"

@tool
def MakeFeatureLayer_management(
    input_shp: Annotated[str, "Full path to the input shapefile (e.g., 'C:/data/features.shp')"],
    layer_name: Annotated[str, "Name of the output layer (e.g., 'temp_layer')"]
) -> str:
    """MakeFeatureLayer_tool
    Creates a temporary in-memory layer from a shapefile, useful for selections and joins."""
    try:
        arcpy.MakeFeatureLayer_management(in_features=input_shp, out_layer=layer_name)
        return f"Feature layer '{layer_name}' created from: {input_shp}"
    except Exception as e:
        return f"Make feature layer failed. Error: {repr(e)}"

@tool
def AddJoin_management(
    layer_name: Annotated[str, "Name of the layer to join to (must already be a feature layer)"],
    layer_field: Annotated[str, "Field in the layer to base the join on (e.g., 'ID')"],
    table_path: Annotated[str, "Full path to the join table (e.g., 'C:/data/attributes.dbf')"],
    table_field: Annotated[str, "Field in the table to base the join on (e.g., 'ID')"]
) -> str:
    """AddJoin_tool
    Joins a table to a layer using a common field."""
    try:
        arcpy.AddJoin_management(layer_name, layer_field, table_path, table_field)
        return f"Join successful between {layer_name} and {table_path}"
    except Exception as e:
        return f"Add join failed. Error: {repr(e)}"

@tool
def RemoveJoin_management(
    layer_name: Annotated[str, "Name of the joined feature layer (e.g., 'joined_layer')"]
) -> str:
    """RemoveJoin_tool
    Removes all joins from the specified feature layer."""
    try:
        arcpy.RemoveJoin_management(layer_name)
        return f"Joins removed from: {layer_name}"
    except Exception as e:
        return f"Remove join failed. Error: {repr(e)}"

@tool
def PolygonToRaster_conversion(
    input_polygon: Annotated[str, "Full path to the polygon shapefile (e.g., 'C:/data/zones.shp')"],
    value_field: Annotated[str, "Field name used to assign raster values (e.g., 'zone_id')"],
    output_raster: Annotated[str, "Full path to the output raster (e.g., 'C:/data/zones.tif')"],
    cell_size: Annotated[float, "Cell size for the raster (e.g., 10.0)"]
) -> str:
    """PolygonToRaster_tool
    Converts polygon features to a raster dataset using specified value field."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.PolygonToRaster_conversion(
            in_features=input_polygon,
            value_field=value_field,
            out_rasterdataset=output_raster,
            cell_assignment="MAXIMUM_COMBINED_AREA",
            priority_field="NONE",
            cellsize=cell_size
        )
        return f"Raster created at: {output_raster}"
    except Exception as e:
        return f"Polygon to raster failed. Error: {repr(e)}"

@tool
def RasterToPolygon_conversion(
    input_raster: Annotated[str, "Full path to the input raster (e.g., 'C:/data/zones.tif')"],
    output_polygon: Annotated[str, "Full path to the output shapefile (e.g., 'C:/data/zones.shp')"],
    simplify: Annotated[bool, "Simplify polygons (True/False)"]
) -> str:
    """RasterToPolygon_tool
    Converts raster cells to polygon features, with optional simplification."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.RasterToPolygon_conversion(
            in_raster=input_raster,
            out_polygon_features=output_polygon,
            simplify= "SIMPLIFY" if simplify else "NO_SIMPLIFY",
            raster_field="Value"
        )
        return f"Converted raster to polygon: {output_polygon}"
    except Exception as e:
        return f"Raster to polygon failed. Error: {repr(e)}"

@tool
def FeatureClassToShapefile_conversion(
    input_fc_list: Annotated[List[str], "List of feature class paths (e.g., ['C:/gdb.gdb/roads', 'C:/gdb.gdb/lakes'])"],
    output_folder: Annotated[str, "Output folder path to save shapefiles (e.g., 'C:/output/')"]
) -> str:
    """FeatureClassToShapefile_tool
    Converts feature classes to individual shapefiles in the specified folder."""
    try:
        arcpy.FeatureClassToShapefile_conversion(
            Input_Features=input_fc_list,
            Output_Folder=output_folder
        )
        return f"Exported shapefiles to: {output_folder}"
    except Exception as e:
        return f"Feature class to shapefile failed. Error: {repr(e)}"

@tool
def MultipartToSinglepart_analysis(
    input_shp: Annotated[str, "Full path to multipart shapefile (e.g., 'C:/data/multi.shp')"],
    output_shp: Annotated[str, "Output singlepart shapefile path (e.g., 'C:/data/single.shp')"]
) -> str:
    """MultipartToSinglepart_analysis_tool
    Splits multipart features into singlepart features using analysis toolbox version."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.MultipartToSinglepart_analysis(input_shp, output_shp)
        return f"Output saved: {output_shp}"
    except Exception as e:
        return f"Multipart to singlepart (analysis) failed. Error: {repr(e)}"

@tool
def SelectLayerByLocation_management(
    target_layer: Annotated[str, "Name of the layer to select features from"],
    overlap_layer: Annotated[str, "Name of the reference layer used to find overlaps"],
    spatial_relation: Annotated[str, "Type of spatial relationship (e.g., 'INTERSECT', 'WITHIN')"]
) -> str:
    """SelectByLocation_tool
    Selects features in one layer based on spatial relationship to another layer."""
    try:
        arcpy.SelectLayerByLocation_management(
            in_layer=target_layer,
            overlap_type=spatial_relation,
            select_features=overlap_layer,
            selection_type="NEW_SELECTION"
        )
        return f"Selected features in {target_layer} using spatial relation: {spatial_relation}"
    except Exception as e:
        return f"Select by location failed. Error: {repr(e)}"

@tool
def FeatureClassToFeatureClass_conversion(
    input_fc: Annotated[str, "Full path to the input feature class (e.g., 'C:/gdb.gdb/roads')"],
    output_folder: Annotated[str, "Folder path where shapefile will be saved (e.g., 'C:/output/')"],
    output_name: Annotated[str, "Name of the output shapefile (e.g., 'roads_filtered.shp')"],
    where_clause: Annotated[str, "SQL expression for filtering (e.g., \"TYPE = 'Highway'\")"]
) -> str:
    """FeatureClassToFeatureClass_tool
    Exports a filtered subset of features from a feature class to a shapefile."""
    try:
        arcpy.env.overwriteOutput = True
        arcpy.FeatureClassToFeatureClass_conversion(
            in_features=input_fc,
            out_path=output_folder,
            out_name=output_name,
            where_clause=where_clause
        )
        return f"Exported filtered shapefile to: {output_folder}/{output_name}"
    except Exception as e:
        return f"FeatureClassToFeatureClass failed. Error: {repr(e)}"

