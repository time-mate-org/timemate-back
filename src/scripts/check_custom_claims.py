from firebase_admin import auth
from sqlmodel import select, Session
from database.models import User
from database.engine import engine

# pega o tenant_id de cada usuário no banco e seta como claim personalizada no Firebase
# user interno e do firebase são relacionados pelo uid
# criar primeiramente tenant, depois usuário (com tenant_id, pegar ou criar do firebase), depois rodar essa função para popular as claims no Firebase


async def check_user_custom_claims(uid: str):
    with Session(engine) as session:  # ← cria sessão diretamente
        for firebase_user in auth.list_users().iterate_all():

            if not firebase_user.uid == uid:
                print(f"firebase_user.uid: {firebase_user.uid} | uid: {uid}")
                continue

            claims = firebase_user.custom_claims or {}
            tenant_id = claims.get("tenant_id")
            if tenant_id:
                print(
                    f"User {firebase_user.email} already has tenant_id claim: {tenant_id}"
                )
                return tenant_id

            try:
                internal_user = session.exec(
                    select(User).where(User.uid == firebase_user.uid)
                ).first()

                if not internal_user:
                    print(f"No internal user found for {firebase_user.uid}. Skipping.")
                    continue

                tenant_id = str(internal_user.tenant_id)
                auth.set_custom_user_claims(firebase_user.uid, {"tenant_id": tenant_id})

                return tenant_id

            except Exception as e:
                print(f"✗ Error for {firebase_user.email}: {str(e)}")
