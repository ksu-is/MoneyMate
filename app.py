from flask import Flask, render_template, request, redirect, url_for, flash
import json
from datetime import datetime
from os.path import exists
import shutil 

app = Flask(__name__)
app.secret_key = "secret_key_for_session_management"  
DATA_FILE = "moneymate_data.json"


data = {"income": [], "expenses": [], "budgets": {}, "savings_goals": {}}
if exists(DATA_FILE):
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
if not exists(DATA_FILE):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)
else:
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
def save_data():
    if exists(DATA_FILE):
        shutil.copy(DATA_FILE, DATA_FILE + ".bak")
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/log_income', methods=["GET", "POST"])
def log_income():
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            description = request.form["description"]
            entry = {"amount": amount, "description": description, "date": datetime.now().isoformat()}
            data["income"].append(entry)
            save_data()
            flash("Income logged successfully.")
        except ValueError as e:
            flash(f"Error: {e}")
        return redirect(url_for('index'))
    return render_template('log_income.html')


@app.route('/log_expense', methods=["GET", "POST"])
def log_expense():
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            category = request.form["category"]
            description = request.form["description"]
            entry = {"amount": amount, "category": category, "description": description, "date": datetime.now().isoformat()}
            data["expenses"].append(entry)
            save_data()
            flash("Expense logged successfully.")
        except ValueError as e:
            flash(f"Error: {e}")
        return redirect(url_for('index'))
    return render_template('log_expense.html')
    
@app.route('/search_expenses', methods=["GET", "POST"])
def search_expenses():
    if request.method == "POST":
        query = request.form["query"].lower()
        results = [e for e in data["expenses"] if query in e["description"].lower()]
        return render_template('search_results.html', results=results, query=query)
    return render_template('search_expenses.html')
    
@app.route('/set_budget', methods=["GET", "POST"])
def set_budget():
    if request.method == "POST":
        category = request.form["category"]
        amount = float(request.form["amount"])
        data["budgets"][category] = amount
        save_data()
        flash(f"Budget set for {category} successfully.")
        return redirect(url_for('index'))
    return render_template('set_budget.html')


@app.route('/set_goal', methods=["GET", "POST"])
def set_goal():
    if request.method == "POST":
        goal_name = request.form["goal_name"]
        target_amount = float(request.form["target_amount"])
        data["savings_goals"][goal_name] = {"target": target_amount, "saved": 0}
        save_data()
        flash(f"Savings goal '{goal_name}' set successfully.")
        return redirect(url_for('index'))
    return render_template('set_goal.html')


@app.route('/summary')
def summary():
    total_income = sum(item["amount"] for item in data["income"])
    total_expenses = sum(item["amount"] for item in data["expenses"])

    category_expenses = {}
    for expense in data["expenses"]:
        category = expense["category"]
        category_expenses[category] = category_expenses.get(category, 0) + expense["amount"]

    categories = list(category_expenses.keys())
    expenses = list(category_expenses.values())

    return render_template(
        'summary.html',
        total_income=total_income,
        total_expenses=total_expenses,
        categories=categories,
        expenses=expenses,
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
