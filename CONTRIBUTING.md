# Contributing

Thanks for improving AI Animation Director.

## Good Contributions

- New examples that use final user-facing output only.
- Better prompt modules that reduce character drift, style drift, or motion complexity.
- Platform adapters that avoid fake or unverified parameters.
- Validation checks for copy-block structure and manifest consistency.
- Documentation that makes installation and usage clearer.

## Adding Examples

Put examples in `ai-animation-director/examples/`.

Examples should:

- Use final output format.
- Avoid internal reasoning, `Project Packet`, or handoff notes.
- Include stable `IMG-*` and `VID-*` IDs for Jimeng-style examples.
- Keep failure fixes short and practical.

## Adding Platform Support

Platform support should preserve generic director language first, then add platform-specific adaptation. If a parameter, endpoint, or model ID is not verified, document it as unknown instead of inventing it.

## Secrets

Never commit API keys, cookies, session tokens, account credentials, generated private media, or `.env` files.
