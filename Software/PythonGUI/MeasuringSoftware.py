import sys
import random
import numpy as np
import serial
import time
import csv
import os
from datetime import datetime

from MeasurementsPointCreator import MainWindowPointsCreator
from MeasurementsHallReader import getValueofdata

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication, QFormLayout, QLabel, QLineEdit, QWidget, QPushButton, QGridLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Constants
DEFAULT_PORTS = {
    "Robot": "/dev/tty.usbmodem2101",
    "Relay": "/dev/tty.usbmodem101",
    "Hallsensor": "/dev/tty.usbmodem1101",
}
ROBOT_COORD_LIMIT = 600  # mm
CSV_FOLDER = "Measurements"
SPEED_PROGRAM = 10  # Update interval for plot
SPEED_ROBOT_DEFAULT = 1  # Default speed for robot movement

MEASUREMENT_TIME_DEFAULT = 1000  # Default measurement time in ms
GRADIENT_ACTIVE_TIME_DEFAULT = 1000  # Default gradient active time in ms

POINT_FACTOR = 10  # Factor to convert points
FAIL_LIMIT = 10  # Maximum allowed failures before stopping

# Create the 3D plotting canvas
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor="#ffffff")
        self.axes3d = fig.add_subplot(111, projection="3d")
        self.axes3d.set_facecolor("#ffffff")
        super().__init__(fig)

