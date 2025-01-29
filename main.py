from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"  # SQLite database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

origins = ["https://dddankner.github.io/*"]  

# Recommended: Specify allowed origins
# origins = ["http://localhost:3000", "https://yourfrontend.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,  # Allow cookies to be included in requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Database Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    active = Column(Boolean, default=True)


# Create the database tables
Base.metadata.create_all(bind=engine)


# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


# CRUD Operations
# Create a User
@app.post("/users/")
async def create_user(user: dict, db: Session = Depends(get_db)):
    name = user.get("name")
    age = user.get("age")

    if not name or not age:
        raise HTTPException(status_code=400, detail="Name and age are required!")

    db_user = User(name=name, age=age, active=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully!", "user": {"id": db_user.id, "name": db_user.name, "age": db_user.age}}


# Read All Users
@app.get("/users/")
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.active == True).all()
    return [{"id": user.id, "name": user.name, "age": user.age} for user in users]


# Update a User
@app.put("/users/")
async def update_user(user: dict, db: Session = Depends(get_db)):
    user_id = user.get("id")
    name = user.get("name")
    age = user.get("age")

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")

    db_user.name = name
    db_user.age = age
    db.commit()
    db.refresh(db_user)
    return {"message": "User updated successfully!", "user": {"id": db_user.id, "name": db_user.name, "age": db_user.age}}


# Delete a User
@app.delete("/users/")
async def delete_user(user: dict, db: Session = Depends(get_db)):
    user_id = user.get("id")

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")

    db_user.active = False
    db.commit()
    return {"message": "User deleted successfully!"}
