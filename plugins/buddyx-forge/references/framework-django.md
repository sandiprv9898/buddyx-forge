# Django + DRF Rules Reference

Use this when generating RULES.md for a Django project.

## Detection

```
# requirements.txt or pyproject.toml
django>=5.0
djangorestframework>=3.15
```

Also detect:
- `celery` → task queue present
- `django-filter` → filtering
- `drf-spectacular` → OpenAPI docs
- `pytest-django` → test framework

## Tier 1: Universal Django Rules (always include)

### BEFORE WRITING ANY CODE

1. READ the file you are about to modify
2. READ one sibling file to confirm patterns
3. SEARCH for existing mixins, utils, managers — NEVER duplicate
4. Check if feature belongs in existing app or needs a new one

### Django Models

- One model per logical entity — don't stuff unrelated fields
- Use `verbose_name` and `verbose_name_plural` on Meta
- Custom managers for common queries: `objects = CustomManager()`
- `__str__()` on every model — return meaningful representation
- Indexes: add `indexes` in Meta for frequently queried fields
- Soft deletes: use a mixin with `is_deleted` + `deleted_at`, not actual deletion
- Ordering: define `ordering` in Meta
- Validators: field-level for simple, `clean()` for cross-field

### Django Views / DRF

- Class-based views: `APIView` for custom logic, `ModelViewSet` for CRUD
- Serializers: one per use case (list vs detail vs create)
- Permissions: `permission_classes` on every view — never leave default
- Pagination: set `DEFAULT_PAGINATION_CLASS` in settings
- Filtering: use `django-filter` with `FilterSet`, not manual query params
- Throttling: configure rate limits for public endpoints

### Database

- `select_related()` for ForeignKey — prevents N+1
- `prefetch_related()` for ManyToMany / reverse FK — prevents N+1
- `only()` or `defer()` for large models — don't fetch unnecessary fields
- `exists()` not `count() > 0`
- `bulk_create()` / `bulk_update()` for batch operations
- Never raw SQL in views — use ORM or custom manager methods
- Transactions: `atomic()` for multi-step writes

### Security

- `ALLOWED_HOSTS` configured — never `['*']` in production
- CSRF protection enabled (default) — don't disable
- `@login_required` or DRF `IsAuthenticated` on every view
- Parameterized queries always — ORM handles this, but check raw SQL
- File uploads: validate type, size, sanitize filenames
- Secrets in environment variables, not settings.py

### Testing

- `pytest-django` preferred over unittest
- Factory Boy for test data — not manual `Model.objects.create()`
- Test at API level (integration) not just unit level
- Use `APIClient` for DRF tests
- Fixture files for complex setup: `conftest.py`
- `@pytest.mark.django_db` on tests that hit database

### File Organization

- One Django app per domain/feature
- `apps/{app_name}/` structure:
  - `models.py`, `views.py`, `serializers.py`, `urls.py`
  - `tests/`, `migrations/`, `admin.py`, `filters.py`
  - `services.py` for business logic (not in views)
  - `managers.py` for custom querysets
- Shared code in `core/` or `common/` app
- Settings split: `settings/base.py`, `settings/dev.py`, `settings/prod.py`

### Imports

- Group: stdlib → Django → third-party → local
- Absolute imports: `from apps.billing.models import Invoice`
- No circular imports between apps
- No wildcard imports

### Celery Rules (if Celery detected)

- Tasks in `tasks.py` per app
- `@shared_task` decorator — not `@app.task`
- Idempotent tasks: safe to retry
- Set `max_retries` and `default_retry_delay`
- Pass IDs not objects — serialize-friendly
- Error handling: `on_failure` callback or try/except with logging

## NEVER DO

- Put business logic in views — use services
- Use `Model.objects.all()` without filtering in views
- Commit `SECRET_KEY` or database credentials
- Use `print()` — use `logging` module
- Override `save()` for side effects — use signals or services
- Write raw SQL unless ORM cannot express the query
