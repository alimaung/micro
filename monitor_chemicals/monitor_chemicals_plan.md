
# 📷 Developer Monitoring System Plan (ESP32-Based)

## 🔬 Overview

This system monitors the chemical state of a photographic **developer solution** (e.g., Piccolo-Eco Developer Typ 25), focusing on the redox chemistry involved in developing **silver halide microfilm**.

Secondary processes like **fixing** and **cleaning** are included for context, but the primary goal is to track developer effectiveness using sensors and an ESP32.

---

## ⚗️ Chemical Process: Developer and Silver Halide

### 🎞️ Film Chemistry (Simplified Emulsion Layer)

Film contains:
- **Silver halide crystals**: `AgBr` or `AgCl`
- Suspended in gelatin

When exposed to light, latent image forms:
```
AgBr (light-exposed) → Ag⁺ + Br⁻ + e⁻
```

---

### 🧪 Developer Reaction: Reduction to Metallic Silver

**Main developer**: Phenidone (C₉H₁₀N₂O)

#### 🔁 Reduction Reaction
Phenidone donates electrons to silver ions:

```
Ag⁺ + e⁻ → Ag⁰ (black metallic silver)
```

#### 🔬 Overall Reaction (Simplified):
```
Phenidone (Red) + Ag⁺  → Phenidone (Ox) + Ag⁰ (metallic image)
```

**Result:** Exposed silver halide is reduced to black metallic silver → visible image  
**Unexposed silver halide remains unchanged → removed later by fixer**

---

## 📉 How the Developer Changes Over Time

| Component           | Role                      | After Use                            |
|---------------------|---------------------------|---------------------------------------|
| **Phenidone**        | Reducing agent            | Oxidized → inactive                   |
| **Potassium carbonate** | Maintains high pH      | Gradually depleted                    |
| **Sodium sulfite**   | Antioxidant               | Consumed → less protection from air   |
| **EDTA (Trilon B)**  | Chelates metal ions       | Largely stable                        |

### 🧪 Side Effects of Depletion:
- pH drops
- Oxidized phenidone builds up
- Risk of fogging or underdevelopment increases

---

## 🧠 System Design: ESP32 Monitoring Setup

### 🎯 Objective:
Track developer **pH** in real-time using ESP32 and a **pH probe**.

---

### 🔌 Hardware Components

| Component               | Purpose                        |
|-------------------------|--------------------------------|
| ESP32 Dev Board         | Main controller                |
| Analog pH Sensor (BNC)  | Detects pH drop (e.g. SEN0161) |
| pH Calibration Buffers  | For accurate readings (pH 4/7/10) |
| (Optional) OLED Display | Show live readings             |
| Waterproof Housing      | Safe placement in developer bath |

---

### 🧪 Target Sensor Range
| Fresh Developer | ~pH 10.0–10.4 |
| Near Depletion  | ~pH 9.4–9.6   |
| Exhausted       | < pH 9.2      |

Set a threshold (e.g. 9.4) to trigger maintenance alert.

---

## 🔁 Secondary Fluids Overview

### 🧴 Fixer Solution

- **Sodium Thiosulfate (Na₂S₂O₃)**: Dissolves unexposed silver halide
- **Sodium Sulfite (Na₂SO₃)**: Preserves fixer

#### Reaction:
```
AgBr + 2 Na₂S₂O₃ → Na₃[Ag(S₂O₃)₂] + NaBr
```

Optional: Track **conductivity** to estimate silver buildup.

---

### 💧 Cleaner 1 & 2

| Cleaner       | Contents             | Sensor?                |
|---------------|----------------------|-------------------------|
| **Cleaner 1** | Sulfite (1–5%)       | Not needed (replace w/ fixer) |
| **Cleaner 2** | Deionized Water      | Conductivity (optional)       |

---

## 🧭 Data Logging & Alerts

| Feature            | Description                                      |
|--------------------|--------------------------------------------------|
| ESP32 + RTC        | Timestamps pH logs locally or via SD card        |
| Wi-Fi/Bluetooth    | Send alerts to mobile/web dashboard              |
| Threshold Alarms   | LED/buzzer/display warnings when pH too low      |
| Manual Calibration | Button or serial command for recalibration       |

---

## 🎯 Summary: What to Monitor?

| Fluid         | Sensor             | Why                              |
|---------------|--------------------|-----------------------------------|
| **Developer** | ✅ pH               | Most reliable & relevant          |
| Fixer         | ⚠️ Conductivity     | Optional for silver ion buildup   |
| Cleaner 1     | ❌ None             | Change with fixer                 |
| Cleaner 2     | ⚠️ Conductivity     | Optional; detects contamination   |

---

## 📌 Final Thoughts

This ESP32-based system helps you:
- Visualize chemical degradation in real-time
- Replace fluids proactively
- Ensure consistent film quality
- Learn deeper chemical/physical relationships in analog film processing
