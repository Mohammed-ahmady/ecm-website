# Deployment Checklist - ECM Website

## Environment Variables to Set in Railway

```
# Django Core Settings
DEBUG=False
SECRET_KEY=<generate-secure-random-string>
DJANGO_SETTINGS_MODULE=ecm_website.settings

# Database Configuration
# Railway will automatically provide this
# DATABASE_URL=postgres://...

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Domain and Security
ALLOWED_HOSTS=magiruscenter.me,www.magiruscenter.me,ecm-website-production-638d.up.railway.app,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://magiruscenter.me,https://www.magiruscenter.me,https://ecm-website-production-638d.up.railway.app
```

## Pre-Deployment Steps

1. Generate a proper SECRET_KEY for production:
```bash
# Using our provided script (Windows):
.\scripts\Fix-SecretKey.ps1

# Using our provided script (Linux/Mac):
python scripts/fix_secret_key.py

# Or manually in Python shell:
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

2. Run Django system checks:
```bash
python manage.py check --deploy
```

3. Test database migrations:
```bash
# Check migration status
python manage.py showmigrations

# Ensure no migrations are pending
python manage.py makemigrations --check

# Test migrations without applying them
python manage.py migrate --plan

# If you need to check for conflicts or issues:
python manage.py migrate --check
```

4. Test static files collection:
```bash
python manage.py collectstatic --noinput
```

5. Create cache table for database caching:
```bash
python manage.py createcachetable
```

## Deployment Commands for Railway

These commands will run automatically through the Railway platform:

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Collect static files:
```
python manage.py collectstatic --noinput
```

3. Apply migrations:
```
python manage.py migrate
```

4. Create cache table:
```
python manage.py createcachetable
```

5. Run gunicorn:
```
gunicorn ecm_website.wsgi:application
```

## Post-Deployment Verification

1. Check website loads correctly: https://magiruscenter.me/
2. Verify health check endpoint: https://magiruscenter.me/health/
3. Ensure static files are loading (images, CSS, JS)
4. Test core functionality:
   - Browse parts catalog
   - Search for parts
   - View part details
   - Add items to cart
   - Checkout process
5. Test admin panel: https://magiruscenter.me/admin/

## Rollback Procedures

If deployment fails or causes issues:

1. Check Railway logs for specific errors
2. Use Railway's rollback feature to revert to previous version
3. If database issues occur:
   - Check database migrations with `python manage.py showmigrations`
   - Consider restoring from backup if available
   - If schema changes can't be rolled back easily, use Django shell to fix data

4. Emergency fix for corrupted database:
   ```
   # If using a managed PostgreSQL database on Railway
   # 1. Connect to the database directly
   # 2. Execute repair commands or restore from backup
   ```

## Future Optimization Roadmap

1. Implement Redis caching instead of database caching
2. Add Sentry or similar error tracking
3. Set up CDN for static assets
4. Implement full test suite
5. Set up automated backups
6. Implement page-specific caching strategy
7. Optimize images further with WebP format
8. Set up monitoring alerts for site performance
9. Add comprehensive logging and analytics
