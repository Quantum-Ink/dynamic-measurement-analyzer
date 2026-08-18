#include "SensorManager.h"
#include <iostream>

void SensorManager::addSensor(const std::string& name) {
    sensors.emplace(name, Sensor(name));
}

bool SensorManager::hasSensor(const std::string& name) const {
    return sensors.find(name) != sensors.end();
}

Sensor& SensorManager::getSensor(const std::string& name) {
    return sensors.at(name);
}

void SensorManager::listSensors() const {
    if (sensors.empty()) {
        std::cout << "No sensors available.\n";
        return;
    }

    std::cout << "Sensors:\n";

    for (const auto& pair : sensors)
        std::cout << "- " << pair.first << std::endl;
}

const std::map<std::string, Sensor>& SensorManager::getSensors() const {
    return sensors;
}