#include <SPI85.h>
#include <Mirf.h>
#include <nRF24L01.h>
#include <MirfHardwareSpi85Driver.h>

const uint64_t ADDRESS = 0x45;
byte addr[mirf_ADDR_LEN] = { ADDRESS, 0, 0, 0, 0 };

void setup()
{
    Serial.begin(9600);
    Serial.println("master starting");
    
    Mirf.spi = &MirfHardwareSpi85;
    Mirf.cePin = 7;
    Mirf.csnPin = 3;    
    Mirf.init();
    Mirf.setRADDR((byte *)"aaaaa");
    Mirf.payload = 3;
    Mirf.channel = 125;
    Mirf.configRegister(RF_SETUP,0x05); // 1mbps rate, HIGH transmit rate
    Mirf.configRegister(EN_AA, 0);      // turn off auto ack for all channels.
    Mirf.baseConfig = _BV(EN_CRC) | _BV(CRCO);
    Mirf.config();  
    delay(100);  
    
    Serial.println("startup complete:" + String(Mirf.getStatus()));
    pinMode(1, OUTPUT);
}

uint32_t color_wheel(byte WheelPos, byte color[3]) 
{
    WheelPos = 255 - WheelPos;
    if(WheelPos < 85) 
    {
        color[0] = 255 - WheelPos * 3;
        color[1] = 0;
        color[2] = WheelPos * 3;
    } 
    else if(WheelPos < 170) 
    {
        WheelPos -= 85;
        color[0] = 0;
        color[1] = WheelPos * 3;
        color[2] = 255 - WheelPos * 3;
    } 
    else 
    {
        WheelPos -= 170;
        color[0] = WheelPos * 3;
        color[1] = 255 - WheelPos * 3;
        color[2] = 0;
    }
}

void loop()
{
    uint16_t j;
    byte col[3];
    
    Mirf.setTADDR((byte *)"aaaaa");

    //col[0] = i % 2 ? 255 : 0;
    //col[1] = 0;
    //col[2] = i % 2 ? 0 : 255;
    //Serial.println("data: " + String(col[0]) + " " + String(col[1]) + " " + String(col[2]));

    for(j=0; j<256*5; j++) 
    {
        color_wheel(j & 255, col);
        Mirf.send(col);
        while(Mirf.isSending())
            ;

        if (j % 2)
            digitalWrite(1, HIGH);
        else
            digitalWrite(1, LOW);
        delay(20);
    }
}




