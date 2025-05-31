# Roamly

An adventure-sharing webapp built for exploration
<img src="https://github.com/user-attachments/assets/f671d2aa-bb36-4c26-a583-08ca82ad3581" width="400"/>

Roamly is a social platform where each user can share their outdoor adventures like hikes, travels, and any other new expieriences. This is done through posting Adventures which is a collection of photos with a description and location information. Explorers can search up locations or titles and see other peoples adventures to similiar places and how they enjoyed it!

This project is built from the ground up to demonstrate full-stack web development, cloud deployment, and eventually data stream processing with tools like Kafka and Spark.

# Why Im building this?
Roamly is meant to be more than just another Instagram clone project, its my training ground for:
- backend engineering
- building cloud architecture
- learning AWS deployment
- showing potential for data engineering

# Features:
  ### Completed:
    - User Authentication with JWT
    - Post Adventures with:
      - Title
      - Description
      - Images
      - Captions
    - CI/CD Pipline with GitHub Actions
    - Thouroghly tested with PyTest
    - Fuzzy Searching for titles
  ### Planned:
    - Frontend
    - Location (search, implementation, etc)
    - Kafka integration for real-time event streaming (e.g. new post notifications)
    - PySpark data pipeline to analyze user engagement (likes, post frequency, etc.)
    - Websocket communication ( realtime feed updates, messaging etc..)
    - Like and Comment systems

# Tech Stack by layer:
| Layer | Tools |
|-------|-------|
|Backend | FastAPI, Python, SQLAlchemy, Alembic |
|Database |PostgreSQL |
|Storage | Amazon S3 |
|CI/CD | 	GitHub Actions|
|Deployment | AWS (EC2, RDS, S3 planned)|
|Data Processing | PySpark (planned)|
|Frontend |(TBD — API-first design) |


# Contributing

This is currently a solo developer project, but I'm open to contributions, especially from others interested in:
- FastAPI best practices
- Kafka/PySpark integration
- AWS infrastructure

# Contact
If you're a recruiter, engineer, or just someone who loves cool software, feel free to connect:
- Email: Igorchernenko1928@gmail.com
- LinkedIn: linkedin.com/in/igor--chernenko
- GitHub: @Igor-Chernenko
