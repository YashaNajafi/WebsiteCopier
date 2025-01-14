#----------<Library>----------
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import logging
import fake_useragent
#----------<Functions>----------
class WebsiteCopier:
    def __init__(self, URL : str, OutPut_Dir : str = "WebsiteCopy"):
        self.base_url = URL
        self.base_domain = urlparse(URL).netloc
        self.output_dir = OutPut_Dir
        self.visited_urls = set()
        self.failed_urls = set()
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': str(fake_useragent.UserAgent().random)
        }

        logging.basicConfig(
            filename='website_copier.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def DownloadAgain(self, URL : str, MaxRetries : int = 3):
        for attempt in range(MaxRetries):
            try:
                response = self.session.get(URL, timeout=30)
                response.raise_for_status()
                return response.content
            except Exception as e:
                if attempt == MaxRetries - 1:
                    logging.error(f"Failed to download {URL} after {MaxRetries} attempts: {str(e)}")
                    self.failed_urls.add(URL)
                    return None
                time.sleep(1)
        return None

    def SaveContent(self, Content, FilePath : str):
        try:
            os.makedirs(os.path.dirname(FilePath), exist_ok=True)
            with open(FilePath, 'wb') as f:
                f.write(Content)
            return True
        except Exception as e:
            logging.error(f"Failed to save {FilePath}: {str(e)}")
            return False

    def GetLocalPath(self, URL : str):
        parsed = urlparse(URL)
        path = parsed.path
        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'
        elif not any(path.endswith(ext) for ext in ['.html', '.css', '.js', '.jpg', '.png', '.gif']):
            path += '.html'

        return os.path.join(self.output_dir, parsed.netloc, path.lstrip('/'))

    def DownloadAssets(self, URL):
        if URL in self.visited_urls or URL in self.failed_urls:
            return

        self.visited_urls.add(URL)
        content = self.DownloadAgain(URL)
        if content:
            local_path = self.GetLocalPath(URL)
            if self.SaveContent(content, local_path):
                logging.info(f"Successfully downloaded: {URL}")
                return content
        return None

    def ExtractUrls(self, HTML_Content , BaseURL):
        soup = BeautifulSoup(HTML_Content, 'html.parser')
        urls = set()

        patterns = {
            'a': 'href',
            'link': 'href',
            'script': 'src',
            'img': 'src',
            'source': 'src',
            'video': 'src',
            'audio': 'src',
        }

        for tag, attr in patterns.items():
            for element in soup.find_all(tag):
                url = element.get(attr)
                if url:
                    absolute_url = urljoin(BaseURL, url)
                    if urlparse(absolute_url).netloc == self.base_domain:
                        urls.add(absolute_url)

        return urls

    def ProcessPage(self, URL):
        content = self.DownloadAssets(URL)
        if not content:
            return

        if URL.endswith(('.html', '/')) or not urlparse(URL).path.endswith(('.css', '.js', '.jpg', '.png', '.gif')):
            urls = self.ExtractUrls(content, URL)
            for new_url in urls:
                if new_url not in self.visited_urls and new_url not in self.failed_urls:
                    self.ProcessPage(new_url)

    def CopyWebsite(self,Version : int = 1):
        logging.info(f"Starting to copy website: {self.base_url}")
        if Version == 1:
            self.ProcessPage(self.base_url)
            logging.info(f"Website copy complete. Downloaded {len(self.visited_urls)} files, "
                        f"Failed {len(self.failed_urls)} files")
            return self.visited_urls, self.failed_urls
        elif Version == 2:
            json_data = {
                'url': self.base_url,
                'renameAssets': False,
                'saveStructure': False,
                'alternativeAlgorithm': False,
                'mobileVersion': False,
            }

            Json = requests.post('https://copier.saveweb2zip.com/api/copySite', headers=self.session.headers, json=json_data).json()
            response = requests.get(f'https://copier.saveweb2zip.com/api/downloadArchive/{str(Json["md5"])}',headers=self.session.headers)

            with open(f"Download/{self.GetLocalPath(self.base_url)}.zip", 'wb') as f:
                f.write(response.content)

class GetLink:
    def __init__(self,URL : str):
        self.url = URL

        self.headers = {
            'User-Agent': str(fake_useragent.UserAgent().random)
        }

    def __CheckURL(self):
        url = self.url.lower()
        if url[:26] != "https://www.rtl-theme.com/":
            return False

        url = url.replace(url[:26],"")
        url = url.replace("/","")

        if "html" in url.rsplit("-"):
            return True
        else:
            return False

    def __GetBaseURL(self):
        if self.__CheckURL():
            Content = requests.get(self.url,headers=self.headers).content
            soup = BeautifulSoup(Content, 'html.parser')

            Buttons = soup.find_all('button', {
            'class': 'btn btn-orange float-left product-demo',
            'data-type': 'ProductPreview'
            })

            data_targets = []
            for button in Buttons:
                data_target = button.get('data-target')
                if data_target:
                    data_targets.append(data_target)

            return data_targets[0]
        else:
            return False

    def GetURL(self):
        ViewURL = self.__GetBaseURL()
        Content = requests.get(ViewURL,self.headers).content
        soup = BeautifulSoup(Content, "html.parser")
        iframe = soup.find("iframe")
        if iframe and "src" in iframe.attrs:
            iframe_src = iframe["src"]
        return iframe_src
