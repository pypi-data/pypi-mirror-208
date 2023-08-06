import argparse


def get_args():
    parser = argparse.ArgumentParser(description="Create a copy of the input "
                                                 "file "
                                                 "and substitute the values "
                                                 "in the file according to the"
                                                 " provided map file")

    parser.add_argument('-i', '--input', help='Input file to be handled')
    parser.add_argument('-m',
                        '--map',
                        help='File with 2 rows of values. '
                             'the first row values will be '
                             'substituted with the 2nd row')
    parser.add_argument('-s', '--separator', help='Map file separator. '
                                                  'Tabulation is the default',
                        default='\t')

    args = parser.parse_args()

    return args
