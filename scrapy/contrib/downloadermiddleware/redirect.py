from scrapy import log
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_meta_refresh
from scrapy.core.exceptions import IgnoreRequest
from scrapy.conf import settings


class RedirectMiddleware(object):
    """Handle redirection of requests based on response status and meta-refresh html tag"""

    def __init__(self):
        self.max_metarefresh_delay = settings.getint('REDIRECT_MAX_METAREFRESH_DELAY')
        self.max_redirect_times = settings.getint('REDIRECT_MAX_TIMES')
        self.priority_adjust = settings.getint('REDIRECT_PRIORITY_ADJUST')

    def process_response(self, request, response, spider):
        if response.status in [302, 303] and 'Location' in response.headers:
            redirected_url = urljoin_rfc(request.url, response.headers['location'])
            redirected = self._redirect_request_using_get(request, redirected_url)
            return self._redirect(redirected, request, spider, response.status)

        if response.status in [301, 307] and 'Location' in response.headers:
            redirected_url = urljoin_rfc(request.url, response.headers['location'])
            redirected = request.replace(url=redirected_url)
            return self._redirect(redirected, request, spider, response.status)

        interval, url = get_meta_refresh(response)
        if url and interval < self.max_metarefresh_delay:
            redirected = self._redirect_request_using_get(request, url)
            return self._redirect(redirected, request, spider, 'meta refresh')

        return response

    def _redirect(self, redirected, request, spider, reason):
        ttl = request.meta.setdefault('redirect_ttl', self.max_redirect_times)
        redirects = request.meta.get('redirect_times', 0) + 1

        if ttl and redirects <= self.max_redirect_times:
            redirected.meta['redirect_times'] = redirects
            redirected.meta['redirect_ttl'] = ttl - 1
            redirected.dont_filter = request.dont_filter
            redirected.priority = request.priority + self.priority_adjust
            log.msg("Redirecting (%s) to %s from %s" % (reason, redirected, request),
                    spider=spider, level=log.DEBUG)
            return redirected
        else:
            log.msg("Discarding %s: max redirections reached" % request,
                    spider=spider, level=log.DEBUG)
            raise IgnoreRequest

    def _redirect_request_using_get(self, request, redirect_url):
        redirected = request.replace(url=redirect_url, method='GET', body='')
        redirected.headers.pop('Content-Type', None)
        redirected.headers.pop('Content-Length', None)
        return redirected


