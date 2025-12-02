import os
import re
from pathlib import Path
import sys
# TODO verify that there are no duplicate EYF IDs in the list
# TODO verify what to do if there is a duplicate EYF ID or we cannot find one?


def validate_file_formats(folder_path, regex_pattern):
    """
    Iterate over all files in a folder and validate filenames against a regex pattern.
    
    Args:
        folder_path (str): Path to the folder containing files to validate
        regex_pattern (str): Regular expression pattern to match against filenames
        
    Returns:
        tuple: (valid_files list, invalid_files list)
    """
    valid_files = []
    invalid_files = []
    
    pattern = re.compile(regex_pattern)
    
    folder = Path(folder_path)
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder_path}")
    
    for file_path in folder.iterdir():
        if file_path.is_file():
            filename = file_path.name
            
            if pattern.match(filename):
                valid_files.append(filename)
            else:
                invalid_files.append(filename)
    
    return valid_files, invalid_files

def get_files_for_eyf_ids(folder_path, eyf_ids):
    """
    Validate the existence of expected files in a folder.
    
    Args:
        folder_path (str): Path to the folder containing files
        eyf_ids (list): List of EYF IDs to grab FERPA waivers for
        
    Returns:
        tuple: (eyf_id, list of matching file paths) for each EYF ID
    """
    result = []
        
    folder = Path(folder_path)
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder_path}")
    
    for eyf_id in eyf_ids:
        matching_files = list(folder.glob(f"{eyf_id}_*.pdf"))
        result.append((eyf_id, matching_files))
    
    return result

def read_eyf_ids_from_file(ids_file):
    """
    Reads a list of EYF IDs from a text file.

    Args:
        ids_file (str): Path to the text file containing EYF IDs (one per line).

    Returns:
        list: A list of EYF IDs.
    """
    with open(ids_file, 'r') as f:
        return [line.strip() for line in f]

def process_waiver_matches(eyf_ids_with_filepaths):
    """
    Processes the matched waiver files, identifying errors and successful matches.

    Args:
        eyf_ids_with_filepaths (list): A list of tuples, each containing an EYF ID and a list of file paths.

    Returns:
        list: A list of file paths for the PDFs that are ready to be combined.
    """
    pdfs_to_combine = []
    for eyf_id, filepaths in eyf_ids_with_filepaths:
        if len(filepaths) == 0:
            print(f"ERROR: No waiver found for EYF ID {eyf_id}")
        elif len(filepaths) > 1:
            print(f"ERROR: Multiple waivers found for EYF ID {eyf_id}:")
            for filepath in filepaths:
                print(f"  {filepath}")
        else:  # exactly one file found
            pdfs_to_combine.append(filepaths[0])
    return pdfs_to_combine

def combine_pdfs(pdf_list):
    """
    Creates the combined PDF from the list of files

    Args:
        pdf_list (list): A list of paths to PDF files to be combined.
    """
    print('PDFs to combine:')
    for pdf in pdf_list:
        print(f"  {pdf}")
        
def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_pdf_request.py <waiver_folder_path> <ids_file>")
        print("  <waiver_folder_path>: Path to the folder containing the FERPA waivers")
        print("  <ids_file>: Path to text file containing EYF IDs (one per line)")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    ids_file = sys.argv[2]
    
    eyf_ids = read_eyf_ids_from_file(ids_file)
    
    file_pattern = "[EYF ID]_[Client name]_KCS Records Consent_[previous file name]_[date].pdf"
    regex_pattern = r"^[0-9]+_[A-Za-z ]+_KCS Records Consent_.*\.pdf$"
    
    try:
        valid_files, invalid_files = validate_file_formats(folder_path, regex_pattern)
        
        if (len(invalid_files) > 0):
            print(f"ERROR: Some files do not match the expected format: {file_pattern}")
            for file in invalid_files:
                print(f"{file}")
            sys.exit(1)

        eyf_ids_with_filepaths = get_files_for_eyf_ids(folder_path, eyf_ids)
        pdfs_to_combine = process_waiver_matches(eyf_ids_with_filepaths)

        fully_matched_count = len(pdfs_to_combine)
        eyf_id_count = len(eyf_ids)

        print(f"Successfully matched waivers for {fully_matched_count} out of {eyf_id_count} EYF IDs. Proceed with PDF generation?")
        user_input = input("Enter 'y' to continue or 'n' to cancel: ").strip().lower()
        if user_input != 'y':
            print("Operation cancelled.")
            sys.exit(0)

        combine_pdfs(pdfs_to_combine)
            
    except Exception as e:
        print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()
