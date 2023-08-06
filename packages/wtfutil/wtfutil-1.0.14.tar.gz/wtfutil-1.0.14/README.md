# wftutil

<a href="https://pypi.python.org/pypi/wtfutil"><img src="https://img.shields.io/pypi/v/wtfutil.svg"></a>
<a href="https://pypi.python.org/pypi/wtfutil"><img src="https://img.shields.io/pypi/pyversions/wtfutil.svg"></a>
=================================================================================================================

## ☤ The Basics

WTF A Python utility / library

## ☤ Installation

Of course, the recommended installation method is `pipenv <http://pipenv.org>`\_::

```bash
pipenv install wtfutil
```

or

```bash
pip install wtfutil
```

## ☤ Features

```python
fileutil
sqlutil
notifyutil
httputil
hashutil
strutil
```

## ☤ Example

```python
from wtfutil import util
# 1. get requests session
# def requests_session(proxies=False, max_retries=1, timeout=30, debug=False, base_url=None, user_agent=None, use_cache=None):
req1 = util.requests_session(timeout=30, max_retries=1)
req1.post('http://localhost:8080/xxx')

req2 = util.requests_session(base_url='http://localhost:8080', timeout=30, max_retries=1)
req2.post('/xxx/update')
```

```python
from wtfutil import util
# send http raw
util.httpraw('''
POST /a/bbbb?id=1&type=jsp HTTP/1.1
Host: abc.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:88.0) Gecko/20100101 Firefox/88.0
Content-Length: 1
Accept-Charset: utf-8
Content-Type: multipart/; boundary=----WebKitFormBoundaryzxcxzcxz
Accept-Encoding: gzip

------WebKitFormBoundaryzxcxzcxz
Content-Disposition: form-data; name="upload";filename="f.jsp"

test
------WebKitFormBoundaryzxcxzcxz
Content-Disposition: form-data; name="submit"

submit
------WebKitFormBoundaryzxcxzcxz--
    ''')
```

```python
from wtfutil import util
# read and write file
# def read_lines(filepath, encoding='utf-8', not_exists_ok: bool = False) -> list:
urls = util.read_lines('input_url.txt')
# def read_text(filepath, encoding='utf-8', not_exists_ok: bool = False) -> str:
data = util.read_text('input.txt')
data_bytes = util.read_bytes('input.txt')
# def write_text(filepath, content, mode='w', encoding='utf-8'):
util.write_text('output.txt', 'test')
util.write_lines('output.txt', ['te','st'])
...
# like py3.9 removesuffix
util.removesuffix('test123456', '456')
util.removeprefix('test123456', 'test')
util.str_to_bool('yes')
...
```

## ☤ Thank You

Thanks for checking this library out! I hope you find it useful.

Of course, there's always room for improvement. Feel free to [https://github.com/vicrack](https://github.com/vicrack)
