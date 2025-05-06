from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
# For production, set via environment variable
app.secret_key = os.environ.get("SECRET_KEY", "change_this_secret_key")

# Simple in-memory user (for demo purposes only)
USER = {
    "username": "Justice4Julia",
    "password_hash": generate_password_hash("password123")
}

# --- Project storage ---
PROJECTS = []  # In-memory list of projects (dicts with 'name' and 'created_by')

# --- Planner Events Storage ---
PLANNER_EVENTS = []  # Each event: {"id": int, "title": str, "date": str, "created_by": str}

# --- Inventory Storage ---
INVENTORY = []  # Each item: {"id": int, "name": str, "quantity": int, "price": float}

def login_required(view):
    """Decorator to ensure a user is logged in."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USER["username"] and check_password_hash(USER["password_hash"], password):
            session["username"] = username
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password", "danger")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session["username"])

@app.route("/logout")
@login_required
def logout():
    session.pop("username", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

@app.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    if request.method == "POST":
        if "delete" in request.form:
            # Deletion request
            idx = int(request.form.get("delete"))
            if 0 <= idx < len(PROJECTS):
                deleted = PROJECTS.pop(idx)
                flash(f"Deleted project '{deleted['name']}'", "info")
            else:
                flash("Invalid project index.", "danger")
            return redirect(url_for("projects"))
        else:
            # New project creation
            project_name = request.form.get("project_name", "").strip()
            if project_name:
                PROJECTS.append({
                    "name": project_name,
                    "created_by": session["username"]
                })
                flash(f"Project '{project_name}' created!", "success")
            else:
                flash("Project name cannot be empty.", "danger")
            return redirect(url_for("projects"))
    return render_template("projects.html", username=session["username"], projects=PROJECTS)

@app.route("/planner", methods=["GET", "POST"])
@login_required
def planner():
    from datetime import datetime
    if request.method == "POST":
        if "delete_event" in request.form:
            event_id = int(request.form.get("delete_event"))
            idx = next((i for i, e in enumerate(PLANNER_EVENTS) if e["id"] == event_id), None)
            if idx is not None:
                deleted = PLANNER_EVENTS.pop(idx)
                flash(f"Deleted event '{deleted['title']}'", "info")
            else:
                flash("Event not found.", "danger")
            return redirect(url_for("planner"))
        else:
            # Add new event
            title = request.form.get("title", "").strip()
            date = request.form.get("date", "").strip()
            if title and date:
                event_id = (PLANNER_EVENTS[-1]["id"] + 1) if PLANNER_EVENTS else 1
                PLANNER_EVENTS.append({
                    "id": event_id,
                    "title": title,
                    "date": date,
                    "created_by": session["username"]
                })
                flash(f"Event '{title}' added!", "success")
            else:
                flash("Event title and date required.", "danger")
            return redirect(url_for("planner"))
    # Events sorted by date
    events_sorted = sorted(PLANNER_EVENTS, key=lambda e: e["date"])
    return render_template("planner.html", username=session["username"], events=events_sorted)

@app.route("/inventory", methods=["GET", "POST"])
@login_required
def inventory():
    if request.method == "POST":
        if "add_item" in request.form:
            name = request.form.get("item_name", "").strip()
            price = request.form.get("item_price", "").strip()
            if name and price:
                try:
                    price = float(price)
                except ValueError:
                    flash("Price must be a number.", "danger")
                    return redirect(url_for("inventory"))
                item_id = (INVENTORY[-1]["id"] + 1) if INVENTORY else 1
                INVENTORY.append({
                    "id": item_id,
                    "name": name,
                    "quantity": 1,
                    "price": price
                })
                flash(f"Item '{name}' added!", "success")
            else:
                flash("Item name and price required.", "danger")
            return redirect(url_for("inventory"))
        elif "delete_item" in request.form:
            item_id = int(request.form.get("delete_item"))
            idx = next((i for i, item in enumerate(INVENTORY) if item["id"] == item_id), None)
            if idx is not None:
                deleted = INVENTORY.pop(idx)
                flash(f"Deleted item '{deleted['name']}'", "info")
            else:
                flash("Item not found.", "danger")
            return redirect(url_for("inventory"))
        elif "inc_item" in request.form:
            item_id = int(request.form.get("inc_item"))
            item = next((item for item in INVENTORY if item["id"] == item_id), None)
            if item:
                item["quantity"] += 1
                flash(f"Increased quantity of '{item['name']}'", "success")
            else:
                flash("Item not found.", "danger")
            return redirect(url_for("inventory"))
    total_value = sum(item["quantity"] * item["price"] for item in INVENTORY)
    return render_template("inventory.html", username=session["username"], inventory=INVENTORY, total_value=total_value)

@app.route("/contact")
@login_required
def contact():
    # Redirect user to the Streamlit contact page
    return redirect("http://localhost:8505")

if __name__ == "__main__":
    app.run(debug=True, port=5000)