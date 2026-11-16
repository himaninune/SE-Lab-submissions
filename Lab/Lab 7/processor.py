import math


def validate_height_and_fastpass(rider_spec):
    if not isinstance(rider_spec, str):
        return "Invalid input: rider spec must be text"
    parts = rider_spec.strip().split(':')
    if len(parts) != 2:
        return "Invalid input: use Height:FastPass (e.g. 140:YES)"
    height_str = parts[0].strip()
    pass_str = parts[1].strip().upper()
    if not (height_str.isascii() and height_str.isdigit()) or len(height_str) > 4:
        return "Invalid input: height must be a whole number in cm"
    height = int(height_str)
    if height < 50 or height > 250:
        return "Invalid input: height must be between 50 and 250 cm"
    pass_map = {"YES": True, "NO": False}
    if pass_str not in pass_map:
        return "Invalid input: FastPass must be YES or NO"
    has_fastpass = pass_map[pass_str]
    eligible = height >= 120
    status = "FastPass Priority" if has_fastpass else "Standard Entry"
    return f"Height {height}cm: {'Approved' if eligible else 'Denied'} ({status})"


def compute_dispatch_throughput(ride_metric_str):
    if not isinstance(ride_metric_str, str):
        return "Invalid input: metric must be text"
    parts = ride_metric_str.split('/')
    if len(parts) != 2:
        return "Invalid input: use riders/mins (e.g. 48/2.5)"
    try:
        riders = float(parts[0])
        cycle_mins = float(parts[1])
    except (ValueError, OverflowError):
        return "Invalid input: riders and mins must be numbers"
    if not (math.isfinite(riders) and math.isfinite(cycle_mins)):
        return "Invalid input: riders and mins must be finite numbers"
    if riders < 0:
        return "Invalid input: riders cannot be negative"
    if cycle_mins <= 0:
        return "Invalid input: cycle time must be greater than 0"
    rate = riders / cycle_mins
    if not math.isfinite(rate):
        return "Invalid input: values too large"
    return round(rate, 2)


def resolve_safety_restraint_code(zone_code):
    if not isinstance(zone_code, str):
        return "Invalid input: zone code must be text"
    prefix = zone_code.strip().upper()[:3]
    restraint_types = {
        "CST": "Over-the-Shoulder Harness",
        "WTR": "Lap Bar and Seatbelt",
        "DRP": "Hydraulic Shoulder Vest",
        "WHL": "Manual Safety Bar"
    }
    if prefix not in restraint_types:
        return "Invalid input: unknown zone code"
    return restraint_types[prefix]


def main():
    print("==== Running validate_height_and_fastpass ====")
    r_input = input("Enter rider spec (Height:FastPass, e.g. 140:YES): ")
    print(validate_height_and_fastpass(r_input))

    print("\n==== Running compute_dispatch_throughput ====")
    t_input = input("Enter riders/mins (e.g. 48/2.5): ")
    print("Throughput (riders/min):", compute_dispatch_throughput(t_input))

    print("\n==== Running resolve_safety_restraint_code ====")
    z_input = input("Enter ride zone code (e.g. CST_01, WTR_A): ")
    print("Restraint:", resolve_safety_restraint_code(z_input))


if __name__ == "__main__":
    main()
