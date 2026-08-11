from pydantic import BaseModel, Field, EmailStr


class ProductCreate(BaseModel):   # Model for creating a new product
    name: str
    description: str
    price: float=Field(..., gt=0, description="Price must be greater than 0")
    quantity: int=Field(..., ge=0, description="Quantity must be greater than or equal to 0")   


class ProductUpdate(BaseModel):  # Model for updating an existing product
    name: str | None = None
    description: str | None = None
    price: float | None =Field(default=None, gt=0, description="Price must be greater than 0")
    quantity: int | None = Field(default=None, ge=0, description="Quantity must be greater than or equal to 0")


class ProductResponse(BaseModel):   # Model for returning product data in responses
    id: int
    name: str
    description: str
    price: float
    quantity: int

class UserCreate(BaseModel): #Model for creating a new user
    username: str= Field(min_length=3, max_length=128)
    email: EmailStr
    password: str= Field(min_length=8, max_length=128)


class UserResponse(BaseModel): # Model for returning user data in responses
    id: int
    username: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str