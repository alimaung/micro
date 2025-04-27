// Serial Relay Controller for ESP32
// Controls 8 relays via serial commands

#include <esp_system.h>  // For ESP32 system functions
#include <esp_adc_cal.h> // For voltage reading
#include <driver/adc.h>  // For ADC configuration in ESP-IDF style

// Define relay pins - changed to more reliable pins that won't pull on boot
// Original pins: 13, 12, 14, 27, 26, 25, 33, 32
// New pins: 16, 17, 18, 19, 21, 22, 23, 5
const int relayPins[] = {16, 17, 18, 19, 21, 22, 23, 5};
const int numRelays = 8;

// Store relay states (false for OFF, true for ON)
bool relayStates[numRelays] = {false, false, false, false, false, false, false, false};

// Pulse duration for relay 1 (in milliseconds)
const int pulseDuration = 500;

// Variables for system stats
unsigned long bootTime = 0;
float cpuTemp = 0.0;
float cpuFreqMHz = 0.0;
uint32_t freeHeapBytes = 0;
float mainVoltage = 0.0;

// For voltage measurement
#define VOLTAGE_MONITORING_PIN 34 // ADC1_CH6
#define VOLTAGE_SAMPLES 64
esp_adc_cal_characteristics_t adc_chars;

// Variables for serial command processing
String inputString = "";
bool stringComplete = false;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  Serial.println("ESP32 Serial Relay Controller");
  Serial.println("Available commands:");
  Serial.println("  ON:n  - Turn relay n ON (n=1-8)");
  Serial.println("  OFF:n - Turn relay n OFF (n=1-8)");
  Serial.println("  PULSE:n - Pulse relay n (n=1-8)");
  Serial.println("  STATUS - Show all relay states");
  Serial.println("  STATUS:SYSTEM - Show system stats");
  
  // Configure relay pins as outputs
  for (int i = 0; i < numRelays; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], LOW); // Initialize all relays to OFF (HIGH = OFF for most relay modules)
  }
  
  // Initialize voltage reading using ESP-IDF style
  // Configure ADC
  adc1_config_width(ADC_WIDTH_BIT_12);
  adc1_config_channel_atten(ADC1_CHANNEL_6, ADC_ATTEN_DB_11); // GPIO34 is ADC1_CHANNEL_6
  
  // Characterize ADC
  esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_11, ADC_WIDTH_BIT_12, 1100, &adc_chars);
  
  pinMode(VOLTAGE_MONITORING_PIN, INPUT);
  
  // Initialize system parameters
  bootTime = millis();
  cpuFreqMHz = ESP.getCpuFreqMHz();
  
  // Reserve memory for inputString
  inputString.reserve(20);

  // Send initial relay status
  printRelayStatus();
  
  // Update system stats
  updateSystemStats();
}

void loop() {
  // Process serial commands when a complete string is received
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
  
  // Read serial data
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    
    // Check for end of command (newline)
    if (inChar == '\n') {
      stringComplete = true;
      break;
    }
  }

  // Periodically update system stats and send relay status
  static unsigned long lastStatusTime = 0;
  unsigned long currentTime = millis();
  if (currentTime - lastStatusTime >= 5000) { // Update every 5 seconds
    updateSystemStats();
    
    // Only send status automatically if no commands in last 5 seconds
    static unsigned long lastCommandTime = 0;
    if (currentTime - lastCommandTime >= 5000) {
      printRelayStatus();
    }
    
    lastStatusTime = currentTime;
  }
}

void updateSystemStats() {
  // Update CPU temperature
  cpuTemp = temperatureRead();
  
  // Update free heap
  freeHeapBytes = ESP.getFreeHeap();
  
  // Update CPU frequency (rarely changes)
  cpuFreqMHz = ESP.getCpuFreqMHz();
  
  // Read supply voltage using the ESP-IDF ADC calibration
  uint32_t voltage_reading = 0;
  for (int i = 0; i < VOLTAGE_SAMPLES; i++) {
    // Use adc1_get_raw instead of analogRead for consistency with ESP-IDF
    voltage_reading += adc1_get_raw(ADC1_CHANNEL_6);
  }
  voltage_reading /= VOLTAGE_SAMPLES;
  
  // Convert ADC reading to voltage
  uint32_t millivolts = esp_adc_cal_raw_to_voltage(voltage_reading, &adc_chars);
  mainVoltage = millivolts / 1000.0; // Convert to volts
  
  // If using a voltage divider, apply the appropriate factor
  // (Most ESP32 boards run on 3.3V, but might measure via a voltage divider)
  // Uncomment if needed, based on your specific hardware setup
  // mainVoltage = mainVoltage * VOLTAGE_DIVIDER_RATIO;
}

// ALTERNATIVE VOLTAGE MEASUREMENT METHOD
// Uncomment this section and comment out the calibrated ADC method above if you encounter issues

/*
void updateSystemStats() {
  // Update CPU temperature
  cpuTemp = temperatureRead();
  
  // Update free heap
  freeHeapBytes = ESP.getFreeHeap();
  
  // Update CPU frequency (rarely changes)
  cpuFreqMHz = ESP.getCpuFreqMHz();
  
  // Simple VCC reading method using multiple samples for stability
  uint32_t vcc_reading = 0;
  for (int i = 0; i < 16; i++) {
    vcc_reading += analogRead(VOLTAGE_MONITORING_PIN);
    delay(1);  // Small delay between readings
  }
  vcc_reading /= 16;
  
  // Convert ADC reading to voltage (ESP32 reference voltage is 3.3V)
  // Formula: ADC value * 3.3V / 4095 (12-bit ADC max value)
  mainVoltage = (vcc_reading * 3.3) / 4095.0;
  
  // If your power circuit includes a voltage divider, uncomment and adjust this line:
  // mainVoltage = mainVoltage * YOUR_VOLTAGE_DIVIDER_RATIO;
}
*/

