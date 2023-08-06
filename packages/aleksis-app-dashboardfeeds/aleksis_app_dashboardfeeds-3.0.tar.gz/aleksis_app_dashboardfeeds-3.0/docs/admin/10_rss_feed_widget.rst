RSS feed widget
===============

This widget, unlike the name suggests, allows RSS, Atom and JSONFeed feeds to be parsed 
and displayed on the dashboard. Only the most recent article is displayed, with a short caption 
and optionally an image. For this, the feed must contain a JPG image as an enclosure 
(this is not the case by default in every CMS, but most have plugins for this). 
In addition, the news source is linked on the dashboard.

* **RSS feed source URL**: The URL of the source feed
* **Base URL**: The home or base URL of the news provider
* **Text only**: With this being enabled, no images will be shown.

.. note::

    The RSS widget provides a task to pull data. The task ``get_feeds`` updates all active RSS feeds inside AlekSIS. 
    We recommend to run the task every 5 to 10 minutes. The task is automatically scheduled every 10 minutes;
    this can be changed as described in :ref:`core-periodic-tasks`.

.. image:: ../_static/create_rss_widget.png
  :width: 100%
  :alt: Create a RSS widget

.. image:: ../_static/rss_widget.png
  :width: 400
  :alt: The RSS widget on dashboard

