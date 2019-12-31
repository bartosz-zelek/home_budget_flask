from flaskapp import db
from flask_login import UserMixin
from flaskapp import login_manager
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class BudgetAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    budget_action_type_id = db.Column(db.Integer, db.ForeignKey('budget_action_type.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2, 2), nullable=False)
    title = db.Column(db.String(60), nullable=False)
    budget_action_category_id = db.Column(db.Integer, db.ForeignKey('budget_action_category.id'), nullable=False, default=-1)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    money_source_id = db.Column(db.Integer, db.ForeignKey('money_source.id'), nullable=False)
    remember = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class User(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    budget_action = db.relationship('BudgetAction')
    budget_action_category = db.relationship('BudgetActionCategory')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class BudgetActionType(db.Model):   # wydatek/przychód
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    budget_action_category = db.relationship('BudgetActionCategory', backref='budget_action_type', lazy=True)
    budget_action = db.relationship('BudgetAction', backref='budget_action', lazy=True)


class BudgetActionCategory(db.Model):   # np.: pensja, zakupy
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action_type_id = db.Column(db.Integer, db.ForeignKey('budget_action_type.id'), nullable=False)

    budget_action = db.relationship('BudgetAction', backref='budget_action_category', lazy=True)


class MoneySource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    saving = db.Column(db.Boolean, default=False)

    budget_action = db.relationship('BudgetAction', backref='money_source', lazy=True)


'''
do stworzenia danych w cmd uruchom python:
from myapp import create_app, db
app = create_app()
ctx = app.app_context()
ctx.push()

db.create_all()
db.session.commit()

ctx.pop()
'''