#include <util/crc16.h>
#include <Adafruit_NeoPixel.h>

const uint8_t NUM_PIXELS = 8;
const uint8_t OUT_PIN = 13;
const uint8_t MAX_PACKET_LEN = 32;

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUM_PIXELS, OUT_PIN, NEO_GRB + NEO_KHZ800);

void show_color(uint8_t r, uint8_t g, uint8_t b)
{
    uint8_t j;
    
    for(j = 0; j < NUM_PIXELS; j++)
        pixels.setPixelColor(j, r, g, b);
    pixels.show();
}

void startup_animation(void)
{
    uint8_t i, j;
    uint8_t col1[3] = { 128, 70, 0 };
    uint8_t col2[3] = { 128, 0, 128 };

    for(i = 0; i < 10; i++)
    {       
        for(j = 0; j < NUM_PIXELS; j++)
        {
            if (i % 2 == 0)
            {
                if (j % 2 == 1)
                    pixels.setPixelColor(j, col1[0], col1[1], col1[2]);
                else
                    pixels.setPixelColor(j, 0, 0, 0);    
            }
            else
            {
                if (j % 2 == 0)
                    pixels.setPixelColor(j, col2[0], col2[1], col2[2]);
                else
                    pixels.setPixelColor(j, 0, 0, 0);  
            }
        }   
        pixels.show();
        delay(100);
    }
    show_color(0, 0, 0);
}

void setup()
{ 
    pixels.begin();
    startup_animation();
    
    Serial.begin(38400);
}

void handle_packet(uint8_t len, uint8_t *data)
{
    uint8_t            j;

    for(int j=0; j < NUM_PIXELS; j++)
        pixels.setPixelColor(j, pixels.Color(data[0], data[1], data[2]));

    pixels.show();
}

void loop()
{
    uint8_t            i, ch, data[3];
    static uint8_t     recd = 0, found_header = 0, len = 0;
    static uint16_t    crc = 0;
    static uint8_t     packet[MAX_PACKET_LEN];

    if (Serial.available() > 0) 
    {
        ch = Serial.read();
        if (!found_header)
        {
            if (ch == 0xFF)
            {
                //show_color(255, 0, 255);
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
                packet[recd++] = ch;

                if (recd <= len - 2)
                    crc = _crc16_update(crc, ch);

                if (recd == len || recd == MAX_PACKET_LEN)
                {
                    uint16_t *pcrc;

                    // if we received the right length, check the crc. If that matches, we have a packet!
                    if (recd == len)
                    {            
                        pcrc = (uint16_t *)(packet + len - 2);
                        if (crc == *pcrc)
                            handle_packet(len - 2, packet);
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
