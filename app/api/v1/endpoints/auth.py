from fastapi import APIRouter

auth_router = APIRouter()

@auth_router.get('/auth/signup')
def signup():
    pass

@auth_router.get('/auth/login')
def login():
    pass