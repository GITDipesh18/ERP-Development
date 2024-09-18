from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, make_response, Response
from flask_mail import Mail, Message
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abcd1234@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Indent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    indent_number = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    initiated_by = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(100), nullable=False)
    manager = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    items = db.relationship('Item', backref='indent', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    indent_number = db.Column(db.String(100), db.ForeignKey('indent.indent_number'), nullable=False)
    item_code = db.Column(db.String(100), nullable=False)
    type_of_item = db.Column(db.String(100), nullable=False)
    item_with_specification = db.Column(db.String(100), nullable=False)
    to_be_used = db.Column(db.String(100), nullable=False)
    required_by = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)
    udm = db.Column(db.String(100), nullable=False)

class PaymentAdvice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    vendor_name = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.String(100), nullable=False)
    mode_of_payment = db.Column(db.String(100), nullable=False)
    terms_of_payment = db.Column(db.String(100), nullable=False)
    nature_of_payment = db.Column(db.String(100), nullable=False)

class GRN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    vendor_name = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    item_code = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)
    uom = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/indent', methods=['GET', 'POST'])
def indent():
    if request.method == 'POST':
        indent_number = request.form['indent_number']
        date = request.form['date']
        department = request.form['department']
        project_name = request.form['project_name']
        initiated_by = request.form['initiated_by']
        store = request.form['store']
        manager = request.form['manager']
        director = request.form['director']
        new_indent = Indent(indent_number=indent_number, date=date, department=department, project_name=project_name, initiated_by=initiated_by, store=store, manager=manager, director=director)
        db.session.add(new_indent)
        db.session.commit()
        return redirect(url_for('indent'))
    return render_template('indent.html')

@app.route('/item', methods=['GET', 'POST'])
def item():
    if request.method == 'POST':
        indent_number = request.form['indent_number']
        item_code = request.form['item_code']
        type_of_item = request.form['type_of_item']
        item_with_specification = request.form['item_with_specification']
        to_be_used = request.form['to_be_used']
        required_by = request.form['required_by']
        quantity = request.form['quantity']
        udm = request.form['udm']
        new_item = Item(indent_number=indent_number, item_code=item_code, type_of_item=type_of_item, item_with_specification=item_with_specification, to_be_used=to_be_used, required_by=required_by, quantity=quantity, udm=udm)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('item'))
    return render_template('item.html')

@app.route('/paymentadvice', methods=['GET', 'POST'])
def paymentadvice():
    if request.method == 'POST':
        po_number = request.form['po_number']
        date = request.form['date']
        vendor_name = request.form['vendor_name']
        project_name = request.form['project_name']
        amount = request.form['amount']
        mode_of_payment = request.form['mode_of_payment']
        terms_of_payment = request.form['terms_of_payment']
        nature_of_payment = request.form['nature_of_payment']
        new_payment_advice = PaymentAdvice(po_number=po_number, date=date, vendor_name=vendor_name, project_name=project_name, amount=amount, mode_of_payment=mode_of_payment, terms_of_payment=terms_of_payment, nature_of_payment=nature_of_payment)
        db.session.add(new_payment_advice)
        db.session.commit()
        return redirect(url_for('paymentadvice'))
    return render_template('paymentadvice.html')

@app.route('/grn', methods=['GET', 'POST'])
def grn():
    if request.method == 'POST':
        po_number = request.form['po_number']
        date = request.form['date']
        vendor_name = request.form['vendor_name']
        project_name = request.form['project_name']
        item_code = request.form['item_code']
        quantity = request.form['quantity']
        uom = request.form['uom']
        new_grn = GRN(po_number=po_number, date=date, vendor_name=vendor_name, project_name=project_name, item_code=item_code, quantity=quantity, uom=uom)
        db.session.add(new_grn)
        db.session.commit()
        return redirect(url_for('grn'))
    return render_template('grn.html')

@app.route('/paindex/<path:po_number>')
def paindex(po_number):
    pas = PaymentAdvice.query.filter_by(po_number=po_number).all()
    return render_template('paindex.html', pas=pas)

@app.route('/grnindex/<path:po_number>')
def grnindex(po_number):
    grns = GRN.query.filter_by(po_number=po_number).all()
    return render_template('grnindex.html', grns=grns)

@app.route('/indentindex/<path:indent_number>')
def indentindex(indent_number):
    indents = Indent.query.filter_by(indent_number=indent_number).all()
    return render_template('indentindex.html', indents=indents)

@app.route('/itemindex/<path:indent_number>')
def itemindex(indent_number):
    items = Item.query.filter_by(indent_number=indent_number).all()
    return render_template('itemindex.html', items=items)

if __name__ == '__main__':
    app.run(debug=True)