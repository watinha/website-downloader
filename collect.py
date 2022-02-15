import sys, os

from time import sleep
#from appium import webdriver
from selenium import webdriver as webdriver2

ind = -1 if len(sys.argv) <= 2 else int(sys.argv[2])

if len(sys.argv) < 2:
    sys.stderr('there should be another argument: desktop/mobile\n')
    sys.exit(1)

mode = sys.argv[1]

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
        options = webdriver2.ChromeOptions()
        options.headless = True
        return webdriver2.Remote(
            command_executor='http://host.docker.internal:4444/wd/hub',
            desired_capabilities=options.to_capabilities())


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

companies = [ url[11:].split('.')[0] for url in urls ]
to_remove = []
for index, company in enumerate(companies):
    if (company in companies[index+1:]):
        to_remove.append(companies[index+1:].index(company) + index + 1)
print('Removed considering company duplicate in alexa list: %s' % ([ urls[i] for i in to_remove ]))
urls = [ url for i, url in enumerate(urls) if i not in to_remove ]

for idx, url in enumerate([ url.rstrip() for url in urls ]):
    err_count = 0
    while err_count < 5:
        if ind > idx:
            print('collected %s in folder %d.' % (url, idx))
            err_count = 5
        else:
            try:
                print('collecting %s in folder %d...' % (url, idx))

                html = collect(url)

                folder = './%s/%d' % (mode, idx)
                if not os.path.exists(folder):
                    os.mkdir(folder)

                f = open('%s/index.html' % (folder), 'wt')
                f.write(html)
                f.close()
                err_count = 5
            except:
                err_count += 1
                print(' - error in %s... %d' % (url, err_count))

driver.quit()
