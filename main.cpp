#include <iostream>
#include <string>
#include <filesystem>

#include <asio.hpp>

#include "SensorManager.h"
#include "DataManager.h"
#include "ApiServer.h"


// ============================================================
// 程序信息
// ============================================================

constexpr const char* APP_NAME =
    "Sensor Data Backend";

constexpr const char* APP_VERSION =
    "v2.0.0";


// ============================================================
// 打印程序信息
// ============================================================

void printBanner()
{
    std::cout << std::endl;

    std::cout
        << "========================================"
        << std::endl;

    std::cout
        << "       "
        << APP_NAME
        << std::endl;

    std::cout
        << "       Version "
        << APP_VERSION
        << std::endl;

    std::cout
        << "========================================"
        << std::endl;

    std::cout << std::endl;
}


// ============================================================
// 检查 Asio 环境
// ============================================================

bool checkAsio()
{
    try
    {
        asio::io_context io;

        std::cout
            << "[OK] Asio environment initialized."
            << std::endl;

        return true;
    }
    catch (const std::exception& e)
    {
        std::cerr
            << "[ERROR] Asio initialization failed: "
            << e.what()
            << std::endl;

        return false;
    }
}


// ============================================================
// 初始化传感器
// ============================================================

void initializeSensors(
    SensorManager& manager
)
{
    std::cout
        << "[INFO] Initializing sensors..."
        << std::endl;


    // 示例传感器
    //
    // 后续这里可以替换成：
    //
    // USB
    // 串口
    // 摄像头
    // 激光测距
    // 手机视觉测量
    // 其他传感器

    if (!manager.hasSensor("Measurement"))
    {
        manager.addSensor(
            "Measurement"
        );
    }


    std::cout
        << "[OK] SensorManager initialized."
        << std::endl;


    manager.listSensors();
}


// ============================================================
// 加载历史数据
// ============================================================

void loadExistingData(
    SensorManager& manager,
    const std::string& filename
)
{
    if (
        !std::filesystem::exists(
            filename
        )
    )
    {
        std::cout
            << "[INFO] No existing data file."
            << std::endl;

        return;
    }


    std::cout
        << "[INFO] Loading existing data..."
        << std::endl;


    if (
        DataManager::loadFromCSV(
            manager,
            filename
        )
    )
    {
        std::cout
            << "[OK] Existing data loaded."
            << std::endl;
    }
    else
    {
        std::cout
            << "[WARNING] Failed to load data."
            << std::endl;
    }
}


// ============================================================
// 主程序
// ============================================================

int main()
{
    printBanner();


    // ========================================================
    // 1. 检查 Asio
    // ========================================================

    if (!checkAsio())
    {
        return 1;
    }


    // ========================================================
    // 2. 创建 SensorManager
    // ========================================================

    SensorManager sensorManager;


    initializeSensors(
        sensorManager
    );


    // ========================================================
    // 3. 加载历史数据
    // ========================================================

    const std::string dataFile =
        "sensor_data.csv";


    loadExistingData(
        sensorManager,
        dataFile
    );


    // ========================================================
    // 4. 显示当前传感器状态
    // ========================================================

    std::cout
        << std::endl;

    std::cout
        << "[INFO] Current sensors:"
        << std::endl;

    sensorManager.listSensors();


    // ========================================================
    // 5. 启动 API Server
    // ========================================================

    std::cout
        << std::endl;

    std::cout
        << "[INFO] Starting API server..."
        << std::endl;


    try
    {
        startApiServer(
            sensorManager
        );
    }
    catch (
        const std::exception& e
    )
    {
        std::cerr
            << "[ERROR] API server failed: "
            << e.what()
            << std::endl;

        return 1;
    }


    return 0;
}