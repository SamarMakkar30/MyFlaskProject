from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260726_department_model"
down_revision = "1576a46d2cf3"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()
    if "departments" not in tables:
        op.create_table("departments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("budget", sa.Float(), nullable=True), sa.UniqueConstraint("name"))
        op.execute("INSERT INTO departments (name) SELECT DISTINCT department FROM employees")
    columns = {column["name"] for column in inspect(bind).get_columns("employees")}
    if "department_id" not in columns:
        with op.batch_alter_table("employees") as batch:
            batch.add_column(sa.Column("department_id", sa.Integer(), nullable=True))
    if "department" in columns:
        op.execute("UPDATE employees SET department_id=(SELECT id FROM departments WHERE departments.name=employees.department) WHERE department_id IS NULL")
    columns = {column["name"] for column in inspect(bind).get_columns("employees")}
    with op.batch_alter_table("employees") as batch:
        if "department" in columns:
            batch.drop_column("department")
        batch.alter_column("department_id", existing_type=sa.Integer(), nullable=False)
        batch.alter_column("password", type_=sa.String(255), existing_type=sa.String(50))
        if not any(fk.get("name") == "fk_employees_department_id" for fk in inspect(bind).get_foreign_keys("employees")):
            batch.create_foreign_key("fk_employees_department_id", "departments", ["department_id"], ["id"])

def downgrade():
    raise NotImplementedError("Department migration is irreversible")

