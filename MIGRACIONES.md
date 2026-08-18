# Migraciones de base de datos (Alembic)

Antes, cada modelo ejecutaba `Base.metadata.create_all()` al importarse: el
esquema se creaba solo, sin versionado y sin forma de aplicar un cambio de
tipo sobre datos existentes. Eso se reemplazó por Alembic.

## Instalación

```powershell
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y completa `DATABASE_URL`.

## Primera vez

### Caso A — La base de datos YA EXISTE (producción actual)

Las tablas ya están creadas, así que hay que marcar la migración baseline
como aplicada **sin ejecutarla**, y luego aplicar solo los cambios nuevos:

```powershell
alembic stamp 0001
alembic upgrade head
```

### Caso B — Base de datos nueva o vacía (local, staging)

```powershell
alembic upgrade head
```

## Qué hace cada migración

| Revisión | Contenido |
|----------|-----------|
| `0001` | Esquema inicial. Equivale a lo que creaba `create_all()`. |
| `0002` | `raffles.tickets_sold_list`: `text[]` → `integer[]`.<br>`bank_accounts.document_name` y `number_cta_1`: `float` → `varchar`.<br>`bank_accounts.is_active`: `NOT NULL DEFAULT false`.<br>Índices en `purchases(raffle_id)` y `purchases(buyer_email)`. |

`0002` convierte los datos existentes con `USING`, no los borra. Es
reversible con `alembic downgrade 0001`.

## Antes de aplicar 0002 en producción

1. **Respaldo de la base de datos.** La conversión de tipos no es destructiva,
   pero es un ALTER sobre tablas con datos.
2. **Revisar la numeración de boletos.** La reserva ahora respeta
   `raffles.total_tickets` y emite números en el rango `0 .. total_tickets-1`.
   Antes sorteaba siempre en `0..9998` ignorando ese campo. Consulta si hay
   rifas activas con boletos vendidos fuera de su propio rango:

   ```sql
   SELECT id, title, total_tickets,
          (SELECT count(*) FROM unnest(tickets_sold_list) t WHERE t >= total_tickets) AS fuera_de_rango
   FROM raffles
   WHERE raffle_status = 1;
   ```

   Si alguna devuelve `fuera_de_rango > 0`, ajusta su `total_tickets` antes de
   desplegar; si no, el inventario disponible se verá más chico de lo real.

## Cambios futuros

```powershell
alembic revision --autogenerate -m "descripcion del cambio"
alembic upgrade head
```

`migrations/env.py` importa el `Base` único y todos los modelos, así que
`--autogenerate` ve el esquema completo.

## Pruebas

Las pruebas necesitan una base de datos **de pruebas** (nunca la de
producción):

```powershell
$env:DATABASE_URL="postgresql://postgres@localhost:5432/plp_test"
$env:DB_SSLMODE="disable"
$env:API_JWT_SECRET="cualquier-secreto-de-pruebas"
pytest tests/ -v
```
