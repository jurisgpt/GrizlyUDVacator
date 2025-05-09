import json
import os
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class WebTest:
    def __init__(self, base_url="http://localhost:8090"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            }
        )
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "total": 0},
        }

    def run_test(self, name, test_func):
        try:
            result = test_func()
            self.results["tests"].append(
                {"name": name, "result": "PASS", "details": result}
            )
            self.results["summary"]["passed"] += 1
        except Exception as e:
            self.results["tests"].append(
                {"name": name, "result": "FAIL", "details": str(e)}
            )
            self.results["summary"]["failed"] += 1
        finally:
            self.results["summary"]["total"] += 1

    def test_home_page(self):
        """Test the home page"""
        response = self.session.get(self.base_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Check title
        title = soup.title.string
        assert "GrizlyUDVacator" in title, "Title does not contain GrizlyUDVacator"

        # Check meta tags
        description = soup.find("meta", {"name": "description"})["content"]
        assert len(description) > 50, "Description is too short"

        # Check robots.txt
        robots = self.session.get(urljoin(self.base_url, "robots.txt"))
        assert robots.status_code == 200, "robots.txt not found"

        return {"status": "OK", "title": title, "description_length": len(description)}

    def test_performance(self):
        """Test page load performance"""
        start = time.time()
        response = self.session.get(self.base_url)
        load_time = time.time() - start

        assert response.status_code == 200, "Page load failed"
        assert load_time < 2, f"Page load time too slow: {load_time:.2f}s"

        return {"status": "OK", "load_time": f"{load_time:.2f}s"}

    def test_seo(self):
        """Test SEO elements"""
        response = self.session.get(self.base_url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Check meta tags
        meta_tags = {
            "description": soup.find("meta", {"name": "description"})["content"],
            "keywords": soup.find("meta", {"name": "keywords"})["content"],
            "robots": soup.find("meta", {"name": "robots"})["content"],
        }

        # Check Open Graph tags
        og_tags = {
            "title": soup.find("meta", {"property": "og:title"})["content"],
            "description": soup.find("meta", {"property": "og:description"})["content"],
            "type": soup.find("meta", {"property": "og:type"})["content"],
        }

        return {"status": "OK", "meta_tags": meta_tags, "og_tags": og_tags}

    def test_sitemap(self):
        """Test sitemap.xml"""
        response = self.session.get(urljoin(self.base_url, "sitemap.xml"))
        assert response.status_code == 200, "Sitemap not found"

        # Basic XML validation
        assert "<?xml" in response.text, "Invalid XML format"
        assert "urlset" in response.text, "Missing urlset element"

        return {"status": "OK", "xml_valid": True}

    def test_404(self):
        """Test 404 page"""
        response = self.session.get(urljoin(self.base_url, "nonexistent-page"))
        assert response.status_code == 404, "404 page not working"

        soup = BeautifulSoup(response.text, "html.parser")
        assert "404" in soup.text, "404 page content not found"

        return {"status": "OK", "404_content": True}

    def test_links(self):
        """Test all internal links"""
        response = self.session.get(self.base_url)
        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.find_all("a", href=True)
        broken_links = []

        for link in links:
            href = link["href"]
            if href.startswith("#") or href.startswith("mailto:"):
                continue

            try:
                full_url = urljoin(self.base_url, href)
                resp = self.session.head(full_url, allow_redirects=True, timeout=5)
                assert resp.status_code < 400, f"Broken link: {href}"
            except Exception as e:
                broken_links.append({"url": href, "error": str(e)})

        assert not broken_links, f"Found {len(broken_links)} broken links"

        return {"status": "OK", "total_links": len(links), "broken_links": broken_links}

    def generate_report(self):
        """Generate a test report"""
        with open("web_test_report.json", "w") as f:
            json.dump(self.results, f, indent=2)

        print("\n=== WEB TEST REPORT ===")
        print(f"Total Tests: {self.results['summary']['total']}")
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")

        for test in self.results["tests"]:
            print(f"\n{test['name']}: {test['result']}")
            if test["details"]:
                print(json.dumps(test["details"], indent=2))


def main():
    import signal
    import subprocess

    # Start the server in a separate process
    server_process = subprocess.Popen(
        ["python3", "scripts/test_404.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    time.sleep(2)

    # Check if server is running
    try:
        # Try to connect to the server
        requests.get("http://localhost:8082", timeout=2)
    except requests.exceptions.RequestException as e:
        print(f"Error: Server failed to start: {e}")
        server_process.terminate()
        return

    # Run tests
    tester = WebTest()

    # Add all test cases
    tests = [
        ("Home Page", tester.test_home_page),
        ("Performance", tester.test_performance),
        ("SEO Elements", tester.test_seo),
        ("Sitemap", tester.test_sitemap),
        ("404 Page", tester.test_404),
        ("Internal Links", tester.test_links),
    ]

    # Run all tests
    for name, test_func in tests:
        tester.run_test(name, test_func)

    # Generate report
    tester.generate_report()

    # Clean up
    server_process.terminate()
    try:
        server_process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        server_process.kill()


if __name__ == "__main__":
    main()
