from fastapi import FastAPI
from pydantic import BaseModel
from database import(create_table, add_credit,add_products,add_sale, update_credits,update_product,get_credit,get_inventory_logs,get_products,get_sales,delete_credit,get_financial_summary)

app = FastAPI()
create_table()

class Product(BaseModel):
    name:str
    quantity:int 
    low_threshold:int
    buying_price:float
    selling_price:float

class Sale(BaseModel):
    product_id:int
    quantity_sold:int
    

class Credit(BaseModel):
    cust_name:str
    amount_owed:int
    payment_status:str
    items_borrowed:str


class Inventory(BaseModel):
    product_id:int
    quantity_added:int


@app.get("/")
def home():
    return{"Message":"Welcome to Pollah's Inventory Manager"}

@app.get("/products")
def list_products():
    return get_products()

@app.put("/products/{id}")
def edit_products(id:int, product:Product):
    update_product(id,product.name,product.quantity,product.low_threshold,product.selling_price,product.buying_price)
    return{"Message": "Product Updated Successfully","product":Product}

@app.post("/products")
def insert_product(product:Product):
    add_products(product.name,product.quantity,product.low_threshold,product.selling_price,product.buying_price)
    return {"Message":"Product Added Successfully","product":Product}


@app.get("/sales") 
def list_sales():
    return get_sales()

@app.post("/sales")
def insert_sales(sale:Sale):
    success = add_sale(sale.product_id, sale.quantity_sold)
    if not success:
        return {"Error": "Product not found"}
    return {"Message": "Sales logged and profit calculated "}

    add_sale(sale.product_id,sale.quantity_sold,sale.total_profit)
    return{"Message":"Sales Added Successfully","sale":Sale}

@app.get("/sales")
def list_sales():
    return get_sales()

@app.post("/credits")
def insert_credit(credit:Credit):
    add_credit(credit.cust_name,credit.amount_owed,credit.payment_status,credit.items_borrowed)
    return {"Message":"Credit Added Successfully","credit":Credit}

@app.get("/credits")
def list_crediits():
    return get_credit()

@app.put("/credits/{id}")
def edit_credits(credit:Credit, id:int):
    update_credits(credit.cust_name,credit.amount_owed,credit.payment_status,credit.items_borrowed,id)
    return{"Message": "Credit Updated Successfully","credit":Credit}

@app.delete("/credits/{id}")
def remove_credit(id:int):
    delete_credit(id)
    return {"Message": "Credit Deleted Successfully","id":id}

@app.get("/inventory_logs")
def list_inventory_logs():
    return get_inventory_logs()

@app.get("/dashboard/summary")
def get_summary():
    return get_financial_summary()


 