import csv
import statistics
import math


# =========================
# 标准件真实值
# =========================

TRUE_VALUE = 125.000


# =========================
# 读取数据
# =========================

measurements = []

with open(
    "measurement.csv",
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        measurements.append(
            float(row["Measurement_mm"])
        )


# =========================
# 样本数量
# =========================

n = len(measurements)


# =========================
# 平均值
# =========================

mean_value = statistics.mean(
    measurements
)


# =========================
# 标准差
# =========================

std_dev = statistics.stdev(
    measurements
)


# =========================
# 最大值 / 最小值
# =========================

maximum = max(
    measurements
)

minimum = min(
    measurements
)


# =========================
# 极差
# =========================

measurement_range = (
    maximum - minimum
)


# =========================
# A类标准不确定度
# =========================

u_A = (
    std_dev /
    math.sqrt(n)
)


# =========================
# 系统误差 / 偏差
# =========================

bias = (
    mean_value -
    TRUE_VALUE
)


# =========================
# 平均绝对误差
# =========================

absolute_error = abs(
    bias
)


# =========================
# 相对误差
# =========================

relative_error = (
    absolute_error /
    TRUE_VALUE
) * 100


# =========================
# 输出
# =========================

print()

print(
    "=============================================="
)

print(
    "       Precision & Accuracy Analysis"
)

print(
    "=============================================="
)

print(
    f"Samples              : {n}"
)

print(
    f"True Value           : "
    f"{TRUE_VALUE:.6f} mm"
)

print(
    f"Mean Measurement     : "
    f"{mean_value:.6f} mm"
)

print(
    f"Standard Deviation   : "
    f"{std_dev:.6f} mm"
)

print(
    f"Range                : "
    f"{measurement_range:.6f} mm"
)

print(
    f"Type-A Uncertainty   : "
    f"{u_A:.6f} mm"
)

print(
    f"Bias                 : "
    f"{bias:.6f} mm"
)

print(
    f"Absolute Error       : "
    f"{absolute_error:.6f} mm"
)

print(
    f"Relative Error       : "
    f"{relative_error:.4f}%"
)

print(
    "=============================================="
)


# =========================
# 判断
# =========================

print()

if std_dev < 0.2:

    print(
        "Precision: GOOD"
    )

else:

    print(
        "Precision: NEEDS IMPROVEMENT"
    )


if absolute_error < 0.1:

    print(
        "Accuracy: GOOD"
    )

else:

    print(
        "Accuracy: SYSTEMATIC BIAS DETECTED"
    )


print()

print(
    "Final measurement:"
)

print(
    f"{mean_value:.4f} mm"
)