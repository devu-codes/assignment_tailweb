#### Steps
1. Clone the repository.
2. create virtual ennvironment `python -m venv venv`
3. install dependencies `pip install -r requiremments.txt`
4. run the app - `uvicorn run app:main --reload`
5. Endpoints exposed -
    1. POST /register
    2. POST /login
    3. GET /home
    4. POST /student/{student_id}/update
    5. POST /student/add
    6. POST /logout
