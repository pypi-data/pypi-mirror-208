=============
Release Notes
=============

-----
0.8.0
-----

Released: ?

*  **Features**

   *  Initial release.

   *  Port of `lockss-daemon <https://gitub.com/lockss/lockss-daemon>`_'s
      ``scripts/ws/daemonstatusservice.py`` into the package
      ``lockss.turtles``:

      =============================================================== =====
      0.7.x                                                           0.8.x
      =============================================================== =====
      ``import daemonstatusservice`` (with ``PYTHONPATH``)            ``import lockss.soap.daemon_status_service``
      ``scripts/ws/daemonstatusservice --hosts=... --host=...``       ``daemonstatusservice --nodes=... --node=...``
      ``--get-au-article-urls``                                       n/a
      ``--get-au-status``                                             ``get-au-status`` (``gas``)
      ``--get-au-subst-urls``                                         n/a
      ``--get-au-urls``                                               ``get-au-urls`` (``gau``)
      ``--get-auids``                                                 ``get-auids`` (``ga``)
      ``--get-auids-names``                                           ``get-auids --names`` (``ga --names``)
      ``--get-peer-agreements``                                       n/a
      ``--get-platform-configuration``                                ``get-platform-configuration`` (``gpc``)
      ``--is-daemon-ready``                                           ``is-daemon-ready`` (``idr``)
      ``--is-daemon-ready-quiet``                                     n/a
      ``--query-aus``                                                 ``query-aus`` (``qa``)
      ``--query-crawls``                                              ``query-crawls`` (``qc``)
      n/a                                                             ``query-polls`` (``qp``)
      ``--version``                                                   ``version``
      =============================================================== =====

