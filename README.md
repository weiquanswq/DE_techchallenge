# Data Engineer Tech Challenge


## Section 1 : Data pipeline 

### Scheduler
Deploy below command in the crontab to schedule daily at 1am. 
The cronjob will trigger the python script ,S1_datapipeline.py, and pass current date to the script as parameter in the following format (YYYMMDD). logs are be captured in S1_datapipeline.log for future troubleshooting incase of failure
```sh
0 1 * * * python S1_datapipeline.py $(date +%Y%m%d) > /var/log/S1_datapipeline.log 2>&1
```

Alternative, we can use Airflow to schedule as the number of pipelines increases. Airflow will be able to configure complex dependencies and will support backfilling of pipelines.

### Scripts 
S1_datapipeline.py
The script will check for all .csv files in the directory and will process all of them. 

Assumptions: 
 1. New files will be provided in the path "Data-Engineer-Tech-Challenge"
 2. New files will be overwritten by 1am daily
 3. New files will be sent in csv format
 
The code will take in an argument from cronjob to indicate as the processing date. 
1. It will pass the argument (YYYYMMDD) as statdate to the main function 
2. It will check all .csv files that are in the folders. If there are more than 2 files, it will still be able to capture these files and process accordingly.
3. The destination directory will be generated, it will be based on the statdate and will increment daily. This will differentiate each day and prevent overwritten of files 
4.  For each file, it will loop through the data cleansing process
    4a. dropna to remove any null names;  name != "" will remmove those that are empty
    4b. Converting price to float, will remove any prepended 0
    4c. first_name and last_name are processed based on space delimited.
5. Processed file will be output to the designated output directory

In current implementation, is using Pandas to process which is single machine computation. It can be improved to be implemented in Pyspark instead, it will provide scalability and handling huge volume of data

```py
import pandas as pd
import os
import sys

setpath='Data-Engineer-Tech-Challenge/'
saluationlist =['mr.','ms.','mrs.','dr.','mdm.']

#Describe data to understand data structure
#dff["name"].describe()
#dff['price'].describe()
#dff.describe()
#dff.info()

def main(statdate):
	dff = None
	all_files = os.listdir(setpath)    
	csv_files = list(filter(lambda f: f.endswith('.csv'), all_files))
	print("list of files to process",csv_files)
	try:
		os.mkdir(statdate)
	except OSError as error:
		print(error)
	for file in csv_files:
	    dff = pd.read_csv(setpath+file)
	    print("file read - ", file)
	    # Remove any columns with Null; 
	    dff=dff.dropna()
	    # Remove any columns with Empty name; 
	    dff=dff[dff["name"] != ""]
	    # Converting to float, will remove any prepended 0; 
	    dff["price"]= dff.price.astype(float) 
	    dff["first_name"] = dff["name"].transform(lambda x: x.split(" ")[1] if x.split(" ")[0].lower() in saluationlist else x.split(" ")[0] )
	    dff["last_name"] = dff["name"].transform(lambda x: " ".join(x.split(" ")[2:]) if x.split(" ")[0].lower() in saluationlist else " ".join(x.split(" ")[1:])  )
	    dff["above_100"] = dff["price"].transform(lambda x: True if x > 100 else False )	    
	    dff.to_csv(statdate+"/processed_"+file, sep=',')
	    print("File to CSV completed", file)


if __name__ == '__main__':
	print ('Argument List:', str(sys.argv))
	statdate = sys.argv[1]
	main(statdate)
```

# Section 2: Databases 


 - Docker Image ( import container using wq_postgres.tar )
 - Created a Database cardb and uses public schema for PG design  (refer to S2_databases.ddl)
 - Entity Relationship Diagram (refer to er_diagram.jpg)
- SQL Questions ( refer to S2_databases.sql)

