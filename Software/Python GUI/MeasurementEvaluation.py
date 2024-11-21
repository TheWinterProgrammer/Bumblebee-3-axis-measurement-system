import sys
import numpy as np
import pandas as pd 
import os
import csv

from scipy.stats import norm
import sys

from PyQt5 import QtCore

from PyQt5.QtWidgets import (
    QApplication,
    QFormLayout,
    QLabel,
    QLineEdit,
    QWidget,
    QPushButton,
    QGridLayout,
    QGroupBox,
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Evaluation Software for the Measurements for CSV Files


# Create the figure for the histogramm and the 3D plot 
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=12, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi,facecolor='#ffffff')
        self.axes = self.fig.add_subplot(1,2,1)
        self.axes.tick_params(color='black', labelcolor='black')
        self.axes.locator_params(axis='x', nbins=4)
        self.axes.set_facecolor('#ffffff')
        self.axes3d = self.fig.add_subplot(1,2,2,projection='3d')
        self.axes3d.set_facecolor('#ffffff')
        self.axes3d.tick_params(color='black', labelcolor='black')
        super(MplCanvas, self).__init__(self.fig)

# save the two shown figure function
# input: imagename - name of the saved figure
        
    def saveFigure(self,imagename,evaluationDirection):
        self.axes.set_facecolor('w')
        if evaluationDirection == "Hom":
            self.axes.set_xlabel("$B$ in " +  r'$T$')
        else: 
            self.axes.set_xlabel("$G$ in " +  r'$T/mm$')
        self.axes.set_ylabel("number of values")
        self.axes3d.set_facecolor('w')
        self.axes3d.set_xlabel('X axis')
        self.axes3d.set_ylabel('Y axis')
        self.axes3d.set_zlabel('Z axis')
        self.axes.tick_params(color='black', labelcolor='black')
        self.axes3d.tick_params(color='black', labelcolor='black')
        self.fig.savefig(imagename, format="pdf", facecolor="white")
        self.axes.set_facecolor('#ffffff')
        self.axes3d.set_facecolor('#ffffff')
        self.axes.tick_params(color='black', labelcolor='black')
        self.axes3d.tick_params(color='black', labelcolor='black')

# ... (imports and initial code remain unchanged)

