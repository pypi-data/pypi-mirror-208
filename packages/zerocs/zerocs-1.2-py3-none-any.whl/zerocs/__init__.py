"""
    Copyright (c) 2023-present YanPing <zyphhxx@foxmail.com> Authors. All Rights Reserve.
    This file is part of zerocs.

    This software is provided 'as-is', without any express or implied
    warranty.  In no event will the authors be held liable for any damages
    arising from the use of this software.

    Permission is granted to anyone to use this software for any purpose,
    including commercial applications, and to alter it and redistribute it
    freely, subject to the following restrictions:

        1.The origin of this software must not be misrepresented;
            you must not claim that you wrote the original software

        2.Altered source versions must be plainly marked as such, and must not be
            misrepresented as being the original software

        3.This notice may not be removed or altered from any source distribution.

        4.You promise to use the software legally and reasonably.
            Do not use the software shelf to carry out any illegal,
            infringing on others' legitimate interests and other malicious acts.
            The software will not be used on any platform in violation of Chinese laws and regulations.
"""
import eventlet

eventlet.monkey_patch()

import os
from zerocs.zerocs_ import MetaClass


class _Service(MetaClass):

    def __init__(self, **kwargs):
        """
        Initialize zerocs service

        Description of various environmental variables:

        ZERO_PROJECT_PATH:
                        The project path can be obtained from the entry file using the following command,
                        os_path = os.path.dirname(os.path.abspath(__file__))

        ZERO_FW_LOGS_PATH:
                        logs path

        ZERO_FW_FILE_PATH:
                        Other file storage directories, it is recommended to store task data

        ZERO_FW_SERVICE_PATH：
                        service script path

        RABBITMQ_CONFIG_URL：
                        The interface for obtaining rabbitmq configuration information. The return information
                        must include RM_CONFIG field: {'RM_CONFIG':{'AMQP_URI': 'admin@123456@127.0.0.1'}}

        RABBITMQ_CONFIG:
                        rabbitmq This field and RABBITMQ_CONFIG_URL must have one，
                        Prioritize the use of this configuration item, e.g: admin@123456@127.0.0.1

        RABBITMQ_PORT:
                    rabbitmq port, default 5672

        ZERO_FW_NODE_MASTER:
                    zerocs service node type Master: True ,Slave: False

        ZERO_FW_DB_FILE:
                    zero tmp file name
        :param kwargs:
        """
        if 'ZERO_PROJECT_PATH' not in kwargs:
            raise 'ZERO_PROJECT_PATH cannot be empty'
        else:
            os.environ['ZERO_PROJECT_PATH'] = kwargs['ZERO_PROJECT_PATH']

        if 'ZERO_FW_LOGS_PATH' not in kwargs:
            raise 'ZERO_FW_LOGS_PATH cannot be empty'
        else:
            os.environ['ZERO_FW_LOGS_PATH'] = kwargs['ZERO_FW_LOGS_PATH']

        if 'ZERO_FW_FILE_PATH' not in kwargs:
            raise 'ZERO_FW_FILE_PATH cannot be empty'
        else:
            os.environ['ZERO_FW_FILE_PATH'] = kwargs['ZERO_FW_FILE_PATH']

        if 'RABBITMQ_CONFIG' in kwargs or 'RABBITMQ_CONFIG_URL' in kwargs:

            if 'RABBITMQ_CONFIG' in kwargs:
                os.environ['RABBITMQ_CONFIG'] = kwargs['RABBITMQ_CONFIG']

            if 'RABBITMQ_CONFIG_URL' in kwargs:
                os.environ['RABBITMQ_CONFIG_URL'] = kwargs['RABBITMQ_CONFIG_URL']
        else:
            raise 'RABBITMQ_CONFIG or RABBITMQ_CONFIG_URL  cannot be empty'

        if 'RABBITMQ_PORT' not in kwargs:
            os.environ['RABBITMQ_PORT'] = '5672'
        else:
            os.environ['RABBITMQ_PORT'] = kwargs['RABBITMQ_PORT']

        if 'ZERO_FW_SERVICE_PATH' not in kwargs:
            raise 'ZERO_FW_SERVICE_PATH cannot be empty'
        else:
            os.environ['ZERO_FW_SERVICE_PATH'] = kwargs['ZERO_FW_SERVICE_PATH']

        if 'ZERO_FW_DB_FILE' not in kwargs:
            raise 'ZERO_FW_DB_FILE cannot be empty'
        else:
            os.environ['ZERO_FW_DB_FILE'] = kwargs['ZERO_FW_DB_FILE']

        if 'ZERO_FW_NODE_MASTER' not in kwargs:
            os.environ['ZERO_FW_NODE_MASTER'] = 'False'
        else:
            os.environ['ZERO_FW_NODE_MASTER'] = kwargs['ZERO_FW_NODE_MASTER']

        """
        Initialize global environment variables
        """
        self._getenv()

        """
        Service initialization. \n
        1.Get a list of services \n
        2.Register default functions to microservices \n
        3.Start microservice queue \n
        4.Start microservice work
        """
        self._service_init()


Service = _Service
