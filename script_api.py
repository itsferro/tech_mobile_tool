from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Script Runner API"}

@app.post("/run-script")
def run_script():
    try:
        # Run the temp_main.py script using the virtual environment Python
        result = subprocess.run(
            [".\\tmtenv\\Scripts\\python.exe", "./temp_main.py"], 
            capture_output=True, 
            text=True, 
            timeout=30  # 30 second timeout
        )
        
        return {
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
    
    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": "Script execution timed out after 30 seconds",
            "return_code": -1
        }
    
    except Exception as e:
        return {
            "output": "",
            "error": str(e),
            "return_code": -1
        }