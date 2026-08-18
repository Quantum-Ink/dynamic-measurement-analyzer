# -*- coding: utf-8 -*-

"""
Dynamic Measurement Analyzer
实时多传感器测量分析器 v5.0

主要功能：
1. 多传感器选择
2. 实时 API 数据刷新
3. 暂停 / 继续
4. 暂停后自动追赶历史数据
5. 实时曲线
6. 实时数据表格
7. 传感器状态卡片
8. CSV 导出
9. Hampel 异常检测
10. 移动平均滤波
11. 实时采样率
12. 平均值 / 标准差
13. API 自动重连
14. 高清 Matplotlib UI
15. 不强制窗口置顶
"""

import csv
import os
import time
import statistics
import requests

from collections import deque
from datetime import datetime

import matplotlib

# ============================================================
# 中文字体
# ============================================================

matplotlib.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "Arial Unicode MS"
]

matplotlib.rcParams["axes.unicode_minus"] = False

matplotlib.rcParams["figure.dpi"] = 120
matplotlib.rcParams["savefig.dpi"] = 180

import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, RadioButtons
from matplotlib.ticker import MaxNLocator
from matplotlib.gridspec import GridSpec


# ============================================================
# 配置
# ============================================================

API_BASE_URL = "http://127.0.0.1:18080"

REFRESH_INTERVAL = 1000

MAX_POINTS = 150

FILTER_WINDOW = 5

REQUEST_TIMEOUT = 2

TABLE_ROWS = 8


# ============================================================
# API Session
# ============================================================

session = requests.Session()


# ============================================================
# API
# ============================================================