# Main Window Class
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()


    # initialize the variables and the GUI
    def initUI(self):

        now = datetime.now()
        date_time = now.strftime("%m.%d.%Y, %H%M%S")
        # factor to convert from 0.1 mm to 1 mm
        self.PointRobotfactor = 10
        self.allowedNumberOfFails = 10
        # text variables for buttons
        self.measurementFolder = "Measurements"
        self.pointsFolder = ""
        self.textImportMeasurement = "Import points"
        self.importPointsFileName = "measurement_points.csv"
        self.textMoveTo = "Move to position"
        self.textMeasurementStop = "Stop measuring"
        self.textContinueMeasurement = "Continue measuring"
        self.textStepForwardMeasurement = "Step forward"
        self.textStepBackMeasurement = "Step back"
        # standard ports, but can be changed in the programm
        self.RobotPort = DEFAULT_PORTS["Robot"]
        self.RelaisPort = DEFAULT_PORTS["Relay"]
        self.HallsensorPort = DEFAULT_PORTS["Hallsensor"]

        # create csv file
        now = datetime.now()
        date_time = now.strftime("%m.%d.%Y, %H %M %S")
        self.csvDataName = "Measurement " + str(date_time)

        self.csvDataHeader = 'x,y,z,Bx,By,Bz,Btotal,Average number'
        self.dataarray = np.array([[0,0,0,0.0,0.0,0.0,0.0,0]])
        self.csvDataCreated = False

        self.portRobot = serial.Serial()
        self.portRelais = serial.Serial()
        self.portHallsensor = serial.Serial()
        
        # limit for the robot coordinate system 600x600x600mm
        self.limitsCoordRobot = ROBOT_COORD_LIMIT

        # in Code created booleans
        self.measurementInported = False
        self.isMoving = False
        self.atPosition = False
        self.measurementIsRunning = False
        self.measurementIsActive = False

        self.portsConnectedRobot = False
        self.portsConnectedHallsensor = False
        self.portConnectedRelais = False
        self.robotIsMoving = False

        self.isRelayOn = False

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setWindowTitle("ALF Robot Measurement Software")
        self.resize(800, 900)

        self.speedPlotRobot = SPEED_PROGRAM
        self.measurementTime = MEASUREMENT_TIME_DEFAULT

        self.timeCheckerMovement = 3000

        self.gradientActiveTime = GRADIENT_ACTIVE_TIME_DEFAULT
        self.robotSpeed = SPEED_ROBOT_DEFAULT
        self.numberOfMeans = 10

        self.startPoint = np.array([0,0,0])
        self.targetPoint = np.array([0,0,0])


        # Create a QFormLayout instance
        
        self.MeasurementFileLabel = QLabel("no imported measurement")
        self.MeasurementFileStep = QLabel("no measurement values")
        self.MeasurmemenStep = QLineEdit()
        self.MeasurmemenStep.setText("none")
        self.MeasurmementTotaStep = QLabel("total steps")
        self.buttonMoveToPoint = QPushButton("Got to point", self)
        self.buttonMoveToPoint.clicked.connect(self.moveManualToPoint)
        
        xPositionLabel = QLabel("x position in mm: ")
        yPositionLabel = QLabel("y position in mm: ")
        zPositionLabel = QLabel("z position in mm: ")

        self.xPositionInput = QLineEdit()
        self.xPositionInput.setText(str(0))
        self.yPositionInput = QLineEdit()
        self.yPositionInput.setText(str(0))
        self.zPositionInput = QLineEdit()
        self.zPositionInput.setText(str(0))

        self.speedRobotLabel = QLabel("Robot speed")

        self.speedRobotInput = QLineEdit()
        self.speedRobotInput.setText(str(self.robotSpeed))

        self.buttonTakeSpeed = QPushButton("Take speed", self)
        self.buttonTakeSpeed.clicked.connect(self.inportNewSpeed)

        robotPortLabel = QLabel("Robot port: ")
        relaisPortLabel = QLabel("Relay port: ")
        hallsensorPortLabel = QLabel("Hallsensor port: ")

        self.robotPortInput = QLineEdit()
        self.robotPortInput.setText(self.RobotPort)
        self.relaisPortInput = QLineEdit()
        self.relaisPortInput.setText(self.RelaisPort)
        self.hallsensorPortInput = QLineEdit()
        self.hallsensorPortInput.setText(self.HallsensorPort)

        self.buttonImportMeasurement = QPushButton(self.textImportMeasurement, self)
        self.buttonImportMeasurement.clicked.connect(self.importMeasurement)

        buttonMove = QPushButton(self.textMoveTo, self)
        buttonMove.clicked.connect(self.moveTo)

        buttonStopMeasurement = QPushButton(self.textMeasurementStop, self)
        buttonStopMeasurement.clicked.connect(self.processStopMeasurement)

        buttonContinueMeasurement = QPushButton(self.textContinueMeasurement, self)
        buttonContinueMeasurement.clicked.connect(self.processContinueMeasurement)

        buttonStepForwardMeasurement = QPushButton(self.textStepForwardMeasurement, self)
        buttonStepForwardMeasurement.clicked.connect(self.processStepForwartMeasurement)

        buttonStepbackMeasurement = QPushButton(self.textStepBackMeasurement, self)
        buttonStepbackMeasurement.clicked.connect(self.processStepBackMeasurement)

        buttonXPlus = QPushButton("+1mm", self)
        buttonXPlus.clicked.connect(self.add1mmX)
        buttonXMinus = QPushButton("-1mm", self)
        buttonXMinus.clicked.connect(self.sub1mmX)

        buttonYPlus = QPushButton("+1mm", self)
        buttonYPlus.clicked.connect(self.add1mmY)
        buttonYMinus = QPushButton("-1mm", self)
        buttonYMinus.clicked.connect(self.sub1mmY)

        buttonZPlus = QPushButton("+1mm", self)
        buttonZPlus.clicked.connect(self.add1mmZ)
        buttonZMinus = QPushButton("-1mm", self)
        buttonZMinus.clicked.connect(self.sub1mmZ)

        self.buttonRebootRobot = QPushButton("Reboot Robot", self)
        self.buttonRebootRobot.clicked.connect(self.rebootRobotPort)

        self.buttonConnectToPorts = QPushButton("Connect", self)
        self.buttonConnectToPorts.clicked.connect(self.connectToPorts)

        self.buttonRebootHall = QPushButton("Reboot Hallsensor", self)
        self.buttonRebootHall.clicked.connect(self.rebootHallPort)

        self.buttonRebootRelay = QPushButton("Reboot Relay", self)
        self.buttonRebootRelay.clicked.connect(self.rebootRelayPort)

        self.DataFileLabel = QLabel("No Data File")

        self.DataFileNameInput = QLineEdit()
        self.DataFileNameInput.setText(self.csvDataName)

        self.buttonCreateDataFile = QPushButton("Create Data File", self)
        self.buttonCreateDataFile.clicked.connect(self.createDataFile)

        gradientTimeLabel = QLabel("gradient time in ms: ")
        measurementTimeLabel = QLabel("measurement pause time in ms: ")
        meanvaluesLabel = QLabel("number of means: ")

        self.gradientTimeInput = QLineEdit()
        self.gradientTimeInput.setText(str(self.gradientActiveTime))
        self.measurementTimeInput = QLineEdit()
        self.measurementTimeInput.setText(str(self.measurementTime))
        self.meanvaluesInput = QLineEdit()
        self.meanvaluesInput.setText(str(self.numberOfMeans))

        self.buttonRelayOn = QPushButton("Relay on", self)
        self.buttonRelayOn.clicked.connect(self.relayOn)

        self.buttonMeasurePoint = QPushButton("measure point", self)
        self.buttonMeasurePoint.clicked.connect(self.measurePointwithHall)

        self.buttonInportNewValues = QPushButton("Take new values", self)
        self.buttonInportNewValues.clicked.connect(self.inportNewValues)

        # Create a the layout of the GUI, stuctured in a grid layout, rows a columns, with are getting added up
        # Add widgets to the layout

        layout = QGridLayout()
        row = 0
        layout.addWidget(self.MeasurementFileLabel,row,0)
        layout.addWidget(self.MeasurementFileStep,row,1)
        layout.addWidget(self.MeasurmemenStep,row,3)
        layout.addWidget(self.MeasurmementTotaStep,row,4)
        layout.addWidget(self.buttonMoveToPoint,row,5)
        row = row + 1
        layout.addWidget(self.canvas, row, 0, 1, 6)
        row = row + 2
        layout.addWidget(xPositionLabel,row,0,1,2)
        layout.addWidget(yPositionLabel,row,2,1,2)
        layout.addWidget(zPositionLabel,row,4,1,2)
        row = row + 1
        layout.addWidget(self.xPositionInput,row,0,1,2)
        layout.addWidget(self.yPositionInput,row,2,1,2)
        layout.addWidget(self.zPositionInput,row,4,1,2)
        row = row + 1
        layout.addWidget(buttonXPlus,row,0)
        layout.addWidget(buttonXMinus,row,1)

        layout.addWidget(buttonYPlus,row,2)
        layout.addWidget(buttonYMinus,row,3)

        layout.addWidget(buttonZPlus,row,4)
        layout.addWidget(buttonZMinus,row,5)
        row = row + 1
        layout.addWidget(self.speedRobotLabel,row,0,1,2)
        layout.addWidget(self.speedRobotInput,row,2,1,2)
        layout.addWidget(self.buttonTakeSpeed,row,4,1,2)
        row = row + 1
        layout.addWidget(buttonMove,row,0,1,2)
        layout.addWidget(self.buttonImportMeasurement, row,2,1,2)
        layout.addWidget(buttonStopMeasurement, row,4,1,2)
        row = row + 1
        layout.addWidget(buttonContinueMeasurement,row,0,1,2)
        layout.addWidget(buttonStepForwardMeasurement, row,2,1,2)
        layout.addWidget(buttonStepbackMeasurement, row,4,1,2)
        row = row + 1
        layout.addWidget(robotPortLabel,row,0,1,2)
        layout.addWidget(relaisPortLabel,row,2,1,2)
        layout.addWidget(hallsensorPortLabel,row,4,1,2)
        row = row + 1
        layout.addWidget(self.robotPortInput,row,0,1,2)
        layout.addWidget(self.relaisPortInput,row,2,1,2)
        layout.addWidget(self.hallsensorPortInput,row,4,1,2)
        row = row + 1
        layout.addWidget(self.buttonRebootRobot,row,0,1,2)
        layout.addWidget(self.buttonRebootRelay, row,2,1,2)
        layout.addWidget(self.buttonRebootHall,row,4,1,2)
        row = row + 1
        layout.addWidget(self.DataFileLabel,row,0,1,2)
        layout.addWidget(self.DataFileNameInput,row,2,1,2)
        layout.addWidget(self.buttonCreateDataFile,row,4,1,2)
        row = row + 1
        layout.addWidget(gradientTimeLabel,row,0,1,2)
        layout.addWidget(measurementTimeLabel,row,2,1,2)
        layout.addWidget(meanvaluesLabel,row,4,1,2)
        row = row + 1
        layout.addWidget(self.gradientTimeInput,row,0,1,2)
        layout.addWidget(self.measurementTimeInput,row,2,1,2)
        layout.addWidget(self.meanvaluesInput,row,4,1,2)
        row = row + 1
        layout.addWidget(self.buttonRelayOn,row,0,1,2)
        layout.addWidget(self.buttonMeasurePoint, row,2,1,2)
        layout.addWidget(self.buttonInportNewValues,row,4,1,2)
        row = row + 1
        layout.addWidget(self.buttonConnectToPorts,row,2,1,2)


        # Set timer for updating the plot and timer Measurement

        self.timer = QtCore.QTimer()
        self.timerMeasurement = QtCore.QTimer(self)

        self.timer.setInterval(self.speedPlotRobot)
        self.timer.timeout.connect(self.update_plot)
        
        # Set the layout on the application's window

        self.i = 0
        self.movingPoints = self.moveToPoint()
        self.update_plot()
        
        self.setLayout(layout)


    def getMeasurementPoints(self):
        measurementsPoints = np.loadtxt(
        os.path.join(
            str(sys.path[0]), self.pointsFolder, str(self.importPointsFileName)
        ),              # Path to file
        delimiter=',',  # Column delimiter
        skiprows=1,     # Skip header row
        dtype=float     # Directly read as floats
        )
    
    # Convert to integer if you need integer data
        self.allData = measurementsPoints.astype(int)
        x = int(self.xPositionInput.text())
        y = int(self.yPositionInput.text()) 
        z = int(self.zPositionInput.text())
        self.allData = measurementsPoints[:,:].astype(int) + np.array([x,y,z])
        self.color = np.full((np.shape(measurementsPoints[:,0])),'b',dtype='U25')
        return self.allData,self.color

