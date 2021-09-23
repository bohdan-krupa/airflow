import time
from datetime import timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def get_download_url() -> str:
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path='./geckodriver', options=options)
    time.sleep(3)
    driver.get('https://www.cms.gov/medicare/medicare-part-b-drug-average-sales-price/2021-asp-drug-pricing-files')
    time.sleep(3)

    link = driver.find_element_by_partial_link_text('2021 ASP Pricing File')

    return link.get_attribute('href')


def format_url(**kwargs) -> str:
    ti = kwargs['ti']
    url = ti.xcom_pull(task_ids='get_download_url')

    return f'Download URL: {url}'


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
) as dag:
    t1 = PythonOperator(
        task_id='get_download_url',
        python_callable=get_download_url
    )

    t2 = PythonOperator(
        task_id='format_url',
        python_callable=format_url
    )

    t1 >> t2
