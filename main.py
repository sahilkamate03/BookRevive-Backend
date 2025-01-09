import os
import datetime

import pytz
import mechanicalsoup
from dotenv import load_dotenv

load_dotenv()

url = "http://14.139.108.229/W27"


def main():
    print("Scheduled task is running... " + str(datetime.datetime.now()))

    browser = mechanicalsoup.StatefulBrowser()
    login_url = url + "/login.aspx"

    browser.open(login_url)
    browser.get_current_page()
    browser.select_form()
    browser.get_current_form()

    browser["txtUserName"] = os.getenv("REG_NO")
    browser["Password1"] = os.getenv("PASSWORD")
    browser.submit_selected()

    info_url = url + "/MyInfo/w27MyInfo.aspx"
    browser.open(info_url)

    page = browser.get_current_page()
    table = page.find_all(
        "table", attrs={"id": "ctl00_ContentPlaceHolder1_CtlMyLoans1_grdLoans"}
    )

    if table:
        tds = table[0].find_all("td")
        book_data = []
        for td in tds:
            book_data.append(td.text.replace("\n", ""))

        # no_of_book_issued = len(book_data) // 9
    else:
        return

    # Manually create data rows
    num_columns = 9
    data_rows = [
        book_data[i : i + num_columns] for i in range(0, len(book_data), num_columns)
    ]

    columns = [
        "AccNum",
        "Title",
        "Author",
        "Borrowed On",
        "Due On",
        "Status",
        "Recalled",
        "FineDue",
        "Reissue",
    ]

    # Prepare a list of dictionaries for each row
    books = []
    for row in data_rows:
        book = dict(zip(columns, row))
        books.append(book)

    # Collect "Reissue" button names
    reissue_btns = table[0].find_all("input")
    issue_book_btn = [btn.attrs["name"] for btn in reissue_btns]

    # Add the 'Reissue' button names to each book entry
    for i in range(len(books)):
        books[i]["Reissue"] = issue_book_btn[i] if i < len(issue_book_btn) else None

    indian_current_date = datetime.datetime.now(pytz.timezone("Asia/Kolkata")).date()
    # Loop through each book to check if it should be reissued
    for book in books:
        due_date_str = book["Due On"]
        due_date = datetime.datetime.strptime(due_date_str.strip(), "%d-%b-%Y").date()
        if due_date <= indian_current_date:
            browser.select_form('form[action="./w27MyInfo.aspx"]')
            browser.submit_selected(btnName=book["Reissue"])
            print("Book Reissued: ", book["Title"])


if __name__ == "__main__":
    main()
