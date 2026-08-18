#include <iostream>
#include <asio.hpp>

using asio::ip::tcp;

int main() {
    try {
        asio::io_context io;

        tcp::acceptor acceptor(
            io,
            tcp::endpoint(tcp::v4(), 8080)
        );

        std::cout << "Server started." << std::endl;
        std::cout << "Waiting for client..." << std::endl;

        tcp::socket socket(io);

        acceptor.accept(socket);

        std::cout << "Client connected!" << std::endl;

        std::string message = "Hello from server!";

        asio::write(
            socket,
            asio::buffer(message)
        );

        std::cout << "Message sent." << std::endl;

    } catch (std::exception& e) {
        std::cerr << "Error: "
                  << e.what()
                  << std::endl;
    }

    return 0;
}