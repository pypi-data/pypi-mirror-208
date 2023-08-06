import os
import subprocess
import sys
import argparse
import os.path
from .map import read_sql


def download(args):
    print('downloading')
    print(args.query)
    read_sql(args.query).to_csv(
        args.output_file, index=False)


def upload(args):
    # Read environment variables
    pg_user = os.environ['PG_USER']
    pg_password = os.environ['PG_PASSWORD']
    pg_host = os.environ['PG_HOST']
    pg_dbname = os.environ['PG_DBNAME']

    for input_file_and_table_name in args.input_files_and_table_names:
        if ':' in input_file_and_table_name:
            input_file, table_name = input_file_and_table_name.split(':')
        else:
            input_file = input_file_and_table_name
            table_name, _ = os.path.splitext(os.path.basename(input_file))

        # Set up ogr2ogr command
        ogr2ogr_command = [
            'ogr2ogr',
            '--config', 'OGR_STREAM_FEATURE_COUNT', '1000',
            '-f', 'PostgreSQL',
            f'PG:user={pg_user} password={pg_password} host={pg_host} dbname={pg_dbname}',
            '-nln', f'{args.schema}.{table_name}',
            input_file
        ]

        # Run the command
        subprocess.run(ogr2ogr_command, check=True)


def main(args=None):
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Scrap is gold. Tools to play with it!')

    # Create subparsers for the "upload" and "download" commands
    subparsers = parser.add_subparsers(dest='command', required=True)
    upload_parser = subparsers.add_parser(
        'upload', help='Upload input files to a PostgreSQL database.')
    download_parser = subparsers.add_parser(
        'download', help='Download data from a PostgreSQL database using a SQL query.')

    # Add arguments for the "upload" command
    upload_parser.add_argument('input_files_and_table_names',
                               help='Input file names and optional table names (e.g., input_file1.tab[:table_name1])', nargs='+')
    upload_parser.add_argument(
        '--schema', help='Schema name to use in the database', default='raw')

    # Add arguments for the "download" command
    download_parser.add_argument('query', help='SQL query to execute')
    download_parser.add_argument(
        '--output-file', '-o', help='Output file name', default='output.csv', )

    # Parse arguments
    args = parser.parse_args(args)

    # Call the appropriate function based on the command
    if args.command == 'upload':
        # Call function to upload input files to PostgreSQL
        upload(args)
    elif args.command == 'download':
        # Call function to download data from PostgreSQL using SQL query
        download(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
