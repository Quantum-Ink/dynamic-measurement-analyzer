import csv
import statistics
import math
import matplotlib.pyplot as plt


# ========================================
# 参数
# ========================================

MA_WINDOW = 5

MEDIAN_WINDOW = 5

EMA_ALPHA = 0.2

KALMAN_Q = 0.01

KALMAN_R = 0.25


# ========================================
# 读取数据
# ========================================

true_data = []

raw_data = []


with open(
    "dynamic_measurement.csv",
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        true_data.append(
            float(
                row["True_Value_mm"]
            )
        )

        raw_data.append(
            float(
                row["Measurement_mm"]
            )
        )


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
            sum(buffer)
            /
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
# Kalman
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

        covariance += q

        gain = (
            covariance
            /
            (covariance + r)
        )

        estimate = (
            estimate
            +
            gain *
            (
                measurement
                -
                estimate
            )
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

ma_data = moving_average(
    raw_data,
    MA_WINDOW
)

median_data = median_filter(
    raw_data,
    MEDIAN_WINDOW
)

ema_data = ema_filter(
    raw_data,
    EMA_ALPHA
)

kalman_data = kalman_filter(
    raw_data,
    KALMAN_Q,
    KALMAN_R
)


# ========================================
# 阶跃响应分析
# ========================================

STEP_INDEX = 100

FINAL_VALUE = 130.0

START_VALUE = 125.0

STEP_SIZE = (
    FINAL_VALUE -
    START_VALUE
)


# ========================================
# 计算达到 90% 的时间
# ========================================

def calculate_rise_time(
    data
):

    target = (
        START_VALUE
        +
        0.9 *
        STEP_SIZE
    )

    for i in range(
        STEP_INDEX,
        len(data)
    ):

        if data[i] >= target:

            return i - STEP_INDEX

    return None


# ========================================
# 结果
# ========================================

print()

print(
    "========================================"
)

print(
    "       Dynamic Response Analysis"
)

print(
    "========================================"
)

print(
    f"{'Method':<20}"
    f"{'90% Rise Samples':>20}"
)

print(
    "----------------------------------------"
)


methods = [
    (
        "Raw",
        raw_data
    ),
    (
        "Moving Average",
        ma_data
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

    rise_time = calculate_rise_time(
        data
    )

    if rise_time is None:

        text = "Not reached"

    else:

        text = str(
            rise_time
        )

    print(
        f"{name:<20}"
        f"{text:>20}"
    )


print(
    "========================================"
)


# ========================================
# 绘图
# ========================================

x = range(
    len(raw_data)
)


plt.figure(
    figsize=(12, 7)
)

plt.plot(
    x,
    true_data,
    linestyle="--",
    label="True Value"
)

plt.plot(
    x,
    raw_data,
    alpha=0.35,
    label="Raw"
)

plt.plot(
    x,
    ma_data,
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


plt.axvline(
    STEP_INDEX,
    linestyle=":"
)


plt.xlabel(
    "Sample"
)

plt.ylabel(
    "Measurement (mm)"
)

plt.title(
    "Dynamic Response Comparison"
)

plt.grid(True)

plt.legend()

plt.tight_layout()

plt.show()