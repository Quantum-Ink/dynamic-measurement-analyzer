#pragma once

#include <map>
#include <string>
#include "Sensor.h"

class SensorManager {
private:
    std::map<std::string, Sensor> sensors;

public:
    void addSensor(const std::string& name);

    bool hasSensor(const std::string& name) const;

    Sensor& getSensor(const std::string& name);

    void listSensors() const;

    const std::map<std::string, Sensor>& getSensors() const;
};