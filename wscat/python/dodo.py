import subprocess


def task_build_protos():
    """Build protocol buffer files"""
    return {
        'actions': [
            [
                'protoc',
                '-I=../proto',
                '--python_out=src/wscat/server',
                '--pyi_out=src/wscat/server', 
                '../proto/simple_math.proto'
            ]
        ],
        'file_dep': ['../proto/simple_math.proto'],
        'targets': ['src/wscat/server/simple_math_pb2.py', 'src/wscat/server/simple_math_pb2.pyi'],
        'clean': True,
    }


def task_run_server():
    """Run the uvicorn server with auto-reload"""
    return {
        'actions': [
            [
                'uvicorn', 
                'wscat.server.main:c', 
                '--reload', 
                '--app-dir', 
                'src'
            ]
        ],
        'task_dep': ['build_protos'],
        'uptodate': [False],
        'verbosity': 2,
    }
