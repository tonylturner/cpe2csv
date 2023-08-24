# cpe2csv

cpe2csv solves a very basic issue with me hating dealing with XML and wanting an easier way to work with Common Platform Enumeration (CPE) data in a more spreadsheet friendly format. It retrieves the latest copy of the CPE dictionary from https://nvd.nist.gov/products/cpe or you can provide your own copy and performs the following operations:

Converts the XML to CSV and extracts CPE URI string, name and an array of references from the dictionary
Parses the URI and extracts part, vendor, product, version, update, edition and language and write this to same CSV file
Cleans up the downloaded artifacts


# Usage
```
usage: cpe2csv.py [-h] [-v] [-u] [-i INPUT] csv_file

A tool to convert CPE XML to CSV. The script can either fetch the XML from NVD
or you can provide it.

positional arguments:
  csv_file              Output CSV file path where the conversion will be
                        saved.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase output verbosity. Shows progress and other
                        messages while processing.
  -u, --update          Fetch the latest XML file from the NVD, convert it to
                        CSV and then clean up. Overrides --input if both are
                        provided.
  -i INPUT, --input INPUT
                        Path to the input XML file for conversion. If --update
                        is provided, this option is ignored.
```
