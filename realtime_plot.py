import socket
import matplotlib.pyplot as plt
from collections import deque
import statistics
import time

# =========================
# Hampel异常检测
# =========================

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

# =========================
# 参数
# =========================

HOST = "127.0.0.1"
PORT = 12345

MAX_POINTS = 100

FILTER_WINDOW = 5


# =========================
# 数据
# =========================

sequence_data = deque(
    maxlen=MAX_POINTS
)

time_data = deque(
    maxlen=MAX_POINTS
)

raw_data = deque(
    maxlen=MAX_POINTS
)

filtered_data = deque(
    maxlen=MAX_POINTS
)

filter_buffer = deque(
    maxlen=FILTER_WINDOW
)

all_raw = []

all_filtered = []


# =========================
# TCP Server
# =========================

server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server_socket.bind(
    (HOST, PORT)
)

server_socket.listen(1)

print(
    "Real-Time Measurement Monitor"
)

print(
    f"Filter Window: "
    f"{FILTER_WINDOW}"
)

print(
    "Waiting for measurement server..."
)


connection, address = \
    server_socket.accept()

print(
    "Measurement server connected:",
    address
)


# =========================
# Matplotlib
# =========================

plt.ion()

figure, axis = plt.subplots(
    figsize=(10, 6)
)

raw_line, = axis.plot(
    [],
    [],
    marker="o",
    markersize=3,
    label="Raw"
)

filtered_line, = axis.plot(
    [],
    [],
    linewidth=2,
    label="Filtered"
)

axis.set_xlabel(
    "Time (s)"
)

axis.set_ylabel(
    "Measurement (mm)"
)

axis.set_title(
    "Real-Time Measurement"
)

axis.grid(True)

axis.legend()


# =========================
# TCP缓冲
# =========================

receive_buffer = ""

last_time = None

sample_count = 0

try:

    while True:

        data = connection.recv(
            4096
        )

        if not data:
            break

        receive_buffer += \
            data.decode(
                "utf-8"
            )

        while "\n" in receive_buffer:

            message, receive_buffer = \
                receive_buffer.split(
                    "\n",
                    1
                )

            message = message.strip()

            if not message:
                continue

            # =====================
            # END
            # =====================

            if message == "END":

                print(
                    "\nMeasurement finished."
                )

                raise SystemExit


            # =====================
            # 解析协议
            # =====================

            fields = {}

            parts = message.split(";")

            for part in parts:

                if "=" not in part:
                    continue

                key, value = \
                    part.split(
                        "=",
                        1
                    )

                fields[key] = value


            # =====================
            # 检查字段
            # =====================

            required_fields = [
                "SEQ",
                "TIME",
                "VALUE",
                "UNIT",
                "STATUS"
            ]

            if not all(
                field in fields
                for field in required_fields
            ):

                print(
                    "Invalid packet:",
                    message
                )

                continue


            # =====================
            # 读取数据
            # =====================

            try:

                sequence = int(
                    fields["SEQ"]
                )

                time_ms = float(
                    fields["TIME"]
                )

                value = float(
                    fields["VALUE"]
                )

                unit = fields["UNIT"]

                status = fields["STATUS"]

            except ValueError:

                print(
                    "Invalid numeric data:",
                    message
                )

                continue


            # =========================
            # Hampel异常检测
            # =========================

            is_anomaly = hampel_is_anomaly(
                all_raw,
                value,
                window_size=7,
                threshold=3.0
            )


            # =========================
            # 数据状态
            # =========================

            if is_anomaly:

                status = "ANOMALY"

                print(
                    f"⚠ HAMPEL ANOMALY | "
                    f"SEQ={sequence} | "
                    f"VALUE={value:.4f} {unit}"
                )

            else:

                status = "OK"


            # =====================
            # 保存数据
            # =====================

            time_seconds = (
                time_ms / 1000.0
            )

            sequence_data.append(
                sequence
            )

            time_data.append(
                time_seconds
            )

            raw_data.append(
                value
            )

            all_raw.append(
                value
            )


            # =====================
            # 移动平均
            # =====================

            if not is_anomaly:

                filter_buffer.append(
                    value
                )


            if len(filter_buffer) > 0:

                filtered_value = (
                    sum(filter_buffer)
                    /
                    len(filter_buffer)
                )

            else:

                filtered_value = value


            filtered_data.append(
                filtered_value
            )

            all_filtered.append(
                filtered_value
            )

            # =====================
            # 采样率
            # =====================

            sampling_rate = 0.0

            if last_time is not None:

                dt = (
                    time_ms -
                    last_time
                )

                if dt > 0:

                    sampling_rate = (
                        1000.0 / dt
                    )

            last_time = time_ms

            sample_count += 1


            # =====================
            # 统计
            # =====================

            raw_std = 0.0

            filtered_std = 0.0

            if len(all_raw) > 1:

                raw_std = \
                    statistics.stdev(
                        all_raw
                    )

            if len(all_filtered) > 1:

                filtered_std = \
                    statistics.stdev(
                        all_filtered
                    )


            # =====================
            # 控制台
            # =====================

            if is_anomaly:
                display_status = "⚠ ANOMALY"

            else:
                display_status = "OK"


            print(
                f"SEQ={sequence:03d} | "
                f"T={time_seconds:7.3f}s | "
                f"VALUE={value:8.4f} "
                f"{unit} | "
                f"STATUS={display_status} | "
                f"Rate={sampling_rate:5.1f}Hz"
            )


            # =====================
            # 更新曲线
            # =====================

            raw_line.set_data(
                list(time_data),
                list(raw_data)
            )

            filtered_line.set_data(
                list(time_data),
                list(filtered_data)
            )

            axis.relim()

            axis.autoscale_view()

            figure.canvas.draw()

            figure.canvas.flush_events()

            plt.pause(
                0.001
            )


finally:

    connection.close()

    server_socket.close()

    plt.ioff()

    plt.show()


    # =========================
    # 最终统计
    # =========================

    print()

    print(
        "================================"
    )

    print(
        "Measurement Summary"
    )

    print(
        "================================"
    )

    print(
        f"Samples       : "
        f"{sample_count}"
    )

    if len(all_raw) > 1:

        print(
            f"Mean          : "
            f"{statistics.mean(all_raw):.6f} "
            f"{unit}"
        )

        print(
            f"Raw Std       : "
            f"{statistics.stdev(all_raw):.6f} "
            f"{unit}"
        )

    if len(all_filtered) > 1:

        print(
            f"Filtered Std  : "
            f"{statistics.stdev(all_filtered):.6f} "
            f"{unit}"
        )

    if len(time_data) >= 2:

        duration = (
            time_data[-1]
            -
            time_data[0]
        )

        if duration > 0:

            average_rate = (
                sample_count - 1
            ) / duration

            print(
                f"Average Rate  : "
                f"{average_rate:.2f} Hz"
            )

    print(
        "================================"
    )