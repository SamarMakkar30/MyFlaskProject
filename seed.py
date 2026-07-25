"""Idempotently seed the employee table with realistic demo data.

Run after `flask --app app.py db upgrade`:
    python seed.py
"""

from app import create_app
from app.models import db
from app.models.employee import Employee
from app.models.department import Department


EMPLOYEES = [
    ("Aarav Mehta", "aarav.mehta@example.com", 68000, "Engineering"),
    ("Maya Shah", "maya.shah@example.com", 82500, "Engineering"),
    ("Rohan Kapoor", "rohan.kapoor@example.com", 97000, "Engineering"),
    ("Priya Nair", "priya.nair@example.com", 112000, "Engineering"),
    ("Dev Malhotra", "dev.malhotra@example.com", 76000, "Engineering"),
    ("Ananya Iyer", "ananya.iyer@example.com", 61000, "People Operations"),
    ("Kabir Singh", "kabir.singh@example.com", 71500, "People Operations"),
    ("Ishita Rao", "ishita.rao@example.com", 89000, "People Operations"),
    ("Vikram Sethi", "vikram.sethi@example.com", 54000, "Sales"),
    ("Neha Verma", "neha.verma@example.com", 67000, "Sales"),
    ("Arjun Bhat", "arjun.bhat@example.com", 81000, "Sales"),
    ("Simran Kaur", "simran.kaur@example.com", 99000, "Sales"),
    ("Aditya Joshi", "aditya.joshi@example.com", 58000, "Marketing"),
    ("Riya Patel", "riya.patel@example.com", 69000, "Marketing"),
    ("Karan Gupta", "karan.gupta@example.com", 84500, "Marketing"),
    ("Meera Menon", "meera.menon@example.com", 101000, "Marketing"),
    ("Sanjay Das", "sanjay.das@example.com", 62000, "Finance"),
    ("Tanya Bose", "tanya.bose@example.com", 73500, "Finance"),
    ("Nikhil Jain", "nikhil.jain@example.com", 91000, "Finance"),
    ("Aditi Kulkarni", "aditi.kulkarni@example.com", 107000, "Finance"),
    ("Yash Khanna", "yash.khanna@example.com", 50500, "Engineering"),
    ("Sneha Reddy", "sneha.reddy@example.com", 64500, "People Operations"),
    ("Rahul Arora", "rahul.arora@example.com", 78000, "Sales"),
    ("Pooja Chawla", "pooja.chawla@example.com", 86500, "Marketing"),
    ("Manav Bansal", "manav.bansal@example.com", 93000, "Finance"),
    ("Kavya Pillai", "kavya.pillai@example.com", 72000, "Engineering"),
    ("Harsh Vardhan", "harsh.vardhan@example.com", 59000, "Sales"),
    ("Diya Chopra", "diya.chopra@example.com", 80500, "Marketing"),
    ("Om Prakash", "om.prakash@example.com", 87500, "Finance"),
    ("Leena Dutta", "leena.dutta@example.com", 69500, "People Operations"),
]


def seed_database():
    app = create_app()
    with app.app_context():
        existing_emails = {email for (email,) in db.session.query(Employee.email).all()}
        new_employees = [
            Employee(
                name=name,
                email=email,
                password="",
                salary=salary,
                department=Department.query.filter_by(name=department).first() or Department(name=department),
            )
            for name, email, salary, department in EMPLOYEES
            if email not in existing_emails
        ]

        for employee in new_employees:
            employee.set_password("demo-password")
        if not new_employees:
            print("Seed data already exists; no employees added.")
            return

        db.session.add_all(new_employees)
        db.session.commit()
        print(f"Added {len(new_employees)} demo employees.")


if __name__ == "__main__":
    seed_database()

