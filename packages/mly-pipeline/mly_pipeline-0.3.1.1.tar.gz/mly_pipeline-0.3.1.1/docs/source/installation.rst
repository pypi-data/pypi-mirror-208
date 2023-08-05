Installation
############



The search functionality needs a provision of real-time data (data that become available in real time) from a predefined directory. 
This directory needs to be accessible directly from the location where the search scripts will be running. 
Usually the real-time data directory is located in the CIT LIGO cluster and we will use it as the default place to run the search. 
For more information about how to access it see `here <https://computing.docs.ligo.org/guide/computing-centres/ldg/>`_.


Environment
-----------

MLy-Pipeline and MLy need a series of python packages and authentications. We summarized all those dependencies into one conda environment
 that you can source using the following command:

.. code-block:: bash
    
    conda activate /home/mly/mly-env
    
Installation of MLy-pipeline
----------------------------

Now you are ready to install MLy-pipeline. First you will have to clone the git repository of the pipeline:

.. code-block:: bash

    git clone git@git.ligo.org:mly/mlyPipeline.git
    
Or if you haven't set an ssh key yet use:

.. code-block:: bash

    git clone https://git.ligo.org/mly/mlyPipeline.git

This will create a directory called ``mlyPipeline``. Now get into the directory that was created by using ``cd mlyPipeline``. 
For review purposes makes sure you checkout to the version of the pipeline that is provided, current review version **v0.3**. 

.. code-block:: bash

    git checkout vX.x

Where **X.x** is the version of the tag you need. If you type ``ls`` you will see the list of its contents. One of the directories is ``mly``, this is the submodule with the core packages to run MLy-Pipeline.
It will be currently empty, we have to initiate it. Given that you are in ``mlyPipeline`` directory type:

.. code-block:: bash

    git submodule init
    git submodule update --remote

You might be requested to provide you GitLab username and password. If not it is still fine. The last command might needed to be used again later if there are any updates in ``mly``.
Now get in the mlyPipeline/mly directory by typing ``cd mly``. The mly submodule will be on the master branch, we can check that by typing ``git branch``. This will show all the branches available, and next to the active branch there will be an asterisc. 
We want mly submodule also to be on the same review version. You can do that by typing:

.. code-block:: bash

    git checkout vX.x

Check again with ``git branch`` command to verify that **v0.3** is the active tag.
And that's it! You successfully installed MLy-Pipeline and you are ready to run the search. 
Now check :ref:`Setting_up_a_search` to set up your search directory and run the search.