#  function for updating the plot
    def update_plot(self):
        self.canvas.axes3d.cla()  # Clear the canvas.
        # Set limits of the 3d plot
        self.canvas.axes3d.set_xlim(0, self.limitsCoordRobot) 
        self.canvas.axes3d.set_ylim(self.limitsCoordRobot, 0)
        self.canvas.axes3d.set_zlim(self.limitsCoordRobot, 0)
        # Start timer to wait for robot movement end
        if self.robotIsMoving and self.portsConnectedRobot:
            #checkRobotProcess = multiprocessing.Process(target=self.checkRobotMovement())
            #checkRobotProcess.start()
            self.checkRobotMovement()
        self.canvas.axes3d.set_aspect('equal')
        # plot the measure points
        if self.measurementInported == True:
            self.showMeasurementPoints()
        self.canvas.axes3d.scatter(self.movingPoints[self.i,0], self.movingPoints[self.i,1], self.movingPoints[self.i,2], c='r',marker="^", s= 30)
        # if we not reached the end of the measurement points
        if self.i < (len(self.movingPoints[:,0])-1):
            self.isMoving = True
            self.i = self.i + 1
        # if we reached the end of the measurement points
        if self.i == (len(self.movingPoints[:,0])-1):
            self.isMoving = False
            if self.measurementIsRunning == False:
                self.endPosition()
            elif self.measurementIsRunning == True and self.robotIsMoving == False:
                self.measurePoint()
        # Trigger the canvas to update and redraw.
        self.canvas.draw()

    def showMeasurementPoints(self):
        self.canvas.axes3d.scatter(self.allData[:,0], self.allData[:,1], self.allData[:,2], c=self.color,s= 5)
    # function for the last measurement point
    def endPosition(self):
        self.atPosition = True
        self.startPoint = self.targetPoint
        self.i = 0
        self.movingPoints = self.moveToPoint()
        self.isMoving = False

    # function for the check for the coordinate inputs
    def differentCoordasBefore(self):
        if int(self.xPositionInput.text()) == self.startPoint[0] and int(self.yPositionInput.text()) == self.startPoint[1] and int(self.zPositionInput.text()) == self.startPoint[2]:
            return False
        else:
            return True

    # function for the progress of the measurement, it moves to the measurement point
    def processMeasurement(self):
        if self.measurementIsRunning == True and (len(self.allData[:,0])-1) >= self.measurementPointNr and self.isMoving == False:
            self.startPoint = self.targetPoint
            self.MeasurmementTotaStep.setText("/" + str(len(self.allData[:,0])))
            self.MeasurmemenStep.setText(str(self.measurementPointNr + 1))
            self.xPositionInput.setText(str(self.allData[self.measurementPointNr,0]))
            self.yPositionInput.setText(str(self.allData[self.measurementPointNr,1]))
            self.zPositionInput.setText(str(self.allData[self.measurementPointNr,2]))
            self.color[self.measurementPointNr] = 'g'
            self.measurementPointNr = self.measurementPointNr + 1
            self.moveTo()
        elif (len(self.allData[:,0])-1) == self.measurementPointNr:
            self.measurementIsRunning = False
            self.endPosition()

