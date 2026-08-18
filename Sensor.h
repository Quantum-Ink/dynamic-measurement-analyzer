#pragma once

#include <string>
#include <vector>


class Sensor
{
private:

    // 传感器名称
    std::string name;

    // 测量数据
    std::vector<double> data;

    // 每个数据对应的时间戳
    std::vector<std::string> timestamps;


public:

    // ========================================================
    // 构造函数
    // ========================================================

    Sensor(
        const std::string& sensorName
    );


    // ========================================================
    // 添加数据
    //
    // 不指定时间戳时自动生成当前时间
    // ========================================================

    void addData(
        double value
    );


    // 指定时间戳
    void addData(
        double value,
        const std::string& timestamp
    );


    // ========================================================
    // 基本信息
    // ========================================================

    const std::string& getName() const;


    // ========================================================
    // 数据输出
    // ========================================================

    void printData() const;


    // ========================================================
    // 统计
    // ========================================================

    double getAverage() const;

    double getMax() const;

    double getMin() const;


    // ========================================================
    // 异常检测
    // ========================================================

    std::vector<double> detectAnomalies(
        double minLimit,
        double maxLimit
    ) const;


    // ========================================================
    // 获取数据
    // ========================================================

    const std::vector<double>& getData() const;


    // 获取时间戳
    const std::vector<std::string>&
    getTimestamps() const;
};