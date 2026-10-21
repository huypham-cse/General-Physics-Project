import argparse
import csv
import json
import math
from pathlib import Path
import sys

from physics_model import simulate_ejection, tail_position


ROOT = Path(__file__).resolve().parent


def read_config(path):
    with path.open(encoding="utf-8-sig") as file:
        config = json.load(file)

    if not isinstance(config, dict):
        raise ValueError("Input phai la mot doi tuong JSON")

    fields = {
        "launch": ["average_gun_force", "rail_angle_deg", "rail_length",
                   "tail_offset", "tail_top_height", "clearance_margin"],
        "seat": ["total_mass", "drag_coefficient", "frontal_area_A"],
        "aircraft": ["speed", "initial_altitude"],
        "constants": ["gravity", "air_density"],
        "simulation": ["max_time", "time_step"],
        "parachute": ["drag_coefficient", "area", "max_deceleration",
                      "deployment_altitude"],
    }
    for section, names in fields.items():
        if not isinstance(config.get(section), dict):
            raise ValueError(f"Thieu nhom input: {section}")
        for name in names:
            value = config[section].get(name)
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or value < 0):
                raise ValueError(f"{section}.{name} phai la so huu han khong am")

    positive_fields = {
        "launch": ["rail_length", "tail_offset"],
        "seat": ["total_mass"],
        "constants": ["gravity"],
        "simulation": ["max_time", "time_step"],
        "parachute": ["drag_coefficient", "area", "max_deceleration"],
    }
    for section, names in positive_fields.items():
        for name in names:
            if config[section][name] <= 0:
                raise ValueError(f"{section}.{name} phai lon hon 0")

    if config["launch"]["rail_angle_deg"] > 180:
        raise ValueError("Goc ray phai nam trong khoang 0 den 180 do")

    config.setdefault("scenario_name", path.stem)
    if not isinstance(config["scenario_name"], str):
        raise ValueError("scenario_name phai la chuoi")
    return config


def make_summary(config, result):
    trajectory = result["trajectory"]
    last = trajectory[-1]
    peak = max(trajectory, key=lambda state: state["pos_y"])
    clearance = result["tail_clearance"]
    deployment = result["parachute_deployment"]

    if deployment is not None:
        end_reason = "parachute_deployed"
    elif last["pos_y"] <= 0:
        end_reason = "ground_reached_without_deployment"
    else:
        end_reason = "max_time_reached"

    if clearance is not None and not clearance["cleared"]:
        status = "not_met"
        conclusion = "CHUA DAT: ghe khong vuot duoi du khoang cach an toan."
    elif clearance is not None and deployment is not None:
        status = "met"
        conclusion = "DAT: thoa dieu kien vuot duoi va bung du theo mo hinh."
    elif end_reason == "ground_reached_without_deployment":
        status = "not_met"
        conclusion = "CHUA DAT: cham dat truoc khi du dieu kien bung du."
    else:
        status = "incomplete"
        conclusion = "CHUA DU KET QUA: chua xac dinh du ca hai dieu kien."

    return {
        "scenario_name": config["scenario_name"],
        "model_status": status,
        "conclusion": conclusion,
        "end_reason": end_reason,
        "method": "Euler",
        "time_step_s": config["simulation"]["time_step"],
        "sample_count": len(trajectory),
        "launch_acceleration_m_s2": result["launch_acceleration"],
        "ejection_speed_m_s": result["ejection_speed"],
        "release_velocity_m_s": list(result["release_velocity"]),
        "max_altitude_m": peak["pos_y"],
        "peak_time_s": peak["time_t"],
        "tail_clearance": clearance,
        "required_margin_m": config["launch"]["clearance_margin"],
        "parachute_deployment": deployment,
        "last_state": last,
        "scope": "Kiem tra 7 phuong trinh trong Word; dung khi bung du. Chua mo phong ha canh duoi du.",
    }


