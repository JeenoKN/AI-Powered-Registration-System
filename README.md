# AI-Powered Registration & Dynamic Form System

A full-stack senior project that uses AI to simplify the creation and management of dynamic registration forms.

The system can generate structured form content from multiple input formats, including text, PDF documents, images, and audio. It combines a Vue.js frontend, FastAPI backend, MongoDB database, Gemini API integration, and Docker-based development environment.

## Features

- Create and manage dynamic registration forms
- Generate structured form content using AI
- Process text, PDF, image, and audio inputs
- Upload and process files through backend APIs
- Edit generated forms through an interactive web interface
- Drag-and-drop form editing
- Store forms and application data in MongoDB
- RESTful API communication between frontend and backend
- Dockerized frontend, backend, and database services

## Tech Stack

### Frontend
- Vue.js 3
- Vite
- Vue Router
- Tailwind CSS
- Vue Draggable

### Backend
- Python
- FastAPI
- Uvicorn
- Pydantic

### Database
- MongoDB
- PyMongo
- Motor

### AI & Document Processing
- Google Gemini API
- SpeechRecognition
- PyPDF
- Pandas
- OpenPyXL

### DevOps
- Docker
- Docker Compose

## System Architecture

```text
User
  |
  v
Vue.js Frontend
  |
  | REST API
  v
FastAPI Backend
  |
  +----------------------+----------------------+
  |                      |                      |
  v                      v                      v
MongoDB            Gemini API          File Processing
                                      PDF / Image / Audio
```

## Project Structure

```text
AI-Powered-Registration-System/
├── frontend-vue/          # Vue.js frontend
├── backend-python/        # FastAPI backend and AI processing
├── docs/                  # Project documentation
├── test-files/            # Sample files for testing
├── docker-compose.yml     # Multi-service local environment
└── README.md
```

## Getting Started

### Requirements

- Git
- Docker
- Docker Compose
- Google Gemini API key

### 1. Clone the repository

```bash
git clone https://github.com/JeenoKN/AI-Powered-Registration-System.git
cd AI-Powered-Registration-System
```

### 2. Configure environment variables

Copy the example backend environment file and add your local values:

```bash
cp backend-python/.env.example backend-python/.env
```

Example values:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
MONGO_URI=mongodb://localhost:27018/ai_registration
```

Do not commit real API keys, passwords, tokens, or other secrets to GitHub.

### 3. Run with Docker

```bash
docker compose up --build
```

This starts the application services defined in `docker-compose.yml`.

## Key Learning Outcomes

This project provided hands-on experience with:

- Full-stack web application development
- Vue.js frontend development
- REST API design with FastAPI
- MongoDB integration
- AI API integration
- Multi-format document processing
- Frontend/backend integration
- Docker-based development environments
- Debugging and integrating multiple application services

## Project Type

Senior Project  
Bachelor of Engineering in Computer Engineering

## Author

**Treemonrapat Vichisri**  
Computer Engineering Student
