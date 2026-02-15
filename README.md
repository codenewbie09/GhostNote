# GhostNote

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![Redis](https://img.shields.io/badge/Redis-7.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A secure, self-destructing messaging service built with **FastAPI** and **Redis**. Send a secret link that self-destructs immediately after reading.

**Live Demo:** [https://ghostnote-xa32.onrender.com](https://ghostnote-xa32.onrender.com)

## Features

- ** End-to-End Encryption:** Notes are encrypted (AES-128) using `cryptography.fernet` before storage.
- ** Self-Destruct:** Uses Redis `GETDEL` for atomic read-and-destroy operations.
- ** High Performance:** Built with `asyncio` and Redis for sub-millisecond latency.
- ** Rate Limiting:** Protects against spam/abuse using Redis-based rate limiting.
- ** Modern UI:** A clean, "human-made" responsive interface using vanilla CSS (no frameworks).

## Tech Stack

- **Backend:** FastAPI, Python
- **Database:** Redis (In-memory store + TTL)
- **Security:** `cryptography.fernet` (Encryption)
- **Deployment:** Docker, Render

## Getting Started

### Prerequisites

- Python 3.9+
- Redis Server

### Installation

1.  **Clone the repo**

    ```bash
    git clone https://github.com/codenewbie09/ghostnote.git
    cd ghostnote
    ```

2.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables**
    Create a `.env` file:

    ```text
    GHOSTNOTE_SECRET_KEY=your_generated_fernet_key_here
    REDIS_URL=redis://localhost:6379
    BASE_URL=http://localhost:8000
    ```

    _To generate a secret key, run: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`_

4.  **Run Redis**

    ```bash
    docker run -d -p 6379:6379 redis
    ```

5.  **Start the server**
    ```bash
    uvicorn main:app --reload
    ```

## How it Works

1.  **Create:** User enters a secret. The backend encrypts it and stores it in Redis with a TTL.
2.  **Share:** The user receives a unique link containing a Note ID and an Access Token.
3.  **Read:** Recipient opens the link. The backend validates the token, decrypts the message, and **immediately deletes** it from Redis (`GETDEL`).

## Deployment

This project is deployed on Render:

- \*\*Backend (FastAPI): [ghostnote-xa32.onrender.com](https://ghostnote-xa32.onrender.com)
- **Database:** Render Redis (Free Tier)

## License

MIT License

---

**Built by [Prateek Agrawal](https://github.com/codenewbie09)**
