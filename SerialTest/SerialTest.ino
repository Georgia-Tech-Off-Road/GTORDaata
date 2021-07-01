#include <UARTComms.h>
#include <Sensor.h>
#include <SpeedSensor.h>

#define LED 13

UARTComms uart(115200, Serial);
TimeSensor t(MICROS);
TimeSensor t0(MICROS);
TimeSensor t1(MICROS);
TimeSensor t2(MICROS);
TimeSensor t3(MICROS);
TimeSensor t4(MICROS);
TimeSensor t5(MICROS);
TimeSensor t6(MICROS);
TimeSensor t7(MICROS);
TimeSensor t8(MICROS);
TimeSensor t9(MICROS);
SpeedSensor he_speed(600, 5);

uint32_t prev_time = micros();
bool led_state = 0;

void setup() {
  // put your setup code here, to run once:
  uart.begin();
  uart.attach_output_sensor(t, TIME_GENERIC);
  uart.attach_output_sensor(t0, TEST_SENSOR_0);
  uart.attach_output_sensor(t1, TEST_SENSOR_1);
  uart.attach_output_sensor(t2, TEST_SENSOR_2);
  uart.attach_output_sensor(t3, TEST_SENSOR_3);
  uart.attach_output_sensor(t4, TEST_SENSOR_4);
  uart.attach_output_sensor(t5, TEST_SENSOR_5);
  uart.attach_output_sensor(t6, TEST_SENSOR_6);
  uart.attach_output_sensor(t7, TEST_SENSOR_7);
  uart.attach_output_sensor(t8, TEST_SENSOR_8);
  uart.attach_output_sensor(t9, TEST_SENSOR_9);
  
  
  uart.attach_output_sensor(he_speed, SPEED_POSITION_GENERIC600);

  pinMode(LED, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  uart.update();

  if(abs(micros() - prev_time) > 250000){
    led_state = !led_state;
    digitalWrite(LED, led_state);
    prev_time = micros();
  }
}
