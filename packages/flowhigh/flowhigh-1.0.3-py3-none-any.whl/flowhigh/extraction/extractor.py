"""
 Extractor module:
 The main script which needs to be used for using the command line interface
"""

import argparse
import json
import os.path

from flowhigh.utils.converter import FlowHighSubmissionClass
from flowhigh.format.formatting import Formatter


def main():
    parser = argparse.ArgumentParser(description="SDK for SQLAnalyzer")
    parser.add_argument("-s", "--sql", nargs=1, help="Pass sql statement(s) directly")
    parser.add_argument("-f", "--file", nargs=1, help="Pass sql in the form of a file")
    parser.add_argument("-x", "--extended", action="store_true", help="Extended options to extract more info")
    parser.add_argument("-ex", "--export", nargs=1, help="Save the json to a file")
    parser.add_argument("-EX", "--EXPORT", nargs=1, help="Save the nodes as text to a file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
    parser.add_argument("-fr", "--format", nargs=1,
                        help="Format the sql. Specify option: 1. Compact (Default) 2. Balanced 3. Comfortable")
    args = parser.parse_args()

    source = ""
    if args.sql is not None:
        source = args.sql[0]

    elif args.file is not None and os.path.exists(args.file[0]):
        with open(args.file[0]) as file:
            source = file.read()
            file.close()
    else:
        raise Exception("Invalid Input")

    converter = FlowHighSubmissionClass.from_sql(source)

# def extended(visitor: SDKVisitor, parseql):
#     print("Options")
#     print("0. Get all results")
#     print("1. Get All Column Names")
#     print("2. Get All Table Names")
#     print("3. Get Columns used in Joins")
#     print("4. Get Columns and filters used on them")
#     print("5. Get Columns used in Order By with direction")
#     print("6. Get Columns used in Group By with direction")
#     print("7. Get lineage for columns")
#     options = input("Select Option(s) - ")
#     for option in options:
#         if option == '0':
#             print("All Results")
#             print("-------------------------------------------------------------")
#             print("Column Names - ")
#             if visitor.get_columns() == set():
#                 print("None")
#             else:
#                 print(visitor.get_columns())
#             print("-------------------------------------------------------------")
#             print("Table Names - ")
#             if visitor.get_tables() == set():
#                 print("None")
#             else:
#                 print(visitor.get_tables())
#             print("-------------------------------------------------------------")
#             print("Columns used in Joins - ")
#             if visitor.get_join_columns() == set():
#                 print("None")
#             else:
#                 print(visitor.get_join_columns())
#             print("-------------------------------------------------------------")
#             print("Columns and filters applied to them")
#             if visitor.get_filter_columns() == {}:
#                 print("None")
#             else:
#                 print(visitor.get_filter_columns())
#             print("-------------------------------------------------------------")
#             print("Columns used in Order By with direction")
#             if visitor.get_sort_columns() == set():
#                 print("None")
#             else:
#                 print(visitor.get_sort_columns())
#             print("-------------------------------------------------------------")
#             print("Columns used in Group By with direction")
#             if visitor.get_agg_columns() == set():
#                 print("None")
#             else:
#                 print(visitor.get_agg_columns())
#             print("-------------------------------------------------------------")
#             print("Column Lineage - ")
#             lineage_visitor_obj = LineageVisitor()
#             parseql.accept(lineage_visitor_obj)
#             if not lineage_visitor_obj.get_column_and_lineage():
#                 print("None")
#             else:
#                 for lineage in lineage_visitor_obj.get_column_and_lineage():
#                     print("{} \n".format(lineage))
#             print("-------------------------------------------------------------")
#
#         if option == '1':
#             print("Column Names - ")
#             if visitor.get_columns() == set():
#                 print("None")
#             else:
#                 print(visitor.get_columns())
#             print("-------------------------------------------------------------")
#         if option == '2':
#             print("Table Names - ")
#             if visitor.get_tables() == set():
#                 print("None")
#             else:
#                 print(visitor.get_tables())
#             print("-------------------------------------------------------------")
#         if option == '3':
#             print("Columns used in Joins - ")
#             if visitor.get_join_columns() == set():
#                 print("None")
#             else:
#                 print(visitor.get_join_columns())
#             print("-------------------------------------------------------------")
#         if option == '4':
#             print("Columns and filters applied to them")
#             if visitor.get_filter_columns() == {}:
#                 print("None")
#             else:
#                 print(visitor.get_filter_columns())
#             print("-------------------------------------------------------------")
#         if option == '5':
#             print("Columns used in Order By with direction")
#             if visitor.get_sort_columns() == set():
#                 print("None")
#             else:
#                 print(visitor.get_sort_columns())
#             print("-------------------------------------------------------------")
#         if option == '6':
#             print("Columns used in Group By with direction")
#             if visitor.get_agg_columns() == set():
#                 print("None")
#             else:
#                 print(visitor.get_agg_columns())
#             print("-------------------------------------------------------------")
#
#         if option == '7':
#             print("Column Lineage - ")
#             lineage_visitor_obj = LineageVisitor()
#             parseql.accept(lineage_visitor_obj)
#             if not lineage_visitor_obj.get_column_and_lineage():
#                 print("None")
#             else:
#                 for lineage in lineage_visitor_obj.get_column_and_lineage():
#                     print("{} \n".format(lineage))
#             print("-------------------------------------------------------------")


def export_json(json_data, file):
    with open(file, mode="w") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
        f.close()


def export_nodes(parseql, file):
    with open(file, mode="w") as f:
        f.write(str(parseql))
        f.close()


if __name__ == "__main__":
    main()