# function for the robot movement, it sends the movement points to the moveTo function, if the points are diffenent then before
    def moveToPoint(self):
        if self.targetPoint[0] == self.startPoint[0] and self.targetPoint[1] == self.startPoint[1] and self.targetPoint[2] == self.startPoint[2]:
            return np.expand_dims(self.startPoint,axis=0)
        pointDistance = np.array([0,0,0])
        pointDistance[0] = self.targetPoint[0] - self.startPoint[0]
        pointDistance[1] = self.targetPoint[1] - self.startPoint[1]
        pointDistance[2] = self.targetPoint[2] - self.startPoint[2]
        pointDistanceMax = np.abs(pointDistance).max()
        points = np.zeros((3,int(pointDistanceMax)))
        points[0] = np.linspace(self.startPoint[0],self.targetPoint[0],int(pointDistanceMax)) 
        points[1] = np.linspace(self.startPoint[1],self.targetPoint[1],int(pointDistanceMax)) 
        points[2] = np.linspace(self.startPoint[2],self.targetPoint[2],int(pointDistanceMax)) 
        return points.astype(int)   
    
# function for the robot movement, it sends the robot the coordinates per Serial Communication if connected
    def moveTo(self):
        x = int(self.xPositionInput.text())
        y = int(self.yPositionInput.text())
        z = int(self.zPositionInput.text())
        if (isinstance(x, int)) and self.limitsCoordRobot >= x >= 0 and (isinstance(y, int)) and self.limitsCoordRobot >= y >= 0 and (isinstance(z, int)) and self.limitsCoordRobot >= z >= 0 and self.differentCoordasBefore():
            self.atPosition = False
            self.i = 0
            self.targetPoint = np.array([x,y,z])
            self.movingPoints = self.moveToPoint().transpose()
            self.timer.start()
            self.isMoving = True
            if self.portsConnectedRobot:
                self.portRobot.write(str.encode(str("x:" + str(self.targetPoint[0]*self.PointRobotfactor))+";y:"+str(self.targetPoint[1]*self.PointRobotfactor)+";z:"+str(self.targetPoint[2]*self.PointRobotfactor)+ ";s:" + str(self.robotSpeed) +'\n'))
                self.robotIsMoving = True
                time.sleep(self.measurementTime/1000)
        else:
            self.xPositionInput.setText(str(self.startPoint[0]))
            self.yPositionInput.setText(str(self.startPoint[1]))
            self.zPositionInput.setText(str(self.startPoint[2]))

    def inportNewSpeed(self):
        speedRobotInput = int(self.speedRobotInput.text())
        if (isinstance(speedRobotInput, int)) and 2 >= speedRobotInput > 0:
            self.robotSpeed = speedRobotInput
        else:
            self.speedRobotInput.setText(str(self.robotSpeed))
        
    # function for the import of the measurement from the MeasurementPointCreator class
    def importMeasurement(self):
        if self.isMoving == False:
            try:
                self.allData,self.color = self.getMeasurementPoints()
                self.measurementPointNr = 0
                self.measurementPointChecker = 1
                self.measurementInported = True
                self.MeasurmementTotaStep.setText("/" + str(len(self.allData[:,0])))
                self.buttonImportMeasurement.setText("Imported")
                self.update_plot()
            except:
                self.measurementInported = False
                self.buttonImportMeasurement.setText("Not imported")
            
    # button function to continue the measurement
    def processContinueMeasurement(self):
        if self.isMoving == False and self.measurementInported:
            self.measurementIsRunning = True
            self.processMeasurement()

    # button function to move one step forwart 
    def processStepForwartMeasurement(self):
        if self.measurementInported:
            self.measurementIsRunning = True
            self.processMeasurement()
            self.measurementIsRunning = False
