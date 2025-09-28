import bcrypt
from main_users import security
from fastapi import HTTPException, Depends

def verify_admin(token:str = Depends(security.access_token_required)):
    decoded_token = security._decode_token(token)
    
    role = decoded_token._get_value("role")

    if role == "Admin":
        return True
    else:
        return False