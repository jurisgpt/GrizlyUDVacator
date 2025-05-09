import datetime
import os
from pathlib import Path


def create_robots_txt():
    content = """
User-agent: *
Allow: /
Sitemap: https://jurisgpt.github.io/GrizlyUDVacator/sitemap.xml
"""
    return content


def create_sitemap_xml():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    content = f"""
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://jurisgpt.github.io/GrizlyUDVacator/</loc>
    <lastmod>{today}</lastmod>
    <priority>1.0</priority>
  </url>
</urlset>
"""
    return content


def create_404_html():
    content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #444;
            background-color: #f9f9f9;
            margin: 0;
            padding: 2rem;
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: #0077b5;
            margin-bottom: 1rem;
        }
        a {
            color: #0077b5;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>404 - Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <a href="/">Go back to home</a>
</body>
</html>
"""
    return content


def create_google_verification_html():
    # This is a placeholder - you'll need to get your actual verification code from Google Search Console
    content = """
<html>
<head>
    <meta name="google-site-verification" content="YOUR_VERIFICATION_CODE_HERE" />
</head>
<body>
</body>
</html>
"""
    return content


def main():
    # Define paths
    docs_dir = Path("docs")
    assets_dir = Path("docs/assets")

    # Create files
    with open(docs_dir / "robots.txt", "w") as f:
        f.write(create_robots_txt())

    with open(docs_dir / "sitemap.xml", "w") as f:
        f.write(create_sitemap_xml())

    with open(docs_dir / "404.html", "w") as f:
        f.write(create_404_html())

    # Create placeholder for Google verification
    with open(docs_dir / "google-site-verification.html", "w") as f:
        f.write(create_google_verification_html())

    print("SEO files generated successfully!")
    print("Next steps:")
    print("1. Get your Google Search Console verification code")
    print("2. Update the verification code in google-site-verification.html")
    print("3. Commit and push changes to GitHub")
    print("4. Configure GitHub Pages")


if __name__ == "__main__":
    main()
