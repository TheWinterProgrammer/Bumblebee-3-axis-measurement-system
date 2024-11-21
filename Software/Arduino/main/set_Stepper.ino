void set_Stepper(float accel, float speed) {

  stepperX.setMaxSpeed(speed);
  stepperX.setAcceleration(accel);

  stepperY.setMaxSpeed(speed);
  stepperY.setAcceleration(accel);
  
  stepperZ.setMaxSpeed(speed * Config.zgain); //*2, weil z-Achse halb so große Steigung wie XY-Achse
  stepperZ.setAcceleration(accel * Config.zgain);


}