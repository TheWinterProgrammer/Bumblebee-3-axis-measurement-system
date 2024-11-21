#include <AccelStepper.h>


//Variablen für die Taster
struct Pins_str {

  //Taster Konsole
  uint8_t Sw_x;  //x-Achse
  uint8_t Sw_y;  //y-Achse
  uint8_t Sw_z;  //z
  uint8_t Sw_v;  //Speed Auswahl
  uint8_t Sw_Extra;

  //Endschalter
  uint8_t LS_y1;  //x1
  uint8_t LS_y2;
  uint8_t LS_x1;
  uint8_t LS_x2;
  uint8_t LS_z1;
  uint8_t LS_z2;

  //Notaus
  uint8_t Sw_Notaus;   //Abfrage, wie der Zustand phys Notschalter ist
  uint8_t Set_Notaus;  // Schalte den Notaus ein
};

Pins_str Pins = {
  31,   //Sw_x;
  29,   //Sw_y
  27,   //Sw_z
  25,   //Sw_v
  A10,  //Sw_Extra
  42,   //LS_x1
  44,   //LS_x2
  46,   //LS_y1
  48,   //LS_y2
  50,   //LS_z1
  52,   //LS_z2
  11,   //Sw_Notaus
  2     //Set_Notaus
};



// Definition Schrittmotoren
AccelStepper stepperX(AccelStepper::DRIVER, 13, 12);
AccelStepper stepperY(AccelStepper::DRIVER, 6, 5);
AccelStepper stepperZ(AccelStepper::DRIVER, 4, 3);



//Endschalter Struct
struct LS_str {
  bool one;  // true wenn einer der Schalter aktiv
  bool x1;
  bool x2;
  bool y1;
  bool y2;
  bool z1;
  bool z2;
};

LS_str LS = {
  false,
  false,
  false,
  false,
  false,
  false,
  false
};

//Status Struct in Schritten
struct Status_str {  //Roboterkoordinaten
  long posX;
  long posY;
  long posZ;
  bool Error;  // Error während der Messung, aber nicht gefählrich (zB LS sind getriggert, obwohl das nicht sein sollte)

  bool Notaus;  // Muss gemessen werden. Sicherer Zustand = true (Notaus ist getriggert)
};

Status_str Status = {
  0,
  0,
  0,
  false,
  true
};

//Messeinstellungen Struct
struct Config_str {  //pins
  long lengthX; // In R-Steps
  long lengthY;
  long lengthZ;

  double minres_stepper;  //Kleinste Auflösung des Schrittmotors in mm  = SStep 1 (10mm/1600) -> Falsche Spindelmutter geliefert, daher 10mm Steigung... (oder so ähnlich)  
  double minres_roboter;  //Kleinste Auflösung des Roboters in mm  = RStep 1. minres_roboter = minres_stepper * steps_perminres
  long steps_perminres;   // Wähle Mindestschrittweite im Roboter KoorSystem (ca 0,1mm <=> 16 Schritte)
  long steps_perrev;      //
  long zgain;             // z Achse Gain, weil doppelte Steigung verbaut
};

Config_str Config = {
  6630,  // 106.080 -> 6630 R-Steps (16Steps pro 0.1mm)
  6060,  //96.960 -> 6060 R-Steps (bei 16 Steps pro 0.1mm)
  6870,  // Mit aktueller Konfig macht die z-Achse maximal 219.840 Schritte, Steigung 5mm -> 0.1mm=32S -> max_l = 6870 
  0.00625,  
  0.1,
  16,
  1600,
  2
};

const int MaxString = 4;
const int coodValNum = 4;
String inputString = "";
  long coor_x = 0;
  long coor_y = 0;
  long coor_z = 0;
  int speed_slow = 0;  // Langsam
  int speed_mid = 1;   // Mittel
  int speed_fast = 2;  // Schnell
  int speed = 0;
 // bool nextStepfast = false;
  bool finish = false;

  //bool Display_Wait = false;
  bool sendTextMoved = false;
  String strings[MaxString];


void setup() {

  //Motoren
  stepperX.setMaxSpeed(1000);
  stepperX.setAcceleration(1000);
  stepperX.setEnablePin(A4);
  stepperX.setPinsInverted(true, false, false);

  stepperY.setMaxSpeed(1000);
  stepperY.setAcceleration(1000);
  stepperY.setEnablePin(A6);

  stepperZ.setMaxSpeed(1000);
  stepperZ.setAcceleration(1000);
  stepperZ.setEnablePin(A8);

  // Setze digitale Pins

  //Notaus
  pinMode(Pins.Set_Notaus, OUTPUT);
  //Endschalter
  pinMode(Pins.LS_x1, INPUT);
  pinMode(Pins.LS_x2, INPUT);
  pinMode(Pins.LS_y1, INPUT);
  pinMode(Pins.LS_y2, INPUT);
  pinMode(Pins.LS_z1, INPUT);
  pinMode(Pins.LS_z2, INPUT);
  //Taster
  pinMode(Pins.Sw_x, INPUT);
  pinMode(Pins.Sw_y, INPUT);
  pinMode(Pins.Sw_z, INPUT);
  pinMode(Pins.Sw_v, INPUT);
  pinMode(Pins.Sw_Extra, INPUT);

  Serial.begin(115200);
  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
  }
  delay(500);
  Serial.println("Robot Online - Start to initialize");



  while (Serial.available() == false) { ; } // Für INB - Start erst nach Kommando

  digitalWrite(Pins.Set_Notaus, HIGH);
  // Suche den Nullpunkt

  Status.Notaus == false;
  DrivetoZero();
  getNotaus();
  delay(1000);

  // Starte Messung
  Meas_FOV_new();
  delay(1000);

  // Messung zu
  Robot_Status_Error("Error");
  delay(1000);
}

void loop() {
}