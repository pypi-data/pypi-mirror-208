from enum import Enum


class DsAction(Enum):
    source = 1
    target = 2
    delete = 3
    insert = 4
    update = 5
    insert_overwrite = 6
    insert_overwrite_all = 7
    insert_all = 8
    create_table = 9
    create_table_local = 10
    create_table_global = 11
    create_table_global_volatile = 12
    create_table_local_volatile = 13
    create_table_global_transient = 14
    create_table_local_transient = 15
    copy_table = 16

