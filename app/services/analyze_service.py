import re
from typing import List, TypedDict

class Evaluation(TypedDict):
    label: str
    percentage: str

class AttributeExplanation(TypedDict):
    attribute: str
    explanation: str
    evaluation: Evaluation

def clean_string(input: str) -> str:
    match = re.match(r'^\d+\.\s*(.*?)$', input)
    return match.group(1) if match else input

def get_attribute_and_explanation_object(
    attribute: str,
    explanation: str,
    label: str,
    percentage: str
) -> AttributeExplanation:
    attribute = clean_string(attribute.strip())
    explanation = explanation.strip()
    label = label.strip()
    percentage = percentage.strip().rstrip('.')
    evaluation: Evaluation = {"label": label, "percentage": percentage}
    return {"attribute": attribute, "explanation": explanation, "evaluation": evaluation}

def get_attribute_and_explanation_object_array(input: str) -> List[AttributeExplanation]:
    """
    Parses the input string and returns a list of objects containing attributes, explanations, and evaluations.

    The input string should follow this pattern:
    - Each attribute and explanation should be on a new line.
    - Each line should start with a number followed by a period and a space.
    - The attribute and explanation should be separated by ' - '.
    - The evaluation should be enclosed in curly braces and separated by a colon.

    Example:
    1. Growth - The individual demonstrates a commitment to personal development and improvement, often seeking opportunities for learning and self-discovery - {high: 90%}
    2. Authenticity - They prioritize being true to themselves and their beliefs, often expressing their thoughts and feelings honestly in social settings - {high: 85%}

    :param input: The input string to parse.
    :return: A list of dictionaries containing attributes, explanations, and evaluations.
    """
    result: List[AttributeExplanation] = []
    for line in input.split('\n'):
        line = line.strip()
        if not line or not re.match(r'^\d+\.', line):
            continue

        parts = [part.strip() for part in line.split(' - ')]
        if len(parts) != 3:
            raise ValueError(f"Invalid input format: {line}")

        attribute, explanation, evaluation_str = parts
        # Remove curly braces and split by colon
        eval_parts = [part.strip() for part in evaluation_str.replace("{", "").replace("}", "").split(':')]
        if len(eval_parts) != 2:
            raise ValueError(f"Invalid evaluation format: {evaluation_str}")

        label, percentage = eval_parts
        result.append(get_attribute_and_explanation_object(attribute, explanation, label, percentage))

    return result
