from selenium.webdriver.common.by import By
from src.testproject.classes import DriverStepSettings, StepSettings
from src.testproject.decorator import report_assertion_errors
from src.testproject.enums import SleepTimingType
from src.testproject.sdk.drivers import webdriver
import pytest


"""
This pytest test was automatically generated by TestProject
    Project: IT00051 HCI2 Project - Asfalis System Testing
    Package: TestProject.Generated.Tests.Asfalis
    Test: Asfalis Flask Test
    Generated by: Jericho Quintanilla (echoquintanilla@gmail.com)
    Generated on 11/26/2022, 14:37:43
"""


@pytest.fixture()
def driver():
    driver = webdriver.Chrome(token="XXqFr_U2pj2jVcnU1hVLxw508V9rYtXO14CSY9UpB3g",
                              project_name="My first Project",
                              job_name="Asfalis Flask Test")
    step_settings = StepSettings(timeout=15000,
                                 sleep_time=500,
                                 sleep_timing_type=SleepTimingType.Before)
    with DriverStepSettings(driver, step_settings):
        yield driver
    driver.quit()


@report_assertion_errors
def test_main(driver):
    """HCI 2 Project Testing for User Login/Registration Module of Asfalis."""
    # Test Parameters
    # Auto generated application URL parameter
    ApplicationURL = "https://asfalis-app.herokuapp.com/login"

    # 1. Navigate to '{ApplicationURL}'
    # Navigates the specified URL (Auto-generated)
    driver.get(f'{ApplicationURL}')

    # 2. Click 'Sign UP'
    sign_up = driver.find_element(By.XPATH,
                                  "//a[. = 'Sign UP']")
    sign_up.click()

    # 3. Click 'employee_id'
    employee_id = driver.find_element(By.CSS_SELECTOR,
                                      "#employeeid_create")
    employee_id.click()

    # 4. Type '201910456' in 'employee_id'
    employee_id = driver.find_element(By.CSS_SELECTOR,
                                      "#employeeid_create")
    employee_id.send_keys("201910456")

    # 5. Type 'testusername' in 'username'
    username = driver.find_element(By.CSS_SELECTOR,
                                   "#username_create")
    username.send_keys("testusername")

    # 6. Type 'testemail@gmail.com' in 'email'
    email = driver.find_element(By.CSS_SELECTOR,
                                "#email_create")
    email.send_keys("testemail@gmail.com")

    # 7. Type 'password' in 'password'
    password = driver.find_element(By.CSS_SELECTOR,
                                   "#pwd_create")
    password.send_keys("password")

    # 8. Click 'register'
    register = driver.find_element(By.CSS_SELECTOR,
                                   "[name='register']")
    register.click()

    # 9. Click 'employee_id'
    employee_id = driver.find_element(By.CSS_SELECTOR,
                                      "#employeeid_create")
    employee_id.click()

    # 10. Clear 'employee_id' contents
    employee_id = driver.find_element(By.CSS_SELECTOR,
                                      "#employeeid_create")
    employee_id.clear()

    # 11. Type '201910123' in 'employee_id'
    employee_id = driver.find_element(By.CSS_SELECTOR,
                                      "#employeeid_create")
    employee_id.send_keys("201910123")

    # 12. Click 'password'
    password = driver.find_element(By.CSS_SELECTOR,
                                   "#pwd_create")
    password.click()

    # 13. Type 'password' in 'password'
    password = driver.find_element(By.CSS_SELECTOR,
                                   "#pwd_create")
    password.send_keys("password")

    # 14. Click 'register'
    register = driver.find_element(By.CSS_SELECTOR,
                                   "[name='register']")
    register.click()

    # 15. Click 'email'
    email = driver.find_element(By.CSS_SELECTOR,
                                "#email_create")
    email.click()

    # 16. Clear 'email' contents
    email = driver.find_element(By.CSS_SELECTOR,
                                "#email_create")
    email.clear()

    # 17. Type 'testemployee@gmail.com' in 'email'
    email = driver.find_element(By.CSS_SELECTOR,
                                "#email_create")
    email.send_keys("testemployee@gmail.com")

    # 18. Click 'password'
    password = driver.find_element(By.CSS_SELECTOR,
                                   "#pwd_create")
    password.click()

    # 19. Type 'password' in 'password'
    password = driver.find_element(By.CSS_SELECTOR,
                                   "#pwd_create")
    password.send_keys("password")

    # 20. Click 'register'
    register = driver.find_element(By.CSS_SELECTOR,
                                   "[name='register']")
    register.click()

    # 21. Click 'Sign IN'
    sign_in = driver.find_element(By.XPATH,
                                  "//a[. = 'Sign IN']")
    sign_in.click()

    # 22. Click 'login1'
    login1 = driver.find_element(By.CSS_SELECTOR,
                                 "[name='login']")
    login1.click()

    # 23. Click 'username'
    username = driver.find_element(By.CSS_SELECTOR,
                                   "#username_login")
    username.click()

    # 24. Type 'testusername' in 'username'
    username = driver.find_element(By.CSS_SELECTOR,
                                   "#username_login")
    username.send_keys("testusername")

    # 25. Click 'login1'
    login1 = driver.find_element(By.CSS_SELECTOR,
                                 "[name='login']")
    login1.click()

    # 26. Click 'password'
    password = driver.find_element(By.CSS_SELECTOR,
                                   "#pwd_login")
    password.click()

    # 27. Type '1234' in 'password'
    password = driver.find_element(By.CSS_SELECTOR,
                                   "#pwd_login")
    password.send_keys("1234")

    # 28. Click 'login1'
    login1 = driver.find_element(By.CSS_SELECTOR,
                                 "[name='login']")
    login1.click()

    # 29. Click 'password'
    password = driver.find_element(By.CSS_SELECTOR,
                                   "#pwd_login")
    password.click()

    # 30. Clear 'password' contents
    password = driver.find_element(By.CSS_SELECTOR,
                                   "#pwd_login")
    password.clear()

    # 31. Type 'password' in 'password'
    password = driver.find_element(By.CSS_SELECTOR,
                                   "#pwd_login")
    password.send_keys("password")

    # 32. Click 'login1'
    login1 = driver.find_element(By.CSS_SELECTOR,
                                 "[name='login']")
    login1.click()

    # 33. Scroll window by ('0','1251')
    driver.execute_script("window.scrollBy(0,1251)")

    # 34. Scroll window by ('0','488')
    driver.execute_script("window.scrollBy(0,488)")

    # 35. Scroll window by ('0','-1739')
    driver.execute_script("window.scrollBy(0,-1739)")