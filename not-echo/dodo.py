def task_server():
    return {
        'actions': ['PYTHONPATH=src uvicorn not-echo.server.main:app --reload']
       # 'verbocity': 2
    }
def task_client():
    return {
        'actions': ['python client.py']
        #'verbocity': 2
    }