# button function to move one step back 
    def processStepBackMeasurement(self):
        if  self.measurementInported == True and self.measurementPointNr > 1:
            self.measurementPointNr = self.measurementPointNr - 2
            self.measurementIsRunning = True
            self.processMeasurement()
            self.measurementIsRunning = False
# button function to stop the measurement
    def processStopMeasurement(self):
        self.isMoving = False
        self.measurementIsRunning = False
# button functions to move one mm in one direction
    def add1mmX(self):
        self.xPositionInput.setText(str(self.startPoint[0] + 1))
        self.moveTo()
    def sub1mmX(self):
        self.xPositionInput.setText(str(self.startPoint[0] - 1))
        self.moveTo()

    def add1mmY(self):
        self.yPositionInput.setText(str(self.startPoint[1] + 1))
        self.moveTo()
    def sub1mmY(self):
        self.yPositionInput.setText(str(self.startPoint[1] - 1))
        self.moveTo()

    def add1mmZ(self):
        self.zPositionInput.setText(str(self.startPoint[2] + 1))
        self.moveTo()

    def sub1mmZ(self):
        self.zPositionInput.setText(str(self.startPoint[2] - 1))
        self.moveTo()

    # function for the connection to the ports
    def connectToPorts(self):
        
        try:
            self.portRelais = serial.Serial(self.relaisPortInput.text(),  baudrate=9600, timeout=.1)
            self.portRelais.close();
            self.portRelais.open();
            # self.portRelais.flush();
            self.portConnectedRelais = True
            self.buttonConnectToPorts.setText("Relais Connected")
        except:
            self.portConnectedRelais = False
            self.buttonConnectToPorts.setText("Relais not connected")

        try:
            self.portRobot = serial.Serial(self.robotPortInput.text(),baudrate=115200)
            self.portRobot.close();
            self.portRobot.open();
            self.portsConnectedRobot = True
            self.buttonConnectToPorts.setText("Robot connected")
        except:
            self.portsConnectedRobot = False
            self.buttonConnectToPorts.setText("Robot not connected")

        try:
            self.portHallsensor = serial.Serial(self.hallsensorPortInput.text())
            self.portHallsensor.close();
            self.portsConnectedHallsensor = True
            self.buttonConnectToPorts.setText("Hall Connected")
        except:
            self.portsConnectedHallsensor = False
            self.buttonConnectToPorts.setText("Hall not connected")

        if self.portsConnectedRobot and self.portsConnectedHallsensor and self.portConnectedRelais:
            self.buttonConnectToPorts.setText("All connected")

            

