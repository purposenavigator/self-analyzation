import math
from typing import List
from app.type import LabeledAttribute, ConsolidatedAttribute

def add_new_label(data: List[ConsolidatedAttribute]) -> List[LabeledAttribute]:
    """
    Adds a new label to the data based on dynamic thresholds of relevance scores.

    Args:
        data (list): List of dictionaries containing attribute data.

    Returns:
        list: List of dictionaries with added labels.
    """
    # Function to compute percentile
    def percentile(arr, p):
        sorted_arr = sorted(arr)
        index = math.floor((p / 100) * len(sorted_arr))
        return sorted_arr[index]

    # Extract all relevance scores
    relevance_scores = [item["relevance_score"] for item in data]

    # Determine dynamic thresholds
    high_threshold = percentile(relevance_scores, 66)  # Top 33%
    medium_threshold = percentile(relevance_scores, 33)  # Middle 33%

    # Assign a new label based on dynamic thresholds
    classified_data: List[LabeledAttribute] = []
    for item in data:
        if item["relevance_score"] >= high_threshold:
            new_label = "high"
        elif item["relevance_score"] >= medium_threshold:
            new_label = "medium"
        else:
            new_label = "low"

        # Append the new data with updated label
        classified_data.append({**item, "label": new_label})

    # Sort by relevance score in descending order
    sorted_results = sorted(classified_data, key=lambda x: x["relevance_score"], reverse=True)

    return sorted_results
