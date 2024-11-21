bool getStepperRunning() {

  if (stepperX.isRunning() == false && stepperY.isRunning() == false && stepperZ.isRunning() == false) {
    return false;
  } else {
    return true;
  }
}