# Cricket Auction (Claymore)

Small Streamlit app to manage cricket auctions (teams, player pool, bidding).

Quickstart
1. Create a virtual environment and activate it (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

Files
- [app.py](app.py) — main Streamlit application
- [requirements.txt](requirements.txt) — Python dependencies

Deploying to Streamlit Cloud

1. Push this repository to GitHub.
2. Go to https://streamlit.io/cloud and click "New app" → choose your GitHub repo and branch.
3. Set the `requirements.txt` path if needed and deploy.

Setting Admin Credentials (Streamlit Secrets)

1. In Streamlit Cloud app settings, open "Secrets" and add keys:

```
ADMIN_USERNAME = your_admin_username
ADMIN_PASSWORD = your_secure_password
```

2. The app uses these secrets for the admin login (defaults to `admin` / `adminpass` locally).

Granting Access

- To give someone admin access to the deployed app, either share the admin credentials above or invite them as a collaborator to the GitHub repository and set their own secrets in a fork/deployment.


If you want me to run the app locally or add tests/CI, tell me which you'd prefer.
