
## Installation
```
python3 -m venv .venv
```

Create `.env` file (copy `.env.example`) in root and `credentials.yml` in the credentials path (check out `.streamlit/credentials.example.yml`).

### Install dependencies
```
source .venv/bin/activate
pip install -r requirements.txt
```

And updating requirements.txt
```
pip freeze > requirements.txt
```

## Run
```bash
./bin/streamlit
```
