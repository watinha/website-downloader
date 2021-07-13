import sys, os

from time import sleep
from appium import webdriver

ind = -1 if len(sys.argv) < 2 else int(sys.argv[1])

def collect (url):
    desired_capabilities = {
        "platformName": "Android",
        "deviceName": "pixel",
        "browserName": "Chrome",
        "automationName": "UiAutomator2",
        "nativeWebScreenshot": True
    }

    driver = webdriver.Remote('http://host.docker.internal:4723/wd/hub', desired_capabilities)
    driver.get(url)

    sleep(10)

    html = driver.execute_script('''
        let scripts = document.querySelectorAll('script'),
            head = document.querySelector('head'),
            base = document.createElement('base'),
            html = document.querySelector('html');
        base.href = '%s';
        head.appendChild(base);
        for (let i = 0; i < scripts.length; i++) {
            const target = scripts[i];
            if (target.parentElement)
                target.parentElement.removeChild(target);
        }
        return html.outerHTML;
    ''' % (url))

    driver.close()
    sleep(10)

    return html

urls_file = open('./url_list.txt', 'r')
urls = urls_file.readlines()
urls_file.close()

for idx, url in enumerate([ url.rstrip() for url in urls ]):
    if ind > idx:
        print('collected %s in folder %d.' % (url, idx))
    else:
        print('collecting %s in folder %d...' % (url, idx))

        html = collect(url)

        folder = './static/%d' % (idx)
        if not os.path.exists(folder):
            os.mkdir(folder)

        f = open('%s/index.html' % (folder), 'wt')
        f.write(html)
        f.close()

driver.quit()
