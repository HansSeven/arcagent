"""1. Buffer"""
@tool
def arc_gis_pro_create_buffer(
        input_feature: Annotated[str, "The path to the input features to buffer (e.g., C:/data/roads.shp)"],
        output_folder: Annotated[str, "The folder where the buffer output will be saved (e.g., C:/Users/90608/Desktop/b)"],
        buffer_distance: Annotated[str, "The buffer distance, in the format '<value> <unit>' (e.g., '100 Meters')"],
        buffer_name: Annotated[str, "The filename for the buffer output, including extension (e.g., 'roads_buffer.shp')"],
        dissolve_option: Annotated[str, "Dissolve option: 'NONE' (default, no dissolve), 'ALL' (merge all buffers), or a field name"]
):
    """Buffer
    Creates buffer zones around input features at the specified distance.
    Output: a new feature class saved at the specified path (e.g., C:/Users/90608/Desktop/b/roads_buffer.shp)."""
    try:
        output_path = create_buffer(input_feature, output_folder, buffer_distance, buffer_name, dissolve_option)
    except BaseException as e:
        return f"Failed to execute Buffer. Error: {repr(e)}"
    return f"the output path is {output_path}."

"""2. Clip"""
@tool
def arc_gis_pro_clip(
        input_fc: Annotated[str, "The path to the input features to be clipped (e.g., C:/data/landuse.shp)"],
        clip_fc: Annotated[str, "The path to the clip feature that defines the clipping extent (e.g., C:/data/clip_area.shp)"],
        output_fc: Annotated[str, "The path to save the clipped output features (e.g., C:/data/landuse_clipped.shp)"]
):
    """Clip
    Extracts the portions of the input features that overlap the clip features and writes them to a new feature class.
    Output: a feature class saved at output_fc containing only the clipped features (e.g., C:/data/landuse_clipped.shp)."""
    try:
        output_path = simple_clip(input_fc, clip_fc, output_fc)
    except BaseException as e:
        return f"Failed to execute Clip. Error: {repr(e)}"
    return f"the output path is {output_path}."
"""3. Create Layer (Layer-level)"""
@tool
def arc_gis_pro_create_layer_layer_level(
        input_path: Annotated[str, "The path to the input feature class or shapefile (e.g., C:/data/residents.shp)"],
        layer_name: Annotated[str, "The name to assign to the created in-memory layer (e.g., 'residents_lyr')"]
):
    """Create Layer (Layer-level)
    A layer-level tool that loads a dataset into memory as a feature layer.
    This allows subsequent tools (e.g., SelectLayerByAttribute, SelectLayerByLocation, CalculateField) to operate on the layer without immediately writing to disk.
    Output: the name of the in-memory layer (e.g., 'residents_lyr'), which can be passed to other layer-level tools."""
    try:
        result = create_layer(input_path, layer_name)
    except BaseException as e:
        return f"Failed to execute Create Layer. Error: {repr(e)}"
    return result
"""4. Select Layer By Location (Layer-level)"""
@tool
def arc_gis_pro_select_by_location_layer_level(
        target_layer: Annotated[str, "The name of the layer to apply spatial selection on (e.g., 'residents_lyr')"],
        overlap_layer: Annotated[str, "The name of the layer defining the spatial reference (e.g., 'greenspace_buffer')"],
        spatial_relation: Annotated[str, "The spatial relationship type: 'INTERSECT' (default), 'WITHIN', 'CONTAINS', etc."]
):
    """Select Layer By Location (Layer-level)
    Selects features in the target layer based on their spatial relationship to features in another layer.
    Output: the same layer (target_layer) with a new selection applied according to spatial_relation."""
    try:
        result = select_by_location(target_layer, overlap_layer, spatial_relation)
    except BaseException as e:
        return f"Failed to execute Select Layer By Location. Error: {repr(e)}"
    return result
