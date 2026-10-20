from flask import Flask, request, jsonify, render_template_string, redirect
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)  # exposes /metrics for Prometheus

tasks = []
next_id = 1

PAGE = """
<!doctype html>
<title>To-Do App</title>
<h1>To-Do App</h1>
<form action="/add" method="post">
  <input name="title" placeholder="New task" required>
  <button>Add</button>
</form>
<ul>
{% for t in tasks %}
  <li>{{ '✔' if t.done else '○' }} {{ t.title }}
    <a href="/done/{{ t.id }}">toggle</a> |
    <a href="/delete/{{ t.id }}">delete</a></li>
{% endfor %}
</ul>
"""


@app.route("/")
def home():
    return render_template_string(PAGE, tasks=tasks)


@app.route("/add", methods=["POST"])
def add_form():
    global next_id
    tasks.append({"id": next_id, "title": request.form["title"], "done": False})
    next_id += 1
    return redirect("/")


@app.route("/done/<int:tid>")
def toggle(tid):
    for t in tasks:
        if t["id"] == tid:
            t["done"] = not t["done"]
    return redirect("/")


@app.route("/delete/<int:tid>")
def delete_form(tid):
    tasks[:] = [t for t in tasks if t["id"] != tid]
    return redirect("/")


# ---- REST API (test with Postman) ----
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def create_task():
    global next_id
    data = request.get_json(silent=True) or {}
    if "title" not in data:
        return jsonify({"error": "title required"}), 400
    task = {"id": next_id, "title": data["title"], "done": False}
    next_id += 1
    tasks.append(task)
    return jsonify(task), 201


@app.route("/api/tasks/<int:tid>", methods=["PUT"])
def update_task(tid):
    data = request.get_json(silent=True) or {}
    for t in tasks:
        if t["id"] == tid:
            t["title"] = data.get("title", t["title"])
            t["done"] = data.get("done", t["done"])
            return jsonify(t)
    return jsonify({"error": "not found"}), 404


@app.route("/api/tasks/<int:tid>", methods=["DELETE"])
def delete_task(tid):
    for t in tasks:
        if t["id"] == tid:
            tasks.remove(t)
            return jsonify({"deleted": tid})
    return jsonify({"error": "not found"}), 404


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)