def get_sensors():

    response = session.get(
        f"{API_BASE_URL}/sensors",
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    result = response.json()

    return result.get(
        "sensors",
        []
    )


def get_sensor_data(sensor_name):

    response = session.get(
        f"{API_BASE_URL}/sensors/{sensor_name}/data",
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# Hampel
# ============================================================

def hampel_is_anomaly(
    data,
    new_value,
    window_size=7,
    threshold=3.0
):

    if len(data) < window_size:

        return False

    recent = list(data)[-window_size:]

    median_value = statistics.median(
        recent
    )

    deviations = [
        abs(x - median_value)
        for x in recent
    ]

    mad = statistics.median(
        deviations
    )

    if mad == 0:

        return (
            abs(
                new_value -
                median_value
            ) > 0.001
        )

    robust_sigma = (
        1.4826 * mad
    )

    return (
        abs(
            new_value -
            median_value
        )
        >
        threshold *
        robust_sigma
    )


# ============================================================
# Sensor Buffer
# ============================================================

def create_sensor_buffer():

    return {

        "timestamps":
            deque(maxlen=MAX_POINTS),

        "raw":
            deque(maxlen=MAX_POINTS),

        "filtered":
            deque(maxlen=MAX_POINTS),

        "all_raw":
            [],

        "all_filtered":
            [],

        "filter_buffer":
            deque(maxlen=FILTER_WINDOW),

        "last_timestamp":
            None,

        "last_value":
            0.0,

        "last_filtered":
            0.0,

        "unit":
            "mm",

        "status":
            "等待数据",

        "rate":
            0.0,

        "anomaly_count":
            0,

        "sample_count":
            0,

        "connected":
            False
    }


# ============================================================
# 获取传感器
# ============================================================

try:

    available_sensors = get_sensors()

except Exception as error:

    print()
    print("=" * 60)
    print("无法连接 API")
    print("=" * 60)
    print(error)
    print()
    print(
        "请确认 API Server 已启动："
    )
    print(
        "http://127.0.0.1:18080"
    )
    print()

    raise SystemExit


if not available_sensors:

    print("没有发现传感器。")

    raise SystemExit


# ============================================================
# 初始化缓存
# ============================================================

sensor_buffers = {}

for sensor in available_sensors:

    sensor_buffers[sensor] = \
        create_sensor_buffer()


current_sensor = available_sensors[0]

running = True

api_connected = False


# ============================================================
# 控制台
# ============================================================

print()
print("=" * 65)
print(
    "Dynamic Measurement Analyzer"
)
print(
    "实时多传感器测量分析器 v5.0"
)
print("=" * 65)

print()

print("发现传感器：")

for sensor in available_sensors:

    print(
        f"  ● {sensor}"
    )

print()

print(
    f"当前传感器：{current_sensor}"
)

print("=" * 65)


# ============================================================
# 创建 Figure
# ============================================================

figure = plt.figure(
    figsize=(15, 9),
    dpi=120
)

figure.canvas.manager.set_window_title(
    "Dynamic Measurement Analyzer v5.0"
)


# ============================================================
# GridSpec
#
# 左侧：
#   曲线
#   表格
#
# 右侧：
#   状态卡片
#   传感器选择
#   控制按钮
# ============================================================

grid = GridSpec(
    12,
    12,
    figure=figure,
    left=0.055,
    right=0.965,
    top=0.94,
    bottom=0.07,
    wspace=1.0,
    hspace=1.4
)


# ============================================================
# 曲线区域
# ============================================================

axis = figure.add_subplot(
    grid[0:7, 0:9]
)

axis.set_title(
    "实时测量曲线 / Real-Time Measurement",
    fontsize=15,
    fontweight="bold",
    pad=12
)

axis.set_xlabel(
    "时间 / Time (s)",
    fontsize=11
)

axis.set_ylabel(
    "测量值 / Measurement",
    fontsize=11
)

axis.grid(
    True,
    linestyle="--",
    alpha=0.25
)

axis.xaxis.set_major_locator(
    MaxNLocator(nbins=8)
)

axis.yaxis.set_major_locator(
    MaxNLocator(nbins=8)
)

axis.tick_params(
    labelsize=9
)


# ============================================================
# 曲线
# ============================================================

raw_line, = axis.plot(
    [],
    [],
    marker="o",
    markersize=3,
    linewidth=1.2,
    label="原始数据 Raw",
    antialiased=True
)

filtered_line, = axis.plot(
    [],
    [],
    linewidth=2.5,
    label="移动平均 Filtered",
    antialiased=True
)

axis.legend(
    loc="upper left",
    fontsize=9,
    framealpha=0.9
)


# ============================================================
# 数据表格区域
# ============================================================

table_axis = figure.add_subplot(
    grid[8:12, 0:9]
)

table_axis.axis(
    "off"
)

table_axis.set_title(
    "实时数据 / Live Data",
    fontsize=12,
    fontweight="bold",
    loc="left",
    pad=8
)


# ============================================================
# 状态卡片区域
# ============================================================

card_axis = figure.add_subplot(
    grid[0:4, 9:12]
)

card_axis.axis(
    "off"
)

card_axis.text(
    0.02,
    0.92,
    "传感器状态",
    fontsize=13,
    fontweight="bold",
    transform=card_axis.transAxes
)


sensor_card_text = card_axis.text(
    0.03,
    0.72,
    "",
    fontsize=10.5,
    verticalalignment="top",
    transform=card_axis.transAxes,
    linespacing=1.6
)


# ============================================================
# 传感器选择
# ============================================================

sensor_axis = figure.add_subplot(
    grid[4:7, 9:12]
)

sensor_axis.set_title(
    "传感器选择",
    fontsize=11,
    pad=8
)

sensor_radio = RadioButtons(
    sensor_axis,
    available_sensors,
    active=available_sensors.index(
        current_sensor
    )
)

for label in sensor_radio.labels:

    label.set_fontsize(9)


# ============================================================
# 控制区域
# ============================================================

control_axis = figure.add_subplot(
    grid[7:12, 9:12]
)

control_axis.axis(
    "off"
)


# ============================================================
# 按钮
# ============================================================

pause_axis = figure.add_axes(
    [
        0.755,
        0.285,
        0.18,
        0.045
    ]
)

pause_button = Button(
    pause_axis,
    "暂停刷新"
)


clear_axis = figure.add_axes(
    [
        0.755,
        0.225,
        0.18,
        0.045
    ]
)

clear_button = Button(
    clear_axis,
    "清空曲线"
)


export_axis = figure.add_axes(
    [
        0.755,
        0.165,
        0.18,
        0.045
    ]
)

export_button = Button(
    export_axis,
    "导出 CSV"
)


# ============================================================
# 底部信息
# ============================================================

statistics_text = figure.text(
    0.055,
    0.025,
    "平均值：--    标准差：--    异常点：0",
    fontsize=10
)


api_text = figure.text(
    0.70,
    0.025,
    "API：● 连接中",
    fontsize=10
)


# ============================================================
# 表格对象
# ============================================================

data_table = None


# ============================================================
# 创建表格
# ============================================================

def rebuild_table():

    global data_table

    table_axis.clear()

    table_axis.axis(
        "off"
    )

    table_axis.set_title(
        "实时数据 / Live Data",
        fontsize=12,
        fontweight="bold",
        loc="left",
        pad=8
    )

    buffer = sensor_buffers[
        current_sensor
    ]

    timestamps = list(
        buffer["timestamps"]
    )

    raw_values = list(
        buffer["raw"]
    )

    filtered_values = list(
        buffer["filtered"]
    )

    rows = []

    count = len(raw_values)

    start_index = max(
        0,
        count - TABLE_ROWS
    )

    for i in range(
        start_index,
        count
    ):

        timestamp = (
            datetime.fromtimestamp(
                timestamps[i]
            ).strftime(
                "%H:%M:%S"
            )
        )

        rows.append(
            [
                i + 1,
                timestamp,
                f"{raw_values[i]:.4f}",
                f"{filtered_values[i]:.4f}",
                buffer["unit"]
            ]
        )

    if not rows:

        rows = [
            [
                "--",
                "--",
                "--",
                "--",
                "--"
            ]
        ]

    data_table = table_axis.table(
        cellText=rows,
        colLabels=[
            "序号",
            "时间",
            "原始值",
            "滤波值",
            "单位"
        ],
        cellLoc="center",
        colLoc="center",
        bbox=[
            0,
            0.02,
            1,
            0.82
        ]
    )

    data_table.auto_set_font_size(
        False
    )

    data_table.set_fontsize(
        9
    )

    for cell in data_table.get_celld().values():

        cell.set_height(
            0.12
        )


# ============================================================
# 传感器切换
# ============================================================

def change_sensor(label):

    global current_sensor

    current_sensor = label

    print(
        f"切换传感器：{current_sensor}"
    )

    update_ui()


sensor_radio.on_clicked(
    change_sensor
)


# ============================================================
# 暂停 / 继续
# ============================================================

def toggle_pause(event):

    global running

    running = not running

    if running:

        pause_button.label.set_text(
            "暂停刷新"
        )

        sensor_buffers[
            current_sensor
        ]["status"] = \
            "正在追赶数据..."

        print(
            "实时刷新：继续"
        )

    else:

        pause_button.label.set_text(
            "继续刷新"
        )

        sensor_buffers[
            current_sensor
        ]["status"] = \
            "已暂停"

        print(
            "实时刷新：暂停"
        )

    update_ui()

    figure.canvas.draw_idle()


pause_button.on_clicked(
    toggle_pause
)


# ============================================================
# 清空数据
# ============================================================

def clear_data(event):

    buffer = sensor_buffers[
        current_sensor
    ]

    buffer[
        "timestamps"
    ].clear()

    buffer[
        "raw"
    ].clear()

    buffer[
        "filtered"
    ].clear()

    buffer[
        "all_raw"
    ].clear()

    buffer[
        "all_filtered"
    ].clear()

    buffer[
        "filter_buffer"
    ].clear()

    buffer[
        "last_timestamp"
    ] = None

    buffer[
        "last_value"
    ] = 0.0

    buffer[
        "last_filtered"
    ] = 0.0

    buffer[
        "rate"
    ] = 0.0

    buffer[
        "anomaly_count"
    ] = 0

    buffer[
        "sample_count"
    ] = 0

    buffer[
        "status"
    ] = "等待数据"

    raw_line.set_data(
        [],
        []
    )

    filtered_line.set_data(
        [],
        []
    )

    axis.relim()

    axis.autoscale_view()

    print(
        f"已清空 {current_sensor} 数据"
    )

    rebuild_table()

    update_ui()

    figure.canvas.draw_idle()


clear_button.on_clicked(
    clear_data
)


# ============================================================
# CSV 导出
# ============================================================

def export_csv(event):

    buffer = sensor_buffers[
        current_sensor
    ]

    timestamps = list(
        buffer["timestamps"]
    )

    raw = list(
        buffer["raw"]
    )

    filtered = list(
        buffer["filtered"]
    )

    if not raw:

        print(
            "没有数据可以导出。"
        )

        return

    filename = (
        f"{current_sensor}_"
        f"{datetime.now():%Y%m%d_%H%M%S}.csv"
    )

    filepath = os.path.abspath(
        filename
    )

    try:

        with open(
            filepath,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow(
                [
                    "Timestamp",
                    "Sensor",
                    "Raw",
                    "Filtered",
                    "Unit"
                ]
            )

            for i in range(
                len(raw)
            ):

                timestamp_string = \
                    datetime.fromtimestamp(
                        timestamps[i]
                    ).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                writer.writerow(
                    [
                        timestamp_string,
                        current_sensor,
                        f"{raw[i]:.6f}",
                        f"{filtered[i]:.6f}",
                        buffer["unit"]
                    ]
                )

        print()
        print("=" * 60)
        print("CSV 导出成功")
        print(filepath)
        print("=" * 60)

    except Exception as error:

        print(
            "CSV 导出失败：",
            error
        )


export_button.on_clicked(
    export_csv
)


# ============================================================
# 处理数据
# ============================================================

def process_data(
    buffer,
    timestamp_string,
    value
):

    try:

        timestamp = datetime.strptime(
            timestamp_string,
            "%Y-%m-%d %H:%M:%S"
        ).timestamp()

    except Exception:

        timestamp = time.time()


    # ========================================================
    # 重复数据
    # ========================================================

    if (
        buffer["last_timestamp"]
        ==
        timestamp_string
    ):

        return False


    # ========================================================
    # Hampel
    # ========================================================

    anomaly = hampel_is_anomaly(
        buffer["all_raw"],
        value
    )


    if anomaly:

        buffer[
            "status"
        ] = "异常 / ANOMALY"

        buffer[
            "anomaly_count"
        ] += 1

    else:

        buffer[
            "status"
        ] = "正常 / OK"


    # ========================================================
    # 移动平均
    # ========================================================

    if not anomaly:

        buffer[
            "filter_buffer"
        ].append(
            value
        )


    if buffer[
        "filter_buffer"
    ]:

        filtered_value = (
            sum(
                buffer[
                    "filter_buffer"
                ]
            )
            /
            len(
                buffer[
                    "filter_buffer"
                ]
            )
        )

    else:

        filtered_value = value


    # ========================================================
    # 采样率
    # ========================================================

    if buffer["timestamps"]:

        dt = (
            timestamp
            -
            buffer["timestamps"][-1]
        )

        if dt > 0:

            buffer["rate"] = \
                1.0 / dt


    # ========================================================
    # 保存
    # ========================================================

    buffer[
        "timestamps"
    ].append(
        timestamp
    )

    buffer[
        "raw"
    ].append(
        value
    )

    buffer[
        "filtered"
    ].append(
        filtered_value
    )

    buffer[
        "all_raw"
    ].append(
        value
    )

    buffer[
        "all_filtered"
    ].append(
        filtered_value
    )

    buffer[
        "last_timestamp"
    ] = timestamp_string

    buffer[
        "last_value"
    ] = value

    buffer[
        "last_filtered"
    ] = filtered_value

    buffer[
        "sample_count"
    ] += 1

    buffer[
        "unit"
    ] = "mm"


    return True


# ============================================================
# 获取数据
# ============================================================

def update_data():

    global api_connected

    buffer = sensor_buffers[
        current_sensor
    ]

    try:

        result = get_sensor_data(
            current_sensor
        )

        api_connected = True

        buffer[
            "connected"
        ] = True

        data = result.get(
            "data",
            []
        )

        if not data:

            buffer[
                "status"
            ] = "暂无数据"

            return


        # ====================================================
        # 关键：
        # 不只读取最后一条
        #
        # 这样暂停后继续时，
        # 可以把暂停期间产生的数据全部追赶回来
        # ====================================================

        new_count = 0

        for item in data:

            timestamp_string = \
                item.get(
                    "timestamp"
                )

            value = item.get(
                "value"
            )

            if (
                timestamp_string is None
                or value is None
            ):

                continue

            try:

                value = float(
                    value
                )

            except Exception:

                continue


            # ------------------------------------------------
            # 如果已经存在，跳过
            # ------------------------------------------------

            if (
                timestamp_string
                ==
                buffer[
                    "last_timestamp"
                ]
            ):

                continue


            # ------------------------------------------------
            # 只追赶 last_timestamp 之后的数据
            # ------------------------------------------------

            if buffer[
                "last_timestamp"
            ] is not None:

                if (
                    timestamp_string
                    <=
                    buffer[
                        "last_timestamp"
                    ]
                ):

                    continue


            if process_data(
                buffer,
                timestamp_string,
                value
            ):

                new_count += 1


        if new_count > 0:

            print(
                f"[{current_sensor}] "
                f"更新 {new_count} 条数据"
            )

        elif buffer[
            "status"
        ] != "已暂停":

            buffer[
                "status"
            ] = "等待新数据"


    except requests.exceptions.RequestException:

        api_connected = False

        buffer[
            "connected"
        ] = False

        buffer[
            "status"
        ] = "API 连接失败"


    except Exception as error:

        print(
            "数据更新错误：",
            error
        )


# ============================================================
# UI 更新
# ============================================================

def update_ui():

    buffer = sensor_buffers[
        current_sensor
    ]


    # ========================================================
    # 曲线
    # ========================================================

    if buffer["timestamps"]:

        first_time = \
            buffer["timestamps"][0]

        x = [
            t - first_time
            for t in buffer["timestamps"]
        ]

        raw_line.set_data(
            x,
            list(buffer["raw"])
        )

        filtered_line.set_data(
            x,
            list(buffer["filtered"])
        )

        axis.relim()

        axis.autoscale_view()

    else:

        raw_line.set_data(
            [],
            []
        )

        filtered_line.set_data(
            [],
            []
        )


    # ========================================================
    # 状态卡片
    # ========================================================

    connection_status = (
        "● 在线"
        if buffer["connected"]
        else
        "● 离线"
    )

    card_text = (
        f"传感器\n"
        f"{current_sensor}\n\n"
        f"连接状态\n"
        f"{connection_status}\n\n"
        f"当前值\n"
        f"{buffer['last_value']:.3f} "
        f"{buffer['unit']}\n\n"
        f"滤波值\n"
        f"{buffer['last_filtered']:.3f} "
        f"{buffer['unit']}\n\n"
        f"采样率\n"
        f"{buffer['rate']:.2f} Hz\n\n"
        f"数据点\n"
        f"{len(buffer['raw'])}\n\n"
        f"状态\n"
        f"{buffer['status']}"
    )

    sensor_card_text.set_text(
        card_text
    )


    # ========================================================
    # API
    # ========================================================

    if api_connected:

        api_text.set_text(
            "API：● 已连接"
        )

    else:

        api_text.set_text(
            "API：● 连接失败"
        )


    # ========================================================
    # 统计
    # ========================================================

    if len(
        buffer["all_raw"]
    ) > 1:

        mean_value = statistics.mean(
            buffer["all_raw"]
        )

        std_value = statistics.stdev(
            buffer["all_raw"]
        )

        statistics_text.set_text(
            f"平均值："
            f"{mean_value:.3f} "
            f"{buffer['unit']}"
            f"    "
            f"标准差："
            f"{std_value:.4f} "
            f"{buffer['unit']}"
            f"    "
            f"异常点："
            f"{buffer['anomaly_count']}"
        )

    else:

        statistics_text.set_text(
            "平均值：--    "
            "标准差：--    "
            f"异常点："
            f"{buffer['anomaly_count']}"
        )


    # ========================================================
    # 表格
    # ========================================================

    rebuild_table()


# ============================================================
# 动画
# ============================================================

def animation_update(frame):

    if running:

        update_data()

        update_ui()

    return (
        raw_line,
        filtered_line
    )


animation = FuncAnimation(
    figure,
    animation_update,
    interval=REFRESH_INTERVAL,
    blit=False,
    cache_frame_data=False
)


# ============================================================
# 初始化表格
# ============================================================

rebuild_table()

update_ui()


# ============================================================
# 启动
# ============================================================

print()
print("=" * 65)
print("实时监控已启动")
print("=" * 65)

print()
print("功能：")
print("  ● 多传感器选择")
print("  ● 实时曲线")
print("  ● 实时数据表格")
print("  ● 传感器状态卡片")
print("  ● 暂停 / 继续")
print("  ● 暂停后自动追赶数据")
print("  ● 清空曲线")
print("  ● CSV 导出")
print("  ● Hampel 异常检测")
print("  ● 移动平均滤波")
print()
print("关闭窗口即可退出。")
print()


# ============================================================
# 显示
#
# 不调用：
# focus()
# lift()
# topmost
#
# 因此不会强制窗口保持置顶
# ============================================================

plt.show(
    block=True
)


# ============================================================
# 退出
# ============================================================

session.close()

print()
print("=" * 65)
print(
    "Dynamic Measurement Analyzer 已退出"
)
print("=" * 65)