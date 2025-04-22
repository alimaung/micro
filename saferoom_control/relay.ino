// Serial Relay Controller for ESP32
// Controls 8 relays via serial commands

// Define relay pins - changed to more reliable pins that won't pull on boot
// Original pins: 13, 12, 14, 27, 26, 25, 33, 32
// New pins: 16, 17, 18, 19, 21, 22, 23, 5
const int relayPins[] = {16, 17, 18, 19, 21, 22, 23, 5};
const int numRelays = 8;

// Store relay states (false for OFF, true for ON)
bool relayStates[numRelays] = {false, false, false, false, false, false, false, false};

// Pulse duration for relay 1 (in milliseconds)
const int pulseDuration = 500;

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
  
  // Configure relay pins as outputs
  for (int i = 0; i < numRelays; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], HIGH); // Initialize all relays to OFF (HIGH = OFF for most relay modules)
  }
  
  // Reserve memory for inputString
  inputString.reserve(20);

  // Send initial relay status
  printRelayStatus();
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

  // Periodically send relay status
  static unsigned long lastStatusTime = 0;
  unsigned long currentTime = millis();
  if (currentTime - lastStatusTime >= 5000) { // Send status every 5 seconds
    printRelayStatus();
    lastStatusTime = currentTime;
  }
}

void processCommand(String command) {
  command.trim(); // Remove any whitespace or newline characters
  command.toUpperCase(); // Convert to uppercase for case-insensitive commands
  
  if (command == "STATUS") {
    printRelayStatus();
    return;
  }
  
  // Check for ON command format: ON:n
  if (command.startsWith("ON:")) {
    int relayNum = command.substring(3).toInt();
    if (isValidRelay(relayNum)) {
      setRelay(relayNum - 1, true);
      Serial.println("Relay " + String(relayNum) + " turned ON");
    }
    return;
  }
  
  // Check for OFF command format: OFF:n
  if (command.startsWith("OFF:")) {
    int relayNum = command.substring(4).toInt();
    if (isValidRelay(relayNum)) {
      setRelay(relayNum - 1, false);
      Serial.println("Relay " + String(relayNum) + " turned OFF");
    }
    return;
  }
  
  // Check for PULSE command format: PULSE:n
  if (command.startsWith("PULSE:")) {
    int relayNum = command.substring(6).toInt();
    if (isValidRelay(relayNum)) {
      pulseRelay(relayNum - 1);
      Serial.println("Relay " + String(relayNum) + " pulsed");
    }
    return;
  }
  
  // If we get here, the command wasn't recognized
  Serial.println("Unknown command: " + command);
}

// Check if relay number is valid (1-8)
bool isValidRelay(int relayNum) {
  if (relayNum < 1 || relayNum > numRelays) {
    Serial.println("Error: Invalid relay number. Use 1-8");
    return false;
  }
  return true;
}

// Set relay state (index is 0-based)
void setRelay(int index, bool state) {
  digitalWrite(relayPins[index], state ? LOW : HIGH); // LOW = ON, HIGH = OFF for most relay modules
  relayStates[index] = state;
}

// Pulse a relay (turn ON briefly then OFF)
void pulseRelay(int index) {
  // Turn relay ON
  digitalWrite(relayPins[index], LOW);
  relayStates[index] = true;
  
  // Wait for pulse duration
  delay(pulseDuration);
  
  // Turn relay OFF
  digitalWrite(relayPins[index], HIGH);
  relayStates[index] = false;
}

// Print the status of all relays
void printRelayStatus() {
  Serial.println("Relay Status:");
  for (int i = 0; i < numRelays; i++) {
    Serial.print("Relay ");
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.println(relayStates[i] ? "ON" : "OFF");
  }
}