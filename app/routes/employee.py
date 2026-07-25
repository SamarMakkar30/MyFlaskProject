import csv
import io
import re
from flask import Blueprint, Response, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy import asc, desc, or_
from sqlalchemy.exc import IntegrityError
from app.models import db
from app.models.department import Department
from app.models.employee import Employee

employee_bp = Blueprint("employee", __name__)
SORTABLE_COLUMNS = {"name": Employee.name, "email": Employee.email, "department": Department.name, "salary": Employee.salary}
ALLOWED_PER_PAGE = (5, 10, 25)
DEFAULT_PER_PAGE = 10

def _ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"

def _get_list_filters():
    f = {"search_query": request.args.get("q", "", type=str).strip(), "department_filter": request.args.get("department", "", type=str).strip(), "min_salary_raw": request.args.get("min_salary", "", type=str).strip(), "max_salary_raw": request.args.get("max_salary", "", type=str).strip()}
    try:
        f["min_salary"] = float(f["min_salary_raw"]) if f["min_salary_raw"] else None
        f["max_salary"] = float(f["max_salary_raw"]) if f["max_salary_raw"] else None
    except ValueError:
        f["min_salary"] = f["max_salary"] = None
        f["filter_error"] = "Salary filters must be valid numbers."
    if (f.get("min_salary") is not None and f["min_salary"] < 0) or (f.get("max_salary") is not None and f["max_salary"] < 0):
        f["filter_error"] = "Salary filters cannot be negative."
    if f.get("min_salary") is not None and f.get("max_salary") is not None and f["min_salary"] > f["max_salary"]:
        f["filter_error"] = "Minimum salary must be less than or equal to maximum salary."
    f["sort_by"] = request.args.get("sort_by", "name") if request.args.get("sort_by", "name") in SORTABLE_COLUMNS else "name"
    f["order"] = request.args.get("order", "asc") if request.args.get("order", "asc") in ("asc", "desc") else "asc"
    f["page"] = max(request.args.get("page", 1, type=int), 1)
    per_page = request.args.get("per_page", DEFAULT_PER_PAGE, type=int)
    f["per_page"] = per_page if per_page in ALLOWED_PER_PAGE else DEFAULT_PER_PAGE
    return f

def _query(filters):
    query = Employee.query.join(Department)
    if filters["search_query"]:
        pattern = f"%{filters['search_query']}%"
        query = query.filter(or_(Employee.name.ilike(pattern), Employee.email.ilike(pattern), Department.name.ilike(pattern)))
    if filters["department_filter"]:
        query = query.filter(Department.name == filters["department_filter"])
    if filters.get("min_salary") is not None:
        query = query.filter(Employee.salary >= filters["min_salary"])
    if filters.get("max_salary") is not None:
        query = query.filter(Employee.salary <= filters["max_salary"])
    column = SORTABLE_COLUMNS[filters["sort_by"]]
    return query.order_by(desc(column) if filters["order"] == "desc" else asc(column), Employee.id.asc())

def _form_values():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    department = request.form.get("department", "").strip()
    raw_salary = request.form.get("salary", "").strip()
    password = request.form.get("password", "")
    errors = []
    if not name: errors.append("Name is required.")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email): errors.append("Enter a valid email address.")
    if not department: errors.append("Department is required.")
    try: salary = float(raw_salary)
    except (TypeError, ValueError): salary = None
    if salary is None or salary <= 0: errors.append("Salary must be a positive number.")
    return name, email, department, salary, password, errors

def _departments():
    return Department.query.order_by(Department.name).all()

@employee_bp.get("/employee/list")
def employee_list():
    filters = _get_list_filters()
    pagination = _query(filters).paginate(page=filters["page"], per_page=filters["per_page"], error_out=False)
    persisted = {key: filters[key] for key in ("search_query", "department_filter", "min_salary_raw", "max_salary_raw") if filters[key]}
    def sort_url(column):
        order = "desc" if filters["sort_by"] == column and filters["order"] == "asc" else "asc"
        return url_for("employee.employee_list", sort_by=column, order=order, page=1, per_page=filters["per_page"], **persisted)
    def page_url(number, per_page=None):
        return url_for("employee.employee_list", page=number, sort_by=filters["sort_by"], order=filters["order"], per_page=per_page or filters["per_page"], **persisted)
    return render_template("employee.html", employees=pagination.items, pagination=pagination, departments=_departments(), search_query=filters["search_query"], department_filter=filters["department_filter"], min_salary=filters["min_salary_raw"], max_salary=filters["max_salary_raw"], sort_by=filters["sort_by"], order=filters["order"], per_page=filters["per_page"], allowed_per_page=ALLOWED_PER_PAGE, sort_url=sort_url, page_url=page_url, filter_error=filters.get("filter_error"))

