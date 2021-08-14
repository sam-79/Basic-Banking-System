import sqlite3 as sql
from flask import Flask, jsonify, request
from flask import render_template
import random as r
from datetime import datetime
import string, time, os


app = Flask(__name__)
app.debug = True

# database connection
if(not os.path.isfile('banking.db')):
    conn = sql.connect('banking.db')
    conn.execute(
        """create table customers (
            account_no primary key,
            name varchar[30],
            email varchar[30],
            current_bal int
        );"""
    )

    conn.execute("""
        create table transHistory (
            txnid varchar[25] PRIMARY key,
            sender int,
            receiver int,
            amount int,
            datetime datetime
        )
    """)
    conn.close()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/all-Customers')
def customers():
    return render_template ('all-customers.html')


@app.route('/getCustomersDetails',methods=['POST'])
def getCustomersDetails():

    try:
        conn = sql.connect('banking.db')
        mycur = conn.cursor()
        mycur.execute('select * from customers')
        data = mycur.fetchall()
        conn.close()
        return jsonify(data)
    except Exception as exp:
        return 'Try Again '+exp

    


@app.route('/transfer',methods=['POST'])
def tranfer():
    data = request.form.to_dict()
    
    sender = data['sender_num']
    receiver = data['rec_num']
    amount = data['amount']

    if(sender == receiver):
        return render_template('msg.html',head='Error',msg='Sender & Receiver are same')

    try:
        conn = sql.connect('banking.db')

        #Retrive data before updating values to check sender have sufficient balance to transfer money
        mycur = conn.cursor()
        mycur.execute(f"Select current_bal from customers where account_no = {sender};")
        
        
        if (float(amount) >= float(mycur.fetchall()[0][0]) ):
            raise Exception('Insufficient Balance')

        #Subtract from sender
        query = f"UPDATE customers SET current_bal = current_bal-{amount} WHERE account_no = {sender} AND current_bal>{amount};"
        
        conn.execute(query)
        
        #Add to receiver
        query = f"UPDATE customers SET current_bal = current_bal+{amount} WHERE account_no = {receiver};"
        conn.execute(query)
        
        #Commit changes
        conn.commit()
        conn.close()


        conn = sql.connect('banking.db')

        #Adding to history table
        seq = string.ascii_letters+string.digits
        txnid = "".join(r.choices(seq, k=10))
        ttime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        query = f"INSERT INTO transHistory VALUES ('{txnid}', {sender}, {receiver}, {amount}, '{ttime}' )"
        conn.execute(query)
        conn.commit()
        conn.close()

        return render_template('msg.html', head='Done',msg =f'Transaction Successfully Done Of Rs. {amount} on {ttime}.  Transaction ID: {txnid} ')
    
    except Exception as exp:
        print(exp)
        return render_template('msg.html',head='Error',msg= f'{exp}')


@app.route('/trans-history')
def history():
    return render_template('history.html')

@app.route('/getHistory', methods=['POST'])
def getHistory():
    try:
        conn = sql.connect('banking.db')
        mycur = conn.cursor()
        mycur.execute('select * from transHistory')
        data = mycur.fetchall()
        conn.close()

        return jsonify(data)
    except Exception as exp:
        return 'Try Again '+exp

@app.route('/addCustomer',methods=['POST'])
def add():
    data = request.form.to_dict()
    
    name = data['C_name']
    email = data['email']
    amount = data['amount']
    acct_no="".join(r.choices(string.digits, k=10))

    try:
        conn = sql.connect('banking.db')
        query = f"INSERT INTO customers VALUES ({acct_no}, '{name}', '{email}', {amount})"
        conn.execute(query)
        conn.commit()
        conn.close()

        return render_template('msg.html', head='Done',msg =f'Account created successfully. Account Number: {acct_no}.  Balance: {amount}')
    except Exception as exp:
        print(exp)
        return render_template('msg.html',head='Error',msg= f'{exp}')




if __name__ == '__main__':
    app.run(port=1222)