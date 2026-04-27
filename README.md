# 🟪 mySquareAi: The Human Search Engine 🔍✨

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Weaviate](https://img.shields.io/badge/Weaviate-green?style=for-the-badge&logo=weaviate)](https://weaviate.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com/)

> **Connecting minds through AI.** mySquareAi is a next-generation "Human Search Engine" that goes beyond keywords to find people based on deep semantic meaning, interests, and professional profiles.

---

## 🌟 Overview

**mySquareAi** is a sophisticated backend engine built to revolutionize how we discover and connect with people. Unlike traditional search engines that rely on exact matches, mySquareAi leverages **Vector Embeddings** and **Large Language Models (LLMs)** to understand the *essence* of a search query and match it with the most relevant human profiles.

Whether you're looking for a mentor with specific niche expertise, a co-founder with matching values, or simply someone who shares your obscure hobbies, mySquareAi finds the needle in the human haystack. 🧵📍

---

## 🚀 Key Features

*   **🧠 Semantic Human Search**: Search for people using natural language prompts. The system understands context, not just keywords.
*   **🤖 AI-Powered Optimization**: Uses **Google Gemini 1.5 Pro** to analyze and optimize user queries for the most accurate results.
*   **⚡ Vector-Based Retrieval**: Built on **Weaviate**, a state-of-the-art vector database, ensuring lightning-fast and highly relevant similarity searches.
*   **🔐 Secure API Management**: Custom API key system with encryption to ensure secure access to the platform.
*   **🔥 Firebase Integration**: Seamless user authentication and metadata management using Firebase.
*   **📈 Dynamic Profile Evolution**: Interests and vectors update dynamically as users evolve their profiles, keeping the search index fresh.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) ⚡ |
| **Vector DB** | [Weaviate](https://weaviate.io/) 🟩 |
| **LLM & Embeddings** | [Google Gemini 1.5 Pro](https://ai.google.dev/) ♊ |
| **Authentication** | [Firebase Auth](https://firebase.google.com/docs/auth) 🔥 |
| **Database/Storage** | [Firebase Firestore](https://firebase.google.com/docs/firestore) 📁 |
| **Server/Deployment** | [Uvicorn](https://www.uvicorn.org/) & [Mangum](https://mangum.io/) (AWS Lambda Ready) ☁️ |

---

## 🏁 Getting Started

### 📋 Prerequisites

*   **Python 3.10+**
*   **Weaviate Instance** (WCS or Local)
*   **Google AI API Key** (for Gemini)
*   **Firebase Project** (Service Account Credentials)

### ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/mysquareaiAPI.git
    cd mysquareaiAPI
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    WCS_URL=your_weaviate_cluster_url
    WCS_API_KEY=your_weaviate_api_key
    GOOGLE_API_KEY=your_google_gemini_api_key
    # Add other necessary keys here
    ```

### 🚀 Running the Server

Start the development server with auto-reload:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The API documentation will be available at `http://localhost:8000/docs`.

---

## 📡 API Endpoints

### 👤 User Discovery
*   `GET /get_people/`: Search for users similar to a prompt.
*   `GET /get_user/`: Retrieve detailed profile information by ID.

### ✍️ Profile Management
*   `POST /upload_user/`: Create a new user profile with semantic indexing.
*   `POST /update_user/`: Update a user's description.
*   `POST /update_interests/`: Modify user interests (automatically re-calculates vectors).
*   `POST /delete_user/`: Remove a user from the system.

### 🛠️ Utilities
*   `GET /test/`: Basic health check.
*   `GET /verify_user/`: Verify Firebase credentials.

### 📓 Interactive Testing
*   `apiTesting.ipynb`: A Jupyter Notebook containing examples and tests for interacting with the API endpoints. Perfect for getting started!

---

## 🗺️ Roadmap & TODOs

- [ ] 🛡️ Implement daily call limits to prevent API abuse.
- [ ] 📸 Integrate **Multimodal Embedders** for profile image analysis (Premium feature).
- [ ] 🧹 Refactor monolithic Firebase helpers for better modularity.
- [ ] ⚠️ Improve error handling with specific `HTTPException` responses.
- [ ] 📜 Implement comprehensive search history for users.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">Made with ❤️ by Marco De Luca</p>
