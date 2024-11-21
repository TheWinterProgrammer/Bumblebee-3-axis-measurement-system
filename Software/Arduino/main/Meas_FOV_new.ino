
void Meas_FOV_new() {
  // Komplettes Punktbewegungsprogramm

  while (finish == false && Status.Error == false) {
    //setDisplay_Status("Wait");     

    if (finish == true) {
      // Ende aller Punkte erreicht --> Messung zuende
      //setDisplay_Status("Finish");      
      break;
    }
    // Wenn momoveCoordinatesStep sauber durchläuft bis hierher, gibts 2 Möglichkeiten:
    // 1: Alles okay -> Weitermachen
    // 2: Abbruch Taste wurde gedrückt (Sonde sehr/zu nah an Hindernis)
    // Check über Status.Error

    if (Status.Error == true) {
      // Fall 2 eingetreten -> Abbruch + Neustart!
      Robot_Status_Error("Final");
    }

    

    while (SerialComm() == false) {
      delay(10);      
    }

    //setDisplay_Status("Drive");
    moveCoordinatesStep(coor_x, coor_y, coor_z, speed);

    if (sendTextMoved == false){
      Serial.println("Moved");
      sendTextMoved = true;
    }
  }
}


