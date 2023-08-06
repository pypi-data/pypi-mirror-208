from flask import Blueprint


api = Blueprint(__name__)


@api.get("/books")
def get_books():
    return dict(books=[])
