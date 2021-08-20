#include <UARTComms.h>
#include <Sensor.h>
#include <SpeedSensor.h>

#define LED 13

UARTComms uart(115200, Serial);
TimeSensor t1(MICROS);
SpeedSensor he_speed(22, 22);
StateSensor led_state_sensor;

uint32_t prev_time = micros();
bool led_state = 0;

void setup() {
  // put your setup code here, to run once:
  uart.begin();
  uart.attach_output_sensor(t1, TEST_SENSOR_1);
  uart.attach_output_sensor(he_speed, SPEED_POSITION_GENERIC600);
  uart.attach_input_sensor(led_state_sensor, COMMAND_TOGGLE_TEENSY_LED);

  pinMode(LED, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  uart.update();

  if(abs(micros() - prev_time) > 250000){
    led_state = led_state_sensor.get_state();
    digitalWrite(LED, led_state);
    prev_time = micros();
  }
}