# Section 3 : System Design
![image](https://user-images.githubusercontent.com/23369572/189514936-fbd0560f-ce82-4628-8a82-1a39593a67c1.png)



1.  Since the data source is send over kafka broker, I would recommend Apache flume to do the ingestion of the image files. Not only can Flume consume from kafka broker, it also supports alot of source connections and as the project decided to read from different data sources, flume will be able to accomodate accordingly.Most importantly, Flume is able to scale easily when the data volume increases/decreases by starting/shutting down the agents. If connection allows, it can even access the web server to pull image files instead of going through kafka server.

2.  Flume has a HDFS sink which allows file to be written to the HDFS directly. HDFS is a distributed file System which act as a data lake storage. It will store all of the files and will only be processed when needed. Since HDFS is a file system, it will be ideal for storing unstructured data such as image, video. 

3.  Spark is recommended as the processing engine for image processing. Spark has a wide range of Machine Learning libraries and supports common language such as Python and Scala. Spark will be able to process data in parallel and ideal for processing large amount of data. Spark will be able to read/write on the HDFS and to fulfill Business Intelligence (BI)  key statistics analysis. After inital processing of images, the output/results (which will be structured format) can be written back to HDFS/ Hive table for future analysis. Likewise, Spark is able to interact with Hive table and using SQL-like to process and analyse the data. SQL is a commonly known query language which BI will be able to self-serve to analyse the data for more insights.

4.  Airflow is used as a scheduler and orchestration. It serves 2 purposes based on our current use case.   
- 1) it is to do house cleaning of HDFS. As the ingestion continues to run 24/7, the storage in HDFS will increase and some of the legacy data might not be used frequency. Airflow is able to schedule housekeeping daily to move legacy data to another location for achive or even delete to free up more space. This process will ensure the default directory only contains warm data and will increase processing perforamnce as lesser files/directory to process. However, there is a downside, is that there will be data movement and have to have a separate script to process cold data. 
- 2) BI team might have daily/ hourly pipeline which will need to run for their reporting. Airflow will be able to trigger the routine job and automate the entire process. For example, If BI want to know total number of images sent from webserver per day, this can be written into a spark schedule job to trigger in the morning and the results can be seen first thing then they reach office.

5. The Storage consists of final results output. HDFS is suitable to store raw/detailed information but it will take longer time to read due to getting resources and network latency. The storage in this section is mainly for commonly use data which are used for analysis. MYSQL is a relation Database where data is stored in a structured/Tabluar format. For example, Data scientist/BI which will need to revisist the output of the results consistently to find insights, they can read from MYSQL which able to compute analysis more efficiently than interacting with HDFS. As for Hbase is a non-relational database which is suitable for columnar data-storage where we want to store large amount of data. For example, In our current usecase, we want to know which customer has processed which type of images. the number of customer will be huge and the type of images can have many categories, it is not practical to have a fix structure of customer to categories combination. It will be wasting data storage as most of it will be empty. by storing it in Hbase, it will only store which ever categories that are applicable to the customer and resulting in saving more spaces. In addition, by setting Customer ID as the key, the performance of Hbase is able to retrieve specific key out faster and more efficiently.

6. For Data Visualisation, will process Tableau and Flask. Tableau is more on graphical visualisation to analyse the data whereas Flask is more of a API services/ web application. Both of the visualisations are compatiable with Mysql as for Hbase, will need to wrap with Phoenix to make it a connectable using JDBC.



# Section 5 : Machine learning
Predicted Value is "Low" buying power and the code and model is available in the python script. (refer to S5-Machine_learning.ipynb)

There are some handling that are taken within the script. 
- The current Machine learning problem is Classification problem. 
- The distribution of Class output is skewed towards unacc and acc which resulting the model is not well-trained
-- Based on the test record, I have filtered keeping only good and vgood class but resulting in only 130 records for training.
-- Further do a 7:3 split for train and test datasets for training of models.
- Tried implementing Logistic regression, Random forest and Decision trees and Logistic regression has a training accuaracy of 63%. Whereas the other 2 models are around 43%. However, all 3 of the models predicted "Low" output for the below parameters 
-- Maintenance = High
-- Number of doors = 4
-- Lug Boot Size = Big
-- Safety = High
-- Class Value = Good
 
