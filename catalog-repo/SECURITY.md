# Security Best Practices

## Environment Variables

### Setup
1. Copy `.env.example` to `.env`
2. Replace all placeholder values with actual credentials
3. **NEVER commit `.env` to version control** (protected by .gitignore)

### Sensitive Data
- `DATABASE_URL`: Contains database password
- `JWT_SECRET_KEY`: Must be strong random string (32+ chars)
- `REDIS_URL`: Contains Redis password
- `RABBITMQ_URL`: Contains RabbitMQ credentials

### Production
- Use secrets management (AWS Secrets Manager, Vault, Kubernetes secrets)
- Rotate credentials regularly
- Enable SSL/TLS for all connections

## Authentication & Authorization

### External Auth Service
- All authentication delegated to external service
- Automatic retry with exponential backoff (3 attempts, 5s timeout)
- Returns 503 if auth service unavailable

### RBAC
- **user**: Read-only access
- **admin**: Full CRUD access
- JWT tokens via `Authorization: Bearer <token>` header

## Infrastructure Security

### Rate Limiting
- Default: 60 requests per minute per IP
- Configurable via `RATE_LIMIT_PER_MINUTE`
- Returns 429 when exceeded

### CORS
- Whitelist specific origins in `CORS_ORIGINS`
- Never use `["*"]` in production

### Database
- Connection pooling prevents exhaustion attacks
- Parameterized queries prevent SQL injection
- Never concatenate user input into SQL

### Logging
- All write operations logged with user_id
- Sensitive data excluded from logs
- Separate audit and error logs

## Deployment Checklist

- [ ] Change `JWT_SECRET_KEY` to strong random value
- [ ] Update `DATABASE_URL` with production credentials
- [ ] Configure `REDIS_URL` with production instance
- [ ] Update `CORS_ORIGINS` with production URLs
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR`
- [ ] Enable SSL/TLS for database, Redis, RabbitMQ
- [ ] Configure log rotation
- [ ] Set up monitoring for `/health` endpoint
- [ ] Enable firewall rules
- [ ] Set up automated database backups
- [ ] Configure secrets management

## Dependency Security

```bash
# Check for vulnerabilities
pip install safety
safety check

# Update dependencies
pip list --outdated
```

## Monitoring

- Monitor `/health` endpoint for infrastructure status
- Set up alerts for error rates
- Track audit logs for suspicious activity
- Monitor rate limit violations
