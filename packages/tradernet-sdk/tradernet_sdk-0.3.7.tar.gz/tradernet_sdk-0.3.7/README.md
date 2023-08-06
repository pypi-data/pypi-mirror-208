# tradernet-sdk

Public Python API for TraderNet

## Installation

Installing tradernet with pip is straightforward:  
`python -m pip install tradernet-sdk`  
Instead of `python` you can use here and further `pypy3` depending on your preferences.

## Usage

Import the client library into your script:  
`from tradernet import TraderNetAPI`  
Initialize it with your credentials:  
`api = TraderNetAPI('public_key', 'private_key', 'login', 'passwd')`  
or create a config file `tradernet.ini` with the following content:  
```
[auth]
public   = public_key
private  = private_key
login    = login
password = passwd
```
and initialize the client with `api = TraderNetAPI.from_config('tradernet.ini')`  
Call any of its public methods, for example:  
`api.user_info()`  

### How to trade

Usage of the trading interface is similar to common API. Import and instantiate `Trading` class:  
```
from tradernet import Trading


order = Trading.from_config('tradernet.ini')
```
Now let's buy 1 share of FRHC.US at the market price:  
```
order.buy('FRHC.US')
```

### Advanced techniques

One can import the core class to write their own methods:
```
from tradernet import TraderNetCore


class MyTNAPI(TraderNetCore):
    pass
```
This allows using sophisticated request methods for TN API like
`TraderNetCore.authorized_request`.  

One can have several instances of the API serving different purposes:  
```
config = TraderNetCore.from_config('tradernet.ini')
order = Trading.from_instance(config)
```
The instance `config` stores the credentials, and `order` can be used to trade and may be destroyed after trades completed while `config` is still can be used to instantiate other classes.


### Websockets

Websocket API can be accessed via another class `TraderNetWSAPI`. It
implements asynchronous interface for TraderNet API, and its usage is a bit
more complicated:  
```
from tradernet import TraderNetCore, TraderNetWSAPI


async def main() -> None:
    api = TraderNetCore.from_config('tradernet.ini')
    async with TraderNetWSAPI(api) as wsapi:  # type: TraderNetWSAPI
        async for quote in wsapi.market_depth('FRHC.US'):
            print(quote)
```

### Legacy API

The library also has the legacy `PublicApiClient.py` which provides almost
the same functionality as most of TraderNet users used to:
```
from tradernet import NtApi


pub_ = '[public Api key]'
sec_ = '[secret Api key]'
cmd_ = 'getPositionJson'
res = NtApi(pub_, sec_, NtApi.V2)
print(res.sendRequest(cmd_))
```
The only difference is that one doesn't have to decode the content of the
response as before.

### Options

The notation of options in TraderNet now can easily be deciphered:
```
from tradernet import TraderNetOption


option = TraderNetOption('+FRHC.16SEP2022.C55')
print(option)  # FRHC.US @ 55 Call 2022-09-16
```
or the scary old notation:
```
from tradernet import DasOption


option = DasOption('+FRHC^C7F45.US')
print(option)  # FRHC.US @ 45 Call 2022-07-15
```

### Wrapping market data

Another feature is to get handy pandas.DataFrame objects with market data:
```
from tradernet import TraderNetSymbol, TraderNetAPI


api = TraderNetAPI('public_key', 'private_key', 'login', 'passwd')
symbol = TraderNetSymbol('AAPL.US', api)
symbol.get_data()
print(symbol.market_data.head().to_markdown())
# | date                |     high |      low |     open |    close |      volume |
# |:--------------------|---------:|---------:|---------:|---------:|------------:|
# | 1980-12-12 00:00:00 | 0.128876 | 0.12834  | 0.12834  | 0.12834  | 1.17258e+08 |
# | 1980-12-15 00:00:00 | 0.122224 | 0.121644 | 0.122224 | 0.121644 | 4.39712e+07 |
# | 1980-12-16 00:00:00 | 0.113252 | 0.112716 | 0.113252 | 0.112716 | 2.6432e+07  |
# | 1980-12-17 00:00:00 | 0.116064 | 0.115484 | 0.115484 | 0.115484 | 2.16104e+07 |
# | 1980-12-18 00:00:00 | 0.119412 | 0.118876 | 0.118876 | 0.118876 | 1.83624e+07 |
```

## License

The package is licensed under permissive MIT License. See the `LICENSE` file in
the top directory for the full license text.
