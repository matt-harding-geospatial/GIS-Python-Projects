#This is for Polygons
#Importing the libraries
import arcpy
import os

#Setting up workspace
pol_feature_class = r"C:\Users\mhard\OneDrive\Documents\ArcGIS\AnglianWater\Testing\Testing_3\Testing_3\Testing_3.gdb\Poly"
shapefile_folder = r"C:\Users\mhard\OneDrive\Documents\ArcGIS\AnglianWater\Biodiversity Net Gain Reporting Layers\ArcGIS\Biodiversity Net Gain Reporting Layers\Shapefiles"
output_folder = r"C:\Users\mhard\OneDrive\Documents\ArcGIS\AnglianWater\Biodiversity Net Gain Reporting Layers\ArcGIS\Polygons"

#Creating output folder if one does not already exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

#Selecting only the shapefiles from the shapefile folder
shapefiles = [f for f in os.listdir(shapefile_folder) if f.endswith('.shp')]

#Main tool
for shapefile in shapefiles:
    shapefile_path = os.path.join(shapefile_folder, shapefile)
    
    #Creating the name of the new shapefiles and saving them in a new folder
    output_name = os.path.splitext(shapefile)[0] + "_Biodiversity_Net_Gain_Pol.shp"
    output_path = os.path.join(output_folder, output_name)
    
    #Selecting layers the tool will clip from and what shapefiles it will use to clip. Then using this, uses the Select Layer By Location tool with the INTERSECT function
    arcpy.MakeFeatureLayer_management(pol_feature_class, "pol_lyr")
    arcpy.MakeFeatureLayer_management(shapefile_path, "shapefile_lyr")
    arcpy.SelectLayerByLocation_management("pol_lyr", "INTERSECT", "shapefile_lyr")
    
    #Uses the Python window to tell user how many features have been clipped to their respective site
    selected_count = int(arcpy.GetCount_management("pol_lyr")[0])
    if selected_count > 0:
        arcpy.FeatureClassToFeatureClass_conversion("pol_lyr", output_folder, output_name)
        print(f"Extracted {selected_count} features for {shapefile} and saved to {output_name}.")
    else:
        print(f"No features found within {shapefile}.")
    
    arcpy.Delete_management("pol_lyr")
    arcpy.Delete_management("shapefile_lyr")

print("Batch clip tool finished, you're welcome - Matt :^P.")

#This is for lines
import arcpy
import os
line_feature_class = r"C:\Users\mhard\OneDrive\Documents\ArcGIS\AnglianWater\Testing\Testing_3\Testing_3\Testing_3.gdb\Lines"
shapefile_folder = r"C:\Users\mhard\OneDrive\Documents\ArcGIS\AnglianWater\Biodiversity Net Gain Reporting Layers\ArcGIS\Biodiversity Net Gain Reporting Layers\Shapefiles"
output_folder = r"C:\Users\mhard\OneDrive\Documents\ArcGIS\AnglianWater\Biodiversity Net Gain Reporting Layers\ArcGIS\Lines"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    
shapefiles = [f for f in os.listdir(shapefile_folder) if f.endswith('.shp')]
for shapefile in shapefiles:
    shapefile_path = os.path.join(shapefile_folder, shapefile)
    
    output_name = os.path.splitext(shapefile)[0] + "_Biodiversity_Net_Gain_Line.shp"
    output_path = os.path.join(output_folder, output_name)
    
    arcpy.MakeFeatureLayer_management(line_feature_class, "line_lyr")

    arcpy.MakeFeatureLayer_management(shapefile_path, "shapefile_lyr")
    
    arcpy.SelectLayerByLocation_management("line_lyr", "INTERSECT", "shapefile_lyr")
    
    selected_count = int(arcpy.GetCount_management("line_lyr")[0])
    
    if selected_count > 0:
        arcpy.FeatureClassToFeatureClass_conversion("line_lyr", output_folder, output_name)
        print(f"Extracted {selected_count} features for {shapefile} and saved to {output_name}.")
    else:
        print(f"No features found within {shapefile}.")
    
    arcpy.Delete_management("line_lyr")
    arcpy.Delete_management("shapefile_lyr")

print("Batch clip tool finished, you're welcome - Matt :^P.")