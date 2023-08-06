import pandas as pd
import json
import requests
import datetime
import boto3
from botocore.exceptions import ClientError

#Create Control File Class
class ControlFile:
    """
    This class creates a control file to store URLs for query extraction.
    """
    def __init__(self, client_s3, bucket_name, prefix, filename_control):
        self.url = None
        self.client_s3 = client_s3
        self.prefix = prefix
        self.bucket_name = bucket_name
        self.file_control = filename_control.lower()
        self.key_table = f"{self.prefix}/{self.file_control}.json"
        self.date_period = None
        self.days_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.dataframe = pd.DataFrame(columns=['data', 'url', 'status', 'download'])

    def set_url(self, url):
        """
        This function sets the url for the current instance of the class. 
        Parameters:
            url (str): The url to be set
        Returns:
            None
        """
        self.url = url
    
    def set_date_period(self, date_period):
        """ Sets the date period of the data.
        
        Args:
            date_period (datetime): The date period of the data
            
        Returns:
            None
        """
        self.date_period = date_period
    
    def view_object(self, key_table):
        """
        This function takes in a key_table and returns the response of an S3 object.

        Params:
            key_table (string): The key name to retrieve the S3 object.

        Returns:
            response (object): The response of the S3 object.

        Raises:
            ClientError: If a ClientError occurs, the error is printed. 
        """
        try:
            response = self.client_s3.get_object(Bucket=self.bucket_name, Key=key_table)
            return response
        except ClientError as e:
            print(e)
        
        return None

    

    def read_file_control(self):
        """
        Reads a file from an S3 bucket and returns the content of the file.

        Args:
            self: The instance of the class.
        Returns:
            file_content: The content of the file as json.

        Raises:
            Exception: If the file could not be read, a new file is created.
        """

        try:
            file_content =  self.client_s3.Object(self.bucket_name, self.key_table).get()['Body'].read().decode('utf-8')
            return json.loads(file_content)
        except Exception as e:
            df = pd.DataFrame(columns=['data', 'url', 'status', 'download'])
            df = df.to_json(orient='records')
            self.client_s3.Object(self.bucket_name, self.key_table).put(Body=df)
            return json.loads(df)


    def put_object_file_json_in_s3(self, file_content):
        """
        This function uploads a json file to an S3 bucket.

        Parameters:
        file_content (json): content of the file to be uploaded

        Returns:
        message (string): success message

        """
        
        table_name = self.file_control.lower()
        key_table = f"{self.prefix}/{table_name}.json"
        self.client_s3.Object(self.bucket_name, key_table).put(Body=json.dumps(file_content))
        return {
            'message': 'File {} uploaded to {}.'.format(self.file_control, self.bucket_name)
        }
    

    def check_url_control(self):
        '''
        Checks if the URL has already been processed for the current date period.
        
        Parameters:
            self: The instance of the class.
        
        Returns:
            False: If the URL has already been processed for the current date period.
            True: If the URL has not been processed for the current date period.
        '''
        data_file = self.read_file_control()
        date_today = self.date_period
        if date_today in data_file and self.url in data_file[date_today]:
            return False
        else:
            return True
    
    def add_data_control(self, status: str, download: bool):
        """
        This function adds data to file control in the S3 bucket.

        Parameters:
            self (object): Object of the class.
            status (str): Status of the download.
            download (bool): Downloaded file.

        Returns:
            data_file: (object):
        """
        data_file = self.read_file_control()
        date_today = self.date_period 
        if date_today not in data_file:
            data_file[date_today] = {}
        data_file[date_today][self.url] = {'status': status, 'download': download}
        self.put_object_file_json_in_s3(data_file)
        return data_file
        
    def update_dataframe(self):
        """
        This function updates the dataframe associated with the class by reading the data from the file control.
        The file control data is read and stored into a list of dataframes. The dataframes are then concatenated into a single dataframe.
        The dataframe is stored as an attribute of the class.

        Args:
            self: The instance of the class.

        Returns:
            dataframe: Dataframe

        """
        data_file = self.read_file_control()
        df_list = []
        for data in data_file:
            for url, dados in data_file[data].items():
                df_list.append(pd.DataFrame({'data': data, 'url': url, 'status': dados['status'], 'download': dados['download']}, index=[0]))
        self.dataframe = pd.concat(df_list, ignore_index=True)
        return self.dataframe
    
    def execute(self):
        """Execute the request for the given URL

        Checks to see if the URL has been processed
        and updates the dataframe accordingly. Raises
        an exception if there is an error.

        Args:
            self: The instance of the class.

        Returns:
            Nothing.

        Raises:
            An exception if an error occurs.
        """
        if self.check_url_control():
            try:
                req = requests.get(self.url)
                self.add_data_control('Processed', True)
            except:
                self.add_data_control('Pending', False)
        self.update_dataframe()
        
    def print_result(self):
        """
        This function prints the results of a given dataframe.

        Parameters:
            self (object): The instance of the class.

        Returns:
            None
        """
        print('Report Extract:')
        for day_week in self.days_week:
            df_dia = self.dataframe[self.dataframe['data'] == self.date_period]
            print(f'{day_week}:')
            for index, row in df_dia.iterrows():
                print(f'URL: {row["url"]} | Status: {row["status"]} | Download: {row["download"]}')
