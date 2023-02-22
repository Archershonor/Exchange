from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from datetime import datetime
from Parser import ExchangeAPI
from flask_crontab import Crontab



app = Flask (__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://odoo:odoo@localhost/exchange'
db = SQLAlchemy(app)
ma = Marshmallow(app)
Parser = ExchangeAPI()
crontab = Crontab(app)

class currency(db.Model):
    __tablename__ = 'currency'
    id = db.Column('id', db.Integer, primary_key = True)
    code = db.Column(db.String(6), nullable=False)
    name = db.Column(db.String(100))
    currency_value_ids = db.relationship('values', backref='currency')

    def __repr__(self):
        return f"<{self.code}>"


class values(db.Model):
    __tablename__ = 'values'
    id = db.Column(db.Integer, primary_key = True)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))


class currencySchema(ma.SQLAlchemySchema):
    class Meta:
        model = currency
        include_relationship = True
        load_instance = True
    
    id   = ma.auto_field()
    name = ma.auto_field()
    code = ma.auto_field()
    currency_value_ids = ma.List(ma.HyperlinkRelated("values"))
    # currency_value_ids = ma.auto_field() 
    # in current last version of marshmallow_sqlalchemy 
    # SQLAlchemyAutoSchema can`t work with relationship fields
    # But we can use SQLAlchemySchema with list of HyperlinkRelated

class valuesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = values
        include_relationship = True
        load_instance = True


@app.route('/', methods = ['GET', 'POST'])
def show_all():
    if request.form.get('search'):
        return show_one_intime(request.form.get('search'))
        # if the search function needs to search the db, uncomment this block of code
        # return  render_template("insex.html", 
        #         currency_list=currency.query.like(code = request.form.get('search')))
    elif request.form.get('get_values'):
        parce_now()
    return render_template('index.html', currency_list = currency.query.all() )


@app.route('/currency-<code>', methods = ['GET', 'POST'])
def show_one(code):
    exch = currency.query.filter_by(code=code).first()
    vals  = values.query.filter_by(currency_id=exch.id).all()
    print(exch.currency_value_ids)
    return render_template('currency.html', currency_list=vals, code=code)

@app.route('/intime/<code>', methods = ['GET', 'POST'])
def show_one_intime(code):
    exch = Parser.get_one_exchange_value(code)
    vat = currencySchema(exch)
    print(vat)
    if exch.get('rates'):
        base=exch.get('base')
        for key,val in exch.get('rates').items():
            cur, value = key, val
    else:
        base='USD'
        cur=code
        value="{} is not a code of currency".format(cur)
    return render_template('show_one.html', base=base, cur=cur, value=value )


@app.cli.command
@crontab.job(minute="1", hour="0")
def planning_updator():
    print('crontab running ...')
    app.logger.info('crontab running ...')


def parce_now():
    ex_dict = Parser.get_exchange_values()
    if ex_dict:
        _date = ex_dict.get('date')
        for key, value in ex_dict.get('rates').items():
            print(key, value)
            exch = currency.query.filter_by(code=key).first()
            if not exch:
                c = currency(code=key)
                db.session.add(c)
                db.session.commit()
                exch = currency.query.filter_by(code=key).first()
            val = values.query.filter_by(date=_date, currency_id=exch.id).first()
            if not val:
                vall = values(currency_id=exch.id,value=value,date=_date)
                db.session.add(vall)
                db.session.commit()
                val = values.query.filter_by(date=_date, currency_id=exch.id).first()
            elif val.value != value:
                val.value=value
                db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.cli.add_command(planning_updator, 'planning_updator')
    app.run(debug = True)