#include <util/crc16.h>
#include <EEPROM.h>
#include <Adafruit_NeoPixel.h>

#include "parse.h"

const uint8_t NUM_PIXELS = 4;
const uint8_t OUT_PIN = 2;

const uint8_t BROADCAST = 0;
const uint8_t PACKET_SINGLE_COLOR = 0;
const uint8_t PACKET_COLOR_ARRAY  = 1;
const uint8_t PACKET_PATTERN      = 2;

const uint16_t MAX_PACKET_LEN     = 200;
uint8_t    g_packet[MAX_PACKET_LEN];

Adafruit_NeoPixel g_pixels = Adafruit_NeoPixel(NUM_PIXELS, OUT_PIN, NEO_GRB + NEO_KHZ800);

// where in EEPROM our node id is stored
const int id_address = 0;
uint8_t g_node_id = 0;

void show_color(uint8_t r, uint8_t g, uint8_t b)
{
    uint8_t j;
    
    for(j = 0; j < NUM_PIXELS; j++)
        g_pixels.setPixelColor(j, r, g, b);
    g_pixels.show();
}

void startup_animation(void)
{
    uint8_t i, j;
    uint8_t col1[3] = { 128, 40, 0 };
    uint8_t col2[3] = { 128, 0, 128 };

    for(i = 0; i < 10; i++)
    {       
        for(j = 0; j < NUM_PIXELS; j++)
        {
            if (i % 2 == 0)
            {
                if (j % 2 == 1)
                    g_pixels.setPixelColor(j, col1[0], col1[1], col1[2]);
                else
                    g_pixels.setPixelColor(j, 0, 0, 0);    
            }
            else
            {
                if (j % 2 == 0)
                    g_pixels.setPixelColor(j, col2[0], col2[1], col2[2]);
                else
                    g_pixels.setPixelColor(j, 0, 0, 0);  
            }
        }   
        g_pixels.show();
        delay(100);
    }
    show_color(0, 0, 0);
}

void error_pattern(void)
{
    uint8_t i;

    for(i = 0; i < NUM_PIXELS; i++)
        g_pixels.setPixelColor(i, 255, 0, 0);  

    g_pixels.show();
}

void show_pattern(s_source_t *pattern)
{
    uint8_t  i;
    uint32_t t;
    color_t  color;

    Serial.println("Start animation\n");
    for(t = 0; t <= 6000; t+=10)
    {   

        //Serial.println(t);
        evaluate(pattern, t, &color);
        //Serial.print(color.c[0]);
        //Serial.print(", ");
        //Serial.print(color.c[1]);        
        //Serial.print(", ");
        //Serial.println(color.c[2]);
        
        for(i = 0; i < NUM_PIXELS; i++)
            g_pixels.setPixelColor(i, color.c[0], color.c[1], color.c[2]); 
        g_pixels.show();
        delay(10); 
    }
    Serial.println("Animation complete\n");
}

void setup()
{ 
    g_pixels.begin();
    startup_animation();

    
    Serial.begin(38400);
    Serial.println("led-board hello!");
    
    g_node_id = EEPROM.read(id_address);
}

void handle_packet(uint16_t len, uint8_t *packet)
{
    uint8_t    j, type, target;
    uint8_t   *data;
    void      *g_pattern = NULL;

    target = packet[0];
    if (target != BROADCAST && target != g_node_id)
         return;
    
    type = packet[1];
    data = &packet[2];
    switch(type)
    {
        case PACKET_SINGLE_COLOR:
            for(int j=0; j < NUM_PIXELS; j++)
                g_pixels.setPixelColor(j, g_pixels.Color(data[0], data[1], data[2]));
            break;
        case PACKET_COLOR_ARRAY:
            for(int j=0; j < NUM_PIXELS; j++, data += 3)
                g_pixels.setPixelColor(j, g_pixels.Color(data[0], data[1], data[2]));      
            break;  
        case PACKET_PATTERN:
            g_pattern = parse(data, len - 2);
            if (!g_pattern)
            {
                Serial.println("Parse failed.");
                error_pattern();
                return;
            }

            Serial.println("Parse ok.");
            show_pattern((s_source_t *)g_pattern);
            break;  
    }
}

void loop()
{
    uint8_t            i, ch, data[3];
    static uint8_t     found_header = 0;
    static uint16_t    crc = 0, len = 0, recd = 0;

    if (Serial.available() > 0) 
    {
        ch = Serial.read();
        if (!found_header)
        {
            if (ch == 0xFF)
            {
                found_header = 1;
            }
        }
        else
        {
            if (!len)
            {
                // We just found the header, now a realistic packet size must follow
                if (ch > 0 && ch <= MAX_PACKET_LEN)
                {
                    len = ch;
                    recd = 0;
                }
                else
                    // Nope, that was no header, better keep looking.
                    found_header = 0;
            }
            else
            {
                g_packet[recd++] = ch;
                
                if (recd <= len - 2)
                    crc = _crc16_update(crc, ch);

                if (recd == len || recd == MAX_PACKET_LEN)
                {
                    uint16_t *pcrc;
                            
                            
                    // if we received the right length, check the crc. If that matches, we have a packet!
                    if (recd == len)
                    {            
                        pcrc = (uint16_t *)(g_packet + len - 2);
                        if (crc == *pcrc)
                            handle_packet(len - 2, g_packet);
                    }

                    len = 0;
                    crc = 0;
                    found_header = 0;
                    recd = 0;
                }
            }
        }
    }
}
