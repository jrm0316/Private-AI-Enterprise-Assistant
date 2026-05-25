from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# =====================================================
# USUÁRIO FAKE (INICIAL)
# =====================================================

fake_users_db = {
    "admin@admin.com": {
        "email": "admin@admin.com",
        "hashed_password": pwd_context.hash("123456")
    }
}


# =====================================================
# VERIFICA SENHA
# =====================================================

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# =====================================================
# BUSCA USUÁRIO
# =====================================================

def get_user(email: str):

    if email in fake_users_db:
        return fake_users_db[email]

    return None