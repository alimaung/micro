#include <WiFi.h>
#include <WebSocketsServer.h>
#include <ArduinoJson.h>
#include <esp_system.h>
#include <esp_adc_cal.h>
#include <driver/adc.h>
#include <Preferences.h>
#include <HTTPUpdate.h>

// WiFi credentials (now constants)
/* const char* ssid = "MICRO-RELAY";
const char* password = "microrelay"; */
const char* ssid = "gigacube-B9B1";
const char* password = "charleshenry1904";

// Static network config for STA mode
IPAddress staticIP(192,168,1,101);
IPAddress gateway(192,168,1,1);
IPAddress subnet(255,255,255,0);

// WebSocket server on port 81
WebSocketsServer webSocket = WebSocketsServer(81);

// Relay/LED pins for ESP32-S3-N16R8 (left side)
const int relayPins[] = {1, 2, 42, 41, 36, 35, 38, 37};
const int numRelays = 8;
bool relayStates[numRelays] = {false, false, false, false, false, false, false, false};

// Button pins for ESP32-S3-N16R8 (right side)
const int buttonPins[] = {4, 5, 6, 46, 15, 16, 17, 18};
const int numButtons = 8;

// Button debounce parameters
const unsigned long debounceDelay = 50;
unsigned long lastDebounceTime[8] = {0, 0, 0, 0, 0, 0, 0, 0};
int lastButtonState[8] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};
int buttonState[8] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};

// Pulse duration for relay 1 (ms)
const int pulseDuration = 500;

// Pulse task struct for non-blocking pulse
struct PulseTask {
  int relay;
  unsigned long endTime;
  bool active;
} pulseTask = {-1, 0, false};

// System stats
unsigned long bootTime = 0;
float cpuTemp = 0.0;
float cpuFreqMHz = 0.0;
uint32_t freeHeapBytes = 0;
float mainVoltage = 0.0;

#define VOLTAGE_MONITORING_PIN 34
#define VOLTAGE_SAMPLES 64
esp_adc_cal_characteristics_t adc_chars;

Preferences prefs;

// Configurable parameters (with defaults)
String wifiMode = "ap"; // "sta" or "ap"
String wifiSSID = "MICRO-RELAY";
String wifiPassword = "microrelay";
int relayPinConfig[numRelays] = {1, 2, 42, 41, 40, 39, 38, 37};
int pulseDurationConfig = 500;

void loadConfig() {
  prefs.begin("relaycfg", true);
  pulseDurationConfig = prefs.getInt("pulse_duration", 500);
  for (int i = 0; i < numRelays; i++) {
    relayPinConfig[i] = prefs.getInt((String("pin") + i).c_str(), relayPins[i]);
  }
  prefs.end();
}

void saveConfig() {
  prefs.begin("relaycfg", false);
  prefs.putInt("pulse_duration", pulseDurationConfig);
  for (int i = 0; i < numRelays; i++) {
    prefs.putInt((String("pin") + i).c_str(), relayPinConfig[i]);
  }
  prefs.end();
}

void applyPinConfig() {
  for (int i = 0; i < numRelays; i++) {
    pinMode(relayPinConfig[i], OUTPUT);
    digitalWrite(relayPinConfig[i], HIGH);  // Initialize relays to OFF (HIGH for relay modules)
  }
}

void setup() {
  Serial.begin(115200);
  delay(500); // Wait for serial to initialize
  Serial.println("\n\n====================");
  Serial.println("Micro Relay Tester Firmware v0.7.0");
  Serial.println("ESP32-S3-N16R8 Edition - Starting...");
  
  Serial.println("Loading config...");
  prefs.begin("relaycfg", false);
  loadConfig();
  
  Serial.println("Setting up relay pins...");
  // Use relayPinConfig for pin setup
  for (int i = 0; i < numRelays; i++) {
    pinMode(relayPinConfig[i], OUTPUT);
    digitalWrite(relayPinConfig[i], HIGH);  // Initialize relays to OFF (HIGH for relay modules)
    Serial.printf("Relay %d on pin %d initialized\n", i+1, relayPinConfig[i]);
  }
  
  Serial.println("Setting up button pins...");
  // Set up button pins with pull-up resistors
  for (int i = 0; i < numButtons; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
    Serial.printf("Button %d on pin %d initialized\n", i+1, buttonPins[i]);
  }
  
  Serial.println("Setting up ADC...");
  try {
    // ADC setup
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(ADC1_CHANNEL_6, ADC_ATTEN_DB_11);
    esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_11, ADC_WIDTH_BIT_12, 1100, &adc_chars);
    pinMode(VOLTAGE_MONITORING_PIN, INPUT);
    Serial.println("ADC initialized successfully");
  } catch(...) {
    Serial.println("Error initializing ADC, continuing anyway");
  }
  
  bootTime = millis();
  cpuFreqMHz = ESP.getCpuFreqMHz();
  Serial.printf("CPU: %.1f MHz\n", cpuFreqMHz);

  // WiFi STA mode connection with timeout
  Serial.printf("Connecting to WiFi: %s...\n", ssid);
  WiFi.mode(WIFI_STA);
  WiFi.config(staticIP, gateway, subnet);
  WiFi.begin(ssid, password);
  
  // Wait for connection with timeout
  int wifiAttempts = 0;
  while (WiFi.status() != WL_CONNECTED && wifiAttempts < 50) {
    delay(500);
    Serial.print(".");
    wifiAttempts++;
  }
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Connected! IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Failed to connect to WiFi. Continuing anyway...");
  }
  
  // WebSocket
  Serial.println("Starting WebSocket server...");
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
  
  Serial.println("Setup complete!");
  Serial.println("Micro Relay Tester Firmware v0.7.0");
  Serial.println("ESP32-S3-N16R8 Edition - Ready");
  Serial.println("====================");
}

