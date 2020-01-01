from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, DecimalField, SelectField, DateField
from wtforms.validators import DataRequired, Length, NumberRange
from datetime import datetime
from flaskapp.models import BudgetActionCategory, BudgetActionType, MoneySource


class AddIncomeForm(FlaskForm):
    amount_income = DecimalField('Kwota', places=2, validators=[DataRequired()])
    title_income = StringField('Tytuł', validators=[Length(max=60)])
    category_income = SelectField('Kategoria', validators=[DataRequired()],
                                  coerce=int)
    date_income = DateField('Data', default=datetime.now)
    source_income = SelectField('Źródło', validators=[DataRequired()], coerce=int)
    remember_income = BooleanField('Zapamiętaj transakcję', default=False)
    submit_income = SubmitField('Zapisz przychód')

    @staticmethod
    def form_with_choices(user_id):
        form = AddIncomeForm()
        action_type_id = BudgetActionType.query.filter_by(name='income').first().id
        form.category_income.choices = ([(cat.id, cat.name.capitalize()) for cat in
                                         BudgetActionCategory.query.filter_by(user_id=user_id,
                                                                              action_type_id=action_type_id)] or [
                                            (-1, 'Brak kategorii')])
        form.source_income.choices = [(src.id, src.name.capitalize()) for src in
                                      MoneySource.query.order_by(MoneySource.id.desc()).all()]
        return form, action_type_id


class AddExpenseForm(FlaskForm):
    amount_expense = DecimalField('Kwota', places=2, validators=[DataRequired()])
    title_expense = StringField('Tytuł', validators=[Length(max=60)])
    category_expense = SelectField('Kategoria', validators=[DataRequired()],
                                   coerce=int)
    date_expense = DateField('Data', default=datetime.now)
    source_expense = SelectField('Źródło', validators=[DataRequired()], coerce=int)
    remember_expense = BooleanField('Zapamiętaj transakcję', default=False)
    submit_expense = SubmitField('Zapisz wydatek')

    @staticmethod
    def form_with_choices(user_id):
        form = AddExpenseForm()
        action_type_id = BudgetActionType.query.filter_by(name='expense').first().id
        form.category_expense.choices = ([(cat.id, cat.name.capitalize()) for cat in
                                          BudgetActionCategory.query.filter_by(user_id=user_id,
                                                                               action_type_id=action_type_id)] or [
                                             (-1, 'Brak kategorii')])
        form.source_expense.choices = [(src.id, src.name.capitalize()) for src in
                                       MoneySource.query.order_by(MoneySource.id.desc()).all()]
        return form, action_type_id


class AddIncomeCategoryForm(FlaskForm):
    name_income = StringField('Nazwa nowej kategorii', validators=[DataRequired(), Length(min=3, max=15)])
    submit_income = SubmitField('Zapisz kategorię')


class AddExpenseCategoryForm(FlaskForm):
    name_expense = StringField('Nazwa nowej kategorii', validators=[DataRequired(), Length(min=3, max=25)])
    submit_expense = SubmitField('Zapisz kategorię')


class TransferMoneyForm(FlaskForm):
    money_source = SelectField('Przenieść z (źródło)', validators=[DataRequired()], coerce=int)
    money_destination = SelectField('Przenieść do (miejsce przeznaczenia)',
                                                     validators=[DataRequired()], coerce=int)
    amount = DecimalField('Kwota', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Przenieś środki')

    @staticmethod
    def form_with_choices():
        form = TransferMoneyForm()
        form.money_source.choices = [(src.id, src.name.capitalize()) for src in
                                     MoneySource.query.order_by(MoneySource.id.desc()).all()]
        form.money_destination.choices = [(src.id, src.name.capitalize()) for src in
                                     MoneySource.query.order_by(MoneySource.id.desc()).all()]
        return form
