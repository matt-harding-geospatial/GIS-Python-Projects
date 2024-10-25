import arcpy

# Slope Raster (Importing Slope Raster - MH)

arcpy.env.workspace = r"K:\GIS_Tools_Pro\zz_Development\Peat Depth Calculation\Dev\PeatProbes.gdb\PeatProbes"
arcpy.env.overwriteOutput = True
input_raster = r"K:\GIS_Tools_Pro\zz_Development\Peat Depth Calculation\Dev\PeatProbes.gdb\DTM"
output_slope_raster = "Slope"
arcpy.sa.Slope(input_raster, output_slope_raster, "DEGREE")

 

# Multivalues to points (Giving Values from the slope raster to point shapefiles - MH)

arcpy.env.workpace = r"K:\GIS_Tools_Pro\zz_Development\Peat Depth Calculation\Dev\PeatProbes.gdb\PeatProbes"
arcpy.env.overwriteOutput = True
input_points = "PeatProbePoints"
input_raster_list = [
    "Slope"    
]
output_feature_class = "PeatProbePoints"
arcpy.sa.ExtractMultiValuesToPoints(input_raster_list, "PeatProbePoints")

 # Updating Attribute tables - MH

def updatePeatCoefficient(row):
    depth = row[4]
    if row[1] == 0:
        row[1] = 0
    elif depth < 0.1 or depth > 0.49:
        row[1] = 1
    elif depth < 0.5 or depth > 1.49:
        row[1] = 2
    elif depth >= 1.5:
        row[1] = 3          
    return row[1]

def updateSubstrate(row):
    if row[1] == "Granular":
        row[1] = 1
    elif row[1]== "Rock":
        row[1] = 2
    elif row[1] == "Cohesive":
        row[1] = 3
    elif row[1] == "Depth not proven":
        row[1] = 3      
    return row[2]

def updateSlope(row):
    slope = row[9]
    if row[1] == slope <=2:
        row[1] = 1
    elif slope < 2 or slope > 4:
        row[1] = 2
    elif slope < 4 or slope > 8:
        row[1] = 4
    elif slope < 8 or slope > 12:
        row[1] = 6
    elif slope >= 12:
        row[1] = 8      
    return row[3]

def updateRisk(row):
    risk = row[8]
    if row[1] == 0 < risk > 5:
        row[1] = "Negligble"
    elif risk < 5 or risk > 15:
        row[1] = "Low"
    elif risk < 15 or risk > 31:
        row [2] = "Medium"
    elif risk < 31 or risk > 100:
        row[1] = "High"
    return row[4]

def updateFields(peatFC):
    fields = ["OBJECTID", "Substrate", "Substrat_Thickness", "PeatDepthCalc", "PtDepth", "PtCoeff", "SubCoeff", "SlpCoeff", "Risk", "Slope", "SlopeOST5Degrees"]
    with arcpy.da.UpdateCursor(peatFC, fields) as cursor:
        for row in cursor:
            row[1] = updatePeatCoefficient(row)
            row[2] = updateSubstrate(row)
            row[3] = updateSlope(row)
            row[4] = updateRisk(row)
            cursor.updateRow(row)

# Peat Depth (New Peat depth calculations - MH)

arcpy.env.workspace = r"K:\GIS_Tools_Pro\zz_Development\Peat Depth Calculation\Dev\PeatProbes.gdb\PeatProbes"
arcpy.env.overwriteOutput = True
aprx = arcpy.mp.ArcGISProject()
map = aprx.listMaps()[0]
dataframe = map.listDataFrames()[0]
inputpoints = "PeatProbePoints"
output_spline_raster = ()
output_clipped_raster = ()
extent = dataframe.extent
arcpy.ddd.SplineWithBarriers()
boundary_features = ""
arcpy.managment.Clip()

# Slide Risk (Calculation of slide risks - MH)

arcpy.env.workspace = r"K:\GIS_Tools_Pro\zz_Development\Peat Depth Calculation\Dev\PeatProbes.gdb\PeatProbes"
arcpy.env.overwriteOutput = True
aprx = arcpy.mp.ArcGISProject()
map = aprx.listMaps()[0]
dataframe = map.listDataFrames()[0]
inputpoints = "PeatProbePoints"
output_spline_raster = ()
output_clipped_raster = ()
extent = dataframe.extent
arcpy.ddd.SplineWithBarriers()
boundary_features = ""
arcpy.managment.Clip()

# Updating model with new peat depth calculation data - MH 

def calculate_sum_and_update_field(peatFC, source_fields, destination_field):
    with arcpy.da.UpdateCursor(peatFC, source_fields + [destination_field]) as cursor:
        for row in cursor:
            total = round(sum(value if value is not None else 0 for value in row[:-1]),1)
            row[-1] = total
            cursor.updateRow(row)

def main():
    feature_class_path = r"K:\GIS_Tools_Pro\zz_Development\Peat Depth Calculation\Dev\PeatProbes.gdb\PeatProbes"
    source_fields_list = ["Depth_0pt1_to_0pt5", "Depth_0pt6_to_1", "Depth_1pt1_to_1pt5", "Depth_1pt6_to_2", "Depth_2pt1_to_2pt5", "Depth_2pt6_to_3", "Depth_3pt1_to_4"]
    destination_field_name = "PeatDepthCalc"
    calculate_sum_and_update_field(feature_class_path, source_fields_list, destination_field_name)
    updateFields(feature_class_path)

if __name__ == "__main__":
    main()