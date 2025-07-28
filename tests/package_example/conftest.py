import pytest
import os
from dotenv import load_dotenv
from src.utilities import customlogger
import allure

# Load environment variables from a .env file
load_dotenv(os.path.abspath(".env"))

# Set up a logger
logger = customlogger.custom_logger()

# Custom command-line option for setting the database environment
def pytest_addoption(parser):
    parser.addoption(
        "--db-env",
        action="store",
        default="development",
        help="Environment for database execution (e.g. R1, V3)"
    )

# Fixture to set the DB_ENV environment variable before the session starts
@pytest.fixture(scope='session', autouse=True)
def set_db_env(request):
    db_env = request.config.getoption("--db-env")
    
    if not db_env:
        pytest.exit("Error: --db-env option is required, but not provided. Aborting Test Run.", returncode=1)
    
    os.environ['DB_ENV'] = db_env
    logger.info(f"Setting DB_ENV to {db_env}")

# Test result plugin to detect broken tests and manage retries
class TestResultPlugin:
    def __init__(self):
        self.results = {}
 
# Fixture to register the test result plugin
@pytest.fixture(scope='session', autouse=True)
def test_result_plugin(pytestconfig):
    plugin = TestResultPlugin()
    pytestconfig.pluginmanager.register(plugin, 'test-result-plugin')
    return plugin

# Pytest-BDD hook to write environment details before each scenario
def pytest_bdd_before_scenario(request, feature, scenario):
    test_pack = "SVOC_Tests"

    source_base = os.path.join("tests", test_pack)
    target_base = os.path.join("target", test_pack)

    create_allure_results_and_env_file(target_base)

    for sub_pack in os.listdir(source_base):
        sub_pack_path = os.path.join(source_base, sub_pack)

        if os.path.isdir(sub_pack_path):
            target_sub_pack_path = os.path.join(target_base, sub_pack)
            create_allure_results_and_env_file(target_sub_pack_path)
        

def create_allure_results_and_env_file(target_path):
    allure_results_path = os.path.join(target_path, "allure-results")

    if not os.path.exists(allure_results_path):
        os.makedirs(allure_results_path)

        create_env_properties_file(target_path)
    else:
        create_env_properties_file(target_path)
        pass

def create_env_properties_file(pack_path):
    os_platform = "os_platform = Microsoft Windows Server 2019 Standard"
    os_version = "os_version = 10"
    test_environment = f"test_environment = {os.environ.get('DB_ENV')}"
    build_version = "build_version = 17763"
    python_version = "python_version = Python 3.10.7"

    env_file_path = os.path.join(pack_path, "environment.properties")
    with open(env_file_path, "w") as f:
        f.write(
            f"{os_platform}\n{os_version}\n{test_environment}\n{build_version}\n{python_version}"
        )
