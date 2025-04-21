# This script opens a Chromium browser, allows the user to log in to LinkedIn manually,
# and then saves the session state (cookies and localStorage) to a JSON file.
# Import the sync API from Playwright for browser automation
from playwright.sync_api import sync_playwright

# Function to log into LinkedIn and save the browser session state
def login_and_save_storage():
    # Launch a non-headless Chromium browser so the user can log in manually
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  
        # Create a new browser context (isolated session)
        context = browser.new_context()
        # Open a new tab in the browser
        page = context.new_page()
        # Navigate to the LinkedIn login page
        page.goto("https://www.linkedin.com/login")

        # Pause the script until the user has logged in manually
        print("👉 Please log in manually in the opened browser window.")
        input("⏳ Press Enter after you finish logging in...")

        # Save the session state (cookies and localStorage) to a file
        context.storage_state(path="linkedin_auth.json")
        print("✅ Session saved to linkedin_auth.json")

        # Close the browser after saving the session
        browser.close()

# Run the function if the script is executed directly
if __name__ == "__main__":
    login_and_save_storage()