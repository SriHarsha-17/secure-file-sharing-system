# Test Plan

## Functional tests
1. Register a new user.
2. Login with valid credentials.
3. Reject invalid credentials.
4. Upload a file.
5. Verify stored file is ciphertext.
6. Download ciphertext.
7. Decrypt in browser using the locally retained key.
8. Grant another user permission.
9. Reject unauthorized download.
10. Create a share token.
11. Verify token download.
12. Verify expired token is rejected.
13. Revoke token and verify rejection.
14. Create Secure Space.
15. Add and revoke members.
16. Enable MFA and verify OTP flow.

## Security tests
- Attempt unauthorized file download.
- Modify ciphertext and verify AES-GCM decryption fails.
- Guess random share tokens.
- Reuse an exhausted token.
- Test invalid/expired permissions.
- Test repeated failed logins.
- Run OWASP ZAP against the local application.
- Inspect HTTPS traffic with Wireshark in a TLS-enabled deployment.

## Performance tests
Measure:
- AES-GCM encryption time
- AES-GCM decryption time
- Upload latency
- Download latency
- API response time
- Storage overhead
- Concurrent-user behavior
