Doublebellycluster
******************

Doublebellycluster - это Библиотека кластеризации на анализе плотности


Установка
*********


.. code:: bash

    pip install doublebellycluster

или

.. code:: bash

    python setup.py install

Примеры
*******

.. code:: python

    import doublebellycluster

    # Главный класс
    doubleclustering = doublebellycluster.Doubleclustering()
    # запустить кластеризацию на данных xy
    # данные должны быть непрерывными

    xy['col'] = doubleclustering.do_continis( xy[['xx', 'yy']],
                        calc_aggregate_all= True,
                        percentile_cut = 10)
    doubleclustering.d3_color_map(folder='C:/Users/User/Desktop',show_save = False)

    doubleclustering.show_fi_plot_(folder='C:/Users/User/Desktop',show_save = False)
    

    # Есть еще функции

    # Сравнивает две последовательности
    doublebellycluster.seq_match(a, b)

    # найти расстояние между кластерами
    doublebellycluster.get_inter_dist(df,col)





История изменений
*****************

* **Release 1.3.2 (2023-03-20)**

  * Пока работает только на непрерывных данных

* **Release 1.3.1 (2023-02-28)**

  * Если гео данные - то их нужно подготавливать :code:`import pyproj` 
  * Исправлено :code:`AttributeError` при вызове :code:`ResourceLinkObject.public_listdir()`