# Main Window for the Evaluation
class MainWindowEvaluation(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.measurementFolder = "Measurements"  # Folder name for Measurements

        # Window and figure size
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setWindowTitle("Measurement Evaluation")
        self.resize(800, 600)

        # Constants for data locations and calculations
        self.arrayLocPosx = 0
        self.arrayLocPosy = 1
        self.arrayLocPosz = 2

        self.arrayLocBx = 5
        self.arrayLocBy = 4
        self.arrayLocBz = 3

        self.minDistanceForCalc = 4  # Minimum distance for gradient calculation

        self.usedLocForBz = self.arrayLocBz  # Default used location for Bz

        # Default data for input fields
        self.dataLoaded = False
        self.filename = "Measurement test"
        self.imageName = "image.pdf"
        self.csvName = "data.csv"
        self.evaluationDirection = "Hom"

        self.evaluationGradientXText = "Evaluate Gx"
        self.evaluationGradientYText = "Evaluate Gy"
        self.evaluationGradientZText = "Evaluate Gz"
        self.evaluationGradientHomText = "Evaluate Bz"

        # UI Elements: Labels, Text Inputs, and Buttons
        self.evaluationGradient = QLabel("Gradient Evaluation")
        self.evaluatedFile = QLabel("No evaluated values")
        self.numberOfSteps = QLabel("Total measurement number")

        self.muLabel = QLabel("Average: ")
        self.sndLabel = QLabel("Standard distribution: ")

        filenameLabel = QLabel("Filename: ")
        imageSaveLabel = QLabel("Imagename: ")
        directionGradientLabel = QLabel("Direction gradient: ")

        # Button for evaluating the data
        buttonEvaluate = QPushButton("Evaluate", self)
        buttonEvaluate.clicked.connect(self.evaluate)  # Connect evaluate function

        # Text input fields
        self.filenameInput = QLineEdit()
        self.filenameInput.setText(self.filename)

        self.imageNameInput = QLineEdit()
        self.imageNameInput.setText(self.imageName)

        self.csvNameInput = QLineEdit()
        self.csvNameInput.setText(self.csvName)

        # Load, save, and direction buttons
        self.buttonLoadFile = QPushButton("Load file", self)
        self.buttonLoadFile.clicked.connect(self.loadFile)

        self.buttonSaveImage = QPushButton("Save image", self)
        self.buttonSaveImage.clicked.connect(self.saveImage)

        self.buttonSaveCsv = QPushButton("Save as csv", self)
        self.buttonSaveCsv.clicked.connect(self.saveCsv)

        self.buttonChangeToX = QPushButton("X", self)
        self.buttonChangeToX.clicked.connect(self.changeDirectionToX)

        self.buttonChangeToY = QPushButton("Y", self)
        self.buttonChangeToY.clicked.connect(self.changeDirectionToY)

        self.buttonChangeToZ = QPushButton("Z", self)
        self.buttonChangeToZ.clicked.connect(self.changeDirectionToZ)

        self.buttonChangeToHomo = QPushButton("Hom.", self)
        self.buttonChangeToHomo.clicked.connect(self.changeDirectionToHomo)
        self.buttonChangeToHomo.setStyleSheet("color : red")

        directionBzLabel = QLabel("Direction Bz: ")

        self.buttonChangeBzToX = QPushButton("X", self)
        self.buttonChangeBzToX.clicked.connect(self.changeDirectionBzToX)

        self.buttonChangeBzToY = QPushButton("Y", self)
        self.buttonChangeBzToY.clicked.connect(self.changeDirectionBzToY)

        self.buttonChangeBzToZ = QPushButton("Z", self)
        self.buttonChangeBzToZ.clicked.connect(self.changeDirectionBzToZ)
        self.buttonChangeBzToZ.setStyleSheet("color : red")

        # Layout
        layout = QGridLayout()
        row = 0

        # Add widgets in a structured manner
        layout.addWidget(self.evaluationGradient, row, 0, 1, 2)
        layout.addWidget(self.evaluatedFile, row, 2, 1, 2)
        layout.addWidget(self.numberOfSteps, row, 4, 1, 2)
        row += 1
        layout.addWidget(self.canvas, row, 0, 1, 8)
        row += 2
        layout.addWidget(self.muLabel, row, 0, 1, 2)
        layout.addWidget(self.sndLabel, row, 2, 1, 2)
        layout.addWidget(directionGradientLabel, row, 4, 1, 2)
        layout.addWidget(buttonEvaluate, row, 6, 1, 2)
        row += 1
        layout.addWidget(filenameLabel, row, 0, 1, 2)
        layout.addWidget(imageSaveLabel, row, 2, 1, 2)
        layout.addWidget(self.buttonChangeToX, row, 4)
        layout.addWidget(self.buttonChangeToY, row, 5)
        layout.addWidget(self.buttonChangeToZ, row, 6)
        layout.addWidget(self.buttonChangeToHomo, row, 7)
        row += 1
        layout.addWidget(self.filenameInput, row, 0, 1, 2)
        layout.addWidget(self.imageNameInput, row, 2, 1, 2)
        layout.addWidget(directionBzLabel, row, 4, 1, 2)
        row += 1
        layout.addWidget(self.buttonLoadFile, row, 0, 1, 2)
        layout.addWidget(self.buttonSaveImage, row, 2, 1, 2)
        layout.addWidget(self.buttonChangeBzToX, row, 4)
        layout.addWidget(self.buttonChangeBzToY, row, 5)
        layout.addWidget(self.buttonChangeBzToZ, row, 6)
        row += 1
        layout.addWidget(self.csvNameInput, row, 0, 1, 2)
        layout.addWidget(self.buttonSaveCsv, row, 2, 1, 2)

        # Setup data and timer for plotting
        self.hisdataSim = np.array([])
        self.data = np.array([])
        self.timer = QtCore.QTimer()

        # Timer for updating the plot
        self.timer.setInterval(10)
        self.timer.start()
        self.timer.timeout.connect(self.update_plot)

        self.setLayout(layout)

    # ... (Remaining methods are unchanged from the original code, keeping functionality intact)


    def update_plot(self):
        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes3d.cla()  # Clear the canvas 3d plot.
        self.canvas.axes.hist(self.hisdataSim, density=False, facecolor='r') # Plot the histogram
        self.canvas.axes.locator_params(axis='x', nbins=4)
        if self.dataLoaded: # Plot the data if loaded
            scatter = self.canvas.axes3d.scatter(self.data[:,self.arrayLocPosx],self.data[:,self.arrayLocPosy], self.data[:,self.arrayLocPosz], c=self.data[:,self.usedLocForBz],cmap="inferno")
            self.canvas.axes3d.legend(*scatter.legend_elements(num=5),
                    loc="upper right", title="$B_z$ in " +  r'$T$', fontsize=8)
        # Trigger the canvas to update and redraw.
        self.canvas.draw()

    # Button functions for the different directions of the magnetic field
    def changeDirectionBzToX(self):
        self.colorButtonResetBz()
        self.buttonChangeBzToX.setStyleSheet("color : red") 
        self.usedLocForBz = self.arrayLocBx


    def changeDirectionBzToY(self):
        self.colorButtonResetBz()
        self.buttonChangeBzToY.setStyleSheet("color : red") 
        self.usedLocForBz = self.arrayLocBy
    
    def changeDirectionBzToZ(self):
        self.colorButtonResetBz()
        self.buttonChangeBzToZ.setStyleSheet("color : red") 
        self.usedLocForBz = self.arrayLocBz

# Button functions for the different directions of the gradient
    def changeDirectionToX(self):
        self.colorButtonReset()
        self.buttonChangeToX.setStyleSheet("color : red") 
        self.evaluationDirection = "X"


    def changeDirectionToY(self):
        self.colorButtonReset()
        self.buttonChangeToY.setStyleSheet("color : red") 
        self.evaluationDirection = "Y"
    
    def changeDirectionToZ(self):
        self.colorButtonReset()
        self.buttonChangeToZ.setStyleSheet("color : red") 
        self.evaluationDirection = "Z"

# Button functions to evaluate the homogenity of the field
    def changeDirectionToHomo(self):
        self.colorButtonReset()
        self.buttonChangeToHomo.setStyleSheet("color : red") 
        self.evaluationDirection = "Hom"

# Button functions to load the file
    def loadFile(self):
        try:
            self.data = pd.read_csv(os.path.join(str(sys.path[0]), self.measurementFolder,self.filenameInput.text()), sep=',')
            self.data = np.array(self.data.values)
            self.hisdataSim = self.data[:,self.usedLocForBz].astype(float)
            self.buttonLoadFile.setText("File loaded")
            self.dataLoaded = True
        except:
            self.buttonLoadFile.setText("File not found")
            self.dataLoaded = False

# Button functions to evaluate data
    def evaluate(self):
        if self.dataLoaded:
            self.hisdataSim = self.data[:,self.usedLocForBz]
            self.evaluateAllData()
            

# Button functions to save Image
    def saveImage(self):
        try:
            self.canvas.saveFigure(self.imageNameInput.text(),self.evaluationDirection)
            self.buttonSaveImage.setText("Image saved")
        except:
            self.buttonSaveImage.setText("Image not saved")


    def saveCsv(self):
        try:
            self.saveCsvData()
            self.buttonSaveImage.setText("CSV saved")
        except:
            self.buttonSaveImage.setText("CSV not saved")

    def saveCsvData(self):
        self.csvDataName = os.path.join(str(sys.path[0]), str(self.csvNameInput.text()))
        self.csvDataHeader = ' value of ' + self.evaluationDirection + ' Gradient in ' +  r'$T/mm$'
        np.savetxt(self.csvDataName, self.hisdataSim, delimiter=',', fmt='%s', header=self.csvDataHeader, comments='')

# functions to change the color of the buttons
    def colorButtonReset(self):
        self.buttonChangeToX.setStyleSheet("color : white") 
        self.buttonChangeToY.setStyleSheet("color : white") 
        self.buttonChangeToZ.setStyleSheet("color : white") 
        self.buttonChangeToHomo.setStyleSheet("color : white") 

    def colorButtonResetBz(self):
        self.buttonChangeBzToX.setStyleSheet("color : white") 
        self.buttonChangeBzToY.setStyleSheet("color : white") 
        self.buttonChangeBzToZ.setStyleSheet("color : white") 

# function to evaluate the gradient and the homogenity
    def evaluateAllData(self):
        if self.evaluationDirection == "Hom":
            self.hisdataSim = self.hisdataSim.astype(float)
            self.evaluationGradient.setText(self.evaluationGradientHomText)
        elif self.evaluationDirection == "X": 
            self.hisdataSim = self.getGradientField(self.hisdataSim,self.data[:,self.arrayLocPosx].astype(float))
            self.evaluationGradient.setText(self.evaluationGradientXText)
        elif self.evaluationDirection == "Y": 
            self.hisdataSim = self.getGradientField(self.hisdataSim,self.data[:,self.arrayLocPosy].astype(float))
            self.evaluationGradient.setText(self.evaluationGradientYText)
        elif self.evaluationDirection == "Z": 
            self.hisdataSim = self.getGradientField(self.hisdataSim,self.data[:,self.arrayLocPosz].astype(float))
            self.evaluationGradient.setText(self.evaluationGradientZText)

        self.evaluatedFile.setText("total Values: " + str(len(self.hisdataSim)))
        self.numberOfSteps.setText("Total measurement number: " + str(len(self.data[:,self.usedLocForBz])))

        print(self.hisdataSim)
        mu, std = norm.fit(self.hisdataSim) 
        self.muLabel.setText("Mean: " + str(mu))
        self.sndLabel.setText("Std: " + str(std))

# function to calculate the gradient
    def getGradientField(self,field,pos):
            gradient = np.array([])
            for i in range(len(field)):
                for j in range(len(field)):
                    if i != j and abs(pos[i] - pos[j]) > self.minDistanceForCalc:
                        temp = abs((field[i] - field[j]) / (pos[i] - pos[j]))
                        gradient = np.append(gradient, temp)
            return gradient


# main function to create the object of the class
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindowEvaluation()
    window.show()
    sys.exit(app.exec_())
        