import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.errors import ErrorCode, error_envelope
from src.core.limiter import limiter
from src.routes import raffle_router as raffle
from src.routes import purchase_router as purchase
from src.routes import bank_account_route as bank_account

logger = logging.getLogger("patealaperola")

ALLOWED_ORIGINS = [o for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o]

app = FastAPI()

app.state.limiter = limiter


# Reemplaza el handler default de slowapi (que responde {"error": "..."},
# un formato distinto al resto de la API) para que un 429 también use el
# mismo sobre {"detail": {"code","message","context"}}.
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    response = JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": error_envelope(
                ErrorCode.RATE_LIMITED,
                "Demasiadas solicitudes. Intenta de nuevo en unos segundos.",
                context={"limit": str(exc.detail)},
            )
        },
    )
    return request.app.state.limiter._inject_headers(response, request.state.view_rate_limit)


app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# IMPORTANTE: este middleware debe registrarse ANTES que CORSMiddleware
# (eso lo deja más "adentro" en la pila real de Starlette). Antes, los
# errores 500 no controlados se manejaban con
# @app.exception_handler(Exception), pero FastAPI conecta ese handler a
# ServerErrorMiddleware, que queda FUERA de CORSMiddleware. Consecuencia
# real que vimos: al crear una rifa, un 500 sin controlar salía SIN
# headers CORS, y el navegador lo reportaba como "blocked by CORS
# policy" en vez de mostrar el verdadero error. Capturando la excepción
# aquí (adentro de CORSMiddleware) la respuesta sí sale con los headers
# correctos.
@app.middleware("http")
async def catch_unhandled_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logger.exception("Error no controlado en %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": error_envelope(ErrorCode.INTERNAL_ERROR, "Error interno del servidor")},
        )


app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # exc.detail ya viene como {"code","message","context"} cuando el error
    # se lanzó con ApiError (ver src/core/errors.py). Pero Starlette/FastAPI
    # también lanzan HTTPException por su cuenta con un detail de puro texto
    # (ej: 404 de ruta inexistente -> "Not Found", 405 -> "Method Not
    # Allowed"). Ese caso se normaliza aquí a la misma forma, para que el
    # frontend NUNCA tenga que manejar dos formatos distintos de error.
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        content = exc.detail
    else:
        content = error_envelope(f"HTTP_{exc.status_code}", str(exc.detail))
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": content},
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Reemplaza el 422 default de FastAPI (una lista suelta de errores en
    # "detail", sin "code" ni "message") por el mismo sobre unificado, con
    # los campos afectados en "context" para que el frontend pueda resaltar
    # el campo exacto en el formulario en vez de solo mostrar texto genérico.
    fields = [
        {
            "field": ".".join(str(p) for p in err["loc"] if p not in ("body", "query", "path")),
            "message": err["msg"],
            "type": err["type"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": error_envelope(
                ErrorCode.VALIDATION_ERROR,
                f"Error de validación en {len(fields)} campo(s).",
                context={"fields": fields},
            )
        },
    )


# El handler de Exception no controlada vive ahora en
# catch_unhandled_exceptions_middleware (arriba, antes de CORSMiddleware).
# @app.exception_handler(Exception) se quitó a propósito: FastAPI lo
# conecta a ServerErrorMiddleware, que queda fuera de CORS (ver comentario
# arriba) — tenerlo aquí también sería código muerto que nunca se ejecuta
# porque el try/except del middleware ya captura todo antes de llegar aquí.


app.include_router(raffle.router, prefix="/raffle", tags=["Raffle"])
app.include_router(purchase.router, prefix="/purchase", tags=["Purchase"])
app.include_router(bank_account.router, prefix="/bank-accounts", tags=["Bank Accounts"])


@app.get("/")
def root():
    return {"message": "Aplicación Patea la Perola iniciada exitosamente"}
