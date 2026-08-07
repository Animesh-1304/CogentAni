from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Product
from database import session, engine
import database_models

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)



@app.get("/")
async def greet():
    return "Hello, welcome to the program!"

products=[
    Product(id=1, name="phone", description="A smartphone with 128GB storage", price=699.99, quantity=50),
    Product(id=2, name="laptop", description="A laptop with 16GB RAM and 512GB SSD", price=1299.99, quantity=30),
    Product(id=3, name="headphones", description="Wireless headphones with noise cancellation", price=199.99, quantity=100),
    Product(id=4, name="smartwatch", description="A smartwatch with heart rate monitoring", price=249.99, quantity=75)
]
async def get_db():
    async with session() as db:
        yield db

async def init_db():

    async with session() as db:

        result = await db.execute(
            select(database_models.Product)
        )

        count = len(result.scalars().all())

        if count == 0:

            for product in products:
                db.add(
                    database_models.Product(
                        **product.model_dump()
                    )
                )

            await db.commit()

@app.on_event("startup")
async def startup():

    async with engine.begin() as conn:
        await conn.run_sync(
            database_models.Base.metadata.create_all
        )

    await init_db()

@app.get("/products")
async def get_all_products(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(database_models.Product)
    )

    db_products = result.scalars().all()

    return db_products

@app.get("/products/{product_id}")
async def get_product_by_id(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(database_models.Product).where(
            database_models.Product.id == product_id
        )
    )

    db_product = result.scalar_one_or_none()

    if db_product:
        return db_product

    return None

@app.post("/products")
async def add_product(
    product: Product,
    db: AsyncSession = Depends(get_db)
):

    db_product = database_models.Product(
        **product.model_dump()
    )

    db.add(db_product)

    await db.commit()

    await db.refresh(db_product)

    return db_product

@app.put("/products/{id}")
async def update_product(
    id: int,
    updated_product: Product,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(database_models.Product).where(
            database_models.Product.id == id
        )
    )

    db_product = result.scalar_one_or_none()

    if db_product is None:
        return "Product not found"

    db_product.name = updated_product.name
    db_product.description = updated_product.description
    db_product.price = updated_product.price
    db_product.quantity = updated_product.quantity

    await db.commit()

    await db.refresh(db_product)

    return db_product

@app.delete("/products/{id}")
async def delete_product(
    id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(database_models.Product).where(
            database_models.Product.id == id
        )
    )

    db_product = result.scalar_one_or_none()

    if db_product is None:
        return "Product not found"

    await db.delete(db_product)

    await db.commit()

    return "Product deleted successfully"
          