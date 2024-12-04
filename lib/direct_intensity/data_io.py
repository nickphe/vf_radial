import os, sys, re

def gather_json_files(directory):
    """
    Gather all json files in a given directory, including child directories.
    Args:
        directory (str): directory to find json files in
    Reutrns:
        (list): paths to json files 
    """
    # thanks chatgpt for this error handling 
    if not isinstance(directory, (str, bytes, os.PathLike)):
        raise TypeError("The directory must be a string, bytes, or os.PathLike object.")
    if not os.path.isdir(directory):
        raise ValueError("The provided directory path does not exist or is not a directory.")
    
    json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files

def gather_tif_files(directory):
    """
    Gather all tif files in a given directory, including child directories.
    Args:
        directory (str): directory to find tif files in
    Reutrns:
        (list): paths to tif files
    """
    tif_files = []
    files = os.listdir(directory)
    for file in files:
        if file.endswith('.tif'):
            tif_files.append(file)
    return sorted(tif_files)

def gather_csv_files(directory):
    """
    Gather all csv files in a given directory, including child directories.
    Args:
        directory (str): directory to find csv files in
    Reutrns:
        (list): paths to csv files
    """
    csv_files = []
    files = os.listdir(directory)
    for file in files:
        if file.endswith('.csv'):
            csv_files.append(file)
    return sorted(csv_files)

def extract_cap_number(string):
    """
    Extract the digits following the string "cap" using regex. For example:
    extract_cap_number('cap5') ---> 5
    Args: 
        string (str): string to find the cap number in 
    Returns:
        cap_number (int): capillary number
    """
    match = re.search(r'(?i)cap(\d+)', string)
    if match:
        cap_number = int(match.group(1))
        return cap_number
    else:
        return None 
    
def extract_temp_part(string):
    """
    Extract a number in a string corresponding to a temperature in the format 'XX.XC' using regex.  For example:
    extract_temp_part('15.0C') ---> 15.0
    Args: 
        string (str): string with temperature folder name
    Returns:
        (float): temperature
    """
    match = re.search(r'(\d+\.?\d*)C', string)
    if match:
        return float(match.group(1))  # Use float to handle decimal numbers
    else:
        return None
    
def list_folders(directory):
    """
    List the child directories in a given directory
    Args:
        directory (str): directory to be parsed
    Returns:
        folders (list): list of strings of paths to directories. 
    """
    # thanks chatgpt for error handling
    if not isinstance(directory, (str, bytes, os.PathLike)):
        raise TypeError("The directory must be a string, bytes, or os.PathLike object.")
    if not os.path.isdir(directory):
        raise ValueError("The provided directory path does not exist or is not a directory.")
    
    folders = [entry.name for entry in os.scandir(directory) if entry.is_dir()]
    return folders

def find_logs_dir(directory):
    """
    List the child directories containing the term 'logs' in a given directory
    Args:
        directory (str): directory to be parsed
    Returns:
        folders (list): list of strings of paths to directories containing 'logs'.
    """
    # thanks chatgpt for error handling
    if not isinstance(directory, (str, bytes, os.PathLike)):
        raise TypeError("The directory must be a string, bytes, or os.PathLike object.")
    if not os.path.isdir(directory):
        raise ValueError("The provided directory path does not exist or is not a directory.")
    
    folders_with_logs = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_dir() and 'logs' in entry.name:
                folders_with_logs.append(entry.path)
    
    return folders_with_logs

def lollos(x):
    """
    Convert list of lists to list of scalars
    Args: 
        x (): list of lists
    Returns: 
        (): list of scalars
    """
    # convert list of lists to list of scalars
    if isinstance(x, list):
        for item in x:
            if isinstance(item, list):
                return [item[0] for item in x]
            else:
                continue
        return x
    else:
        return x