import datetime

import matplotlib
import numpy as np
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from matplotlib import pyplot as plt
from flaskapp import db
from flaskapp.budget.forms import AddIncomeForm, AddExpenseForm, AddIncomeCategoryForm, AddExpenseCategoryForm
from flaskapp.models import BudgetAction, MoneySource, BudgetActionType, BudgetActionCategory

budget = Blueprint('budget', __name__)
matplotlib.use('Agg')


def update_funds():
    actions = BudgetAction.query.filter_by(user_id=current_user.id).all()
    income_id = BudgetActionType.query.filter_by(name='income').first().id
    expense_id = BudgetActionType.query.filter_by(name='expense').first().id
    funds = {
        'sum': 0,
        'wallet': 0,
        'account': 0,
        'saving': {
            'moneybox': 0,
            'deposit': 0
        }
    }

    wallet_id = MoneySource.query.filter_by(name='portfel').first().id
    account_id = MoneySource.query.filter_by(name='konta').first().id
    moneybox_id = MoneySource.query.filter_by(name='skarbonki').first().id
    deposit_id = MoneySource.query.filter_by(name='lokaty').first().id

    for action in actions:
        if action.money_source_id == wallet_id:
            if action.budget_action_type_id == income_id:
                funds['wallet'] += action.amount
                funds['sum'] += action.amount
            elif action.budget_action_type_id == expense_id:
                funds['wallet'] -= action.amount
                funds['sum'] -= action.amount
        elif action.money_source_id == account_id:
            if action.budget_action_type_id == income_id:
                funds['account'] += action.amount
                funds['sum'] += action.amount
            elif action.budget_action_type_id == expense_id:
                funds['account'] -= action.amount
                funds['sum'] -= action.amount
        elif action.money_source_id == moneybox_id:
            if action.budget_action_type_id == income_id:
                funds['saving']['moneybox'] += action.amount
                funds['sum'] += action.amount
            elif action.budget_action_type_id == expense_id:
                funds['saving']['moneybox'] -= action.amount
                funds['sum'] -= action.amount
        elif action.money_source_id == deposit_id:
            if action.budget_action_type_id == income_id:
                funds['saving']['deposit'] += action.amount
                funds['sum'] += action.amount
            elif action.budget_action_type_id == expense_id:
                funds['saving']['deposit'] -= action.amount
                funds['sum'] -= action.amount
    return funds


