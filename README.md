# ECM Website - Magirus Parts E-commerce Platform

A modern Django-based e-commerce platform for selling Magirus truck parts with advanced features including cart management, inquiry system, and optimized memory management.

## 🚀 Features

- **Parts Catalog**: Browse and search Magirus truck parts by category and truck model
- **Shopping Cart**: Modern cart system with database persistence
- **Inquiry System**: Request quotes for specific parts
- **Admin Dashboard**: Comprehensive admin interface for managing parts and orders
- **Memory Optimized**: Optimized for development with ngrok tunneling
- **Responsive Design**: Modern UI with Tailwind CSS
- **Interactive Maps**: Contact page with location mapping

## 📁 Project Structure

```
ecm-website/
├── config/              # Deployment and configuration files
│   ├── Procfile
│   ├── runtime.txt
│   ├── nixpacks.toml
│   └── build.sh
├── docs/                # Documentation
│   ├── MEMORY_MANAGEMENT.md
│   └── NGROK_DEPLOYMENT_GUIDE.md
├── scripts/             # Helper scripts
│   ├── manage_memory.ps1
│   ├── memory_helper.bat
│   ├── run_django_optimized.py
│   ├── setup_ngrok_auth.bat
│   └── start_ngrok.bat
├── ecm_website/         # Main Django project
├── parts/               # Parts app
│   ├── utils.py         # Utility functions and cart logic
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   └── ...
├── templates/           # HTML templates
├── static/              # Static files
├── media/               # User uploaded files
└── requirements.txt     # Python dependencies
```

## 🛠️ Technology Stack

- **Backend**: Django 5.2.3
- **Database**: PostgreSQL (Aiven Cloud) / SQLite (local)
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Deployment**: Railway, ngrok for development
- **Memory Management**: Custom optimization scripts

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mohammed-ahmady/ecm-website.git
   cd ecm-website
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install  # For Tailwind CSS
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your database and secret key
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic
   ```

6. **Run development server**
   ```bash
   # Regular Django
   python manage.py runserver
   
   # Or with memory optimization
   python scripts/run_django_optimized.py
   ```

### With ngrok (for external access)

1. **Set up ngrok**
   ```bash
   scripts/setup_ngrok_auth.bat
   ```

2. **Start with ngrok**
   ```bash
   scripts/start_ngrok.bat
   ```

## 📚 Documentation

- [Memory Management Guide](docs/MEMORY_MANAGEMENT.md)
- [ngrok Deployment Guide](docs/NGROK_DEPLOYMENT_GUIDE.md)

## 🧪 Testing

```bash
python manage.py test
```

## 📦 Deployment

The project is configured for deployment on Railway with automatic deployments from the main branch.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, please check the documentation in the `docs/` directory or create an issue on GitHub.

---

**Built with ❤️ for the Magirus truck community**
