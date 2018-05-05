import ee
import time
import pandas as pd

ee.Initialize()

def export_oneimage(img,folder,name,scale,crs):
  full_file_name = folder + '_' + name
  task = ee.batch.Export.image.toCloudStorage(img, full_file_name,\
          bucket='cs231n-satellite-images',\
          fileNamePrefix=full_file_name,\
          scale=scale,\
          crs=crs)
  task.start()
  while task.status()['state'] == 'RUNNING':
    print ('Running...')
    time.sleep(10)
  print ('Done.', task.status())

locations = pd.read_csv('locations_final.csv',header=None)


def appendBand(current, previous):
    previous=ee.Image(previous)
    current = current.select([0,1,2,3,4,5,6])
    accum = ee.Algorithms.If(ee.Algorithms.IsEqual(previous,None), current, previous.addBands(ee.Image(current)))
    return accum

county_region = ee.FeatureCollection('ft:1S4EB6319wWW2sWQDPhDvmSBIVrD3iEmCLYB7nMM')

imgcoll = ee.ImageCollection('MODIS/MOD09A1') \
    .filterBounds(ee.Geometry.Rectangle(-106.5, 50,-64, 23))\
    .filterDate('2002-12-31','2016-8-4')
img=imgcoll.iterate(appendBand)
img=ee.Image(img)

img_0=ee.Image(ee.Number(-100))
img_16000=ee.Image(ee.Number(16000))

img=img.min(img_16000)
img=img.max(img_0)

for loc1, loc2, lat, lon in locations.values:
    fname = '{}_{}'.format(int(loc1), int(loc2))

    scale  = 500
    crs='EPSG:4326'

    region = county_region.filterMetadata('StateFips', 'equals', int(loc1))
    region = ee.FeatureCollection(region).filterMetadata('CntyFips', 'equals', int(loc2))
    region = ee.Feature(region.first())

    while True:
        try:
            export_oneimage(img.clip(region), 'data_image_full', fname, scale, crs)
        except Exception as e:
            print (e)
            print ('retry')
            time.sleep(10)
            continue
        break