from flask import Blueprint, render_template, request
from app.models.department import Department
department_bp=Blueprint("department",__name__)
@department_bp.route("/department")
def departmentHome():
    search=request.args.get("q","").strip()
    page=max(request.args.get('page',1,type=int),1)
    query=Department.query
    if search: query=query.filter(Department.name.ilike(f"%{search}%"))
    pagination=query.order_by(Department.name).paginate(page=page,per_page=10,error_out=False)
    return render_template("department.html",departments=pagination.items,pagination=pagination,search=search)





