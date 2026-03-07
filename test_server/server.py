"""
AutoTestAI Test Server v2
=========================
Single login form with 2 fields: username + password.

INTENTIONAL BUGS (for black-box test detection):
-------------------------------------------------
  BUG-1 [BVA off-by-one]  : FIXED — server now correctly enforces len >= 6,
                             matching the HTML minlength=6.

  BUG-2 [ECP reserved val]: Username "admin" is always rejected, even when it
                             meets all other constraints.

  BUG-3 [ECP hidden rule] : Any username containing a digit (0-9) is rejected,
                             but there is no hint of this rule in the HTML or
                             labels. Tests using numeric usernames like
                             "user1" or "TestUser1" will unexpectedly fail.

Valid credentials for passing tests:
  username : 3-15 chars, letters only (no digits), not "admin"
  password : 6-30 chars (BUG-1 fixed: server min now matches HTML minlength=6)

Run:
    python test_server/server.py
    open http://localhost:5001
"""

from flask import Flask, request

app = Flask(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# HTML helper
# ──────────────────────────────────────────────────────────────────────────────

def _page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    body    {{ font-family: Arial, sans-serif; max-width: 460px;
               margin: 60px auto; padding: 0 20px; }}
    h1      {{ color: #2c3e50; }}
    form    {{ background: #f9f9f9; border: 1px solid #ddd;
               padding: 28px; border-radius: 8px; }}
    label   {{ display: block; margin: 14px 0 4px; font-weight: bold;
               font-size: 14px; }}
    input   {{ width: 100%; padding: 9px; box-sizing: border-box;
               border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }}
    button  {{ margin-top: 20px; padding: 11px 30px; background: #27ae60;
               color: #fff; border: none; border-radius: 4px;
               font-size: 15px; cursor: pointer; }}
    button:hover {{ background: #1e8449; }}
    .error   {{ background: #fdecea; color: #c0392b;
                border: 1px solid #e74c3c;
                padding: 10px 14px; border-radius: 4px; margin-bottom: 14px; }}
    .success {{ background: #eafaf1; color: #1e8449;
                border: 1px solid #27ae60;
                padding: 10px 14px; border-radius: 4px; margin-bottom: 14px; }}
    small   {{ color: #888; font-size: 12px; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  {body}
</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    body = """
    <p>Welcome to the AutoTestAI test server (v2).</p>
    <p><a href="/login">Go to Login Form &rarr;</a></p>
    """
    return _page("Test Server v2", body)


@app.route("/login", methods=["GET", "POST"])
def login():
    errors  = []
    success = ""
    vals    = {"username": "", "password": ""}

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        vals = {"username": username, "password": password}

        # ── required ──────────────────────────────────────────────────────
        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")

        # ── username length (3-15) ─────────────────────────────────────
        if username and len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if username and len(username) > 15:
            errors.append("Username cannot exceed 15 characters.")

        # ── password length ────────────────────────────────────────────
        # BUG-1 FIXED: server now enforces >= 6, matching the HTML minlength=6
        if password and len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password and len(password) > 30:
            errors.append("Password cannot exceed 30 characters.")

        # ── BUG-2: reserved username ────────────────────────────────────
        if username.lower() == "admin":
            errors.append("Username 'admin' is not available.")

        # ── BUG-3: digits not allowed in username (undocumented) ────────
        if username and any(ch.isdigit() for ch in username):
            errors.append("Invalid username.")

        # ── reject HTML-dangerous characters (XSS prevention) ────────────
        if username and ("<" in username or ">" in username):
            errors.append("Username must not contain < or > characters.")
        if password and ("<" in password or ">" in password):
            errors.append("Password must not contain < or > characters.")

        if not errors:
            success = f"Login successful! Welcome, {username}."
            vals    = {"username": "", "password": ""}

    # ── render ────────────────────────────────────────────────────────────
    banner = ""
    if errors:
        items  = "".join(f"<li>{e}</li>" for e in errors)
        banner = f'<div class="error"><ul style="margin:0;padding-left:18px">{items}</ul></div>'
    elif success:
        banner = f'<div class="success">{success}</div>'

    body = f"""
    {banner}
    <form method="POST" action="/login" id="loginForm">

      <label for="username">Username <small>(3-15 characters)</small></label>
      <input type="text" id="username" name="username"
             value="{vals['username']}"
             placeholder="e.g. johndoe"
             minlength="3" maxlength="15" required>

      <label for="password">Password <small>(min 6 chars)</small></label>
      <input type="password" id="password" name="password"
             placeholder="@@@@@@"
             minlength="6" maxlength="30" required>

      <button type="submit">Login</button>
    </form>
    """
    return _page("Login", body)


# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Test server v2 -> http://localhost:5001/login")
    app.run(host="0.0.0.0", port=5001, debug=True)

