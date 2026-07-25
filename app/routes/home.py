from flask import Blueprint, render_template
from sqlalchemy import desc, func
from app.models import db
from app.models.employee import Employee
from app.models.department import Department
home_bp = Blueprint("home", __name__)
@home_bp.route("/home")
def home():
    total_employees = Employee.query.count(); total_departments = Department.query.count()
    average_salary = db.session.query(func.coalesce(func.avg(Employee.salary),0)).scalar() or 0
    highest = db.session.query(Department.name, func.avg(Employee.salary).label("average_salary")).join(Employee).group_by(Department.id).order_by(desc("average_salary")).first()
    by_department = db.session.query(Department.name, func.count(Employee.id), func.coalesce(func.avg(Employee.salary),0)).outerjoin(Employee).group_by(Department.id).order_by(Department.name).all()
    recent = Employee.query.order_by(Employee.id.desc()).limit(5).all()
    salaries = [float(x.salary) for x in Employee.query.order_by(Employee.id).all()]
    return render_template("home.html", total_employees=total_employees, total_departments=total_departments, average_salary=float(average_salary), highest_paid_department=highest, by_department=by_department, salary_distribution=salaries, recent_employees=recent)
