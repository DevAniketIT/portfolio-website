# FastAPI Job Tracker

A modern, secure REST API for tracking job applications built with FastAPI, PostgreSQL, and JWT authentication.

## Features

- **User Authentication**: Secure JWT-based authentication with bcrypt password hashing
- **Job Application Management**: Full CRUD operations for job applications
- **Filtering & Pagination**: Filter by status, company, and paginate results
- **Statistics Dashboard**: Get insights into your job applications
- **Modern Architecture**: Built with FastAPI, SQLAlchemy, and Pydantic
- **Production Ready**: Containerized with Docker, deployable on Render.com

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Authentication**: JWT tokens with passlib bcrypt
- **Validation**: Pydantic models
- **Testing**: Pytest
- **Deployment**: Docker, Render.com

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/verify-token` - Verify token validity

### Job Applications
- `POST /api/v1/jobs/` - Create new job application
- `GET /api/v1/jobs/` - Get job applications (with filtering & pagination)
- `GET /api/v1/jobs/{id}` - Get specific job application
- `PUT /api/v1/jobs/{id}` - Update job application
- `DELETE /api/v1/jobs/{id}` - Delete job application
- `PATCH /api/v1/jobs/{id}/status` - Update application status
- `GET /api/v1/jobs/stats/summary` - Get application statistics

### System
- `GET /` - API information
- `GET /health` - Health check

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (for production) or SQLite (for development)
- Git

### Local Development

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd fastapi-job-tracker
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file:
```env
DATABASE_URL=sqlite:///./jobtracker.db
SECRET_KEY=your-super-secret-key-here
DEBUG=True
```

5. **Run the application**
```bash
python main.py
```

The API will be available at `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Using Docker

1. **Build the image**
```bash
docker build -t fastapi-job-tracker .
```

2. **Run the container**
```bash
docker run -p 8000:8000 -e DATABASE_URL=sqlite:///./app.db fastapi-job-tracker
```

## Testing

Run the test suite:
```bash
pytest test_main.py -v
```

## Deployment on Render.com

### Step 1: Prepare Your Repository
1. Push your code to GitHub/GitLab
2. Ensure `render.yaml` is in the root directory

### Step 2: Create Render Account
1. Sign up at [render.com](https://render.com)
2. Connect your GitHub/GitLab account

### Step 3: Deploy Database
1. Go to Render Dashboard
2. Click "New" → "PostgreSQL"
3. Configure:
   - Name: `job-tracker-db`
   - Database Name: `jobtracker`
   - User: `jobtracker_user`
   - Region: Choose closest to your users
4. Click "Create Database"

### Step 4: Deploy Web Service
1. Click "New" → "Web Service"
2. Connect your repository
3. Configure:
   - Name: `fastapi-job-tracker`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variables:
   - `DATABASE_URL`: Link to your PostgreSQL database
   - `SECRET_KEY`: Generate a secure key
   - `DEBUG`: `False`
   - `ALGORITHM`: `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
5. Click "Create Web Service"

### Step 5: Custom Domain (Optional)
1. In your web service settings
2. Go to "Custom Domains"
3. Add your domain and configure DNS

## Usage Examples

### Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \\
     -H "Content-Type: application/json" \\
     -d '{
       "email": "user@example.com",
       "full_name": "John Doe",
       "password": "securepassword123"
     }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \\
     -H "Content-Type: application/json" \\
     -d '{
       "email": "user@example.com",
       "password": "securepassword123"
     }'
```

### Create Job Application
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/" \\
     -H "Content-Type: application/json" \\
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
     -d '{
       "title": "Senior Software Engineer",
       "company": "Tech Corp",
       "description": "Full-stack development role",
       "location": "San Francisco, CA",
       "salary_range": "$120k - $180k",
       "job_url": "https://techcorp.com/careers/senior-engineer",
       "status": "applied"
     }'
```

### Get Job Applications with Filtering
```bash
# Get all applications
curl -X GET "http://localhost:8000/api/v1/jobs/" \\
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by status
curl -X GET "http://localhost:8000/api/v1/jobs/?status=interviewing" \\
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by company
curl -X GET "http://localhost:8000/api/v1/jobs/?company=Google" \\
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Pagination
curl -X GET "http://localhost:8000/api/v1/jobs/?page=1&per_page=10" \\
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Data Models

### User
- `id`: Integer (Primary Key)
- `email`: String (Unique)
- `full_name`: String
- `hashed_password`: String
- `is_active`: Boolean
- `created_at`: DateTime
- `updated_at`: DateTime

### Job Application
- `id`: Integer (Primary Key)
- `title`: String
- `company`: String
- `description`: Text (Optional)
- `location`: String (Optional)
- `salary_range`: String (Optional)
- `job_url`: String (Optional)
- `status`: Enum (applied, interviewing, rejected, offer, accepted, withdrawn)
- `applied_date`: DateTime
- `notes`: Text (Optional)
- `contact_person`: String (Optional)
- `contact_email`: Email (Optional)
- `owner_id`: Integer (Foreign Key)
- `created_at`: DateTime
- `updated_at`: DateTime

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | sqlite:///./test.db |
| `SECRET_KEY` | JWT secret key | Yes | your-secret-key-here |
| `ALGORITHM` | JWT algorithm | No | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | No | 30 |
| `DEBUG` | Enable debug mode | No | True |

## Security Features

- Password hashing with bcrypt
- JWT tokens with expiration
- CORS middleware configured
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy
- Authentication required for all job operations

## Performance Considerations

- Database indexes on frequently queried fields
- Pagination for large datasets
- Connection pooling with SQLAlchemy
- Efficient query patterns

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check DATABASE_URL format
   - Ensure PostgreSQL is running
   - Verify database credentials

2. **Authentication Errors**
   - Verify SECRET_KEY is set
   - Check token expiration
   - Ensure proper Authorization header format

3. **Deployment Issues**
   - Check environment variables on Render
   - Verify build commands
   - Check application logs in Render dashboard

### Getting Help

- Create an issue in the GitHub repository
- Check the FastAPI documentation
- Review Render.com deployment guides

## What's Next?

This job tracker API provides a solid foundation for freelance work. You can now:

1. **Build Mobile Apps**: Use this API as the backend for React Native or Flutter apps
2. **Create Web Dashboards**: Build React, Vue, or Angular frontends
3. **Extend Features**: Add email notifications, file uploads, analytics
4. **Scale Up**: Add caching with Redis, implement rate limiting
5. **Freelance Ready**: You now have the skills to build modern APIs for clients

## Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic.dev/)
- [Render.com Documentation](https://render.com/docs)
