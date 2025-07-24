import json
import re
import sys
from pathlib import Path

def format_benchmark_row(bench):
    # Convert seconds to microseconds (us)
    min_us = bench["stats"]["min"] * 1e6
    max_us = bench["stats"]["max"] * 1e6
    mean_us = bench["stats"]["mean"] * 1e6
    stddev_us = bench["stats"]["stddev"] * 1e6
    median_us = bench["stats"]["median"] * 1e6
    iqr_us = bench["stats"]["iqr"] * 1e6

    # OPS in original is per second; convert to Kops/s (thousands/s)
    ops_kops = bench["stats"]["ops"] / 1000.0

    outliers = bench["stats"].get("outliers", "")
    rounds = bench["stats"]["rounds"]
    iterations = 1  # Assume 1 since your original string has 1 iteration

    name = bench["name"].replace("test_", "").capitalize().replace("_", " ")

    # Format as Markdown table row
    row = (
        f"| {name:<23} | "
        f"{min_us:9.4f} | "
        f"{max_us:10.4f} | "
        f"{mean_us:10.4f} | "
        f"{stddev_us:9.4f} | "
        f"{median_us:10.4f} | "
        f"{iqr_us:9.4f} | "
        f"{outliers:<9} | "
        f"{ops_kops:12.4f} | "
        f"{rounds:6} | "
        f"{iterations:10} |"
    )
    return row

def update_readme(readme_path, new_content, start_marker, end_marker):
    text = Path(readme_path).read_text(encoding="utf-8")

    pattern = re.compile(
        rf"({re.escape(start_marker)})(.*)({re.escape(end_marker)})",
        flags=re.DOTALL,
    )

    replacement = f"{start_marker}\n\n{new_content}\n\n{end_marker}"
    new_text, count = pattern.subn(replacement, text)

    if count == 0:
        print("ERROR: Markers not found in README file.")
        sys.exit(1)

    if new_text != text:
        Path(readme_path).write_text(new_text, encoding="utf-8")
        print("README.md updated successfully.")
    else:
        print("No changes needed in README.md.")

def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_metrics.py benchmark.json README.md")
        sys.exit(1)

    benchmark_file = Path(sys.argv[1])
    readme_file = Path(sys.argv[2])

    if not benchmark_file.exists():
        print(f"Benchmark file {benchmark_file} does not exist.")
        sys.exit(1)

    if not readme_file.exists():
        print(f"README file {readme_file} does not exist.")
        sys.exit(1)

    # Load benchmark data JSON
    data = json.loads(benchmark_file.read_text(encoding="utf-8"))

    # Extract benchmarks list; for example take first benchmark only
    benchmarks = data.get("benchmarks", [])
    if not benchmarks:
        print("No benchmarks found in the JSON data.")
        sys.exit(1)

   # Prepare Markdown table content
    header = (
        "| Name (time in us)        |    Min    |     Max    |    Mean    |  StdDev   |   Median   |    IQR    | Outliers  | OPS (Kops/s) | Rounds | Iterations |"
    )
    separator = (
        "|------------------------- |-----------|------------|------------|-----------|------------|-----------|-----------|--------------|--------|------------|"
    )

    # Format every benchmark entry into a row, then join all rows
    rows = [format_benchmark_row(bench) for bench in benchmarks]

    legend = """
    **Legend:**


    - **Outliers:** 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.  
    - **OPS:** Operations Per Second, computed as 1 / Mean (displayed in Kops/s = thousands of operations per second)
    """

    full_content = "\n".join([header, separator] + rows + [legend])

    # Define markers in README.md
    START_MARKER = "<!-- PERFORMANCE_METRICS_START -->"
    END_MARKER = "<!-- PERFORMANCE_METRICS_END -->"

    # Update README.md with new benchmarks table
    update_readme(readme_file, full_content, START_MARKER, END_MARKER)


if __name__ == "__main__":
    main()
