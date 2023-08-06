# CNNtech_News
This package will provide you the most update of CNN Tech News

# How It Works
This Package will scrape from https://edition.cnn.com/business/tech

This package will use BeautifulSoup4 and Request, to then produce in the form of JSON that is ready to be used in web or mobile applications.

# How to Use This Package?
```
import updateTechnews

if __name__ == '__main__':
    print('Deskription Package:', description)
    result = updateTechnews.news_data()
    updateTechnews.show_news(result)
```

# Author
Hasan Gani Rachmatullah