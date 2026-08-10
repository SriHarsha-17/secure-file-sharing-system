# Security Model

## Assets
- User plaintext files
- Encryption keys
- User identities
- Access-control decisions
- Share tokens
- Audit records

## Threats
- Unauthorized file access
- Server compromise
- File tampering
- Token guessing
- Expired-share reuse
- Brute-force authentication
- Session theft
- Malicious user

## Controls
- Browser-side AES-256-GCM encryption
- Random 96-bit GCM nonce
- Django password hashing
- Session authentication
- User-specific file permissions
- Expiring, limited-use random share tokens
- Revocation
- Audit logs
- HTTPS in deployment
- Security headers

## CIA mapping
Confidentiality: AES-GCM encryption and access control.
Integrity: AES-GCM authentication tag and file/hash verification.
Availability: controlled storage and application-level validation.
Authentication: Django authentication and optional TOTP MFA.
Authorization: per-file permissions and Secure Space membership.
Accountability: audit logs.

## Limitation
The demonstration implementation stores the client-side AES key in sessionStorage to make the educational flow easy to test. For a stronger production E2EE design, the key must be wrapped/encrypted for each authorized recipient using a public-key mechanism and must never be sent to the server in plaintext.
