# ee.pypr, philippe rufin 2020
# philippe.rufin@googlemail.com
# partly inspired by baumi-berlin
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
import os
import ogr
import csv
import pandas as pd
import fct.cld
import fct.lnd
import fct.sen
import matplotlib.pyplot as plt

def TSS(point_shape, id_string, startDate, endDate,
        write=True, out_path=None, driver='ESRI Shapefile', archive='LND', harmonize_l8=True):

    if driver == 'ESRI Shapefile':
        drv = ogr.GetDriverByName('ESRI Shapefile')
    if not driver == 'ESRI Shapefile':
        drv = ogr.GetDriverByName(driver)

    dataSource = drv.Open(point_shape, 0)

    layer = dataSource.GetLayer()
    feat = layer.GetNextFeature()

    if archive == 'LND':
        collection = fct.lnd.LND(startDate, endDate)
    if archive == 'SEN':
        collection = fct.sen.SEN(startDate, endDate)
    if archive == 'SEN_TOA':
        collection = fct.sen.SEN_TOA(startDate, endDate)

    tss_list = []

    while feat:
        id = feat.GetField(id_string)
        print("point id " + str(id))

        xCoord = feat.GetGeometryRef().GetPoint()[0]
        yCoord = feat.GetGeometryRef().GetPoint()[1]
        pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}

        if ((archive == 'SEN') | (archive == 'SEN_TOA')):
            tss = collection.getRegion(pts, 10).getInfo()
            tss[0].append("ID")

            for i in range(1, len(tss)):
                tss[i].append(id)

            val_reduced = []
            for val in tss:
                if not None in val:
                    val_reduced.append(val)
            tss_list.append(val_reduced)
            feat = layer.GetNextFeature()

        if archive == 'LND':
            tss = collection.getRegion(pts, 30).getInfo()
            tss[0].append("ID")

            for i in range(1, len(tss)):
                tss[i].append(id)

            val_reduced = []
            for val in tss:
                if not None in val:
                    sceneID = val[0]
                    p1 = sceneID.find("L")
                    sceneID = sceneID[p1:]
                    val[0] = sceneID
                    val_reduced.append(val)

            tss_list.append(val_reduced)
            feat = layer.GetNextFeature()

    if ((archive == 'LND') & (harmonize_l8 == True)):
        print('harmonizing OLI reflectances based on OLS regression coefficients in https://doi.org/10.1016/j.rse.2015.12.024')
        for p in range(0, len(tss_list)):
            for r in range(0, len(tss_list[p])):
                if 'LC08' in tss_list[p][r][0]:
                    tss_list[p][r][4] = np.int((10000 * 0.0183) + (0.8850 * tss_list[p][r][4]))
                    tss_list[p][r][5]= np.int((10000 * 0.0123) + (0.9317 * tss_list[p][r][5]))
                    tss_list[p][r][6] = np.int((10000 * 0.0123) + (0.9372 * tss_list[p][r][6]))
                    tss_list[p][r][7]= np.int((10000 * 0.0448) + (0.8339 * tss_list[p][r][7]))
                    tss_list[p][r][8]= np.int((10000 * 0.0306) + (0.8639 * tss_list[p][r][8]))
                    tss_list[p][r][9] = np.int((10000 * 0.0116) + (0.9165 * tss_list[p][r][9]))

    if write == True:

        print("write output table")
        if out_path == None:
            out_path = os.path.splitext(point_shape)[0] + '_TSS_' + archive + '_' + str(startDate.year) + '-' + str(
                endDate.year) + '.csv'

        with open(out_path, "w") as theFile:
            csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
            writer = csv.writer(theFile, dialect="custom")

            for element in tss_list[0]:
                writer.writerow(element)
            tss_list.pop(0)

            for element in tss_list:
                element.pop(0)
                for row in element:
                    writer.writerow(row)


def TSS_LND(point_shape, id_string, startDate, endDate, write, out_path, driver='ESRI Shapefile'):

    collection = fct.lnd.LND_glob(startDate, endDate)
    tss_list = []

    if driver == 'ESRI Shapefile':
        drv = ogr.GetDriverByName('ESRI Shapefile')
    if not driver == 'ESRI Shapefile':
        drv = ogr.GetDriverByName(driver)

    dataSource = drv.Open(point_shape, 0)
    layer = dataSource.GetLayer()
    feat = layer.GetNextFeature()

    while feat:
        id = feat.GetField(id_string)
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

    return tss_list


