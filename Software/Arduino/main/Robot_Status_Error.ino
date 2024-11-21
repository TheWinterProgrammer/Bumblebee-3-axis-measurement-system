void Robot_Status_Error(char* Command) {
  // Error. Evaluieren was notwendig ist
  // Command = Final -> Nichts mehr möglich. Neustart nötig (Nullpunkt nicht mehr bekannt)
  // Command = Retry -> Alles safe. nur zB LS ausversehen getroffen. Programm kann weitermachen bei Suche des FOV Zentrums (Nullpunkt noch bekannt)


  if (strcmp(Command, "Error") == 0) {
    Serial.println("CRITICAL ERROR! - robot off");      
    while (1 == 1) {
        // Encoder muss resetted werden
      }
  }

  else if (strcmp(Command, "Final") == 0) {

    Serial.println("   Robot-Status-Error (Final) aufgerufen");

    if (getNotaus() == true) {

      Serial.println("CRITICAL ERROR! - NOTAUS GEDRÜCKT - WENN SAFE: NOTAUS LÖSEN");
      delay(1000);

    } else {


      while (1 == 1) {
        // Encoder muss resetted werden
      }
    }

  }

  else if (strcmp(Command, "Retry") == 0) {

    // ... ToDo ...
    Robot_Status_Error("Final");

  }

  else if (strcmp(Command, "Finished") == 0) {


    while (1 == 1) {
      // Write Error on Display
    }
  }



}
