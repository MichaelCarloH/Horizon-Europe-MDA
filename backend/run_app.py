import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3

# Now import and run the app
from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 