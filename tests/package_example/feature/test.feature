@test
Feature: For testname
  Scenario Outline: testname
    Description:  
    Given Connect to the datasource
    And  Data in the <data_entity> exists with the above Criteria
    When The <sql_query> written to validate the above Criteria is executed
    Then testname No rows are returned

    Examples:
      | tst_cd	| data_entity   | proc_typ_cd 	| sql_query | p_n|
      | test	| test			|test			|test.sql	|test|