void loop() {
  webSocket.loop();
  handlePulseTask();
  handleButtonInputs(); // Check physical buttons
}

void handleButtonInputs() {
  bool anyButtonPressed = false;
  
  // Check each button for state changes
  for (int i = 0; i < numButtons; i++) {
    // Read the button state (LOW when pressed with pull-up resistor)
    int reading = digitalRead(buttonPins[i]);
    
    // Check if button state changed
    if (reading != lastButtonState[i]) {
      // Reset the debouncing timer
      lastDebounceTime[i] = millis();
    }
    
    // If enough time has passed since last state change
    if ((millis() - lastDebounceTime[i]) > debounceDelay) {
      // If the button state has changed
      if (reading != buttonState[i]) {
        buttonState[i] = reading;
        
        // Toggle relay when button is pressed (LOW with pull-up)
        if (buttonState[i] == LOW) {
          anyButtonPressed = true;
          
          // Special handling for relay 1 (pulse mode)
          if (i == 0) {
            // If relay 1 is already on, turn it off
            if (relayStates[i]) {
              setRelay(i, false);
              broadcastRelayState(i + 1, false);
            } else {
              // Otherwise trigger a pulse
              startPulse(i);
              broadcastRelayState(i + 1, true);
            }
          } else {
            // For all other relays, simply toggle state
            bool newState = !relayStates[i];
            setRelay(i, newState);
            broadcastRelayState(i + 1, newState);
          }
        }
      }
    }
    
    // Save the current reading for next comparison
    lastButtonState[i] = reading;
  }
  
  // If any button was pressed, broadcast all relay states to keep UI in sync
  if (anyButtonPressed) {
    broadcastButtonEvent();
  }
}

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT) {
    StaticJsonDocument<384> doc;
    DeserializationError err = deserializeJson(doc, payload, length);
    if (err) {
      sendError(num, "Invalid JSON");
      return;
    }
    String action = doc["action"] | "";
    if (action == "set") {
      int relay = doc["relay"];
      bool state = doc["state"];
      if (!isValidRelay(relay)) { sendError(num, "Invalid relay"); return; }
      setRelay(relay - 1, state);
      Serial.printf("WebSocket set relay %d to %s\n", relay, state ? "ON" : "OFF");
      broadcastRelayState(relay, state);
    } else if (action == "pulse") {
      int relay = doc["relay"];
      if (relay != 1) { sendError(num, "Pulse only allowed for relay 1"); return; }
      startPulse(0);
      Serial.println("WebSocket triggered pulse on relay 1");
      broadcastRelayState(1, true);
    } else if (action == "status") {
      sendAllRelayStates(num);
    } else if (action == "system") {
      updateSystemStats();
      sendSystemStats(num);
    } else if (action == "ping") {
      sendPong(num);
    } else if (action == "get_buttons") {
      // New command to get button states
      sendButtonStates(num);
    } else if (action == "config") {
      handleConfig(num, doc["params"].as<JsonObject>());
    } else {
      sendError(num, "Unknown action");
    }
  }
}

void setRelay(int idx, bool state) {
  // Print what we're doing
  Serial.printf("Setting relay %d to %s\n", idx + 1, state ? "ON" : "OFF");
  
  // For relays, we use active LOW (relay activates when pin is LOW)
  digitalWrite(relayPinConfig[idx], state ? LOW : HIGH);
  relayStates[idx] = state;
}

void startPulse(int idx) {
  setRelay(idx, true);
  pulseTask = { idx, millis() + pulseDurationConfig, true };
}

void handlePulseTask() {
  if (pulseTask.active && millis() >= pulseTask.endTime) {
    setRelay(pulseTask.relay, false);
    Serial.printf("Pulse completed for relay %d\n", pulseTask.relay + 1);
    broadcastRelayState(pulseTask.relay + 1, false);
    pulseTask.active = false;
  }
}

void broadcastRelayState(int relay, bool state) {
  StaticJsonDocument<64> doc;
  doc["type"] = "relay";
  doc["relay"] = relay;
  doc["state"] = state;
  String msg;
  serializeJson(doc, msg);
  webSocket.broadcastTXT(msg);
}

void sendAllRelayStates(uint8_t num) {
  StaticJsonDocument<128> doc;
  doc["type"] = "relays";
  JsonArray arr = doc.createNestedArray("states");
  for (int i = 0; i < numRelays; i++) arr.add(relayStates[i]);
  String msg;
  serializeJson(doc, msg);
  webSocket.sendTXT(num, msg);
}

