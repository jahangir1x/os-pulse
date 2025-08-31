#include <chrono>
#include <fstream>
#include <iostream>
#include <thread>
using namespace std;

int main() {
    const std::string filename = "log.txt";
    const std::string message = "Hello, world!\n";

    while (true) {
        ofstream outfile(filename, ios::app);
        if (!outfile) {
            cerr << "Error opening file: " << filename << endl;
            break;
        }

        outfile << message;
        cout << "appended to " << filename << endl;
        outfile.close();

        this_thread::sleep_for(chrono::seconds(3));
    }

    return 0;
}
