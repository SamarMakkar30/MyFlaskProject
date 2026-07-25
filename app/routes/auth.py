from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.models.employee import Employee
auth_bp=Blueprint("auth",__name__)
@auth_bp.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        employee=Employee.query.filter_by(email=request.form.get("email","").strip().lower()).first()
        if employee and employee.check_password(request.form.get("password","")):
            session.clear(); session["user_id"]=employee.id; session["csrf_token"]=__import__("secrets").token_urlsafe(32); next_url=request.args.get("next", ""); return redirect(next_url if next_url.startswith("/") and not next_url.startswith("//") else url_for("home.home"))
        flash("Invalid email or password.","danger")
    return render_template("login.html")
@auth_bp.post("/logout")
def logout():
    session.pop("user_id",None); return redirect(url_for("auth.login"))

