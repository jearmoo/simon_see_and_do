#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif


Adafruit_NeoPixel trainLights = Adafruit_NeoPixel(120, 5, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel performLights = Adafruit_NeoPixel(120, 4, NEO_GRB + NEO_KHZ800);

enum{
  your_turn,
  robot_turn,
  training
};

int state = your_turn;

int s = 1;

void setup() {
  trainLights.begin();
  performLights.begin();
  
  trainLights.setBrightness(75);
  performLights.setBrightness(75);
  
  trainLights.show();
  performLights.show();

  Serial.begin(38400);
  Serial.println("Beginning!");
}
int b = 0;
bool up = true;
void loop() {

  while (Serial.available()) { 
    Serial.println("Got Command!");
 
    char cmd = (char)Serial.read();
    if(cmd == 'y'){
      state = your_turn;
    }
    else if(cmd == 'r'){
      state = robot_turn;
    }
    else if(cmd == 't'){
      state = training;
    }
  }

  for(int i = 0; i < trainLights.numPixels(); i++){
    if(state == your_turn){
      trainLights.setPixelColor(i, 0, b, 0);
      performLights.setPixelColor(i, b, 0, 0);
    }
    else if (state == robot_turn){
      trainLights.setPixelColor(i, b, 0, 0);
      performLights.setPixelColor(i, 0, b, 0);
    }
    else if (state == training){
      trainLights.setPixelColor(i, b, b / 2, 0);
      performLights.setPixelColor(i, b, 0, 0);
    }
  }
  trainLights.show();
  performLights.show();

  if(up){
    b++;
  }
  else{
    b--;
  }
  
  if(b == 255){
    up = false;
  }
  else if(b == 50){
    up = true;
  }
  
  //delay(100);

}

