#define input_pin A0
#include <Filter.h>

int value = 0;
long int start_time = millis() - 5;
ExponentialFilter<float> FilteredValue(20,0);

void setup() {
  Serial.begin(2000000);
}

void loop() {
  if(millis() > start_time + 5)
    {
      start_time = millis();
      value = analogRead(input_pin);
      FilteredValue.Filter(value);
      
      Serial.print(millis());
      Serial.print(",");
      Serial.println(int(FilteredValue.Current()));
      
    }
}
