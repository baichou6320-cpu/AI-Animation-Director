# Security Policy

## Supported Versions

The project is pre-1.0. Security fixes apply to the latest commit on `main` until versioned releases are established.

## Secrets And Credentials

Do not commit:

- API keys
- Cookies
- Session tokens
- Account credentials
- `.env` files
- Generated private media

The Jimeng-compatible execution layer must read credentials only from environment variables.

## Reporting A Vulnerability

Open a private security advisory if the repository is hosted on GitHub and advisories are enabled. Otherwise, contact the maintainer through the GitHub profile associated with the repository.

Please include:

- Affected file or workflow
- Reproduction steps
- Whether secrets, generated media, or user credentials could be exposed
- Suggested fix, if known

## Scope

In scope:

- Credential leakage in scripts, manifests, examples, docs, or logs
- Unsafe default handling of API keys or session tokens
- Validation gaps that could allow secrets or generated media to be committed

Out of scope:

- Vulnerabilities in third-party AI image/video platforms
- Prompt output quality issues without a security impact
- Unverified provider endpoint behavior outside this repository
