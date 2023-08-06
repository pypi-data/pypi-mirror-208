# apache-airflow-providers-sktvane

- AIDP 가 제공하는 자원(`NES`, `BigQuery`, `Vault`) 에 접근하는 용도
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

- `airflow.providers.sktvane.operators.nes`
    - `NesOperator` : AIDP 의 `NES(Notebook Executor Service)` 연동 
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

- `airflow.providers.sktvane.sensors.gcp`
    - `BigqueryPartitionSensor` : AIDP 의 `BigQuery` 연동
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

- `airflow.providers.sktvane.macros.slack`
    - `send_fail_message` : AIDP 표준 포맷으로 에러 메시지를 `Slack` 으로 발송
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
        
- `airflow.providers.sktvane.macros.gcp`
    - `bigquery_client` : AIDP 관리 대상 `BigQuery` 연동
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
        
- `airflow.providers.sktvane.macros.vault`
    - `get_secrets` : AIDP 의 `Vault` 를 사용, Secrets 관리
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
        
- `airflow.providers.sktvane.macros.date`
    - `ds_nodash_plus_days` : datetime 관련, 유틸리티성 용도
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