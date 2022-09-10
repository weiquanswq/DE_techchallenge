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

