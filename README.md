# Binis Invoices

A full-stack invoice management system that automates order processing and invoice generation through integration with the Livecis platform.

## Overview

Binis Invoices is a web application designed to streamline invoice creation and order management. It features:
- Real-time order fetching and product registration
- Automated invoice generation via browser automation (Playwright)
- Product and brand management
- Secure user authentication with Django REST Framework tokens
- Modern, responsive frontend built with React and TypeScript

## Tech Stack

### Backend
- **Framework**: Django 4.x with Django REST Framework
- **Language**: Python 3.12
- **Database**: PostgreSQL
- **Automation**: Playwright (for invoice generation)
- **Server**: Gunicorn
- **Containerization**: Docker

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Fetch API with EventSource for streaming

### DevOps
- Docker & Docker Compose for containerization
- Gunicorn WSGI application server

## Project Structure

```
.
├── backend/                           # Django application
│   ├── apps/
│   │   └── binis_invoices/           # Main app
│   │       ├── models.py             # Database models
│   │       ├── views.py              # API endpoints
│   │       ├── urls.py               # URL routing
│   │       ├── InvoiceMaker.py       # Playwright automation
│   │       ├── DataFetcher.py        # Order/product data fetching
│   │       ├── ProductsRegister.py   # Product registration
│   │       └── migrations/           # Database migrations
│   ├── config/                       # Django settings
│   │   ├── settings/
│   │   │   ├── base.py              # Base settings
│   │   │   ├── dev.py               # Development settings
│   │   │   └── prod.py              # Production settings
│   │   ├── urls.py                  # Main URL config
│   │   └── wsgi.py
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── create_admin.py              # Admin user creation
│
├── frontend/                         # React application
│   ├── src/
│   │   ├── pages/                   # Route pages
│   │   │   ├── Login.tsx
│   │   │   ├── Orders.tsx
│   │   │   └── ProductsOfOrder.tsx
│   │   ├── components/              # Reusable components
│   │   │   └── OrderRow.tsx
│   │   ├── App.tsx
│   │   ├── Layout.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── vercel.json
│
├── docker-compose.yml               # Multi-container orchestration
├── .env                             # Environment variables (local)
└── db.sqlite3                       # Development database
```

## Prerequisites

- **Docker** & **Docker Compose** (recommended for development)
- **Python 3.12** (if running locally)
- **Node.js 18+** (if running frontend locally)
- **PostgreSQL** (or use Docker)

## Installation & Setup

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Binis_Invoices
   ```

2. **Create/verify `.env` file** in project root with required variables:
   ```env
   DJANGO_SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:password@db:5432/binis_db
   CIS_NAME=your-livecis-username
   CIS_PASSWD=your-livecis-password
   EMP_NAME=your-company-name
   EMP_PASSWD=your-password
   USERNAME=admin_username
   EMAIL=admin@example.com
   PASSWORD=admin_password
   ```

3. **Build and start containers**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

### Option 2: Local Development

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run migrations
python manage.py migrate

# Create admin user
python create_admin.py

# Start development server
python manage.py runserver
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key for security | `your-random-secret-key` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost/db` |
| `CIS_NAME` | Livecis platform username | `username` |
| `CIS_PASSWD` | Livecis platform password | `password123` |
| `EMP_NAME` | Employee/company name | `username` |
| `EMP_PASSWD` | Employee password | `password123` |
| `USERNAME` | Django admin username | `admin` |
| `EMAIL` | Django admin email | `admin@example.com` |
| `PASSWORD` | Django admin password | `password123` |

## Running the Application

### Docker Compose
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Local Development
```bash
# Terminal 1: Backend
cd backend
python manage.py runserver

# Terminal 2: Frontend
cd frontend
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login (returns token)

### Orders
- `GET /binis_invoices/get_orders/` - Fetch all orders
- `GET /binis_invoices/get_products_of_order/<order_id>/` - Get products for an order

### Invoice Generation
- `POST /binis_invoices/store_extraction_data/` - Store extraction data
- `GET /binis_invoices/extract_invoice/<session_id>/` - Stream invoice generation (Server-Sent Events)

### Product Registration
- `POST /binis_invoices/store_register_data/` - Store product registration data
- `GET /binis_invoices/register_products/<session_id>/` - Stream product registration

## Key Features

### Invoice Automation
- Automated browser automation using Playwright
- Real-time order extraction from Livecis platform
- Invoice generation with batch product handling
- Screenshot capture of generated invoices

### Product Management
- Brand registration and updates
- Product code validation
- Unregistered product tracking

### Authentication & Security
- Token-based authentication
- Permission-based access control
- CORS support for cross-origin requests

### Streaming Response
- Server-Sent Events (SSE) for real-time progress updates
- Live feedback on invoice/product registration status

## Development Notes

### Browser Automation (Playwright)
- Chromium browser launched in headless mode with sandbox disabled for Docker
- 15-second timeout for page operations to prevent hanging
- Graceful error handling and resource cleanup

### Gunicorn Configuration
- 120-second worker timeout (allows time for invoice generation)
- 2 workers with 2 threads each
- Max 100 requests per worker to prevent memory leaks

### Database Migrations
```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migration status
python manage.py showmigrations
```

### Admin Interface
Access the Django admin at `/admin/` with your admin credentials to manage:
- Users
- Orders
- Products
- Brands

## Troubleshooting

### Gunicorn Worker Timeout
If you encounter `WORKER TIMEOUT` errors:
- Increase `--timeout` value in Docker Gunicorn command
- Check browser automation performance
- Verify Livecis platform availability

### Browser Connection Issues
- Ensure Playwright chromium is installed: `playwright install chromium`
- Verify Livecis credentials in `.env`
- Check network connectivity to livecis.gr

### Database Connection
- Verify PostgreSQL is running
- Check `DATABASE_URL` format
- Ensure user has correct permissions

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and test locally
3. Commit with clear messages: `git commit -m "Add feature description"`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

See LICENSE file for details.

## Support

For issues and questions, please open an issue in the repository or contact the development team.
