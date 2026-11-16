"""Scholarship eligibility screener."""
import ast
import json
import logging
import operator

INCOME_LIMIT = 800000
CUTOFF = 85
DEFAULT_FORMULA = "gpa * 10 + credits * 2"
RESULTS_FILE = "scholarships.json"
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def safe_eval(node, variables):
    """Evaluate a parsed arithmetic expression using only allowed nodes."""
    if isinstance(node, ast.Expression):
        return safe_eval(node.body, variables)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.Name) and node.id in variables:
        return variables[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -safe_eval(node.operand, variables)
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        left = safe_eval(node.left, variables)
        right = safe_eval(node.right, variables)
        return OPERATORS[type(node.op)](left, right)
    raise ValueError("unsupported expression")


def calculate_merit_score(gpa, credit_points, formula=DEFAULT_FORMULA):
    """Compute the merit score from gpa and credits using the formula."""
    try:
        tree = ast.parse(formula, mode="eval")
        return safe_eval(tree, {"gpa": gpa, "credits": credit_points})
    except (SyntaxError, ZeroDivisionError) as error:
        raise ValueError(f"invalid formula: {error}") from error


def is_number(value):
    """Return True for real numbers, excluding booleans."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_scores(test_scores):
    """Raise ValueError if the applicant data is missing or out of range."""
    gpa = test_scores.get("gpa")
    credit_points = test_scores.get("credits", 0)
    income = test_scores.get("income")
    if not is_number(gpa) or not 0 <= gpa <= 10:
        raise ValueError("gpa must be a number between 0 and 10")
    if not is_number(credit_points) or credit_points < 0:
        raise ValueError("credits must be a number, 0 or more")
    if not is_number(income) or income < 0:
        raise ValueError("income is required and must be 0 or more")


def evaluate_applicant(student_id, test_scores, results,
                       formula=DEFAULT_FORMULA):
    """Score one applicant, store the result and return eligibility."""
    validate_scores(test_scores)
    score = calculate_merit_score(
        test_scores["gpa"], test_scores.get("credits", 0), formula
    )
    eligible = score >= CUTOFF and test_scores["income"] < INCOME_LIMIT
    results[student_id] = {"score": score, "eligible": eligible}
    logging.info("%s scored %s", student_id, score)
    return eligible


def screen(student_id, test_scores, results, formula=DEFAULT_FORMULA):
    """Evaluate an applicant and report it if the data is rejected."""
    try:
        evaluate_applicant(student_id, test_scores, results, formula)
    except ValueError as error:
        print(f"{student_id} rejected: {error}")


def persist_results(results, file=RESULTS_FILE):
    """Write results to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(results, handle)


def load_results(file=RESULTS_FILE):
    """Read results from a JSON file, or return empty if unavailable."""
    try:
        with open(file, encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def print_shortlist(results):
    """Print every eligible applicant with their score."""
    print("Shortlisted applicants:")
    for student_id, result in results.items():
        if result["eligible"]:
            print(" ", student_id, "score =", result["score"])


def main():
    """Run the screening for the sample applicants."""
    results = {}
    screen("U001", {"gpa": 9.1, "credits": 4, "income": 450000}, results)
    screen("U002", {"gpa": 7.2, "credits": 1, "income": 300000}, results)
    screen("U003", {"gpa": 12.5, "credits": -3, "income": -1}, results)
    screen("U004", {"gpa": 6.5}, results)
    formula = input("Merit formula (Enter to keep default): ")
    if formula:
        try:
            calculate_merit_score(1, 1, formula)
        except ValueError as error:
            print(f"{error}, keeping default formula")
            formula = DEFAULT_FORMULA
    else:
        formula = DEFAULT_FORMULA
    screen("U005", {"gpa": 8.4, "credits": 3, "income": 600000}, results,
           formula)
    persist_results(results)
    print_shortlist(load_results())


if __name__ == "__main__":
    main()
