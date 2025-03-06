import pytest
from app.services.analyze_service import get_attribute_and_explanation_object_array

data = "The individual's priorities and values reflect a strong inclination towards personal growth, social connection, and authenticity. Their actions suggest an appreciation for truth and stability in their relationships, as well as a desire for adventure and discovery. This combination indicates a balance between seeking new experiences and valuing deep, meaningful connections with others.\n\n1. Growth - The individual demonstrates a commitment to personal development and improvement, often seeking opportunities for learning and self-discovery - {high: 90%}.\n2. Authenticity - They prioritize being true to themselves and their beliefs, often expressing their thoughts and feelings honestly in social settings - {high: 85%}.\n3. Adventure - They enjoy taking risks and exploring new experiences, showing a preference for novelty and excitement in life - {medium: 70%}.\n4. Connection - Building and maintaining relationships is important to them, as evidenced by their efforts to create deeper bonds with others - {high: 80%}.\n5. Truth - They value honesty and integrity, striving to engage with others in a transparent and genuine manner - {high: 85%}.\n6. Stability - The individual seeks a sense of security in their relationships and personal life, often favoring routines and familiarity - {medium: 65%}."

def test_get_attribute_and_explanation_object_array():
    result = get_attribute_and_explanation_object_array(data)
    
    assert len(result) == 6
    
    assert result[0]["attribute"] == "Growth"
    assert result[0]["explanation"] == "The individual demonstrates a commitment to personal development and improvement, often seeking opportunities for learning and self-discovery"
    assert result[0]["evaluation"]["label"] == "high"
    assert result[0]["evaluation"]["percentage"] == "90%"
    
    assert result[1]["attribute"] == "Authenticity"
    assert result[1]["explanation"] == "They prioritize being true to themselves and their beliefs, often expressing their thoughts and feelings honestly in social settings"
    assert result[1]["evaluation"]["label"] == "high"
    assert result[1]["evaluation"]["percentage"] == "85%"
    
    assert result[2]["attribute"] == "Adventure"
    assert result[2]["explanation"] == "They enjoy taking risks and exploring new experiences, showing a preference for novelty and excitement in life"
    assert result[2]["evaluation"]["label"] == "medium"
    assert result[2]["evaluation"]["percentage"] == "70%"
    
    assert result[3]["attribute"] == "Connection"
    assert result[3]["explanation"] == "Building and maintaining relationships is important to them, as evidenced by their efforts to create deeper bonds with others"
    assert result[3]["evaluation"]["label"] == "high"
    assert result[3]["evaluation"]["percentage"] == "80%"
    
    assert result[4]["attribute"] == "Truth"
    assert result[4]["explanation"] == "They value honesty and integrity, striving to engage with others in a transparent and genuine manner"
    assert result[4]["evaluation"]["label"] == "high"
    assert result[4]["evaluation"]["percentage"] == "85%"
    
    assert result[5]["attribute"] == "Stability"
    assert result[5]["explanation"] == "The individual seeks a sense of security in their relationships and personal life, often favoring routines and familiarity"
    assert result[5]["evaluation"]["label"] == "medium"
    assert result[5]["evaluation"]["percentage"] == "65%"

def test_get_attribute_and_explanation_object_array_empty():
    empty_data = ""
    result = get_attribute_and_explanation_object_array(empty_data)
    
    assert result == []

def test_get_attribute_and_explanation_object_array_invalid_format():
    invalid_data = "This is some random text that does not match the expected format."
    result = get_attribute_and_explanation_object_array(invalid_data)
    
    assert result == []
