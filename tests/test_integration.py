import os
import re
import subprocess
import time
from pathlib import Path

import pytest

#
# Description of the tests
#
# 260827.csv is to test the caching really works (it will failed in timeout if cache is not working)
# 261027.csv is to test the case on domino with same left and right dot cannot satsify the NE constraint
# 261017.csv is to test the input file using ! instead of !=, but the puzzle should also be solved
# 261026.csv will loop forever if the _check_constraint has a bug
#


def get_test_puzzles():
    """Get all test puzzle files and their corresponding expected output files."""
    data_dir = Path(__file__).parent / "integration" / "input"
    output_dir = Path(__file__).parent / "integration" / "output"

    puzzles = []
    for csv_file in data_dir.glob("*.csv"):
        puzzle_name = csv_file.stem
        expected_file = output_dir / f"{puzzle_name}_E.txt"
        if expected_file.exists():
            puzzles.append((str(csv_file), str(expected_file)))
    return puzzles


def normalize_output(output: str) -> str:
    """Normalize output to remove ANSI color codes, cache statistics, and whitespace differences."""
    # Remove ANSI escape codes (colors)
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    output = ansi_escape.sub("", output)

    # Remove cache statistics lines which may vary between runs
    # output = re.sub(r"Cache statistics:.*?\n", "", output, flags=re.DOTALL)
    # output = re.sub(r"  Total function calls:.*?\n", "", output)
    # output = re.sub(r"  Function calls cached:.*?\n", "", output)

    # Normalize newlines and strip extra whitespace
    output = os.linesep.join(
        [line.rstrip() for line in output.splitlines() if line.strip()]
    )

    return output


@pytest.mark.parametrize("csv_path, expected_path", get_test_puzzles())
def test_puzzle_solution(csv_path, expected_path, capsys):
    """Test that each puzzle solves correctly and matches the expected output."""
    # Run solve_pips.py as a subprocess with the given csv file
    project_root = Path(__file__).parent.parent
    start_time = time.perf_counter()

    try:
        # Add timeout to prevent infinite loops - kills process after 2 seconds
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                str(project_root / "solve_pips.py"),
                "-c",
                csv_path,
            ],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=2.0,  # This will raise TimeoutExpired if it takes longer than 2 seconds
        )
    except subprocess.TimeoutExpired as e:
        end_time = time.perf_counter()
        runtime = end_time - start_time
        # Print the runtime even with pytest's capture
        print(f"runtime: {runtime:.2f} seconds")
        pytest.fail(
            f"Puzzle {csv_path} timed out after {runtime:.2f} seconds, which exceeds the 2 second limit and may be an infinite loop"
        )

    end_time = time.perf_counter()
    runtime = end_time - start_time
    # Print the runtime - use capsys to ensure it's visible even if pytest captures output
    with capsys.disabled():
        print(f"\nPuzzle {csv_path} runtime: {runtime:.2f} seconds")

    # Check that the program ran successfully
    assert result.returncode == 0, f"solve_pips.py failed with error: {result.stderr}"

    # Read expected output
    with open(expected_path, "r") as f:
        expected_output = f.read()

    # Normalize both outputs to compare them
    normalized_actual = normalize_output(result.stdout)
    normalized_expected = normalize_output(expected_output)

    # Verify the outputs match
    assert normalized_actual == normalized_expected, (
        f"Output for {csv_path} does not match expected output"
    )
