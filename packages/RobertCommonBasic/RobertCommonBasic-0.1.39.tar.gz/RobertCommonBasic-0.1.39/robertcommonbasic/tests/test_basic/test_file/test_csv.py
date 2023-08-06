from robertcommonbasic.basic.file.csv import values_to_csv

points = [{'point_name': '192_168_1_184_47808_6_2_602_2_1', 'index': 0,
                                                       'point_writable': 'True',
                                                       'point_device_address': '6:20/616/192.168.1.12:47808',
                                                       'point_type': 'analogValue', 'point_property': 'presentValue',
                                                       'point_address': 1, 'description': 'None', 'point_value': '1.0',
                                                       'object_name': 'Random-602-1'},
          {'point_name': '192_168_1_184_47808_6_2_602_2_1', 'index': 0,
           'point_writable': 'True',
           'point_device_address': '6:20/616/192.168.1.12:47808',
           'point_type': 'analogValue', 'point_property': 'presentValue',
           'point_address': 1, 'description': 'None', 'point_value': '1.0',
           'object_name': 'Random-602-1'}
          ]

values_to_csv(points, 'E:/aa.csv', index=None)