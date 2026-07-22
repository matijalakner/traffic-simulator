from typing import List
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.gridspec import GridSpec
from .track import Track
from .constants import AnimationConst
from .geometry import position

class Animation(Track):
    """
    Encapsulates traffic simulation data and animation logic.
    """
    def __init__(self, name: str, numc: int, dt: float) -> None:
        super().__init__()
        # Defined constants
        self.dt = dt
        self.t = np.arange(int(AnimationConst.FACTOR / self.dt))
        self.name = name
        self.numc = numc

        # Pre-defined objects
        self.animated_cars: dict = {}
        self.position_history: List[np.ndarray] = []
        self.speed_history: List[np.ndarray] = []
        self.congestion_history: List[np.ndarray] = []
        # Pre-define animation objects
        self.bar_container = None
        self.fig = None
        self.ax = None
        
    def _create_data(self, arr: List[np.ndarray]) -> np.ndarray:
        return np.array(arr).T

    def plot(self):
        """Presents plots for positions and velocities in time"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

        positions_arr = np.array(self.position_history)
        velocities_arr = np.array(self.speed_history)

        for car in range(self.numc):
            ax1.plot(self.t, positions_arr[:,car], linewidth=2, label=f"car:{car + 1}")
            ax2.plot(self.t, velocities_arr[:,car], linewidth=2, label=f"car:{car + 1}")

        # Top plot: Position s(t)
        ax1.set_ylabel("Position s(t) [m]", fontsize=11)
        ax1.set_title("Kinematics: Position and Velocity vs Time", fontsize=14, pad=12)
        ax1.grid(True, linestyle="--", alpha=0.6)
        ax1.axhline(0, color="black", linewidth=0.8, linestyle=":")
        ax1.legend(loc="upper right")

        # Bottom plot: Velocity v(t)
        ax2.set_xlabel("Time t [s]", fontsize=11)
        ax2.set_ylabel("Velocity v(t) [m/s]", fontsize=11)
        ax2.grid(True, linestyle="--", alpha=0.6)
        ax2.axhline(0, color="black", linewidth=0.8, linestyle=":")
        ax2.legend(loc="upper right")

        # 4. Clean layout & show plot
        plt.tight_layout()
        plt.show()
        
        return 0

    def animate_cars(self) -> int:
        """Launches an interactive Matplotlib window showing current traffic flows
        and a live speed vs sector speed histogram with congestion highlighting."""

        history_arr = np.array(self.position_history)
        if history_arr.size == 0:
            print("No history data to animate.")
            return 0

        # 1. Compute car speeds from position differences (handling track wrapping)
        # Delta position per frame
        pos_diffs = np.diff(history_arr, axis=0, prepend=history_arr[:1])
        # Fix potential negative jumps if positions wrap around 0 -> length
        pos_diffs = np.where(pos_diffs < -self.length / 2, pos_diffs + self.length, pos_diffs)
        speed_history = np.abs(pos_diffs)

        # 2. Setup Layout: Track on the left, Histogram on the right
        self.fig = plt.figure(figsize=(13, 6))
        gs = GridSpec(1, 2, width_ratios=[1.1, 1], figure=self.fig)

        self.ax_track = self.fig.add_subplot(gs[0])
        self.ax_hist = self.fig.add_subplot(gs[1])

        # --- Setup Track Plot ---
        self.ax_track.set_aspect('equal')
        self.ax_track.set_xlim(-self.r * 1.2, self.r * 1.2)
        self.ax_track.set_ylim(-self.r * 1.2, self.r * 1.2)
        self.ax_track.set_title("Traffic Flow")

        for line in self.lines_dict.values():
            (start, stop, color) = line
            x = self.r * np.cos(np.linspace(start, stop, 1000) / self.r)
            y = self.r * np.sin(np.linspace(start, stop, 1000) / self.r)
            self.ax_track.plot(x, y, color=color)

        # Pre-compute x, y coordinates for each car across all frames
        self.animated_cars = {}
        for i in range(self.numc):
            car_angles = history_arr[:, i]
            x_cor = self.r * np.cos(car_angles / self.r)
            y_cor = self.r * np.sin(car_angles / self.r)
            scatter = self.ax_track.scatter([x_cor[0]], [y_cor[0]], s=60, edgecolors='black', linewidth=0.5)
            self.animated_cars[i] = (x_cor, y_cor, scatter)

        # --- Setup Speed & Congestion Histogram ---
        self.ax_hist.set_title("Segment Speed vs. Sector Speed Limit")
        self.ax_hist.set_xlabel("Track Position [5m segments]")
        self.ax_hist.set_ylabel("Speed")

        segment_size = 5.0
        bins = np.arange(0, self.length + segment_size, segment_size)
        num_segments = len(bins) - 1

        # Map target sector speeds to 5m bins
        # (Uses getattr fallback if self.segment_speeds or self.segment_positions aren't set)

        seg_idx = position(bins[:-1], self.segment_positions)
        sector_limits = self.segment_speeds[seg_idx]

        # Plot static sector speed target (red dashed line)
        self.ax_hist.step(bins[:-1], sector_limits, where='post', color='crimson',
                          linestyle='--', linewidth=2, label='Sector Limit')

        # Draw initial speed bars
        self.bar_container = self.ax_hist.bar(
            bins[:-1], np.zeros(num_segments), width=segment_size, align='edge',
            color='skyblue', edgecolor='black', alpha=0.8, label='Car Avg Speed'
        )

        max_y_limit = max(1.0, float(np.max(sector_limits)) * 1.25)
        self.ax_hist.set_ylim(0, max_y_limit)
        self.ax_hist.legend(loc='upper right')

        # --- Animation Frame Update ---
        def animate(frame: int):
            idx = frame % len(history_arr)
            artists = []

            # 1. Update Car Positions on Track
            for i in range(self.numc):
                x, y, scatter = self.animated_cars[i]
                scatter.set_offsets([[x[idx], y[idx]]])
                artists.append(scatter)

            # 2. Compute Segment Speeds and Congestion Colors
            current_positions = history_arr[idx] % self.length
            current_speeds = speed_history[idx]

            # Group speed totals and car counts by segment bin
            bin_indices = np.digitize(current_positions, bins[:-1]) - 1
            bin_indices = np.clip(bin_indices, 0, num_segments - 1)

            speed_sums = np.bincount(bin_indices, weights=current_speeds, minlength=num_segments)
            car_counts = np.bincount(bin_indices, minlength=num_segments)

            # Average speed per segment (0 if no cars present)
            avg_segment_speeds = np.divide(speed_sums, np.ones(num_segments),
                                           out=np.zeros(num_segments),
                                           where=car_counts > 0)

            # Update Bar Heights & Congestion Colors
            for seg_i, bar in enumerate(self.bar_container):
                avg_spd = avg_segment_speeds[seg_i]
                target_limit = sector_limits[seg_i]
                count = car_counts[seg_i]

                bar.set_height(avg_spd)

                if count == 0:
                    # Empty segment: standard color
                    bar.set_facecolor('skyblue')
                else:
                    # Ratio of actual speed to the segment's speed limit
                    ratio = avg_spd / max(target_limit, 1e-3)

                    if ratio < 0.35 or avg_spd < 0.5:
                        # Heavy congestion / stopped traffic -> Crimson Red
                        bar.set_facecolor('crimson')
                    elif ratio < 0.70:
                        # Moderate congestion / slowdown -> Orange
                        bar.set_facecolor('orange')
                    else:
                        # Smooth flow -> Sky Blue
                        bar.set_facecolor('skyblue')

                artists.append(bar)

            return artists

        num_frames = len(history_arr)
        ani = animation.FuncAnimation(
            self.fig,
            animate,
            frames=num_frames,
            interval=2,
            blit=True,
        )

        plt.tight_layout()
        plt.show()

        return 0

    def add_position_history(self, positions: np.ndarray) -> None:
        """Append vehicle positioning records to track frames history."""
        self.position_history.append(positions)

    def add_speed_history(self, speeds: np.ndarray) -> None:
        """Append vehicle positioning records to track frames history."""
        self.speed_history.append(speeds)

    def add_congestion_history(self, congestions: np.ndarray) -> None:
        """Append vehicle positioning records to track frames history."""
        self.congestion_history.append(congestions)