# functions reboot a Serial connection
    def rebootRobotPort(self):
        if self.portsConnectedRobot:
            self.buttonConnectToPorts.setText("Reboot Robot")
            self.portRobot.close();
            self.portRobot.open();
            self.buttonConnectToPorts.setText("Connected")
            
    def rebootHallPort(self):
        if self.portsConnectedHallsensor:
            self.buttonConnectToPorts.setText("Reboot Hall sensor")
            self.portHallsensor.close();
            self.buttonConnectToPorts.setText("Connected")

    def rebootRelayPort(self):
        if self.portConnectedRelais:
            self.buttonConnectToPorts.setText("Reboot Relay")
            self.portRelais.close();
            self.portRelais.open();
            self.portRelais.flush();
            self.buttonConnectToPorts.setText("Connected")
            
        
# functions start the measurement timer
    def measurePoint(self):
        self.activateMeasurementTimer()
            
            
        
    def activateMeasurementTimer(self):
        if self.measurementIsActive == False:
            self.measurementIsActive = True
            self.measurePointwithHall()
            self.timerMeasurement.singleShot(self.measurementTime,self.reactivateMeasurement)

        
# function to reactivate the measurement
    def reactivateMeasurement(self):
        if self.measurementIsActive == True:
            self.measurementIsActive = False
            self.processMeasurement()
            
# function to create a csv file
    def createDataFile(self):
        self.csvDataName = os.path.join(str(sys.path[0]), self.measurementFolder, str(self.DataFileNameInput.text()))
        np.savetxt(self.csvDataName, np.array([]), delimiter=',', fmt='%s', header=self.csvDataHeader, comments='')
        self.DataFileLabel.setText(self.DataFileNameInput.text())
        self.csvDataCreated = True

# function to add a row to the csv file
    def addRowToCsvData(self):
        with open(self.csvDataName, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.dataarray)
            
# function to activate the relay
    def relayOn(self):
        if self.portConnectedRelais:
            self.portRelais.flush()
            time.sleep(0.1)
            self.portRelais.write(str.encode(str(self.gradientActiveTime)))
            if (self.portRelais.readline() == b'HIGH\r\n'):
                self.isRelayOn = True
            if self.isRelayOn:
                self.buttonRelayOn.setText("Relay active")
        else:
            self.buttonRelayOn.setText("Relay not connected")

            
