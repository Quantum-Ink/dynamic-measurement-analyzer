#include "ApiServer.h"
#include "DataManager.h"

#include "crow.h"

#include <iostream>
#include <string>
#include <algorithm>

// ============================================================
// 启动 API Server
// ============================================================

void startApiServer(
    SensorManager& manager
)
{
    crow::SimpleApp app;


    // ========================================================
    // GET /
    // ========================================================

    CROW_ROUTE(app, "/")
    ([]()
    {
        return "Sensor Data Backend is running!";
    });


    // ========================================================
    // GET /sensors
    //
    // 获取所有传感器
    // ========================================================

    CROW_ROUTE(app, "/sensors")
    ([&manager]()
    {
        crow::json::wvalue result;

        std::vector<std::string> sensorNames;

        const auto& sensors =
            manager.getSensors();


        for (const auto& pair : sensors)
        {
            sensorNames.push_back(
                pair.first
            );
        }


        result["sensors"] =
            std::move(sensorNames);


        return crow::response(
            result
        );
    });


    // ========================================================
    // GET /sensors/<sensor>/data
    //
    // 获取传感器全部数据
    // ========================================================

    CROW_ROUTE(
        app,
        "/sensors/<string>/data"
    )
    ([&manager](
        const std::string& sensorName
    )
    {
        if (
            !manager.hasSensor(
                sensorName
            )
        )
        {
            crow::json::wvalue error;

            error["error"] =
                "Sensor not found";


            return crow::response(
                404,
                error
            );
        }


        const Sensor& sensor =
            manager.getSensor(
                sensorName
            );


        const auto& data =
            sensor.getData();

        const auto& timestamps =
            sensor.getTimestamps();

        crow::json::wvalue result;

        result["sensor"] =
            sensorName;

        crow::json::wvalue::list values;

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
            crow::json::wvalue item;

            item["timestamp"] =
                timestamps[i];

            item["value"] =
                data[i];

            values.push_back(
                std::move(item)
            );
        }

        result["data"] =
            std::move(values);

        return crow::response(
            result
        );
    });


    // ========================================================
    // POST /sensors/<sensor>/data
    //
    // 添加一个新的测量值
    //
    // JSON:
    //
    // {
    //     "value": 125.36
    // }
    //
    // ========================================================

    CROW_ROUTE(
        app,
        "/sensors/<string>/data"
    )
    .methods(
        crow::HTTPMethod::POST
    )
    ([&manager](
        const crow::request& request,
        const std::string& sensorName
    )
    {
        // ----------------------------------------------------
        // 检查 JSON
        // ----------------------------------------------------

        auto body =
            crow::json::load(
                request.body
            );


        if (!body)
        {
            crow::json::wvalue error;

            error["error"] =
                "Invalid JSON";


            return crow::response(
                400,
                error
            );
        }


        // ----------------------------------------------------
        // 检查 value
        // ----------------------------------------------------

        if (
            !body.has("value")
        )
        {
            crow::json::wvalue error;

            error["error"] =
                "Missing value";


            return crow::response(
                400,
                error
            );
        }


        try
        {
            double value =
                body["value"].d();


            // ------------------------------------------------
            // 如果传感器不存在，自动创建
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
                value
            );

            DataManager::saveToCSV(
                manager,
                "sensor_data.csv"
            );

            // ------------------------------------------------
            // 返回结果
            // ------------------------------------------------

            crow::json::wvalue result;

            result["success"] =
                true;

            result["sensor"] =
                sensorName;

            result["value"] =
                value;


            return crow::response(
                result
            );
        }
        catch (
            const std::exception& e
        )
        {
            crow::json::wvalue error;

            error["error"] =
                e.what();


            return crow::response(
                400,
                error
            );
        }
    });


    // ========================================================
    // 启动服务器
    // ========================================================

    std::cout
        << std::endl;

    std::cout
        << "========================================"
        << std::endl;

    std::cout
        << "API Server started."
        << std::endl;

    std::cout
        << "Address: http://localhost:18080"
        << std::endl;

    std::cout
        << "========================================"
        << std::endl;


    app.port(
        18080
    )
    .multithreaded()
    .run();
}