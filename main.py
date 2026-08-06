from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from database import session, engine
import database_models
from sqlalchemy.orm import Session

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
)

database_models.Base.metadata.create_all(bind=engine)

@app.get("/")
def greet():
    return "Hello, welcome to the program!"

products=[
    Product(id=1, name="phone", description="A smartphone with 128GB storage", price=699.99, quantity=50),
    Product(id=2, name="laptop", description="A laptop with 16GB RAM and 512GB SSD", price=1299.99, quantity=30),
    Product(id=3, name="headphones", description="Wireless headphones with noise cancellation", price=199.99, quantity=100),
    Product(id=4, name="smartwatch", description="A smartwatch with heart rate monitoring", price=249.99, quantity=75)
]

def get_db():
    db=session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    
    db=session()
    count=db.query(database_models.Product).count()

    if count==0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))
        db.commit()

init_db()


@app.get("/products")
def get_all_products(db: Session=Depends(get_db)):
   
    db_products=db.query(database_models.Product).all()
    return db_products 

@app.get("/products/{product_id}")
def get_product_by_id(product_id: int, db: Session=Depends(get_db)):
    db_product=db.query(database_models.Product).filter(database_models.Product.id==product_id).first()
    if db_product:
        return db_product
    return None

@app.post("/products")
def add_product(product: Product, db: Session=Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return product

@app.put("/products/{id}")
def update_product(id: int, updated_product: Product, db: Session=Depends(get_db)):
    db_product=db.query(database_models.Product).filter(database_models.Product.id==id).first()
    if db_product:
        db_product.name=updated_product.name
        db_product.description=updated_product.description
        db_product.price=updated_product.price
        db_product.quantity=updated_product.quantity
        db.commit()
        return "Product updated successfully"
    else:   
        return "Product not found"

@app.delete("/products")
def delete_product(id: int, db: Session=Depends(get_db)):
    db_product=db.query(database_models.Product).filter(database_models.Product.id==id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "Product deleted successfully"
    else:
        return "Product not found"
          