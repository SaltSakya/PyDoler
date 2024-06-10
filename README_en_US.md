# PyDoler ![Static Badge](https://img.shields.io/badge/version-0.2--beta-orange)
![Static Badge](https://img.shields.io/badge/license-MIT-green)
![Static Badge](https://img.shields.io/badge/Python-3.10.6-blue)
![Static Badge](https://img.shields.io/badge/requests-2.31.0-red)

This is a scrawler framework written by Python.

## Usage
Implement a class derived from `Agent`, and rewrite the `preprocess` and `fill_list` methods.  
Sample code is as follows:
``` python
# sample.py

class SampleAgent(Agent):
    def preprocess(self):
        self.dirname = "SampleDirname"

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
### Must rewrite methods
* `preprocess(self)`: **Must** rewrite this method. You **must** set the value of `self.dirname` in this method, and content download later will save in this directory in relative path.
``` python
def preprocess(self):
    self.dirname = "SampleDirname"
```

* `fill_list(self)`: **Must** rewrite this method. You should fill the `self.url_list` with the urls you want to download. Be aware that you should use `self.lock.acquire()` and `self.lock.release()` to ensure thread safety.
``` python
def fill_list(self):
    for i in range(10):
        self.lock.acquire()
        self.url_list.append(self.url + str(i))
        self.lock.release()
```
### Optional rewrite methods
* `__init__(self, url, **kwargs)`: You can rewrite the default parameters in this method.
``` python
def __init__(self, url, stream=True, **kwargs):
    kwargs['stream'] = stream
    super().__init__(url, **kwargs)
```
* `url_preprocess(self)`: You can preprocess the url in this method.
> When should I rewrite this method？
> * For example, you want to download a webpage and its subpages, and you want to achieve this goal even you pass a subpage's url to the agent. To achieve this goal, you can rewrite this method and get the parent page's url in this method;
> * Or, you can rewrite this method to ensure the url is valid.
``` python
    def url_preprocess(self):
        if self.is_valid(self.url):
            self.url = "other_url"
        else:
            raise InvalidUrlError(self.url)
```
* `postprocess(self)`: You can define the behavior after all file downloaded. For example, you can zip the directory as a zip file here.
``` python
def postprocess(self):
    zip_dir(os.path.join(self.download_dir, self.dirname))
```
