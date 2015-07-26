// http://startingelectronics.com/articles/arduino/measuring-voltage-with-arduino/

/*--------------------------------------------------------------
  Program:      volt_measure

  Description:  Reads value on analog input A2 and calculates
                the voltage assuming that a voltage divider
                network on the pin divides by 11.
  
  Hardware:     Arduino Uno with voltage divider on A2.
                
  Software:     Developed using Arduino 1.0.5 software
                Should be compatible with Arduino 1.0 +

  Date:         22 May 2013
 
  Author:       W.A. Smith, http://startingelectronics.com
--------------------------------------------------------------*/

// number of analog samples to take per reading
#define NUM_SAMPLES     20

// Sample and loop delays in milliseconds
#define SAMPLE_DELAY    20
#define LOOP_DELAY    4600

// Number of samples (effectively the delay time) before switching power source
#define MAX_SWITCH_COUNT   24

int sum = 0;                    // sum of samples taken
unsigned char sample_count = 0; // current sample number
float voltage = 0.0;            // calculated voltage

int inverter    = 0;            // is the inverter remote on?
int mains_power = 0;            // is mains power on?

#define REF_VOLTAGE  4.97       // Arduino 5V voltage

#define INV_REMOTE      8       // Output pin for inverter remote control
#define INV_LIVE        9       // Output pin for inverter live power
#define INV_NEUTRAL    10       // Output pin for inverter neutral power

// Voltage thresholds for switching between battery/solar and mains
float v_upper = 12.55;
float v_lower = 11.85;

// Number of samples
int switch_to_battery = 0;
int switch_to_mains = 0;

// Voltage divider A0: 12.59 / 2.11

void setup()
{
    Serial.begin(9600);
    pinMode(A0, INPUT);  // Doesn't seem to work 
    pinMode(A1, INPUT);  // Input from voltage divider
    
    pinMode(12, INPUT);  // mains_power voltage sensor (relay contact, 0V/5V)
    // Relay http://www.farnell.com/datasheets/296895.pdf wiring 5V (digital 1)=no power
    
    pinMode(INV_REMOTE, OUTPUT);   // Relay board channel 1: Inverter remote
    pinMode(INV_LIVE, OUTPUT);   // Relay board channel 3: Inverter/mains_power live
    pinMode(INV_NEUTRAL, OUTPUT);   // Relay board channel 4: Inverter/mains_power neutral
    
    digitalWrite(INV_REMOTE, LOW);
    digitalWrite(INV_LIVE, LOW);
    digitalWrite(INV_NEUTRAL, LOW);
    
}

void loop()
{
    // take a number of analog samples and add them up
    while (sample_count < NUM_SAMPLES) {
        float sample = analogRead(A1);
        sum += sample;
        sample_count++;
        // Serial.print("Actual: ");
        // Serial.println(sample);
        delay(SAMPLE_DELAY);
    }
    // calculate the voltage
    // use 5.0 for a 5.0V ADC reference voltage
    // 5.015V is the calibrated reference voltage
    voltage = (((float)sum / (float)NUM_SAMPLES * REF_VOLTAGE) / 1024.0) * 5.99;

    // send voltage for display on Serial Monitor
    // voltage multiplied by 11 when using voltage divider that
    // divides by 11. 11.132 is the calibrated voltage divide
    // value
    
    Serial.print("voltage=");
    Serial.print(voltage);
    
    // mains_power sensor
    mains_power = !digitalRead(12);
    
    Serial.print(" mains_power=");
    Serial.print(mains_power);

    if (!mains_power) {
        // Always use inverter: low-voltage cutoff will cause it to power off eventually        
        if (!inverter) {
            inverterOn();
        }
    } else {

      // Battery getting low
      if ((voltage < v_lower) && inverter) {
          switch_to_mains++;
      } else {
           switch_to_mains = 0; 
      }

      // Battery charged and/or solar power available
      if ((voltage > v_upper) && !inverter) {
        switch_to_battery++;
      } else {
         switch_to_battery = 0; 
      }
      
      if (switch_to_mains > MAX_SWITCH_COUNT) {
        inverterOff();
      }
      
      if (switch_to_battery > MAX_SWITCH_COUNT) {
        inverterOn();        
      }
     
    }
    
    Serial.print(" inverter=");
    Serial.print(inverter);

    Serial.print(" switch_to_mains=");
    Serial.print(switch_to_mains);
    
    Serial.print(" switch_to_battery=");
    Serial.print(switch_to_battery);    
    
    Serial.println();
    
    sample_count = 0;
    sum = 0;
    
    delay(LOOP_DELAY);
}

void inverterOn() {
  digitalWrite(INV_REMOTE, HIGH);
  delay(1000); 
  digitalWrite(INV_LIVE, HIGH);
  digitalWrite(INV_NEUTRAL, HIGH);
  inverter = 1;
}

void inverterOff() {
  digitalWrite(INV_LIVE, LOW);
  digitalWrite(INV_NEUTRAL, LOW);
  delay(500);
  digitalWrite(INV_REMOTE, LOW);
  inverter = 0;
}

