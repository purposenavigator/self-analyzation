from typing import List, Dict
import pytest
from app.services.add_new_label import add_new_label

def test_add_new_label():
    data: List[Dict] = [
        {"attribute": "1. Growth", "explanation": "Explanation 1", "mean": 88.3333, "count": 3, "relevance_score": 210.7893},
        {"attribute": "3. Sustainability", "explanation": "Explanation 6", "mean": 95.0, "count": 1, "relevance_score": 160.849},
        {"attribute": "4. Nature", "explanation": "Explanation 4", "mean": 90.0, "count": 1, "relevance_score": 152.383},
        {"attribute": "2. Nature", "explanation": "Explanation 4", "mean": 85.0, "count": 1, "relevance_score": 143.918},
        {"attribute": "2. Authenticity", "explanation": "Explanation 9", "mean": 85.0, "count": 1, "relevance_score": 143.918},
        {"attribute": "5. Truth", "explanation": "Explanation 11", "mean": 85.0, "count": 1, "relevance_score": 143.918},
        {"attribute": "3. Life", "explanation": "Explanation 3", "mean": 80.0, "count": 1, "relevance_score": 135.452},
        {"attribute": "4. Connection", "explanation": "Explanation 5", "mean": 80.0, "count": 1, "relevance_score": 135.452},
        {"attribute": "2. Harmony", "explanation": "Explanation 2", "mean": 75.0, "count": 1, "relevance_score": 126.986},
        {"attribute": "4. Mindfulness", "explanation": "Explanation 7", "mean": 75.0, "count": 1, "relevance_score": 126.986},
        {"attribute": "5. Connection", "explanation": "Explanation 5", "mean": 70.0, "count": 1, "relevance_score": 118.520},
        {"attribute": "5. Community", "explanation": "Explanation 8", "mean": 70.0, "count": 1, "relevance_score": 118.520},
        {"attribute": "3. Adventure", "explanation": "Explanation 10", "mean": 70.0, "count": 1, "relevance_score": 118.520},
        {"attribute": "6. Stability", "explanation": "Explanation 12", "mean": 65.0, "count": 1, "relevance_score": 110.055}
    ]

    expected_result: List[Dict] = [
{'attribute': '1. Growth', 'explanation': 'Explanation 1', 'mean': 88.3333, 'count': 3, 'relevance_score': 210.7893, 'label': 'high'},
{'attribute': '3. Sustainability', 'explanation': 'Explanation 6', 'mean': 95.0, 'count': 1, 'relevance_score': 160.849, 'label': 'high'},
{'attribute': '4. Nature', 'explanation': 'Explanation 4', 'mean': 90.0, 'count': 1, 'relevance_score': 152.383, 'label': 'high'},
{'attribute': '2. Nature', 'explanation': 'Explanation 4', 'mean': 85.0, 'count': 1, 'relevance_score': 143.918, 'label': 'high'},
{'attribute': '2. Authenticity', 'explanation': 'Explanation 9', 'mean': 85.0, 'count': 1, 'relevance_score': 143.918, 'label': 'high'},
{'attribute': '5. Truth', 'explanation': 'Explanation 11', 'mean': 85.0, 'count': 1, 'relevance_score': 143.918, 'label': 'high'},
{'attribute': '3. Life', 'explanation': 'Explanation 3', 'mean': 80.0, 'count': 1, 'relevance_score': 135.452, 'label': 'medium'},
{'attribute': '4. Connection', 'explanation': 'Explanation 5', 'mean': 80.0, 'count': 1, 'relevance_score': 135.452, 'label': 'medium'},
{'attribute': '2. Harmony', 'explanation': 'Explanation 2', 'mean': 75.0, 'count': 1, 'relevance_score': 126.986, 'label': 'medium'},
{'attribute': '4. Mindfulness', 'explanation': 'Explanation 7', 'mean': 75.0, 'count': 1, 'relevance_score': 126.986, 'label': 'medium'},
{'attribute': '5. Connection', 'explanation': 'Explanation 5', 'mean': 70.0, 'count': 1, 'relevance_score': 118.52, 'label': 'low'},
{'attribute': '5. Community', 'explanation': 'Explanation 8', 'mean': 70.0, 'count': 1, 'relevance_score': 118.52, 'label': 'low'},
{'attribute': '3. Adventure', 'explanation': 'Explanation 10', 'mean': 70.0, 'count': 1, 'relevance_score': 118.52, 'label': 'low'},
{'attribute': '6. Stability', 'explanation': 'Explanation 12', 'mean': 65.0, 'count': 1, 'relevance_score': 110.055, 'label': 'low'}
    ]

    result = add_new_label(data)
    assert len(result) == len(expected_result)
    for res, exp in zip(result, expected_result):
        assert res["attribute"] == exp["attribute"]
        assert res["explanation"] == exp["explanation"]
        assert pytest.approx(res["mean"], 0.01) == exp["mean"]
        assert res["count"] == exp["count"]
        assert pytest.approx(res["relevance_score"], 0.01) == exp["relevance_score"]
        assert res["label"] == exp["label"]
