import pytest
from app import create_app
from app.models import db
from app.models.department import Department
from app.models.employee import Employee

class TestConfig:
    TESTING = True
    SECRET_KEY = "test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        department = Department(name="Engineering")
        employee = Employee(name="Ada Lovelace", email="ada@example.com", password="", salary=100000, department=department)
        employee.set_password("secret")
        db.session.add(employee)
        db.session.commit()
        with app.test_client() as test_client:
            test_client.get("/login")
            with test_client.session_transaction() as session:
                csrf = session["csrf_token"]
            test_client.post("/login", data={"csrf_token": csrf, "email": "ada@example.com", "password": "secret"})
            yield test_client
        db.drop_all()

def token(client):
    client.get("/employee/list")
    with client.session_transaction() as session:
        return session["csrf_token"]

def test_login_is_required_for_directory():
    app = create_app(TestConfig)
    with app.test_client() as test_client:
        assert test_client.get("/employee/list").status_code == 302
        assert "/login" in test_client.get("/employee/list").headers["Location"]

def test_password_is_hashed_and_never_rendered(client):
    with client.application.app_context():
        employee = Employee.query.first()
        assert employee.password != "secret"
        assert employee.check_password("secret")
    assert b"secret" not in client.get("/employee/employeeUpdate/1").data

def test_delete_requires_post_and_csrf(client):
    assert client.get("/employee/employeeDelete/1").status_code == 405
    assert client.post("/employee/employeeDelete/1").status_code == 400
    assert client.post("/employee/employeeDelete/1", data={"csrf_token": token(client)}).status_code == 302

def test_invalid_salary_is_rejected(client):
    response = client.post("/employee/add", data={"csrf_token": token(client), "name": "Bad", "email": "bad@example.com", "department": "Sales", "salary": "not-a-number", "password": "secret"})
    assert response.status_code == 400
    with client.application.app_context():
        assert Employee.query.filter_by(email="bad@example.com").first() is None

def test_duplicate_email_and_missing_employee(client):
    response = client.post("/employee/add", data={"csrf_token": token(client), "name": "Other", "email": "ada@example.com", "department": "Sales", "salary": "50000", "password": "secret"})
    assert response.status_code == 400
    assert client.get("/employee/employeeDetail/999").status_code == 404

def test_csv_export_filter_validation_and_search(client):
    assert client.get("/employee/export.csv?min_salary=200000&max_salary=100000").status_code == 200
    assert b"Minimum salary" in client.get("/employee/list?min_salary=200000&max_salary=100000").data
    response = client.get("/employee/search.json?q=Ada")
    assert response.status_code == 200 and response.json[0]["name"] == "Ada Lovelace"