@employee_bp.get("/employee/export.csv")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Email", "Department", "Salary"])
    for employee in _query(_get_list_filters()).all():
        writer.writerow([employee.name, employee.email, employee.department.name, f"{employee.salary:.2f}"])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=orbithr-employees.csv"})

@employee_bp.get("/employeeDepartment")
def gotodept(): return redirect(url_for("department.departmentHome"))

@employee_bp.get("/employee/register")
def register_employee(): return render_template("add_employee.html", departments=_departments())

@employee_bp.route("/employee/add", methods=["POST", "GET"])
def employeeAdd():
    if request.method == "GET": return redirect(url_for("employee.register_employee"))
    name, email, department_name, salary, password, errors = _form_values()
    if not password: errors.append("Password is required.")
    department = Department.query.filter_by(name=department_name).first() or Department(name=department_name)
    if errors: return render_template("add_employee.html", errors=errors, departments=_departments()), 400
    employee = Employee(name=name, email=email, salary=salary, department=department)
    employee.set_password(password)
    db.session.add(employee)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return render_template("add_employee.html", errors=["An employee with that email already exists."], departments=_departments()), 400
    flash(f"Employee '{employee.name}' was added successfully.", "success")
    if _ajax(): return jsonify(ok=True, message=f"Employee {employee.name} was added.")
    return redirect(url_for("employee.employee_list"))

@employee_bp.get("/employee/employeeDetail/<int:id>")
def employeeDetail(id): return render_template("employee_detail.html", employee=Employee.query.get_or_404(id))

@employee_bp.route("/employee/employeeUpdate/<int:id>", methods=["POST", "GET"])
def employeeUpdate(id):
    employee = Employee.query.get_or_404(id)
    if request.method == "GET": return render_template("update_employee.html", employee=employee, departments=_departments())
    name, email, department_name, salary, password, errors = _form_values()
    if errors: return render_template("update_employee.html", employee=employee, errors=errors, departments=_departments()), 400
    employee.name, employee.email, employee.salary = name, email, salary
    employee.department = Department.query.filter_by(name=department_name).first() or Department(name=department_name)
    if password: employee.set_password(password)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return render_template("update_employee.html", employee=employee, errors=["An employee with that email already exists."], departments=_departments()), 400
    flash(f"Employee '{employee.name}' was updated successfully.", "success")
    if _ajax(): return jsonify(ok=True, message=f"Employee {employee.name} was updated.")
    return redirect(url_for("employee.employee_list"))

@employee_bp.post("/employee/employeeDelete/<int:id>")
def employeeDelete(id):
    employee = Employee.query.get_or_404(id)
    name = employee.name
    db.session.delete(employee)
    db.session.commit()
    flash(f"Employee '{name}' was deleted successfully.", "success")
    if _ajax(): return jsonify(ok=True, message=f"Employee {name} was deleted.")
    return redirect(url_for("employee.employee_list"))

@employee_bp.post("/employee/bulk-delete")
def bulk_delete():
    ids = [int(value) for value in request.form.getlist("employee_ids") if value.isdigit()]
    count = Employee.query.filter(Employee.id.in_(ids)).delete(synchronize_session=False) if ids else 0
    db.session.commit()
    flash(f"Deleted {count} employee(s).", "success")
    return redirect(url_for("employee.employee_list"))

@employee_bp.get("/employee/search.json")
def employee_search():
    term = request.args.get("q", "", type=str).strip()
    if not term: return jsonify([])
    pattern = f"%{term}%"
    matches = Employee.query.join(Department).filter(or_(Employee.name.ilike(pattern), Employee.email.ilike(pattern), Department.name.ilike(pattern))).order_by(Employee.name).limit(8).all()
    return jsonify([{"name": e.name, "department": e.department.name, "url": url_for("employee.employeeDetail", id=e.id)} for e in matches])
