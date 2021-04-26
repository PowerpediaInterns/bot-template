# TODO: before starting
# 1. change the storage page
# 2. rename the bot
# 3. delete this
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================
# =============================

# =============================
# IMPORTS
# =============================
import pywikibot    # for making the bot
import requests     # for making requests to the API, in order to generate pages
import re           # for regex methods
import urllib3      # for ignoring the warnings related to making HTTP requests


# =============================
# CONSTANTS: these can be changed by the user as needed
# =============================

# the number of pages this bot will go through before stopping
PAGES_TO_GO_THROUGH = 25

# the title of the page that stores the last page this bot has seen 
# and where to pick up on a later execution
STORAGE_PAGE = "Mediawiki:TemplateBotInfo"


# =============================
# BOT DEFINITION
# =============================

class TemplateBot:
    '''
    A template for other bots.
    '''

    def __init__(self, site: pywikibot.site.APISite, reference_page_title: str):
        '''
        Creates a new bot.
        The bot will run on the given site.
        The bot will store its information on the page with the title given.
        '''
        self.site = site
        self.api_url = site.protocol() + "://" + site.hostname() + site.apipath()
        self.reference_page_title = reference_page_title

    def _get_page(self, page_name: str) -> pywikibot.Page:
        '''
        Gets a page from this bot's site.
        '''
        return pywikibot.Page(self.site, page_name)

    def _get_page_text(self, page_name: str) -> [str]:
        '''
        Gets the text for a page. Returns it as a list of lines.
        '''
        page = self._get_page(page_name)
        page_lines = page.text.split('\n')
        return page_lines

    def _pages_from(self, start_point: str) -> "page generator":
        '''
        Returns a generator with pages starting from the given page.
        The number of pages to run on is based on the constant for this module.
        '''
        # create a new request session 
        my_session = requests.Session()

        # define the necessary restrictions for the search
        api_arguments= {
            "action": "query",
            "format": "json",
            "list": "allpages",
            "apfrom": start_point,
            "aplimit": PAGES_TO_GO_THROUGH
        }

        # make the request, and store it as a json
        request = my_session.get(url=self.api_url, params=api_arguments, verify=False)
        data = request.json()

        # get and return the received page objects as a generator
        pages = data["query"]["allpages"]
        return pages

    def _get_page_start(self) -> str:
        '''
        Returns the page that this bot is supposed to start editing from,
        according to this bot's reference page.
        '''
        page = pywikibot.Page(self.site, self.reference_page_title)
        return page.text.split('\n')[0]

    def _set_page_start(self, new_start: str) -> None:
        '''
        Sets the page that this bot will start from next to the string given.
        '''
        page = pywikibot.Page(self.site, self.reference_page_title)
        page.text = new_start
        page.save("Store new page from last execution.")

    def run(self) -> None:
        '''
        Runs the bot on a certain number of pages.
        Records the last page the bot saw on a certain Mediawiki page.
        '''
        # get the pages to run on
        start_page_title = self._get_page_start()
        last_page_seen = ""
        pages_to_run = self._pages_from(start_page_title)

        # loop through pages
        for page in pages_to_run:
            # run main function
            last_page_seen = page['title']
            self.main_function(last_page_seen)

        # when done, set the page that we need to start from next
        if len(list(pages_to_run)) < PAGES_TO_GO_THROUGH:
            # if we hit the end, then loop back to beginning
            self._set_page_start("")
        else:
            # otherewise, just record the last page seen
            self._set_page_start(last_page_seen)

    def main_function(self, page: str) -> None:
        '''
        Put the main function of your bot here. You can use the parameter "page,"
        which gives you the title of the page you're working on. In addition,
        the variable "page_line" below gives you a list of all lines
        in the page."
        '''
        page_lines: [str] = self._get_page_text(page)


# =============================
# SCRIPT
# =============================

if __name__ == "__main__":
    # ignore warning due to making HTTP request (rather than HTTPS)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # create the bot
    bot = TemplateBot(
        site=pywikibot.Site(),
        reference_page_title=STORAGE_PAGE
    )

    # run the bot
    bot.run()

