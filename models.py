from pydantic import BaseModel, Field, EmailStr


class ProductCreate(BaseModel):
    """Model for creating a new product."""

    name: str = Field(
        min_length=1,
        max_length=200,
        strip_whitespace=True,
        examples=["Monitor"],
    )

    description: str = Field(
        min_length=1,
        max_length=500,
        strip_whitespace=True,
        examples=["27 inch monitor"],
    )

    price: float = Field(
        gt=0,
        examples=[250.0],
        description="Price must be greater than 0",
    )

    quantity: int = Field(
        ge=0,
        examples=[10],
        description="Quantity must be greater than or equal to 0",
    )


class ProductUpdate(BaseModel):
    """Model for updating an existing product."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        strip_whitespace=True,
        examples=["Updated Monitor"],
    )

    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        strip_whitespace=True,
        examples=["Updated monitor description"],
    )

    price: float | None = Field(
        default=None,
        gt=0,
        examples=[300.0],
        description="Price must be greater than 0",
    )

    quantity: int | None = Field(
        default=None,
        ge=0,
        examples=[15],
        description="Quantity must be greater than or equal to 0",
    )


class ProductResponse(BaseModel):
    """Model for returning product data in responses."""

    id: int
    name: str
    description: str
    price: float
    quantity: int

    model_config = {
        "from_attributes": True
    }


class UserCreate(BaseModel):
    """Model for creating a new user."""

    username: str = Field(
        min_length=3,
        max_length=128,
        strip_whitespace=True,
        examples=["animesh"],
    )

    email: EmailStr = Field(
        examples=["animesh@example.com"],
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    """Model for returning user data in responses."""

    id: int
    username: str
    email: str

    model_config = {
        "from_attributes": True
    }


class UserLogin(BaseModel):
    """Model for user login."""

    username: str = Field(
        min_length=3,
        max_length=128,
        strip_whitespace=True,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )