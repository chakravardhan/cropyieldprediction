import os
# import mount_bucket

bucketLocation = '/'
def setBucketLocation(loc):
    global bucketLocation
    bucketLocation = os.path.expanduser(loc)

def walk(prefix, datatype, delim='_'):
    realPrefix = prefix + delim + datatype + delim
    for filename in os.listdir(bucketLocation):
        if not filename.startswith(realPrefix):
            continue
        yield (prefix, datatype, filename[len(realPrefix):])
        
def getFullPath(fileInfo, delim='_'):
    prefix, datatype, file = fileInfo
    filename = prefix + delim + datatype + delim + file
    return os.path.join(bucketLocation, filename)

def replaceDatatype(fileInfo, newDatatype):
    prefix, _, file = fileInfo
    return (prefix, newDatatype, file)

def getBucketLocation():
    return bucketLocation
