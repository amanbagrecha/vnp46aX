"""scipt to convert h5 to geotiff using gdal"""
# source: https://blackmarble.gsfc.nasa.gov/tools/OpenHDF5.py
from osgeo import gdal
import glob
import os
from pathlib import Path


def convert_h5_to_tif(rasterFile):

    # Get File Name Prefix
    rasterFilePre = Path(rasterFile).stem

    print(rasterFilePre)

    fileExtension = "_BBOX.tif"

    ## Open HDF file
    hdflayer = gdal.Open(rasterFile, gdal.GA_ReadOnly)

    subdatasets = hdflayer.GetSubDatasets()

    for subdataset, meta in subdatasets:

        if "Gap_Filled_DNB_BRDF-Corrected_NTL" in subdataset:
            subhdflayer = subdataset

    if not subhdflayer:
        raise Exception("did not find gap filled dnb NTL")

    # Open raster layer
    rlayer = gdal.Open(subhdflayer, gdal.GA_ReadOnly)

    # Subset the Long Name
    outputName = Path(subhdflayer.split(":")[-1]).stem

    outputNameFinal = f"{outputName}-{rasterFilePre}{fileExtension}"
    print(outputNameFinal)

    outputFolder = "./output"
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder, exist_ok=True)

    outputRaster = os.path.join(outputFolder, outputNameFinal)

    # collect bounding box coordinates
    HorizontalTileNumber = int(rlayer.GetMetadata_Dict()["HorizontalTileNumber"])
    VerticalTileNumber = int(rlayer.GetMetadata_Dict()["VerticalTileNumber"])

    WestBoundCoord = (10 * HorizontalTileNumber) - 180
    NorthBoundCoord = 90 - (10 * VerticalTileNumber)
    EastBoundCoord = WestBoundCoord + 10
    SouthBoundCoord = NorthBoundCoord - 10

    EPSG = "-a_srs EPSG:4326"  # WGS84

    translateOptionText = (
        EPSG
        + " -a_ullr "
        + str(WestBoundCoord)
        + " "
        + str(NorthBoundCoord)
        + " "
        + str(EastBoundCoord)
        + " "
        + str(SouthBoundCoord)
    )

    translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine(translateOptionText))
    gdal.Translate(outputRaster, rlayer, options=translateoptions)

    print("Done")


if __name__ == "__main__":

    ## List input raster files
    rasterFiles = glob.glob("*.h5")
    for rasterFile in rasterFiles:
        convert_h5_to_tif(rasterFile)
