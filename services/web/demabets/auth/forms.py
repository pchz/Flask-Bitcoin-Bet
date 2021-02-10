from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    BooleanField
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    ValidationError,
    EqualTo
)
from wtforms_alchemy import Unique, ModelForm

from demabets.models import User


class SignupForm(FlaskForm, ModelForm):
    class Meta:
        model = User

    """Sign up for a user account."""
    email = StringField(
        'Email',
        [
            Email(message='Not a valid email address.'),
            DataRequired(),
            Length(max=120),
            Unique(User.email)
        ]
    )
    password = PasswordField(
        'Password',
        [
            DataRequired(message="Please enter a password."),
        ]
    )
    username = StringField(
        'Username',
        [
            DataRequired(message="Please enter a username"),
            Length(max=64)
        ]
    )
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        excluded_chars = " *?!'^+%&/()=}][{$#"
        for char in self.username.data:
            if char in excluded_chars:
                raise ValidationError(
                    f"Character {char} is not allowed in username.")


class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        [
            Email(message='Not a valid email address.'),
            DataRequired(),
            Length(max=120),
        ]
    )
    password = PasswordField(
        'Password',
        [
            DataRequired(message="Please enter a password."),
        ]
    )
    remember = BooleanField(
        'Remember'
    )
    submit = SubmitField('Login')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')
