# This file has been produced in the feature file conversion script for the process ACNT_SEG_RDIM
from src.utilities import helpers, customlogger, credentials_cryptographer as cc
from pytest_bdd import scenarios, parsers, given, when, then
from src.utilities.teradatahelper import TeradataHelper
from dotenv import load_dotenv
import pytest, os, re, allure
import pandas as pd

scenarios('../features/<FEATURE_FILE_NAME>.feature')
load_dotenv()
dbHelper = TeradataHelper(host=os.getenv('TERADATA_HOST'), user=cc.decrypt_credential(os.getenv('TERADATA_USERNAME')), password=cc.decrypt_credential(os.getenv('TERADATA_PASSWORD')))
logger = customlogger.custom_logger()

@pytest.fixture
def params(request):
    return {key: str(value.replace(' %SEP% ',', ')) for key, value in (request.node.callspec.params['_pytest_bdd_example']).items()}

@given(parsers.cfparse("Connect to the datasource"), target_fixture='conn')
def establish_connection():
    conn = dbHelper.connect()
    return conn
    
# The Make as many  instances are there are data element to check on the feature file 
@given(parsers.cfparse("Data in the {<DataElementToCheck>} exists with the above Criteria"), target_fixture='conn')
def establish_connection(DataElementToCheck):
    table_name=DataElementToCheck
    database_name = os.environ.get("DB_ENV")

    table = dbHelper.execute_query(f"SELECT CASE WHEN COUNT(*) > 0 THEN 'TRUE' ELSE 'FALSE' END AS TableExists FROM DBC.TablesV WHERE TableName = '{table_name}' AND DatabaseName like '{database_name}%';")
    table_exists = 'FALSE' not in table.loc[0, "TableExists"]
    
    assert table_exists, f"Table: {table_name} not found in ENV: {database_name}"

@when(parsers.cfparse("The {sql_query} written to validate the above Criteria is executed"), target_fixture='result')
def result(sql_query, params):
    sql_file_path = helpers.find_file(sql_query, 'tests/<E2E_AREA_NAME>/<TEMPLATE_NAME>/sql')

    assert os.path.exists(sql_file_path), f"FileNotFound The File Specified at the path {sql_file_path} does not exist"
    with open(os.path.abspath(sql_file_path)) as sql_file:
        sql_query = sql_file.read()

    sql_query = sql_query.replace("{$ENV}",f"{os.getenv('DB_ENV')}")
    for key, value in params.items():     
        sql_query = re.sub(fr'%{re.escape(key)}', value, sql_query, flags=re.IGNORECASE)

    result = dbHelper.execute_query(sql_query)
    allure.attach(sql_query, name='Executed SQL Query', attachment_type=allure.attachment_type.TEXT)

    return result 

@then(parsers.cfparse("The query result returns as PASS, validating that the Breach flags and associated dates are set correctly for Days Past Due"))
def assert_result(result, params):

    dbHelper.close_connection()
    assert isinstance(result, pd.DataFrame), f"Failure in SQL execution in {params['tst_cd']} scenario"

    if not result.empty:
        assert "FAIL" not in result.loc[0, "Test_Sql_Status"], f"Failure in {params['tst_cd']} scenario with SQL params: {params}"
    else:
        assert result.empty, f"Failure in {params['tst_cd']} scenario results dataframe not empty" 
