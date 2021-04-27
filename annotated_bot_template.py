'''
Prerequisites:
Make sure you can run a Pywikibot script (like the sample test scripts on Mediawiki)
and that you have logged into your wiki with a bot account.

Overview:
This is a template for a bot designed to run on Powerpedia and
testable on a Meza Mediawiki.
We are going to create a class for the bot, then create an instance of that class.
That instance object will then run a function that will loop through pages on the wiki
in alphabetical order, running the main_function() function on that page. 
Other utility functions are contained in the larger class and
are usable by that instance object.

Use:
- Change the bot's name
- Change the constants as needed (esp. the storage page)
- Adjust the main function to what the bot needs
'''

# =============================
# IMPORTS
# =============================
import pywikibot    # for making the bot
import requests     # for making requests to the API, in order to generate pages
import re           # for regex methods, useful for searching in pages
import urllib3      # for ignoring the warnings related to making HTTP requests


# =============================
# CONSTANTS: these can be changed by the user as needed
# =============================

# the number of pages this bot will go through before stopping
PAGES_TO_GO_THROUGH = 25

# the title of the page that stores the last page this bot has seen 
# and where to pick up on a later execution

# we typically use the Powerpedia namespace here so that the bot's info page
# cannot be edited by normal users
STORAGE_PAGE = "Powerpedia:TemplateBotInfo"


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
        The bot will run on the given site, which is a pywiki object. 
        The bot will store its information on the page with the title given. 
        '''
        # The typical site this bot will run on is the pywikibot.Site(), which is 
        # a site object for the site you are currently logged into on pywikibot. 
        self.site = site

        # note that the site protocol on Meza wikis will often be HTTP
        # but the requests library wants you to make all your requests to HTTPS
        # this is why we need the urllib library,
        # to ignore any errors that we get from making requests to HTTP
        self.api_url = site.protocol() + "://" + site.hostname() + site.apipath()

        # this is the name of the page that the bot will use to store the
        # last page the bot has run on
        self.reference_page_title = reference_page_title

    def _get_page(self, page_name: str) -> pywikibot.Page:
        '''
        Gets a page from this bot's site.
        '''
        # here, we return a page object

        # page.text
        # the page object has a text attribute containing all the
        # text of the page as a string

        # page.save()
        # the page object has a save() method that will save the 
        # current text

        # editing
        # do page.text = "whatever text you want"
        # and then page.save("save message (like a commit message)")
        # to save your edit to the page
        return pywikibot.Page(self.site, page_name)

    def _get_page_text(self, page_name: str) -> [str]:
        '''
        Gets the text for a page. Returns it as a list of lines.
        '''
        # get the text for the page
        page = self._get_page(page_name)

        # split it along each carriage return to get a list of lines
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
            "aplimit": PAGES_TO_GO_THROUGH + 1
        } 

        # make the request, and store it as a json
        request = my_session.get(url=self.api_url, params=api_arguments, verify=False)
        data = request.json()

        # get and return the received page objects as a generator
        pages = data["query"]["allpages"]

        # you can loop through this pages object to get a list of objects
        # each object has a 'title' attribute accessible by obj['title']
        # which is useful for getting pages off the wiki
        return pages

    def _get_page_start(self) -> str:
        '''
        Returns the page that this bot is supposed to start editing from,
        according to this bot's reference page. 
        '''
        # we'll get the page object for the reference page (see above functions)
        page = pywikibot.Page(self.site, self.reference_page_title)

        # then we'll return the first line of that page, which should contain the 
        # page title we want 
        return page.text.split('\n')[0]
    
    def _set_page_start(self, new_start: str) -> None:
        '''
        Sets the page that this bot will start from next to the string given.
        '''
        # we'll get the page object for the reference page (see above functions)
        page = pywikibot.Page(self.site, self.reference_page_title)

        # change the text to the new place to start
        page.text = new_start

        # save our changes, with a save message
        page.save("Store new page from last execution.")

    def run(self) -> None:
        '''
        Runs the bot on a certain number of pages.
        Records the last page the bot saw on a certain Mediawiki page.
        '''
        # get the pages to run on (see above functions)
        start_page_title = self._get_page_start()
        last_page_seen = ""

        # get the list of pages (see above functions)
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
