from touch_sdk import Watch

class MyWatch(Watch):
    def on_sensors(self, sensors):
        def format_tuple(data):
            return ' '.join(format(field, '.3f') for field in data)

        print(format_tuple(sensors.acceleration), end='\t')
        print(format_tuple(sensors.gravity), end='\t')
        print(format_tuple(sensors.angular_velocity), end='\t')
        if sensors.magnetic_field:
            print(format_tuple(sensors.magnetic_field), end='\t')
        print(sensors.timestamp)


import logging
# logging.basicConfig(level=logging.WARNING, format='> %(message)s')

# logging.info('moi')


watch = MyWatch()
watch.start()
#import asyncio
#asyncio.run(watch.run())
