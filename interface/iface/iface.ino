#include <CapacitiveSensor.h>

#define MAX_SENSORS 6

CapacitiveSensor cs0 = CapacitiveSensor(2,3);
CapacitiveSensor cs1 = CapacitiveSensor(4,5);
CapacitiveSensor cs2 = CapacitiveSensor(6,7);
CapacitiveSensor cs3 = CapacitiveSensor(8,9);
CapacitiveSensor cs4 = CapacitiveSensor(10,11);
CapacitiveSensor cs5 = CapacitiveSensor(12,13);
//CapacitiveSensor cs6 = CapacitiveSensor(14,15);
//CapacitiveSensor cs7 = CapacitiveSensor(16,17);
//CapacitiveSensor cs8 = CapacitiveSensor(18,19);

const long threshold = 700;
const long num = 6;
long states[MAX_SENSORS];

void setup() 
{
    uint8_t i;
    
    Serial.begin(9600);
    
    for(i = 0; i < MAX_SENSORS; i++)
        states[i] = 0;
    
    cs0.set_CS_AutocaL_Millis(0xFFFFFFFF);
    cs1.set_CS_AutocaL_Millis(0xFFFFFFFF);
    cs2.set_CS_AutocaL_Millis(0xFFFFFFFF);
    cs3.set_CS_AutocaL_Millis(0xFFFFFFFF);
    cs4.set_CS_AutocaL_Millis(0xFFFFFFFF);
    cs5.set_CS_AutocaL_Millis(0xFFFFFFFF);
    //cs6.set_CS_AutocaL_Millis(0xFFFFFFFF);
    //cs7.set_CS_AutocaL_Millis(0xFFFFFFFF);
    //cs8.set_CS_AutocaL_Millis(0xFFFFFFFF);
}

void check_sensor(uint8_t id, CapacitiveSensor *s)
{
    long total;
        
    total = s->capacitiveSensor(30);
    //Serial.println(total);
        
    if (total > threshold && states[id] == 0)
    {
        Serial.println(id);
        states[id] = 1;
    }
    if (total <= threshold && states[id] == 1)
        states[id] = 0;
        
}

void loop() 
{
    long total;
    
    delay(100);
    
    check_sensor(0, &cs0);
    if (num == 1)
        return;

    check_sensor(1, &cs1);
    if (num == 2)
        return;        

    check_sensor(2, &cs2);
    if (num == 3)
        return;

    check_sensor(3, &cs3);
    if (num == 4)
        return;

    check_sensor(4, &cs4);
    if (num == 5)
        return;

    check_sensor(5, &cs5);
    if (num == 6)
        return;     
#if 0
    check_sensor(6, &cs6);

    
    if (num == 7)
        return;

    check_sensor(7, &cs7);
    if (num == 8)
        return; 
        
    check_sensor(8, &cs8);
#endif
}