"""5. Export Selected Features (Layer-level)"""
@tool
def arc_gis_pro_export_selected_features_layer_level(
        layer_name: Annotated[str, "The name of the feature layer with a selection applied (e.g., 'residents_lyr')"],
        output_folder: Annotated[str, "The folder where the exported features will be saved (e.g., C:/output/)"],
        output_name: Annotated[str, "The name of the output feature class or shapefile (e.g., 'selected_residents.shp')"]
):
    """Export Selected Features (Layer-level)
    Exports the currently selected features from an in-memory layer to a new feature class or shapefile.
    Output: a new feature class saved at output_folder/output_name containing only the selected features."""
    try:
        result = export_selected_features(layer_name, output_folder, output_name)
    except BaseException as e:
        return f"Failed to execute Export Selected Features. Error: {repr(e)}"
    return result
"""6. Select By Attribute (Layer-level)"""
@tool
def arc_gis_pro_select_by_field_value_layer_level(
        layer_name: Annotated[str, "The name of the feature layer to query (e.g., 'restaurant_layer')"],
        field_name: Annotated[str, "The attribute field to use in the query (e.g., 'fclass')"],
        field_value: Annotated[str, "The value to match for selection (e.g., 'restaurant')"]
):
    """Select By Attribute (Layer-level)
    A layer-level tool that applies an attribute filter to an in-memory feature layer.
    It updates the layer’s selection based on the given field_name = field_value expression.
    Output: the same layer_name with the new selection applied."""
    try:
        result = select_by_field_value(layer_name, field_name, field_value)
    except BaseException as e:
        return f"Failed to execute Select By Attribute. Error: {repr(e)}"
    return result
"""7. Project"""
@tool
def arc_gis_pro_project(
        input_fc: Annotated[str, "The path to the input feature class to be projected (e.g., C:/output/restaurant_selected.shp)"],
        output_fc: Annotated[str, "The path to save the projected feature class (e.g., C:/output/restaurant_projected.shp)"],
        epsg_code: Annotated[int, "The EPSG code of the target coordinate system (default 3857 for Web Mercator)"]
):
    """Project
    Reprojects the input feature class to a specified metric coordinate system.
    Output: a new feature class saved at output_fc in the given spatial reference (e.g., C:/output/restaurant_projected.shp)."""
    try:
        output_path = project_to_metric(input_fc, output_fc, epsg_code)
    except BaseException as e:
        return f"Failed to execute Project. Error: {repr(e)}"
    return f"the output path is {output_path}."

"""8. Kernel Density"""
@tool
def arc_gis_pro_kernel_density(
        input_point_fc: Annotated[str, "The path to the input point feature class (projected in a metric coordinate system, e.g., C:/output/restaurant_projected.shp)"],
        population_field: Annotated[str, "The field used as weight for density calculation (e.g., 'NONE' for equal weight)"],
        output_raster_path: Annotated[str, "The path to save the output density raster (e.g., C:/output/restaurant_density.tif)"],
        cell_size: Annotated[int, "The cell size (in map units, e.g., meters) for the output raster"],
        search_radius: Annotated[str, "The search radius (in map units, e.g., '1000') for the kernel density calculation"]
):
    """Kernel Density
    Calculates a smoothly tapered density surface from point features using a kernel function.
    Output: a raster file saved at output_raster_path (e.g., C:/output/restaurant_density.tif)."""
    try:
        output_path = kernel_density(input_point_fc, population_field, output_raster_path, cell_size, search_radius)
    except BaseException as e:
        return f"Failed to execute Kernel Density. Error: {repr(e)}"
    return f"the output path is {output_path}."

"""9. 空间连接"""
@tool
def arc_gis_pro_spatial_join(
        target_fc: Annotated[str, "The path to the feature class receiving joined attributes (e.g., C:/data/roads_buffer.shp)"],
        join_fc: Annotated[str, "The path to the feature class providing attributes to join (e.g., C:/data/restaurant_points.shp)"],
        output_fc: Annotated[str, "The path to save the spatial join result (e.g., C:/output/buffer_join_result.shp)"],
        join_operation: Annotated[str, "JOIN operation: 'JOIN_ONE_TO_ONE' or 'JOIN_ONE_TO_MANY' (default)."],
        join_type: Annotated[str, "Keep options: 'KEEP_ALL' or 'KEEP_COMMON' (default) for matched features."],
        match_option: Annotated[str, "Spatial relationship: 'INTERSECT' (default), 'CONTAINS', 'WITHIN', 'CLOSEST', etc."]
):
    """Spatial Join
    Appends attributes from join_fc to target_fc based on spatial relationships.
    Output: a new feature class saved at output_fc containing all target_fc features,
    joined with matching join_fc attributes and added fields like Join_Count and TARGET_FID."""
    try:
        result = spatial_join(target_fc, join_fc, output_fc, join_operation, join_type, match_option)
    except BaseException as e:
        return f"Failed to execute Spatial Join. Error: {repr(e)}"
    return f"the output path is {result}."

