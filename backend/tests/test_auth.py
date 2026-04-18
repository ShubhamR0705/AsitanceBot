from app.api.routes.auth import login, signup
from app.core.security import decode_access_token
from app.schemas.auth import LoginRequest, SignupRequest


def test_signup_and_login(db):
    signup_response = signup(
        SignupRequest(email="new.user@company.com", full_name="New User", password="StrongPass123!"),
        db,
    )
    assert signup_response.user.role.value == "USER"
    assert decode_access_token(signup_response.access_token)["sub"] == str(signup_response.user.id)

    login_response = login(LoginRequest(email="new.user@company.com", password="StrongPass123!"), db)
    assert login_response.user.email == "new.user@company.com"
    assert login_response.access_token
