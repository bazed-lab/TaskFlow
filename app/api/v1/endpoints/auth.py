from fastapi import APIRouter

auth_router = APIRouter()

@auth_router.get('/signup')
def signup():
    pass

@auth_router.get('/login')
def login():
    pass