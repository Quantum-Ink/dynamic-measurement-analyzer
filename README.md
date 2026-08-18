Dynamic Measurement Data Analyzer
=================================

多源动态测量数据采集与分析平台

项目简介
--------
用于测控技术与仪器专业实验中的动态测量数据采集、
处理、滤波、统计分析和动态响应分析。

核心架构
--------
传感器
   ↓
C++ Sensor Data Backend
   ↓
HTTP REST API
   ↓
Python Data Analyzer
   ↓
数据处理 / 滤波 / 动态分析
   ↓
可视化 / 实验报告

当前功能
--------
✓ CSV 数据导入
✓ Excel 数据导入
✓ Excel Sheet 选择
✓ 数据列选择
✓ C++ Sensor Backend API
✓ 数据预览
✓ 基础统计分析
✓ 移动平均滤波
✓ 动态响应分析
✓ 动态响应曲线

开发路线
--------
v3.0  C++ API 接入
v4.0  时间序列与采样频率分析
v5.0  实时数据监测
v6.0  数字滤波与异常值检测
v7.0  动态性能自动分析
v8.0  自动实验报告
v9.0  多传感器融合
v10.0 完整测量分析平台

技术栈
------
Python
Tkinter
Matplotlib
OpenPyXL

C++
HTTP REST API

项目定位
--------
面向测控技术与仪器专业本科实验、
传感器实验和动态测量研究。
