# PyDoler ![Static Badge](https://img.shields.io/badge/version-0.2--beta-orange)
![Static Badge](https://img.shields.io/badge/license-MIT-green)
![Static Badge](https://img.shields.io/badge/Python-3.10.6-blue)
![Static Badge](https://img.shields.io/badge/requests-2.31.0-red)

这是一个使用Python编写的爬虫框架。

## 使用
请自行编写继承自 `Agent` 的子类，并重写 `preprocess` 和 `fill_list` 方法。  
示例代码:
``` python
# sample.py

class SampleAgent(Agent):
    def preprocess(self):
        self.dirname = "示例目录名"

    def fill_list(self):
        for i in range(10):
            self.lock.acquire()
            self.url_list.append(self.url + str(i))
            self.lock.release()

if __name__ == '__main__':
    url = "https://www.sample.com/"
    agent = SampleAgent(url)
    agent.download()
```
### 必须重写方法
* `preprocess(self)`：**必须**重写的方法。**必须**在此方法中设置 self.dirname，之后所有下载的内容将会被保存到相对路径下的这一目录中。
``` python
def preprocess(self):
    self.dirname = "示例目录名"
```

* `fill_list(self)`：**必须**重写的方法。在此处填充 `self.url_list`，填充到此列表内的url将实时被下载线程取出并下载。注意在填充时，需要使用 `self.lock.acquire()` 和 `self.lock.release()` 来保证线程安全。
``` python
def fill_list(self):
    for i in range(10):
        self.lock.acquire()
        self.url_list.append(self.url + str(i))
        self.lock.release()
```
### 非必须重写方法
* `__init__(self, url, **kwargs)`：在此处可以重写默认的参数。
``` python
def __init__(self, url, stream=True, **kwargs):
    kwargs['stream'] = stream
    super().__init__(url, **kwargs)
```
* `url_preprocess(self)`：在此处对 url 进行预处理。
> 何时使用？
> * 例如，你希望下载一个网页下所有子页内的文件，并希望即便给出子页的 url，也能达成这一目的，那你便可以在这里通过子页的 url 来获取父页的 url；
> * 或者，你也可以在这里确保 url 有效。
``` python
    def url_preprocess(self):
        if self.is_valid(self.url):
            self.url = "other_url"
        else:
            raise InvalidUrlError(self.url)
```
* `postprocess(self)`：在此处可以重写后处理相关功能。例如，你可以在下载完成后将全部文件压缩成压缩包。
``` python
def postprocess(self):
    zip_dir(os.path.join(self.download_dir, self.dirname))
```
