# Ruby on Rails Rules Reference

Use this when generating RULES.md for a Rails project.

## Detection

```ruby
# Gemfile
gem 'rails', '~> 7.1'
```

Also detect:
- `sidekiq` → background jobs
- `devise` → authentication
- `pundit` → authorization
- `rspec-rails` → test framework
- `factory_bot_rails` → test factories

## Tier 1: Universal Rails Rules (always include)

### BEFORE WRITING ANY CODE

1. READ the file you are about to modify
2. READ one sibling file to confirm patterns
3. SEARCH for existing concerns, helpers, services — NEVER duplicate
4. Check Rails conventions before inventing custom patterns

### Rails Conventions

- Convention over configuration — follow Rails way first
- Fat models, skinny controllers? NO — use service objects for business logic
- RESTful routes: `resources :users` — avoid custom routes unless necessary
- Strong parameters: `params.require(:user).permit(:name, :email)`
- Callbacks: only for simple model lifecycle (before_save). Complex logic → services
- Concerns: for shared model behavior. Don't overuse — prefer composition
- ActiveRecord: trust the ORM — raw SQL only for performance-critical queries

### Models

- Validations: `validates :field, presence: true` — at model level, not controller
- Scopes: `scope :active, -> { where(active: true) }` — for reusable queries
- Associations: always specify `dependent:` on has_many/has_one
- Indexes: add in migration for every foreign key and frequently queried column
- `enum` for status fields: `enum status: { pending: 0, active: 1, archived: 2 }`
- Avoid `default_scope` — use explicit scopes instead
- Soft deletes: use `discard` or `paranoia` gem, not custom columns

### Controllers

- One resource per controller
- Before actions for auth/loading: `before_action :authenticate_user!`
- Respond with proper status codes
- Never query database in views — do it in controller, pass via instance variables
- Flash messages for user feedback
- `redirect_to` after POST/PUT/DELETE (POST-redirect-GET pattern)

### Database

- `includes()` for eager loading — prevents N+1 (like Laravel's `with()`)
- `find_each` for batch processing — not `all.each`
- `exists?` not `count > 0`
- `pluck(:id)` instead of `map(&:id)` for single column
- Transactions: `ActiveRecord::Base.transaction { ... }`
- Migrations: never edit existing migrations — create new ones
- `add_index` in migrations for foreign keys

### Security

- Strong parameters on every controller action
- `has_secure_password` or Devise for authentication
- Pundit or CanCanCan for authorization — check on every action
- CSRF protection enabled (default) — don't skip
- SQL injection: use ActiveRecord methods, parameterize raw SQL
- Mass assignment: never `update(params)` without `permit`

### Testing

- RSpec preferred: `describe`, `context`, `it` structure
- Factory Bot for test data: `create(:user)`, `build(:user)`
- Request specs for API testing
- System specs (Capybara) for E2E
- `let` and `let!` for lazy/eager test data
- `shared_examples` for common behavior across specs
- Run with `bundle exec rspec`

### File Organization

```
app/
  controllers/
  models/
  views/
  services/          — business logic
  jobs/              — background jobs (Sidekiq)
  mailers/
  serializers/       — API response formatting
  policies/          — Pundit authorization
  validators/        — custom validators
lib/                 — shared utilities
spec/                — RSpec tests
config/              — configuration
db/migrations/       — database migrations
```

### Imports / Dependencies

- Gemfile: pin versions — `gem 'rails', '~> 7.1.0'`
- `require` only when needed — Rails autoloads `app/`
- Zeitwerk autoloading: follow file naming conventions strictly
- `app/services/user_creator.rb` → class `UserCreator`

### Background Jobs (if Sidekiq detected)

- Jobs in `app/jobs/` — inherit from `ApplicationJob`
- Idempotent: safe to retry
- Pass IDs not objects — serialize-friendly
- Set `retry` count and `dead` threshold
- Use queues: `default`, `mailers`, `low_priority`

## NEVER DO

- Skip validations with `save(validate: false)` in production code
- Use `update_column` to bypass callbacks (unless intentional + documented)
- Put business logic in controllers or views
- Commit `config/master.key` or `credentials.yml.enc` key
- Use `find_by_sql` when ActiveRecord can express the query
- Monkeypatch core classes in `config/initializers/`
