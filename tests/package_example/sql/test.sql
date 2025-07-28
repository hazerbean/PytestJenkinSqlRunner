SELECT'%TST_CD' AS Test_Cd,
'%Data_Entity' AS Data_Entity,
'%Data_Attribute' AS Data_Attribute,
'FAIL' AS Test_Sql_Status
FROM
  (SELECT (CASE
               WHEN COUNT(1) = 0 THEN 'Pass'
               ELSE 'FAIL'
           END) AS tst_Result
   FROM
     ()
tst_SQL
WHERE tst_SQL.tst_Result = 'FAIL';
