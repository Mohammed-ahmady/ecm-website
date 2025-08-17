# Railway Environment Variables Setup

## Required Environment Variables for Railway Deployment

Set these environment variables in your Railway project dashboard:

### Django Configuration
```
DEBUG=False
SECRET_KEY=your-super-secret-key-here-generate-a-new-one
DJANGO_SETTINGS_MODULE=ecm_website.settings
ALLOWED_HOSTS=*
```

### Database Configuration
Railway will automatically provide:
```
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### Cloudinary Configuration
```
CLOUDINARY_CLOUD_NAME=dr0r0hygs
CLOUDINARY_API_KEY=738811418858869
CLOUDINARY_API_SECRET=OViSfiTGDH8alwAG49i6lkzK-z8
CLOUDINARY_URL=cloudinary://738811418858869:OViSfiTGDH8alwAG49i6lkzK-z8@dr0r0hygs
```

### Domain Configuration (Update when you get your Railway domain)
```
CSRF_TRUSTED_ORIGINS=https://your-railway-app.railway.app,https://your-custom-domain.com
CORS_ALLOWED_ORIGINS=https://your-railway-app.railway.app,https://your-custom-domain.com
```

## How to Set Environment Variables in Railway:

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Variables" tab
4. Add each variable above

## Important Notes:

- Never commit real credentials to git
- The `.env` file is for local development only
- Railway will use environment variables instead of `.env` file
- All media files will be stored in Cloudinary, not Railway storage
- Database will be Railway's PostgreSQL, not SQLite