def format_summary(summary):
    vx0, vy0 = summary["release_velocity_m_s"]
    lines = [
        f"Kich ban: {summary['scenario_name']}",
        summary["conclusion"],
        f"Gia toc tren ray: {summary['launch_acceleration_m_s2']:.3f} m/s^2",
        f"Toc do roi ray so voi may bay: {summary['ejection_speed_m_s']:.3f} m/s",
        f"Van toc roi ray (vx, vy): ({vx0:.3f}, {vy0:.3f}) m/s",
        f"Do cao lon nhat da mo phong: {summary['max_altitude_m']:.3f} m",
    ]
    clearance = summary["tail_clearance"]
    if clearance is None:
        lines.append("Vuot duoi: chua tim thay luc duoi bat kip trong doan mo phong.")
    else:
        height = clearance["seat_y"] - clearance["tail_y"]
        label = "DAT" if clearance["cleared"] else "CHUA DAT"
        lines.append(f"Vuot duoi: {label}, t = {clearance['time_t']:.3f} s")
        lines.append(f"Ghe cao hon dinh duoi: {height:.3f} m; can {summary['required_margin_m']:.3f} m")

    deployment = summary["parachute_deployment"]
    if deployment is None:
        lines.append("Bung du: chua du dieu kien trong doan mo phong.")
    else:
        lines.extend([
            f"Bung du: t = {deployment['time_t']:.3f} s, y = {deployment['pos_y']:.3f} m",
            f"Toc do khi bung du: {deployment['speed']:.3f} m/s",
            f"Giam toc du kien khi bung du: {deployment['drag_acceleration']:.3f} m/s^2",
        ])

    reasons = {
        "parachute_deployed": "Du dieu kien bung du",
        "ground_reached_without_deployment": "Cham dat khi chua bung du",
        "max_time_reached": "Het thoi gian mo phong",
    }
    lines.append(f"Dung mo phong: {reasons[summary['end_reason']]}")
    lines.append(summary["scope"])
    return "\n".join(lines) + "\n"


def save_results(config, result, summary, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in [("input.json", config), ("summary.json", summary)]:
        with (output_dir / filename).open("w", encoding="utf-8") as file:
            json.dump(content, file, ensure_ascii=False, indent=2, allow_nan=False)
            file.write("\n")

    (output_dir / "summary.txt").write_text(format_summary(summary), encoding="utf-8")

    columns = ["time_t", "pos_x", "pos_y", "vel_x", "vel_y", "ax", "ay",
               "speed", "tail_x", "tail_y", "horizontal_gap",
               "height_above_tail", "parachute_drag_acceleration"]
    rho = config["constants"]["air_density"]
    parachute = config["parachute"]
    m = config["seat"]["total_mass"]
    launch = config["launch"]
    with (output_dir / "trajectory.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for state in result["trajectory"]:
            x_tail, y_tail = tail_position(
                launch["tail_offset"], launch["tail_top_height"],
                config["aircraft"]["speed"], config["aircraft"]["initial_altitude"],
                state["time_t"],
            )
            speed = math.hypot(state["vel_x"], state["vel_y"])
            row = dict(state)
            row.update({
                "speed": speed,
                "tail_x": x_tail,
                "tail_y": y_tail,
                "horizontal_gap": state["pos_x"] - x_tail,
                "height_above_tail": state["pos_y"] - y_tail,
                "parachute_drag_acceleration": rho * parachute["drag_coefficient"] * parachute["area"] * speed**2 / (2 * m),
            })
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Mo phong ghe phong thoat hiem theo 7 phuong trinh.")
    parser.add_argument("--input", type=Path, default=ROOT / "inputs" / "example.json",
                        help="Duong dan file JSON dau vao")
    parser.add_argument("--output", type=Path, help="Thu muc luu ket qua")
    parser.add_argument("--no-plots", action="store_true", help="Chi xuat du lieu, bo qua bieu do")
    args = parser.parse_args()

    try:
        config = read_config(args.input)
        result = simulate_ejection(config)
        for state in result["trajectory"]:
            if not all(math.isfinite(value) for value in state.values()):
                raise ValueError("Ket qua so khong hop le. Hay giam time_step va kiem tra input.")
        summary = make_summary(config, result)
        output_dir = args.output if args.output is not None else ROOT / "outputs" / args.input.stem
        save_results(config, result, summary, output_dir)
        if not args.no_plots:
            from visualizations.plots import save_plots
            save_plots(config, result, output_dir)
    except ModuleNotFoundError as error:
        print(f"Thieu thu vien: {error.name}. Chay: python -m pip install -r requirements.txt", file=sys.stderr)
        return 1
    except OverflowError:
        print("Loi: gia tri tinh qua lon. Hay giam time_step va kiem tra input.", file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Loi: {error}", file=sys.stderr)
        return 1

    print(format_summary(summary), end="")
    print(f"Ket qua luu tai: {output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
