# ee.pypr, philippe rufin 2020
# philippe.rufin@googlemail.com
# inspired by baumi-berlin

import numpy as np
import datetime
import csv
import ee
import ogr
import fct.cld
import fct.lnd

def TSI(point_shape, startDate, endDate, interval, aggregation, write, out_path):

    coll = fct.lnd.LND_glob(startDate, endDate)\
        .select(['blue', 'green', 'red', 'nir', 'swir1', 'swir2'])

    steps = int(np.floor(abs(startDate - endDate).days / interval))
    stepsize = datetime.timedelta(days=interval)
    print('Aggregating Landsat at ' + str(interval) + ' day intervals using ' + aggregation)

    for step in range(0, steps + 1):

        if aggregation == 'median':

            if step == 0:
                median = coll.filterDate(startDate, startDate + stepsize).median() \
                    .rename('blue_' + startDate.strftime('%Y%m%d'),
                            'green_' + startDate.strftime('%Y%m%d'),
                            'red_' + startDate.strftime('%Y%m%d'),
                            'nir_' + startDate.strftime('%Y%m%d'),
                            'swir1_' + startDate.strftime('%Y%m%d'),
                            'swir2_' + startDate.strftime('%Y%m%d'))

                tsi = ee.Image([median])

            if step > 0:
                newdate = startDate + step * stepsize
                median = coll.filterDate(newdate, newdate + stepsize).median() \
                    .rename('blue_' + newdate.strftime('%Y%m%d'),
                            'green_' + newdate.strftime('%Y%m%d'),
                            'red_' + newdate.strftime('%Y%m%d'),
                            'nir_' + newdate.strftime('%Y%m%d'),
                            'swir1_' + newdate.strftime('%Y%m%d'),
                            'swir2_' + newdate.strftime('%Y%m%d'))

                tsi = ee.Image([tsi, median])


    print('Aggregation completed over ' + str(steps) + ' time steps.')
    tsi_list = []

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

        tsi_pt = ee.ImageCollection(tsi).getRegion(pts, 30).getInfo()

        ############################ here it gets tricky :)

        tsi_pt[0].append("ID")
        tsi_pt[1].append(id)

        # Append to output then get next feature
        tsi_list.append(tsi_pt)
        feat = layer.GetNextFeature()

    if write == True:

        print("write output table")
        with open(out_path, "w") as theFile:
            csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
            writer = csv.writer(theFile, dialect="custom")
            # Write the complete set of values (incl. the header) of the first entry
            for element in tsi_list[0]:
                writer.writerow(element)
            tsi_list.pop(0)
            # Now write the remaining entries, always pop the header
            for element in tsi_list:
                element.pop(0)
                for row in element:
                    writer.writerow(row)

    return tsi_list