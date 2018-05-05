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
    print 'Running...'
    # Perhaps task.cancel() at some point.
    time.sleep(10)
  print 'Done.', task.status()

locations = pd.read_csv('locations_final.csv', header=None)

# Transforms an Image Collection with 1 band per Image into a single Image with items as bands
# Author: Jamie Vleeshouwer

def appendBand(current, previous):
    # Rename the band
    previous=ee.Image(previous)
    current = current.select([0,4])
    # Append it to the result (Note: only return current item on first element/iteration)
    accum = ee.Algorithms.If(ee.Algorithms.IsEqual(previous,None), current, previous.addBands(ee.Image(current)))
    # Return the accumulation
    return accum

county_region = ee.FeatureCollection('ft:1S4EB6319wWW2sWQDPhDvmSBIVrD3iEmCLYB7nMM')

imgcoll = ee.ImageCollection('MODIS/MYD11A2') \
    .filterBounds(ee.Geometry.Rectangle(-106.5, 50,-64, 23))\
    .filterDate('2002-12-31','2016-8-4')
img=imgcoll.iterate(appendBand)
img=ee.Image(img)

for loc1, loc2, lat, lon in locations.values:
    fname = '{}_{}'.format(int(loc1), int(loc2))
    print(fname)

    # offset = 0.11
    scale  = 500
    crs='EPSG:4326'

    # filter for a county
    region = county_region.filterMetadata('StateFips', 'equals', int(loc1))
    region = ee.FeatureCollection(region).filterMetadata('CntyFips', 'equals', int(loc2))
    region = ee.Feature(region.first())

    while True:
        try:
            export_oneimage(img.clip(region), 'data_temperature', fname, scale, crs)
        except Exception as e:
            print e
            print 'retry'
            time.sleep(10)
            continue
        break