import sys
import scraper as amzn


while True:
    print('=========== Amzn Fetch ==========')
    print('| 1. Scraping By Keywords       |')
    print('| 2. Exit                       |')
    print('=================================')
    menu = input('Type 1/2: ')
    if menu == '1':
        kwd = input('Input ur keywords: ')
        kw = kwd.replace(' ', '+')
        amzn.search_keyword(kw)
        back = input('\nback to menu? y/n: ')
        if back == 'y':
            continue
        else:
            break
    else:
        print('see u')
        sys.exit()
