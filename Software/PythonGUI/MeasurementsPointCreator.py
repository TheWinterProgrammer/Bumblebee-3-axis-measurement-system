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
    QComboBox,
    QLabel,
    QStackedLayout,
    QLineEdit,
    QWidget,
    QPushButton,
    QGridLayout,
    QGroupBox,
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Custom matplotlib canvas for plotting 3D data
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Create a matplotlib figure with a 3D subplot
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#ffffff')
        self.axes3d = fig.add_subplot(111, projection='3d')  # 3D subplot
        self.axes3d.set_facecolor('#ffffff')  # Set background color
        super(MplCanvas, self).__init__(fig)

class MainWindowPointsCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Initialize variables
        self.points = [0, 0, 0]
        self.pointsFolder = ""  # Folder name for saving data
        self.dataLoaded = False

        # Default filenames
        self.filename = "Measurement test"
        self.imageName = "image.pdf"
        self.csvName = "data.csv"

        # Initialize UI labels and buttons
        self.createPointsText = QLabel("Point creator")
        self.totalPointNumberText = QLabel("Total points")
        self.totalPointNumber = QLabel("0")

        self.shapeNameLabel = QLabel("Shape:")
        self.buttonCreatePoints = QPushButton("Create Points", self)
        self.buttonCreatePoints.clicked.connect(self.createPoints)

        # Initialize input fields for filenames
        self.filenameInput = QLineEdit()
        self.filenameInput.setText(self.filename)

        self.imageNameInput = QLineEdit()
        self.imageNameInput.setText(self.imageName)

        self.csvNameInput = QLineEdit()
        self.csvNameInput.setText(self.csvName)

        self.csvDataHeader = 'x,y,z'

        # Canvas for 3D plotting
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Set up main layout with grid
        layout = QGridLayout()
        row = 0

        # Add widgets to the layout
        layout.addWidget(self.createPointsText, row, 0, 1, 1)
        layout.addWidget(self.totalPointNumberText, row, 2, 1, 1)
        layout.addWidget(self.totalPointNumber, row, 3, 1, 1)
        row += 1

        layout.addWidget(self.canvas, row, 0, 1, 4)
        row += 2

        layout.addWidget(self.buttonCreatePoints, row, 2, 1, 2)
        layout.addWidget(self.shapeNameLabel, row, 0, 1, 2)
        row += 1

        # Create a combo box for selecting the shape
        self.pageCombo = QComboBox()
        self.pageCombo.addItems(["cube", "cuboid", "slice", "sphere", "cylinder"])
        self.pageCombo.activated.connect(self.switchPage)

        # Stacked layout for multiple pages (shapes)
        self.stackedLayout = QStackedLayout()
        self.addCubePage()
        self.addCuboidPage()
        self.addSlicePage()
        self.addSpherePage()
        self.addCylinderPage()

        layout.addWidget(self.pageCombo, row, 0, 1, 2)
        layout.addLayout(self.stackedLayout, row, 2, 1, 2)
        row += 1

        # Export points button and input field
        self.filenameTextBox = QLineEdit()
        self.filenameTextBox.setText("measurement_points.csv")
        self.buttonExportPoints = QPushButton("Export points", self)
        self.buttonExportPoints.clicked.connect(self.createDataFile)

        layout.addWidget(self.filenameTextBox, row, 1)
        layout.addWidget(self.buttonExportPoints, row, 2)

        # Timer for updating the plot
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.start()
        self.timer.timeout.connect(self.update_plot)

        # Set main layout
        self.setLayout(layout)

    # Pages for each shape
    def addCubePage(self):
        # Page for creating cube
        self.page1 = QWidget()
        self.page1Layout = QFormLayout()
        self.cubeLengthTextBox = QLineEdit()
        self.cubeLengthTextBox.setText("10")
        self.cubeResolutionTextBox = QLineEdit()
        self.cubeResolutionTextBox.setText("10")
        self.page1Layout.addRow("Length:", self.cubeLengthTextBox)
        self.page1Layout.addRow("Resolution:", self.cubeResolutionTextBox)
        self.page1.setLayout(self.page1Layout)
        self.stackedLayout.addWidget(self.page1)

    def addCuboidPage(self):
        # Page for creating cuboid
        self.page2 = QWidget()
        self.page2Layout = QFormLayout()
        self.cuboidLengthXTextBox = QLineEdit()
        self.cuboidLengthYTextBox = QLineEdit()
        self.cuboidLengthZTextBox = QLineEdit()
        self.cuboidResolutionXTextBox = QLineEdit()
        self.cuboidResolutionYTextBox = QLineEdit()
        self.cuboidResolutionZTextBox = QLineEdit()
        self.page2Layout.addRow("Length X:", self.cuboidLengthXTextBox)
        self.page2Layout.addRow("Length Y:", self.cuboidLengthYTextBox)
        self.page2Layout.addRow("Length Z:", self.cuboidLengthZTextBox)
        self.page2Layout.addRow("Resolution X:", self.cuboidResolutionXTextBox)
        self.page2Layout.addRow("Resolution Y:", self.cuboidResolutionYTextBox)
        self.page2Layout.addRow("Resolution Z:", self.cuboidResolutionZTextBox)
        self.page2.setLayout(self.page2Layout)
        self.stackedLayout.addWidget(self.page2)

    def addSlicePage(self):
        # Page for creating slice
        self.page3 = QWidget()
        self.page3Layout = QFormLayout()
        self.sliceLengthXTextBox = QLineEdit()
        self.sliceLengthYTextBox = QLineEdit()
        self.sliceLengthZTextBox = QLineEdit()
        self.sliceResolutionXTextBox = QLineEdit()
        self.sliceResolutionYTextBox = QLineEdit()
        self.sliceResolutionZTextBox = QLineEdit()
        self.page3Layout.addRow("Length X:", self.sliceLengthXTextBox)
        self.page3Layout.addRow("Length Y:", self.sliceLengthYTextBox)
        self.page3Layout.addRow("Length Z:", self.sliceLengthZTextBox)
        self.page3Layout.addRow("Resolution X:", self.sliceResolutionXTextBox)
        self.page3Layout.addRow("Resolution Y:", self.sliceResolutionYTextBox)
        self.page3Layout.addRow("Resolution Z:", self.sliceResolutionZTextBox)
        self.page3.setLayout(self.page3Layout)
        self.stackedLayout.addWidget(self.page3)

    def addSpherePage(self):
        # Page for creating sphere
        self.page4 = QWidget()
        self.page4Layout = QFormLayout()
        self.sphereRadiusTextBox = QLineEdit()
        self.sphereRadiusTextBox.setText("10")
        self.sphereResolutionRadialTextBox = QLineEdit()
        self.sphereResolutionRadialTextBox.setText("10")
        self.sphereResolutionAngularTextBox = QLineEdit()
        self.sphereResolutionAngularTextBox.setText("10")
        self.page4Layout.addRow("Radius:", self.sphereRadiusTextBox)
        self.page4Layout.addRow("Resolution Radial:", self.sphereResolutionRadialTextBox)
        self.page4Layout.addRow("Resolution Angular:", self.sphereResolutionAngularTextBox)
        self.page4.setLayout(self.page4Layout)
        self.stackedLayout.addWidget(self.page4)

    def addCylinderPage(self):
        # Page for creating cylinder
        self.page5 = QWidget()
        self.page5Layout = QFormLayout()
        self.cylinderRadiusTextBox = QLineEdit()
        self.cylinderRadiusTextBox.setText("10")
        self.cylinderResolutionRadialTextBox = QLineEdit()
        self.cylinderResolutionRadialTextBox.setText("10")
        self.cylinderLengthTextBox = QLineEdit()
        self.cylinderLengthTextBox.setText("10")
        self.cylinderResolutionAngularTextBox = QLineEdit()
        self.cylinderResolutionAngularTextBox.setText("10")
        self.page5Layout.addRow("Radius:", self.cylinderRadiusTextBox)
        self.page5Layout.addRow("Resolution Radial:", self.cylinderResolutionRadialTextBox)
        self.page5Layout.addRow("Length:", self.cylinderLengthTextBox)
        self.page5Layout.addRow("Resolution Angular:", self.cylinderResolutionAngularTextBox)
        self.page5.setLayout(self.page5Layout)
        self.stackedLayout.addWidget(self.page5)

    def switchPage(self):
        # Change stacked layout page based on combo box selection
        self.stackedLayout.setCurrentIndex(self.pageCombo.currentIndex())

    def update_plot(self):
        self.canvas.axes3d.cla()  # Clear the canvas 3d plot.
        self.canvas.axes3d.scatter(self.points[0],self.points[1],self.points[2],cmap="inferno")
        # Trigger the canvas to update and redraw.
        self.canvas.draw()

    def inputCheck(self, text):
            # Check if text is a digit and greater than zero after conversion
        if text.isdigit() and int(text) > 0:
            return True
        else:
            return False
        
    def createDataFile(self, filename="measurement_points.csv"):
        try:
        # Create the file path
            self.csvDataName = os.path.join(
                str(sys.path[0]), self.pointsFolder, str(self.filenameTextBox.text())
            )
            
            # Save the points array directly to CSV
            np.savetxt(
                self.csvDataName,              # File path
                self.points.transpose(),       # 2D array to save
                delimiter=',',                 # Column delimiter
                fmt='%s',                      # Format for each element
                header=self.csvDataHeader,     # Header for CSV
                comments=''                    # Avoid '#' before header line
            )
        except:
            print("Error")


    def createPoints(self):
            try:
                class TargetDefinition:
                    pass
                points = self.points
                if self.pageCombo.currentText() == "cube" and self.inputCheck(self.cubeLengthTextBox.text()) and self.inputCheck(self.cubeResolutionTextBox.text()):
                    # Create a cube based on length and resolution
                    TargetDefinition.shape = 'cube'
                    TargetDefinition.length = [int(self.cubeLengthTextBox.text())] # Half-length of cube
                    TargetDefinition.resolution = int(self.cubeResolutionTextBox.text())  # Step size for meshgrid
                    points = make_target(TargetDefinition)

                elif self.pageCombo.currentText() == "cuboid" and self.inputCheck(self.cuboldLengthXTextBox.text()) and self.inputCheck(self.cuboldLengthYTextBox.text()) and self.inputCheck(self.cuboldLengthZTextBox.text()):
                    # Create a cube based on length and resolution
                    TargetDefinition.shape = 'cuboid'
                    TargetDefinition.length = [int(self.cuboldLengthXTextBox.text()),int(self.cuboldLengthYTextBox.text()),int(self.cuboldLengthZTextBox.text())] # Half-length of cube
                    TargetDefinition.resolution = [int(self.cuboldResolutionXTextBox.text()),int(self.cuboldResolutionYTextBox.text()),int(self.cuboldResolutionZTextBox.text())]  # Step size for meshgrid
                    points = make_target(TargetDefinition)

                elif self.pageCombo.currentText() == "slice" and self.inputCheck(self.sliceLengthXTextBox.text()) and self.inputCheck(self.sliceLengthYTextBox.text()) and self.inputCheck(self.sliceLengthZTextBox.text()):
                    TargetDefinition.shape = 'slice'
                    TargetDefinition.length = [int(self.sliceLengthXTextBox.text()),int(self.sliceLengthYTextBox.text()),int(self.sliceLengthZTextBox.text())]
                    TargetDefinition.resolution = [int(self.sliceResolutionXTextBox.text()),int(self.sliceResolutionYTextBox.text()),int(self.sliceResolutionZTextBox.text())]
                    points = make_target(TargetDefinition)

                elif self.pageCombo.currentText() == 'sphere' and self.inputCheck(self.sphereRadiusTextBox.text()) and self.inputCheck(self.sphereResolutionRadialTextBox.text()) and self.inputCheck(self.sphereResolutionAngularTextBox.text()):
                    TargetDefinition.shape = 'sphere'
                    TargetDefinition.radius = int(self.sphereRadiusTextBox.text())
                    TargetDefinition.resol_radial = int(self.sphereResolutionRadialTextBox.text())
                    TargetDefinition.resol_angular = int(self.sphereResolutionAngularTextBox.text())
                    points = make_target(TargetDefinition)
                
                elif self.pageCombo.currentText() == 'cylinder' and self.inputCheck(self.cylinderRadiusTextBox.text()) and self.inputCheck(self.cylinderResolutionRadialTextBox.text()) and self.inputCheck(self.cylinderLengthTextBox.text()) and self.inputCheck(self.cylinderResolutionRadialTextBox.text()):
                    TargetDefinition.shape = 'cylinder'
                    # Create a cylinder based on radius, length, and resolution
                    TargetDefinition.radius = int(self.cylinderRadiusTextBox.text())
                    TargetDefinition.resol_angular = int(self.cylinderResolutionAngularTextBox.text())
                    TargetDefinition.length = int(self.cylinderLengthTextBox.text())
                    TargetDefinition.resol_radial = int(self.cylinderResolutionRadialTextBox.text())
                    points = make_target(TargetDefinition)
            except:
                print("Error")
            self.points = points

