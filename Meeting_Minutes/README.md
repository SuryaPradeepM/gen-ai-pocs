# PoC's Backend

## Key Points

* **Python >= 3.10** is required to run the package

* Utilize the proxy to install the required packages from requirements.txt with pip
* Setup the config/.env & individual configs in config/config_*.hjson
* By default .env is not pushed to the repo. Please reach out to get apt .env
* Later, Remove proxy settings as huggingface connection is refused
* Files being indexed must have unique names

## Run

```bash
# Install Venv for packages
python -m venv venv
.\venv\Scripts\activate

# Set Proxy (if installing packages inside Cloud PC)*
set http_proxy=http://eu-nlms-proxy.eu.novartis.net:2011
set https_proxy=http://eu-nlms-proxy.eu.novartis.net:2010

# Dependencies
pip install --no-cache-dir -r requirements.txt

# With dev tools
pip install --no-cache-dir -r requirements-dev.txt

# Reset Proxy before running: Cannot connect to HuggingFace otherwise
set http_proxy=
set https_proxy=

# Run
uvicorn app:app --workers 4 --host 0.0.0.0 --port 8000
```

If SSL Verification Issue, try these steps  progressively:

```bash
# 1. Install pip packages
pip install -U certifi
pip install -U pip-system-certs

# 2. Set proxy to environment variables (if running from Cloud PC)*
set http_proxy=http://eu-nlms-proxy.eu.novartis.net:2011
set https_proxy=http://eu-nlms-proxy.eu.novartis.net:2010

# 3. az login
az login

# 4. Grab cert from portal.azure directly, export it and store a .pem file and load
```

Ensure before pushing changes:

```bash
# Before pushing changes, Ensure:
# 1. No High Severity Vulnerabilities:
bandit .

# 2. Sort the imports according to PEP import style
isort --profile black .

# 3. Apply common Code Style
black .
```
