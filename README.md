# AI-Powered Registration & Dynamic Form System

A full-stack senior project that uses AI to simplify the creation and management of dynamic registration forms.

The system allows users to generate structured form content from multiple input formats, including text, documents, images, and audio. It combines a Vue.js frontend, FastAPI backend, MongoDB database, Gemini API integration, and Docker-based development environment.

## Features

- Create and manage dynamic registration forms
- Generate structured form content using AI
- Process multiple input formats including text, PDF, image, and audio
- Upload and process files through the backend API
- Store application and form data using MongoDB
- Interactive web interface for managing generated forms
- Drag-and-drop form editing
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
  +-------------------+
  |                   |
  v                   v
MongoDB          Google Gemini API
                      |
                      v
             AI / Document Processing
