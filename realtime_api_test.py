import time
import requests
import matplotlib.pyplot as plt


# ============================================================
# 配置
# ============================================================

API_URL = (
    "http://localhost:8080"
    "/sensors/Measurement/data"
)

REFRESH_INTERVAL = 1.0

MAX_POINTS = 100


# ============================================================
# 获取数据
# ============================================================

def get_sensor_data():

    try:

        response = requests.get(
            API_URL,
            timeout=3
        )

        response.raise_for_status()

        result = response.json()

        return result.get(
            "data",
            []
        )

    except requests.RequestException as error:

        print(
            f"[ERROR] API request failed: {error}"
        )

        return []


# ============================================================
# 主程序
# ============================================================

def main():

    print()
    print("=" * 50)
    print("       Real-Time API Monitor")
    print("=" * 50)
    print()

    print(
        f"API: {API_URL}"
    )

    print(
        "Press Ctrl+C to stop."
    )

    print()


    plt.ion()

    figure, axis = plt.subplots(
        figsize=(10, 6)
    )


    while True:

        data = get_sensor_data()


        if not data:

            print(
                "[WARNING] No data."
            )

            time.sleep(
                REFRESH_INTERVAL
            )

            continue


        # ----------------------------------------------------
        # 只保留最近 MAX_POINTS 个点
        # ----------------------------------------------------

        data = data[
            -MAX_POINTS:
        ]


        timestamps = []

        values = []


        for item in data:

            timestamps.append(
                item["timestamp"]
            )

            values.append(
                item["value"]
            )


        # ----------------------------------------------------
        # 清空曲线
        # ----------------------------------------------------

        axis.clear()


        axis.plot(
            range(
                len(values)
            ),
            values,
            marker="o"
        )


        axis.set_title(
            "Real-Time Measurement"
        )

        axis.set_xlabel(
            "Sample"
        )

        axis.set_ylabel(
            "Measurement (mm)"
        )


        axis.grid(
            True
        )


        # ----------------------------------------------------
        # 显示最新数据
        # ----------------------------------------------------

        if values:

            latest_value = values[-1]

            latest_time = timestamps[-1]


            axis.set_title(
                f"Real-Time Measurement | "
                f"{latest_value:.3f} mm | "
                f"{latest_time}"
            )


        figure.tight_layout()

        plt.pause(
            0.01
        )


        time.sleep(
            REFRESH_INTERVAL
        )


if __name__ == "__main__":

    main()