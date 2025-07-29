import json 
import os
import sys
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_and_summarize_results(results_dir):
    """Process Allure results and summarize test statuses in a single iteration."""
    status_counts = {"passed": 0, "failed": 0, "broken": 0, "skipped": 0, "unknown": 0}
    modified_count = 0
    skipped_count = 0
    try:
        for filename in os.listdir(results_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(results_dir, filename)
                try:
                    with open(filepath, "r") as file:
                        data = json.load(file)
                except json.JSONDecodeError:
                    logger.error(f"Skipping invalid JSON file: {filepath}")
                    continue
                except Exception as e:
                    logger.error(f"Error reading file {filepath}: {e}")
                    continue

                # Process and modify results if necessary
                try:
                    modified, new_status = modify_and_update_result(data)
                except Exception as e:
                    logger.error(f"Error processing file {filepath}: {e}")
                    continue

                # Check for missing or empty status
                if not new_status:
                    logger.warning(f"Empty status in file {filepath}")
                    new_status = infer_status_from_steps(data)
                    data["status"] = new_status  # Ensure status is set at the top level

                # Update status count (either modified status or original status)
                if new_status in status_counts:
                    status_counts[new_status] += 1
                else:
                    logger.warning(f"Unknown status '{new_status}' in file {filepath}")
                    status_counts["unknown"] += 1

                # Save modified results back to file if any modification occurred
                if modified:
                    try:
                        with open(filepath, "w") as file:
                            json.dump(data, file, indent=4)
                        modified_count += 1
                    except Exception as e:
                        logger.error(f"Error writing file {filepath}: {e}")
                        continue

                # Count skipped tests with logging
                if new_status == "skipped":
                    reason = data.get("statusDetails", {}).get("message", "No reason provided")
                    logger.info(f"Test skipped due to long execution time: {reason}")
                    skipped_count += 1
        logger.info(f"Modified {modified_count} files with status updates.")
        logger.info(f"Logged {skipped_count} skipped tests.")
        logger.info(
            f"Test Summary: \nPassed={status_counts['passed']}, \nFailed={status_counts['failed']}, "
            f"Broken={status_counts['broken']}, \nSkipped={status_counts['skipped']}, \nUnknown={status_counts['unknown']}"
        )

        # Print summary for Jenkins to parse
        print(json.dumps(status_counts))
    except Exception as e:
        logger.error(f"Unexpected error during processing: {e}")
        sys.exit(1)

def modify_and_update_result(data):
    """Modify the result if applicable and return modified flag and updated status."""
    status = data.get("status", "").lower()
    status_details = data.get("statusDetails", {}).get("message", "")
    # Log the initial status for debugging
    logger.debug(f"Initial status: {status}")

    # If failed but not an AssertionError, mark as broken
    if status == "failed" and "assertionerror" not in status_details.lower():
        data["status"] = "broken"
        data["statusDetails"]["message"] += " [Modified: Changed to broken due to non-assertion error.]"
        inject_custom_label(data, "modified_status", "true")
        logger.debug(f"Modified status to broken for file: {data}")
        return True, "broken"

    # Log the final status for debugging
    logger.debug(f"Final status: {status}")

    # Otherwise, return the original status without modifying
    return False, status

def infer_status_from_steps(data):
    """Infer the status from the steps if the root status is missing."""
    steps = data.get("steps", [])
    inferred_status = "passed"  # Default to passed if no steps indicate failure

    for step in steps:
        step_status = step.get("status", "").lower()
        status_details = step.get("statusDetails", {}).get("message", "")

        if step_status == "failed" and "assertionerror" not in status_details.lower():
            return "broken"
        elif step_status == "failed":
            return "failed"
        elif step_status == "skipped":
            inferred_status = "skipped"

    return inferred_status

def inject_custom_label(data, name, value):
    """Add a custom label to the test result."""
    if "labels" not in data:
        data["labels"] = []
    data["labels"].append({"name": name, "value": value})

def create_allure_categories(results_dir):
    """Create categories.json to group test results in Allure report."""
    categories = [
        {
            "name": "Broken Tests",
            "description": "Tests marked as broken due to unexpected errors.",
            "matchedStatuses": ["broken"],
        },
        {
            "name": "Failed Assertions",
            "description": "Tests that failed due to assertion errors.",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*AssertionError.*",
        },
        {
            "name": "Skipped Tests",
            "description": "Tests that were skipped due to timeouts or other reasons.",
            "matchedStatuses": ["skipped"],
        },
    ]
    categories_file = os.path.join(results_dir, "categories.json")
    try:
        with open(categories_file, "w") as file:
            json.dump(categories, file, indent=4)
        logger.info("Allure categories.json created successfully.")
    except Exception as e:
        logger.error(f"Error creating categories.json: {e}")

if __name__ == "__main__":
    # Argument parser to get path from command line
    parser = argparse.ArgumentParser(
        description="Process and modify Allure results JSON files."
    )
    parser.add_argument(
        "--path", required=True, help="Path to the allure-results directory."
    )
    args = parser.parse_args()
    results_dir = args.path
    # Process, modify, and summarize Allure results in one iteration
    process_and_summarize_results(results_dir)
    # Create categories.json for enhanced Allure categorization
    create_allure_categories(results_dir)
