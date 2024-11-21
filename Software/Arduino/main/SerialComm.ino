bool SerialComm() {
  inputString = Serial.readStringUntil('\n');
  if (checkForCoord()){
    return true;
  } else {
    Serial.flush();
    coor_x = 0;
    coor_y = 0;
    coor_z = 0;
    speed = 0;
    inputString = "";
    return false;
  }
}


bool checkForCoord() {
  while (inputString.length() > 0) {
    int w = Split(inputString, ';');
    getCoord(w);
  }
  if (speed < 3 && speed > -1 && correctCoordinates()) {
    inputString = "";
    Serial.flush();
    return true;
  } else {
    return false;
  }
}

size_t Split(String& input, char Sep) {
    int count = 0;
    int p = input.indexOf(Sep);
    while (p >= 0 && count < MaxString-1) {
        strings[count] = input.substring(0,p);
        count++;
        input = input.substring(p+1);
        p = input.indexOf(Sep);
    }
    if (input.length() > 0) {
       if (input.indexOf(Sep) < 0) {
              strings[count] = input;
              count++;
              input = "";
        }
      }  
    return count;
}


void getCoord(int No) {
    for (int i = 0; i < No; i++) {
      String stringTemp = strings[i];
      if(stringTemp[0] == 'x')
      {
        coor_x = stringTemp.substring(2).toInt();
      }
      if(stringTemp[0] == 'y')
      {
        coor_y = stringTemp.substring(2).toInt();
      }
      if(stringTemp[0] == 'z')
      {
        coor_z = stringTemp.substring(2).toInt();
      }
      if(stringTemp[0] == 's')
      {
        speed = stringTemp.substring(2).toInt();
      }
      if(stringTemp[0] == 'f')
      {
        finish = true;
      }
      sendTextMoved = false;
    }
}




bool correctCoordinates() {

  coor_x = coor_x * 1;
  coor_y = coor_y * 1;
  coor_z = coor_z * 1;

  if (coordValueIsGood(coor_x, coor_y, coor_z) && sendTextMoved == false) {
    return true;
  } else {
    sendTextMoved = true;
    return false;
  }
}



bool coordValueIsGood(int valX, int valY, int valZ) {


  if (valX < Config.lengthX && valY < Config.lengthY && valZ < Config.lengthZ) {
    return true;
  } else {
    return false;
  }
}
