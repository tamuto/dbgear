import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()

app.mount('/static', StaticFiles(directory='dist', html=True), name='static')


@app.get('/')
def root():
    return RedirectResponse('/static')


def run():
    uvicorn.run('dbgear.backend:app', port=5000, log_level='info')
