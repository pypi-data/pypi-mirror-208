Engine
======

A Utility Library that assists in Geospatial Machine Learning Experiment
Tracking.

Installation
------------

.. code:: shell

   pip install granular-engine

Usage
-----

CLI
~~~

.. figure:: https://user-images.githubusercontent.com/2713531/210276844-16d3867d-461c-44ba-870b-00d6d6266dbf.gif
   :alt: engine_cli

   engine_cli

Experiment Tracking
~~~~~~~~~~~~~~~~~~~

.. code:: python

   from engine import Engine

   engine = Engine("test_config.yaml")

   for epoch in enumerate(epochs):
      # train 
      # eval
      engine.log(step=epoch, train_loss=train_loss, val_loss=val_loss)

   engine.done()

License
-------

GPLv3

Documentation
-------------

View documentation ``here <https://engine.granular.ai/>``\ \_