@budget.route('/main-panel', methods=['GET', 'POST'])  # dodaje metodę POST jeżeli konieczne
@login_required
def main():
    months = {
        1: 'Styczeń',
        2: 'Luty',
        3: 'Marzec',
        4: 'Kwiecień',
        5: 'Maj',
        6: 'Czerwiec',
        7: 'Lipiec',
        8: 'Sierpień',
        9: 'Wrzesień',
        10: 'Październik',
        11: 'Listopad',
        12: 'Grudzień',
    }

    income_id = BudgetActionType.query.filter_by(name='income').first().id
    expense_id = BudgetActionType.query.filter_by(name='expense').first().id

    month_choosed = datetime.date.today().month

    actions = BudgetAction.query.filter_by(user_id=current_user.id).order_by(BudgetAction.date.desc()).all()
    actions_month_choosed = []

    funds = update_funds()

    income_expense_plot_name = str(current_user.id)
    # ##################################################################################
    # WYKRES - START
    # ##################################################################################
    incomes_month_choosed = 0
    expenses_month_choosed = 0
    for action in actions:
        if action.date.month == month_choosed:
            actions_month_choosed.append(action)
            if action.budget_action_type_id == income_id:
                incomes_month_choosed += action.amount
            elif action.budget_action_type_id == expense_id:
                expenses_month_choosed += action.amount

    bilans = incomes_month_choosed - expenses_month_choosed

    plt.style.use('fivethirtyeight')
    y_labels = ['Wydatki', 'Przychody']
    y_pos = np.arange(len(y_labels))  #
    x_values = [expenses_month_choosed, incomes_month_choosed]

    fig, ax = plt.subplots(figsize=(8, 2))
    ax.barh(y_pos, x_values, height=0.5, color=['#db5353', '#52d95b'], edgecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels)
    plt.tight_layout()
    plt.savefig('flaskapp/static/plots/' + str(current_user.id))
    plt.close()

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.barh(y_pos, x_values, height=0.5, color=['#db5353', '#52d95b'])
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels)
    plt.tight_layout()
    plt.savefig('flaskapp/static/plots/' + str(current_user.id) + '_mobile')
    plt.close()

    expense_categories = BudgetActionCategory.query.filter_by(user_id=current_user.id, action_type_id=expense_id)
    expenses_by_category = {
        'Bez kategorii': 0
    }
    category_by_id = {
        -1: 'Bez kategorii'
    }
    for category in expense_categories:
        expenses_by_category[category.name] = 0
        category_by_id[category.id] = category.name

    for action in actions_month_choosed:
        if action.budget_action_type_id == expense_id:
            expenses_by_category[category_by_id[action.budget_action_category_id]] += action.amount

    values = []
    labels = []

    for label, value in expenses_by_category.items():
        if value > 0:
            labels.append(label)
            values.append(value)

    plt.style.use('fivethirtyeight')
    fig, ax = plt.subplots(figsize=(4.5, 3))
    ax.pie(values, labels=labels, autopct='%1.1f%%', wedgeprops={'edgecolor': 'black'})
    plt.tight_layout()
    plt.savefig('flaskapp/static/plots/' + str(current_user.id) + '_pie_expenses')
    plt.close()

    income_categories = BudgetActionCategory.query.filter_by(user_id=current_user.id, action_type_id=income_id)
    incomes_by_category = {
        'Bez kategorii': 0
    }
    category_by_id = {
        -1: 'Bez kategorii'
    }
    for category in income_categories:
        incomes_by_category[category.name] = 0
        category_by_id[category.id] = category.name

    for action in actions_month_choosed:
        if action.budget_action_type_id == income_id:
            incomes_by_category[category_by_id[action.budget_action_category_id]] += action.amount

    values = []
    labels = []

    for label, value in incomes_by_category.items():
        if value > 0:
            labels.append(label)
            values.append(value)

    plt.style.use('fivethirtyeight')
    fig, ax = plt.subplots(figsize=(4.5, 3))
    ax.pie(values, labels=labels, autopct='%1.1f%%', wedgeprops={'edgecolor': 'black'})
    plt.tight_layout()
    plt.savefig('flaskapp/static/plots/' + str(current_user.id) + '_pie_incomes')
    plt.close()
    # ##################################################################################
    # WYKRES - KONIEC
    # ##################################################################################

    # ##################################################################################
    # PRZYCHODY I WYDATKI - FORMULARZE - START
    # ##################################################################################
    form_income, income_type_id = AddIncomeForm().form_with_choices(current_user.id)
    form_expense, expense_type_id = AddExpenseForm().form_with_choices(current_user.id)
    if form_income.validate_on_submit():  # sprawdzić poprawność kategorii i źródła
        income = BudgetAction(
            budget_action_type_id=income_type_id,
            amount=form_income.amount_income.data,
            title=form_income.title_income.data,
            budget_action_category_id=form_income.category_income.data,
            date=form_income.date_income.data,
            money_source_id=form_income.source_income.data,
            remember=form_income.remember_income.data,
            user_id=current_user.id
        )
        db.session.add(income)
        db.session.commit()
        flash('Pomyślnie dodano przychód.', 'success')
        return redirect(url_for('budget.main'))
    elif form_expense.validate_on_submit():
        expense = BudgetAction(
            budget_action_type_id=expense_type_id,
            amount=form_expense.amount_expense.data,
            title=form_expense.title_expense.data,
            budget_action_category_id=form_expense.category_expense.data,
            date=form_expense.date_expense.data,
            money_source_id=form_expense.source_expense.data,
            remember=form_expense.remember_expense.data,
            user_id=current_user.id,
        )
        db.session.add(expense)
        db.session.commit()
        flash('Pomyślnie dodano wydatek.', 'success')
        return redirect(url_for('budget.main'))
    if form_income.errors.items() and form_income.submit_income.data:
        form_expense = AddExpenseForm().form_with_choices(current_user.id)
        return render_template('main-home.html', title='Panel główny', form_income=form_income,
                               form_expense=form_expense,
                               income_error=True,
                               funds=funds,
                               income_expense_plot_name=income_expense_plot_name,
                               month=months[month_choosed],
                               bilans=bilans,
                               actions_month_choosed=actions_month_choosed,
                               income_id=income_id,
                               expense_id=expense_id,
                               expenses_month_choosed=expenses_month_choosed,
                               incomes_month_choosed=incomes_month_choosed)
    elif form_expense.errors.items() and form_expense.submit_expense.data:
        form_income = AddIncomeForm().form_with_choices(current_user.id)
        return render_template('main-home.html', title='Panel główny', form_income=form_income,
                               form_expense=form_expense,
                               expense_error=True, funds=funds,
                               income_expense_plot_name=income_expense_plot_name,
                               month=months[month_choosed],
                               bilans=bilans,
                               actions_month_choosed=actions_month_choosed,
                               income_id=income_id,
                               expense_id=expense_id,
                               expenses_month_choosed=expenses_month_choosed,
                               incomes_month_choosed=incomes_month_choosed)
    # ##################################################################################
    # PRZYCHODY I WYDATKI - FORMULARZE - KONIEC
    # ##################################################################################

    return render_template('main-home.html', title='Panel główny', form_income=form_income, form_expense=form_expense,
                           funds=funds,
                           income_expense_plot_name=income_expense_plot_name,
                           month=months[month_choosed],
                           bilans=bilans,
                           actions_month_choosed=actions_month_choosed,
                           income_id=income_id,
                           expense_id=expense_id,
                           expenses_month_choosed=expenses_month_choosed,
                           incomes_month_choosed=incomes_month_choosed)


