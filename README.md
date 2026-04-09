# M5Stack Data Integration with OpenClaw via WeChat / DingTalk

> **ENT208 Session 3 — Group 17** | Coursework project using M5Stack and OpenClaw

---

## Kanban Board

[Teambition Project Board](https://www.teambition.com/project/69cdd45fcfcd439e91ac8814/tasks/view/69cdd460f8de99742f38bbdf)

---

## Project Overview

This project collects **plant humidity data** via an M5Stack device, stores it in a database, and leverages **OpenClaw's Skills mechanism** to interact with users through **WeChat / DingTalk**, enabling **natural-language queries** about plant status.

**Core idea:** Users don't need to open any app or dashboard — they can simply chat with an AI in the familiar WeChat or DingTalk environment to check plant humidity at any time. Once deployed, we can write additional Skills to let OpenClaw automate various repetitive tasks such as domain alert analysis, ticket handling, and data reporting — empowering teams and accelerating development and iteration in the AI era.

> **Hardware + AI + Workflow** — this is our complete solution.

---

## Architecture

### Data Flow

```
M5Stack (collect humidity data)
        ↓
   WiFi transmission
        ↓
  Database (store sensor data)
        ↓
  OpenClaw Skills (AI logic)
        ↓
  WeChat / DingTalk (user interaction)
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Hardware** | M5Stack C Plus + Humidity Sensor |
| **Backend** | Python Flask + SQLite |
| **AI Platform** | OpenClaw + Skills Framework |
| **Messaging** | WeChat, DingTalk |

**Example interaction:**

> *User:* "How's my plant doing?"
> → The system instantly returns real-time data and supports free-form conversation.

---

## User Experience

### Primary Features — Library Plant Monitoring Demo

- **Real-time humidity collection** via M5Stack
- **Automatic data ingestion** into an SQLite database
- **Custom Skill development** so ClawBot understands user queries
- **Natural conversation** in WeChat / DingTalk to get plant status
- **Zero expertise required** — fully natural interaction

---

## Skill-Based Architecture

| Layer | Technology |
|-------|------------|
| **Hardware** | M5Stack C Plus + Humidity Sensor |
| **Backend** | Python Flask + SQLite |
| **AI Platform** | OpenClaw + Skills Framework |
| **Messaging** | WeChat, DingTalk |

---

## Key Advantages

- Real-time plant humidity monitoring with M5Stack
- Seamless data flow into SQLite
- Skill-powered ClawBot that understands user intent
- Chat-based interaction via WeChat / DingTalk — no technical knowledge needed

---

## Scalability

| Dimension | Description |
|-----------|-------------|
| **Rapid Skill Development** | Any SOP (Standard Operating Procedure) can be quickly converted into a Skill |
| **Dify Workflows** | Support for complex multi-step automation pipelines |
| **Multi-Sensor** | Easily add temperature, light, CO₂, and more in the future |
| **Multi-Industry** | Expand from plant monitoring to industrial, office, and equipment maintenance scenarios |

---

## Enterprise Deployment with OpenClaw

We have successfully deployed OpenClaw on both **DingTalk Enterprise Edition** and **WeChat Personal Edition**, supporting:

- **Team-level collaboration** (DingTalk Enterprise)
- **Individual user access** (WeChat Personal)
- **Natural-language interaction**
- **Real-time data queries**