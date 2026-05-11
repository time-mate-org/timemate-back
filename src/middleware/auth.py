from fastapi import Request, Response
from sqlmodel import Session

from auth.firebase import get_current_user
from database import engine
from scripts.check_custom_claims import check_user_custom_claims

non_authentication_routes = [
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/send-mail/",
    "/tenants/subdomain/",
    "/services/tenant/",
]


async def authMiddleware(request: Request, call_next):
    try:
        if request.method == "OPTIONS":
            return await call_next(request)
        else:
            should_bypass_route = should_bypass_route = any(
                request.url.path.startswith(route)
                for route in non_authentication_routes
            )

            token = request.headers.get("Authorization")
            if not token and not should_bypass_route:
                raise Exception("Authorization token needed.")
            elif not token and should_bypass_route:
                return await call_next(request)

            credential = token.removeprefix("Bearer ")
            user = await get_current_user(
                credential
            )  # retorna dict do JWT decodificado

            if not user and not should_bypass_route:
                raise Exception("Invalid or expired token.")

            tenant_id = user.get("tenant_id")  # claims já estão no dict direto
            email = user.get("email")
            uid = user.get("uid")

            if not tenant_id:
                # seta o claim para o próximo token
                tenant_id = await check_user_custom_claims(uid)

            if not tenant_id:
                raise Exception(f"Tenant ID not found for user {email}.")

            request.state.user = user
            request.state.tenant_id = tenant_id
            request.state.email = email

            response = await call_next(request)

            # Depois da requisição
            return response

    except Exception as e:
        error = f"Auth middleware error: {str(e)}"
        print(error)
        return Response(content=error, status_code=500)
