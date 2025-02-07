import re
import math
from collections import defaultdict
from typing import List, TypedDict

from app.services.analyze_service import AttributeExplanation


class ConsolidatedAttribute(TypedDict):
    attribute: str
    explanation: str
    mean: float
    count: int
    relevance_score: float

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

# Example usage
if __name__ == "__main__":
    # Sample data
    data = [
        {"attribute": "1. Growth", "explanation": "Explanation 1", "evaluation": {"label": "high", "percentage": "85%"}},
        {"attribute": "2. Harmony", "explanation": "Explanation 2", "evaluation": {"label": "medium", "percentage": "75%"}},
        {"attribute": "3. Life", "explanation": "Explanation 3", "evaluation": {"label": "high", "percentage": "80%"}},
        {"attribute": "4. Nature", "explanation": "Explanation 4", "evaluation": {"label": "high", "percentage": "90%"}},
        {"attribute": "5. Connection", "explanation": "Explanation 5", "evaluation": {"label": "medium", "percentage": "70%"}},
        {"attribute": "1. Growth", "explanation": "Explanation 1", "evaluation": {"label": "high", "percentage": "90%."}},
        {"attribute": "2. Nature", "explanation": "Explanation 4", "evaluation": {"label": "high", "percentage": "85%."}},
        {"attribute": "3. Sustainability", "explanation": "Explanation 6", "evaluation": {"label": "high", "percentage": "95%."}},
        {"attribute": "4. Mindfulness", "explanation": "Explanation 7", "evaluation": {"label": "medium", "percentage": "75%."}},
        {"attribute": "5. Community", "explanation": "Explanation 8", "evaluation": {"label": "medium", "percentage": "70%."}},
        {"attribute": "1. Growth", "explanation": "Explanation 1", "evaluation": {"label": "high", "percentage": "90%."}},
        {"attribute": "2. Authenticity", "explanation": "Explanation 9", "evaluation": {"label": "high", "percentage": "85%."}},
        {"attribute": "3. Adventure", "explanation": "Explanation 10", "evaluation": {"label": "medium", "percentage": "70%."}},
        {"attribute": "4. Connection", "explanation": "Explanation 5", "evaluation": {"label": "high", "percentage": "80%."}},
        {"attribute": "5. Truth", "explanation": "Explanation 11", "evaluation": {"label": "high", "percentage": "85%."}},
        {"attribute": "6. Stability", "explanation": "Explanation 12", "evaluation": {"label": "medium", "percentage": "65%."}},
    ]

    result = consolidate_values(data)
    print(result)