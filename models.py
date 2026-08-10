from pydantic import BaseModel


class ProductCreate(BaseModel):   # Model for creating a new product
    name: str
    description: str
    price: float
    quantity: int


class ProductUpdate(BaseModel):  # Model for updating an existing product
    name: str | None = None
    description: str | None = None
    price: float | None = None
    quantity: int | None = None


class ProductResponse(BaseModel):   # Model for returning product data in responses
    id: int
    name: str
    description: str
    price: float
    quantity: int

class UserCreate(BaseModel): #Model for creating a new user
    username: str
    email: str
    password: str


class UserResponse(BaseModel): # Model for returning user data in responses
    id: int
    username: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str