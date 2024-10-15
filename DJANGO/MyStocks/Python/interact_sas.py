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
import pyperclip
import platform

def run_sas_script(user_email, filenames):
    """
    Automates the process of running a SAS script by interacting with the SAS OnDemand website using Selenium.
    
    :param user_email: The user's email associated with the SAS account.
    :param filename: The name of the file to be processed or uploaded on SAS OnDemand.
    """
    service_id = "SAS"
    password = keyring.get_password(service_id, user_email)  # retrieve password

    start_time = time.time()
    driver = webdriver.Chrome()
    
    print(filenames)
    
    try:
        driver.get("https://welcome.oda.sas.com/?event=logout&eventSource=eu-west-1a")
        driver.maximize_window()

        # Log in process
        sign_in_button = driver.find_element(By.CSS_SELECTOR, ".SIbutton")
        sign_in_button.click()

        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='emailOrAccountName']"))
        )
        email_input.send_keys(user_email)

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='password']"))
        )
        password_input.send_keys(password)

        checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='agreeToLicenseAndTerms']"))
        )
        if not checkbox.is_selected():
            checkbox.click()

        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@mat-based-button='']"))
        )
        sign_in_button.click()

        time.sleep(2)

        # Handle multiple windows
        current_window = driver.current_window_handle
        deploy_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'deploy')]"))
        )
        deploy_button.click()

        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != current_window:
                driver.switch_to.window(window_handle)
                break

        time.sleep(10)

        # Interaction with files
        files_home_element = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Files (Home)')]"))
        )
        actions = ActionChains(driver)
        actions.double_click(files_home_element).perform()

        time.sleep(5)

        files_stock_element = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Stock Data')]"))
        )
        actions.double_click(files_stock_element).perform()
        
        
        for filename in filenames:
            
            # Copy the filename to the clipboard
            pyperclip.copy(filename)
            
            time.sleep(5)
            
            # Refresh the page
            driver.refresh()
            
            time.sleep(5)
            
            files_stock_element = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Stock Data')]"))
            )
            
            files_stock_element.click()
            
            files_upload_element = WebDriverWait(driver, 60).until(
                EC.visibility_of_element_located((By.XPATH, "//span[contains(@class, 'sasUploadIcon')]"))
            )

            files_upload_element.click()
            
            time.sleep(5)

            actions.send_keys(Keys.TAB).perform()

            time.sleep(5)
            
            actions.send_keys(Keys.ENTER).perform()

            time.sleep(5)
            pyautogui.press('tab')
            time.sleep(5)
            # Copy the filename to the clipboard
            pyperclip.copy(filename)
            time.sleep(5)
            pyperclip.copy(filename)
            # Use hotkey to paste the clipboard contents
            pyautogui.hotkey(('command' if platform.system() == 'Darwin' else 'ctrl'), 'v')
            # pyautogui.typewrite(filename)
            time.sleep(5)
            pyautogui.press('tab')
            time.sleep(5)
            pyautogui.press('tab')
            time.sleep(5)
            pyautogui.press('down')
            time.sleep(5)
            pyautogui.press('enter')
            time.sleep(5)

            # Execute the script
            actions.send_keys(Keys.ENTER).perform()
            time.sleep(5)
            
            # Try to click the "Replace" button if the file already exists
            try:
                replace_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@id='decisionDialog_decision1Button_label' and text()='Replace']"))
                )
                replace_button.click()
                print(f"File '{filename}' already exists, clicked 'Replace'.")
            except Exception as e:
                print(f"File '{filename}' does not already exist, or 'Replace' button not found.")

        format_button = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@aria-labelledby='perspectiveTabContainer_tabsBC_tab0_formatCodeBtn_label']"))
        )
        format_button.click()

        time.sleep(5)

        run_button = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@aria-labelledby='perspectiveTabContainer_tabsBC_tab0_submitBtn_label']"))
        )
        run_button.click()

        elapsed_time = time.time() - start_time
        print(f"Script executed successfully in {elapsed_time:.2f} seconds.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        driver.quit()
        print("WebDriver closed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run a SAS script using Selenium.')
    parser.add_argument('email', help='Your SAS email.')
    parser.add_argument('filenames', nargs='+', help='Names of the files to work with (space-separated for multiple files).')

    args = parser.parse_args()

    # Pass the list of files directly to the script
    run_sas_script(args.email, args.filenames)
