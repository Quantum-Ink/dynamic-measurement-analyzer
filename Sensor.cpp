#include "Sensor.h"

#include <iostream>
#include <chrono>
#include <ctime>
#include <iomanip>
#include <sstream>


// ============================================================
// 获取当前时间
// ============================================================

static std::string getCurrentTimestamp()
{
    auto now =
        std::chrono::system_clock::now();


    std::time_t time =
        std::chrono::system_clock::to_time_t(
            now
        );


    std::tm localTime{};


#ifdef _WIN32

    localtime_s(
        &localTime,
        &time
    );

#else

    localtime_r(
        &time,
        &localTime
    );

#endif


    std::ostringstream stream;


    stream
        << std::put_time(
            &localTime,
            "%Y-%m-%d %H:%M:%S"
        );


    return stream.str();
}


// ============================================================
// 构造函数
// ============================================================

Sensor::Sensor(
    const std::string& sensorName
)
{
    name = sensorName;
}


// ============================================================
// 添加数据
// 自动生成时间戳
// ============================================================

void Sensor::addData(
    double value
)
{
    addData(
        value,
        getCurrentTimestamp()
    );
}


// ============================================================
// 添加数据
// 使用指定时间戳
// ============================================================

void Sensor::addData(
    double value,
    const std::string& timestamp
)
{
    data.push_back(
        value
    );

    timestamps.push_back(
        timestamp
    );
}


// ============================================================
// 获取传感器名称
// ============================================================

const std::string&
Sensor::getName() const
{
    return name;
}


// ============================================================
// 打印数据
// ============================================================

void Sensor::printData() const
{
    std::cout
        << "Sensor: "
        << name
        << std::endl;


    std::cout
        << "Data:"
        << std::endl;


    for (
        std::size_t i = 0;
        i < data.size();
        ++i
    )
    {
        std::cout
            << "["
            << timestamps[i]
            << "] "
            << data[i]
            << std::endl;
    }
}


// ============================================================
// 平均值
// ============================================================

double Sensor::getAverage() const
{
    if (data.empty())
        return 0.0;


    double sum = 0.0;


    for (double value : data)
    {
        sum += value;
    }


    return sum / data.size();
}


// ============================================================
// 最大值
// ============================================================

double Sensor::getMax() const
{
    if (data.empty())
        return 0.0;


    double maxVal =
        data[0];


    for (double value : data)
    {
        if (value > maxVal)
        {
            maxVal = value;
        }
    }


    return maxVal;
}


// ============================================================
// 最小值
// ============================================================

double Sensor::getMin() const
{
    if (data.empty())
        return 0.0;


    double minVal =
        data[0];


    for (double value : data)
    {
        if (value < minVal)
        {
            minVal = value;
        }
    }


    return minVal;
}


// ============================================================
// 异常检测
// ============================================================

std::vector<double>
Sensor::detectAnomalies(
    double minLimit,
    double maxLimit
) const
{
    std::vector<double> anomalies;


    for (double value : data)
    {
        if (
            value < minLimit ||
            value > maxLimit
        )
        {
            anomalies.push_back(
                value
            );
        }
    }


    return anomalies;
}


// ============================================================
// 获取数据
// ============================================================

const std::vector<double>&
Sensor::getData() const
{
    return data;
}


// ============================================================
// 获取时间戳
// ============================================================

const std::vector<std::string>&
Sensor::getTimestamps() const
{
    return timestamps;
}