import os 

NODE_ENV = "development" if os.environ.get("NODE_ENV") == "development" else "production"
APP_NAME="sidetrek"
GENERATED_LOCAL_SIDETREK_DIRNAME=".sidetrek" # for cli generated dir, use a hidden dir
GENERATED_PROJECT_DIRNAME="project"