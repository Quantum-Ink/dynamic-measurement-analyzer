import csv
import matplotlib.pyplot as plt

# =========================
# 读取测量数据
# =========================

indices = []
measurements = []

with open("measurement.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        indices.append(int(row["Index"]))
        measurements.append(float(row["Measurement_mm"]))


# =========================
# 计算统计数据
# =========================

average = sum(measurements) / len(measurements)

maximum = max(measurements)

minimum = min(measurements)


# =========================
# 绘制测量曲线
# =========================

plt.figure(figsize=(10, 6))

plt.plot(
    indices,
    measurements,
    marker="o",
    label="Measurement"
)

plt.axhline(
    average,
    linestyle="--",
    label=f"Average = {average:.4f} mm"
)

plt.axhline(
    maximum,
    linestyle=":",
    label=f"Maximum = {maximum:.4f} mm"
)

plt.axhline(
    minimum,
    linestyle=":",
    label=f"Minimum = {minimum:.4f} mm"
)


# =========================
# 图表信息
# =========================

plt.title("Measurement Data")

plt.xlabel("Measurement Index")

plt.ylabel("Distance (mm)")

plt.grid(True)

plt.legend()

plt.tight_layout()


# =========================
# 显示
# =========================

plt.show()