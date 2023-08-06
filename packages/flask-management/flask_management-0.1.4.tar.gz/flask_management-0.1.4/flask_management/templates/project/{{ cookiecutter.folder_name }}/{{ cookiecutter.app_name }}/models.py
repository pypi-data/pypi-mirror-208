from {{ cookiecutter.app_name }}.ext import db


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime(True), nullable=False,
        server_default=db.text("CURRENT_TIMESTAMP")
    )
    updated_at = db.Column(
        db.DateTime(True), nullable=False,
        server_default=db.text("CURRENT_TIMESTAMP")
    )
    name = db.Column(db.String(64))
