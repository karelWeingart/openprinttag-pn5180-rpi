#include "WiFi.h"
#include "esp_wifi.h"
#include <PubSubClient.h>


#include <GxEPD2_BW.h>
#include <Inter_Bold_15.h>
#include <Inter_Light_10.h>

GxEPD2_BW<GxEPD2_290_GDEY029T94, GxEPD2_290_GDEY029T94::HEIGHT> display(GxEPD2_290_GDEY029T94(/*CS=5*/ SS, /*DC=*/ 17, /*RST=*/ 16, /*BUSY=*/ 4)); // GDEY029T94  128x296, SSD1680, (FPC-A005 20.06.15)

// Battery setup
#define ADCpin 34 
#define DividerRatio 1.7693877551 

volatile bool messageReceived = false;

// Sleep setup
#define SLEEP_SECONDS 60
#define WAKEUP_TIME 1

// Network/MQTT setup
const char* ssid="your wifi ssid";
const char* password="your wifi passwd";
const char* mqttServer = "mqtt server url"; 
const int mqttPort = 1883; // Change this if needed
const char* mqttTopic = "rfid/tag"; // Change this if different topic used.


WiFiClient espClient;
PubSubClient client(espClient);

// Setup for caching data between wakes
#define MAX_ITEMS 4
#define MAX_KEY_LEN 16
#define MAX_VAL_LEN 16
#define REDRAW_WAKE_THRESHOLD 8000 // E-Ink is redrawn after 8000 wakeups

RTC_DATA_ATTR int wakeCount = 0;
RTC_DATA_ATTR char messageBody[512];
RTC_DATA_ATTR int messageBodyLen = 0;
RTC_DATA_ATTR char displayKeys[MAX_ITEMS][MAX_KEY_LEN] = {
    "Name:"
};
RTC_DATA_ATTR char displayVals[MAX_ITEMS][MAX_VAL_LEN] = {
    "MQTT Display",
};
RTC_DATA_ATTR int displayItemCount = 4;

// Global cursor position for e ink
int cursorX = 0;
int cursorY = 0;

template <typename DisplayType>
void printLine(DisplayType &display, const char* text, const GFXfont* font, int paddingH, int paddingV, bool inverse = false) {
    display.setFont(font);

    const int lineHeight = 30;

    cursorY += lineHeight;

    if (inverse) {
        display.fillRect(
            0,
            cursorY - lineHeight + 4,
            display.width(),
            lineHeight,
            GxEPD_BLACK
        );
        display.setTextColor(GxEPD_WHITE);
    } else {
        display.setTextColor(GxEPD_BLACK);
    }
    display.setCursor(paddingV, cursorY);
    display.print(text);
}

template <typename DisplayType>
void printSplitLine(DisplayType &display, const char* key, const char* value,
                    const GFXfont* font, bool inverse = false)
{
    display.setFont(font);

    const int lineHeight = 22; 
    const int paddingLeft = 4;
    const int paddingRight = 4;

    cursorY += lineHeight;

    if (inverse) {
        display.fillRect(0, cursorY - lineHeight + 4,
                         display.width(),
                         lineHeight,
                         GxEPD_BLACK);
        display.setTextColor(GxEPD_WHITE);
    } else {
        display.setTextColor(GxEPD_BLACK);
    }

    display.setCursor(paddingLeft, cursorY);
    display.print(key);

    int middlePoint = display.width() / 2;
    display.setCursor(middlePoint, cursorY);
    display.print(value);
}

template <typename DisplayType>
void renderBatteryBar(DisplayType &display, float maxVoltage, float minVoltage, float currentVoltage) 
{
    if (currentVoltage < minVoltage) currentVoltage = minVoltage;
    if (currentVoltage > maxVoltage) currentVoltage = maxVoltage;

    float percent = (currentVoltage - minVoltage) / (maxVoltage - minVoltage);
    if (percent < 0) percent = 0;
    if (percent > 1) percent = 1;

    const int margin = 4;
    const int barHeight = 12;
    const int x = margin;
    const int y = display.height() - barHeight - margin;
    const int w = display.width() - margin * 2;

    int filled = static_cast<int>(w * percent);

    display.drawRect(x, y, w, barHeight, GxEPD_BLACK);

    if (filled > 2) {
        display.fillRect(x + 1, y + 1, filled - 2, barHeight - 2, GxEPD_BLACK);
    }
}

void initWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while(WiFi.status() !=WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println(WiFi.localIP());
}

void initDisplay() {
  pinMode(2, OUTPUT);
  digitalWrite(2, HIGH);
  Serial.println("Display power ON");
 
  display.init(); 
  display.setRotation(1);
}

void parseFormData() {
    displayItemCount = 0;

    char bodyCopy[512];
    strncpy(bodyCopy, messageBody, sizeof(bodyCopy));
    bodyCopy[sizeof(bodyCopy)-1] = '\0';

    char *pair = strtok(bodyCopy, "&");

    while (pair && displayItemCount < MAX_ITEMS) {
        char *eq = strchr(pair, '=');

        if (eq) {
            *eq = '\0';
            char *key = pair;
            char *val = eq + 1;

            strncpy(displayKeys[displayItemCount], key, MAX_KEY_LEN - 1);
            displayKeys[displayItemCount][MAX_KEY_LEN - 1] = '\0';

            strncpy(displayVals[displayItemCount], val, MAX_VAL_LEN - 1);
            displayVals[displayItemCount][MAX_VAL_LEN - 1] = '\0';

            displayItemCount++;
        }

        pair = strtok(NULL, "&");
    }

    Serial.printf("Parsed %d items\n", displayItemCount);
}

void renderDisplay() {
    initDisplay();
    float bat_voltage = analogReadMilliVolts(ADCpin) * DividerRatio / 1000.0;
    display.firstPage();
    do {
        printLine(display, displayVals[0], &Inter_18pt_Bold15pt7b,4,2, true);
        for (int i = 1; i < displayItemCount; i++) {   // FIXED
            printSplitLine(display, displayKeys[i], displayVals[i], &Inter_18pt_Light10pt7b);
        }
        renderBatteryBar(display, 4.2, 3.4, bat_voltage);
    } while (display.nextPage());
}


void connectMqtt() { 
    while (!client.connected()) { 
    	Serial.print("Attempting MQTT connection..."); 
    	if (client.connect("ESP32Client")) { 
    		Serial.println("connected"); 
    		client.subscribe(mqttTopic); } 
    	else { 
    		Serial.print("failed, rc="); 
    		Serial.print(client.state()); 
    		Serial.println(" retrying in 5 seconds"); 
    		delay(5000); 
    	} 
    } 
}

void callback(char* topic, byte* payload, unsigned int length) {
    if (length >= sizeof(messageBody)) {
        length = sizeof(messageBody) - 1;
    }

    char incoming[512];
    memcpy(incoming, payload, length);
    incoming[length] = '\0';

    if (strcmp(incoming, messageBody) == 0) {
        Serial.println("MQTT payload is identical → ignoring");
        return; 
    }

    memcpy(messageBody, incoming, length + 1);
    messageBodyLen = length;

    Serial.print("New MQTT payload stored: ");
    Serial.println(messageBody);
    parseFormData();
    renderDisplay();
    messageReceived = true;
}

void setup() {
  Serial.begin(115200);
  delay(100);  
  
  esp_sleep_wakeup_cause_t cause = esp_sleep_get_wakeup_cause();  
  if (cause == ESP_SLEEP_WAKEUP_UNDEFINED || wakeCount > REDRAW_WAKE_THRESHOLD) {
      renderDisplay();
      wakeCount = 0;
      esp_sleep_enable_timer_wakeup(1 * 1000000ULL);
      delay(50);
      esp_deep_sleep_start(); 
  } else {
    wakeCount++;
  }
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  initWiFi();
  if (!client.connected()) { 
    connectMqtt(); 
  } 
  unsigned long start = millis();


  while (millis() - start < WAKEUP_TIME * 1000) {
    client.loop();
    if (messageReceived) break;
  }
  if (messageReceived) {
    Serial.println("Message received → staying awake");
  }

  esp_sleep_enable_timer_wakeup((uint64_t)SLEEP_SECONDS * 1000000ULL);
  delay(50);
  esp_deep_sleep_start(); 
}

void loop() {
  // nothing happens here..  
}