# function to activate the relay
    def inportNewValues(self):
        measurementTime = int(self.measurementTimeInput.text())
        meanValueNr = int(self.meanvaluesInput.text())
        gradientActiveTime = int(self.gradientTimeInput.text())
        if (isinstance(gradientActiveTime, int)) and 1000000 >= gradientActiveTime > 0 and isinstance(measurementTime, int) and 100000 >= measurementTime >= 10 and (isinstance(meanValueNr, int)) and 1000 >= meanValueNr >= 1:
            self.gradientActiveTime = gradientActiveTime
            self.measurementTime = measurementTime
            self.numberOfMeans = meanValueNr
        else:
            self.gradientTimeInput.setText(str(self.gradientActiveTime))
            self.measurementTimeInput.setText(str(self.measurementTime))
            self.meanvaluesInput.setText(str(self.numberOfMeans))

# function to move to a measurement point manually
    def moveManualToPoint(self):
        if self.measurementInported:
            point = int(self.MeasurmemenStep.text())
            if (len(self.allData[:,0])) >= point > 0:
                self.measurementPointNr = point - 1
                self.measurementIsRunning = True
                self.processMeasurement()
                self.measurementIsRunning = False
            else:
                self.MeasurmemenStep.setText(str(self.measurementPointNr + 1))

# function check robot movement with the serial port
    def checkRobotMovement(self):
        if self.portsConnectedRobot:
            try:
                if (self.portRobot.readline() == b'Moved\r\n'):
                    self.robotIsMoving = False
            except:
                print("none")
        else:
            self.robotIsMoving = False

# function to check if the csv file should be added depending on the connection of the state relay and its connection
    def checkerForAddToCsv(self):
        if self.csvDataCreated:
            if  self.portConnectedRelais and self.isRelayOn:
                return True
            elif self.portConnectedRelais:
                return False
            else:
                return True
        else:
            return False


# change here for a new Hall sensor
# -----------------------------------------------------------------------------------------------
# function to measure with the hall sensor and save to csv

    def measurePointwithHall(self):
        self.MeasurementFileStep.setText("Measured value")
        # check for the connection of the hall sensor
        if self.portsConnectedHallsensor:
            # start the relay 
            self.relayOn()
            # open and flush the serial port of the hall sensor
            self.portHallsensor.open()
            self.portHallsensor.flush()
            # wait for the serial port to be ready
            time.sleep(0.01)
            try:
                realNumberOfMeans = 0
                measurement = np.array([0.0,0.0,0.0,0.0])
                measurementTemp = np.zeros((self.numberOfMeans,4))
                for i in range(self.numberOfMeans):
                    time.sleep(0.01)

                    # function to get the data from the hall sensor, this is a extra function from MeasurementHallReader file with can be changed
                    measurementString = self.portHallsensor.readline()
                    measurementTemp[i,:] = getValueofdata(measurementString)
                    realNumberOfMeans = i+1

                # avarage the measured values
                measurement[0] = np.average(measurementTemp[:,0])
                measurement[1] = np.average(measurementTemp[:,1])
                measurement[2] = np.average(measurementTemp[:,2])
                measurement[3] = np.average(measurementTemp[:,3])
                self.MeasurementFileStep.setText(str(measurement[0]))
                self.dataarray[0,0] = int(self.xPositionInput.text())
                self.dataarray[0,1] = int(self.yPositionInput.text())
                self.dataarray[0,2] = int(self.zPositionInput.text())
                self.dataarray[0,3] = measurement[0]
                self.dataarray[0,4] = measurement[1]
                self.dataarray[0,5] = measurement[2]
                self.dataarray[0,6] = measurement[3]
                self.dataarray[0,7] = realNumberOfMeans
                self.portHallsensor.close();
                if self.checkerForAddToCsv():
                    # add the measured values to the csv file
                    self.addRowToCsvData()
                    self.isRelayOn = False
            except:
                self.portHallsensor.flush();
                self.portHallsensor.close();
                self.rebootHallPort()
                print("No data from hall sensor")
                self.MeasurementFileStep.setText("No hall Data")


        
# main function to create the object of the class
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    