void updateSystemStats() {
  cpuTemp = temperatureRead();
  freeHeapBytes = ESP.getFreeHeap();
  cpuFreqMHz = ESP.getCpuFreqMHz();
  uint32_t voltage_reading = 0;
  for (int i = 0; i < VOLTAGE_SAMPLES; i++) {
    voltage_reading += adc1_get_raw(ADC1_CHANNEL_6);
  }
  voltage_reading /= VOLTAGE_SAMPLES;
  uint32_t millivolts = esp_adc_cal_raw_to_voltage(voltage_reading, &adc_chars);
  mainVoltage = millivolts / 1000.0;
}

void sendSystemStats(uint8_t num) {
  StaticJsonDocument<192> doc;
  doc["type"] = "system";
  doc["cpu_mhz"] = cpuFreqMHz;
  doc["temp_c"] = cpuTemp;
  doc["ram_kb"] = freeHeapBytes / 1024.0;
  doc["voltage_v"] = mainVoltage;
  doc["uptime_s"] = (millis() - bootTime) / 1000;
  doc["board"] = "ESP32-S3-N16R8 Tester";
  String msg;
  serializeJson(doc, msg);
  webSocket.sendTXT(num, msg);
}

void sendPong(uint8_t num) {
  StaticJsonDocument<32> doc;
  doc["type"] = "pong";
  String msg;
  serializeJson(doc, msg);
  webSocket.sendTXT(num, msg);
}

void sendError(uint8_t num, const char* msg) {
  StaticJsonDocument<64> doc;
  doc["type"] = "error";
  doc["message"] = msg;
  String out;
  serializeJson(doc, out);
  webSocket.sendTXT(num, out);
}

bool isValidRelay(int relayNum) {
  return relayNum >= 1 && relayNum <= numRelays;
}

void handleConfig(uint8_t num, JsonObject params) {
  bool changed = false;
  String msg = "";
  if (params.containsKey("pulse_duration")) {
    int pd = params["pulse_duration"];
    if (pd > 0 && pd < 10000) {
      pulseDurationConfig = pd;
      changed = true;
      msg += "pulse_duration updated; ";
    } else {
      sendError(num, "Invalid pulse_duration"); return;
    }
  }
  if (params.containsKey("relay_pins")) {
    JsonArray arr = params["relay_pins"].as<JsonArray>();
    if (arr.size() == numRelays) {
      for (int i = 0; i < numRelays; i++) relayPinConfig[i] = arr[i];
      applyPinConfig();
      changed = true;
      msg += "relay_pins updated; ";
    } else {
      sendError(num, "relay_pins must have 8 values"); return;
    }
  }
  if (params.containsKey("ota_url")) {
    String url = params["ota_url"].as<String>();
    msg += "OTA update started; ";
    sendConfigStatus(num, true, msg + "rebooting if successful");
    doOTA(url);
    return;
  }
  if (changed) {
    saveConfig();
    sendConfigStatus(num, true, msg);
  } else {
    sendConfigStatus(num, true, "No changes");
  }
}

void sendConfigStatus(uint8_t num, bool ok, String msg) {
  StaticJsonDocument<128> doc;
  doc["type"] = "config";
  doc["status"] = ok ? "success" : "error";
  doc["message"] = msg;
  String out;
  serializeJson(doc, out);
  webSocket.sendTXT(num, out);
}

void doOTA(String url) {
  WiFiClient client;
  t_httpUpdate_return ret = httpUpdate.update(client, url);
  if (ret == HTTP_UPDATE_OK) {
    ESP.restart();
  }
}

// Broadcast a button event to inform UI that a button was physically pressed
void broadcastButtonEvent() {
  StaticJsonDocument<192> doc;
  doc["type"] = "buttons";
  
  // Add all relay states to message
  JsonArray statesArray = doc.createNestedArray("states");
  for (int i = 0; i < numRelays; i++) {
    statesArray.add(relayStates[i]);
  }
  
  // Send which buttons are currently being pressed (LOW)
  JsonArray buttonsArray = doc.createNestedArray("pressed");
  for (int i = 0; i < numButtons; i++) {
    buttonsArray.add(buttonState[i] == LOW);
  }
  
  String msg;
  serializeJson(doc, msg);
  webSocket.broadcastTXT(msg);
  Serial.println("Broadcasting button event with relay states");
}

// New function to send button states
void sendButtonStates(uint8_t num) {
  StaticJsonDocument<192> doc;
  doc["type"] = "buttons";
  
  // Add all relay states to message
  JsonArray statesArray = doc.createNestedArray("states");
  for (int i = 0; i < numRelays; i++) {
    statesArray.add(relayStates[i]);
  }
  
  // Send which buttons are currently being pressed (LOW)
  JsonArray buttonsArray = doc.createNestedArray("pressed");
  for (int i = 0; i < numButtons; i++) {
    buttonsArray.add(buttonState[i] == LOW);
  }
  
  String msg;
  serializeJson(doc, msg);
  webSocket.sendTXT(num, msg);
}
