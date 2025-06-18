import os
import time
import requests
import pandas as pd
from PIL import Image
from io import BytesIO
from flask import Flask, render_template, request
import pytesseract as pyt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoAlertPresentException, InvalidSessionIdException


def writeCSV(enroll, name, *args, sgpa, cgpa, remark, filename):
    gradesString = [str(a) + "," for a in args]
    information = [enroll, ",", name, ","
                   ] + gradesString + [sgpa, ",", cgpa, ",", remark, "\n"]
    with open(filename, 'a') as f:
        f.writelines(information)
        f.close()


def makeXslx(filename):
    csvFile = f'{filename}.csv'
    df = pd.read_csv(csvFile)
    excelFile = f'{filename}.xlsx'
    df.index += 1
    df.to_excel(excelFile)


def downloadImage(url, name):
    content = requests.get(url).content
    file = BytesIO(content)
    image = Image.open(file)
    path = f"C:\\Users\\LENOVO\\Desktop\\4 TH SEM\HTML\\{name}"
    with open(path, "wb") as f:
        image.save(f, "JPEG")


def readFromImage(captchaImage: str) -> str:
    # Tesseract is installed at /usr/bin/tesseract on Linux
    pyt.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    image = Image.open(captchaImage)
    captcha = pyt.image_to_string(image)
    captcha = captcha.upper().replace(" ", "")
    os.remove(captchaImage)
    return captcha


def resultFound(start: int, end: int, branch: str, year: str, sem: int):

    if branch not in ["CS", "IT", "ME", "AI", "DS", "EC", "EX"]:
        print("Wrong Branch Entered")
        return

    noResult = []
    '''
    options = Options()
    options.add_argument('--headless')'''
    firstRow = True
    filename = f'{branch}_sem{sem}_result.csv'
    #writeCSV("ENROLLMENT NO.","NAME","BT-","SGPA","CGPA","RESULT",filename)
    driver = webdriver.Chrome()
    #driver = webdriver.Chrome()
    driver.implicitly_wait(0.5)
    driver.get("http://result.rgpv.ac.in/Result/ProgramSelect.aspx")
    driver.find_element(By.ID, "radlstProgram_1").click()

    while start <= end:
        if (start < 10):
            num = "00" + str(start)

        elif (start < 100):
            num = "0" + str(start)

        else:
            num = str(start)

        enroll = f"0105{branch}{year}1{num}"
        print(f"Currently compiling ==> {enroll}")

        img_element = driver.find_element(
            By.XPATH, '//img[contains(@src, "CaptchaImage.axd")]')
        img_src = img_element.get_attribute("src")
        url = f'http://result.rgpv.ac.in/result/{img_src.split("Result/")[-1]}'

        downloadImage(url, "captcha.jpg")
        captcha = readFromImage("captcha.jpg")
        captcha = captcha.replace(" ", "")

        Select(
            driver.find_element(
                By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_drpSemester"]')
        ).select_by_value(str(sem))
        driver.find_element(
            By.XPATH,
            '//*[@id="ctl00_ContentPlaceHolder1_TextBox1"]').send_keys(captcha)
        time.sleep(1)
        driver.find_element(
            By.XPATH,
            '//*[@id="ctl00_ContentPlaceHolder1_txtrollno"]').send_keys(enroll)
        time.sleep(2)
        driver.find_element(
            By.XPATH,
            '//*[@id="ctl00_ContentPlaceHolder1_btnviewresult"]').send_keys(
                Keys.ENTER)

        time.sleep(2)
        alert = Alert(driver)
        try:
            alerttext = alert.text
            alert.accept()
        except NoAlertPresentException:
            pass
        except InvalidSessionIdException:
            pass

        if "Total Credit" in driver.page_source:
            if (firstRow):
                details = []
                rows = driver.find_elements(By.CSS_SELECTOR,
                                            "table.gridtable tbody tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 4 and '[T]' in cells[0].text:
                        details.append(cells[0].text.strip('- [T]'))
                firstRow = False
                writeCSV("Enrollment No.",
                         "Name",
                         *details,
                         sgpa="SGPA",
                         cgpa="CGPA",
                         remark="REMARK",
                         filename=filename)
            name = driver.find_element(
                "id", "ctl00_ContentPlaceHolder1_lblNameGrading").text
            grades = []
            rows = driver.find_elements(By.CSS_SELECTOR,
                                        "table.gridtable tbody tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 4 and '[T]' in cells[0].text:
                    grades.append(cells[3].text.strip())
            sgpa = driver.find_element(
                "id", "ctl00_ContentPlaceHolder1_lblSGPA").text
            cgpa = driver.find_element(
                "id", "ctl00_ContentPlaceHolder1_lblcgpa").text
            result = driver.find_element(
                "id", "ctl00_ContentPlaceHolder1_lblResultNewGrading").text

            result = result.replace(",", " ")
            name = name.replace("\n", " ")
            writeCSV(enroll,
                     name,
                     *grades,
                     sgpa=sgpa,
                     cgpa=cgpa,
                     remark=result,
                     filename=filename)
            print("Compilation Successful")

            driver.find_element(
                By.XPATH,
                '//*[@id="ctl00_ContentPlaceHolder1_btnReset"]').send_keys(
                    Keys.ENTER)

            start = start + 1
        else:
            if "Result" in alerttext:  # when enrollment number is not found
                driver.find_element(
                    By.XPATH,
                    '//*[@id="ctl00_ContentPlaceHolder1_btnReset"]').send_keys(
                        Keys.ENTER)
                start = start + 1
                noResult.append(enroll)
                print(f"Enrollment NO: {enroll} not found.")
            else:  # when captcha is wrong
                driver.find_element(
                    By.XPATH,
                    '//*[@id="ctl00_ContentPlaceHolder1_TextBox1"]').clear()
                driver.find_element(
                    By.XPATH,
                    '//*[@id="ctl00_ContentPlaceHolder1_txtrollno"]').clear()
                print("Wrong Captcha Entered")
                continue

    print(f'Enrollment Numbers not found ====> {noResult}')
    makeXslx(filename.split(".")[0])


'''
branch = input("Enter Branch of Studnent ==> ")
year = input("Enter the year of admission ==> ")
sem = input("Enter the semester ===> ")
start = int(input("Enter the starting Roll ==> "))
end = int(input("Enter the ending Roll ==> "))
resultFound(start,end,branch.upper(),year,sem)


    '''

app = Flask(__name__)


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/submit', methods=['POST'])
def submit():
    branch = request.form['branch']
    year = request.form['year']
    sem = int(request.form['sem'])
    start = int(request.form['start'])
    end = int(request.form['end'])

    resultFound(start, end, branch.upper(), year, sem)

    return f"""
    <h2>✅ Result fetching completed for {branch.upper()} Sem {sem}</h2>
    """


if __name__ == '__main__':
    app.run(debug=True)
