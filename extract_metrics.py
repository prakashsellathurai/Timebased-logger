import json
import re
import os

def extract_metrics(benchmark_file):
    """Extracts mean execution time from a benchmark JSON file."""
    with open(benchmark_file, 'r') as f:
        data = json.load(f)
        if not data or 'benchmarks' not in data or not data['benchmarks']:
            return "No benchmark data found in the file."
        
        benchmark_data = data['benchmarks'][0]  # assuming only one benchmark
        stats = benchmark_data['stats']
        mean_time = stats['mean']
        stddev_time = stats['stddev']
        min_time = stats['min']
        max_time = stats['max']

        metric_string = f"""
| Metric | Value |
|---|---|
| Average execution time | {mean_time:.6f} seconds |
| Standard deviation | {stddev_time:.6f} seconds |
| Minimum execution time | {min_time:.6f} seconds |
| Maximum execution time | {max_time:.6f} seconds |
"""
        
        return f"{metric_string}"

def update_readme(json_file, readme_file):
    """Extract metrics from JSON and update README.md."""
    try:
        metric_string = extract_metrics(json_file)

        # Read the README content
        with open(readme_file, 'r') as f:
            readme_content = f.read()

        # Define the start and end markers for the metrics section
        start_marker = "<!-- PERFORMANCE_METRICS_START -->"
        end_marker = "<!-- PERFORMANCE_METRICS_END -->"

        # Create the regex pattern
        pattern = re.compile(
            re.escape(start_marker) + r"(.*?)" + re.escape(end_marker),
            re.DOTALL
        )

        # Check if the markers exist in the README
        if start_marker not in readme_content or end_marker not in readme_content:
            print(f"Markers '{start_marker}' and '{end_marker}' not found in README.")
            return

        # Create the replacement string
        replacement = f"{start_marker}\n{metric_string}\n{end_marker}"

        # Perform the replacement
        updated_readme = pattern.sub(replacement, readme_content)

        # Write the updated README content back to the file
        with open(readme_file, 'w') as f:
            f.write(updated_readme)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python extract_metrics.py <benchmark_json_file> <readme_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    readme_file = sys.argv[2]

    print(f"Current working directory: {os.getcwd()}")
    print(f"Benchmark file exists: {os.path.exists(json_file)}")
    print(f"Readme file exists: {os.path.exists(readme_file)}")


    update_readme(json_file, readme_file)