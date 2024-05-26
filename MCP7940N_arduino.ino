#include <Wire.h>

unsigned long previousMillis = 0;
const long interval = 250;

#define RTCADDR B1101111  //page11 datasheet
#define RTCSEC 0x00
#define RTCMIN 0x01
#define RTCHOUR 0x02
#define RTCWKDAY 0x03
#define RTCDATE 0x04
#define RTCMTH 0x05
#define RTCYEAR 0x06
#define CONTROL 0x07
#define OSCTRIM 0x08
#define ALM0SEC 0x0A
#define ALM0MIN 0x0B
#define ALM0HOUR 0x0C
#define ALM0WKDAY 0x0D
#define ALM0DATE 0x0E
#define ALM0MTH 0x0F
#define ALM1SEC 0x11
#define ALM1MIN 0x12
#define ALM1HOUR 0x13
#define ALM1WKDAY 0x14
#define ALM1DATE 0x15
#define ALM1MTH 0x16
#define PWRDNMIN 0x18
#define PWRDNHOUR 0x19
#define PWRDNDATE 0x1A
#define PWRDNMTH 0x1B
#define PWRUPMIN 0x1C
#define PWRUPHOUR 0x1D
#define PWRUPDATE 0x1E
#define PWRUPMTH 0x1F


void setup() {
  Serial.begin(9600);
  Wire.setClock(100000);
  Wire.begin();
}

void loop() {
  while (!(Serial.available() || (millis() - previousMillis >= interval))) {}
  previousMillis = millis();
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();
    String index = msg.substring(0, msg.indexOf("_"));
    String value = msg.substring(msg.indexOf("_") + 1, 100);

    long intIndex = strtol(msg.c_str(), NULL, 16);
    int intValue = value.toInt();

    Wire.beginTransmission(RTCADDR);
    Wire.write(intIndex);
    Wire.write(intValue);
    Wire.endTransmission();
  }
  Wire.beginTransmission(RTCADDR);
  Wire.write(RTCSEC);
  Wire.endTransmission();
  Wire.requestFrom(RTCADDR, 9);
  delay(1);
  Serial.print("00");
  Serial.println(Wire.read());
  Serial.print("01");
  Serial.println(Wire.read());
  Serial.print("02");
  Serial.println(Wire.read());
  Serial.print("03");
  Serial.println(Wire.read());
  Serial.print("04");
  Serial.println(Wire.read());
  Serial.print("05");
  Serial.println(Wire.read());
  Serial.print("06");
  Serial.println(Wire.read());
  Serial.print("07");
  Serial.println(Wire.read());
  Serial.print("08");
  Serial.println(Wire.read());
    
  Wire.beginTransmission(RTCADDR);
  Wire.write(ALM0SEC);
  Wire.endTransmission();
  Wire.requestFrom(RTCADDR, 6);
  delay(1);
  Serial.print("0A");
  Serial.println(Wire.read());
  Serial.print("0B");
  Serial.println(Wire.read());
  Serial.print("0C");
  Serial.println(Wire.read());
  Serial.print("0D");
  Serial.println(Wire.read());
  Serial.print("0E");
  Serial.println(Wire.read());
  Serial.print("0F");
  Serial.println(Wire.read());

  Wire.beginTransmission(RTCADDR);
  Wire.write(ALM1SEC);
  Wire.endTransmission();
  Wire.requestFrom(RTCADDR, 6);
  delay(1);
  Serial.print("11");
  Serial.println(Wire.read());
  Serial.print("12");
  Serial.println(Wire.read());
  Serial.print("13");
  Serial.println(Wire.read());
  Serial.print("14");
  Serial.println(Wire.read());
  Serial.print("15");
  Serial.println(Wire.read());
  Serial.print("16");
  Serial.println(Wire.read());

  Wire.beginTransmission(RTCADDR);
  Wire.write(PWRDNMIN);
  Wire.endTransmission();
  Wire.requestFrom(RTCADDR, 4);
  delay(1);
  Serial.print("18");
  Serial.println(Wire.read());
  Serial.print("19");
  Serial.println(Wire.read());
  Serial.print("1A");
  Serial.println(Wire.read());
  Serial.print("1B");
  Serial.println(Wire.read());

  Wire.beginTransmission(RTCADDR);
  Wire.write(PWRUPMIN);
  Wire.endTransmission();
  Wire.requestFrom(RTCADDR, 4);
  delay(1);
  Serial.print("1C");
  Serial.println(Wire.read());
  Serial.print("1D");
  Serial.println(Wire.read());
  Serial.print("1E");
  Serial.println(Wire.read());
  Serial.print("1F");
  Serial.println(Wire.read());
}

