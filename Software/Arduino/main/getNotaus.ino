bool getNotaus(){
  // Check des Notauses 
  if(digitalRead(Pins.Sw_Notaus) == LOW)
    {
      Status.Notaus = true;
      // SChreibe Display
      return true;
    }
    else {
       Status.Notaus = false;
      return false;

    }

}