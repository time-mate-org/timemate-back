from fastapi import Request, Response

from auth.firebase import get_current_user

non_authentication_routes = [
    '/docs',
    '/redoc',
    '/openapi.json'
]


async def authMiddleware(request: Request, call_next):
    try:
        if request.method == 'OPTIONS':
            return await call_next(request)
        else:
            should_bypass_route = request.url.path in non_authentication_routes

            token = request.headers.get("Authorization")
            if not token and not should_bypass_route:
                raise Exception("Authorization token needed.")

            user = get_current_user(token)
            if not user and not should_bypass_route:
                raise Exception("Invalid or expired token.")

            response = await call_next(request)

            # Depois da requisição
            return response

    except Exception as e:
        error = f"Auth middleware error: {str(e)}"
        print(error)
        return Response(
            content=error,
            status_code=500
        )
