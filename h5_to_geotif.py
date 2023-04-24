"""scipt to convert h5 to geotiff using gdal"""
# source: https://blackmarble.gsfc.nasa.gov/tools/OpenHDF5.py
from osgeo import gdal
import glob
## List input raster files

rasterFiles = glob.glob("*.h5")
#print(rasterFiles)

#Get File Name Prefix
rasterFilePre = rasterFiles[0][:-3]
print(rasterFilePre)

fileExtension = "_BBOX.tif"

## Open HDF file
hdflayer = gdal.Open(rasterFiles[0], gdal.GA_ReadOnly)

#print (hdflayer.GetSubDatasets())

# Open raster layer
#hdflayer.GetSubDatasets()[0][0] - for first layer
#hdflayer.GetSubDatasets()[1][0] - for second layer ...etc
subhdflayer = hdflayer.GetSubDatasets()[0][0]
rlayer = gdal.Open(subhdflayer, gdal.GA_ReadOnly)
#outputName = rlayer.GetMetadata_Dict()['long_name']

#Subset the Long Name
outputName = subhdflayer[92:]

outputNameNoSpace = outputName.strip().replace(" ","_").replace("/","_")
outputNameFinal = outputNameNoSpace + rasterFilePre + fileExtension
print(outputNameFinal)

outputFolder = "./"

outputRaster = outputFolder + outputNameFinal

#collect bounding box coordinates
HorizontalTileNumber = int(rlayer.GetMetadata_Dict()["HorizontalTileNumber"])
VerticalTileNumber = int(rlayer.GetMetadata_Dict()["VerticalTileNumber"])
    
WestBoundCoord = (10*HorizontalTileNumber) - 180
NorthBoundCoord = 90-(10*VerticalTileNumber)
EastBoundCoord = WestBoundCoord + 10
SouthBoundCoord = NorthBoundCoord - 10

EPSG = "-a_srs EPSG:4326" #WGS84

translateOptionText = EPSG+" -a_ullr " + str(WestBoundCoord) + " " + str(NorthBoundCoord) + " " + str(EastBoundCoord) + " " + str(SouthBoundCoord)

translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine(translateOptionText))
gdal.Translate(outputRaster,rlayer, options=translateoptions)

#Display image in QGIS (run it within QGIS python Console) - remove comment to display
#iface.addRasterLayer(outputRaster, outputNameFinal)