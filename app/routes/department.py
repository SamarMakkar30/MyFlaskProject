from flask import Blueprint,render_template

department_bp = Blueprint("department", __name__)

@department_bp.route("/department")
def departmentHome():
    return render_template("department.html")