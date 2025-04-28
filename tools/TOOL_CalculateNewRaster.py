################################################################################################################################################################################################################################################################################################################################################
## Libraries 
import arcpy
import os
import sys
import numpy as np
from pathlib import Path
import logging
import datetime


sys.path.append(Path(__file__).resolve().parents[1])
from constants.values import ROOT_DIR
################################################################################################################################################################################################################################################################################################################################################
## Environments
run_debug_mode = True
arcpy.env.overwriteOutput = True
################################################################################################################################################################################################################################################################################################################################################
## Logging ## Don't Change
if run_debug_mode:
    log_file = Path(ROOT_DIR, "logs", "CalculateNewRaster", "CalculateNewRaster_DEBUG.log")
    logging.basicConfig(filename=log_file, filemode="w",format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
else:
    log_file = Path(ROOT_DIR, "logs", "CalculateNewRaster", "CalculateNewRaster.log")
    logging.basicConfig(filename=log_file, filemode="a",format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
################################################################################################################################################################################################################################################################################################################################################
## Functions
def getRangeDictionary(in_table:str, fish_stage:str)->dict:
    out_dict = {}
    with arcpy.da.SearchCursor(in_table=in_table, field_names=["MinDepth", "MaxDepth", "Min_Score", "Max_Score"], where_clause="Fish_Stage = '{}'".format(fish_stage)) as cursor:
        for row in cursor:
            out_dict[(row[0], row[1])] = [row[2], row[3]]

    return out_dict


def getScores(x, in_dict:dict)->float:
    """
    Function to be used in the NumPy Array Vectorize. 
    x is the array element
    in_dict is the range dictionary that contains the depths and the corresponding scores
    """

    if x == -1.0:
        return -1.0
    else:
        for (MinD, MaxD), value in in_dict.items():
            if float(MinD) <= x <= float(MaxD):
                ## Value[0] is the Min Score pulled from the Depth/Velocity Lookup Table
                ## Value[1] is the Max Score pulled from the Depth/Velocity Lookup Table
                MinS = value[0]
                MaxS = value[1]

                new_score = (((x - MinD)/(MaxD - MinD))*(MaxS - MinS))+MinS

                logger.debug(f"X: {x}")
                logger.debug(f"Min D: {MinD}-Max D: {MaxD}")
                logger.debug(f"Min S: {MinS}-Max S: {MaxS}")
                logger.debug(f"New Score: {new_score}")

                return new_score
            


def main(base_raster_path:Path, output_raster_path:Path, depth_lookup_table_path:Path, fish_stage:str, spatial_reference:str)->None:

    logger.info(f"Starting: {datetime.datetime.now()}")
    logger.info(f"Run by: {os.getlogin()}")
    logger.info(f"Run on: {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}")
    logger.info(f"Base Raster Path: {base_raster_path}")
    logger.info(f"Output Raster Path: {output_raster_path}")
    logger.info(f"Depth Lookup Table Path: {depth_lookup_table_path}")
    logger.info(f"Fish Stage: {fish_stage}")
    logger.info(f"Spatial Reference: {spatial_reference}")
    
    logger.info(f"Creating Base Raster...")
    base_raster = arcpy.Raster(str(base_raster_path))

    ## attributes from the Base Raster Object to be used in NumPy/Raster Conversions
    lower_left = arcpy.Point(base_raster.extent.XMin, base_raster.extent.YMin)
    cell_size_width = base_raster.meanCellWidth
    cell_size_height = base_raster.meanCellHeight       
    
    logger.info(f"Converting Base Raster to NumPy Array...")

    arr = arcpy.RasterToNumPyArray(base_raster, lower_left_corner=lower_left, nodata_to_value=-1.0)

    del base_raster
    
    logger.debug(f"Array Row Count: {arr.shape[0]}")
    logger.debug(f"Array Column Count: {arr.shape[1]}")

    range_dictionary = getRangeDictionary(in_table=str(depth_lookup_table_path), fish_stage=fish_stage)

    logger.debug(f"Range Dictionary: {range_dictionary}")

    vectorized_function = np.vectorize(getScores)
    logger.info(f"Calculating New Score...")
    new_arr = vectorized_function(arr, range_dictionary)

    logger.debug(f"New Array Row Count: {new_arr.shape[0]}")
    logger.debug(f"New Array Column Count: {new_arr.shape[1]}")

    logger.info(f"Exporting New NumPy Array to Raster...")

    temp_raster = arcpy.NumPyArrayToRaster(in_array=new_arr,
                                            lower_left_corner=lower_left,
                                            x_cell_size=cell_size_width,
                                            y_cell_size=cell_size_height,
                                            value_to_nodata=-1.0
                                            )

    saved_raster = temp_raster.save(str(output_raster_path))

    del temp_raster

    logger.info(f"Defining Spatial Reference...")

    arcpy.management.DefineProjection(str(output_raster_path), spatial_reference)

    logger.info(f"Finished: {datetime.datetime.now()}")
################################################################################################################################################################################################################################################################################################################################################
