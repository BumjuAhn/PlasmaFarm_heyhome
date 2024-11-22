import csv
import logging

def load_steps_from_csv(filename):
    """Load steps from a CSV file."""
    steps = []
    try:
        with open(filename, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                steps.append({
                    "description": row["description"],
                    "states": {
                        "power1": row["power1"].strip().lower() == "true",
                        "power2": row["power2"].strip().lower() == "true",
                        "power3": row["power3"].strip().lower() == "true",
                    },
                    "duration": int(row["duration"]),
                })
        logging.info(f"Steps loaded successfully from {filename}")
    except Exception as e:
        logging.error(f"Error reading CSV file {filename}: {e}")
    return steps

def create_cycles_from_steps(steps):
    """Create repeating cycles based on predefined patterns."""
    cycle_patterns = [
        ["Turning ON fog", "Turning OFF fog"],
        ["Turning ON plasma", "Turning OFF plasma"],
        ["Turning ON fog and plasma", "Turning OFF fog and plasma"],
    ]

    cycles = []
    pattern_index = 0

    while len(cycles) < 1000:  # Limit cycle creation to prevent infinite loops
        current_pattern = cycle_patterns[pattern_index]
        current_cycle = [step for step in steps if step["description"] in current_pattern]
        cycles.append(current_cycle)
        pattern_index = (pattern_index + 1) % len(cycle_patterns)

    logging.info("Cycles created successfully.")
    return cycles
