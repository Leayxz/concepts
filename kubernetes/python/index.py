import socket
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
      return { "message": "Olá, Kubernetes!", "POD": socket.gethostname() }