"""10. Summary Statistics"""
@tool
def arc_gis_pro_summary_statistics(
        input_fc: Annotated[str, "The path to the input table or feature class to be summarized (e.g., C:/output/buffer_join_result.shp)"],
        statistics_field: Annotated[str, "The field to be counted (e.g., 'osm_id')"],
        output_table: Annotated[str, "The path to save the summary statistics table (e.g., C:/output/statistics_result.dbf)"],
        case_field: Annotated[str, "The field used to group records (e.g., 'TARGET_FID')"]
):
    """Summary Statistics
    Calculates summary statistics for a specified field, grouping by case_field.
    Output: a standalone table saved at output_table containing COUNT(statistics_field) per unique case_field (e.g., C:/output/statistics_result.dbf)."""
    try:
        result = summary_statistics(input_fc, statistics_field, output_table, case_field)
    except BaseException as e:
        return f"Failed to execute Summary Statistics. Error: {repr(e)}"
    return f"the output path is {result}."
"""11. Select By Field (File)"""
@tool
def arc_gis_pro_select_by_field(
        input_layer: Annotated[str, "The path to the input feature class or shapefile (e.g., C:/data/osm_points.shp)"],
        field_name: Annotated[str, "The attribute field to query (e.g., 'fclass')"],
        field_value: Annotated[str, "The value to select in the field (e.g., 'hospital')"],
        output_fc: Annotated[str, "The path to save the selected features (e.g., C:/output/hospitals.shp)"]
):
    """Select By Field
    Extracts features from the input layer matching a specific attribute value and writes them to a new feature class.
    Output: a feature class saved at output_fc containing only features where field_name = field_value."""
    try:
        result = select_by_field_value_file(input_layer, field_name, field_value, output_fc)
    except BaseException as e:
        return f"Failed to execute Select By Field. Error: {repr(e)}"
    return f"the output path is {result}."
"""12. Generate Near Table"""
@tool
def arc_gis_pro_generate_near_table(
        in_points: Annotated[str, "The path to the input point features (e.g., C:/data/schools.shp)"],
        near_points: Annotated[str, "The path to the point features to search against (e.g., C:/data/hospitals.shp)"],
        out_table: Annotated[str, "The path to save the near table (e.g., C:/output/school_nearest_hospital.dbf)"],
        search_radius: Annotated[str, "Maximum search radius (e.g., '1000 Meters'); leave empty for no limit"],
        location: Annotated[str, "Specify 'LOCATION' to add nearest point coordinates or 'NO_LOCATION' (default)"],
        angle: Annotated[str, "Specify 'ANGLE' to add direction angle or 'NO_ANGLE' (default)"]
):
    """Generate Near Table
    Creates a table of the nearest distances between in_points and near_points.
    Output: a table saved at out_table containing NEAR_DIST, NEAR_FID, and optional NEAR_X/NEAR_Y and NEAR_ANGLE fields."""
    try:
        result = generate_near_table(in_points, near_points, out_table, search_radius, location, angle)
    except BaseException as e:
        return f"Failed to execute Generate Near Table. Error: {repr(e)}"
    return f"the output path is {result}."
"""13. Table To Table"""
@tool
def arc_gis_pro_table_to_table(
        input_table: Annotated[str, "The path to the input table to be exported (e.g., C:/output/school_nearest_hospital.dbf)"],
        output_folder: Annotated[str, "The folder where the output table will be saved (e.g., C:/output)"],
        output_name: Annotated[str, "The name of the exported table file (including extension, e.g., near_table_result.csv)"]
):
    """Table To Table
    Exports an input table or table view to a new standalone table in the specified workspace.
    Output: a table saved at the combined path output_folder/output_name (e.g., C:/output/near_table_result.csv)."""
    try:
        result = table_to_table(input_table, output_folder, output_name)
    except BaseException as e:
        return f"Failed to execute Table To Table. Error: {repr(e)}"
    return f"the output path is {result}."
