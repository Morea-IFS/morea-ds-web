from app.models import ExtendUser
from django.core.validators import EmailValidator, ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def validate(request):
    errors = []
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']

    verify_username(username, errors)
    verify_email(email, errors)
    verify_password(password, errors)

    return errors


def verify_username(username, errors):  # This function checks if the username is already registered
    try:
        user_username = ExtendUser.objects.get(username=username)
        if user_username:
            errors.append("username already exist")
    except ExtendUser.DoesNotExist:
        user_username = None


def verify_email(email, errors):  # This function checks whether the email is already registered and its format
    try:
        user_email = ExtendUser.objects.get(email=email)
        if user_email:
            errors.append("email already exist")
    except ExtendUser.DoesNotExist:
        user_email = None

    format_email = EmailValidator(message="Please enter a valid email address")
    try:
        format_email(email)
    except ValidationError as error:
        errors.append(error.message)


def verify_password(password, errors):  # This function checks whether the password is valid
    try:
        validate_password(password)
    except ValidationError as error:
        errors.extend(error.messages)
