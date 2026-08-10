# HTTPS deployment checklist

For a real deployment:
- Serve Django behind a production WSGI/ASGI server.
- Put Nginx or another reverse proxy in front.
- Use a valid TLS certificate.
- Set DEBUG=False.
- Set ALLOWED_HOSTS.
- Set SESSION_COOKIE_SECURE=True.
- Set CSRF_COOKIE_SECURE=True.
- Configure HSTS only after confirming HTTPS works.
- Keep database credentials in environment variables.
- Do not commit `.env`.
- Store uploaded ciphertext outside publicly accessible directories.
- Back up database and encrypted files separately.
