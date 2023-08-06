# APPMMM API AUTOMATION
APPMMM API Automation using Python, Request and Pytest

## Pre-requisites:
- Install Python 3.7 and up
    - for required packages read [requirements.txt](https://github.kyndryl.net/MCMP-IST/mcmp-ui-automation/blob/premaster/requirements.txt)
    and for installation run this command on terminal: 
    ```bash
    pip install -r requirements.txt
    ```
## Understanding folder structure:
### Structure of framework:

* config.ini : is the configuration file that contains the details of tenant, username, password, browser type, headless or headed execution and har collection   
* conftest.py : is the starting point of framework execution  
* test cases are created under the tests folder  
* payload files are store under resourses/payload folder
* Core functionalities like rest api wrapper methods, json utilities are under common folder  
* payload formation model file are there under fixture folder  
* locators are available under locators folder  

Testing application:

url: https://mmmapp.eastus.cloudapp.azure.com

swagger: https://mmmapp.eastus.cloudapp.azure.com/api/v1/explorer/#/ApplicationGroupController/ApplicationGroupController.create

### How to start

By using Windows Terminal, Python and pip
1. Place the repository files into the directory of your choice
2. Create virtual environment
```
py -m venv env
```
2. Activate created virtual environment  
```
env\Scripts\activate
```
3. Install project's dependencies  
```
pip install -r requirements.txt
```
4. Install [Allure Framework](https://docs.qameta.io/allure/)

### How to run tests

All tests:
```
pytest
```
Positive tests:
```
pytest -m positive
```
Negative tests:
```
pytest -m negative
```
- **With Allure Test report**
```
pytest --alluredir=allure_reports
```
Show generated report in browser:
```
allure serve allure_reports
```
