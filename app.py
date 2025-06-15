from flask import Flask, request, jsonify
from Components.validator import generate_ideas, extract_idea_names, research_idea_with_agent
from Components.business_plan import generate_problem_statements, generate_solution
from Components.funding_advisor import extract_domain, find_investors, generate_investor_email
from Components.mvp_builder import generate_mvp_plan

app = Flask(__name__)

@app.route("/generate-ideas", methods=["POST"])
def generate_ideas_api():
    data = request.get_json()
    idea = data.get("idea")
    if not idea:
        return jsonify({"error": "Missing idea"}), 400
    refined = generate_ideas(idea)
    names = extract_idea_names(refined)
    return jsonify({"refined": refined, "idea_names": names})

@app.route("/research", methods=["POST"])
def research_api():
    data = request.get_json()
    idea = data.get("idea")
    if not idea:
        return jsonify({"error": "Missing idea"}), 400
    report = research_idea_with_agent(idea)
    return jsonify({"report": report})

@app.route("/problem-statements", methods=["POST"])
def problem_statements_api():
    data = request.get_json()
    report = data.get("report")
    if not report:
        return jsonify({"error": "Missing report"}), 400
    problems = generate_problem_statements(report)
    return jsonify({"problems": problems})

@app.route("/generate-solution", methods=["POST"])
def solution_api():
    data = request.get_json()
    problem = data.get("problem")
    if not problem:
        return jsonify({"error": "Missing problem"}), 400
    solution = generate_solution(problem)
    return jsonify({"solution": solution})

@app.route("/mvp", methods=["POST"])
def mvp_api():
    data = request.get_json()
    name = data.get("startup_name", "My Startup")
    problem = data.get("problem")
    solution = data.get("solution")
    report = data.get("report")
    if not problem or not solution or not report:
        return jsonify({"error": "Missing fields"}), 400
    plan = generate_mvp_plan(name, problem, solution, report)
    return jsonify({"mvp_plan": plan})

@app.route("/investors", methods=["POST"])
def investors_api():
    data = request.get_json()
    idea = data.get("idea")
    if not idea:
        return jsonify({"error": "Missing idea"}), 400
    domain = extract_domain(idea)
    investors = find_investors(idea, domain)
    return jsonify({"domain": domain, "investors": investors})

@app.route("/cold-email", methods=["POST"])
def cold_email_api():
    data = request.get_json()
    idea = data.get("idea")
    investor_name = data.get("investor_name")
    if not idea or not investor_name:
        return jsonify({"error": "Missing data"}), 400
    email = generate_investor_email(idea, investor_name)
    return jsonify({"email": email})

# Required for Vercel
def handler(request, context):
    return app(request, context)

if __name__ == "__main__":
    app.run(debug=True)
