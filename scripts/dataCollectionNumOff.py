import subprocess
import pandas as pd

# Constants
DEFAULT_POP_SIZE = 5
NUM_OFFSPRING = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 40, 50, 60]
NUM_SCENES = 10
NUM_RESULTS = 10
ACTOR_COUNTS = [4, 2, 3]
OUTPUT_STATS_PATH = "examples/basic/_output/_measurementstats.json"
OUTPUT_EXCEL_PATH = "data/town02-scene-data-numoff.xlsx"
COLUMNS = ["Actors", "File Name", "Population Size", "Number of Offsprings", "Time", "Success"]


def run_hp_tuning(pop_size: int, num_offspring: int, scenic_path: str) -> None:
    """Run the hyperparameter tuning bash script with the given parameters."""
    cmd = f"bash runHPTuning.sh {pop_size} {num_offspring} {scenic_path}"
    subprocess.run([cmd, ""], shell=True)


def load_and_save_results(json_output_path: str) -> tuple[pd.Series, pd.Series]:
    """
    Load measurement stats, save to JSON, and return time and satisfaction series.
    
    Returns:
        A tuple of (time_series, con_sat_series).
    """
    df = pd.read_json(OUTPUT_STATS_PATH)
    df.to_json(json_output_path)

    results = df["results"].apply(pd.Series)
    solutions = results["solutions"].apply(pd.Series)
    sol0 = solutions["sol-0"].apply(pd.Series)

    return results["time"], sol0["CON_sat_%"]


def collect_scene_data(
    scene_idx: int,
    num_actors: int,
    pop_size: int,
    num_offspring: int,
) -> list[list]:
    """Run HP tuning for a scene and collect result rows."""
    scene_id = f"{scene_idx}-0"
    scenic_path = f"examples/basic/{num_actors}actors/{scene_id}/d-nsga.scenic"
    json_output_path = f"data/town02-{num_actors}-actor-scene-{scene_id}-numoff-{num_offspring}.json"

    run_hp_tuning(pop_size, num_offspring, scenic_path)
    time_values, sat_values = load_and_save_results(json_output_path)

    return [
        [num_actors, scene_id, pop_size, num_offspring, time_values[i], sat_values[i]]
        for i in range(NUM_RESULTS)
    ]


def append_to_excel(new_data: list[list]) -> None:
    """Append new rows to the Excel output file, creating it if it doesn't exist."""
    new_df = pd.DataFrame(new_data, columns=COLUMNS)

    try:
        existing_df = pd.read_excel(OUTPUT_EXCEL_PATH)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    except FileNotFoundError:
        combined_df = new_df

    combined_df.to_excel(OUTPUT_EXCEL_PATH, index=False)


def main() -> None:
    for scene_idx in range(NUM_SCENES):
        for num_offspring in NUM_OFFSPRING:
            batch_data = []

            for num_actors in ACTOR_COUNTS:
                rows = collect_scene_data(scene_idx, num_actors, DEFAULT_POP_SIZE, num_offspring)
                batch_data.extend(rows)

            append_to_excel(batch_data)


if __name__ == "__main__":
    main()


    

        
    
