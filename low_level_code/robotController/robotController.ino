#include <Encoder.h>
#include <Wire.h>
#include <Servo.h>

#define LEFT_MTR_CTRL_A 4
#define LEFT_MTR_CTRL_B 5
#define LEFT_MTR_EN 9

#define RIGHT_MTR_CTRL_A 8
#define RIGHT_MTR_CTRL_B 7
#define RIGHT_MTR_EN 6

#define TICKS_PER_REV 2790
#define TICKS_PER_INCH 350
#define MIN_SPEED 60
#define TICKS_PER_DEG 15

#define MAGNET_PIN A3

#define MPU_ADDR 0x68

#define SERVO_PIN A2

typedef enum{
  a_forward,
  a_right,
  a_left,
  a_drop,
  a_pickup,
  a_backward,
  a_none
} action_t;
int actionVal;
action_t todo = a_none;
bool carrying = false;

Encoder leftEncoder(2, 12);
Encoder rightEncoder(3, 10);

Servo servoArm;

void setRightMotor(int s){
  int dc;
  if(s < 0){
    digitalWrite(RIGHT_MTR_CTRL_A, LOW);
    digitalWrite(RIGHT_MTR_CTRL_B, HIGH);
    dc = map(s, 0, -100, 0, 255);
  }
  else{
    digitalWrite(RIGHT_MTR_CTRL_A, HIGH);
    digitalWrite(RIGHT_MTR_CTRL_B, LOW);
    dc = map(s, 0, 100, 0, 255);
  }

  analogWrite(RIGHT_MTR_EN, dc);
}

void setLeftMotor(int s){
  int dc;
  if(s < 0){
    digitalWrite(LEFT_MTR_CTRL_A, LOW);
    digitalWrite(LEFT_MTR_CTRL_B, HIGH);
    dc = map(s, 0, -100, 0, 255);
  }
  else{
    digitalWrite(LEFT_MTR_CTRL_A, HIGH);
    digitalWrite(LEFT_MTR_CTRL_B, LOW);
    dc = map(s, 0, 100, 0, 255);
  }

  analogWrite(LEFT_MTR_EN, dc);
}

void driveForward(int inches){
  int minSpeed = (carrying) ? MIN_SPEED + 15 : MIN_SPEED;
  leftEncoder.write(0);
  rightEncoder.write(0);
  int totalTicks = inches * TICKS_PER_INCH;
  int currentTicks;
  int rightSpeed, leftSpeed;

  while(((rightEncoder.read() - leftEncoder.read()) / 2) < totalTicks){
    int diff = ((rightEncoder.read() + leftEncoder.read()) / 2);
    float kp_d = 100;
    setLeftMotor(minSpeed + (diff * kp_d));
    setRightMotor(minSpeed + -(diff * kp_d));
  }

  setLeftMotor(0);
  setRightMotor(0);
}

void driveBackward(int inches){
  int minSpeed = (carrying) ? MIN_SPEED: MIN_SPEED - 15;
  leftEncoder.write(0);
  rightEncoder.write(0);
  int totalTicks = inches * TICKS_PER_INCH;
  int currentTicks;
  int rightSpeed, leftSpeed;

  while(((leftEncoder.read() - rightEncoder.read()) / 2) < totalTicks){
    setLeftMotor(-minSpeed);
    setRightMotor(-minSpeed);
  }

  setLeftMotor(0);
  setRightMotor(0);
}

int getRight(){
  return rightEncoder.read();
}

int getLeft(){
  return -leftEncoder.read();
}

void turnRight(int deg){
  int minSpeed = (carrying) ? (MIN_SPEED + 25) : MIN_SPEED;
  leftEncoder.write(0);
  rightEncoder.write(0);
  int totalTicks = deg * TICKS_PER_DEG;
  int currentTicks;
  int rightSpeed, leftSpeed;
  int stillCount = 0;
  int deadZone = TICKS_PER_DEG / 2;


  while(true){
    if(((getLeft() - getRight())  / 2) < (totalTicks - deadZone)){
    //float kP = 10;
    //int error = (getLeft() - getRight() / 2) - totalTicks;
    stillCount = 0;
    setLeftMotor(minSpeed);
    setRightMotor(-minSpeed);
//    int diff = ((getLeft() + getRight()) / 2);
//    float kp_d = 5;
//      setLeftMotor(minSpeed - (diff * kp_d));
//      setRightMotor(-minSpeed - (diff * kp_d));
  }
  else if(((getLeft() - getRight())  / 2) > (totalTicks + deadZone)){ 
    stillCount = 0;
    setLeftMotor(-minSpeed);
    setRightMotor(minSpeed);
  }
  else{
    stillCount++;
    if(stillCount == 500){
      break;
    }
  }
  }
  
  
  setLeftMotor(0);
  setRightMotor(0);


}

