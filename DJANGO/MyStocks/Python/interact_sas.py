import argparse
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import keyring
import pyautogui
import time
import os

def load_sas_file(file_path):
    """
    Opens a .sas file and loads its contents into a string variable.
    
    :param file_path: The path to the .sas file.
    :return: The contents of the .sas file as a string.
    """
    try:
        with open(file_path, 'r') as file:
            sas_code = file.read()
        return sas_code
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage:
# sas_code = load_sas_file('path/to/your/file.sas')
# print(sas_code)

def run_sas_code(user_email, filename, sas_code):
    # The service is just a namespace for your app
    service_id = "SAS"
    
    # Retrieve the password from the keyring
    password = keyring.get_password(service_id, user_email)  # retrieve password
    
    # Record the start time
    start_time = time.time()
    
    # Initialize WebDriver (assuming Chrome)
    driver = webdriver.Chrome()
    
    try:
        # Open sas.com
        driver.get("https://welcome.oda.sas.com/?event=logout&eventSource=eu-west-1a")
        driver.maximize_window()

        # Click the Sign In button
        sign_in_button = driver.find_element(By.CSS_SELECTOR, ".SIbutton")
        sign_in_button.click()

        # Enter email using XPath
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='emailOrAccountName']"))
        )
        email_input.send_keys(user_email)

        # Enter password using XPath
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='password']"))
        )
        password_input.send_keys(password)

        # Select the checkbox using XPath
        checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='agreeToLicenseAndTerms']"))
        )
        if not checkbox.is_selected():
            checkbox.click()

        # Click the "Sign In" button using XPath
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@mat-based-button='']"))
        )
        sign_in_button.click()

        # Optionally, wait to observe the result
        time.sleep(2)

        # Store the current window handle
        current_window = driver.current_window_handle

        # Wait for the "Deploy" button to appear
        deploy_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'deploy')]"))
        )

        # Click the "Deploy" button
        deploy_button.click()

        # Switch to the new tab
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != current_window:
                driver.switch_to.window(window_handle)
                break

        # Wait for the page to fully load
        time.sleep(10)

        # Wait for the "Files (Home)" element to be visible
        files_home_element = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Files (Home)')]"))
        )

        pyautogui.typewrite(sas_code)

        # Create ActionChains object and double-click
        actions = ActionChains(driver)
        actions.double_click(files_home_element).perform()

        time.sleep(5)

        files_stock_element = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Stock Data')]"))
        )
        actions.double_click(files_stock_element).perform()

        # Continue with upload steps
        files_upload_element = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, "//span[contains(@class, 'sasUploadIcon')]"))
        )
        files_upload_element.click()

        # Interactions using pyautogui
        pyautogui.press('tab')
        time.sleep(5)
        pyautogui.typewrite(filename)
        time.sleep(5)
        pyautogui.press('tab')
        time.sleep(5)
        pyautogui.press('tab')
        time.sleep(5)
        pyautogui.press('down')
        time.sleep(5)
        pyautogui.press('enter')
        time.sleep(5)
        actions.send_keys(Keys.ENTER).perform()

        # Click the format code and run buttons
        format_button = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@aria-labelledby='perspectiveTabContainer_tabsBC_tab0_formatCodeBtn_label']"))
        )
        format_button.click()

        time.sleep(5)

        run_button = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@aria-labelledby='perspectiveTabContainer_tabsBC_tab0_submitBtn_label']"))
        )
        run_button.click()

        # Optionally, record the elapsed time
        elapsed_time = time.time() - start_time
        print(f"Script executed successfully in {elapsed_time:.2f} seconds.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
        print("WebDriver closed")

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Run SAS code using Selenium.')
    parser.add_argument('email', help='Your SAS email.')
    parser.add_argument('filename', help='Name of the file to work with.')
    parser.add_argument('sas_code', help='Path to a .sas file or the SAS code itself.')

    # Parse the arguments
    args = parser.parse_args()

    # Check if the sas_code argument is a file
    if args.sas_code.endswith(".sas") and os.path.isfile(args.sas_code):
        sas_code = load_sas_file(args.sas_code)
        if sas_code is None:
            print("Error loading SAS code from file.")
        else:
            # Call the function with the file contents as SAS code
            run_sas_code(args.email, args.filename, sas_code)
    else:
        # Call the function assuming the code is directly provided
        run_sas_code(args.email, args.filename, args.sas_code)