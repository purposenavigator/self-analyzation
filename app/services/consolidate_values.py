import re
import math
from collections import defaultdict
from typing import List
from app.type import ConsolidatedAttribute, AttributeExplanation


def consolidate_values(data: List[AttributeExplanation]) -> List[ConsolidatedAttribute]:
    """
    Consolidates values by calculating mean percentage and relevance score for each attribute.

    Args:
        data (list): List of dictionaries containing attribute data.

    Returns:
        list: Sorted list of attributes with mean percentage and relevance score.
    """
    # Normalize percentage values (remove '%', convert to float)
    for entry in data:
        entry["evaluation"]["percentage"] = float(re.sub(r"[^0-9.]", "", entry["evaluation"]["percentage"]))

    # Group by attribute to calculate mean percentage and count occurrences
    grouped_data = defaultdict(lambda: {"total": 0, "count": 0})

    for entry in data:
        attribute = entry["attribute"]
        grouped_data[attribute]["total"] += entry["evaluation"]["percentage"]
        grouped_data[attribute]["count"] += 1

    # Compute mean percentage and relevance score
    results: List[ConsolidatedAttribute] = []

    for attribute, values in grouped_data.items():
        mean_percentage = values["total"] / values["count"]
        relevance_score = mean_percentage * (1 + math.log(values["count"] + 1))
        results.append({
            "attribute": attribute,
            "explanation": next(entry["explanation"] for entry in data if entry["attribute"] == attribute),
            "mean": mean_percentage,
            "count": values["count"],
            "relevance_score": relevance_score
        })

    # Sort results by relevance score in descending order
    sorted_results = sorted(results, key=lambda x: x["relevance_score"], reverse=True)

    return sorted_results
