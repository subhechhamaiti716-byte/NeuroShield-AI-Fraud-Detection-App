import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import settings
from api.deps import get_current_user
from models.user import User

router = APIRouter()

# Plaid configuration
# Note: In a real production app, you'd use a more robust client initialization
def get_plaid_client():
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox if settings.PLAID_ENV == 'sandbox' else plaid.Environment.Development,
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET,
        }
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)

@router.post("/create_link_token")
def create_link_token(current_user: User = Depends(get_current_user)):
    client = get_plaid_client()
    try:
        request = LinkTokenCreateRequest(
            products=[Products(p) for p in settings.PLAID_PRODUCTS.split(',')],
            country_codes=[CountryCode(c) for c in settings.PLAID_COUNTRY_CODES.split(',')],
            language='en',
            client_name=settings.PROJECT_NAME,
            user=LinkTokenCreateRequestUser(client_user_id=str(current_user.id))
        )
        response = client.link_token_create(request)
        return response.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exchange_public_token")
def exchange_public_token(public_token: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    client = get_plaid_client()
    try:
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(request)
        
        current_user.plaid_access_token = response['access_token']
        current_user.plaid_item_id = response['item_id']
        db.commit()
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/balance")
def get_balance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.plaid_access_token:
        # Fallback to current balance if bank not linked
        return {"balance": current_user.balance, "linked": False}
    
    client = get_plaid_client()
    try:
        request = AccountsBalanceGetRequest(access_token=current_user.plaid_access_token)
        response = client.accounts_balance_get(request)
        
        # Calculate total balance across all accounts returned by Plaid
        total_balance = sum(account['balances']['current'] for account in response['accounts'])
        
        # Update user balance in DB with the REAL value from bank
        current_user.balance = total_balance
        db.commit()
        
        return {"balance": total_balance, "linked": True}
    except Exception as e:
        # If Plaid fails (e.g. invalid token), return current DB balance
        return {"balance": current_user.balance, "linked": False, "error": str(e)}