void processCommand(String command) {
  command.trim(); // Remove any whitespace or newline characters
  command.toUpperCase(); // Convert to uppercase for case-insensitive commands
  
  if (command == "STATUS") {
    printRelayStatus();
    return;
  }
  
  if (command == "STATUS:SYSTEM") {
    printSystemStats();
    return;
  }
  
  if (command == "STATUS:FULL") {
    printRelayStatus();
    printSystemStats();
    return;
  }

  // Check for specific status requests
  if (command == "STATUS:CPU") {
    Serial.println("CPU:" + String(cpuFreqMHz) + "MHz");
    return;
  }
  
  if (command == "STATUS:TEMP") {
    Serial.println("TEMP:" + String(cpuTemp, 1) + "C");
    return;
  }
  
  if (command == "STATUS:RAM") {
    Serial.println("RAM:" + String(freeHeapBytes / 1024.0, 1) + "KB");
    return;
  }
  
  if (command == "STATUS:UPTIME") {
    printUptime();
    return;
  }
  
  if (command == "STATUS:VOLTAGE") {
    Serial.println("VOLTAGE:" + String(mainVoltage, 2) + "V");
    return;
  }
  
  // New command to get a specific relay state
  if (command.startsWith("STATUS:RELAY:")) {
    int relayNum = command.substring(13).toInt();
    if (isValidRelay(relayNum)) {
      Serial.println("RELAY:" + String(relayNum) + ":" + (relayStates[relayNum - 1] ? "ON" : "OFF"));
    }
    return;
  }
  
  // Check for ON command format: ON:n
  if (command.startsWith("ON:")) {
    int relayNum = command.substring(3).toInt();
    if (isValidRelay(relayNum)) {
      setRelay(relayNum - 1, true);
      Serial.println("RELAY:" + String(relayNum) + ":ON");
    }
    return;
  }
  
  // Check for OFF command format: OFF:n
  if (command.startsWith("OFF:")) {
    int relayNum = command.substring(4).toInt();
    if (isValidRelay(relayNum)) {
      setRelay(relayNum - 1, false);
      Serial.println("RELAY:" + String(relayNum) + ":OFF");
    }
    return;
  }
  
  // Check for PULSE command format: PULSE:n
  if (command.startsWith("PULSE:")) {
    int relayNum = command.substring(6).toInt();
    if (isValidRelay(relayNum)) {
      pulseRelay(relayNum - 1);
      Serial.println("RELAY:" + String(relayNum) + ":PULSED");
    }
    return;
  }
  
  // If we get here, the command wasn't recognized
  Serial.println("ERROR:Unknown command: " + command);
}

// Print system statistics
void printSystemStats() {
  Serial.println("SYSTEM_STATS_BEGIN");
  Serial.println("CPU:" + String(cpuFreqMHz) + "MHz");
  Serial.println("TEMP:" + String(cpuTemp, 1) + "C");
  Serial.println("RAM:" + String(freeHeapBytes / 1024.0, 1) + "KB");
  printUptime();
  Serial.println("VOLTAGE:" + String(mainVoltage, 2) + "V");
  Serial.println("SYSTEM_STATS_END");
}

// Print formatted uptime
void printUptime() {
  unsigned long uptime = millis() - bootTime;
  unsigned long days = uptime / (24 * 60 * 60 * 1000);
  uptime %= (24 * 60 * 60 * 1000);
  unsigned long hours = uptime / (60 * 60 * 1000);
  uptime %= (60 * 60 * 1000);
  unsigned long minutes = uptime / (60 * 1000);
  uptime %= (60 * 1000);
  unsigned long seconds = uptime / 1000;
  
  String uptimeStr = String(days) + "d " + String(hours) + "h " + String(minutes) + "m " + String(seconds) + "s";
  Serial.println("UPTIME:" + uptimeStr);
}

// Check if relay number is valid (1-8)
bool isValidRelay(int relayNum) {
  if (relayNum < 1 || relayNum > numRelays) {
    Serial.println("ERROR:Invalid relay number. Use 1-8");
    return false;
  }
  return true;
}

// Set relay state (index is 0-based)
void setRelay(int index, bool state) {
  digitalWrite(relayPins[index], state ? HIGH : LOW); // LOW = ON, HIGH = OFF for most relay modules
  relayStates[index] = state;
}

// Pulse a relay (turn ON briefly then OFF)
void pulseRelay(int index) {
  // Turn relay ON
  digitalWrite(relayPins[index], HIGH);
  relayStates[index] = true;
  
  // Wait for pulse duration
  delay(pulseDuration);
  
  // Turn relay OFF
  digitalWrite(relayPins[index], LOW);
  relayStates[index] = false;
}

// Print the status of all relays
void printRelayStatus() {
  Serial.println("RELAY_STATUS_BEGIN");
  for (int i = 0; i < numRelays; i++) {
    Serial.println("RELAY:" + String(i + 1) + ":" + (relayStates[i] ? "ON" : "OFF"));
  }
  Serial.println("RELAY_STATUS_END");
}