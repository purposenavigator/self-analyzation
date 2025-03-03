from typing import List
import pytest
import math
from app.services.consolidate_values import consolidate_values, ConsolidatedAttribute
from app.services.analyze_service import AttributeExplanation

def test_consolidate_values():
    data: List[AttributeExplanation] = [
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

    expected_result: List[ConsolidatedAttribute] = [
        {
            "attribute": "1. Growth",
            "explanation": "Explanation 1",
            "mean": 88.33333333333333,
            "count": 3,
            "relevance_score": 210.789335232257
        },
        {
            "attribute": "3. Sustainability",
            "explanation": "Explanation 6",
            "mean": 95.0,
            "count": 1,
            "relevance_score": 160.8489821531948
        },
        {
            "attribute": "4. Nature",
            "explanation": "Explanation 4",
            "mean": 90.0,
            "count": 1,
            "relevance_score": 152.38324625039508
        },
        {
            "attribute": "2. Nature",
            "explanation": "Explanation 4",
            "mean": 85.0,
            "count": 1,
            "relevance_score": 143.91751034759537
        },
        {
            "attribute": "2. Authenticity",
            "explanation": "Explanation 9",
            "mean": 85.0,
            "count": 1,
            "relevance_score": 143.91751034759537
        },
        {
            "attribute": "5. Truth",
            "explanation": "Explanation 11",
            "mean": 85.0,
            "count": 1,
            "relevance_score": 143.91751034759537
        },
        {
            "attribute": "3. Life",
            "explanation": "Explanation 3",
            "mean": 80.0,
            "count": 1,
            "relevance_score": 135.45177444479563
        },
        {
            "attribute": "4. Connection",
            "explanation": "Explanation 5",
            "mean": 80.0,
            "count": 1,
            "relevance_score": 135.45177444479563
        },
        {
            "attribute": "2. Harmony",
            "explanation": "Explanation 2",
            "mean": 75.0,
            "count": 1,
            "relevance_score": 126.98603854199591
        },
        {
            "attribute": "4. Mindfulness",
            "explanation": "Explanation 7",
            "mean": 75.0,
            "count": 1,
            "relevance_score": 126.98603854199591
        },
        {
            "attribute": "5. Connection",
            "explanation": "Explanation 5",
            "mean": 70.0,
            "count": 1,
            "relevance_score": 118.52030263919617
        },
        {
            "attribute": "5. Community",
            "explanation": "Explanation 8",
            "mean": 70.0,
            "count": 1,
            "relevance_score": 118.52030263919617
        },
        {
            "attribute": "3. Adventure",
            "explanation": "Explanation 10",
            "mean": 70.0,
            "count": 1,
            "relevance_score": 118.52030263919617
        },
        {
            "attribute": "6. Stability",
            "explanation": "Explanation 12",
            "mean": 65.0,
            "count": 1,
            "relevance_score": 110.05456673639645
        }
    ]

    result = consolidate_values(data)
    assert len(result) == len(expected_result)
    for res, exp in zip(result, expected_result):
        assert res["attribute"] == exp["attribute"]
        assert res["explanation"] == exp["explanation"]
        assert pytest.approx(res["mean"], 0.01) == exp["mean"]
        assert res["count"] == exp["count"]
        assert pytest.approx(res["relevance_score"], 0.01) == exp["relevance_score"]