"""14. Multiple Ring Buffer"""
@tool
def arc_gis_pro_multiple_ring_buffer(
        input_fc: Annotated[str, "The path to the input point features (e.g., C:/data/restaurant.shp)"],
        output_fc: Annotated[str, "The path to save the multiple ring buffer output (e.g., C:/output/restaurant_buffer.shp)"],
        distances: Annotated[str, "Semicolon-separated list of distances for rings (e.g., '500;1000;1500')"],
        buffer_unit: Annotated[str, "The unit for buffer distances (e.g., 'Meters')"],
        dissolve_option: Annotated[str, "Dissolve option: 'ALL' to merge rings or 'NONE' to keep separate"]
):
    """Multiple Ring Buffer
    Creates concentric buffer rings around input points for the specified distances.
    Output: a feature class saved at output_fc containing the buffer rings (e.g., C:/output/restaurant_buffer.shp)."""
    try:
        dist_list = distances.split(";")
        result = create_multiple_ring_buffers(input_fc, output_fc, dist_list, buffer_unit, dissolve_option)
    except BaseException as e:
        return f"Failed to execute Multiple Ring Buffer. Error: {repr(e)}"
    return f"the output path is {result}."
"""15. Erase"""
@tool
def arc_gis_pro_erase(
        input_fc: Annotated[str, "The path to the input features to be erased (e.g., C:/data/residential.shp)"],
        erase_fc: Annotated[str, "The path to the features defining areas to remove (e.g., C:/data/park_buffer.shp)"],
        output_fc: Annotated[str, "The path to save the erased output features (e.g., C:/output/residential_no_park.shp)"]
):
    """Erase
    Calculates the geometric difference between input_fc and erase_fc, preserving only the portions of input_fc that fall outside erase_fc.
    Output: a feature class saved at output_fc containing only the non-overlapping areas (e.g., C:/output/residential_no_park.shp)."""
    try:
        result = erase_features(input_fc, erase_fc, output_fc)
    except BaseException as e:
        return f"Failed to execute Erase. Error: {repr(e)}"
    return f"the output path is {result}."
"""16. Dissolve"""
@tool
def arc_gis_pro_dissolve(
        input_fc: Annotated[str, "The path to the input features to be dissolved (e.g., C:/data/park_buffer.shp)"],
        output_fc: Annotated[str, "The path to save the dissolved output features (e.g., C:/output/park_merged.shp)"],
        dissolve_field: Annotated[str, "Comma-separated field names to dissolve by (e.g., 'CITY_NAME'); leave empty for full dissolve."],
        multi_part: Annotated[str, "'SINGLE_PART' or 'MULTI_PART' to specify output feature type (default 'SINGLE_PART')."]
):
    """Dissolve
    Merges features based on common attribute values or combines all features when no fields are specified.
    Output: a feature class saved at output_fc containing the dissolved results (e.g., C:/output/park_merged.shp)."""
    try:
        fields = dissolve_field.split(",") if dissolve_field else []
        result = dissolve_features(input_fc, output_fc, fields, multi_part)
    except BaseException as e:
        return f"Failed to execute Dissolve. Error: {repr(e)}"
    return f"the output path is {result}."
"""17. Identity"""
@tool
def arc_gis_pro_identity(
        input_fc: Annotated[str, "The path to the input features to overlay (e.g., C:/data/residential.shp)"],
        identity_fc: Annotated[str, "The path to the features whose attributes will be joined (e.g., C:/data/road_buffer.shp)"],
        output_fc: Annotated[str, "The path to save the identity result features (e.g., C:/output/resid_road_identity.shp)"]
):
    """Identity
    Overlays input_fc with identity_fc, preserving input_fc’s attributes and appending identity_fc’s attributes where they overlap.
    Output: a new feature class saved at output_fc containing the combined geometries and attributes (e.g., C:/output/resid_road_identity.shp)."""
    try:
        result = identity_features(input_fc, identity_fc, output_fc)
    except BaseException as e:
        return f"Failed to execute Identity. Error: {repr(e)}"
    return f"the output path is {result}."

