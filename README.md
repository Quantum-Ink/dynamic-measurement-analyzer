# Dynamic Measurement Data Analyzer

动态测量数据采集与分析平台

> Measurement & Control Technology and Instrumentation Project

---

## 1. 项目简介

Dynamic Measurement Data Analyzer 是一个面向测控技术与仪器专业实验、传感器实验和动态测量研究的数据分析平台。

项目采用：

- C++ 负责传感器数据后端
- HTTP REST API 负责数据传输
- Python 负责数据分析与可视化
- GitHub 负责项目版本管理

当前系统可以从 CSV、Excel 或 C++ Sensor Data Backend 获取测量数据，并进行统计分析、数字滤波和动态响应分析。

---

## 2. 系统架构

```text
┌─────────────────────┐
│      Sensor         │
│      传感器          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ C++ Sensor Backend  │
│ 传感器数据采集后端    │
└──────────┬──────────┘
           │
           │ HTTP REST API
           ▼
┌─────────────────────┐
│ Python Data Analyzer│
│ Python 数据分析平台   │
└──────────┬──────────┘
           │
           ├───────────────┐
           ▼               ▼
      数据处理          数据可视化
           │               │
           ▼               ▼
      动态分析        动态响应曲线
