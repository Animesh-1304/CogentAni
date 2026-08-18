from fastapi import FastAPI, Depends, HTTPException, Request, status, Query
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import os
from arq.connections import ArqRedis
from arq import create_pool
from arq.connections import RedisSettings
import json
from redis_client import redis_client, clear_product_cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from logging_config import logger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    UserCreate,
    UserLogin,
    UserResponse
)
from auth import hash_password, verify_password
from jwt_auth import create_access_token, verify_access_token
from database import session, engine
import database_models

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Connecting to Redis...")

    await redis_client.ping()

    logger.info("Redis connection successful")

    app.state.arq_pool = await create_pool(
        RedisSettings(
            host="redis",
            port=6379
        )
    )

    logger.info("ARQ pool created")

    yield

    logger.info("Closing ARQ pool...")

    await app.state.arq_pool.close()

    logger.info("ARQ pool closed")

    logger.info("Closing Redis connection...")

    await redis_client.aclose()

    logger.info("Redis connection closed")
def get_arq_pool(request: Request)-> ArqRedis:
    return request.app.state.arq_pool

app=FastAPI(lifespan=lifespan)
security = HTTPBearer()

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):
    logger.error(
        "Database integrity error on %s %s",
        request.method,
        request.url.path
    )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": "Database constraint violation"
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    logger.warning(
        "Request validation failed on %s %s",
        request.method,
        request.url.path
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Invalid request data"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error"
        }
    )


allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_headers=["*"],
    allow_methods=["*"],
)



@app.get("/")
async def greet():
    return "Hello, welcome to the program!"


async def get_db():
    async with session() as db:
        yield db

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    result = await db.execute(
        select(database_models.User).where(
            database_models.User.id == int(user_id)
        )
    )

    current_user = result.scalar_one_or_none()

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return current_user

@app.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    logger.info(
        "Registration attempt for username: %s",
        user.username
    )

    result = await db.execute(
        select(database_models.User).where(
            (database_models.User.username == user.username)
            | (database_models.User.email == user.email)
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        if existing_user.username == user.username:
            logger.warning(
                "Registration failed: username already exists: %s",
                user.username
            )

            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )

        logger.warning(
            "Registration failed: email already exists: %s",
            user.email
        )

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    password_hash = hash_password(user.password)

    db_user = database_models.User(
        username=user.username,
        email=user.email,
        password_hash=password_hash
    )

    db.add(db_user)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        logger.warning(
            "Registration failed due to duplicate username or email: %s",
            user.username
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists"
        )

    await db.refresh(db_user)

    logger.info(
        "User registered successfully: %s",
        db_user.username
    )

    return db_user

@app.post("/login")
async def login_user(
    user: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    logger.info(
        "Login attempt for username: %s",
        user.username
    )
    result = await db.execute(   #Find the user
        select(database_models.User).where(
            database_models.User.username == user.username
        )
    )

    db_user = result.scalar_one_or_none()

    if db_user is None: #If user doesn't exist
        logger.warning(
            "Login failed: user not found: %s",
            user.username)
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )

    if not verify_password(
        user.password,
        db_user.password_hash
    ):
        logger.warning(
        "Login failed: incorrect password for username: %s",
        user.username
    )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    #Create JWT if password is correct
    access_token = create_access_token(
        data={
            "sub": str(db_user.id)
        }
    )
    logger.info(
    "Login successful for username: %s",
    db_user.username
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/products", response_model=list[ProductResponse])
async def get_all_products(
    page: int = Query(1, ge=1, description="Page number, must be greater than or equal to 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of products per page"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    offset = (page - 1) * limit

    cache_key = f"products:page:{page}:limit:{limit}"

    cached_products = await redis_client.get(cache_key)

    if cached_products:
        return json.loads(cached_products)

    result = await db.execute(
        select(database_models.Product)
        .order_by(database_models.Product.id)
        .offset(offset)
        .limit(limit)
    )

    db_products = result.scalars().all()

    products_data = [
        ProductResponse.model_validate(product).model_dump(mode="json")
        for product in db_products
    ]

    await redis_client.set(
        cache_key,
        json.dumps(products_data),
        ex=60
    )

    return db_products

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    result = await db.execute(
        select(database_models.Product).where(
            database_models.Product.id == product_id
        )
    )

    db_product = result.scalar_one_or_none()

    if db_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return db_product

@app.post("/products", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
async def add_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    db_product = database_models.Product(
        **product.model_dump()
    )

    db.add(db_product)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        logger.error(
            "Database error while creating product"
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create product"
        )

    await db.refresh(db_product)
    await clear_product_cache()

    return db_product

@app.put("/products/{id}", response_model=ProductResponse)
async def update_product(
    id: int,
    updated_product: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    result = await db.execute(
        select(database_models.Product).where(
            database_models.Product.id == id
        )
    )

    db_product = result.scalar_one_or_none()

    if db_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found")

    db_product.name = updated_product.name
    db_product.description = updated_product.description
    db_product.price = updated_product.price
    db_product.quantity = updated_product.quantity

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        logger.error(
            "Database error while updating product: %s",
            id
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update product"
        )

    await db.refresh(db_product)
    await clear_product_cache()

    return db_product

@app.delete("/products/{id}")
async def delete_product(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(
        select(database_models.Product).where(
            database_models.Product.id == id
        )
    )

    db_product = result.scalar_one_or_none()

    if db_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(db_product)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        logger.error(
            "Database error while deleting product: %s",
            id
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not delete product"
        )
    await clear_product_cache()

    return {"message": "Product deleted successfully"}

@app.patch("/products/{id}", response_model=ProductResponse)
async def patch_product(
    id: int, 
    updated_product: ProductUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    result = await db.execute(
        select(database_models.Product).where(
            database_models.Product.id == id
        )
    )

    db_product = result.scalar_one_or_none()

    if db_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    update_data = updated_product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        logger.error(
            "Database error while patching product: %s",
            id
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update product"
        )

    await db.refresh(db_product)
    await clear_product_cache()

    return db_product

@app.get("/redis-test")
async def redis_test():
    await redis_client.set("message", "Hello from Redis")

    value = await redis_client.get("message")

    return {
        "message": value
    }
@app.get("/redis-cache-test")
async def redis_cache_test():

    cached_value = await redis_client.get("cache_test")

    if cached_value:
        return {
            "source": "redis",
            "message": cached_value
        }

    message = "This came from the source"

    await redis_client.set(
        "cache_test",
        message,
        ex=60
    )

    return {
        "source": "source",
        "message": message
    }

@app.post("/hello-job")
async def create_hello_job(
    name: str,
    pool: ArqRedis = Depends(get_arq_pool)
):
    job = await pool.enqueue_job(
        "say_hello",
        name
    )

    return {
        "message": "Job queued successfully",
        "job_id": job.job_id
    }