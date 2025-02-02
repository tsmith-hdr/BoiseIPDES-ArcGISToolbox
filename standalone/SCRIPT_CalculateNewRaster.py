import sys
from pathlib import Path
import arcpy

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools import TOOL_CalculateNewRaster
################################################################################################################################################################################################################################################################################################################################################
## Input Parameters
base_raster_path = Path(r"C:\Users\tedsmith\OneDrive - HDR, Inc\Documents\Projects\Boise\HabitatSuitability\DATA\GDB\Scratch.gdb\Test_Raster")
output_raster_path = Path(r"C:\Users\tedsmith\OneDrive - HDR, Inc\Documents\Projects\Boise\HabitatSuitability\DATA\GDB\Scratch.gdb\OutPut_Raster_MWFs_")
depth_lookup_table_path = Path(r"C:\Users\tedsmith\OneDrive - HDR, Inc\Documents\Projects\Boise\HabitatSuitability\DATA\GDB\Inputs_1.gdb\DepthLU")
fish_stage = "MWFs"
spatial_reference = arcpy.Describe(str(base_raster_path)).spatialReference.exportToString()
################################################################################################################################################################################################################################################################################################################################################

if __name__ == "__main__":
    TOOL_CalculateNewRaster.main(base_raster_path=base_raster_path, 
                                 output_raster_path=output_raster_path,
                                 depth_lookup_table_path=depth_lookup_table_path,
                                 fish_stage=fish_stage,
                                 spatial_reference=spatial_reference
                                 )