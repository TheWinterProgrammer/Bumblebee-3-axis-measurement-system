	
# tabs_ui.py
  
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
  

import os, sys

# Import the measurement evaluation software

from MeasurementEvaluation import *

# Import the Point Creator

from MeasurementsPointCreator import *

# Import the measurement software

from MeasuringSoftware import *


#@section author Author
# *
# * Written by Sergej Maltsev

# This creates a tab view of the measurement and evaluation software


  
# class for the tab layout
class Demo(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        
        # Ensure our window stays in front and give it a title
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint)
        self.setWindowTitle("ALF Robot Software")
        self.resize(800, 900)
        
        # Create and assign the main (vertical) layout.
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)    
        
        self.addTabs(vlayout)
        vlayout.addStretch()
        self.addButtonPanel(vlayout)
        self.show()
    #--------------------------------------------------------------------
    def addTabs(self, parentLayout):
        self.tabs = QTabWidget()
        page_1 = MainWindow()
        page_2 = MainWindowPointsCreator()
        page_3 = MainWindowEvaluation()
  
        self.tabs.addTab(page_1, "Measuring")
        self.tabs.addTab(page_2, "Point Creator")
        self.tabs.addTab(page_3, "Evaluation")
  
        parentLayout.addWidget(self.tabs)
    #--------------------------------------------------------------------
    def addButtonPanel(self, parentLayout):
        self.button = QPushButton("OK")
        self.button.clicked.connect(self.buttonAction)
  
        hlayout = QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(self.button)
        parentLayout.addLayout(hlayout)
    #--------------------------------------------------------------------
    def buttonAction(self):
        page = self.tabs.currentWidget()
        page.doAction()
    #--------------------------------------------------------------------
  
# ========================================================        

# create object of the class
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())


# Translate asset paths to useable format for PyInstaller
def resource_path(relative_path):
  if hasattr(sys, '_MEIPASS'):
      return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(os.path.abspath('.'), relative_path)
  