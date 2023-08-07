import os
import sys
from pathlib import Path
import requests  
import zipfile
from tqdm import tqdm
import tarfile
urls = {
    'morph': 'https://portal.sina.birzeit.edu/ALMA27012000.pickle',
    'ner': 'http://portal.sina.birzeit.edu/Wj27012000.zip'
}

#     'salma': 'http://portal.sina.birzeit.edu/SALMA27012000.zip',
#     'salma2021': 'http://portal.sina.birzeit.edu/SALMA_v2.zip'
# 


def get_appdatadir():
    """
    This method checks if the directory exists and creates if it doesn't. And returns the path to the directory where the application data is stored.
   
    Returns:
    --------
    Path: A pathlib.Path object representing the path to the application data directory.

    Raises:
    -------
    None.

    **Example:**

    .. highlight:: python
    .. code-block:: python

        from nlptools.DataDownload import downloader

        path = downloader.get_appdatadir()

        Windows: 'C:/Users/<Username>/AppData/Roaming/nlptools'
        MacOS: '/Users/<Username>/Library/Application Support/nlptools'
        Linux: '/home/<Username>/.nlptools'
        Google Colab: '/content/nlptools'

    """
    home = str(Path.home())

    # if 'google.colab' in sys.modules:
    #     return Path('/content/nlptools')
    # elif sys.platform == 'win32':
    #     return Path(home, 'AppData/Roaming/nlptools')
    # elif sys.platform == 'darwin':
    #     return Path(home, 'Library/Application Support/nlptools')
    # else:
    #     return Path(home, '.nlptools')

    if 'google.colab' in sys.modules:
        path = Path('/content/nlptools')
    elif sys.platform == 'win32':
        path = Path(home, 'AppData/Roaming/nlptools')
    elif sys.platform == 'darwin':
        path = Path(home, 'Library/Application Support/nlptools')
    else:
        path = Path(home, '.nlptools')

    if not os.path.exists(path):
        os.makedirs(path)

    return path









def download_file(url, dest_path=get_appdatadir()):
    """
    Downloads a file from the specified URL and saves it to the specified destination path.

    Args:
        url (:obj:`str`): The URL of the file to be downloaded.
        dest_path (:obj:`str`): The destination path to save the downloaded file to. Defaults
            to the user's application data directory.


    Returns:
        :obj:`str`: The absolute path of the downloaded file.

    Raises:
        requests.exceptions.HTTPError: If there was an HTTP error during the request.

    Note:
        This method uses the `requests` and `tqdm` libraries. It also checks if the
        downloaded file is a zip file and extracts it if necessary.

    **Example:**

    .. highlight:: python
    .. code-block:: python

          download_file(url='https://example.com/data.zip', dest_path='data/')

    """
    filename = os.path.basename(url)
    file_path = os.path.join(dest_path, filename)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    # NOTE the stream=True parameter below
    try:
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                total_size = int(r.headers.get('content-length', 0))
                block_size = 8192
                progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
                for chunk in r.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
                progress_bar.close()
        # Check the file type and extract accordingly
        file_extension = os.path.splitext(file_path)[1]
        extracted_folder_name = os.path.splitext(file_path)[0]
        
        # Extract zip file if downloaded file is a zip
        if zipfile.is_zipfile(file_path):
            extracted_folder_name = os.path.splitext(file_path)[0]
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                zip_file.extractall(extracted_folder_name)
            os.remove(file_path)
        
        return file_path

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f'Error 403: Forbidden. The requested file url {url} could not be downloaded due to insufficient permissions. Please check the URL and try again.')
        else:
            print('An error occurred while downloading the file:', e)

def download_file(url, dest_path=get_appdatadir()):
    """
    Downloads a file from the specified URL and saves it to the specified destination path.

    Args:
        url (:obj:`str`): The URL of the file to be downloaded.
        dest_path (:obj:`str`): The destination path to save the downloaded file to. Defaults
            to the user's application data directory.


    Returns:
        :obj:`str`: The absolute path of the downloaded file.

    Raises:
        requests.exceptions.HTTPError: If there was an HTTP error during the request.

    Note:
        This method uses the `requests` and `tqdm` libraries. It also checks if the
        compressed downloaded file type and extracts it.

    **Example:**

    .. highlight:: python
    .. code-block:: python

          download_file(url='https://example.com/data.zip', dest_path='data/')

    """
    filename = os.path.basename(url)
    file_path = os.path.join(dest_path, filename)

    print(filename)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                total_size = int(r.headers.get('content-length', 0))
                block_size = 8192
                progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
                for chunk in r.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
                progress_bar.close()

        # Check the file type and extract accordingly
        file_extension = os.path.splitext(file_path)[1]
        extracted_folder_name = os.path.splitext(file_path)[0]
        
        if file_extension == '.zip':
            extract_zip(file_path, extracted_folder_name)
        elif file_extension == '.gz':

            extract_tar(file_path, extracted_folder_name)
        else:
            print(f'Unsupported file type for extraction: {file_extension}')

        return file_path

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f'Error 403: Forbidden. The requested file URL {url} could not be downloaded due to insufficient permissions. Please check the URL and try again.')
        else:
            print('An error occurred while downloading the file:', e)

def extract_zip(file_path, extracted_folder_name):
    """
    Extracts the contents of a ZIP file to the specified folder.

    Args:
        file_path (str): The path to the ZIP file.
        extracted_folder_name (str): The name of the folder where the contents will be extracted.

    Returns:
        None
    """
    with zipfile.ZipFile(file_path, 'r') as zip_file:
        zip_file.extractall(extracted_folder_name)


def extract_tar(file_path, dest_path):
    """
    Extracts the contents of a tar.gz file to the specified destination path.

    Args:
        file_path (str): The path to the tar.gz file.
        dest_path (str): The destination path where the contents will be extracted.

    Returns:
        str: The path to the extracted folder if successful, or None if extraction failed.
    """
    try:
        with tarfile.open(file_path, 'r:gz') as tar:
            # Remove the extension from the file name
            extracted_folder_name = os.path.splitext(os.path.basename(file_path))[0]
            extracted_folder_path = os.path.join(dest_path, extracted_folder_name)

            # Extract the contents to the destination path
            tar.extractall(dest_path)
        
        # Remove the compressed file
        os.remove(file_path)
        
        return extracted_folder_path

    except tarfile.ReadError:
        print(f'Failed to extract the file: {file_path}')
        return None


def download_files_from_urls():
    """
    Downloads multiple files from a dictionary of urls using the download_file() function.

    Args:
        None

    Returns:
        None
    """
    for url in urls.values():
        download_file(url)

def download_files_from_urls(key=None):
    """
    Downloads multiple files from a dictionary of urls using the download_file() function.

    Args:
        key (optional): The key of the dictionary to specify which URLs to download. If not provided, all URLs will be downloaded.

    Returns:
        None
    """
    if key is None:
        urls_to_download = urls.values()
    else:
        urls_to_download = [urls[key]]

    for url in urls_to_download:
        download_file(url)




