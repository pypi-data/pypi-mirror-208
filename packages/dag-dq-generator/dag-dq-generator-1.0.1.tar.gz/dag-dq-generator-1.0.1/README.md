# dag-dq-generator
DPaaS Airflow DAG (Dynamic Acyclic Graph) and DQ (Data Quality) generator.

*dag-dq-generator* is a DPaaS [Apache Airflow](https://github.com/apache/incubator-airflow) Airflow DAG (Dynamic Acyclic Graph) and DQ (Data Quality) generator  from YAML configuration files.
- [Usage](#usage)
- [YAML Definition](#yaml-definition)
- [Benefits](#benefits)
- [Contributing](#contributing)

## Usage
### Setup
*dag-dq-generator* requires Python 3.6.0+. To set up your environment, you can run `sh build.sh` which installs the required Python packages and run the generator program. Otherwise, you can run `pip install -r requirements.txt` to install the required Python packages and run `python dag_generator.py` with the following parameters:
* `--config-path` defines the path to the configurations folder. Defaults to `./configs/`
* `--dag-storage-path` defines the path to the folder where generated DAGs will be stored. Defaults to `./dags/`
* `--dq-storage-path` defines the path to the folder where DQ SQL files will be stored. Defaults to `./sql/`

## YAML Definition

## Benefits

* Construct DAGs without knowing Python
* Construct DAGs without learning Airflow primitives
* Avoid duplicative code

## Contributing

Contributions are welcome! Just submit a Pull Request or Github Issue. Feel free to join the discussions on the `#dag-dq-generator` Slack channel.
