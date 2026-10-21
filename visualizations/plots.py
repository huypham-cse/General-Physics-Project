import math


def save_plots(config, result, output_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    states = result["trajectory"]
    t = [state["time_t"] for state in states]
    x = [state["pos_x"] for state in states]
    y = [state["pos_y"] for state in states]
    vx = [state["vel_x"] for state in states]
    vy = [state["vel_y"] for state in states]
    speed = [math.hypot(state["vel_x"], state["vel_y"]) for state in states]
    ax_values = [state["ax"] for state in states]
    ay_values = [state["ay"] for state in states]
    clearance = result["tail_clearance"]
    deployment = result["parachute_deployment"]
    name = config["scenario_name"]
    launch = config["launch"]
    aircraft = config["aircraft"]
    parachute = config["parachute"]
    rho = config["constants"]["air_density"]
    m = config["seat"]["total_mass"]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x, y, label="Seat trajectory", color="tab:blue")
    ax.scatter(x[0], y[0], label="Rail exit", color="black", zorder=5)
    if clearance is not None:
        for state in states:
            if state["time_t"] == clearance["time_t"]:
                color = "tab:green" if clearance["cleared"] else "tab:red"
                ax.scatter(state["pos_x"], state["pos_y"], color=color,
                           label="Tail clearance check", zorder=5)
                break
    if deployment is not None:
        ax.scatter(deployment["pos_x"], deployment["pos_y"], marker="*",
                   s=150, color="tab:orange", label="Parachute deployment", zorder=6)
    ax.set(xlabel="Horizontal position x (m)", ylabel="Altitude y (m)",
           title=f"Trajectory - {name}")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "trajectory.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    axes[0].plot(t, vx, label="vx")
    axes[0].plot(t, vy, label="vy")
    axes[0].plot(t, speed, label="Speed", linestyle="--", color="black")
    axes[0].set(ylabel="Velocity (m/s)")
    axes[1].plot(t, ax_values, label="ax")
    axes[1].plot(t, ay_values, label="ay")
    axes[1].set(xlabel="Time after rail exit (s)", ylabel="Acceleration (m/s^2)")
    for ax in axes:
        if deployment is not None:
            ax.axvline(deployment["time_t"], color="tab:orange", linestyle=":",
                       label="Deployment")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.suptitle(f"Velocity and acceleration - {name}")
    fig.tight_layout()
    fig.savefig(output_dir / "motion.png", dpi=160)
    plt.close(fig)

    tail_states = states
    if clearance is not None:
        end_time = max(2 * clearance["time_t"], config["simulation"]["time_step"])
        tail_states = [state for state in states if state["time_t"] <= end_time]
    tail_t = [state["time_t"] for state in tail_states]
    gap = [state["pos_x"] - (-launch["tail_offset"] + aircraft["speed"] * state["time_t"])
           for state in tail_states]
    height = [state["pos_y"] - aircraft["initial_altitude"] - launch["tail_top_height"]
              for state in tail_states]

    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    axes[0].plot(tail_t, gap, label="Seat x - tail x")
    axes[0].axhline(0, color="black", linestyle="--", label="Tail catches seat")
    axes[0].set(ylabel="Horizontal gap (m)")
    axes[1].plot(tail_t, height, label="Seat height above tail")
    axes[1].axhline(launch["clearance_margin"], color="tab:red", linestyle="--",
                   label="Required margin")
    axes[1].set(xlabel="Time after rail exit (s)", ylabel="Height above tail (m)")
    for ax in axes:
        if clearance is not None:
            label = "Clearance met" if clearance["cleared"] else "Clearance not met"
            ax.axvline(clearance["time_t"], color="tab:purple", linestyle=":", label=label)
        ax.grid(alpha=0.3)
        ax.legend()
    fig.suptitle(f"Tail clearance - {name}")
    fig.tight_layout()
    fig.savefig(output_dir / "tail_clearance.png", dpi=160)
    plt.close(fig)

    opening_acceleration = [rho * parachute["drag_coefficient"] * parachute["area"] * v**2 / (2 * m)
                            for v in speed]
    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    axes[0].plot(t, y, label="Altitude")
    axes[0].axhline(parachute["deployment_altitude"], color="tab:red", linestyle="--",
                   label="Maximum deployment altitude")
    axes[0].set(ylabel="Altitude (m)")
    axes[1].plot(t, opening_acceleration, label="Predicted opening deceleration")
    axes[1].axhline(parachute["max_deceleration"], color="tab:red", linestyle="--",
                   label="Maximum allowed deceleration")
    axes[1].set(xlabel="Time after rail exit (s)", ylabel="Deceleration (m/s^2)")
    for ax in axes:
        if deployment is not None:
            ax.axvline(deployment["time_t"], color="tab:orange", linestyle=":", label="Deployment")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.suptitle(f"Parachute conditions checked on descent - {name}")
    fig.tight_layout()
    fig.savefig(output_dir / "parachute_conditions.png", dpi=160)
    plt.close(fig)
