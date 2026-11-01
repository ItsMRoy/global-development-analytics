# Upload this project to GitHub and feature it on LinkedIn

## Option A — GitHub website (no Git required)

1. Sign in at https://github.com and select **New repository**.
2. Repository name: `global-development-analytics`.
3. Choose **Public** if you are comfortable showing your code and choose not to initialize with another README.
4. Use **Add file → Upload files** and upload the **contents of this extracted project folder**, preserving subfolders. For many files, GitHub Desktop or the Git command line is easier.
5. Verify `README.md`, `dashboard/index.html`, `src/`, `sql/`, `reports/figures/` and `notebooks/` appear.
6. In the repository's **About** section, add a short description and topics: `data-analytics`, `python`, `sql`, `statistics`, `gapminder`, `data-visualization`, `portfolio`.
7. Pin the repository to your GitHub profile.
8. On LinkedIn, add the repository URL under **Featured → Add link** and as a Project. Describe the project accurately as a historical dataset analysis.

## Option B — Git command line

```bash
cd global-development-analytics
git init
git add .
git commit -m "Add historical development analytics portfolio project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/global-development-analytics.git
git push -u origin main
```

Create an empty repository with the same name on GitHub before pushing. Never paste tokens into public files.

## Optional — GitHub Pages dashboard

The project already includes `docs/index.html`. Configure repository **Settings → Pages → Deploy from branch → main /docs** to make the dashboard publicly viewable. The page is static and works without a backend. GitHub Pages settings and account eligibility may vary.

## What to say in interviews

- I used a real, historical, country-year dataset, and I explicitly checked its scope and limitations.
- I wrote reusable Python functions for quality checks and population-weighted aggregations.
- I verified calculations using SQLite SQL queries and automated tests.
- I published a standalone interactive dashboard and a short evidence-focused case study.
- The association between GDP per capita and life expectancy is correlational, not causal.

**Personalization matters:** Read the code, run the analysis yourself, modify at least one visualization or analytical question, write your own interpretation, and be prepared to show your contribution. Don't claim to have independently authored code you did not actually develop.
