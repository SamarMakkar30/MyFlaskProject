"""Require positive employee salaries."""
from alembic import op
revision = "20260726_salary_constraint"
down_revision = "20260726_department_model"
branch_labels = None
depends_on = None
def upgrade():
    with op.batch_alter_table("employees") as batch:
        batch.create_check_constraint("ck_employee_salary_positive", "salary > 0")
def downgrade():
    with op.batch_alter_table("employees") as batch:
        batch.drop_constraint("ck_employee_salary_positive", type="check")
