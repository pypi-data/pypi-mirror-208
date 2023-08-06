
import delegator
import os

from google.cloud import bigquery


def merge_files(files_path, output_file_path=None):

    output = 'merged.csv'

    with open(output_file_path if output_file_path else output, 'w') as outfile:
        for file_path in files_path:
            with open(file_path) as infile:
                outfile.write(infile.read())

    return output


def clean_mysql_export(file_path):
    """Cleans MySQL export (CSV) format removing "N values and replacing them with null.
    Args:
        file_path (str): CSV file path

    Returns:
        str: Cleaned CSV file name
    """

    # Crazy SED command to clean Cloud SQL CSV export
    # that doesn't support Null values which are written as "N....seriously.
    command = "cat {file_path} | sed 's/,\"N,/,,/g' | sed 's/,\"N,/,,/g' | sed 's/^\"N,/,/g' | sed 's/,\"N$/,/g'" \
              " >> {file_name}_cleaned.csv"
    file_name = os.path.splitext(file_path)[0]
    command = command.format(file_path=file_path, file_name=file_name)
    delegator.run(command, block=True)

    return "{}_cleaned.csv".format(file_name)


def get_bq_write_disposition(write_preference):
    """Convert write_preference string to BigQuery WriteDisposition values

    Args:
        write_preference (str): The write preference string which should be 'truncate', 'append' or 'empty'

    Returns:
        bigquery.WriteDisposition: The BigQuery WriteDisposition value

    """

    disposition = {
        'truncate': bigquery.WriteDisposition.WRITE_TRUNCATE,
        'append': bigquery.WriteDisposition.WRITE_APPEND,
        'empty': bigquery.WriteDisposition.WRITE_EMPTY
    }

    return disposition.get(write_preference, None)
