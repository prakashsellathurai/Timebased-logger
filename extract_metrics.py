import json
import re

def update_readme(json_file, readme_file):
    """Extract metrics from JSON and update README.md."""

    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract metrics (example: average execution time)
    if 'benchmarks' not in data or not data['benchmarks']:
        print("No benchmark data found in JSON file.")
        return

    benchmark_data = data['benchmarks'][0] # assuming only one benchmark
    mean_time = benchmark_data['stats']['mean']
    metric_string = f"Average execution time: {mean_time:.4f} seconds"

    # Read the README content
    with open(readme_file, 'r') as f:
        readme_content = f.read()

    # Find the Metrics section
    metrics_header = "## Performance Metrics"
    if metrics_header not in readme_content:
        print(f"Metrics header '{metrics_header}' not found in README. Creating one.")
        readme_content += f"\n{metrics_header}\n"

    # Regex to find lines after the metrics header until the next header
    pattern = re.compile(rf"{re.escape(metrics_header)}\n(.*?)(?=\n##|\Z)", re.DOTALL)

    match = pattern.search(readme_content)

    if match:
        existing_metrics = match.group(1).strip()  # Existing text after the header
        updated_metrics = f"{metric_string}\n" # Add new metrics.

        # Replace the old section with updated metrics
        updated_readme = pattern.sub(f"{metrics_header}\n{updated_metrics}", readme_content)

    else:
        print("Could not find existing Metrics section, appending new metrics.")
        updated_readme = readme_content + f"\n{metric_string}\n"

    # Write the updated README content back to the file
    with open(readme_file, 'w') as f:
        f.write(updated_readme)