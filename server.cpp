#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <asio.hpp>

using asio::ip::tcp;

int main()
{
    try
    {
        asio::io_context io_context;

        tcp::acceptor acceptor(
            io_context,
            tcp::endpoint(
                tcp::v4(),
                12345
            )
        );

        std::cout
            << "Measurement Server started."
            << std::endl;

        std::cout
            << "Waiting for sensor..."
            << std::endl;

        tcp::socket socket(io_context);

        acceptor.accept(socket);

        std::cout
            << "Sensor connected!"
            << std::endl;

        // =========================
        // CSV
        // =========================

        std::ofstream csv(
            "measurement.csv"
        );

        csv
            << "Sequence,"
            << "Time_ms,"
            << "Measurement_mm,"
            << "Unit,"
            << "Status"
            << "\n";

        // =========================
        // 接收缓冲
        // =========================

        asio::streambuf buffer;

        while (true)
        {
            asio::read_until(
                socket,
                buffer,
                '\n'
            );

            std::istream input(
                &buffer
            );

            std::string message;

            std::getline(
                input,
                message
            );

            if (message == "END")
            {
                std::cout
                    << "Measurement finished."
                    << std::endl;

                break;
            }

            // =========================
            // 解析协议
            // =========================

            std::string sequence;
            std::string time_ms;
            std::string value;
            std::string unit;
            std::string status;

            std::stringstream ss(
                message
            );

            std::string field;

            while (
                std::getline(
                    ss,
                    field,
                    ';'
                )
            )
            {
                auto pos =
                    field.find('=');

                if (
                    pos ==
                    std::string::npos
                )
                {
                    continue;
                }

                std::string key =
                    field.substr(
                        0,
                        pos
                    );

                std::string val =
                    field.substr(
                        pos + 1
                    );

                if (key == "SEQ")
                {
                    sequence = val;
                }
                else if (key == "TIME")
                {
                    time_ms = val;
                }
                else if (key == "VALUE")
                {
                    value = val;
                }
                else if (key == "UNIT")
                {
                    unit = val;
                }
                else if (key == "STATUS")
                {
                    status = val;
                }
            }

            // =========================
            // 检查数据
            // =========================

            if (
                sequence.empty() ||
                time_ms.empty() ||
                value.empty() ||
                unit.empty() ||
                status.empty()
            )
            {
                std::cout
                    << "Invalid packet:"
                    << message
                    << std::endl;

                continue;
            }

            // =========================
            // 写入 CSV
            // =========================

            csv
                << sequence
                << ","
                << time_ms
                << ","
                << value
                << ","
                << unit
                << ","
                << status
                << "\n";

            csv.flush();

            // =========================
            // 控制台显示
            // =========================

            std::cout
                << "SEQ="
                << sequence

                << " | TIME="
                << time_ms
                << " ms"

                << " | VALUE="
                << value
                << " "
                << unit

                << " | STATUS="
                << status

                << std::endl;
        }

        csv.close();

        socket.close();

        acceptor.close();

        std::cout
            << "CSV saved:"
            << " measurement.csv"
            << std::endl;
    }
    catch (
        std::exception& e
    )
    {
        std::cerr
            << "Server error: "
            << e.what()
            << std::endl;

        return 1;
    }

    return 0;
}