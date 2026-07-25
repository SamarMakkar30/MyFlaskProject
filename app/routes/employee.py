from flask import Blueprint, request, redirect, url_for, render_template, flash
from sqlalchemy import asc, desc, or_
from sqlalchemy.exc import IntegrityError

from app.models import db
from app.models.employee import Employee

employee_bp = Blueprint("employee", __name__)


# Columns the employee list is allowed to be sorted by.
# Keeping this as an explicit whitelist prevents arbitrary column/SQL injection
# through the `sort_by` query parameter.
SORTABLE_COLUMNS = {
    "name": Employee.name,
    "email": Employee.email,
    "department": Employee.department,
    "salary": Employee.salary,
}

ALLOWED_PER_PAGE = (5, 10)
DEFAULT_PER_PAGE = 10


def _get_list_filters():
    """Read and sanitize all query-string parameters used by the employee list."""

    search_query = request.args.get("q", "", type=str).strip()
    department_filter = request.args.get("department", "", type=str).strip()

    min_salary_raw = request.args.get("min_salary", "", type=str).strip()
    max_salary_raw = request.args.get("max_salary", "", type=str).strip()

    min_salary = float(min_salary_raw) if min_salary_raw else None
    max_salary = float(max_salary_raw) if max_salary_raw else None

    sort_by = request.args.get("sort_by", "name", type=str)
    if sort_by not in SORTABLE_COLUMNS:
        sort_by = "name"

    order = request.args.get("order", "asc", type=str)
    if order not in ("asc", "desc"):
        order = "asc"

    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1

    per_page = request.args.get("per_page", DEFAULT_PER_PAGE, type=int)
    if per_page not in ALLOWED_PER_PAGE:
        per_page = DEFAULT_PER_PAGE

    return {
        "search_query": search_query,
        "department_filter": department_filter,
        "min_salary_raw": min_salary_raw,
        "max_salary_raw": max_salary_raw,
        "min_salary": min_salary,
        "max_salary": max_salary,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "per_page": per_page,
    }


@employee_bp.route("/employee/list")
def employee_list():
    filters = _get_list_filters()

    query = Employee.query

    # --- Searching (name / email / department) ---
    if filters["search_query"]:
        like_pattern = f"%{filters['search_query']}%"
        query = query.filter(
            or_(
                Employee.name.ilike(like_pattern),
                Employee.email.ilike(like_pattern),
                Employee.department.ilike(like_pattern),
            )
        )

    # --- Filtering (department / salary range) ---
    if filters["department_filter"]:
        query = query.filter(Employee.department == filters["department_filter"])

    if filters["min_salary"] is not None:
        query = query.filter(Employee.salary >= filters["min_salary"])

    if filters["max_salary"] is not None:
        query = query.filter(Employee.salary <= filters["max_salary"])

    # --- Sorting ---
    sort_column = SORTABLE_COLUMNS[filters["sort_by"]]
    sort_expression = desc(sort_column) if filters["order"] == "desc" else asc(sort_column)
    query = query.order_by(sort_expression, Employee.id.asc())

    # --- Pagination ---
    pagination = query.paginate(
        page=filters["page"], per_page=filters["per_page"], error_out=False
    )

    # Query params shared by every "keep the current view" link (sort headers,
    # pagination bar, per-page switcher) - built once so nothing gets lost
    # when the user moves between pages.
    persisted_params = {
        "q": filters["search_query"],
        "department": filters["department_filter"],
        "min_salary": filters["min_salary_raw"],
        "max_salary": filters["max_salary_raw"],
    }
    persisted_params = {k: v for k, v in persisted_params.items() if v not in (None, "")}

    def sort_url(column):
        next_order = "desc" if (filters["sort_by"] == column and filters["order"] == "asc") else "asc"
        return url_for(
            "employee.employee_list",
            sort_by=column,
            order=next_order,
            page=1,
            per_page=filters["per_page"],
            **persisted_params,
        )

    def page_url(page_number, per_page=None):
        return url_for(
            "employee.employee_list",
            page=page_number,
            sort_by=filters["sort_by"],
            order=filters["order"],
            per_page=per_page or filters["per_page"],
            **persisted_params,
        )

    departments = [
        row[0]
        for row in db.session.query(Employee.department)
        .distinct()
        .order_by(Employee.department)
        .all()
    ]

    return render_template(
        "employee.html",
        employees=pagination.items,
        pagination=pagination,
        departments=departments,
        search_query=filters["search_query"],
        department_filter=filters["department_filter"],
        min_salary=filters["min_salary_raw"],
        max_salary=filters["max_salary_raw"],
        sort_by=filters["sort_by"],
        order=filters["order"],
        per_page=filters["per_page"],
        allowed_per_page=ALLOWED_PER_PAGE,
        sort_url=sort_url,
        page_url=page_url,
    )


@employee_bp.route("/employeeDepartment")
def gotodept():
    return redirect(url_for("department.departmentHome"))


@employee_bp.route("/employee/register")
def register_employee():
    return render_template("add_employee.html")


@employee_bp.route("/employee/add", methods=["POST", "GET"])
def employeeAdd():
    if request.method == "POST":
        employee = Employee(
            name=request.form["name"].strip(),
            email=request.form["email"].strip(),
            password=request.form["password"],
            salary=request.form["salary"],
            department=request.form["department"].strip(),
        )

        try:
            db.session.add(employee)
            db.session.commit()
            flash(f"Employee '{employee.name}' was added successfully.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("An employee with that email already exists.", "danger")
            return render_template("add_employee.html")

        return redirect(url_for("employee.employee_list"))

    return render_template("add_employee.html")


@employee_bp.route("/employee/employeeDetail/<int:id>", methods=["GET"])
def employeeDetail(id):
    employee = Employee.query.get_or_404(id)
    return render_template("employee_detail.html", employee=employee)


@employee_bp.route("/employee/employeeUpdate/<int:id>", methods=["POST", "GET"])
def employeeUpdate(id):
    employee = Employee.query.get_or_404(id)

    if request.method == "POST":
        employee.name = request.form["name"].strip()
        employee.email = request.form["email"].strip()
        employee.password = request.form["password"]
        employee.salary = request.form["salary"]
        employee.department = request.form["department"].strip()

        try:
            db.session.commit()
            flash(f"Employee '{employee.name}' was updated successfully.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("An employee with that email already exists.", "danger")
            return render_template("update_employee.html", employee=employee)

        return redirect(url_for("employee.employee_list"))

    return render_template("update_employee.html", employee=employee)


@employee_bp.route("/employee/employeeDelete/<int:id>")
def employeeDelete(id):
    employee = Employee.query.get_or_404(id)
    name = employee.name

    db.session.delete(employee)
    db.session.commit()

    flash(f"Employee '{name}' was deleted successfully.", "success")
    return redirect(url_for("employee.employee_list"))