def TSS_SEN(point_shape, id_string, startDate, endDate, write, out_path, driver='ESRI Shapefile'):

    collection = fct.sen.SEN(startDate, endDate)
    tss_list = []

    if driver == 'ESRI Shapefile':
        drv = ogr.GetDriverByName('ESRI Shapefile')
    if not driver == 'ESRI Shapefile':
        drv = ogr.GetDriverByName(driver)

    dataSource = drv.Open(point_shape, 0)

    layer = dataSource.GetLayer()
    feat = layer.GetNextFeature()

    while feat:
        id = feat.GetField(id_string)
        print("point id " + str(id))

        xCoord = feat.GetGeometryRef().GetPoint()[0]
        yCoord = feat.GetGeometryRef().GetPoint()[1]
        pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}

        tss = collection.getRegion(pts, 10).getInfo()
        tss[0].append("ID")

        for i in range(1, len(tss)):
            tss[i].append(id)

        # Remove right away the masked values, and some remnants from the sceneID
        val_reduced = []
        for val in tss:
            if not None in val:
                #sceneID = val[0]
                #p1 = sceneID.find("S")
                #sceneID = sceneID[p1:]
                #val[0] = sceneID
                val_reduced.append(val)
                #val_reduced.append(val[0])
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



def TSS_SEN_TOA(point_shape, id_string, startDate, endDate, write, out_path):

    collection = fct.sen.SEN_TOA(startDate, endDate)
    tss_list = []

    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(point_shape, 0)
    layer = dataSource.GetLayer()
    feat = layer.GetNextFeature()

    while feat:
        id = feat.GetField(id_string)
        print("point id " + str(id))

        xCoord = feat.GetGeometryRef().GetPoint()[0]
        yCoord = feat.GetGeometryRef().GetPoint()[1]
        pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}

        tss = collection.getRegion(pts, 10).getInfo()
        tss[0].append("ID")

        for i in range(1, len(tss)):
            tss[i].append(id)

        # Remove right away the masked values, and some remnants from the sceneID
        val_reduced = []
        for val in tss:
            if not None in val:
                #sceneID = val[0]
                #p1 = sceneID.find("S")
                #sceneID = sceneID[p1:]
                #val[0] = sceneID
                val_reduced.append(val)
                #val_reduced.append(val[0])
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


def TSS_PR(csv_path, archive='LND', index=['NDVI', 'EVI', 'TCB', 'TCG', 'TCW', 'NDWI', 'NDMI'], out_path=None):
    ts = pd.read_csv(csv_path)

    if archive == 'LND':
        ts['date'] = pd.to_datetime(ts['d'].str[12:20], format='%Y%m%d')

    if archive == 'SEN':
        ts['date'] = pd.to_datetime(ts['d'].str[0:8], format='%Y%m%d')

    if 'NDVI' in index:
        ts['NDVI'] = (ts['nir'] - ts['red']) / (ts['nir'] + ts['red'])

    if 'EVI' in index:
        ts['EVI'] = (2.5 * (((ts['nir']/10000) - ts['red']/10000)) / ((ts['nir']/10000) + 6 * (ts['red']/10000) - 7.5 * (ts['blue']/10000) + 1))

    if 'NDWI' in index:
        ts['NDWI'] = ((ts['swir1'] + ts['red']) + (ts['nir'] + ts['blue'])) / ((ts['swir1'] + ts['red']) - (ts['nir'] + ts['blue']))

    if 'NDMI' in index:
        ts['NDMI'] = (ts['nir'] - ts['swir1']) / (ts['nir'] + ts['swir1'])

    if 'TCB' in index:
        co = [0.2043,  0.4158,  0.5524, 0.5741,  0.3124,  0.2303]
        ts['TCB'] = (ts['blue'] * co[0] + ts['green'] * co[1] +ts['red'] * co[2] + ts['nir'] * co[3] + ts['swir1'] * co[4] + ts['swir2'] * co[5]) / 10000

    if 'TCG' in index:
        co = [-0.1603, -0.2819, -0.4934, 0.7940, -0.0002, -0.1446]
        ts['TCG'] = (ts['blue'] * co[0] + ts['green'] * co[1] + ts['red'] * co[2] + ts['nir'] * co[3] + ts['swir1'] * co[4] + ts['swir2'] * co[5]) / 10000

    if 'TCW' in index:
        co = [0.0315,  0.2021,  0.3102, 0.1594, -0.6806, -0.6109]
        ts['TCW'] = (ts['blue'] * co[0] + ts['green'] * co[1] + ts['red'] * co[2] + ts['nir'] * co[3] + ts['swir1'] * co[4] + ts['swir2'] * co[5]) / 10000

    print("write output table")
    if out_path == None:
        out_path = os.path.splitext(csv_path)[0] + '_PR.csv'

    ts.to_csv(out_path, index=False)