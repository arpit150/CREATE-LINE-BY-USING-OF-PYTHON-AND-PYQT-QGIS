from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog,QLabel,QHBoxLayout,QMessageBox
from qgis.core import *
from qgis.gui import *
from qgis.core import Qgis
from .line_create_dialog import line_createDialog

class Map_Tool(QgsMapTool):
    def __init__(self, iface):
        QgsMapTool.__init__(self, iface.mapCanvas())
        self.canvas = iface.mapCanvas()
        self.iface = iface
        self.status = 0
        self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self.rb.setColor(QColor(255, 70, 0, 200))
        self.rb.setWidth(5)
        self.rb.setBrushStyle(Qt.NoBrush) 

    def submit(self):
        QMessageBox.information(self.iface.mainWindow(),"Info Message", "data is submit")
        id = (self.dlg.lineEdit.text())
        print('id =' , id)
        
        current_layer = self.iface.mapCanvas().currentLayer()
        pr = current_layer.dataProvider()
        caps = current_layer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.AddFeatures:
            feat = QgsFeature(current_layer.fields())
            feat.setAttribute('id' , id )
            feat.setGeometry(self.rb.asGeometry())
            pr.addFeature(feat)
            current_layer.updateExtents()
            current_layer.commitChanges()
            current_layer.triggerRepaint()

        else:
           self.iface.messageBar().pushMessage("Edit Layer", "Layer Is ReadOnly", level=Qgis.Warning)
  

    def canvasMoveEvent(self,event):
        if self.rb.numberOfVertices() > 0 and self.status ==1:
            self.rb.removeLastPoint(0)
            self.rb.addPoint(self.toMapCoordinates(event.pos()))
    
  
    def canvasReleaseEvent(self, event):
        if event.button()==Qt.LeftButton:
            if self.status ==0:
                self.rb.reset(QgsWkbTypes.LineGeometry)
                self.status =1
            self.rb.addPoint(self.toMapCoordinates(event.pos()))
        else:
            if self.rb.numberOfVertices() > 1:
                self.status = 0
                self.dlg = line_createDialog()
                self.dlg.pushButton.clicked.connect(self.submit)
                self.dlg.show()


    def intersection(self):
        current_layer = self.iface.mapCanvas().currentLayer()
        print (current_layer[0].name()) 
        print (current_layer[1].name()) 
        selections=[] 
        for f in current_layer[0].getFeatures():
            for a in current_layer[1].getFeatures():
                if a.geometry().intersects(f.geometry()):
                    intersection = a.geometry().intersection(f.geometry())
                    print (intersection.exportToWkt())
                    selections.append( f.id() )
                    break 

        print (len(selections))
        print (current_layer[0].selectedFeatureCount())
        print (current_layer[1].featureCount())
