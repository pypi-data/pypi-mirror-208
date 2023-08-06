import os
import ftplib
import time
from ftplib import FTP
from salure_helpers.salureconnect import SalureConnect
from typing import Union, List
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception


def is_ftp_exception(e: BaseException) -> bool:
    if isinstance(e, ftplib.all_errors):
        error = str(e)[:400].replace('\'', '').replace('\"', '')
        print(f"{error}, retrying")
        return True
    else:
        return False


class FTPS(SalureConnect):
    def __init__(self, label: Union[str, List] = None, debug=False):
        super().__init__()
        if label is not None:
            credentials = self.get_system_credential(system='ftps', label=label)
            self.host = credentials['host']
            self.username = credentials['username']
            self.password = credentials['password']
        elif os.getenv("QLIK_HOST") is not None and os.getenv("QLIK_USER") is not None and os.getenv("QLIK_PASSWORD") is not None:
            self.host = os.getenv("QLIK_HOST")
            self.username = os.getenv("QLIK_USER")
            self.password = os.getenv("QLIK_PASSWORD")
        else:
            raise ValueError("Set the environment variables QLIK_HOST, QLIK_USER and QLIK_PASSWORD or provide the label parameter for a credential from SalureConnect")
        self.debug = debug

    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=60, max=900), retry=retry_if_exception(is_ftp_exception), reraise=True)
    def upload_file(self, local_path, filename, remote_path):
        """
        Upload a file from the client to another client or server
        :param local_path: the path where the upload file is located
        :param filename: The file which should be uploaded
        :param remote_path: The path on the destination client where the file should be saved
        :return: a status if the upload is succesfull or not
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.cwd(remote_path)
            with open(local_path + filename, 'rb') as fp:
                # This runs until upload is successful, then breaks
                while True:
                    try:
                        ftp.storbinary("STOR " + filename, fp)
                    except ftplib.error_temp as e:
                        # this catches 421 errors (socket timeout), sleeps 10 seconds and tries again. If any other exception is encountered, breaks.
                        if str(e).split()[0] == '421':
                            time.sleep(10)
                            continue
                        else:
                            raise
                    break
            ftp.close()
            return 'File is transferred'

    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=60, max=900), retry=retry_if_exception(is_ftp_exception), reraise=True)
    def upload_multiple_files(self, local_path, remote_path):
        """
        Upload all files in a directory from the client to another client or server
        :param local_path: the path from where all the files should be uploaded
        :param remote_path: The path on the destination client where the file should be saved
        :return: a status if the upload is succesfull or not
        """
        ftp = FTP(host=self.host, user=self.username, passwd=self.password)
        ftp.cwd(remote_path)
        for filename in os.listdir(local_path):
            file = local_path + filename
            if self.debug:
                print(f"Remote path: {remote_path}, local file: {file}")
            if os.path.isfile(file):
                with open(file, 'rb') as fp:
                    # This runs until upload is successful, then breaks
                    while True:
                        try:
                            ftp.storbinary("STOR " + filename, fp)
                        except ftplib.error_temp as e:
                            # this catches 421 errors (socket timeout), sleeps 10 seconds and tries again. If any other exception is encountered, breaks.
                            if str(e).split()[0] == '421':
                                time.sleep(10)
                                continue
                            else:
                                raise
                        break
        ftp.close()
        return 'All files are transferred'

    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=60, max=900), retry=retry_if_exception(is_ftp_exception), reraise=True)
    def download_file(self, local_path, remote_path, filename, remove_after_download=False):
        """
        Returns a single file from a given remote path
        :param local_path: the folder where the downloaded file should be stored
        :param remote_path: the folder on the server where the file should be downloaded from
        :param filename: the filename itself
        :param remove_after_download: Should the file be removed on the server after the download or not
        :return: a status
        """
        if self.debug:
            print(f"Remote path: {remote_path}, local file path: {filename}")
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            with open('{}/{}'.format(local_path, filename), 'wb') as fp:
                res = ftp.retrbinary('RETR {}/{}'.format(remote_path, filename), fp.write)
                if not res.startswith('226 Successfully transferred'):
                    # Remove the created file on the local client if the download is failed
                    if os.path.isfile(f'{local_path}/{filename}'):
                        os.remove(f'{local_path}/{filename}')
                else:
                    if remove_after_download:
                        ftp.delete(filename)

                return res

    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=60, max=900), retry=retry_if_exception(is_ftp_exception), reraise=True)
    def make_dir(self, dir_name):
        """
        Create a directory on a remote machine
        :param dir_name: give the path name which should be created
        :return: the status if the creation is successfull or not
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            status = ftp.mkd(dir_name)
            return status

    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=60, max=900), retry=retry_if_exception(is_ftp_exception), reraise=True)
    def list_directories(self, remote_path=''):
        """
        Give a NoneType of directories and files in a given directory. This one is only for information. The Nonetype
        can't be iterated or something like that
        :param remote_path: give the folder where to start in
        :return: a NoneType with folders and files
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.cwd(remote_path)
            if self.debug:
                print(ftp.dir())
            return ftp.dir()

    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=60, max=900), retry=retry_if_exception(is_ftp_exception), reraise=True)
    def make_dirs(self, filepath: str):
        """
        shadows os.makedirs but for ftp
        :param filepath: filepath that you want to create
        :return: nothing
        """
        filepath = filepath.split('/')
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.cwd('/')
            for subpath in filepath:
                if subpath != '':
                    file_list = []
                    ftp.retrlines('NLST', file_list.append)
                    if subpath in file_list:
                        ftp.cwd(subpath)
                    else:
                        ftp.mkd(subpath)
                        ftp.cwd(subpath)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=60, max=900), retry=retry_if_exception(is_ftp_exception), reraise=True)
    def list_files(self, remote_path=''):
        """
        Give a list with files in a certain folder
        :param remote_path: give the folder where to look in
        :return: a list with files
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.cwd(remote_path)
            if self.debug:
                print(ftp.nlst())
            return ftp.nlst()

    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=60, max=900), retry=retry_if_exception(is_ftp_exception), reraise=True)
    def remove_file(self, remote_filepath):
        """
        Remove a file on a remote location
        :param remote_file: the full path of the file that needs to be removed
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.delete(remote_filepath)
