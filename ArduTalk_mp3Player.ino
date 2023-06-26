#include <Arduino.h>
const String version = "ESP12e_1_t5";
#define DefaultIoTtalkServerIP  "140.113.199.204"
#define DM_name  "SmartAlarm" 
#define DF_list  {"D0~","D1~","D2~","D5","D6","D7","D8","A0","Control_signal","mp3URL"}
#define nODF     10  // The max number of ODFs which the DA can pull.
#define LENTH_INFO 64    // 100;  64;  length of SSID, PASS, IP
int obLED = 2;       // NodeMCU by LoLin, GPIO 02 is on board LED 
#define clr_ROM_pin 0

#include "AudioFileSourceICYStream.h"
#include "AudioFileSourceBuffer.h"
#include "AudioGeneratorMP3.h"
#include "AudioOutputI2SNoDAC.h"
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFiMulti.h>
#include <EEPROM.h>


char IoTtalkServerIP[LENTH_INFO] = "";    // LENTH_INFO  is  64
String result;
String url = "";
String passwordkey ="";

char DefaultMyAP_SSID_[LENTH_INFO]= "meow";   // connect to Internet through this AP
char DefaultMyAP_PASS_[LENTH_INFO]= "catissocute";
char mp3URL[87]="http://192.168.137.1:32768/link.mp3";//default mp3 URL

AudioGeneratorMP3 *mp3;
AudioFileSourceICYStream *file;
AudioFileSourceBuffer *buff;
AudioOutputI2SNoDAC *out;

HTTPClient http;

// Called when a metadata event occurs (i.e. an ID3 tag, an ICY block, etc.
void MDCallback(void *cbData, const char *type, bool isUnicode, const char *string)
{
  const char *ptr = reinterpret_cast<const char *>(cbData);
  (void) isUnicode; // Punt this ball for now
  // Note that the type and string may be in PROGMEM, so copy them to RAM for printf
  char s1[32], s2[64];
  strncpy_P(s1, type, sizeof(s1));
  s1[sizeof(s1)-1]=0;
  strncpy_P(s2, string, sizeof(s2));
  s2[sizeof(s2)-1]=0;
  Serial.printf("METADATA(%s) '%s' = '%s'\n", ptr, s1, s2);
  Serial.flush();
}

// Called when there's a warning or error (like a buffer underflow or decode hiccup)
void StatusCallback(void *cbData, int code, const char *string)
{
  const char *ptr = reinterpret_cast<const char *>(cbData);
  // Note that the string may be in PROGMEM, so copy it to RAM for printf
  char s1[64];
  strncpy_P(s1, string, sizeof(s1));
  s1[sizeof(s1)-1]=0;
  Serial.printf("STATUS(%s) '%d' = '%s'\n", ptr, code, s1);
  Serial.flush();
}

String remove_ws(const String& str )   // remove white space
{
    String str_no_ws ;
    for( char c : str ) if( !std::isspace(c) ) str_no_ws += c ;
    return str_no_ws ;
}

void clr_eeprom(int sw=0){    
    /// Usage:  call  clr_eeprom(1);  if you want to do CLEAR via software on purpose
    if (sw == 0){   // Not enforce via software(不是軟體強制), 若要強制CLEAR可傳不是 0 進來
        Serial.println("Count down 5 seconds to clear EEPROM.");Serial.flush( );
        delay(168); digitalWrite(obLED, LOW);  // on board LED ON
        for(int i=0; i < 3; ++i) {   // divided into serval period to check button Released
          delay(888);
          if( digitalRead(clr_ROM_pin) == HIGH)  {  // pin released (放掉了?)
             digitalWrite(obLED, HIGH);  delay(123); // turn OFF LED
             return;   // abort if button released (已經放掉按鈕就不做 Clear EEPROM)
          } // if( button released GPIO 0 is HIGH ( Flash button Released)
         } // for( int i
         delay(1968);   // Total around 5 seconds = 3*(888+123) ms + 1968 ms
    }
    /// check clr_ROM_pin (GPIO 0) after 5 sec. to confirm (做確認) again
    if( (digitalRead(clr_ROM_pin) == LOW) || (sw == 1) ) {  //  sw==1 means on purpose in Software
        Serial.println("DO clear EEPROM NOW . . . will Reboot !"); Serial.flush( );
        digitalWrite(obLED, HIGH);   // GPIO 2 is on board LED
        delay(168);
        for(int addr=0; addr<50; addr++) EEPROM.write(addr,0);   // clear eeprom
        EEPROM.commit(); delay(168);
        Serial.println("Clear EEPROM and reboot."); Serial.flush( );
        delay(58);
        digitalWrite(0, HIGH); 
        digitalWrite(15, LOW);    // on Boot/Reset we must keep GPIO 15 LOW
        pinMode(0, INPUT_PULLUP);  digitalWrite(0, HIGH);
        digitalWrite(2, HIGH);    // GPIO 2 is on board LED
        /// make sure GPIO 0 : HIGH, GPIO 2: HIGH, GPIO 15: :LOW  when ESP.restart( )
        delay(168);    // NodeMCU 手冊建議說改用 ESP.restart( ); 因 .reset( ) 會殘留暫存器 !
        ESP.restart();   // ESP.reset();    // can ONLY use ESP.restart( );  if ESP32
    }
} // clr_eeprom(int