class Points:
        def __init__(self):
            self.x1 = None
            self.x2 = None
            self.x3 = None
# Function to generate a target shape based on the provided definition
def make_target(TargetDefinition):

    points = Points()

    # Handle different shapes based on TargetDefinition.shape
    if TargetDefinition.shape == 'cube':
        # Create a cube based on length and resolution
        r1 = TargetDefinition.length[0] / 2  # Half-length of cube
        d1 = TargetDefinition.length[0] / max(TargetDefinition.resolution - 1, 1)

        # Generate grid points for the cube
        x1, x2, x3 = np.meshgrid(
            np.arange(-r1, r1 + d1, d1),
            np.arange(-r1, r1 + d1, d1),
            np.arange(-r1, r1 + d1, d1),
            indexing='ij'
        )

    elif TargetDefinition.shape == 'cuboid':
        # Create a cuboid (rectangular box) based on length and resolution
        r1 = TargetDefinition.length[0] / 2
        r2 = TargetDefinition.length[1] / 2
        r3 = TargetDefinition.length[2] / 2
        d1 = TargetDefinition.length[0] / (TargetDefinition.resolution[0] - 1)
        d2 = TargetDefinition.length[1] / (TargetDefinition.resolution[1] - 1)
        d3 = TargetDefinition.length[2] / (TargetDefinition.resolution[2] - 1)

        # Generate grid points using meshgrid
        x1, x2, x3 = np.meshgrid(
            np.arange(-r1, r1 + d1, d1),
            np.arange(-r2, r2 + d2, d2),
            np.arange(-r3, r3 + d3, d3),
            indexing='ij'
        )

    elif TargetDefinition.shape == 'slice':
        # Create a slice based on specified lengths and resolutions
        r1 = TargetDefinition.length[0] / 2
        r2 = TargetDefinition.length[1] / 2
        r3 = TargetDefinition.length[2] / 2
        d1 = TargetDefinition.length[0] / (TargetDefinition.resolution[0] - 1)
        d2 = TargetDefinition.length[1] / (TargetDefinition.resolution[1] - 1)
        d3 = TargetDefinition.length[2] / (TargetDefinition.resolution[2] - 1)

        # Special case where one of the dimensions might be 0
        if d1 == 0:
            x1, x2, x3 = np.meshgrid(0, -r2 + np.arange(0, r2 * 2 + d2, d2), -r3 + np.arange(0, r3 * 2 + d3, d3))
        elif d2 == 0:
            x1, x2, x3 = np.meshgrid(-r1 + np.arange(0, r1 * 2 + d1, d1), 0, -r3 + np.arange(0, r3 * 2 + d3, d3))
        elif d3 == 0:
            x1, x2, x3 = np.meshgrid(-r1 + np.arange(0, r1 * 2 + d1, d1), -r2 + np.arange(0, r2 * 2 + d2, d2), 0)
        else:
            x1, x2, x3 = np.meshgrid(-r1 + np.arange(0, r1 * 2 + d1, d1), -r2 + np.arange(0, r2 * 2 + d2, d2), -r3 + np.arange(0, r3 * 2 + d3, d3))
    
    elif TargetDefinition.shape == 'sphere':
        # Create a sphere based on radial and angular resolution
        r = TargetDefinition.radius
        d1 = TargetDefinition.radius / (TargetDefinition.resol_radial - 1)
        d2 = np.pi / (TargetDefinition.resol_angular - 1)
        d3 = 2 * np.pi / (TargetDefinition.resol_angular - 1)

        # Generate spherical coordinates
        ra, theta, phi = np.meshgrid(0 + np.arange(0, r + d1, d1), 0 + np.arange(0, np.pi + d2, d2), -np.pi + np.arange(0, np.pi * 2 + d3, d3))

        # Convert spherical to Cartesian coordinates
        x1 = ra * np.sin(theta) * np.cos(phi)
        x2 = ra * np.sin(theta) * np.sin(phi)
        x3 = ra * np.cos(theta)
    
    elif TargetDefinition.shape == 'cylinder':
        # Create a cylinder based on radius, length, and resolution
        r = TargetDefinition.radius
        d2 = 2 * np.pi / (TargetDefinition.resol_angular - 1)
        d3 = TargetDefinition.length / (TargetDefinition.resol_angular - 1)
        l1 = TargetDefinition.length / 2
        
        # Different cases based on radial resolution
        if TargetDefinition.resol_radial == 1:
            ra, phi, z = np.meshgrid(r + np.arange(0, r + d1, d1), 0 + np.arange(0, 2 * np.pi + d2, d2), -l1 + np.arange(0, l1 * 2 + d3, d3))
        else:
            d1 = TargetDefinition.radius / (TargetDefinition.resol_angular - 1)
            ra, phi, z = np.meshgrid(0 + np.arange(0, r + d1, d1), 0 + np.arange(0, 2 * np.pi + d2, d2), -l1 + np.arange(0, l1 * 2 + d3, d3))

        # Convert cylindrical to Cartesian coordinates
        x1 = ra * np.cos(phi)
        x2 = ra * np.sin(phi)
        x3 = z

    # Other shapes as per your original code...

    # Flatten the meshgrid arrays to create 3-column point array
    x1 = x1.flatten()
    x2 = x2.flatten()
    x3 = x3.flatten()
    
    # Combine flattened arrays into a 3-column array
    points = np.column_stack((x1, x2, x3))

    # Remove any duplicate points (in case they occur on boundaries)
    points = np.unique(points, axis=0).transpose()


    return points  # Return the B_out object

# Main block to visualize the points
if __name__ == "__main__":
    # Get points and filename from MeasurementPoints
    app = QApplication(sys.argv)

    window = MainWindowPointsCreator()
    window.show()
    sys.exit(app.exec_())