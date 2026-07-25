from app.models import db
from werkzeug.security import check_password_hash, generate_password_hash
class Employee(db.Model):
    __tablename__ = "employees"
    __table_args__ = (db.CheckConstraint("salary > 0", name="ck_employee_salary_positive"),)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    department = db.relationship("Department", back_populates="employees")
    def set_password(self, raw_password): self.password = generate_password_hash(raw_password)
    def check_password(self, raw_password): return check_password_hash(self.password, raw_password)
    def __repr__(self): return f"Employee Name : {self.name}"


