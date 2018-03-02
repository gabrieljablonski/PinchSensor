#define sensorPin A0
#define rgbRedPin 11
#define rgbGreenPin 10
#define rgbBluePin 9
#define redPin 7
#define triggerPin 2
#define signalOutputPin 3
#define signalInputPin 4
#define N 175

int value = 0;
int interval = 5;  // Sample rate: 200 Hz
long int current_time = micros()/1000. - interval;
long int start_time;
long int wait_timer = micros()/1000.;
int trigger_input[N] = {0};
int ref = 0;
bool online = false;
bool plotting = false;
bool test_available = false;
bool testing = false;
int test_stage = 0;

void setup() 
{
  Serial.begin(2000000);
  pinMode(rgbRedPin, OUTPUT);
  pinMode(rgbGreenPin, OUTPUT);
  pinMode(rgbBluePin, OUTPUT);  
  pinMode(redPin, OUTPUT);
  pinMode(signalOutputPin, OUTPUT);
}

void loop()
{
  if(Serial.read() == 's')
    {
      online = true;
      plotting = false;
      test_available = false;
      digitalWrite(redPin, LOW);
      test_stage = 3;
      setColor(0, 0, 255);
    }
  if(Serial.read() == 'p' && online && !plotting)
    {
      plotting = true;
      start_time = millis();
      current_time = millis() - interval - start_time;
      test_available = true;
      setColor(0, 255, 0);
    }
  
  if(test_available)
  {
     if(micros()/1000. - start_time > current_time + interval)
    {
      current_time = micros()/1000. - start_time;
      value = analogRead(sensorPin);
      Serial.print(current_time);
      Serial.print(",");
      Serial.print(value);
      Serial.print(",");
  
      if(testing)
      {
        Serial.println(1);
      }
      else
      {
        Serial.println(0);
      }
    }
  // Input signal
    if(digitalRead(signalInputPin))
    {
      testing = true;
    }
    else
    {
      if(!test_stage)
      { 
        testing = false;
      }
    }

//  Trigger 
  
    int i;
    for(i = 0; i < N-1; i++)
      trigger_input[i] = trigger_input[i+1];
    trigger_input[N-1] = digitalRead(triggerPin);
  
    ref = 1;
    for(i = 0; i < N; i++)
    {
      if(!trigger_input[i])
        ref = 0;
    }
  
    if(ref)
    {
      if(test_stage == 0)
      { 
        test_stage = 1;
        testing = true;
        
      }
      if(test_stage == 2)
      {
        test_stage = 3;
        testing = false;
      }
    }
    else
    {
      if(test_stage == 1)
      {
        test_stage = 2;
      }
      if(test_stage == 3)
      {
        test_stage = 0;
      }
    }
    if(testing)
    {
      digitalWrite(redPin, HIGH);
      digitalWrite(signalOutputPin, HIGH);
    }
    else
    {
        digitalWrite(redPin, LOW);
        digitalWrite(signalOutputPin, LOW);
    }
  }
  else
  {
    if(millis() > wait_timer + 500)
    {
        wait_timer = micros()/1000.;
        Serial.write("w\n");
    }
    testing = false;
  }
}

void setColor(int red, int green, int blue)
{
  analogWrite(rgbRedPin, red);
  analogWrite(rgbGreenPin, green);
  analogWrite(rgbBluePin, blue);  
}
