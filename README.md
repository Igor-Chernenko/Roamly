# Roamly

Roamly is a full-stack social platform built for adventure lovers. Users can post their adventures, view others' journeys, leave comments, and ask a built-in AI hiking assistant for personalized suggestions — all powered by modern cloud infrastructure, vector databases, and LLMs.

This project was a solo build to showcase real-world full-stack engineering, modern backend architecture, and practical AI integration.


##  Features
###  Core Functionality
- **User authentication** using JWT (login, signup, profile view/edit)
- **Adventure posting system**: title, description, image uploads(S3) with captions
- **Comment system** under each adventure
- **Trigram search** for users and posts using PostgreSQL `pg_trgm` extension with `GIN` indexing

###  AI Hiking Assistant ("Roamly Rabbit")
- Users can ask hiking-related questions directly in-app
- Uses `all-MiniLM-L6-v2` for vector embeddings
- Stores vectors in **Qdrant** for similarity search
- Retrieves top matching hikes, then pipes summaries into **OpenAI GPT** with token monitoring
- Only in-memory no chats stored, privacy-friendly
- **Rate limiting** (5 chat requests/hour/user) to control abuse

### Backend Architecture
- Built with **FastAPI** and **SQLAlchemy ORM**
- Uses **Alembic** for schema migration/versioning
- PostgreSQL for relational data, with deep DBeaver and indexing usage

### Frontend
- Built in **React** with token-aware routing
- Real-time UX: post feed, profile view, inline commenting, AI sidebar chat
- Image carousel, adventure detail pages, and username search suggestions

### Cloud & DevOps
- Fully **Dockerized** stack (backend, frontend, Qdrant)
- Deployed on **AWS EC2**
- PostgreSQL hosted on **AWS RDS**
- Image storage handled via **AWS S3**
- DNS mapping
- **GitHub Actions** CI/CD pipeline with pytest validation on push
- AWS managed with **Boto3** for scripted interactions

---

## Testing & Reliability
- Built with **pytest** for backend unit/integration tests
- Automated testing pipeline using **GitHub Actions**
- Custom rate limiter and auth middleware to guard endpoints

---

## Technologies Used

| Area        | Stack / Tool |
|-------------|--------------|
| Backend     | FastAPI, Python, SQLAlchemy, Alembic |
| Frontend    | React, Tailwind CSS, JWT |
| Database    | PostgreSQL (pg_trgm + GIN), Qdrant |
| AI / NLP    | HuggingFace Transformers, OpenAI GPT |
| Cloud       | AWS (EC2, RDS, S3, IAM), Docker |
| CI/CD       | GitHub Actions, Pytest |
| Other       | DBeaver, Boto3, Docker Compose |

---

## Local Development

```bash
git clone https://github.com/Igor-Chernenko/roamly.git
cd roamly
docker compose up --build
```


## Contributing

This is currently a solo developer project, but I'm open to contributions, especially from others interested in:
- FastAPI best practices
- Kafka/PySpark integration
- AWS infrastructure

## Contact
If you're a recruiter, engineer, or just someone who loves cool software, feel free to connect:
- Email: Igorchernenko1928@gmail.com **or** Chernenko.s.igor@gmail.com
- LinkedIn: linkedin.com/in/igor--chernenko
- GitHub: @Igor-Chernenko