extern void onOffLED(int onTime=15, int offTime=60, int count=7, int finVal=1);

uint8_t wifimode = 1; //1:AP , 0: STA 
long connectFlash = 0;
void connect_to_wifi(char *wifiSSID, char *wifiPASS){

  Serial.print("Try to connect to "); Serial.println(String(wifiSSID));

  WiFi.softAPdisconnect(true);
  Serial.println("====== ----- Do WiFi.begin() to Connect to Wi-Fi----- ======");
  WiFi.begin(wifiSSID, wifiPASS);

  
  while (WiFi.status() != WL_CONNECTED  ) {  
    Serial.println("...Connecting to WiFi");
    delay(1000);
  } // while ( not timeOut 

  if(WiFi.status() == WL_CONNECTED){
    Serial.print ( "Connected to WiFi SSID ");
    Serial.println ( WiFi.SSID( ) );    Serial.flush( );

    wifimode = 0;  // STA  , station mode
  }
  
}  // connect_to_wifi( 

int iottalk_register(void){

    url = "http://" + String(DefaultIoTtalkServerIP) + ":9999/";  
    
    String df_list[] = DF_list;
    int n_of_DF = sizeof(df_list)/sizeof(df_list[0]); // the number of DFs in the DF_list
    String DFlist = ""; 
    for (int i=0; i<n_of_DF; i++){
        DFlist += "\"" + df_list[i] + "\"";  
        if (i<n_of_DF-1) DFlist += ",";
    }
  
    uint8_t MAC_array[6];
    WiFi.macAddress(MAC_array);//get esp12f mac address
    for (int i=0;i<6;i++){
        if( MAC_array[i]<0x10 ) url+="0";
        url+= String(MAC_array[i],HEX);      //Append the mac address to url string
    }
 
    //send the register packet
    Serial.println("[HTTP] POST..." + url);
    String profile="{\"profile\": {\"d_name\": \"";
    //profile += "MCU.";
    for (int i=3;i<6;i++){
        if( MAC_array[i]<0x10 ) profile+="0";
        profile += String(MAC_array[i],HEX);
    }
    profile += "\", \"dm_name\": \"";
    profile += DM_name;
    profile += "\", \"is_sim\": false, \"df_list\": [";
    profile +=  DFlist;
    profile += "]}}";

    http.begin(url);
    http.addHeader("Content-Type","application/json");
    int httpCode = http.POST(profile);

    Serial.println("[HTTP] Register... code: " + (String)httpCode );
    Serial.println(http.getString());
    //http.end();
    url +="/";  
    return httpCode;
}

String df_name_list[nODF];
String df_timestamp[nODF];
void init_ODFtimestamp(){
  for (int i=0; i<nODF; i++) df_timestamp[i] = "";
  for (int i=0; i<nODF; i++) df_name_list[i] = "";  
}

int DFindex(char *df_name){
    for (int i=0; i<nODF; i++){
        if (String(df_name) ==  df_name_list[i]) return i;
        else if (df_name_list[i] == ""){
            df_name_list[i] = String(df_name);
            return i;
        }
    }
    return nODF+1;  // df_timestamp is full
}

int push(char *df_name, String value){

    http.begin( url + String(df_name));
    http.addHeader("Content-Type","application/json");
    String data = "{\"data\":[" + value + "]}";
    int httpCode = http.PUT(data);
    if (httpCode != 200) Serial.println("[HTTP] PUSH \"" + String(df_name) + "\"... code: " + (String)httpCode + ", retry to register.");
    http.end();
    return httpCode;
}

String pull(char *df_name){

    http.begin( url + String(df_name) );
    http.addHeader("Content-Type","application/json");
    int httpCode = http.GET(); //http state code
    
    if (httpCode != 200)
    {
        Serial.println("[HTTP] "+url + String(df_name)+" PULL \"" + String(df_name) + "\"... code: " + (String)httpCode + ", retry to register.");
        return "___NULL_DATA___";
    }

    String get_ret_str = http.getString();  //After send GET request , store the return string

    http.end();

    get_ret_str = remove_ws(get_ret_str);
    int string_index = 0;
    string_index = get_ret_str.indexOf("[",string_index);
    String portion = "";  //This portion is used to fetch the timestamp.
    if (get_ret_str[string_index+1] == '[' &&  get_ret_str[string_index+2] == '\"'){
        string_index += 3;
        while (get_ret_str[string_index] != '\"'){
          portion += get_ret_str[string_index];
          string_index+=1;
        }
        
        if (df_timestamp[DFindex(df_name)] != portion){
            df_timestamp[DFindex(df_name)] = portion;
            string_index = get_ret_str.indexOf("[",string_index);
            string_index += 1;
            portion = ""; //This portion is used to fetch the data.
            while (get_ret_str[string_index] != ']'){
                portion += get_ret_str[string_index];
                string_index+=1;
            }
            return portion;   // return the data.
         }
         else return "___NULL_DATA___";
    }
    else return "___NULL_DATA___";
}


