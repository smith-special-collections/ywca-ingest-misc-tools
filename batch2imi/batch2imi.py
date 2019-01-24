import glob
import os
import argparse
import logging
import csv
import pprint

argparser = argparse.ArgumentParser()
argparser.add_argument("TOPFOLDER")
argparser.add_argument("OUTPUT")
argparser.add_argument("PARENTID")
argparser.add_argument("--parent-cmodel", default="islandora:compoundCModel", help="default: 'islandora:compoundCModel'")
argparser.add_argument("--child-cmodel", default="islandora:sp_basic_image", help="default: 'islandora:sp_basic_image'")
args = argparser.parse_args()

TOPFOLDER = args.TOPFOLDER

sourceFolder = TOPFOLDER.strip().strip('/')

findDatastreamsChild = ['OBJ','JP2','MODS', 'TN', 'LARGE_JPG', 'OCR', 'HOCR', 'JPG']
findDatastreamsParent = ['TN', 'OCR']
PARENT_TYPE = args.parent_cmodel
CHILD_TYPE = args.child_cmodel


def getSubDirs(sourceFolder):
    level1 = glob.glob(sourceFolder + '/*')
    parents = []
    for filename in level1:
        if os.path.isdir(filename):
            parents.append(filename)
    parents.sort()
    return parents

def getDatastreams(objectDir, findDatastreams):
    datastreams = {}
    for datastreamType in findDatastreams:
        datastreamInstances = glob.glob(objectDir  + '/' + datastreamType + '.*')
        datastreamInstances.sort()
        if len(datastreamInstances) > 1:
            logging.warning("More than one instances of %s datastream in %s. Arbitrarily picking %s." % (datastreamType, objectDir, datastreamInstances[0]))
        elif len(datastreamInstances) < 1:
            logging.error("No instances of %s datastream in %s" % (datastreamType, objectDir))
        else:
            datastreamFile = datastreamInstances[0]
            datastreams[datastreamType] = datastreamFile
    return datastreams

class CompoundObject():
    def __init__(self, parent):
        self.data = {
            'path': parent,
            'datastreams': [],
            'type': PARENT_TYPE,
            'children': [],
        }
        self.data['datastreams'] = getDatastreams(parent, findDatastreamsParent)
        children_s = getSubDirs(parent)
        for child in children_s:
            childData = {
                'path': child,
                'datastreams': [],
                'type': CHILD_TYPE,
            }
            childData['datastreams'] = getDatastreams(child, findDatastreamsChild)
            self.data['children'].append(childData)
    def getParentTabular(self):
        myline = self.data['datastreams']
        myline['path'] = self.data['path']
        myline['type'] = self.data['type']
        myline['localIndex'] = 1
        return(myline)
    def getChildrenTabular(self):
        mydata = []
        localIndex = 1
        for child in self.data['children']:
            myline = child['datastreams']
            myline['path'] = child['path']
            myline['type'] = child['type']
            myline['localIndex'] = localIndex
            mydata.append(myline)
            localIndex = localIndex + 1
        return mydata
    def getLength(self):
        return len(self.data['children']) + 1 # +1 to account for the parent

class Batch():
    def __init__(self):
        self.object_s = []
    def addObject(self, object):
        self.object_s.append(object)
    def getLength(self):
        length = 0
        for object in self.object_s:
            length = length + object.getLength()
        return length
    def getImiBatch(self):
        # Assuming that all objects in the batch are a compound of some kind
        myData = []
        for object in self.object_s:
            myParentLine = object.getParentTabular()
            myData.append(myParentLine)
            for child in object.getChildrenTabular():
                myChildLine = child
                myData.append(myChildLine)
        globalIndex = 1
        currentParentGlobalIndexNumber = None
        for myLine in myData:
            myLine['globalIndex'] = globalIndex
            myLine['parentLineNumber'] = None
            if myLine['type'] == PARENT_TYPE:
                currentParentGlobalIndexNumber = globalIndex
                myLine['parentLineNumber'] = args.PARENTID
            else:
                myLine['parentLineNumber'] = currentParentGlobalIndexNumber
            globalIndex = globalIndex + 1
        return myData

if __name__ == '__main__':
    parent_s = getSubDirs(sourceFolder)

    batch = Batch()
    for parent in parent_s:
        compoundObject = CompoundObject(parent)
        batch.addObject(compoundObject)
    table = batch.getImiBatch()

    csvFieldsSet = set()
    for line in table:
        csvFieldsSet.update(line.keys())
    fieldnames = list(csvFieldsSet)
    fieldnames.sort()
    with open(args.OUTPUT, 'w', newline='') as csvfile:
        csvWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

        csvWriter.writeheader()
        for line in table:
            csvWriter.writerow(line)
