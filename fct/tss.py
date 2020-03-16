# ee.pypr, philippe rufin 2020
# philippe.rufin@googlemail.com
# inspired by baumi-berlin
#######################################################
# TSS function returns pixel-wise time series from
#######################################################
# TM, ETM+, and OLI blue, green, red, nir, swir1, swir2
# bands
#######################################################
# point_shape is path to point shapefile,
# startDate and endDate to be provided as datetime
# mark beginning and end of collection period
# write = True produces csv file, as defined in
# out_path containing results
#######################################################

import ee
import datetime
import numpy as np
import gdal
import ogr
import csv
import fct.cld
import fct.lnd

def TSS(point_shape, startDate, endDate, write, out_path):

    collection = fct.lnd.LND_glob(startDate, endDate)
    tss_list = []

    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(point_shape, 0)
    layer = dataSource.GetLayer()
    feat = layer.GetNextFeature()

    while feat:
        id = feat.GetField("ID")
        print("point id " + str(id))

        xCoord = feat.GetGeometryRef().GetPoint()[0]
        yCoord = feat.GetGeometryRef().GetPoint()[1]
        pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}

        tss = collection.getRegion(pts, 30).getInfo()
        tss[0].append("ID")

        for i in range(1, len(tss)):
            tss[i].append(id)

        # Remove right away the masked values, and some remnants from the sceneID
        val_reduced = []
        for val in tss:
            if not None in val:
                sceneID = val[0]
                p1 = sceneID.find("L")
                sceneID = sceneID[p1:]
                val[0] = sceneID
                val_reduced.append(val)

        # Append to output then get next feature
        tss_list.append(val_reduced)
        feat = layer.GetNextFeature()

    if write == True:

        print("write output table")
        with open(out_path, "w") as theFile:
            csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
            writer = csv.writer(theFile, dialect="custom")
            # Write the complete set of values (incl. the header) of the first entry
            for element in tss_list[0]:
                writer.writerow(element)
            tss_list.pop(0)
            # Now write the remaining entries, always pop the header
            for element in tss_list:
                element.pop(0)
                for row in element:
                    writer.writerow(row)