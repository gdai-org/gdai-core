# gdai-core

Cross-cutting mechanics shared by GD.AI services: HTTP client, error taxonomy,
correlation id, logging, health and settings.

Design and rationale: [lq-api#115](https://github.com/GD-Artifical-Inteligence/lq-api/issues/115).

## Two rules it exists to enforce

- **`RequestPolicy.timeout` has no default.** A client cannot be constructed
  without choosing how long to wait.
- **`ServiceError` is abstract.** Raising it is a `TypeError`, so every failure
  has to say what it was.

Both close the same hole: a caught failure becoming a neutral value, so the
caller cannot tell "no data" from "the call failed". The two lead to opposite
decisions, so they must not share a return value.

## Usage

```python
from gdai_core import RequestPolicy, ServiceClient

client = ServiceClient(
    base_url="http://lq-api",
    service="lq-api",
    policy=RequestPolicy(timeout=5.0, retries=2),
    token_provider=provider,   # gdai-auth implements this
)

response = await client.get("/companies/internal/abc/billing")
```

Errors propagate. There is no `default=None` and no `or []`: degrading is
written at the call site by whoever accepts it.

Media and attachments do not go through JSON:

```python
media = await client.get_bytes("/attachments/1")   # media.content is bytes
await client.post("/upload", files={"image": ("photo.png", media.content, "image/png")})
```

`get_bytes` skips JSON parsing entirely — a `get` on an image would raise
`ServiceContractError`, correctly, because the body is not JSON. `Response.content`
carries the raw bytes on every response, so a caller that wants both does not
need a second response type.

```python
try:
    settings = await lq.get_billing_settings(company_id)
except ServiceTimeout:
    ...   # an explicit decision, visible in the diff
```

## Structure

| Piece | Kind |
|---|---|
| `Transport`, `TokenProvider`, `HealthProbe` | interface |
| `RequestPolicy`, `Response`, error hierarchy | data |
| `ServiceClient`, `ErrorEnvelope`, `HealthCheck`, `ServiceSettings` | logic |

Interfaces exist only at the seams where services legitimately differ. Everything
else is concrete, because uniformity is the point.

## What this package does not hold

Domain. No `Company`, no `Contact`. A shared domain model forces a redeploy of
every service on every change — the monolith again, distributed and worse,
because the coupling becomes invisible. The contract between services is the API
schema; typed clients live in the repo of the service that produces them.

## Consuming it

Built during the consumer's Docker build. No registry, and no credential ever
enters the image.

```yaml
- uses: actions/checkout@v4
  with:
    repository: GD-Artifical-Inteligence/gdai-core
    ref: v0.2.0        # never main
    path: gdai-core
```

```dockerfile
FROM python:3.12 AS libs
COPY gdai-core/ /src/gdai-core
RUN uv build /src/gdai-core --out-dir /wheels

FROM python:3.12
COPY --from=libs /wheels /wheels
RUN uv sync --frozen --find-links /wheels
```

The tag must be explicit. Checking out `main` would mean every service build
silently picks up the newest library — one change becoming a coordinated deploy
of seven services, with no diff for anyone to review.

## Official holidays of Brazil

Holidays are a calculation, not data (ADR-0036 in the workspace): `brazilian_holidays(year, state=None)`
and `brazilian_holidays_between(start, end, state=None)` return the national fixed holidays, the ones
that depend on Easter and, with a state (`"SP"`, `"rj"`), the civil holidays of that state. No network,
no clock: the same input always gives the same list, sorted by day, one holiday per day.

```python
from gdai_core import brazilian_holidays_between

for holiday in brazilian_holidays_between(date(2026, 2, 1), date(2026, 6, 30), state="SP"):
    holiday.day, holiday.name, holiday.scope, holiday.kind
```

- `scope` is `national` or `state`; when both fall on the same day the national one stays.
- `kind` is `holiday` or `optional`. Carnaval (Monday and Tuesday) and Corpus Christi are *ponto
  facultativo* in the federal calendar, so they come as `optional`: whether the company stops is the
  company's choice, made by whoever builds the calendar (company-api), not here.
- Dia Nacional de Zumbi e da Consciência Negra is national from 2024 (Lei 14.759/2023); before that it
  comes only for the states that had it.
- An unknown state raises `UnknownBrazilianState`; a range that ends before it starts raises
  `InvalidHolidayRange`.

Municipal holidays are out: they are thousands, and a company adds its own city's days as its days off.
The state table lives in `holidays.py`, `STATE_FIXED_HOLIDAYS`; a correction there is a minor release.

## Development

```bash
uv sync
uv run pytest
uv run ruff check src tests
uv run pyright src
```

`BLE001` and `TRY400` are enabled. This repo starts at zero blind excepts and
stays there; a broad catch needs an explicit `noqa` signed by whoever wrote it.
