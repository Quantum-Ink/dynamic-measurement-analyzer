#include <iostream>
#include <string>
#include <random>
#include <thread>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <asio.hpp>

using asio::ip::tcp;

int main()
{
    try
    {
        asio::io_context io_context;

        tcp::socket socket(io_context);

        tcp::resolver resolver(io_context);

        auto endpoints =
            resolver.resolve(
                "127.0.0.1",
                "12345"
            );

        asio::connect(
            socket,
            endpoints
        );

        std::cout
            << "Sensor connected to server!"
            << std::endl;

        // =========================
        // 模拟参数
        // =========================

        const double true_value = 125.000;

        const double systematic_error = 0.200;

        std::random_device rd;

        std::mt19937 generator(rd());

        std::normal_distribution<double>
            noise(0.0, 0.5);

        // =========================
        // 时间起点
        // =========================

        auto start_time =
            std::chrono::system_clock::now();

        // =========================
        // 发送 200 个测量值
        // =========================

        for (int i = 0; i < 200; ++i)
        {
            double measurement =
                true_value
                + systematic_error
                + noise(generator);
            
            // =========================
// 模拟异常值
// 第 101 次测量故意产生异常
// =========================

if (i == 100)
{
    measurement = 999.9;
}
            // 当前时间
            auto current_time =
                std::chrono::system_clock::now();

            auto elapsed =
                std::chrono::duration_cast<
                    std::chrono::milliseconds
                >(
                    current_time - start_time
                );

            // =========================
            // 构造协议数据
            // =========================

            std::ostringstream message;

            message
                << "SEQ="
                << i + 1

                << ";TIME="
                << elapsed.count()

                << ";VALUE="
                << std::fixed
                << std::setprecision(4)
                << measurement

                << ";UNIT=mm"

                << ";STATUS=OK"

                << "\n";

            std::string data =
                message.str();

            // 发送
            asio::write(
                socket,
                asio::buffer(data)
            );

            // 控制台显示
            std::cout
                << data;

            // 50 ms
            std::this_thread::sleep_for(
                std::chrono::milliseconds(
                    50
                )
            );
        }

        // =========================
        // END
        // =========================

        std::string end_message =
            "END\n";

        asio::write(
            socket,
            asio::buffer(
                end_message
            )
        );

        std::cout
            << "All measurements sent."
            << std::endl;
    }
    catch (std::exception& e)
    {
        std::cerr
            << "Error: "
            << e.what()
            << std::endl;
    }

    return 0;
}