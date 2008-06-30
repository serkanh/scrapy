"""
Auxiliary functions which doesn't fit anywhere else
"""
import re

from twisted.internet import defer, reactor
from twisted.python import failure

from scrapy.core.exceptions import UsageError
from scrapy.utils.python import flatten
from decobot.utils.text_extraction import unquote_html

def dict_updatedefault(D, E, **F):
    """
    updatedefault(D, E, **F) -> None.

    Update D from E and F: for k in E: D.setdefault(k, E[k])
    (if E has keys else: for (k, v) in E: D.setdefault(k, v))
    then: for k in F: D.setdefault(k, F[k])
    """
    for k in E:
        if isinstance(k, tuple):
            k, v = k
        else:
            v = E[k]
        D.setdefault(k, v)

    for k in F:
        D.setdefault(k, F[k])


def defer_fail(_failure):
    """same as twsited.internet.defer.fail, but delay calling errback """
    d = defer.Deferred()
    reactor.callLater(0, d.errback, _failure)
    return d


def defer_succeed(result):
    """same as twsited.internet.defer.succed, but delay calling callback"""
    d = defer.Deferred()
    reactor.callLater(0, d.callback, result)
    return d


def mustbe_deferred(f, *args, **kw):
    """same as twisted.internet.defer.maybeDeferred, but delay calling callback/errback"""
    deferred = None
    try:
        result = f(*args, **kw)
    except:
        return defer_fail(failure.Failure())
    else:
        if isinstance(result, defer.Deferred):
            return result
        elif isinstance(result, failure.Failure):
            return defer_fail(result)
        else:
            return defer_succeed(result)
    return deferred


def chain_deferred(d1, d2):
    if callable(d2):
        d2 = lambda_deferred(d2)

    def _pause(_):
        d2.pause()
        reactor.callLater(0, d2.unpause)
        return _

    def _reclaim(_):
        return d2

    #d1.addBoth(_pause) ## needs more debugging before reenable it
    d1.chainDeferred(d2)
    d1.addBoth(_reclaim)
    return d1


def lambda_deferred(func):
    deferred = defer.Deferred()
    def _success(res):
        d = func()
        d.callback(res)
        return d
    def _fail(res):
        d = func()
        d.errback(res)
        return d
    return deferred.addCallbacks(_success, _fail)


def memoize(cache, hash):
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = hash(*args, **kwargs)
            if key in cache:
                return defer_succeed(cache[key])

            def _store(_):
                cache[key] = _
                return _

            result = func(*args, **kwargs)
            if isinstance(result, defer.Deferred):
                return result.addBoth(_store)
            cache[key] = result
            return result
        return wrapper
    return decorator


def deferred_degenerate(generator):
    generator = iter(generator)
    deferred = defer.Deferred()
    result = []
    def _next():
        try:
            result.append(generator.next())
        except StopIteration:
            reactor.callLater(0, deferred.callback, result)
        except:
            reactor.callLater(0, deferred.errback, failure.Failure())
        else:
            reactor.callLater(0, _next)
    _next()
    return deferred


def stats_getpath(dict_, path, default=None):
    for key in path.split('/'):
        if key in dict_:
            dict_ = dict_[key]
        else:
            return default
    return dict_

def load_class(class_path):
    """Load a class given its absolute class path, and return it without
    instantiating it"""
    try:
        dot = class_path.rindex('.')
    except ValueError:
        raise UsageError, '%s isn\'t a module' % class_path
    module, classname = class_path[:dot], class_path[dot+1:]
    try:
        mod = __import__(module, {}, {}, [''])
    except ImportError, e:
        raise UsageError, 'Error importing %s: "%s"' % (module, e)
    try:
        cls = getattr(mod, classname)
    except AttributeError:
        raise UsageError, 'module "%s" does not define a "%s" class' % (module, classname)

    return cls

def extract_regex(regex, text, encoding):
    """Extract a list of unicode strings from the given text/encoding using the following policies:
    
    * if the regex contains a named group called "extract" that will be returned
    * if the regex contains multiple numbered groups, all those will be returned (flattened)
    * if the refex doesn't contain any group the entire regex matching is returned
    """

    if isinstance(regex, basestring):
        regex = re.compile(regex)

    try:
        strings = [regex.search(text).group('extract')]   # named group
    except:
        strings = regex.findall(text)    # full regex or numbered groups
    strings = flatten(strings)

    if isinstance(text, unicode):
        return [unquote_html(s, keep_reserved=True) for s in strings]
    else:
        return [unquote_html(unicode(s, encoding), keep_reserved=True) for s in strings]

