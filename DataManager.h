#pragma once

#include <string>
#include "SensorManager.h"

class DataManager {
public:
    static bool saveToCSV(
        const SensorManager& manager, 
        const std::string& filename
    );

    static bool loadFromCSV(
        SensorManager& manager, 
        const std::string& filename
    );
};