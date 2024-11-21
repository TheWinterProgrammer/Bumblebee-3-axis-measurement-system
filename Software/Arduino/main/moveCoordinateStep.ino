void moveCoordinatesStep(long x, long y, long z, int speed) {

  if (Status.Error == true || Status.Notaus == true)
  {
    // Es wird kein Step gemacht -> ErrorNachricht auf Display
    Robot_Status_Error("Final"); 
    return;
  }


  switch (speed) {
    case 0:  //langsam
      set_Stepper(500, 500);
      break;
    case 1:  //mittelschnell
      set_Stepper(1000, 1000);
      break;
    case 2:  //schnell
      set_Stepper(1000, 4000);
      break;
    default:  //default -> langsam
      set_Stepper(100, 100);
      break;
  }


  stepperX.moveTo(ConvertCoor(0, x, "R_Steps->S_Steps_XY"));
  stepperY.moveTo(ConvertCoor(0, y, "R_Steps->S_Steps_XY"));
  stepperZ.moveTo(ConvertCoor(0, z, "R_Steps->S_Steps_Z"));


  while (stepperX.distanceToGo() != 0 || stepperY.distanceToGo() != 0 || stepperZ.distanceToGo() != 0) {

    stepperX.run();
    stepperY.run();
    stepperZ.run();

    if (getLS("x") == true) {
    
      disableStepper("x");
      setError(true);
      Robot_Status_Error("Retry");  
      break;
    }

    if (getLS("y") == true) {
     
      disableStepper("y");
      setError(true);
      Robot_Status_Error("Retry");  
      break;
    }

    if (getLS("z") == true) {
     
      disableStepper("z");
      setError(true);
      Robot_Status_Error("Retry");      
      break;
    }

    if (digitalRead(Pins.Sw_Extra) == HIGH) {  // extra Button if needed
      Serial.println("  Cancel through User");
      disableStepper("x");
      disableStepper("y");
      disableStepper("z");
      setError(true);
      break;          
    }

// Check Emergency Switch
    if (getNotaus() == true) {
      disableStepper("x");
      disableStepper("y");
      disableStepper("z");
      setError(true);      
      Robot_Status_Error("Final");
      break;
    }
 
  }
    Status.posX = ConvertCoor(0, stepperX.currentPosition(), "S_Steps->R_Steps_XY");
    Status.posY = ConvertCoor(0, stepperY.currentPosition(), "S_Steps->R_Steps_XY");
    Status.posZ = ConvertCoor(0, stepperZ.currentPosition(), "S_Steps->R_Steps_Z");


}

void disableStepper(char Axis)
{
  if (strcmp(Axis, "x") == 0) {
    stepperX.stop();
    stepperX.disableOutputs();
  } else if (strcmp(Axis, "y") == 0) {
    stepperY.stop();
    stepperY.disableOutputs();
  } else if (strcmp(Axis, "z") == 0) {
    stepperZ.stop();
    stepperZ.disableOutputs();
  }
  
}