void turnLeft(int deg){
  int minSpeed = (carrying) ? (MIN_SPEED + 25) : MIN_SPEED;
  leftEncoder.write(0);
  rightEncoder.write(0);
  int totalTicks = deg * TICKS_PER_DEG;
  int currentTicks;
  int rightSpeed, leftSpeed;
  int stillCount = 0;
  int deadZone = TICKS_PER_DEG / 2;


  while(true){
    if(((getRight() - getLeft())  / 2) < (totalTicks - deadZone)){
    //float kP = 10;
    //int error = (getLeft() - getRight() / 2) - totalTicks;
    stillCount = 0;
    setLeftMotor(-minSpeed);
    setRightMotor(minSpeed);
//    int diff = ((getLeft() + getRight()) / 2);
//    float kp_d = 5;
//      setLeftMotor(minSpeed - (diff * kp_d));
//      setRightMotor(-minSpeed - (diff * kp_d));
  }
  else if(((getRight() - getLeft())  / 2) > (totalTicks + deadZone)){ 
    stillCount = 0;
    setLeftMotor(minSpeed);
    setRightMotor(-minSpeed);
  }
  else{
    stillCount++;
    if(stillCount == 500){
      break;
    }
  }
  }
  
  
  setLeftMotor(0);
  setRightMotor(0);
}

void pickup(){
  digitalWrite(MAGNET_PIN, HIGH);
}

void drop(){
  digitalWrite(MAGNET_PIN, LOW);
}

void setup() {
  Wire.begin();
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0);     // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);
  // put your setup code here, to run once:
  pinMode(LEFT_MTR_CTRL_A, OUTPUT);
  pinMode(LEFT_MTR_CTRL_B, OUTPUT);
  pinMode(LEFT_MTR_EN, OUTPUT);
  pinMode(RIGHT_MTR_CTRL_A, OUTPUT);
  pinMode(RIGHT_MTR_CTRL_B, OUTPUT);
  pinMode(RIGHT_MTR_EN, OUTPUT);
  pinMode(MAGNET_PIN, OUTPUT);

  leftEncoder.write(0);
  rightEncoder.write(0);

  Serial.begin(38400);

}

void loop() {

  
  switch(todo){
    case a_forward:
      driveForward(actionVal);
      Serial.println("A");
      todo = a_none;
    break;

    case a_backward:
      driveBackward(actionVal);
      Serial.println("A");
      todo = a_none;

    case a_right:
      turnRight(actionVal);
      Serial.println("A");
      todo = a_none;
    break;

    case a_left:
      turnLeft(actionVal);
      Serial.println("A");
      todo = a_none;
    break;

    case a_pickup:
      pickup();
      carrying = true;
      Serial.println("A");
      todo = a_none;
    break;

    case a_drop:
      drop();
      delay(1000);
      driveBackward(2);
      carrying = false;
      Serial.println("A");
      todo = a_none;
    break;
    
    default:
    break;
  }
  
  
  
}

float makeInt(byte b0, byte b1, byte b2, byte b3){
//  Serial.println(b0);
//  Serial.println(b1);
//  Serial.println(b2);
//  Serial.println(b3);
  return ((int) ((uint32_t)b0 | ((uint32_t)b1 << 8) | ((uint32_t)b2 << 16) | ((uint32_t)b3 << 24)));
}

void serialEvent() {
  byte b0, b1, b2, b3;
  while (Serial.available()) {
    char cmd = (char)Serial.read();
    switch(cmd){
      case 'p':
        todo = a_pickup;
      break;
      
      case 'd':
        todo = a_drop;
      break;

      case 'f':
        todo = a_forward;
        while(!Serial.available()){}
        b0 = Serial.read();
        while(!Serial.available()){}
        b1 = Serial.read();        
        while(!Serial.available()){}
        b2 = Serial.read();
        while(!Serial.available()){}
        b3 = Serial.read();
        actionVal = (int)((float)makeInt(b0, b1, b2, b3) / 10.0);
      break;

      case 'b':
        todo = a_backward;
        while(!Serial.available()){}
        b0 = Serial.read();
        while(!Serial.available()){}
        b1 = Serial.read();        
        while(!Serial.available()){}
        b2 = Serial.read();
        while(!Serial.available()){}
        b3 = Serial.read();
        actionVal = (int)((float)makeInt(b0, b1, b2, b3) / 10.0);
      break;

      case 'r':
        todo = a_right;
        while(!Serial.available()){}
        b0 = Serial.read();
        while(!Serial.available()){}
        b1 = Serial.read();        
        while(!Serial.available()){}
        b2 = Serial.read();
        while(!Serial.available()){}
        b3 = Serial.read();
        actionVal = makeInt(b0, b1, b2, b3);
      break;
      
      case 'l':
        todo = a_left;
        while(!Serial.available()){}
        b0 = Serial.read();
        while(!Serial.available()){}
        b1 = Serial.read();        
        while(!Serial.available()){}
        b2 = Serial.read();
        while(!Serial.available()){}
        b3 = Serial.read();
        actionVal = makeInt(b0, b1, b2, b3);
      break;

      default:
        todo = a_none;
      break;
        
    }
  }
}
