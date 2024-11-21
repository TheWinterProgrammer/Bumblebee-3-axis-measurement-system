void DrivetoZero() {

  delay(1000);

  stepperX.move(-10000000);
  stepperY.move(-10000000);
  stepperZ.move(-10000000);

  set_Stepper(3000.0, 1500.0); // Mittelschnelles Bewegen des Roboters

  // Fahre zuerst die x-Achse
  while (1==1)
  {
    if (getLS("x") == false) //Endschalter in x ist nicht getriggert -> Weiter fahren
    {
      stepperX.run();
    }
    else { //Nullposition erreicht
      stepperX.stop();
      stepperX.move(100); //Fahre 100 Steps nach vorne, als Puffer
      stepperX.runToPosition();
      stepperX.setCurrentPosition(0); //Diese Position ist die 0 Positon vom Roboter
      break;
    }

  }

  // Fahre danach die y-Achse
  while (1==1)
  {
    if (getLS("y") == false) //Endschalter in x ist nicht getriggert -> Weiter fahren
    {
      stepperY.run();
    }
    else { //Nullposition erreicht
      stepperY.stop();
      stepperY.move(100); //Fahre 100 Steps nach vorne, als Puffer
      stepperY.runToPosition();
      stepperY.setCurrentPosition(0); //Diese Position ist die 0 Positon vom Roboter
      break;
    }

  }

  // Fahre als letzes die z-Achse
  while (1==1)
  {
    if (getLS("z") == false) //Endschalter in x ist nicht getriggert -> Weiter fahren
    {
      stepperZ.run();
    }
    else { //Nullposition erreicht
      stepperZ.stop();
      stepperZ.move(100*2); //Fahre 100 Steps nach vorne, als Puffer, z-Achse braucht doppelt so viele Steps
      stepperZ.runToPosition();
      stepperZ.setCurrentPosition(0); //Diese Position ist die 0 Positon vom Roboter
      break;
    }

  }

Status.posX = 0;
Status.posY = 0;
Status.posZ = 0;

}