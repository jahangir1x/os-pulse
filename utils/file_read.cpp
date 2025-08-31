
#include <chrono>
#include <fstream>
#include <iostream>
#include <string>
#include <thread>

int main() {
    while (true) {
        std::ifstream inputFile("input.txt");

        if (!inputFile.is_open()) {
            std::cerr << "Failed to open input.txt\n";
        } else {
            std::string line;
            std::cout << "[INFO] Reading input.txt and writing to output.txt\n";
            while (std::getline(inputFile, line)) {
                std::cout << "Read: " << line << "\n";
            }
            inputFile.close();
            std::cout << "[INFO] Done. Waiting 3 seconds...\n";
        }

        std::this_thread::sleep_for(std::chrono::seconds(3));
    }

    return 0;
}
