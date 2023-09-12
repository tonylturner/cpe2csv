import csv
import xml.etree.ElementTree as ET
import argparse
import requests
import zipfile
import os


NVD_URL = "https://nvd.nist.gov/feeds/xml/cpe/dictionary/official-cpe-dictionary_v2.3.xml.zip"
LOCAL_ZIP = "official-cpe-dictionary_v2.3.xml.zip"
LOCAL_XML = "official-cpe-dictionary_v2.3.xml"

def parse_cpe(cpe_string):
    """Parse a CPE string and return its components."""
    parts = (cpe_string.split(":") + ["" for _ in range(8)])[:8]
    _, part, vendor, product, version, update, edition, language = parts
    return {
        "part": part,
        "vendor": vendor,
        "product": product,
        "version": version,
        "update": update,
        "edition": edition,
        "language": language
    }

def parse_xml(xml_file, csv_file, verbose=False):
    """Converts XML to CSV."""
    context = ET.iterparse(xml_file, events=("start", "end"))
    context = iter(context)
    event, root = next(context)
    
    ns = {'cpe': 'http://cpe.mitre.org/dictionary/2.0'}

    if verbose:
        print("Starting XML to CSV conversion...")

    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = None
        headers_set = False

        for event, elem in context:
            if event == "end" and elem.tag == "{http://cpe.mitre.org/dictionary/2.0}cpe-item":
                cpe_parts = parse_cpe(elem.attrib.get("name", ""))
                data_dict = {
                    "name": elem.attrib.get("name", ""),
                    **cpe_parts,
                    "title": elem.find("cpe:title", ns).text if elem.find("cpe:title", ns) is not None else "",
                    "references": [ref.attrib.get("href", "") for ref in elem.findall("cpe:references/cpe:reference", ns)]
                }

                if not headers_set:
                    writer = csv.DictWriter(csvfile, fieldnames=data_dict.keys())
                    writer.writeheader()
                    headers_set = True
                writer.writerow(data_dict)
                root.clear()

                if verbose:
                    print(f"Processed item: {data_dict['name']}")

    if verbose:
        print(f"Conversion from {xml_file} to {csv_file} completed.")


def update_xml(verbose=False):
    """Downloads the current CPE XML file and extracts it."""
    print("Fetching the latest XML file from NVD...")

    if verbose:
        print("Fetching the latest XML file from NVD...")
    
    response = requests.get(NVD_URL, stream=True)
    with open(LOCAL_ZIP, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    if verbose:
        print("Unzipping the fetched file...")
    with zipfile.ZipFile(LOCAL_ZIP, 'r') as zip_ref:
        zip_ref.extractall()

    return LOCAL_XML

def tmp_cleanup(verbose=False):
    """Removes the temporary files."""
    if verbose:
        print("Cleaning up downloaded files...")
    os.remove(LOCAL_ZIP)
    os.remove(LOCAL_XML)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A tool to convert CPE XML to CSV. The script can either fetch the XML from NVD or you can provide it.")
    
    parser.add_argument("csv_file", help="Output CSV file path where the conversion will be saved.")
    parser.add_argument("-v", "--verbose", 
                        help="Increase output verbosity. Shows progress and other messages while processing.",
                        action="store_true")
    parser.add_argument("-u", "--update", 
                        help="Fetch the latest XML file from the NVD, convert it to CSV and then clean up. Overrides --input if both are provided.",
                        action="store_true")
    parser.add_argument("-i", "--input",
                        help="Path to the input XML file for conversion. If --update is provided, this option is ignored.",
                        type=str, 
                        default=None)
    
    args = parser.parse_args()

    xml_file = None
    if args.update:
        xml_file = update_xml(verbose=args.verbose)

    elif args.input:
        if os.path.exists(args.input):
            xml_file = args.input
        else:
            parser.error(f"The specified XML file '{args.input}' does not exist.")

    else:
        parser.error("You need to specify either the --update flag to fetch the latest XML file or the --input flag to specify an XML file.")

    parse_xml(xml_file, args.csv_file, args.verbose)

    if args.update:
        tmp_cleanup(verbose=args.verbose)
