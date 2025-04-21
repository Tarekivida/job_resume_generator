from playwright.sync_api import sync_playwright

def login_and_save_storage():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False to allow manual login
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.linkedin.com/login")

        print("👉 Please log in manually in the opened browser window.")
        input("⏳ Press Enter after you finish logging in...")

        # Save cookies and localStorage to a file
        context.storage_state(path="linkedin_auth.json")
        print("✅ Session saved to linkedin_auth.json")

        browser.close()

if __name__ == "__main__":
    login_and_save_storage()