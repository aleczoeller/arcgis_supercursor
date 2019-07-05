This is a stub project created by the ArcGIS Desktop Python AddIn Wizard.

Tool allows you to select any vector layer in your Data Frame and (with the click of a button) create new features (with "Add Features") or delete selected ones (with "Delete Features").

The "Copy Query" button copies a query identifying ALL FEATURES selected that can be pasted (ctrl+v) into a Definition Query for that layer.

"Supercursor" refers to the feature data cursors that enables these functions.


TO INSTALL, RUN makeaddin.py with ArcGIS Desktop 10.0+ Python 2.7 interpretter (or double-click file), then double-click to run the file 
supercursor.esriaddin that is created by that script.  Toolbar is then accessible in ArcMap for immediate use.

MANIFEST
========

README.txt   : This file

makeaddin.py : A script that will create a .esriaddin file out of this 
               project, suitable for sharing or deployment

config.xml   : The AddIn configuration file

Images/*     : all UI images for the project (icons, images for buttons, 
               etc)

Install/*    : The Python project used for the implementation of the
               AddIn. The specific python script to be used as the root
               module is specified in config.xml.
