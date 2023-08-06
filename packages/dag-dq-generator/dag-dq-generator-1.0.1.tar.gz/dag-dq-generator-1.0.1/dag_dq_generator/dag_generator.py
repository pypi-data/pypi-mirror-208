"""This module generates DAG and DQ SQL files using the input configuration files."""

import os
import argparse
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader, PackageLoader
import yaml
from yamlinclude import YamlIncludeConstructor
import logging
import warnings
warnings.filterwarnings("ignore")

# Global Constants
about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "__version__.py")) as f:
        exec(f.read(), about)
DAG_GENERATOR_VERSION = about['__version__']

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Define DAG template filename and config path
CONFIG_FILEPATH = './configs/'
DAG_STORAGE_PATH = './dags/'
DQ_STORAGE_PATH = './sql/'
DAG_TEMPLATE_FILENAME = 'dag_template.py'
DQ_TEMPLATE_FILENAME = 'dq_sql_template.sql'


# Instantiate Jinja environment
#template_env = Environment(loader=FileSystemLoader(searchpath='./'))
template_env = Environment(loader=PackageLoader(__name__))

# Define utility functions

def _create_logger(name):
    """Create a formatted console logger."""
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # create logging formatter
    logFormatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(name)s: %(message)s')
    
    # create console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)    
    
    # Add console handler to logger
    logger.addHandler(consoleHandler)
    logger.propagate = False
    
    return logger


# Create Logger
logger = _create_logger('dag-generator')


def validate_config_file(config: Dict) -> None:
    """Validates the input config file."""

    # pipeline_settings validations
    if 'pipeline_settings' not in config:
        raise ValueError("`pipeline_settings` configuration required in config file.")

    if 'dag_name' not in config['pipeline_settings']:
        raise ValueError("`dag_name` value required in config pipeline_settings.")

    if 'dag_owner' not in config['pipeline_settings']:
        raise ValueError("`dag_owner` value required in pipeline_settings.")

    #if 'sql_endpoint_name' not in config['pipeline_settings']:
    #    raise ValueError("`sql_endpoint_name` value required in pipeline_settings.")

    if 'conn_id' not in config['pipeline_settings']:
        raise ValueError("`conn_id` value required in pipeline_settings.")

    if 'pull_fiscal_attributes' not in config['pipeline_settings']:
        raise ValueError("`pull_fiscal_attributes` value required in pipeline_settings.")

    if 'dag_schedule' not in config['pipeline_settings']:
        raise ValueError("`dag_schedule` value required in pipeline_settings.")

    if 'dag_start_date' not in config['pipeline_settings']:
        raise ValueError("`dag_start_date` value required in pipeline_settings.")

    if 'dbx_base_path' not in config['pipeline_settings']:
        raise ValueError("`dbx_base_path` value required in pipeline_settings.")

    # pre/post checks validations
    if 'pre_checks' in config or 'post_checks' in config:
        for group in (config.get('pre_checks', []) + config.get('post_checks', [])):
            if 'group_name' not in group:
                raise ValueError("`group_name` required in pre/post-check group.")
            if 'tasks' not in group:
                raise ValueError(f"`tasks` need to be added in pre/post-check `{group['group_name']}` group.")
            
            for task in group['tasks']:
                if 'task_id' not in task:
                    raise ValueError(f"`task_id` required for all tasks in pre/post-check `{group['group_name']}` group.")
                if 'arguments' not in task:
                    raise ValueError(f"`arguments` required for all tasks in pre/post-check `{group['group_name']}` group, `{task['task_id']}` task.")
                if 'operator' in task:
                    raise ValueError(f"`operator` is not allowed in pre/post-check tasks. All pre/post-check tasks are `DatabricksSqlOperator`.")

    # data quality validations
    if 'data_quality' in config:
        for dq in config['data_quality']:
            if 'id' not in dq:
                raise ValueError("`id` required in for each data quality block.")

            if 'source_table' not in dq:
                raise ValueError("`source_table` required in for each data quality block.")

            if 'period_type' not in dq:
                raise ValueError("`period_type` required in for each data quality block.")

            if dq['period_type'] not in ['DAILY', 'FISCAL_WK', 'FISCAL_QTR', 'FISCAL_YR']:
                raise ValueError("Data quality `period_type` must be one of DAILY, FISCAL_WK, FISCAL_QTR, FISCAL_YR.")

            if 'key_dimensions' not in dq or 'key_measures' not in dq:
                raise ValueError("`key_dimensions` and `key_measures` must be defined in data quality block.")
            
            if 'key_dimensions' in dq and not isinstance(dq['key_dimensions'], list):
                raise ValueError("`key_dimensions` must be a list in data quality block.")

            if 'key_measures' in dq and not isinstance(dq['key_measures'], list):
                raise ValueError("`key_measures` must be a list in data quality block.")

            if 'partition' in dq and ('col_name' not in dq['partition'] or 'col_value' not in dq['partition']):
                raise ValueError("`col_name` & `col_value` must be defined in `partition` for data quality block.")

    logger.info(f"{config['pipeline_settings']['dag_name']} configuration file validated!")


