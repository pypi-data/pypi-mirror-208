# Copyright Formic Technologies 2023
import asyncio
import logging.config
import time

from formic_opcua import AsyncOpcuaClient

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s | %(levelname)s | %(name)s | %(module)s | %(funcName)s:%(lineno)d | %(message)s',
        },
    },
    'handlers': {
        'root_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': './opcua.log',
            'formatter': 'verbose',
            'backupCount': 5,
            'maxBytes': 10000000,
            'encoding': 'utf-8',
        },
        'opcua_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': './opcua.log',
            'formatter': 'verbose',
            'backupCount': 5,
            'maxBytes': 10000000,
            'encoding': 'utf-8',
        },
        'background_lib_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': './asyncua.log',
            'formatter': 'verbose',
            'backupCount': 5,
            'maxBytes': 10000000,
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'root': {
            'handlers': ('root_file_handler',),
            'level': logging.INFO,
            'propagate': False,
        },
        'formic_opcua': {
            'handlers': ('opcua_file_handler',),
            'level': logging.WARNING,
            'propagate': False,
        },
        'asyncua': {
            'handlers': ('background_lib_file_handler',),
            'level': logging.INFO,
            'propagate': False,
        },
    },
}

logging.config.dictConfig(LOG_CONFIG)


async def main() -> None:
    # config_file_name = './example_configs/opcua_config_1.yaml'
    start = time.perf_counter()
    async with AsyncOpcuaClient(
        url='opc.tcp://192.168.140.201:48016', uri='http://wittmann-group.com/RobotSharedApiOpcUa', connect_timeout=5
    ) as client:
        print(time.perf_counter() - start)
        for i in range(10):
            # client.write(
            #     path='formic/device_type/PLC/device/SYS1_PLC1/connection/connection_status',
            #     value=i,
            # )
            # client.write(
            #     path='formic/device_type/PLC/device/SYS1_PLC1/states/critical_system_statuses/level_1_errors',
            #     value=i,
            # )
            var = await client.read(
                path='RobotSharedApi/OperationMode/State',
            )
            var1 = await client.read(
                path='RobotSharedApi/DeviceCollection/Counters/Counter [100]/Value',
            )
            print(i)
            print(var)
            print(var1)
            # all_variables = client.read_all()
            # print(all_variables)
            # print(i)
            time.sleep(2)


if __name__ == '__main__':
    asyncio.run(main())
