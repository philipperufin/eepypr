import ee
import fct.exp

years = range(1987, 2020)
y = years[0]

for y in years:
    image = ee.Image('users/philipperufin/susadica_map_v02_'+ str(y))
    description = 'susadica_map_v02_'+ str(y)
    folder = 'SUSADICA_v02'
    scale = 30
    fct.exp.exportDrive(image, description, folder, scale)

