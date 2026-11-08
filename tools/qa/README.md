# Local QA utilities

These scripts are optional developer checks and are not required to run the app.

- `api_qa.py`: exercises local health, authentication, API and seeded-data routes.
- `visual_browser_qa.py`: Selenium-based local browser screenshots and interaction checks.

Both scripts calculate the repository root from their new location. The browser script expects a local Chrome installation and a compatible ChromeDriver; it retains the optional local driver lookup under the ignored `work/chromedriver-*/` scratch path. It writes results to `reports/screenshots/`.

Run the QA scripts only against a disposable local database and synthetic test account. They can create accounts, seed records and submit feedback; do not point them at production data.
