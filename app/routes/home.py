from flask import Blueprint, render_template
from sqlalchemy import desc, distinct, func

from app.models import db
from app.models.employee import Employee


home_bp = Blueprint("home", __name__)


@home_bp.route("/home")
def home():
    """Render live dashboard metrics from the existing employee table."""
    total_employees, total_departments, average_salary = db.session.query(
        func.count(Employee.id),
        func.count(distinct(Employee.department)),
        func.coalesce(func.avg(Employee.salary), 0),
    ).one()

    highest_paid_department = (
        db.session.query(
            Employee.department,
            func.avg(Employee.salary).label("average_salary"),
        )
        .group_by(Employee.department)
        .order_by(desc("average_salary"))
        .first()
    )

    return render_template(
        "home.html",
        total_employees=total_employees,
        total_departments=total_departments,
        average_salary=float(average_salary or 0),
        highest_paid_department=highest_paid_department,
    )
