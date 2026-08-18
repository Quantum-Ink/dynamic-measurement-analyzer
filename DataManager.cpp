#include "DataManager.h"

#include <fstream>
#include <iostream>
#include <sstream>
#include <algorithm>


// ============================================================
// 保存数据到 CSV
//
// 新格式：
// Timestamp,Sensor,Value
//
// 例如：
// 2026-08-18 17:40:01,Measurement,125.36
// ============================================================

bool DataManager::saveToCSV(
    const SensorManager& manager,
    const std::string& filename
)
{
    std::ofstream file(
        filename
    );


    if (!file.is_open())
    {
        std::cerr
            << "[ERROR] Failed to open file: "
            << filename
            << std::endl;

        return false;
    }


    // --------------------------------------------------------
    // CSV 表头
    // --------------------------------------------------------

    file
        << "Timestamp,Sensor,Value\n";


    // --------------------------------------------------------
    // 获取所有传感器
    // --------------------------------------------------------

    const auto& sensors =
        manager.getSensors();


    // --------------------------------------------------------
    // 写入数据
    // --------------------------------------------------------

    for (
        const auto& pair : sensors
    )
    {
        const std::string& sensorName =
            pair.first;


        const Sensor& sensor =
            pair.second;


        const auto& data =
            sensor.getData();


        const auto& timestamps =
            sensor.getTimestamps();


        // ----------------------------------------------------
        // 理论上两个 vector 长度应该完全一致
        // ----------------------------------------------------

        std::size_t count =
            std::min(
                data.size(),
                timestamps.size()
            );


        for (
            std::size_t i = 0;
            i < count;
            ++i
        )
        {
            file
                << timestamps[i]
                << ","
                << sensorName
                << ","
                << data[i]
                << "\n";
        }
    }


    file.close();


    std::cout
        << "[OK] Data saved to "
        << filename
        << std::endl;


    return true;
}


// ============================================================
// 从 CSV 加载数据
//
// 支持两种格式：
//
// 新格式：
// Timestamp,Sensor,Value
//
// 旧格式：
// Sensor,Value
// ============================================================

bool DataManager::loadFromCSV(
    SensorManager& manager,
    const std::string& filename
)
{
    std::ifstream file(
        filename
    );


    if (!file.is_open())
    {
        std::cout
            << "[INFO] No data file found: "
            << filename
            << std::endl;

        return false;
    }


    std::string line;


    // --------------------------------------------------------
    // 读取表头
    // --------------------------------------------------------

    if (!std::getline(file, line))
    {
        std::cerr
            << "[ERROR] Empty CSV file."
            << std::endl;

        return false;
    }


    // 判断 CSV 格式

    bool newFormat =
        line.find("Timestamp") !=
        std::string::npos;


    // --------------------------------------------------------
    // 读取数据
    // --------------------------------------------------------

    while (
        std::getline(
            file,
            line
        )
    )
    {
        if (line.empty())
            continue;


        std::stringstream stream(
            line
        );


        std::string timestamp;
        std::string sensorName;
        std::string valueText;


        // ====================================================
        // 新格式
        // ====================================================

        if (newFormat)
        {
            std::getline(
                stream,
                timestamp,
                ','
            );


            std::getline(
                stream,
                sensorName,
                ','
            );


            std::getline(
                stream,
                valueText
            );
        }


        // ====================================================
        // 旧格式
        // ====================================================

        else
        {
            std::getline(
                stream,
                sensorName,
                ','
            );


            std::getline(
                stream,
                valueText
            );


            // 旧数据没有时间戳
            timestamp =
                "unknown";
        }


        // ----------------------------------------------------
        // 检查数据
        // ----------------------------------------------------

        if (
            sensorName.empty() ||
            valueText.empty()
        )
        {
            continue;
        }


        try
        {
            double value =
                std::stod(
                    valueText
                );


            // ------------------------------------------------
            // 如果传感器不存在，创建
            // ------------------------------------------------

            if (
                !manager.hasSensor(
                    sensorName
                )
            )
            {
                manager.addSensor(
                    sensorName
                );
            }


            // ------------------------------------------------
            // 添加数据
            // ------------------------------------------------

            Sensor& sensor =
                manager.getSensor(
                    sensorName
                );


            sensor.addData(
                value,
                timestamp
            );
        }
        catch (
            const std::exception&
            e
        )
        {
            std::cerr
                << "[WARNING] Invalid CSV data: "
                << line
                << std::endl;

            continue;
        }
    }


    file.close();


    std::cout
        << "[OK] Data loaded from "
        << filename
        << std::endl;


    return true;
}