# Security

## Secrets

Do not open an issue or commit a file containing:

- Meshy API keys;
- GitHub tokens;
- cloud credentials;
- private model download URLs;
- personal access information.

Use environment variables or the operating system keychain. `meshy2bambu` expects the Meshy API
key in `MESHY_API_KEY` and does not need the key stored in the repository.

If a credential is committed accidentally, revoke it at the provider immediately, remove it from
Git history, and rotate any related credentials.
