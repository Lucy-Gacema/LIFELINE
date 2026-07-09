import sqlite3
from contextlib import contextmanager

sqlite_file_name="shop.db"
@contextmanager
def get_connection():
    connection=sqlite3.connect(sqlite_file_name)
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON;")

    try:
        yield connection
        connection.commit()

    finally:
        connection.close()
        
def create_table():
    with get_connection() as connection:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS products(
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL,
                           quantity INTEGER NOT NULL,
                           low_threshold INTEGER NOT NULL,
                           buying_price REAL NOT NULL,
                           selling_price REAL NOT NULL)''')
        
        connection.execute('''
            CREATE TABLE IF NOT EXISTS sales(
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           product_id INTEGER NOT NULL,
                           quantity_sold INTEGER NOT NULL,
                           total_profit REAL NOT NULL,
                           sale_date TEXT DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY(product_id) REFERENCES products(id))''')
        

        connection.execute('''
            CREATE TABLE IF NOT EXISTS credits(
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           cust_name TEXT NOT NULL,
                           amount_owed INTEGER NOT NULL,
                           date_borrowed TEXT DEFAULT CURRENT_TIMESTAMP,
                           payment_status TEXT DEFAULT 'Pending' CHECK(payment_status IN ('Pending', 'Paid')),
                           items_borrowed TEXT NOT NULL)''')
        
        connection.execute(''' 
            CREATE TABLE IF NOT EXISTS inventory_logs(
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           product_id INTEGER NOT NULL,
                           quantity_added INTEGER NOT NULL,
                           log_date TEXT DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY(product_id) REFERENCES products(id))''')

def add_products(name, quantity, low_threshold, buying_price,selling_price):
    with get_connection()as connection:
        connection.execute('INSERT INTO products(name, quantity, low_threshold, buying_price,selling_price) VALUES(?,?,?,?,?)',(name, quantity, low_threshold, buying_price,selling_price))
        

def get_products():
    with get_connection()as connection:
        connection.execute('SELECT * FROM products').fetchall()

def update_product(name, quantity, low_threshold, buying_price,selling_price,id):
    with get_connection()as connection:
        connection.execute('UPDATE products SET name=?, quantity=?, low_threshold=?, buying_price=?,selling_price=?, id=? WHERE id = ?',(name, quantity, low_threshold, buying_price,selling_price, id))


def add_sale(product_id,quantity_sold,):
    with get_connection() as connection:
        product = connection.execute('SELECT buying_price, selling_price, quantity FROM products WHERE id=?',(product_id).fetchone())
        if not product:
            return False
        profit_per_item = product['selling_price']- product['buying_price']
        total_profit = profit_per_item*quantity_sold
        connection.execute(
            'INSERT INTO sales(product_id,quantity_sold,total_profit)VALUES(?,?,?)',(product_id,quantity_sold,total_profit))
        connection.execute('UPDATE products SET quantity=quantity ? WHERE id=?',(quantity_sold, product_id))
        return True
        
        

def get_sales():
    with get_connection() as connection:
        connection.execute('SELECT * FROM sales').fetchall()


def add_credit(cust_name,amount_owed,payment_status,items_borrowed):
    with get_connection() as connection:
        connection.execute('INSERT INTO credits(cust_name,amount_owed,payment_status,items_borrowed)VALUES(?,?,?,?)',(cust_name,amount_owed,payment_status,items_borrowed))

def get_credit():
    with get_connection() as connection:
        connection.execute('SELECT * FROM credits').fetchall()

def update_credits(id,cust_name,amount_owed,payment_status,items_borrowed):
    with get_connection() as connection:
        connection.execute('UPDATE credits SET cust_name=?,amount_owed=?,payment_status=?,items_borrowed=?, id =? WHERE id=?',(cust_name,amount_owed,payment_status,items_borrowed,id))

def delete_credit(id):
    with get_connection() as connection:
        connection.execute('DELETE FROM credits WHERE id=?', (id,))



def get_inventory_logs():
          
        with get_connection() as connection:
            return connection.execute("SELECT * FROM inventory_logs").fetchall()

def replenish_stock(product_id, quantity_added):
    with get_connection() as connection:
       
        connection.execute(
            "UPDATE products SET quantity = quantity + ? WHERE id = ?",
            (quantity_added, product_id)
        )
      
        connection.execute(
            "INSERT INTO inventory_logs (product_id, quantity_added) VALUES (?, ?)",
            (product_id, quantity_added)
        )
    
def get_financial_summary():
    with get_connection as connection:
        sales_data = connection.execute('SELECT SUM(total_profit)AS net_profit FROM sales').fetchone()
        total_profit= sales_data['net_profit'] if sales_data['net_profit']else 0.0

        credit_data = connection.execute("SELECT SUM(amount_owed)AS total_debt FROM credits WHERE payment_status='Pending'").fetchone()
        money_in_debt= credit_data['total_debt'] if credit_data['total_debt'] else 0.0

        take_home_cash = total_profit-money_in_debt
        return{
            "Total_profit_earned":total_profit,
            "Money_tied_in_debt": money_in_debt,
            "Actual_take_home_cash":take_home_cash
        }
    


