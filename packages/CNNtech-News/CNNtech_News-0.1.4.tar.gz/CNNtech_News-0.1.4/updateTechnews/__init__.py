import bs4
import requests

description = 'To get the most update of Tech news in CNN https://edition.cnn.com/business/tech'

def news_data():
    try:
        content = requests.get('https://edition.cnn.com/business/tech')
    except Exception:
        return None

    if content.status_code == 200:
        soup = bs4.BeautifulSoup(content.text, 'html.parser')

        result = soup.find('div', {'class': 'container_lead-plus-headlines-with-images__cards-wrapper'})
        result = result.findChildren('span')

        i = 0

        newsOne = None
        newsTwo = None
        newsThree = None
        newsFour = None
        newsFive = None
        newsSix = None
        newsSeven = None
        newsEight = None

        for res in result:
            if i == 0:
                newsOne = res.text
            elif i == 1:
                newsTwo = res.text
            elif i == 2:
                newsThree = res.text
            if i == 3:
                newsFour = res.text
            elif i == 4:
                newsFive = res.text
            elif i == 5:
                newsSix = res.text
            if i == 6:
                newsSeven = res.text
            if i == 7:
                newsEight = res.text
            i = i + 1

        tech = dict()
        tech['newsOne'] = newsOne
        tech['newsTwo'] = newsTwo
        tech['newsThree'] = newsThree
        tech['newsFour'] = newsFour
        tech['newsFive'] = newsFive
        tech['newsSix'] = newsSix
        tech['newsSeven'] = newsSeven
        tech['newsEight'] = newsEight

        return tech

    else:
        return None

def show_news(result):
    if result is None:
        print("Update News Not Found")
        return

    print(description)
    print("Most Updates Technology News Today")
    print(f"News 1 > {result['newsOne']}")
    print(f"News 2 > {result['newsTwo']}")
    print(f"News 3 > {result['newsThree']}")
    print(f"News 4 > {result['newsFour']}")
    print(f"News 5 > {result['newsFive']}")
    print(f"News 6 > {result['newsSix']}")
    print(f"News 7 > {result['newsSeven']}")
    print(f"News 8 > {result['newsEight']}")

if __name__ == '__main__':
    print('Deskription Package:', description)
    result = news_data()
    show_news(result)