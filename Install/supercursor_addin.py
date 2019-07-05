# -*- coding: utf-8 -*-

"""
***************************************************************************
    supercursor_addin.py
    ---------------------
    Date                 : June 2019
    Copyright            : (C) 2019 by Alec Zoeller
    Email                : alec zoeller at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__version__ = '0.1'
__author__ = 'Alec Zoeller'
__copyright__ = '(c) 2019 by Alec Zoeller'


import os

import arcpy
import pythonaddins
import pyperclip


class TargetLayer(object):
    """Implementation for supercursor_addin.target_layer (ComboBox)"""
    def __init__(self):
        self.mxd = arcpy.mapping.MapDocument("CURRENT")
        #Loads all vector layers in dataframe to dropdown menu
        lyrs = [i.name for i in arcpy.mapping.ListLayers(self.mxd) if i.isFeatureLayer == True]
        self.items = lyrs
        if len(lyrs) > 0:
            self.target = lyrs[0]
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWWWWWWWWWWWWWWW'
        self.width = 'WWWWWWW'
    def onSelChange(self, selection):
        self.selection = selection
        self.target = selection
    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
        #Adjust as new layers are added to dataframe
        lyrs = [i.name for i in arcpy.mapping.ListLayers(self.mxd) if i.isFeatureLayer == True]
        self.items = lyrs
        if len(lyrs) > 0:
            self.target = lyrs[0]
            try:
                if not self.target == self.selection:
                    self.target = self.selection
            except AttributeError:
                pass
    def onEnter(self):
        pass
    def refresh(self):
        pass
        
        

class AddFeatures(object):
    """Implementation for supercursor_addin.add_features (Tool)"""
    def __init__(self):
        self.enabled = True #Initiallly false, with comments in combobox
        #self.cursor = 3
        self.shape = 'NONE'
        self.doubleclick = False
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        #Capture clicks in map canvas, create points if Point feature type
        self.x = x 
        self.y = y 
        
        try:
            self.shp = target_layer.target
        except NameError:
            pythonaddins.MessageBox('Select target layer from dropdown and retry.', 'Alert')
            pass
        desc = arcpy.Describe(self.shp)
        self.type = desc.shapeType
        
        #If feature is Polyline or Polygon, save points until doubleclick
        if not self.type == 'Point' and self.doubleclick == False:
            self.doubleclick = True
            self.list_pts = []
            self.list_pts.append([x,y])
        elif not self.type == 'Point' and self.doubleclick == True:
            self.list_pts.append([x,y])
        else:
            with arcpy.da.InsertCursor(self.shp, 'SHAPE@XY') as cursor:
                cursor.insertRow([(x, y)])
            arcpy.RefreshActiveView()
    def onMouseUp(self, x, y, button, shift):
        pass
    def onMouseUpMap(self, x, y, button, shift):
        pass
    def onMouseMove(self, x, y, button, shift):
        pass
    def onMouseMoveMap(self, x, y, button, shift):
        pass
    def onDblClick(self):
        #Create new feature if layer is Polyline or Polygon
        if self.doubleclick == False:
            pass
        else:
            self.list_pts.append([self.x,self.y])
            arr = arcpy.Array(arcpy.Point(i[0], i[1]) for i in self.list_pts)
            if self.type == 'Polyline':
                this_shape = arcpy.Polyline(arr)
            if self.type == 'Polygon':
                this_shape = arcpy.Polygon(arr)
            cursor = arcpy.InsertCursor(self.shp)
            feature = cursor.newRow()
            feature.shape = this_shape
            cursor.insertRow(feature)
            del cursor
            arcpy.RefreshActiveView()
            self.doubleclick = False
    def onKeyDown(self, keycode, shift):
        pass
    def onKeyUp(self, keycode, shift):
        pass
    def deactivate(self):
        pass
    def onCircle(self, circle_geometry):
        pass
    def onLine(self, line_geometry):
        pass
    def onRectangle(self, rectangle_geometry):
        pass

class DeleteFeatures(object):
    """Implementation for supercursor_addin.delete_features (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        try:
            target = target_layer.target
        except AttributeError:
            pythonaddins.MessageBox('Select target layer from dropdown and retry.', 'Alert')
        #Delete all selected features for the selected layer
        response = pythonaddins.MessageBox('All features will be deleted if none are'\
                        ' selected. Selected features will be deleted. Are you sure?', 
                        'Delete Features', 4)
        if response == 'Yes':
            with arcpy.da.UpdateCursor(target, 'OID@') as cursor:
                for row in cursor:
                    cursor.deleteRow()
            arcpy.RefreshActiveView()
        else:
            pass
        

class QueryCopy(object):
    """Implementation for supercursor_addin.copyquery (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        try:
            target = target_layer.target
        except AttributeError:
            pythonaddins.MessageBox('Select target layer from dropdown and retry.', 'Alert')
        oid = [i.name for i in arcpy.ListFields(target) if i.type == 'OID'][0]
        oidf = arcpy.AddFieldDelimiters(target, oid)
        oids = [i[0] for i in arcpy.da.SearchCursor(target, 'OID@')]
        #if len(oids) % 500 != 0:
        chunks = len(oids)/500 + 1
        query = ''
        #Iterate through 500 features at a time, maximum returned for each SQL query
        for i in range(chunks):
            subset_oids = oids[i*500:][:(((i+1) * 500) - 1)]
            #Only block of query - no "OR" in SQL query
            if chunks == 1:
                subset_query = '{0} IN ({1})'.format(oidf, ','.join(map(str, subset_oids)))
                query += subset_query
                #Copy query to clipboard
                pyperclip.copy(query)
                break
            if i == 0:
                subset_query = '{0} IN ({1})'.format(oidf, ','.join(map(str, subset_oids)))
                query += subset_query
            else:
                subset_query = '\nOR {0} IN ({1})'.format(oidf, ','.join(map(str, subset_oids)))
                query += subset_query
            #Copy query to clipboard
            pyperclip.copy(query)
                  