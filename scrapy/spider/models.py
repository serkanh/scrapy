"""
Base class for Scrapy spiders

See documentation in docs/topics/spiders.rst
"""
from zope.interface import Interface, Attribute, invariant, implements
from twisted.plugin import IPlugin

from scrapy import log
from scrapy.http import Request
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.trackref import object_ref

def _valid_domain_name(obj):
    """Check the domain name specified is valid"""
    if not obj.domain_name:
        raise ValueError("Spider 'domain_name' attribute is required")

class ISpider(Interface, IPlugin) :
    """Interface to be implemented by site-specific web spiders"""

    domain_name = Attribute("The domain name of the site to be scraped.")

    invariant(_valid_domain_name)

class BaseSpider(object_ref):
    """Base class for scrapy spiders. All spiders must inherit from this
    class.
    """

    implements(ISpider)

    # XXX: class attributes kept for backwards compatibility
    domain_name = None
    start_urls = []
    extra_domain_names = []

    def __init__(self, domain_name=None):
        if domain_name is not None:
            self.domain_name = domain_name
        # XXX: create instance attributes (class attributes were kept for
        # backwards compatibility)
        if not self.start_urls:
            self.start_urls = []
        if not self.extra_domain_names:
            self.extra_domain_names = []

    def log(self, message, level=log.DEBUG):
        """Log the given messages at the given log level. Always use this
        method to send log messages from your spider
        """
        log.msg(message, spider=self, level=level)

    def start_requests(self):
        reqs = []
        for url in self.start_urls:
            reqs.extend(arg_to_iter(self.make_requests_from_url(url)))
        return reqs

    def make_requests_from_url(self, url):
        return Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        """This is the default callback function used to parse the start
        requests, although it can be overrided in descendant spiders.
        """
        pass

    def __str__(self):
        return "<%s %r>" % (type(self).__name__, self.domain_name)

    __repr__ = __str__
