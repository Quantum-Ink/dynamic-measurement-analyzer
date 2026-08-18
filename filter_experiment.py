import statistics
import matplotlib.pyplot as plt


# =========================
# 参数
# =========================

WINDOWS = [3, 5, 10, 20]


# =========================
# 读取 CSV
# =========================

measurements = []

with open(
    "measurement.csv",
    "r",
    encoding="utf-8"
) as file:

    next(file)

    for line in file:

        line = line.strip()

        if not line:
            continue

        parts = line.split(",")

        value = float(parts[1])

        measurements.append(value)


print(
    f"Loaded {len(measurements)} measurements."
)


# =========================
# 原始标准差
# =========================

raw_std = statistics.stdev(
    measurements
)

print(
    f"\nRaw Std Dev = "
    f"{raw_std:.6f} mm"
)


# =========================
# 移动平均函数
# =========================

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


# =========================
# 实验
# =========================

results = []

for window in WINDOWS:

    filtered = moving_average(
        measurements,
        window
    )

    filtered_std = \
        statistics.stdev(
            filtered
        )

    reduction = (
        1 -
        filtered_std /
        raw_std
    ) * 100

    results.append(
        (
            window,
            filtered_std,
            reduction
        )
    )


# =========================
# 输出结果
# =========================

print()

print(
    "=============================================="
)

print(
    "       Moving Average Experiment"
)

print(
    "=============================================="
)

print(
    f"{'Window':<10}"
    f"{'Filtered Std':<20}"
    f"{'Reduction':<15}"
)

print(
    "----------------------------------------------"
)

for window, std, reduction in results:

    print(
        f"{window:<10}"
        f"{std:<20.6f}"
        f"{reduction:<15.2f}%"
    )

print(
    "=============================================="
)


# =========================
# 绘制降噪率
# =========================

windows = [
    item[0]
    for item in results
]

reductions = [
    item[2]
    for item in results
]

plt.figure(
    figsize=(8, 5)
)

plt.plot(
    windows,
    reductions,
    marker="o"
)

plt.xlabel(
    "Moving Average Window"
)

plt.ylabel(
    "Noise Reduction (%)"
)

plt.title(
    "Filter Window vs Noise Reduction"
)

plt.grid(True)

plt.tight_layout()

plt.show()


# =========================
# 绘制标准差
# =========================

stds = [
    item[1]
    for item in results
]

plt.figure(
    figsize=(8, 5)
)

plt.plot(
    windows,
    stds,
    marker="o"
)

plt.xlabel(
    "Moving Average Window"
)

plt.ylabel(
    "Standard Deviation (mm)"
)

plt.title(
    "Filter Window vs Standard Deviation"
)

plt.grid(True)

plt.tight_layout()

plt.show()