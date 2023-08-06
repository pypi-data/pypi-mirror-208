# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dokuWikiDumper',
 'dokuWikiDumper.dump',
 'dokuWikiDumper.dump.content',
 'dokuWikiDumper.dump.html',
 'dokuWikiDumper.dump.info',
 'dokuWikiDumper.dump.media',
 'dokuWikiDumper.dump.pdf',
 'dokuWikiDumper.utils',
 'dokuWikiUploader']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.11.2,<5.0.0',
 'internetarchive>=3.3.0,<4.0.0',
 'lxml>=4.9.2,<5.0.0',
 'requests>=2.28.2,<3.0.0',
 'rich>=13.3.4,<14.0.0']

entry_points = \
{'console_scripts': ['dokuWikiDumper = dokuWikiDumper:main',
                     'dokuWikiUploader = dokuWikiUploader:main']}

setup_kwargs = {
    'name': 'dokuwikidumper',
    'version': '0.1.29',
    'description': 'A tool for archiving DokuWiki',
    'long_description': '# DokuWiki Dumper\n\n> A tool for archiving DokuWiki.\n\nRecommend using `dokuWikiDumper` on _modern_ filesystems, such as `ext4` or `btrfs`. `NTFS` is not recommended because of it denys many special characters in filename.\n\n## Requirements\n\n### dokuWikiDumper\n\n- Python 3.8+ (developed on py3.10)\n- beautifulsoup4\n- requests\n- lxml\n- rich\n\n### dokuWikiUploader\n\n> Upload wiki dump to [Internet Archive](https://archive.org/).\n> `dokuWikiUploader -h` for help.\n\n- internetarchive\n- p7zip (`7z` command) (`p7zip-full` package)\n\n## Install `dokuWikiDumper`\n\n> `dokuWikiUploader` is included in `dokuWikiDumper`.\n\n### Install `dokuWikiDumper` with `pip` (recommended)\n\n> <https://pypi.org/project/dokuwikidumper/>\n\n```bash\npip3 install dokuWikiDumper\n```\n\n### Install `dokuWikiDumper` with `Poetry` (for developers)\n\n- Install `Poetry`\n\n    ```bash\n    pip3 install poetry\n    ```\n\n- Install `dokuWikiDumper`\n\n    ```bash\n    git clone https://github.com/saveweb/dokuwiki-dumper\n    cd dokuwiki-dumper\n    poetry install\n    rm dist/ -rf\n    poetry build\n    pip install --force-reinstall dist/dokuWikiDumper*.whl\n    ```\n\n## Usage\n\n```bash\nusage: dokuWikiDumper [-h] [--content] [--media] [--html] [--pdf] [--current-only] [--skip-to SKIP_TO] [--path PATH] [--no-resume] [--threads THREADS]\n                      [--insecure] [--ignore-errors] [--ignore-action-disabled-edit] [--ignore-disposition-header-missing] [--trim-php-warnings]\n                      [--delay DELAY] [--retry RETRY] [--hard-retry HARD_RETRY] [--parser PARSER] [--username USERNAME] [--password PASSWORD]\n                      [--cookies COOKIES] [--auto]\n                      url\n\ndokuWikiDumper Version: 0.1.20\n\npositional arguments:\n  url                   URL of the dokuWiki (provide the doku.php URL)\n\noptions:\n  -h, --help            show this help message and exit\n  --current-only        Dump latest revision, no history [default: false]\n  --skip-to SKIP_TO     !DEV! Skip to title number [default: 0]\n  --path PATH           Specify dump directory [default: <site>-<date>]\n  --no-resume           Do not resume a previous dump [default: resume]\n  --threads THREADS     Number of sub threads to use [default: 1], not recommended to set > 5\n  --insecure            Disable SSL certificate verification\n  --ignore-errors       !DANGEROUS! ignore errors in the sub threads. This may cause incomplete dumps.\n  --ignore-action-disabled-edit\n                        Some sites disable edit action for anonymous users and some core pages. This option will ignore this error and textarea not\n                        found error.But you may only get a partial dump. (only works with --content)\n  --ignore-disposition-header-missing\n                        Do not check Disposition header, useful for outdated (<2014) DokuWiki versions [default: False]\n  --trim-php-warnings   Trim PHP warnings from HTML [default: False]\n  --delay DELAY         Delay between requests [default: 0.0]\n  --retry RETRY         Maximum number of retries [default: 5]\n  --hard-retry HARD_RETRY\n                        Maximum number of retries for hard errors [default: 3]\n  --parser PARSER       HTML parser [default: lxml]\n  --username USERNAME   login: username\n  --password PASSWORD   login: password\n  --cookies COOKIES     cookies file\n  --auto                dump: content+media+html, threads=5, ignore-action-disable-edit. (threads is overridable)\n\nData to download:\n  What info download from the wiki\n\n  --content             Dump content\n  --media               Dump media\n  --html                Dump HTML\n  --pdf                 Dump PDF [default: false] (Only available on some wikis with the PDF export plugin) (Only dumps the latest PDF revision)\n```\n\nFor most cases, you can use `--auto` to dump the site.\n\n```bash\ndokuWikiDumper https://example.com/wiki/ --auto\n```\n\nwhich is equivalent to\n\n```bash\ndokuWikiDumper https://example.com/wiki/ --content --media --html --threads 5 --ignore-action-disabled-edit\n```\n\n> Highly recommend using `--username` and `--password` to login (or using `--cookies`), because some sites may disable anonymous users to access some pages or check the raw wikitext.\n\n`--cookies` accepts a Netscape cookies file, you can use [cookies.txt Extension](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) to export cookies from Firefox. It also accepts a json cookies file created by [Cookie Quick Manager](https://addons.mozilla.org/en-US/firefox/addon/cookie-quick-manager/).\n\n## Dump structure\n\n<!-- Dump structure -->\n| Directory or File       | Description                                 |\n|-----------              |-------------                                |\n| `attic/`                | old revisions of page. (wikitext)           |\n| `dumpMeta/`             | (dokuWikiDumper only) metadata of the dump. |\n| `dumpMeta/check.html`   | ?do=check page of the wiki.                 |\n| `dumpMeta/config.json`  | dump\'s configuration.                       |\n| `dumpMeta/favicon.ico`  | favicon of the site.                        |\n| `dumpMeta/files.txt`    | list of filename.                           |\n| `dumpMeta/index.html`   | homepage of the wiki.                       |\n| `dumpMeta/info.json`    | infomations of the wiki.                    |\n| `dumpMeta/titles.txt`   | list of page title.                         |\n| `html/`                 | (dokuWikiDumper only) HTML of the pages.    |\n| `media/`                | media files.                                |\n| `meta/`                 | metadata of the pages.                      |\n| `pages/`                | latest page content. (wikitext)             |\n| `*.mark`                | mark file.                                  |\n<!-- /Dump structure -->\n\n## Available Backups/Dumps\n\nI made some backups for testing, you can check out the list: <https://github.com/orgs/saveweb/projects/4>.\n\n> Some wikidump has been uploaded to IA, you can check out: <https://archive.org/search?query=subject%3A"dokuWikiDumper">\n>\n> If you dumped a DokuWiki and want to share it, please feel free to open an issue, I will add it to the list.\n\n## How to import dump to DokuWiki\n\nIf you need to import Dokuwiki, please add the following configuration to `local.php`\n\n```php\n$conf[\'fnencode\'] = \'utf-8\'; // Dokuwiki default: \'safe\' (url encode)\n# \'safe\' => Non-ASCII characters will be escaped as %xx form.\n# \'utf-8\' => Non-ASCII characters will be preserved as UTF-8 characters.\n\n$conf[\'compression\'] = \'0\'; // Dokuwiki default: \'gz\'.\n# \'gz\' => attic/<id>.<rev_id>.txt.gz\n# \'bz2\' => attic/<id>.<rev_id>.txt.bz2\n# \'0\' => attic/<id>.<rev_id>.txt\n```\n\nImport `pages` dir if you only need the latest version of the page.  \nImport `meta` dir if you need the **changelog** of the page.  \nImport `attic` and `meta` dirs if you need the old revisions **content** of the page.  \nImport `media` dir if you need the media files.\n\n`dumpMeta` and `html` dirs are only used by `dokuWikiDumper`, you can ignore it.\n\n## Information\n\n### DokuWiki links\n\n- [DokuWiki](https://www.dokuwiki.org/)\n- [DokuWiki changelog](https://www.dokuwiki.org/changelog)\n- [DokuWiki source code](https://github.com/splitbrain/dokuwiki)\n\n### Other tools\n\n- [MediaWiki Scraper](https://github.com/mediawiki-client-tools/mediawiki-scraper) (aka `wikiteam3`), a tool for archiving MediaWiki, forked from [WikiTeam](https://github.com/wikiteam/wikiteam/) and has been rewritten in Python 3.\n- [WikiTeam](https://github.com/wikiteam/wikiteam/), a tool for archiving MediaWiki, written in Python 2.\n\n## License\n\nGPLv3\n\n## Contributors\n\nThis tool is based on an unmerged PR (_8 years ago!_) of [WikiTeam](https://github.com/WikiTeam/wikiteam/): [DokuWiki dump alpha](https://github.com/WikiTeam/wikiteam/pull/243) by [@PiRSquared17](https://github.com/PiRSquared17).\n\nI ([@yzqzss](https://github.com/yzqzss)) have rewritten the code in Python 3 and added some features, also fixed some bugs.\n',
    'author': 'yzqzss',
    'author_email': 'yzqzss@yandex.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
