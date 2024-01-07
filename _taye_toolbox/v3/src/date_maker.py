import pyperclip
from datetime import datetime

def get_formatted_date(date="today"):
    if date == "today":
        date = datetime.today()
    else:
        date = datetime.strptime(date, "%Y-%m-%d")
    formatted_date = date.strftime("%Y%m%d_%A")
    return formatted_date

if __name__ == "__main__":
    _date = input("\nUse today's date, right? (Y/N): ")
    if _date.upper() == "Y":
        formatted_date = get_formatted_date()
    else:
        _date = input("\nNo worries! Please enter date in YYYY-MM-DD format: ")
        formatted_date = get_formatted_date(_date)
    print(f"\n  OK. Date is saved to your clipboard, as {formatted_date}")
    pyperclip.copy(formatted_date)
    formatted_date