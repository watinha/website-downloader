f = open('htmls-undergrad.txt')
filenames = f.read().split('\n')
filenames = [ filename for filename in filenames if len(filename) > 0 ]

for filename in filenames:
    html = open(filename).read()
    html = html.replace('<head>', '<head><meta name="google" content="notranslate">', 1)
    new = filename.replace('.html', '.notranslate.html', 1)
    n_f = open(new, 'wt')
    n_f.write(html)
    n_f.close()
