## Introduction

This here is a Python interface module meant to streamline obtaining macroeconomic data from Zypl.ai's alternative data API macro endpoint. It offers a few simple methods to obtain the data from server and store it locally for future usage, whatever that may be.
Please keep in mind that for succesfull usage of this module it is absolutely essential for you to be in a good mood and healthy disposition, otherwise it might not work. To be fair, it might not work either way, but if you meet the requirement stated above you, at the very least, won't get upset by this fact nearly as much.

## Usage

This module is obtained from pip with the usual installation line:
```
pip install zypl_macro
```
If you're not running your machine under Windows or do not know how to use pip, please refer [here](https://pip.pypa.io/en/stable/) for pointers. It is all very straightforward.

After installing the module first order of business is to import and instantiate its utility class, like so:
```
from zypl_macro.library import DataGetter

getter_instance = DataGetter()
```

After this you're going to have to provide authorization token aka API key in order to be allowed to query data endpoint. It is done via a dedicated method:
```
getter_instance.auth('your-very-very-secret-token')
```
You can get an API key from zypl's alternative data API server administration, if they'll feel like providing you with one. Please don't lose it.
Once you succesfully got an instance of the class in your code and provided it with the token, you can start querying data. For now there are three main methods you can utilize.

### get_countries

You can obtain the list of all the countries supported in alt data system calling this method.
```
getter_instance.get_countries()
```
Please note that the result will be stored in a csv file in the directory you launch your script from. It doesn't prompt anything in console.

### get_indicators

Works similar to the previous one and provides you with a list of all the macroeconomic indicators in the database. You can call with a country specified in order to get only indicators pertaining to that country, otherwise you're gonna get them all.
```
getter_instance.get_indicators(country='Uzbekistan')
```
Results are also stored in a csv file near your executing script.

### get_data

This is the main method that allows you to obtain the data itself. The only mandatory argument is the country you want your data on:
```
getter_instance.get_data(country='Tajikistan')
```

You can also provide it with `start` and `end` arguments to specify the date range you want to get your data in. Dates must be in iso format, e.g. YYYY-MM-DD.
```
getter_instance.get_data(country='Tajikistan', start='2020-02-01', end='2022-02-01')
```
You can provide either of these arguments or both of them or none, it'll be fine.

## Misc
All the error messages, and there is quite a few, are ouput to console. So you should keep an eye it in case of something not working properly.

If alt data API endpoint gets changed or moved somewhere (it shouldn't, but weirder things has been known to happen), this module is not going to work properly. In this case, and if you happen to know its new living address, you can call _set_url method to point the module there. Please don't touch this method otherwise, things will break.

On the other note, every indicator in the has the `frequency` parameter associated with it specifying the period data is gathered at. These are typically associated with a certain group of indicators each and go like "Daily", "Monthly", "Quarterly" and "Yearly". It is entirely optional, but you can provide this parameter to get_data too (i.e. get_data(..., frequency="Monthly")) if you want to narrow down the dataset you get.