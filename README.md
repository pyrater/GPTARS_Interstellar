# **My Modifications and Documentation of the Build**

---

## **3D Printing**

- **Printer**: Bambu Labs P1S
- **Material Guidelines**:
  - All "Flexor" parts: **TPU** ([Buy TPU](https://us.store.bambulab.com/products/tpu-for-ams))
  - All other parts: **PETG** ([Buy PETG](https://us.store.bambulab.com/products/petg-hf))

### **Modifications**
- The default v9 chassis bottom does not allow for SD card installation due to clearance issues. Modified this part to address it.
  - **File**: `Chassis Bottom (Mod SD CARD).stl`

---

## **Plan**

### **Core Modules**
- **LLM**: ooba / OpenAI / Tabby  
- **TTS**: Local or X-TTSv2 via `xtts-api-server` (with voice cloning)  
- **SST**: Under `stt/module_stt_standalone.py` (Whisper.py)  
- **VAD**: Vlad  
- **SD**: Automatic1111  
- **Vision**: Image Classifier  

---

## **Hardware**

### **Main Components**
- **Servos**:
  - [MG996R 55g Digital RC Servo Motors](https://www.amazon.com/diymore-6-Pack-MG996R-Digital-Helicopter/dp/B0CGRP59HJ/ref=sr_1_5?sr=8-5)
  - Alternative: [LewanSoul LD-3015MG High Torque Digital Servo](https://www.aliexpress.com/item/32787763122.html)
- **Rods**:
  - [Rod Option 1](https://www.amazon.com/gp/product/B01MAYQ12S/ref=ox_sc_act_title_1)
  - [Rod Option 2](https://www.amazon.com/gp/product/B0CTSX8SJS/ref=ox_sc_act_title_2)
- **Bolts**:
  - [10mm Hex Bolts](https://www.amazon.com/gp/product/B0D9GW9K4G/ref=ox_sc_act_title_5)
  - [14mm Hex Bolts](https://www.amazon.com/gp/product/B0CR6DY4SS/ref=ox_sc_act_title_4)
  - [20mm Hex Bolts](https://www.amazon.com/gp/product/B0CR6G5XWC/ref=ox_sc_act_title_6)
  - [30mm Hex Bolts](https://www.amazon.com/gp/product/B0CR6F3N45/ref=ox_sc_act_title_7)
- **Springs**:
  - [Compression Spring](https://www.amazon.com/gp/product/B076M6SFFP/ref=ox_sc_act_title_8)
- **Bearings**:
  - [Bearings 6x15x5](https://www.amazon.com/gp/product/B07FW26HD4/ref=ox_sc_act_title_9)
- **PWM Servo Driver**:
  - [16-Channel 12-bit PWM Servo Driver](https://www.amazon.com/gp/product/B00EIB0U7A/ref=ox_sc_act_title_10)
- **Microphone**:
  - [Raspberry Pi Compatible Microphone](https://www.amazon.com/gp/product/B086DRRP79/ref=ox_sc_act_title_11)
- **Linkages**:
  - [M4 Linkage Rods](https://www.amazon.com/gp/product/B0CRDRWYXW/ref=ox_sc_act_title_12)
- **Buck Converter**:
  - [Buck Converter 12V to 6V](https://www.amazon.com/gp/product/B07SGJSLDL/ref=ox_sc_act_title_13)

### **Additional Components**
- **Raspberry Pi 5**: [Buy here](https://www.amazon.com/Raspberry-Pi-Quad-core-Cortex-A76-Processor/dp/B0CTQ3BQLS/ref=sr_1_2_sspa?sr=8-2-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1)
- **3" LCD Display**: [Buy here](https://www.amazon.com/OSOYOO-3-5inch-Display-Protective-Raspberry/dp/B09CD9W6NQ/ref=sr_1_8?sr=8-8)
- **Servo Wires**: [Buy here](https://www.amazon.com/OliYin-7-87in-Quadcopter-Extension-Futaba/dp/B0711TBZY2/ref=sr_1_7?sr=8-7)

---

## **Software**

### **Tutorials**
- **Fusion 360**: [Fusion 360 Personal Use](https://www.autodesk.com/ca-en/products/fusion-360/personal)  
- **Raspberry Pi Setup**: [Get started with Raspberry Pi](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/2)  
- **Operating System**: [Raspberry Pi OS](https://www.raspberrypi.com/software/)  

### **Servo Drivers**
- **Adafruit 16-Channel PWM HAT**:
  - [Watch this tutorial](https://www.youtube.com/watch?v=bB-xymRI8BY)
  - [Learn more](https://learn.adafruit.com/adafruit-16-channel-pwm-servo-hat-for-raspberry-pi)  

---

## **3D Printing Resources**
- **Steel/Aluminum/PLA Printing**:
  - [ForgeLabs](https://forgelabs.ca/)
  - [JLC3DP](https://jlc3dp.com/3d-printing-quote)
  - [Treatstock](https://www.treatstock.com/)
