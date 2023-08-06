# Latest Indonesia Earthquake
This package will get the latest earthquake from BMKG | Meteorological, Climatological, and Geophysical Agency.

##How to use ?
```
import gempaterkini

if __name__ == '__main__':
    result = gempaterkini.ekstraksi_data()
    gempaterkini.tampilkan_data(result)
```

##How does it work ?
This package will scrape from [BMKG](https://www.bmkg.go.id) to get latest earthquake information in Indonesia

This package will use Beautifulsoup4 to produce output in the form of JSON which is ready to use in web or mobile application