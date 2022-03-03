// Library for i2c communication
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

//  i2c config
#define BAUD_RATE 19200
#define CHAR_BUF 128

// Buzzer
#define BUZZER_PIN 10

// LCD
LiquidCrystal_I2C lcd(0x27,16,2);

void setup() {
    // i2c
    Serial.begin(BAUD_RATE);
    Wire.begin();

    lcd.init();
    lcd.backlight();

    // Buzzer
    pinMode(BUZZER_PIN, OUTPUT);

}

void loop() {
  controller(recieveData());

}

// Main function
void controller(String msg) {
    lcd.clear();
  lcdPrint(0, 0, msg);

  if (msg.equals("fire!")) {
    tone(BUZZER_PIN, 1000); // Send 1KHz sound signal...
    delay(400);
    noTone(BUZZER_PIN);
    delay(100);
    tone(BUZZER_PIN, 1000); // Send 1KHz sound signal...
    delay(400);
  } else {
    noTone(BUZZER_PIN); 
  }
}


/* Utils */
// Function for recieving data through i2c 
String recieveData() {
  int32_t temp = 0;
  char buff[CHAR_BUF] = {0};

  Wire.requestFrom(0x12, 2);
  if (Wire.available() == 2) {
    temp = Wire.read() | (Wire.read() << 8);
    delay(1);

    Wire.requestFrom(0x12, temp);
    if(Wire.available() == temp) {
      temp = 0;
      while(Wire.available()) buff[temp++] = Wire.read();
    } else {
      while(Wire.available()) Wire.read(); // Toss garbage bytes.
    }
  } else {
      while(Wire.available()) Wire.read(); // Toss garbage bytes.
    }
  return String(buff);
 
  delay(1);
}

// LCD functions
template <typename T>
void lcdPrint(int x, int y, T genericInput) {
  lcd.setCursor(x, y);
  lcd.print(genericInput);
}
