import os
from pathlib import Path
import logging 

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]:%(message)s:')


project_name ="wasteDetection"


list_of_files = [
    ".github/workflows/.gitkeep",                        # CI workflow directory placeholder (stores GitHub Actions configs); .gitkeep ensures the empty folder is tracked
    "data/.gitkeep",             # datasets folder placeholder (where raw/processed data will be stored)
    f"{project_name}/__init__.py",         # package initializer for the main project package
    f"{project_name}/components/__init__.py", # package initializer for components (ingestion, validation, training, etc.)
    f"{project_name}/components/data_ingestion.py",      # module to handle downloading/collecting and saving raw dataset
    f"{project_name}/components/data_validation.py",     # module to validate dataset integrity, labels, and expected structure
    f"{project_name}/components/model_trainer.py",       # module that implements model training logic (e.g., YOLOv5 training loop)
    f"{project_name}/constant/__init__.py",              # package initializer for constants used across the project
    f"{project_name}/constant/training_pipeline/__init__.py", # constants specific to the training pipeline (paths, default params)
    f"{project_name}/constant/application.py",           # application-level constants (env names, default directories, file names)
    f"{project_name}/entity/config_entity.py",           # dataclass/structures representing configuration objects for components
    f"{project_name}/entity/artifacts_entity.py",        # dataclass/structures describing produced artifacts (models, metrics, plots)
    f"{project_name}/exception/__init__.py",             # custom exception types for consistent error handling
    f"{project_name}/logger/__init__.py",   # logging configuration and helper functions
    f"{project_name}/pipeline/__init__.py",              # pipeline package initializer (orchestration of steps)
    f"{project_name}/pipeline/training_pipeline.py",     # orchestrator that runs data ingestion -> validation -> training -> export
    f"{project_name}/utils/__init__.py",                 # utility package initializer
    f"{project_name}/utils/main_utils.py",               # general helper functions used across modules (file ops, parsing, etc.)
    "reseach/trials.ipynb", # research/experiment notebook(s) for exploratory analysis and trials
    "templates/index.html",      # HTML template for simple UI or report rendering
    "app.py",   # application entrypoint (e.g., Flask/FastAPI) to serve model or UI
    "Dockerfile", # container build instructions to package the application/model
    "requirements.txt",  # pinned Python dependencies for the project environment
    "setup.py",  # package metadata and install configuration (if packaging the project)
]



for filepath in list_of_files:
    filepath = Path(filepath)

    filedir, filename = os.path.split(filepath)

    if filedir!="":
        os.makedirs(filedir,exist_ok=True)
        logging.info(f"Creating directory: {filedir} for the file {filename}")

    
    if(not os.path.exists(filename)) or (os.path.getsize(filename) == 0):
        with open(filepath, "w") as f:
            pass
            logging.info(f"Creating empty file: {filename}")

    
    else:
        logging.info(f"{filename} is already created")