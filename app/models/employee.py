
from app.models import db

class Employee(db.Model):

    __tablename__ = "employees"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(50),
        nullable=False
    )

    salary = db.Column(
        db.Float,
        nullable=False
    )

    department = db.Column(
        db.String(100),
        nullable=False
    )

    def __repr__(self):
        return f"Employee Name : {self.name}"