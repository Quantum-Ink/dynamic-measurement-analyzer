import csv
import random
import math


# =========================
# 实验参数
# =========================

SAMPLE_COUNT = 200

TRUE_VALUE_1 = 125.0
TRUE_VALUE_2 = 130.0

STEP_INDEX = 100

NOISE_STD = 0.5


# =========================
# 生成动态数据
# =========================

data = []


for i in range(SAMPLE_COUNT):

    # 阶跃变化
    if i < STEP_INDEX:

        true_value = TRUE_VALUE_1

    else:

        true_value = TRUE_VALUE_2


    # 随机噪声
    noise = random.gauss(
        0,
        NOISE_STD
    )


    measurement = (
        true_value +
        noise
    )


    data.append(
        (
            i + 1,
            true_value,
            measurement
        )
    )


# =========================
# 保存
# =========================

with open(
    "dynamic_measurement.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "Sequence",
            "True_Value_mm",
            "Measurement_mm"
        ]
    )


    for row in data:

        writer.writerow(row)


print(
    "Dynamic measurement data generated."
)

print(
    "File: dynamic_measurement.csv"
)

print(
    f"Samples: {SAMPLE_COUNT}"
)

print(
    f"Step: {TRUE_VALUE_1} "
    f"-> {TRUE_VALUE_2} mm"
)

print(
    f"Step position: "
    f"{STEP_INDEX}"
)