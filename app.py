from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


# CREATE DATABASE TABLES WHEN SERVER STARTS
with app.app_context():
    db.create_all()


@app.route('/')
def index():

    expenses = Expense.query.all()

    total = db.session.query(func.sum(Expense.amount)).scalar() or 0

    category_data = db.session.query(
        Expense.category,
        func.sum(Expense.amount)
    ).group_by(Expense.category).all()

    labels = [c[0] for c in category_data]
    values = [c[1] for c in category_data]

    return render_template(
        'index.html',
        expenses=expenses,
        total=total,
        labels=labels,
        values=values
    )


@app.route('/add', methods=['POST'])
def add():

    title = request.form['title']
    category = request.form['category']
    amount = float(request.form['amount'])

    new_expense = Expense(
        title=title,
        category=category,
        amount=amount
    )

    db.session.add(new_expense)
    db.session.commit()

    return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):

    expense = Expense.query.get(id)

    db.session.delete(expense)
    db.session.commit()

    return redirect('/')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    expense = Expense.query.get_or_404(id)

    if request.method == 'POST':
        expense.title = request.form['title']
        expense.category = request.form['category']
        expense.amount = float(request.form['amount'])

        db.session.commit()

        return redirect('/')

    return render_template('edit.html', expense=expense)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
