from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import datetime  # Import datetime module

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bill'

mysql = MySQL(app)

@app.route('/')
def index():
    menu = [
        {'name': 'pizza', 'price': 250},
        {'name': 'Burger', 'price': 120},
        {'name': 'Pasta', 'price': 180},
        {'name': 'Fries', 'price': 250}
    ]
    return render_template('index.html', menu=menu)

@app.route('/bill', methods=['POST'])
def bill():
    name = request.form['customer_name']
    quantities = request.form.getlist('quantity')
    items = request.form.getlist('item')  # Get selected item names

    menu = {'pizza': 250, 'Burger': 120, 'Pasta': 180, 'Fries': 250}
    total = 0
    details = []

    cur = mysql.connection.cursor()
    for item, qty in zip(items, quantities):
        if item in menu and qty:
            qty = int(qty)
            amount = menu[item] * qty
            total += amount
            details.append((item, qty, amount))
            cur.execute("INSERT INTO bills(customer_name, item, quantity, amount) VALUES(%s, %s, %s, %s)",
                        (name, item, qty, amount))
    mysql.connection.commit()
    cur.close()
    return render_template('bill.html', details=details, total=total, name=name)

@app.route('/dashboard')
def dashboard():
    cur = mysql.connection.cursor()
    today = datetime.date.today()
    cur.execute('SELECT COUNT(DISTINCT customer_name) FROM bills WHERE DATE(ordered_at)=%s', (today,))
    customer_count = cur.fetchone()[0]

    cur.execute("SELECT id, customer_name, item, quantity, amount, status, payment_status FROM bills ORDER BY ordered_at DESC")
    orders = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', orders=orders, customer_count=customer_count)

@app.route('/update_status/<int:bill_id>/<string:field>/<string:value>')
def update_status(bill_id, field, value):
    cur = mysql.connection.cursor()
    if field in ['status', 'payment_status']:
        cur.execute(f"UPDATE bills SET {field}=%s WHERE id=%s", (value, bill_id))
        mysql.connection.commit()
    cur.close()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
