def task_server():
    return {
        'actions': ['PYTHONPATH=src uvicorn not-echo.server.main:app --reload'],
        'verbosity': 2
    }
def task_client():
    return {
        'actions': ['python src/not-echo/client/main.py'],
        'verbosity': 2
    }
