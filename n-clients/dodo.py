def task_server():
    return {
        'actions': ['PYTHONPATH=src uvicorn n-clients.server.main:app --reload'],
        'verbosity': 2
    }
def task_client():
    return {
        'actions': ['python client.py'],
        'verbosity': 2
    }