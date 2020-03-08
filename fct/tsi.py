import numpy as np
import datetime
import csv
import ee
import ogr
import fct.cld
import fct.lnd

def TSI(point_shape, startDate, endDate, interval, aggregation, write, out_path):

    collection = fct.lnd.LND_glob(startDate, endDate)

    #print('Aggregation completed yielding ' + str(len(tsi.bandNames)) + ' bands.')
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
        pts = ee.FeatureCollection(ee.Geometry(pts))

        tsi_pt = collection.getRegion(pts, 30).getInfo()

        ############################ here it gets tricky :)

        tsi_pt[0].append("ID")

        for i in range(1, len(tsi_pt)):
            tsi_pt[i].append(id)

        # Remove right away the masked values, and some remnants from the sceneID
        val_reduced = []
        for val in tsi_pt:
            if not None in val:
                sceneID = val[0]
                sceneID = sceneID[sceneID.find("L"):]
                val[0] = sceneID
                #val.append(sceneID[12:])
                val_reduced.append(val)

        # Append to output then get next feature
        tsi_list.append(val_reduced)
        feat = layer.GetNextFeature()

    for entry in tsi_list:
        print(entry[2][0][12:])

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

    return tsi


"""    it = 0
    for feat in layer:
        if it == 0:
            xCoord = [feat.GetGeometryRef().GetPoint()[0]]
            yCoord = [feat.GetGeometryRef().GetPoint()[1]]

        if it > 1:
            xCoord = np.vstack(xCoord, feat.GetGeometryRef().GetPoint()[0])
            yCoord = np.vstack(yCoord, feat.GetGeometryRef().GetPoint()[1])
        it += 1
"""