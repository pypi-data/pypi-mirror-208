Modeler package
--------------------

1. set up virtual environment for python
    - for Pycharm
        - https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html
    - for pure python
        - go to your/download/src/directory and run the below commands

        >>> python3 -m venv venv
        >>> source venv/bin/activate


2. after downloading source from git, open terminal and run the below command.
    >>>  python setup.py test install


3. if you added a new package then run the following commend
    >>> python setup.py install

4. Install protobuf 3.6.1 on Ubuntu 18.04
    .. code-block::

        #! /bin/bash
        # Make sure you grab the latest version
        curl -OL https://github.com/google/protobuf/releases/download/v3.6.1/protoc-3.6.1-linux-x86_64.zip
        https://github.com/google/protobuf/releases/download/v3.6.1/protoc-3.6.1-linux-x86_64.zip

        # Unzip
        unzip protoc-3.6.1-linux-x86_64.zip -d protoc3

        # Move protoc to /usr/local/bin/
        sudo mv(or cp -pr) protoc3/bin/* /usr/local/bin/

        # Move protoc3/include to /usr/local/include/
        sudo mv(or cp -pr) protoc3/include/* /usr/local/include/

        # Optional: change owner
        sudo chown $USER /usr/local/bin/protoc
        sudo chown -R $USER /usr/local/include/google

    - if you update or add "\*.proto" file in protos package
        - excute generate-protos.sh

How to use
    - for Lifecycle
        - see Lifecycle/README.MD

