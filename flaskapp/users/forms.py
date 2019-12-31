from flaskapp.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj się')


class RegistrationForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired(), Length(min=6)])
    password_repeated = PasswordField('Powtórz hasło', validators=[DataRequired(), EqualTo('password',
                                                                                           message='Pola nie są takie same.')])
    submit = SubmitField('Zarejestruj się')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Resetuj hasło')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Hasło', validators=[DataRequired(), Length(min=6)])
    password_repeated = PasswordField('Powtórz hasło', validators=[DataRequired(), EqualTo('password',
                                                                                           message='Pola nie są takie same.')])
    submit = SubmitField('Zmień hasło')