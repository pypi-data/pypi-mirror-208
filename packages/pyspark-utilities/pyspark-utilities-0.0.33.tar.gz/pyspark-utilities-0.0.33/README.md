# spark-utilities

Spark utilities for BDA-services.

Pyspark utilities supports the following storage to load/save datasets:

- FileSystem
- Hdfs
- Presto
- Hive

"spark_initalizer" method automatically sets the Spark session based on the input/output data storage type.