def generate_dq_query(config: List) -> None:
    """
    Helper function to generate data quality (DQ) SQL file
    """
    template = template_env.get_template(DQ_TEMPLATE_FILENAME)

    if 'data_quality' in config:

        # Create DQ sub directory
        sql_subdir = os.path.join(DQ_STORAGE_PATH, config['pipeline_settings']['dbx_base_path'].lstrip('/'))
        os.makedirs(sql_subdir, exist_ok=True)
        
        for dq in config['data_quality']:

            _dimensions = dq['key_dimensions']
            _group_set = _dimensions

            if 'grouping_level' in dq and isinstance(dq['grouping_level'], int):

                if dq['grouping_level'] == 2:
                    _group_set = _group_set + [f'({_dimensions[i]}, {_dimensions[j]})' for i in range(0, len(_dimensions)) for j in range(i + 1, len(_dimensions))]
                elif dq['grouping_level'] == 3:
                    _group_set = _group_set + [f'({_dimensions[i]}, {_dimensions[j]})' for i in range(0, len(_dimensions)) for j in range(i + 1, len(_dimensions))] + \
                                              [f'({_dimensions[i]}, {_dimensions[j]}, {_dimensions[k]})' for i in range(0, len(_dimensions)) for j in range(i + 1, len(_dimensions)) for k in range(j + 1, len(_dimensions))]
                
            dq['group_set'] = _group_set

            sql_filename = os.path.join(sql_subdir, config['pipeline_settings']['dag_name']+ '_' + dq['id'] + '_metric.sql')
            
            # Render template to file
            with open(sql_filename, "w") as f:  # Replaces file if already exists
                f.write(template.render(dq))


# Define Jinja global filters
def format_dict(d: Dict, indent=0):
    return d.values()
    

filters_dict = {
    "format_dict": format_dict,
}

# Define Jinja global functions
def operator_generator(operator_definition) -> None:
    """
    Helper function to generate an Airflow Operator using YAML definition.
    Supported operators include:
        - All DatabricksOperators (DatabricksSubmitRunOperator, DatabricksRunNowOperator, DatabricksSqlOperator)
        - etc.

    :param operator_definition: Required dictionary containing operator definition metadata.
        The following keys are required in the dict:
            - operator_name: String representing the name of the operator to instantiate
            - etc.
        All other keys are passed to the operator as kwargs 
    """

def raise_helper(msg: str) -> ValueError:
    """Helper function to raise exception when generating rendering the Jinja template"""
    raise ValueError(msg)


func_dict = {
    "raise": raise_helper,
}

def _main() -> None:

    template_env.filters.update(filters_dict)

    template = template_env.get_template(DAG_TEMPLATE_FILENAME)
    template.globals.update(func_dict)
    
    # Check if config directory exist
    if not os.path.isdir(CONFIG_FILEPATH):
        raise ValueError(f"`{CONFIG_FILEPATH}` does not exist.")

    YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader, base_dir=CONFIG_FILEPATH)

    # Obtain all the config files
    for filename in os.listdir(CONFIG_FILEPATH):

        if os.path.isdir(os.path.join(CONFIG_FILEPATH, filename)) or filename.startswith(('_', '.')):
            continue

        # Load config file
        f = open(os.path.join(CONFIG_FILEPATH, filename))
        config = yaml.load(f, Loader=yaml.FullLoader)
        
        # Validate config
        validate_config_file(config)

        # Generate DQ SQL files
        generate_dq_query(config)

        # Generate new DAG file
        new_dag_filename = DAG_STORAGE_PATH + config['pipeline_settings']['dag_name'] + '.py'

        # Render template to file
        with open(new_dag_filename, "w") as f:
            f.write(template.render(config))
        

##if __name__ == "__main__":

def main():

    global DAG_GENERATOR_VERSION, CONFIG_FILEPATH, DAG_STORAGE_PATH, DQ_STORAGE_PATH, DAG_TEMPLATE_FILENAME, DQ_TEMPLATE_FILENAME

    # Parse input arguments
    parser = argparse.ArgumentParser(description=f"DAG Generator v{DAG_GENERATOR_VERSION}")
    
    parser.add_argument('--config-path', type=str, required=False, dest='config_path', help=f"Path to the configurations folder. Defaults to `{CONFIG_FILEPATH}`")
    parser.add_argument('--dag-storage-path', type=str, required=False, dest='dag_storage_path', help=f"Path to the folder where generated DAGs will be stored. Defaults to `{DAG_STORAGE_PATH}`")
    parser.add_argument('--dq-storage-path', type=str, required=False, dest='dq_storage_path', help=f"Path to the folder where DQ SQL files will be stored. Defaults to `{DQ_STORAGE_PATH}`")
    
    args = parser.parse_args()
    
    if hasattr(args, 'config_path') and args.config_path:
        CONFIG_FILEPATH = args.config_path

    if hasattr(args, 'dag_storage_path') and args.dag_storage_path:
        logger.info(f'Setting DAG storage path to {args.dag_storage_path}')
        DAG_STORAGE_PATH = args.dag_storage_path

    if hasattr(args, 'dq_storage_path') and args.dq_storage_path:
        DQ_STORAGE_PATH = args.dq_storage_path

    # Check if dag storage directory exist. If not, create directory
    if not os.path.isdir(DAG_STORAGE_PATH):
        os.mkdir(DAG_STORAGE_PATH)

    # Check if dq storage directory exist. If not, create directory
    if not os.path.isdir(DQ_STORAGE_PATH):
        os.mkdir(DQ_STORAGE_PATH)

    # Generate DAGs and SQL files
    _main()

    # Run black
    os.system(f"black --line-length 124 {DAG_STORAGE_PATH}")