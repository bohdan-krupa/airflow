FROM apache/airflow:2.0.0-python3.7

USER root

# INSTALL TOOLS
RUN apt-get update \
&& apt-get -y install libaio-dev \
&& apt-get install postgresql-client \
&& apt-get -y install firefox-esr \
&& apt-get install unzip
RUN mkdir extra

COPY docker/scripts/airflow/init.sh ./init.sh
RUN chmod +x ./init.sh

USER airflow

# COPY SQL SCRIPT
COPY docker/scripts/airflow/check_init.sql ./extra/check_init.sql
COPY docker/scripts/airflow/set_init.sql ./extra/set_init.sql

# PYTHON REQUIREMENTS
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# FIREFOX DRIVER FOR SELENIUM
COPY geckodriver .

# ENTRYPOINT SCRIPT
ENTRYPOINT ["./init.sh"]
