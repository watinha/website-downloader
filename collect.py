import sys, os

from time import sleep
from appium import webdriver

ind = -1 if len(sys.argv) < 2 else int(sys.argv[1])

if len(sys.argv) < 3:
    sys.stderr('there should be another argument: desktop/mobile\n')
    sys.exit(1)

mode = sys.argv[2]

def get_driver (mode):
    if mode == 'mobile':
        desired_capabilities = {
            "platformName": "Android",
            "deviceName": "pixel",
            "browserName": "Chrome",
            "automationName": "UiAutomator2",
            "nativeWebScreenshot": True
        }
        return webdriver.Remote('http://host.docker.internal:4723/wd/hub', desired_capabilities)
    if mode == 'desktop':
        desired_capabilities = {
            "browserName": "Chrome",
        }
        return webdriver.Remote('http://host.docker.internal:4444/wd/hub', desired_capabilities)

def collect (url):
    driver = get_driver(mode)
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

        folder = './%s/%d' % (mode, idx)
        if not os.path.exists(folder):
            os.mkdir(folder)

        f = open('%s/index.html' % (folder), 'wt')
        f.write(html)
        f.close()

driver.quit()
