import csv
import math
import statistics
import matplotlib.pyplot as plt


# ========================================
# 参数
# ========================================

TRUE_VALUE = 125.000

MOVING_AVERAGE_WINDOW = 5

MEDIAN_WINDOW = 5

EMA_ALPHA = 0.2

KALMAN_Q = 0.01

KALMAN_R = 0.25


# ========================================
# 读取 measurement.csv
# ========================================

raw_data = []

with open(
    "measurement.csv",
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        value = float(
            row["Measurement_mm"]
        )

        raw_data.append(value)


# ========================================
# 移动平均
# ========================================

def moving_average(
    data,
    window
):

    result = []

    buffer = []

    for value in data:

        buffer.append(value)

        if len(buffer) > window:

            buffer.pop(0)

        result.append(
            sum(buffer) /
            len(buffer)
        )

    return result


# ========================================
# 中值滤波
# ========================================

def median_filter(
    data,
    window
):

    result = []

    buffer = []

    for value in data:

        buffer.append(value)

        if len(buffer) > window:

            buffer.pop(0)

        result.append(
            statistics.median(
                buffer
            )
        )

    return result


# ========================================
# EMA
# ========================================

def ema_filter(
    data,
    alpha
):

    result = []

    if not data:

        return result

    previous = data[0]

    result.append(
        previous
    )

    for value in data[1:]:

        current = (
            alpha * value
            +
            (1 - alpha) * previous
        )

        result.append(
            current
        )

        previous = current

    return result


# ========================================
# 一维卡尔曼滤波
# ========================================

def kalman_filter(
    data,
    q,
    r
):

    result = []

    estimate = data[0]

    covariance = 1.0

    for measurement in data:

        # Prediction

        covariance += q

        # Kalman Gain

        gain = (
            covariance /
            (covariance + r)
        )

        # Update

        estimate = (
            estimate
            +
            gain *
            (measurement - estimate)
        )

        covariance = (
            (1 - gain)
            *
            covariance
        )

        result.append(
            estimate
        )

    return result


# ========================================
# 执行滤波
# ========================================

moving_average_data = \
    moving_average(
        raw_data,
        MOVING_AVERAGE_WINDOW
    )

median_data = \
    median_filter(
        raw_data,
        MEDIAN_WINDOW
    )

ema_data = \
    ema_filter(
        raw_data,
        EMA_ALPHA
    )

kalman_data = \
    kalman_filter(
        raw_data,
        KALMAN_Q,
        KALMAN_R
    )


# ========================================
# RMSE
# ========================================

def calculate_rmse(
    data,
    true_value
):

    squared_errors = []

    for value in data:

        error = (
            value -
            true_value
        )

        squared_errors.append(
            error ** 2
        )

    return math.sqrt(
        statistics.mean(
            squared_errors
        )
    )


# ========================================
# 标准差
# ========================================

def calculate_std(
    data
):

    if len(data) < 2:

        return 0.0

    return statistics.stdev(
        data
    )


# ========================================
# 输出结果
# ========================================

print()

print(
    "=============================================="
)

print(
    "        Filter Comparison"
)

print(
    "=============================================="
)

print(
    f"{'Method':<20}"
    f"{'STD(mm)':>12}"
    f"{'RMSE(mm)':>12}"
)

print(
    "----------------------------------------------"
)


methods = [
    (
        "Raw",
        raw_data
    ),
    (
        "Moving Average",
        moving_average_data
    ),
    (
        "Median",
        median_data
    ),
    (
        "EMA",
        ema_data
    ),
    (
        "Kalman",
        kalman_data
    )
]


for name, data in methods:

    std = calculate_std(
        data
    )

    rmse = calculate_rmse(
        data,
        TRUE_VALUE
    )

    print(
        f"{name:<20}"
        f"{std:>12.6f}"
        f"{rmse:>12.6f}"
    )


print(
    "=============================================="
)


# ========================================
# 绘图
# ========================================

plt.figure(
    figsize=(12, 7)
)

x = range(
    len(raw_data)
)

plt.plot(
    x,
    raw_data,
    label="Raw",
    alpha=0.4
)

plt.plot(
    x,
    moving_average_data,
    label="Moving Average"
)

plt.plot(
    x,
    median_data,
    label="Median"
)

plt.plot(
    x,
    ema_data,
    label="EMA"
)

plt.plot(
    x,
    kalman_data,
    label="Kalman"
)

plt.axhline(
    TRUE_VALUE,
    linestyle="--",
    label="True Value"
)

plt.xlabel(
    "Sample"
)

plt.ylabel(
    "Measurement (mm)"
)

plt.title(
    "Filter Comparison"
)

plt.grid(True)

plt.legend()

plt.tight_layout()

plt.show()