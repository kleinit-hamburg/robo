#!/usr/bin/env python3
"""Transparent first-pass calculations; never substitutes for Gazebo or hardware data."""
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def calculate(spec, assumptions):
    g = assumptions["gravity_mps2"]
    drive = assumptions["drive"]
    stability = assumptions["stability"]
    tool = assumptions["tool"]
    energy = assumptions["energy"]
    variants = {}
    for key in assumptions["variants"]:
        robot = spec["variants"][key]
        mass = robot["mass_kg"]
        gauge = robot["track"]["gauge_m"]
        width = robot["track"]["belt_width_m"]
        length = robot["track"]["ground_contact_length_m"]
        radius = robot["drive"]["wheel_radius_m"]
        belt_area = 2 * width * length
        grades = []
        for angle in drive["grade_deg"]:
            radians = math.radians(angle)
            normal = mass * g * math.cos(radians)
            force = (mass * g * math.sin(radians)
                     + drive["rolling_resistance_coefficient"] * normal
                     + mass * drive["acceleration_mps2"])
            grades.append({
                "grade_deg": angle,
                "required_force_N": force,
                "torque_per_side_Nm": force * radius / 2,
                "mechanical_power_W": force * drive["design_speed_mps"],
                "traction_limits_N": {
                    str(mu): mu * normal for mu in drive["traction_mu"]
                },
            })
        margins = []
        for offset in stability["lateral_com_offset_m"]:
            lever = (gauge + width) / 2 - offset
            for force in stability["side_force_N"]:
                margins.append({
                    "com_offset_m": offset,
                    "side_force_N": force,
                    "ideal_roll_margin_Nm": mass * g * lever - force * stability["tool_height_m"],
                })
        variants[key] = {
            "mass_kg": mass,
            "gauge_m": gauge,
            "belt_width_m": width,
            "outer_width_m": gauge + width,
            "nominal_clearance_m": robot["clearance"]["nominal_body_bottom_m"],
            "body_link_com_height_m": robot["body"]["com_z_m"],
            "assumed_full_belt_area_m2": belt_area,
            "optimistic_mean_ground_pressure_kPa": mass * g / belt_area / 1000,
            "drive_grades": grades,
            "ideal_static_lateral_margins": margins,
        }

    bore_m = tool["hydraulic_example_bore_mm"] / 1000
    area = math.pi * bore_m**2 / 4
    pressure_Pa = tool["hydraulic_example_pressure_bar"] * 100000
    flow_m3s = area * tool["linear_speed_mps"]
    battery_Wh = (energy["battery_voltage_V"] * energy["battery_capacity_Ah"]
                  * energy["usable_fraction"])
    return {
        "status": assumptions["status"],
        "notes": [
            "Belt area and outer-edge support are optimistic proxies; the current Gazebo model contacts on rollers.",
            "No sinkage, soil shear failure, actuator thermal limits, braking, power peaks, or crop contact included.",
            "Mechanical drive power is not battery power; static lateral margin excludes vertical/tool-arm moments.",
        ],
        "variants": variants,
        "tool_example": {
            "cylinder_area_mm2": area * 1e6,
            "cylinder_force_at_example_pressure_N": pressure_Pa * area * tool["hydraulic_example_cylinder_efficiency"],
            "flow_at_example_speed_Lmin": flow_m3s * 60000,
            "hydraulic_power_at_example_pressure_W": pressure_Pa * flow_m3s,
            "pump_electric_power_at_example_pressure_W": pressure_Pa * flow_m3s / tool["hydraulic_example_pump_motor_efficiency"],
            "force_cases": [
                {
                    "force_N": force,
                    "mechanical_power_W": force * tool["linear_speed_mps"],
                    "electric_direct_example_W": force * tool["linear_speed_mps"] / tool["electric_example_total_efficiency"],
                    "hydraulic_required_pressure_bar": force / (area * tool["hydraulic_example_cylinder_efficiency"]) / 100000,
                    "within_example_pressure": force <= pressure_Pa * area * tool["hydraulic_example_cylinder_efficiency"],
                }
                for force in tool["linear_force_N"]
            ],
        },
        "battery_example": {
            "nominal_Wh": energy["battery_voltage_V"] * energy["battery_capacity_Ah"],
            "usable_Wh": battery_Wh,
            "runtime_h_at_mean_power": {
                str(power): battery_Wh / power
                for power in energy["illustrative_mean_battery_power_W"]
            },
            "mean_power_budget_W_for_target": battery_Wh / energy["mission_target_hours"],
        },
    }


if __name__ == "__main__":
    spec = json.loads((ROOT / "config/robot-spec.json").read_text())
    assumptions = json.loads((ROOT / "config/mechanical-sizing.json").read_text())
    print(json.dumps(calculate(spec, assumptions), indent=2, ensure_ascii=False))
