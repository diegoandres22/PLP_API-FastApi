# Base de datos: proveedor, conexión y puesta en marcha

## Qué necesita realmente esta API

Una sola variable: **`DATABASE_URL`**.

La API se conecta a Postgres directo con SQLAlchemy. **No usa el SDK de
Supabase.** Por eso `SUPABASE_URL`, `SUPABASE_KEY`, `ANON_KEY` y
`SERVICE_ROLE_KEY` no hacen falta: añadirlas solo sería acumular secretos que
nadie lee y que habría que rotar. En este proyecto:

| Función | Quién la cubre |
|---|---|
| Base de datos | Postgres (cualquier proveedor) vía `DATABASE_URL` |
| Almacenamiento de comprobantes | Google Cloud Storage |
| Autenticación del panel | NextAuth (Google) + JWT propio hacia la API |

Cambiar de proveedor de base de datos es, literalmente, cambiar una línea
del `.env`.

---

## Poner en marcha una base nueva

### Opción A — con el repositorio (recomendada)

```powershell
# 1. Configura la conexión
copy .env.example .env
#    edita .env y pega tu DATABASE_URL

# 2. Crea el esquema
pip install -r requirements.txt
alembic upgrade head

# 3. Comprueba que todo responde
python scripts/verificar_conexion.py
```

### Opción B — sin Python, desde el editor SQL del proveedor

Pega y ejecuta el contenido de **`db/esquema_completo.sql`**. Crea las tres
tablas con los tipos ya corregidos y deja la base sellada en la revisión
`0002`, de modo que un `alembic upgrade head` posterior no intente reaplicar
nada.

---

## Notas por proveedor

### Neon

- Copia la cadena de conexión desde *Dashboard → Connection Details*.
- Neon ofrece dos cadenas: la **pooled** (contiene `-pooler` en el host) y la
  **directa**. Para esta API funcionan ambas; si alguna migración diera
  problemas, usa la directa para `alembic` y la pooled para la aplicación.
- Deja `DB_SSLMODE=require`.
- El cómputo se suspende tras unos minutos de inactividad y la primera
  consulta lo despierta. Eso puede tardar. `create_engine` ya está
  configurado con `pool_pre_ping=True`, así que la reconexión es transparente
  y no hay que tocar nada.

### Supabase

La cadena está en *Project Settings → Database → Connection string*. Supabase
ofrece **tres** y elegir mal es la causa nº1 de que "no conecta":

| Opción | Host / puerto | Cuándo usarla |
|---|---|---|
| **Direct connection** | `db.<ref>.supabase.co:5432` | Solo si tu red tiene **IPv6**. Sin IPv6 hay que pagar el add-on de IPv4. |
| **Session pooler** | `aws-0-<región>.pooler.supabase.com:5432` | **La que debes usar en redes IPv4** (la mayoría). Válida en todos los planes. |
| **Transaction pooler** | `...pooler.supabase.com:6543` | Serverless / edge. **No soporta prepared statements**: no la uses para migraciones. |

Para este proyecto: **usa la del Session pooler**. Funciona tanto para
`alembic upgrade head` como para la API en marcha.

Si copias la directa desde una red IPv4 verás errores del tipo
`could not translate host name` o `Network is unreachable`, aunque la
contraseña sea correcta.

Otros puntos:

- `DB_SSLMODE=require`.
- La cadena trae un literal `[YOUR-PASSWORD]`: hay que sustituirlo por la
  contraseña real (y codificarla si lleva caracteres especiales).
- **Atención al plan gratuito:** el proyecto se pausa tras 7 días sin
  actividad en la base de datos y hay que reactivarlo a mano desde el panel.
  Para un sitio publicado esto no es viable; o se sube a Pro o se usa otro
  proveedor.

### Render / RDS / Postgres local

- Igual: `DATABASE_URL` y `DB_SSLMODE`.
- En local, `DB_SSLMODE=disable`.

---

## Fallos habituales

**`password authentication failed` con la contraseña correcta.**
Casi siempre es la contraseña sin codificar en la URL. Si contiene `@`, `:`,
`/`, `?`, `#` o `%`, hay que escaparla:

```python
from urllib.parse import quote_plus
print(quote_plus("mi:contraseña@rara"))   # mi%3Acontrase%C3%B1a%40rara
```

**`could not translate host name`.**
El proyecto está pausado o borrado: el DNS del host deja de resolver.

**`SSL connection required`.**
Falta `DB_SSLMODE=require`.

**`relation "raffles" does not exist`.**
La base está vacía: falta `alembic upgrade head`.

---

## Cambiar de proveedor sin perder datos

```powershell
# 1. Volcado del origen (esquema + datos)
pg_dump "$ORIGEN_DATABASE_URL" --no-owner --no-privileges -f respaldo.sql

# 2. Carga en el destino
psql "$DESTINO_DATABASE_URL" -v ON_ERROR_STOP=1 -f respaldo.sql

# 3. Actualiza .env y verifica
python scripts/verificar_conexion.py
```

Si el origen está pausado hay que reactivarlo antes: no se puede volcar una
base apagada.

---

## Qué comprueba `scripts/verificar_conexion.py`

1. Que `DATABASE_URL` existe y avisa si se conecta a un host remoto sin SSL.
2. Que la conexión se establece, con la latencia y la versión del servidor.
3. Que están las tres tablas (`raffles`, `purchases`, `bank_accounts`).
4. En qué revisión de Alembic está la base.
5. Que los tipos críticos son los correctos: `tickets_sold_list` como
   `integer[]` y los identificadores bancarios como texto. Estos tres tipos
   fueron la causa del bug de boletos revendidos y de la pérdida de dígitos
   en cédulas y números de cuenta; si una base se creó con el esquema viejo,
   este chequeo lo detecta.
6. Cuántas filas hay en cada tabla.

Nunca imprime la contraseña.