@budget.route('/modify-categories', methods=['GET', 'POST'])
@login_required
def mod_category():
    if request.args.get('delcatid'):
        cat_id = request.args.get('delcatid')
        try:
            BudgetActionCategory.query.filter_by(user_id=current_user.id, id=cat_id).delete()
            actions_change_category = BudgetAction.query.filter_by(user_id=current_user.id,
                                                                   budget_action_category_id=cat_id).all()
            for action in actions_change_category:
                action.budget_action_category_id = -1
            db.session.commit()
            flash('Pomyślnie usunięto kategorię', 'success')
        except:
            flash('Coś poszło nie tak', 'warning')

    income_id = BudgetActionType.query.filter_by(name='income').first().id
    expense_id = BudgetActionType.query.filter_by(name='expense').first().id

    funds = update_funds()

    income_category_form = AddIncomeCategoryForm()
    expense_category_form = AddExpenseCategoryForm()

    income_categories = BudgetActionCategory.query.filter_by(user_id=current_user.id, action_type_id=income_id)
    expense_categories = BudgetActionCategory.query.filter_by(user_id=current_user.id, action_type_id=expense_id)

    if income_category_form.validate_on_submit():  # sprawdzić poprawność kategorii i źródła
        income_category = BudgetActionCategory(
            name=income_category_form.name_income.data,
            user_id=current_user.id,
            action_type_id=income_id
        )
        db.session.add(income_category)
        db.session.commit()
        flash('Pomyślnie dodano kategorię przychodu.', 'success')
        return redirect(url_for('budget.add_category'))
    elif expense_category_form.validate_on_submit():
        expense_category = BudgetActionCategory(
            name=expense_category_form.name_expense.data,
            user_id=current_user.id,
            action_type_id=expense_id
        )
        db.session.add(expense_category)
        db.session.commit()
        flash('Pomyślnie dodano kategorię wydatku.', 'success')
        return redirect(url_for('budget.add_category'))
    if income_category_form.errors.items() and income_category_form.submit_income.data:
        expense_category_form = AddExpenseCategoryForm()
        return render_template('mod-category.html', title='Modyfikacja kategorii', funds=funds,
                               income_category_form=income_category_form, expense_category_form=expense_category_form)
    elif expense_category_form.errors.items() and expense_category_form.submit_expense.data:
        income_category_form = AddIncomeCategoryForm()
        return render_template('mod-category.html', title='Modyfikacja kategorii', funds=funds,
                               income_category_form=income_category_form, expense_category_form=expense_category_form)

    return render_template('mod-category.html', title='Modyfikacja kategorii', funds=funds,
                           income_category_form=income_category_form, expense_category_form=expense_category_form,
                           income_categories=income_categories, expense_categories=expense_categories)