"""18. Near"""
@tool
def arc_gis_pro_near(
        input_fc: Annotated[str, "The path to the features for which nearest distances will be calculated (e.g., C:/data/hospitals.shp)"],
        near_fc: Annotated[str, "The path to the features to search for nearest neighbors (e.g., C:/data/roads.shp)"],
        search_radius: Annotated[str, "Optional maximum search radius (e.g., '500 Meters'); leave empty for no limit"],
        location: Annotated[str, "Specify 'LOCATION' to add nearest point coordinates or 'NO_LOCATION' (default)"],
        angle: Annotated[str, "Specify 'ANGLE' to add direction angle or 'NO_ANGLE' (default)"],
        method: Annotated[str, "Distance calculation method: 'PLANAR' (flat earth) or 'GEODESIC' (earth curvature)"]
):
    """Near
    Calculates the distance from each feature in input_fc to the nearest feature in near_fc and writes the results into input_fc’s attribute table.
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
def arc_gis_pro_split(
        input_fc: Annotated[str, "The path to the input feature class to split (e.g., C:/data/roads.shp)"],
        split_fc: Annotated[str, "The path to the feature class defining split boundaries (e.g., C:/data/counties.shp)"],
        output_folder: Annotated[str, "The folder where the split feature classes will be saved (e.g., C:/output/roads_by_county/)"],
        split_field: Annotated[str, "The attribute field to split by if split_fc is empty (e.g., 'CITY_NAME'); leave empty to use split_fc"]
):
    """Split
    Splits input_fc into multiple feature classes based on split_fc boundaries or split_field values.
    Output: multiple feature class files created in output_folder."""
    try:
        split_features(input_fc, split_fc, output_folder, split_field)
    except BaseException as e:
        return f"Failed to execute Split. Error: {repr(e)}"
    return f"Features have been split into {output_folder}."
"""20. Feature To Point"""
@tool
def arc_gis_pro_feature_to_point(
        input_fc: Annotated[str, "The path to the input polygon feature class (e.g., C:/data/service_area.shp)"],
        output_fc: Annotated[str, "The path to save the output point feature class (e.g., C:/output/service_area_centroids.shp)"],
        point_location: Annotated[str, "Specifies point placement: 'CENTROID' for geometric center or 'INSIDE' to ensure point falls within the polygon (default 'CENTROID')"]
):
    """Feature To Point
    Converts polygon features into point features by placing a point at each polygon’s centroid or inside position.
    Output: a new point feature class saved at output_fc (e.g., C:/output/service_area_centroids.shp)."""
    try:
        result = feature_to_point(input_fc, output_fc, point_location)
    except BaseException as e:
        return f"Failed to execute Feature To Point. Error: {repr(e)}"
    return f"the output path is {result}."
"""21. Feature Vertices To Points"""
@tool
def arc_gis_pro_feature_vertices_to_points(
        input_fc: Annotated[str, "The path to the input line or polygon feature class (e.g., C:/data/roads.shp)"],
        output_fc: Annotated[str, "The path to save the output point feature class (e.g., C:/output/road_vertices.shp)"],
        point_type: Annotated[str, "The type of vertices to export: 'ALL' (all vertices), 'START', 'END', or 'MID'"]
):
    """Feature Vertices To Points
    Converts each specified vertex of line or polygon features into point features.
    Output: a point feature class saved at output_fc containing the requested vertices."""
    try:
        result = feature_vertices_to_points(input_fc, output_fc, point_type)
    except BaseException as e:
        return f"Failed to execute Feature Vertices To Points. Error: {repr(e)}"
    return f"the output path is {result}."
"""22. Feature To Line"""
@tool
def arc_gis_pro_feature_to_line(
        input_fc: Annotated[str, "The path to the input polygon feature class (e.g., C:/data/park.shp)"],
        output_fc: Annotated[str, "The path to save the output line feature class (e.g., C:/output/park_boundaries.shp)"]
):
    """Feature To Line
    Converts polygon boundaries or multipart features into line features.
    Output: a line feature class saved at output_fc (e.g., C:/output/park_boundaries.shp)."""
    try:
        result = feature_to_line(input_fc, output_fc)
    except BaseException as e:
        return f"Failed to execute Feature To Line. Error: {repr(e)}"
    return f"the output path is {result}."