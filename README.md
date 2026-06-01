# VisionNova AI 🌿

![VisionNova AI](assets/bg.png)

**VisionNova AI** is a premium, full-stack web application designed to provide users with an immersive, AI-driven career and portfolio platform. Featuring a gorgeous "dark forest" glassmorphism UI, cinematic splash screens, and a robust Python backend, VisionNova bridges the gap between high-end web design and powerful backend processing.

## ✨ Features
*   **Cinematic UI/UX:** A stunning, fully responsive front-end featuring 3D-morphing splash screens, heavy frosted-glass elements (`backdrop-filter`), and deep emerald color grading.
*   **Secure SQL Authentication:** A complete backend authentication system (Sign Up, Login) built with Python FastAPI and SQLAlchemy (SQLite).
*   **OTP Password Recovery:** A simulated (and SMTP-ready) OTP password reset flow.
*   **AI Resume Analysis & Mock Interviews:** Powered by local LLMs via Ollama to dynamically score resumes and generate specific technical interview questions.
*   **Live Job Fetching:** Instantly fetches live job data from the Adzuna API based on parsed resume metrics.
*   **Profile Image Engine:** Built-in image cropping and serialization for user avatars.

## 🛠️ Technology Stack
*   **Frontend:** Pure HTML5, Vanilla CSS3, Vanilla JavaScript, Cropper.js, Remix-Icons.
*   **Backend:** Python, FastAPI, Uvicorn, SQLAlchemy.
*   **Database:** SQLite (Local Serverless SQL).
*   **Server Environment:** Node.js (`http-server`, `concurrently`).

---

## 🚀 How to Run the Project Locally

### Prerequisites
1. Ensure you have **[Python 3.8+](https://www.python.org/downloads/)** installed on your system.
2. Ensure you have **[Node.js](https://nodejs.org/)** installed.

### Step 1: Install Dependencies
Open your terminal in the root `VisionNova` folder and install the Node server dependencies:
```bash
npm install
```

Next, install the Python backend dependencies:
```bash
cd backend
pip install fastapi uvicorn sqlalchemy requests
cd ..
```

### Step 2: Start the Application
Thanks to our unified startup script, you can launch both the frontend and backend servers simultaneously with a single command. 

Ensure you are in the root `VisionNova` directory and run:
```bash
npm run dev
```

### Step 3: Access the Website
Once the servers boot up, open your web browser and navigate to:
**http://localhost:3000/login.html**

*Note: The SQLite database file (`visionnova.db`) will automatically generate the first time you run the backend server.*

---
*Built with passion and AI assistance.*
