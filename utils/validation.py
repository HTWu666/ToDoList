from functools import wraps
from flask import request, jsonify
from pydantic import ValidationError


def validate_input(validation_model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                validated_data = validation_model(**request.json)

                return func(*args, **kwargs, validated_data=validated_data)
            except ValidationError as e:
                return jsonify({"errors": e.errors()[0]["msg"]}), 400

        return wrapper

    return decorator