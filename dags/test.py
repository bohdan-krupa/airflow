import time
import requests
from datetime import timedelta

import pandas as pd

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

DOWNLOADED_FILE_NAME = 'ASP Pricing File.zip'


def get_download_url() -> str:
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path='./geckodriver', options=options)
    time.sleep(5)
    driver.get('https://www.cms.gov/medicare/medicare-part-b-drug-average-sales-price/2021-asp-drug-pricing-files')
    time.sleep(5)

    link = driver.find_element_by_partial_link_text('2021 ASP Pricing File')

    return link.get_attribute('href')


def download_file(**kwargs) -> None:
    ti = kwargs['ti']
    url = ti.xcom_pull(task_ids='get_download_url')

    res = requests.get(url)

    with open(DOWNLOADED_FILE_NAME, 'wb') as file:
        file.write(res.content)


def read_csv(**kwargs):
    ti = kwargs['ti']
    file_name = ti.xcom_pull(task_ids='get_csv_name')

    data = pd.read_csv(file_name, encoding='windows-1252')
    df = pd.DataFrame(data, columns=['HCPCS Code', 'Short Description', 'HCPCS Code Dosage'])

    return str(df.head(50))


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
        'tutorial',
        default_args=default_args,
        description='A simple tutorial DAG',
        schedule_interval=timedelta(days=1),
        start_date=days_ago(2),
        tags=['selenium', 'pandas']
) as dag:
    get_download_url = PythonOperator(
        task_id='get_download_url',
        python_callable=get_download_url
    )

    clear_old_files = BashOperator(
        task_id='clear_old_files',
        bash_command=f'cd /opt/airflow && rm -f *.zip *.xlsx *.csv'
    )

    download_file = PythonOperator(
        task_id='download_file',
        python_callable=download_file
    )

    unzip_file = BashOperator(
        task_id='unzip_file',
        bash_command=f'cd /opt/airflow && unzip "{DOWNLOADED_FILE_NAME}"'
    )

    get_csv_name = BashOperator(
        task_id='get_csv_name',
        bash_command='cd /opt/airflow && ls | grep *.csv'
    )

    read_csv = PythonOperator(
        task_id='read_csv',
        python_callable=read_csv
    )

    get_download_url >> clear_old_files >> download_file >> unzip_file >> get_csv_name >> read_csv
