unsigned long ConvertCoor(double val_mm, long val_steps, char* command) {
  // Funktion ConvertCoor berechnet die Anzahl der Roboter-Schritte (Rsteps) für eine gewünschte Distanz
  // Eingabeparameter:
  //   val (double) = Eingabe der umzurechnenden Distanz in mm
  //   command (char) = Angabe von welchem Koorsystem in welches konvertiert wird
  //   struct Config_str* Config = Die Konfig des Roboters, um die Umrechnung zu ermöglichen (nutze minres)
  // Rückgabeparameter: Die umgerechnete Distanzt in RSteps


  /*

Beachte 3 Koordinatensysteme:
1) Koorsystem vom DuT (das zu scannende Volumen), vom Nutzer vorgegeben, metrisch, in mm, daher in double.
   Nullpunkt vom Nutzer ist die (von vorne betrachtet) hintere linke obere Ecke. 
2) Koorsystem vom Roboter, vorgegeben durch SetUp, in Vielfachen von Schritten (und zwar Config_str.steps_perminres), sodass ca 0.1mm bewegt werden. Das entspricht einem "Roboter-Schritt". Mur ganzzahlige, positive Werte möglich. Daher in uint
   Nullpunkt von Roboter ist (von Vorne betrachtet) hintere linke obere Ecke
3) Korrsystem vom Stepper selbst, vorgegeben durch Libraray AccelStepper.h. in Stepper-Schritten. Ein Schritt entspricht der Distanz Config_str.minres. Nur ganzzahlige Steps möglich. Positiv = Vorwärstfahren. Negativ = Rückwärtsfahren. Daher signed int
   Nullpunt/Startpunkt ist da wo er gerade ist

  */

  if (strcmp(command, "DuT->R_Steps")==0) {  // mm-> R_Steps
    double calc_R_Steps = val_mm / Config.minres_roboter;  // mm/min-Auflösung
                                                           //Anzahl der Robot Steps für die gewünschte metrische Länge. uint() rundet den berechneten double Wert ab
    return (long) calc_R_Steps;
  }

  else if (strcmp(command, "R_Steps->S_Steps_XY")==0) {  // R_Steps -> S_Steps für XY-Achse
    // R_Steps = Roboter Step
    // S_Steps = Stepper_Steps
    long calc_S_Steps = Config.steps_perminres * val_steps;
    return calc_S_Steps;
  }
   else if (strcmp(command, "R_Steps->S_Steps_Z")==0) {  // R_Steps -> S_Steps für Z-Achse
    // R_Steps = Roboter Step
    // S_Steps = Stepper_Steps
    long calc_S_Steps = Config.steps_perminres * val_steps;
    return calc_S_Steps * Config.zgain; // *2, weil Steigung der z-Achse halb so groß wie Steigung von XY-Achse
  }

  else if (strcmp(command, "S_Steps->R_Steps_XY")==0) { //XY-Achse
    double calc_S_Steps = (double) val_steps / Config.steps_perminres;
    return (long) calc_S_Steps;
  }

   else if (strcmp(command, "S_Steps->R_Steps_Z")==0) { //Z-Achse (halb so große Steigung wie XY-Achsen)
    double calc_S_Steps = (double) val_steps / Config.steps_perminres;
    return (long) calc_S_Steps/Config.zgain; ///2 weil z Achse doppelt so viele Steps
  }

}