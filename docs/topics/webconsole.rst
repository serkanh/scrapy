.. _topics-webconsole:

===========
Web Console
===========

Scrapy comes with a built-in web server for monitoring and controlling a Scrapy
running process. 

The web console is :ref:`built-in Scrapy extension
<topics-extensions-ref>` which comes enabled by default, but you can also
disable it if you're running tight on memory.

For more information about this extension see
:ref:`topics-extensions-ref-webconsole`.

Writing a web console extension
===============================

Writing a web console extension is similar to writing any other :ref:`Scrapy
extensions <topics-extensions>` except that the extension class must:

1. catch the ``scrapy.management.web.webconsole_discover_module`` signal, and
   return itself in the handler.

2. have the following two attributes:

.. attribute:: webconsole_id

    The id by which the Scrapy web interface will known this extension, and
    also the main dir under which this extension interface will work. For
    example, assuming Scrapy web server is listening on
    http://localhost:8000/ and the ``webconsole_id='extension1'`` the web
    main page for the interface of that extension will be:

        http://localhost:8000/extension1/
    
.. attribute:: webconsole_name

    The name by which the Scrapy web server will know that extension. That name
    will be displayed in the main web console index, as the text that links to
    the extension main page.

3. implement the following method:

.. method:: webconsole_render(wc_request)

``wc_request`` is a `twisted.web.http.Request`_ object with the HTTP request
sent to the web console.

.. _twisted.web.http.Request: http://python.net/crew/mwh/apidocs/twisted.web.http.Request.html

It must return a str with the web page to render, typically containing HTML
code.

Example web console extension
=============================

Here's an example of a simple web console extension that just displays a "Hello
world!" text::

    from scrapy.xlib.pydispatch import dispatcher
    from scrapy.management.web import webconsole_discover_module

    class HelloWorldConsole(object):
        webconsole_id = 'helloworld'
        webconsole_name = 'Hello world'

        def __init__(self):
            dispatcher.connect(self.webconsole_discover_module, signal=webconsole_discover_module)

        def webconsole_discover_module(self):
            return self

        def webconsole_render(self, wc_request):
            return "<html><head></head><body><h1>Hello world!</h1></body>"

If you start Scrapy with the web console enabled on http://localhost:8000/ and
you access the URL:

    http://localhost:8000/helloworld/

You will see a page containing a big "Hello World!" text.

.. _topics-webconsole-extensions-ref:

Available Web console extensions
--------------------------------

.. module:: scrapy.contrib.webconsole
   :synopsis: Contains most built-in web console extensions

Here is a list of built-in web console extensions.

Scheduler queue extension
~~~~~~~~~~~~~~~~~~~~~~~~~

.. module:: scrapy.contrib.webconsole.scheduler
   :synopsis: Scheduler queue web console extension

.. class:: scrapy.contrib.webconsole.scheduler.SchedulerQueue

Display a list of all pending Requests in the Scheduler queue, grouped by
domain/spider.

Spider live stats extension
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. module:: scrapy.contrib.webconsole.livestats
   :synopsis: Spider live stats web console extension

.. class:: scrapy.contrib.webconsole.livestats.LiveStats

Display a table with stats of all spider crawled by the current Scrapy run,
including:

* Number of items scraped
* Number of pages crawled
* Number of pending requests in the scheduler
* Number of pending requests in the downloader queue
* Number of requests currently being downloaded

Engine status extension
~~~~~~~~~~~~~~~~~~~~~~~

.. module:: scrapy.contrib.webconsole.enginestatus
   :synopsis: Engine status web console extension

.. class:: scrapy.contrib.webconsole.enginestatus.EngineStatus

Display the current status of the Scrapy Engine, which is just the output of
the Scrapy engine ``getstatus()`` method.

Stats collector dump extension
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. module:: scrapy.contrib.webconsole.stats
   :synopsis: Stats dump web console extension

.. class:: scrapy.contrib.webconsole.stats.StatsDump

Display the stats collected so far by the stats collector.
