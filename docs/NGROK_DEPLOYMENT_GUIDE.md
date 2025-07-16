# ECM Website - ngrok Deployment Guide

## 🚀 Your Django app is ready for ngrok deployment!

### Prerequisites ✅
- [x] Django application configured for ngrok
- [x] SQLite database set up (for demo purposes)
- [x] Static files collected
- [x] Admin user created (username: admin)
- [x] ngrok installed

### Quick Start Steps:

#### 1. Set up ngrok authentication
1. Go to https://ngrok.com/ and sign up for a FREE account
2. After signing up, go to https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy your auth token
4. Open PowerShell and run:
   ```powershell
   & "$env:USERPROFILE\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" config add-authtoken YOUR_TOKEN_HERE
   ```
   (Replace YOUR_TOKEN_HERE with your actual token)

#### 2. Start your Django server (if not already running)
```powershell
& "C:/Program Files/Python313/python3.13t.exe" manage.py runserver 127.0.0.1:8000
```

#### 3. Start ngrok tunnel
Open a NEW PowerShell window and run:
```powershell
& "$env:USERPROFILE\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" http 8000
```

Or simply double-click the `start_ngrok.bat` file in your project folder.

#### 4. Access your website
ngrok will show you a public URL like: `https://abc123.ngrok-free.app`
Your ECM website will be accessible worldwide at that URL!

### What's configured:
- ✅ **ALLOWED_HOSTS**: Updated to accept ngrok URLs
- ✅ **Database**: SQLite for demo (easily portable)
- ✅ **Static Files**: Collected and ready
- ✅ **Admin Panel**: Available at /admin (username: admin)
- ✅ **Media Files**: Configured for uploads
- ✅ **Two-column Layout**: With thumbnails left of main image
- ✅ **Enhanced Models**: TruckModel with images and descriptions

### Admin Access:
- URL: `https://your-ngrok-url.ngrok-free.app/admin`
- Username: `admin`
- Password: (the one you set during superuser creation)

### Important Notes:
- 🔒 Free ngrok tunnels are temporary and will change on restart
- 🌐 The tunnel will be public and accessible to anyone with the URL
- ⏰ ngrok free tier has session limits
- 🔄 You can restart the tunnel anytime by running ngrok again

### Production Tip:
When ready for permanent hosting, you can easily switch back to PostgreSQL by:
1. Uncommenting the PostgreSQL configuration in settings.py
2. Installing psycopg2-binary
3. Setting up your production database

### Troubleshooting:
- If you get ALLOWED_HOSTS errors, the ngrok URL patterns are already configured
- If static files don't load, run `python manage.py collectstatic` again
- If you need to add data, use the admin panel at /admin

🎉 **Your ECM website is ready to go live with ngrok!**
