# Documentation Index

## Getting Started

1. **[README.md](README.md)** - Start here
   - Quick start guide
   - Project overview
   - Installation steps
   - Basic usage

2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Developer cheat sheet
   - Common commands
   - Code templates
   - Quick patterns
   - Troubleshooting

## Core Documentation

3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design
   - Folder structure explained
   - Layer responsibilities
   - Request flow
   - Design patterns

4. **[SECURITY.md](SECURITY.md)** - Security practices
   - Environment variables
   - Authentication & authorization
   - Deployment checklist
   - Security monitoring

## Detailed Guides

5. **[docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)** - API reference
   - All endpoints documented
   - Request/response examples
   - Authentication details
   - Error codes

6. **[docs/TESTING.md](docs/TESTING.md)** - Testing guide
   - Test structure
   - Running tests
   - Writing tests
   - Fixtures & mocking

7. **[docs/MESSAGING.md](docs/MESSAGING.md)** - Async messaging
   - RabbitMQ setup
   - Sending messages
   - Priority queues
   - Examples

8. **[docs/NAMING_CONVENTIONS.md](docs/NAMING_CONVENTIONS.md)** - Code standards
   - Naming rules
   - File organization
   - Best practices
   - Examples

## Configuration

9. **[.env.example](.env.example)** - Environment template
   - All configuration options
   - Example values
   - Required vs optional

10. **[docs/init_db.sql](docs/init_db.sql)** - Database schema
    - Table definitions
    - Initial setup
    - SQL scripts

## Quick Navigation

### For New Developers
1. Read [README.md](README.md)
2. Follow setup in [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. Review [ARCHITECTURE.md](ARCHITECTURE.md)
4. Check [docs/NAMING_CONVENTIONS.md](docs/NAMING_CONVENTIONS.md)

### For Adding Features
1. Review [ARCHITECTURE.md](ARCHITECTURE.md) - Understand layers
2. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Code templates
3. Follow [docs/NAMING_CONVENTIONS.md](docs/NAMING_CONVENTIONS.md) - Standards
4. Write tests per [docs/TESTING.md](docs/TESTING.md)

### For API Integration
1. Read [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
2. Check [SECURITY.md](SECURITY.md) - Authentication
3. Review [docs/MESSAGING.md](docs/MESSAGING.md) - Async communication

### For Deployment
1. Review [SECURITY.md](SECURITY.md) - Deployment checklist
2. Configure [.env.example](.env.example) - Environment
3. Run [docs/init_db.sql](docs/init_db.sql) - Database setup

## File Organization

```
catalog-service/
├── README.md                    # Start here
├── QUICK_REFERENCE.md           # Developer cheat sheet
├── ARCHITECTURE.md              # System design
├── SECURITY.md                  # Security practices
├── .env.example                 # Configuration template
├── docs/
│   ├── API_DOCUMENTATION.md     # API reference
│   ├── TESTING.md               # Testing guide
│   ├── MESSAGING.md             # Async messaging
│   ├── NAMING_CONVENTIONS.md    # Code standards
│   └── init_db.sql              # Database schema
└── app/                         # Source code
```

## Documentation Maintenance

### When to Update

- **README.md**: New features, setup changes
- **ARCHITECTURE.md**: Structural changes, new patterns
- **SECURITY.md**: Security updates, new practices
- **API_DOCUMENTATION.md**: New endpoints, changed responses
- **TESTING.md**: New test patterns, fixtures
- **MESSAGING.md**: Messaging changes, new patterns
- **NAMING_CONVENTIONS.md**: New standards, conventions

### How to Contribute

1. Keep documentation in sync with code
2. Update examples when changing implementation
3. Add new sections for new features
4. Keep language clear and concise
5. Include code examples where helpful

## Additional Resources

- Interactive API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Source code: `app/` directory
- Tests: `tests/` directory