void onOffLED(int onTime, int offTime, int count, int finVal){
  digitalWrite(obLED, HIGH); delay(15);
  for(int i=0; i < count; ++i) {
    digitalWrite(obLED, LOW); delay(onTime);
    digitalWrite(obLED, HIGH); delay(offTime);
  }
  digitalWrite(obLED, finVal);   // 1 = Off,  0== On
} // onOffLED(

long sensorValue, suspend = 0;
long cycleTimestamp = millis();

void setup() {
    Serial.begin(115200);

    
    pinMode(obLED, OUTPUT); // D4 : on board led, GPIO 2
    digitalWrite(obLED, LOW);   // turn On the on board LED
    pinMode(clr_ROM_pin, INPUT_PULLUP); // D3, GPIO 0: clear eeprom button

    pinMode(16, OUTPUT);// D0~    
    pinMode(5, OUTPUT); // D1~    
    pinMode(4, OUTPUT); // D2~
    pinMode(14, OUTPUT);// D5
    pinMode(12, OUTPUT);// D6    
    pinMode(13, OUTPUT);// D7        
    pinMode(15, OUTPUT);// D8        

    EEPROM.begin(512);

    char *wifissid=DefaultMyAP_SSID_;
    char *wifipass=DefaultMyAP_PASS_;

 
    connect_to_wifi(wifissid, wifipass);

    int statesCode = 0;
    long tryRegTime = millis( );
    while (statesCode != 200) {
        statesCode = iottalk_register();
        if (statesCode != 200){
            Serial.println("Retry to register to the IoTtalk server. Suspend 3 seconds.");
            if (digitalRead(clr_ROM_pin) == LOW) clr_eeprom();
            delay(1000);
            if (digitalRead(clr_ROM_pin) == LOW) clr_eeprom();
            delay(1000);
            if (digitalRead(clr_ROM_pin) == LOW) clr_eeprom();
            delay(1000);
        } // if (
 
    } // while( != 200
    
    init_ODFtimestamp();

    digitalWrite(16,LOW);   // D0~
    digitalWrite(5,LOW);    // D1~
    digitalWrite(4,LOW);    // D2~
    digitalWrite(14,LOW);    /// D5
    digitalWrite(12,LOW);    /// D6
    digitalWrite(13,LOW);    /// D7
    digitalWrite(15,LOW);    /// D8

  audioLogger = &Serial;

  out = new AudioOutputI2SNoDAC();
  mp3 = new AudioGeneratorMP3();
  mp3->RegisterStatusCB(StatusCallback, (void*)"mp3");


} 

int pinA0; 
long LEDflashCycle = millis();
long LEDonCycle = millis();
int LEDhadFlashed = 0;
int LEDisON = 0;
char Control_signal='0';

void loop() {

  if (mp3->isRunning()) {
    if (!mp3->loop()) mp3->stop();
  } else if(Control_signal=='1'){
    if(file)
      delete file;
    file = new AudioFileSourceICYStream(mp3URL);
    file->RegisterMetadataCB(MDCallback, (void*)"ICY");
    mp3->begin(file, out);
  }

    pinA0 = analogRead(A0);
    int tmp87=pinA0/4-22;
    if (tmp87 >= 0 && tmp87 <= 255) analogWrite(16, tmp87);
    tmp87=(pinA0-1)&64;
    if (tmp87 > 0 ) digitalWrite(14, 1); else digitalWrite(14, 0);
    tmp87=(pinA0-1)&128;
    if (tmp87 > 0 ) digitalWrite(12, 1); else digitalWrite(12, 0);
    tmp87=(pinA0-1)&256;
    if (tmp87 > 0 ) digitalWrite(13, 1); else digitalWrite(13, 0);
    tmp87=(pinA0-1)&512;
    if (tmp87 > 0 ) digitalWrite(4, 1); else digitalWrite(4, 0);
    if (millis() - cycleTimestamp > 10000) { 
        http.begin( url + String("A0"));
        http.addHeader("Content-Type","application/json");
        String data = "{\"data\":[" + String(pinA0) + "]}";
        int httpCode = http.PUT(data);
        http.end();
        if (httpCode != 200)
        {
            Serial.println("[HTTP] PUSH code: " + (String)httpCode);
        }else
        {
          String ttmp;
          ttmp=pull("Control_signal");
          if(ttmp[0]=='0'&&Control_signal!='0')
          {
            Control_signal='0';
            if(mp3->isRunning())
            {
              mp3->stop();
              delete file;
            }
            
          }else if(ttmp[0]=='1'&&Control_signal!='1')
          {
            Control_signal='1';
          }
          
          ttmp=pull("mp3URL");
          if(ttmp[1]=='h')
          {
            ttmp=ttmp.substring(1,ttmp.length()-1);
            ttmp.toCharArray(mp3URL,100);
          }
        }
        cycleTimestamp = millis();
    }
}