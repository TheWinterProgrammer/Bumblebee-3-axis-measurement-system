bool getLS(char* Axis) {
  //Funktion überprüft die Endschalter:
  //Mind ein ES (pro Achse) gedrückt --> return true
  //Überträgt Rückgabewert in LS--struct


  int Val_Trig = LOW;  // Dieser Wert gilt, wenn der Limitswitch gedrückt ist. NPN-Augang am LS


// // Rückgabe strcmp:
// 0 -> Strings sind identisch
// != 0 -> Strings sind nicht identich!


  // x-Achse
  if (strcmp(Axis, "x") == 0) {

    if (digitalRead(Pins.LS_x1) == Val_Trig) {
      LS.x1 = true;
    } else {
      LS.x1 = false;
    }
    if (digitalRead(Pins.LS_x2) == Val_Trig) {
      LS.x2 = true;
    } else {
      LS.x2 = false;
    }
    return LS.x1 || LS.x2; // Ist ein LS gedrückt -> return == true
  }

  // y-Achse
  if (strcmp(Axis, "y") == 0) {

    if (digitalRead(Pins.LS_y1) == Val_Trig) {
      LS.y1 = true;

    } else {
      LS.y1 = false;
    }

    if (digitalRead(Pins.LS_y2) == Val_Trig) {
      LS.y2 = true;

    } else {
      LS.y2 = false;
    }
    return LS.y1 || LS.y2;
  }

  // z-Achse
  if (strcmp(Axis, "z") == 0) {

    if (digitalRead(Pins.LS_z1) == Val_Trig) {
      LS.z1 = true;
    } else {
      LS.z1 = false;
    }
    if (digitalRead(Pins.LS_z2) == Val_Trig) {
      LS.z2 = true;
    } else {
      LS.z2 = false;
    }
    return LS.z1 || LS.z2;
  }
}
