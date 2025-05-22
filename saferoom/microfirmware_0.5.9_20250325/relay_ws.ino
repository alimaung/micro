#include <WiFi.h>
#include <WebSocketsServer.h>
#include <ArduinoJson.h>
#include <esp_system.h>
#include <esp_adc_cal.h>
#include <driver/adc.h>
#include <Preferences.h>
#include <HTTPUpdate.h>

// WiFi credentials (now constants)
const char* ssid = "4G-UFI-0E4";
const char* password = "microrelay";

// Static network config for STA mode
IPAddress staticIP(192,168,1,101);
IPAddress gateway(192,168,1,1);
IPAddress subnet(255,255,255,0);

// WebSocket server on port 81
WebSocketsServer webSocket = WebSocketsServer(81);

// Relay pins
const int relayPins[] = {16, 17, 18, 19, 21, 22, 23, 5};
const int numRelays = 8;
bool relayStates[numRelays] = {false, false, false, false, false, false, false, false};

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
int relayPinConfig[numRelays] = {16, 17, 18, 19, 21, 22, 23, 5};
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
    digitalWrite(relayPinConfig[i], HIGH);
  }
}

void setup() {
  Serial.begin(115200);
  prefs.begin("relaycfg", false);
  loadConfig();
  // Use relayPinConfig for pin setup
  for (int i = 0; i < numRelays; i++) {
    pinMode(relayPinConfig[i], OUTPUT);
    digitalWrite(relayPinConfig[i], HIGH);
  }
  // ADC setup
  adc1_config_width(ADC_WIDTH_BIT_12);
  adc1_config_channel_atten(ADC1_CHANNEL_6, ADC_ATTEN_DB_11);
  esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_11, ADC_WIDTH_BIT_12, 1100, &adc_chars);
  pinMode(VOLTAGE_MONITORING_PIN, INPUT);
  bootTime = millis();
  cpuFreqMHz = ESP.getCpuFreqMHz();

  // WiFi STA mode only
  WiFi.mode(WIFI_STA);
  WiFi.config(staticIP, gateway, subnet);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  // WebSocket
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
}

void loop() {
  webSocket.loop();
  handlePulseTask();
  // Optionally, broadcast status every 5s (not required if UI only updates on change)
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
      broadcastRelayState(relay, state);
    } else if (action == "pulse") {
      int relay = doc["relay"];
      if (relay != 1) { sendError(num, "Pulse only allowed for relay 1"); return; }
      startPulse(0);
      broadcastRelayState(1, true);
    } else if (action == "status") {
      sendAllRelayStates(num);
    } else if (action == "system") {
      updateSystemStats();
      sendSystemStats(num);
    } else if (action == "ping") {
      sendPong(num);
    } else if (action == "config") {
      handleConfig(num, doc["params"].as<JsonObject>());
    } else {
      sendError(num, "Unknown action");
    }
  }
}

void setRelay(int idx, bool state) {
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
  StaticJsonDocument<128> doc;
  doc["type"] = "system";
  doc["cpu_mhz"] = cpuFreqMHz;
  doc["temp_c"] = cpuTemp;
  doc["ram_kb"] = freeHeapBytes / 1024.0;
  doc["voltage_v"] = mainVoltage;
  doc["uptime_s"] = (millis() - bootTime) / 1000;
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
