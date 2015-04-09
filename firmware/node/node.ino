#include <SPI85.h>
#include <Mirf.h>
#include <nRF24L01.h>
#include <MirfHardwareSpi85Driver.h>
#include <Adafruit_NeoPixel.h>

const uint8_t NUM_PIXELS = 8;
const uint8_t OUT_PIN = 1;
const uint64_t ADDRESS = 0x45;
byte addr[mirf_ADDR_LEN] = { ADDRESS, 0, 0, 0, 0 };


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
    
    //Serial.begin(9600);
    //Serial.println("node starting");

    Mirf.spi = &MirfHardwareSpi85;
    Mirf.cePin = 7;
    Mirf.csnPin = 3;    
    Mirf.init();
    Mirf.setRADDR((byte *)"aaaaa");
    Mirf.payload = 3;
    Mirf.channel = 110;
    Mirf.configRegister(RF_SETUP,0x05);
    //Mirf.configRegister(EN_AA, 0);      // turn off auto ack for all channels.
    Mirf.baseConfig = _BV(EN_CRC) | _BV(CRCO);
    Mirf.config();
    delay(100);  
    //Serial.println("startup complete:" + String(Mirf.getStatus()));
}

void loop()
{
    byte data[Mirf.payload];

    if (Mirf.dataReady())
    {   
        Mirf.getData(data);
        //Serial.println("data: " + String(data[0]) + " " + String(data[1]) + " " + String(data[2]));
        for(int i=0; i < NUM_PIXELS; i++)
        {
            pixels.setPixelColor(i, pixels.Color(data[0], data[1], data[2]));
        }
        pixels.show();
    }
}