@budget.route('/modify-budget-actions', methods=['GET', 'POST'])
@login_required
def mod_budget_actions():
    funds = update_funds()
    income_id = BudgetActionType.query.filter_by(name='income').first().id
    expense_id = BudgetActionType.query.filter_by(name='expense').first().id
    page = request.args.get('page', 1, type=int)
    actions = BudgetAction.query.filter_by(user_id=current_user.id).order_by(BudgetAction.date.desc()).paginate(
        page=page, per_page=12)

    sources = MoneySource.query.all()
    source_by_id = {}
    for source in sources:
        source_by_id[source.id] = source.name

    categories = BudgetActionCategory.query.filter_by(user_id=current_user.id).all()
    category_by_id = {
        -1: 'Bez kategorii'
    }
    for category in categories:
        category_by_id[category.id] = category.name

    if request.args.get('delete_action_id'):
        id = request.args.get('delete_action_id')
        try:
            BudgetAction.query.filter_by(id=id, user_id=current_user.id).delete()
            db.session.commit()
            flash('Pomyślnie usunięto transakcję.', 'success')
            return redirect(url_for('budget.mod_budget_actions'))
        except:
            flash('Pomyślnie usunięto transakcję.', 'danger')
            return redirect(url_for('budget.mod_budget_actions'))

    if request.args.get('action_id'):
        action_id = request.args.get('action_id')
        action = BudgetAction.query.filter_by(id=action_id, user_id=current_user.id).first()
        if action.budget_action_type_id == income_id:
            form_income_mod, income_id = AddIncomeForm().form_with_choices(current_user.id)

            if form_income_mod.validate_on_submit():
                action.amount = form_income_mod.amount_income.data
                action.title = form_income_mod.title_income.data
                action.budget_action_category_id = form_income_mod.category_income.data
                action.date = form_income_mod.date_income.data
                action.money_source_id = form_income_mod.source_income.data
                action.remember = form_income_mod.remember_income.data
                db.session.commit()
                flash('Pomyślnie zmodyfikowano transakcję.', 'success')
                return redirect(url_for('budget.mod_budget_actions', page=actions.page))

            form_income_mod.amount_income.data = action.amount
            form_income_mod.title_income.data = action.title
            form_income_mod.category_income.data = action.budget_action_category_id
            form_income_mod.date_income.data = action.date
            form_income_mod.source_income.data = action.money_source_id
            form_income_mod.remember_income.data = action.remember
            return render_template('mod-budget-actions.html', title='Transakcje', funds=funds, actions=actions,
                                   form_income_mod=form_income_mod, income_id=income_id, expense_id=expense_id,
                                   source_by_id=source_by_id, action=action)

        if action.budget_action_type_id == expense_id:
            form_expense_mod, expense_id = AddExpenseForm().form_with_choices(current_user.id)

            if form_expense_mod.validate_on_submit():
                action.amount = form_expense_mod.amount_expense.data
                action.title = form_expense_mod.title_expense.data
                action.budget_action_category_id = form_expense_mod.category_expense.data
                action.date = form_expense_mod.date_expense.data
                action.money_source_id = form_expense_mod.source_expense.data
                action.remember = form_expense_mod.remember_expense.data
                db.session.commit()
                flash('Pomyślnie zmodyfikowano transakcję.', 'success')
                return redirect(url_for('budget.mod_budget_actions'))

            form_expense_mod.amount_expense.data = action.amount
            form_expense_mod.title_expense.data = action.title
            form_expense_mod.category_expense.data = action.budget_action_category_id
            form_expense_mod.date_expense.data = action.date
            form_expense_mod.source_expense.data = action.money_source_id
            form_expense_mod.remember_expense.data = action.remember
            return render_template('mod-budget-actions.html', title='Transakcje', funds=funds, actions=actions,
                                   form_expense_mod=form_expense_mod, income_id=income_id, expense_id=expense_id,
                                   source_by_id=source_by_id, action=action)
    return render_template('mod-budget-actions.html', title='Transakcje', funds=funds, actions=actions,
                           income_id=income_id, expense_id=expense_id, source_by_id=source_by_id)