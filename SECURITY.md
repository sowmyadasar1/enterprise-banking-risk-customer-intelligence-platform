# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅         |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do NOT** open a public GitHub issue.
2. Email the maintainer directly at the address listed in the repository.
3. Include a detailed description and steps to reproduce.

We will acknowledge your report within 48 hours and provide a fix timeline.

## Security Practices

- **API Authentication**: All prediction endpoints require an `X-API-Key` header.
- **Docker Security**: The API container runs as a non-root user (`apiuser`).
- **Secrets Management**: Environment variables are used for all credentials (never hardcoded).
- **Dependency Scanning**: We recommend enabling GitHub Dependabot for CVE monitoring.
- **No PII in Logs**: The structured logging middleware does not log request bodies containing personal data.
