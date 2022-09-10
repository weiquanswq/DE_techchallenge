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
	    dff["first_name"] = dff["name"].transform(lambda x: x.split(" ")[0])
	    dff["last_name"] = dff["name"].transform(lambda x: " ".join(x.split(" ")[1:]) )
	    dff["above_100"] = dff["price"].transform(lambda x: True if x > 100 else False )	    
	    dff.to_csv(statdate+"/processed_"+file, sep=',')
	    print("File to CSV completed", file)


if __name__ == '__main__':
	print ('Argument List:', str(sys.argv))
	statdate = sys.argv[1]
	main(statdate)
```



