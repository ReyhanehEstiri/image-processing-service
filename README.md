# Image Processing Service

A REST API for uploading and transforming images, built with FastAPI.
Users can register, upload images, apply transformations, and retrieve the results.

This project is a solution to the [Image Processing Service](https://roadmap.sh/projects/image-processing-service) project from [roadmap.sh](https://roadmap.sh).
## Features

- User registration and login with JWT authentication
- Upload images (JPEG, PNG, WEBP) with validation and a 5MB size limit
- List your images with pagination
- Retrieve images (each user can only access their own images)
- Image transformations: resize, crop, rotate, flip, mirror, grayscale, format conversion
- Rate limiting on the transform endpoint (10 requests per minute)

## Tech Stack

FastAPI, SQLAlchemy, SQLite, Pillow, PyJWT, slowapi

## Setup

```bash
git clone <your-repo-url>
cd image-processing-service
python -m venv venv
venv\Scripts\activate       
pip install -r requirements.txt
cp .env.example .env        
uvicorn app.main:app --reload
```

Then edit `.env` and set a strong `SECRET_KEY`. You can generate one with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Open http://127.0.0.1:8000/docs to explore and test the API with Swagger UI.

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register` | No | Create an account |
| POST | `/login` | No | Log in and receive a JWT |
| GET | `/me` | Yes | Get the current user |
| POST | `/images` | Yes | Upload an image |
| GET | `/images?page=1&limit=10` | Yes | List your images (paginated) |
| GET | `/images/{id}` | Yes | Retrieve an image file |
| POST | `/images/{id}/transform` | Yes | Apply transformations (creates a new image) |

## Example

Transform request:

```json
{
  "transformations": {
    "resize": {"width": 400, "height": 700},
    "rotate": 90,
    "filters": {"grayscale": true},
    "format": "webp"
  }
}
```

The original image is never modified. Each transformation creates a new image with its own ID.

## Project Structure

```
app/
├── main.py          # App setup and routers
├── database.py      # Database connection
├── models.py        # User and Image models
├── auth.py          # Password hashing and JWT
├── limiter.py       # Rate limiter
├── transforms.py    # Image processing functions
└── routers/
    ├── users.py     # Auth endpoints
    └── images.py    # Image endpoints
```