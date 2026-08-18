import requests
import tkinter as tk

from tkinter import ttk, messagebox

import threading
import queue
import statistics
from datetime import datetime

from collections import deque

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg
)


# ============================================================
# Dynamic Measurement Analyzer
# API Client / GUI v2.0
# ============================================================

API_BASE_URL = "http://127.0.0.1:18080"

DEFAULT_SENSOR = "Measurement"

DEFAULT_REFRESH_INTERVAL = 1000

MAX_DATA_POINTS = 500

TABLE_POINTS = 30


# ============================================================
# API
# ============================================================

def get_sensors():

    url = f"{API_BASE_URL}/sensors"

    response = requests.get(
        url,
        timeout=3
    )

    response.raise_for_status()

    return response.json()


def get_sensor_data(sensor_name):

    url = (
        f"{API_BASE_URL}"
        f"/sensors/"
        f"{sensor_name}"
        f"/data"
    )

    response = requests.get(
        url,
        timeout=3
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# GUI
# ============================================================

class MeasurementAnalyzer:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Dynamic Measurement Analyzer v2.0"
        )

        self.root.geometry(
            "1250x800"
        )

        self.root.minsize(
            1000,
            650
        )

        # ----------------------------------------------------
        # 关键：
        # 不设置 topmost
        # 不调用 focus_force()
        # 不调用 lift()
        # ----------------------------------------------------

        self.root.attributes(
            "-topmost",
            False
        )

        # ----------------------------------------------------
        # 状态
        # ----------------------------------------------------

        self.running = True

        self.refresh_enabled = True

        self.refresh_interval = (
            DEFAULT_REFRESH_INTERVAL
        )

        self.current_sensor = (
            DEFAULT_SENSOR
        )

        self.request_queue = queue.Queue()

        self.data_lock = threading.Lock()

        self.data_timestamps = deque(
            maxlen=MAX_DATA_POINTS
        )

        self.data_values = deque(
            maxlen=MAX_DATA_POINTS
        )

        self.latest_data = []

        self.last_update_time = None

        self.total_requests = 0

        self.success_requests = 0

        self.failed_requests = 0

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self.create_style()

        self.create_header()

        self.create_statistics()

        self.create_chart()

        self.create_table()

        self.create_status_bar()

        # ----------------------------------------------------
        # 初始化传感器
        # ----------------------------------------------------

        self.load_sensors_async()

        # ----------------------------------------------------
        # 定时检查后台线程结果
        # ----------------------------------------------------

        self.root.after(
            100,
            self.process_queue
        )

        # ----------------------------------------------------
        # 自动刷新
        # ----------------------------------------------------

        self.root.after(
            self.refresh_interval,
            self.auto_refresh
        )

        # ----------------------------------------------------
        # 关闭事件
        # ----------------------------------------------------

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )


    # ========================================================
    # Style
    # ========================================================

    def create_style(self):

        style = ttk.Style()

        try:

            style.theme_use(
                "vista"
            )

        except tk.TclError:

            pass

        style.configure(
            "Title.TLabel",
            font=(
                "Segoe UI",
                18,
                "bold"
            )
        )

        style.configure(
            "Subtitle.TLabel",
            font=(
                "Segoe UI",
                9
            )
        )

        style.configure(
            "StatTitle.TLabel",
            font=(
                "Segoe UI",
                9
            )
        )

        style.configure(
            "StatValue.TLabel",
            font=(
                "Segoe UI",
                15,
                "bold"
            )
        )


    # ========================================================
    # Header
    # ========================================================

    def create_header(self):

        header = ttk.Frame(
            self.root,
            padding=15
        )

        header.pack(
            fill=tk.X
        )

        title_frame = ttk.Frame(
            header
        )

        title_frame.pack(
            side=tk.LEFT
        )

        ttk.Label(
            title_frame,
            text="Dynamic Measurement Analyzer",
            style="Title.TLabel"
        ).pack(
            anchor=tk.W
        )

        ttk.Label(
            title_frame,
            text="Real-Time Multi-Sensor Measurement Platform",
            style="Subtitle.TLabel"
        ).pack(
            anchor=tk.W,
            pady=(2, 0)
        )

        control_frame = ttk.Frame(
            header
        )

        control_frame.pack(
            side=tk.RIGHT
        )

        ttk.Label(
            control_frame,
            text="Sensor:"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        self.sensor_combo = ttk.Combobox(
            control_frame,
            width=18,
            state="readonly"
        )

        self.sensor_combo.pack(
            side=tk.LEFT,
            padx=(0, 10)
        )

        self.sensor_combo.bind(
            "<<ComboboxSelected>>",
            self.on_sensor_changed
        )

        self.refresh_button = ttk.Button(
            control_frame,
            text="Refresh",
            command=self.manual_refresh
        )

        self.refresh_button.pack(
            side=tk.LEFT,
            padx=5
        )

        self.auto_refresh_var = tk.BooleanVar(
            value=True
        )

        self.auto_refresh_check = ttk.Checkbutton(
            control_frame,
            text="Auto Refresh",
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh
        )

        self.auto_refresh_check.pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Label(
            control_frame,
            text="Interval:"
        ).pack(
            side=tk.LEFT,
            padx=(10, 5)
        )

        self.interval_combo = ttk.Combobox(
            control_frame,
            width=8,
            state="readonly",
            values=[
                "0.5 s",
                "1 s",
                "2 s",
                "5 s",
                "10 s"
            ]
        )

        self.interval_combo.set(
            "1 s"
        )

        self.interval_combo.pack(
            side=tk.LEFT
        )

        self.interval_combo.bind(
            "<<ComboboxSelected>>",
            self.on_interval_changed
        )


    # ========================================================
    # Statistics
    # ========================================================

    def create_statistics(self):

        frame = ttk.Frame(
            self.root,
            padding=(15, 0, 15, 10)
        )

        frame.pack(
            fill=tk.X
        )

        self.stat_current = self.create_stat_card(
            frame,
            "Current Value"
        )

        self.stat_mean = self.create_stat_card(
            frame,
            "Mean"
        )

        self.stat_std = self.create_stat_card(
            frame,
            "Std Dev"
        )

        self.stat_min = self.create_stat_card(
            frame,
            "Minimum"
        )

        self.stat_max = self.create_stat_card(
            frame,
            "Maximum"
        )

        self.stat_rate = self.create_stat_card(
            frame,
            "Sample Rate"
        )


    def create_stat_card(
        self,
        parent,
        title
    ):

        card = ttk.LabelFrame(
            parent,
            text=title,
            padding=10
        )

        card.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=4
        )

        value_label = ttk.Label(
            card,
            text="--",
            style="StatValue.TLabel"
        )

        value_label.pack(
            anchor=tk.CENTER
        )

        return value_label


    # ========================================================
    # Chart
    # ========================================================

    def create_chart(self):

        chart_frame = ttk.LabelFrame(
            self.root,
            text="Real-Time Measurement",
            padding=5
        )

        chart_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=15,
            pady=(0, 10)
        )

        self.figure = Figure(
            figsize=(10, 4),
            dpi=100
        )

        self.axis = self.figure.add_subplot(
            111
        )

        self.axis.set_xlabel(
            "Time"
        )

        self.axis.set_ylabel(
            "Value"
        )

        self.axis.grid(
            True,
            alpha=0.3
        )

        self.raw_line, = self.axis.plot(
            [],
            [],
            marker="o",
            markersize=3,
            linewidth=1.5,
            label="Measurement"
        )

        self.axis.legend()

        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=chart_frame
        )

        self.canvas_widget = (
            self.canvas.get_tk_widget()
        )

        self.canvas_widget.pack(
            fill=tk.BOTH,
            expand=True
        )


    # ========================================================
    # Table
    # ========================================================

    def create_table(self):

        table_frame = ttk.LabelFrame(
            self.root,
            text="Recent Data",
            padding=5
        )

        table_frame.pack(
            fill=tk.X,
            padx=15,
            pady=(0, 10)
        )

        columns = (
            "sequence",
            "timestamp",
            "value",
            "status"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=6
        )

        self.table.heading(
            "sequence",
            text="SEQ"
        )

        self.table.heading(
            "timestamp",
            text="Timestamp"
        )

        self.table.heading(
            "value",
            text="Value"
        )

        self.table.heading(
            "status",
            text="Status"
        )

        self.table.column(
            "sequence",
            width=80,
            anchor=tk.CENTER
        )

        self.table.column(
            "timestamp",
            width=220,
            anchor=tk.CENTER
        )

        self.table.column(
            "value",
            width=160,
            anchor=tk.CENTER
        )

        self.table.column(
            "status",
            width=120,
            anchor=tk.CENTER
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        self.table.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )


    # ========================================================
    # Status bar
    # ========================================================

    def create_status_bar(self):

        self.status_frame = ttk.Frame(
            self.root,
            padding=(15, 5)
        )

        self.status_frame.pack(
            fill=tk.X
        )

        self.connection_status = ttk.Label(
            self.status_frame,
            text="● Connecting..."
        )

        self.connection_status.pack(
            side=tk.LEFT
        )

        self.api_status = ttk.Label(
            self.status_frame,
            text=f"API: {API_BASE_URL}"
        )

        self.api_status.pack(
            side=tk.RIGHT
        )


    # ========================================================
    # Sensors
    # ========================================================

    def load_sensors_async(self):

        thread = threading.Thread(
            target=self.request_sensors,
            daemon=True
        )

        thread.start()


    def request_sensors(self):

        try:

            result = get_sensors()

            self.request_queue.put(
                (
                    "sensors",
                    result
                )
            )

        except Exception as error:

            self.request_queue.put(
                (
                    "error",
                    error
                )
            )


    # ========================================================
    # Data Request
    # ========================================================

    def request_data_async(self):

        sensor = self.current_sensor

        thread = threading.Thread(
            target=self.request_sensor_data,
            args=(sensor,),
            daemon=True
        )

        thread.start()


    def request_sensor_data(
        self,
        sensor
    ):

        try:

            self.total_requests += 1

            result = get_sensor_data(
                sensor
            )

            self.success_requests += 1

            self.request_queue.put(
                (
                    "data",
                    result
                )
            )

        except Exception as error:

            self.failed_requests += 1

            self.request_queue.put(
                (
                    "data_error",
                    error
                )
            )


    # ========================================================
    # Queue
    # ========================================================

    def process_queue(self):

        try:

            while True:

                message_type, payload = \
                    self.request_queue.get_nowait()

                if message_type == "sensors":

                    self.handle_sensors(
                        payload
                    )

                elif message_type == "data":

                    self.handle_data(
                        payload
                    )

                elif message_type == "error":

                    self.handle_connection_error(
                        payload
                    )

                elif message_type == "data_error":

                    self.handle_data_error(
                        payload
                    )

        except queue.Empty:

            pass

        if self.running:

            self.root.after(
                100,
                self.process_queue
            )


    # ========================================================
    # Handle Sensors
    # ========================================================

    def handle_sensors(
        self,
        result
    ):

        sensors = result.get(
            "sensors",
            []
        )

        if not sensors:

            return

        self.sensor_combo["values"] = sensors

        if self.current_sensor in sensors:

            self.sensor_combo.set(
                self.current_sensor
            )

        else:

            self.current_sensor = sensors[0]

            self.sensor_combo.set(
                self.current_sensor
            )

        self.request_data_async()


    # ========================================================
    # Handle Data
    # ========================================================

    def handle_data(
        self,
        result
    ):

        self.connection_status.configure(
            text="● Connected"
        )

        sensor_name = result.get(
            "sensor",
            self.current_sensor
        )

        data = result.get(
            "data",
            []
        )

        if not isinstance(
            data,
            list
        ):

            return

        if not data:

            return

        # ----------------------------------------------------
        # 保存数据
        # ----------------------------------------------------

        parsed_data = []

        for item in data:

            try:

                timestamp = item.get(
                    "timestamp"
                )

                value = float(
                    item.get(
                        "value"
                    )
                )

                parsed_data.append(
                    {
                        "timestamp": timestamp,
                        "value": value
                    }
                )

            except (
                TypeError,
                ValueError
            ):

                continue

        if not parsed_data:

            return

        # ----------------------------------------------------
        # 只保存当前 API 返回的数据
        # ----------------------------------------------------

        with self.data_lock:

            self.latest_data = parsed_data

            self.data_timestamps.clear()

            self.data_values.clear()

            for item in parsed_data[-MAX_DATA_POINTS:]:

                timestamp = item["timestamp"]

                value = item["value"]

                self.data_timestamps.append(
                    timestamp
                )

                self.data_values.append(
                    value
                )

        # ----------------------------------------------------
        # 更新 UI
        # ----------------------------------------------------

        self.update_statistics(
            parsed_data
        )

        self.update_chart(
            parsed_data
        )

        self.update_table(
            parsed_data
        )

        self.last_update_time = (
            datetime.now()
        )


    # ========================================================
    # Statistics
    # ========================================================

    def update_statistics(
        self,
        data
    ):

        values = []

        for item in data:

            try:

                values.append(
                    float(
                        item["value"]
                    )
                )

            except (
                TypeError,
                ValueError
            ):

                pass

        if not values:

            return

        current = values[-1]

        mean_value = statistics.mean(
            values
        )

        std_value = 0.0

        if len(values) > 1:

            std_value = statistics.stdev(
                values
            )

        min_value = min(
            values
        )

        max_value = max(
            values
        )

        rate = self.calculate_sample_rate(
            data
        )

        self.stat_current.configure(
            text=f"{current:.4f}"
        )

        self.stat_mean.configure(
            text=f"{mean_value:.4f}"
        )

        self.stat_std.configure(
            text=f"{std_value:.4f}"
        )

        self.stat_min.configure(
            text=f"{min_value:.4f}"
        )

        self.stat_max.configure(
            text=f"{max_value:.4f}"
        )

        self.stat_rate.configure(
            text=f"{rate:.2f} Hz"
        )


    # ========================================================
    # Sample Rate
    # ========================================================

    def calculate_sample_rate(
        self,
        data
    ):

        if len(data) < 2:

            return 0.0

        times = []

        for item in data:

            try:

                timestamp = datetime.strptime(
                    item["timestamp"],
                    "%Y-%m-%d %H:%M:%S"
                )

                times.append(
                    timestamp.timestamp()
                )

            except Exception:

                continue

        if len(times) < 2:

            return 0.0

        duration = (
            times[-1]
            -
            times[0]
        )

        if duration <= 0:

            return 0.0

        return (
            len(times) - 1
        ) / duration


    # ========================================================
    # Chart Update
    # ========================================================

    def update_chart(
        self,
        data
    ):

        values = []

        times = []

        for item in data:

            try:

                timestamp = datetime.strptime(
                    item["timestamp"],
                    "%Y-%m-%d %H:%M:%S"
                )

                value = float(
                    item["value"]
                )

                times.append(
                    timestamp
                )

                values.append(
                    value
                )

            except Exception:

                continue

        if not values:

            return

        self.raw_line.set_data(
            times,
            values
        )

        self.axis.relim()

        self.axis.autoscale_view()

        self.axis.set_title(
            f"Real-Time Measurement - "
            f"{self.current_sensor}"
        )

        self.canvas.draw_idle()


    # ========================================================
    # Table Update
    # ========================================================

    def update_table(
        self,
        data
    ):

        for item in self.table.get_children():

            self.table.delete(
                item
            )

        recent_data = data[
            -TABLE_POINTS:
        ]

        start_sequence = (
            len(data)
            -
            len(recent_data)
            +
            1
        )

        for index, item in enumerate(
            recent_data
        ):

            timestamp = item.get(
                "timestamp",
                ""
            )

            value = item.get(
                "value",
                ""
            )

            try:

                value_text = f"{float(value):.6f}"

            except Exception:

                value_text = str(value)

            self.table.insert(
                "",
                tk.END,
                values=(
                    start_sequence + index,
                    timestamp,
                    value_text,
                    "OK"
                )
            )


        # 自动显示最新一条数据
        children = self.table.get_children()

        if children:

            self.table.see(
                children[-1]
            )


    # ========================================================
    # Refresh
    # ========================================================

    def auto_refresh(self):

        if not self.running:

            return

        if self.refresh_enabled:

            self.request_data_async()

        self.root.after(
            self.refresh_interval,
            self.auto_refresh
        )


    def manual_refresh(self):

        self.request_data_async()


    # ========================================================
    # Sensor Changed
    # ========================================================

    def on_sensor_changed(
        self,
        event=None
    ):

        selected = (
            self.sensor_combo.get()
        )

        if not selected:

            return

        self.current_sensor = selected

        with self.data_lock:

            self.data_timestamps.clear()

            self.data_values.clear()

            self.latest_data = []

        self.clear_display()

        self.request_data_async()


    # ========================================================
    # Auto Refresh
    # ========================================================

    def toggle_auto_refresh(self):

        self.refresh_enabled = (
            self.auto_refresh_var.get()
        )


    # ========================================================
    # Interval
    # ========================================================

    def on_interval_changed(
        self,
        event=None
    ):

        value = self.interval_combo.get()

        interval_map = {
            "0.5 s": 500,
            "1 s": 1000,
            "2 s": 2000,
            "5 s": 5000,
            "10 s": 10000
        }

        self.refresh_interval = (
            interval_map.get(
                value,
                1000
            )
        )


    # ========================================================
    # Clear
    # ========================================================

    def clear_display(self):

        self.raw_line.set_data(
            [],
            []
        )

        self.axis.relim()

        self.axis.autoscale_view()

        self.canvas.draw_idle()

        for item in self.table.get_children():

            self.table.delete(
                item
            )

        self.stat_current.configure(
            text="--"
        )

        self.stat_mean.configure(
            text="--"
        )

        self.stat_std.configure(
            text="--"
        )

        self.stat_min.configure(
            text="--"
        )

        self.stat_max.configure(
            text="--"
        )

        self.stat_rate.configure(
            text="--"
        )


    # ========================================================
    # Connection Error
    # ========================================================

    def handle_connection_error(
        self,
        error
    ):

        self.connection_status.configure(
            text="● Offline"
        )


    def handle_data_error(
        self,
        error
    ):

        self.connection_status.configure(
            text="● API Offline"
        )


    # ========================================================
    # Close
    # ========================================================

    def on_close(self):

        self.running = False

        self.refresh_enabled = False

        self.root.destroy()


# ============================================================
# Main
# ============================================================

def main():

    root = tk.Tk()

    app = MeasurementAnalyzer(
        root
    )

    root.mainloop()


if __name__ == "__main__":

    main()