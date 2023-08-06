# apache-airflow-providers-sktvane

- AIDP 가 제공하는 자원들에 접근하는 용도
  - `NES`
  - `BigQuery`
  - `Vault`
- 기타 공용 목적의 코드

## PyPI

- https://pypi.org/project/apache-airflow-providers-sktvane

## Deployment

* `main` 브랜치에 `push` 이벤트 발생 시 배포, 부득이하게 로컬 환경에서 배포할 경우 아래 명령 수행
    ```shell
    # build
    $ python setup.py sdist bdist_wheel
    # upload
    $ twine upload dist/*
    # remove
    $ rm -rf build dist apache_airflow_providers_sktvane.egg-info 
    ```

## Components

###### Operators

- `airflow.providers.sktvane.operators.nes` : AIDP 의 `NES` 연동
    - `NesOperator` 
        ```python
        # import
        from airflow.providers.sktvane.operators.nes import NesOperator
        
        ...
        
        # usage
        NesOperator(
        	task_id="jupyter_daily_count",
        	input_nb="https://github.com/sktaiflow/notebooks/blob/master/statistics/jupyter_daily_count.ipynb",
        	parameters={"current_date": "{{ ds }}", "channel": "#aim-statistics"},
        )
        ```
        

###### Sensors

- `airflow.providers.sktvane.sensors.gcp` : AIDP 의 `GCP` 연동
    - `BigqueryPartitionSensor`
        ```python
        # import
        from airflow.providers.sktvane.sensors.gcp import BigqueryPartitionSensor
        
        ...
        
        # usage
        BigqueryPartitionSensor(
        	task_id=f"{table}_partition_sensor",
        	dataset_id="wind_tmt",
        	table_id=table,
        	partition="dt = '{{ds}}'",
        )
        ```
        

###### Macros

- `airflow.providers.sktvane.macros.slack` : AIDP 정의 규격으로 `Slack` 연동
    - `send_fail_message`
        ```python
        # import
        from airflow.providers.sktvane.macros.slack import send_fail_message
        
        ...
        
        # usage
        def send_aidp_fail_message(slack_email: str) -> None:
          send_fail_message(
            slack_channel="#aidp-airflow-monitoring",
            slack_username=f"Airflow-AlarmBot-{env}",
            slack_email=slack_email,
          )
        ```
        
- `airflow.providers.sktvane.macros.gcp` : AIDP 의 `GCP` 연동
    - `bigquery_client`
        ```python
        # import
        from airflow.providers.sktvane.macros.gcp import bigquery_client
        
        ...
        
        # usage
        def bq_query_to_bq(query, dest_table_name, **kwarg):
        	bq_client = bigquery_client()
        
          job_config = QueryJobConfig(
            create_disposition="CREATE_IF_NEEDED",
            write_disposition="WRITE_TRUNCATE",
            destination=f"{bq_client.project}.prcpln_smp.{dest_table_name}",
          )
          job = bq_client.query(query, job_config=job_config)
          job.result()
        ```
        
- `airflow.providers.sktvane.macros.vault` : AIDP 의 `Vault` 연동
    - `get_secrets`
        ```python
        # import
        from airflow.providers.sktvane.macros.vault import get_secrets
        
        ...
        
        # usage
        def get_hive_conn():
          from pyhive import hive
        
          hiveserver2 = get_secrets(path="ye/hiveserver2")
          host = hiveserver2["ip"]
          port = hiveserver2["port"]
          user = hiveserver2["user"]
          conn = hive.connect(host, port=port, username=user)
          return conn
        ```
        
- `airflow.providers.sktvane.macros.date` : AIDP 에서 제공하는 date 유틸리티
    - `ds_nodash_plus_days`
        ```python
        # import
        from airflow.providers.sktvane.macros.date import ds_nodash_plus_days
        
        ...
        
        # usage
        def ds_nodash_tomorrow(ds):
            ds_nodash_plus_days(ds, 1)
        ```
    - `ds_nodash_minus_days`
    - `ym_nodash_add_month`
    - `first_day_of_this_month`
    - `last_day_of_this_month`
    - `get_latest_loaded_dt`
