#reference - https://flask.palletsprojects.com/en/2.0.x/quickstart/
from flask import Flask
import sys,requests,time,os

app = Flask(__name__)
hadoop_url=''
spark_url=''
jupyter_url=''
sonarqube_url=''

#function to check if the micro-services are up and running by making the get request to their addresses
def checkServices():
    hadoop=requests.get(hadoop_url).status_code
    spark=requests.get(spark_url).status_code
    jupyter=requests.get(jupyter_url).status_code
    sonarqube=requests.get(sonarqube_url).status_code

    if hadoop==200 and spark==200 and jupyter==200 and sonarqube==200:
        return True
    else:
        return False


@app.route("/")
def terminal():
    #returning the webpage with hyperlinks
    return "<H1> Welcome to Big Data Processing Application </H1> <p> Please click on link to chose which application you would like to run </p>"\
        +"<ol> <li> <a href="+hadoop_url+"> Apache Hadoop</a></li> <li> <a href="+spark_url+"> Apache Spark </a></li> <li> <a href="+jupyter_url+"> Jupyter Notebook </a></li> <li><a href="+sonarqube_url+"> SonarQube and SonarScanner </a></li></ol>"

#setting the urls using env variables
hadoop_url=os.environ['HADOOP_URL']
spark_url=os.environ['SPARK_URL']
jupyter_url=os.environ['JUPYTER_URL']
sonarqube_url=os.environ['SONAR_URL']

#check every 3 seconds if micro-services are up or not
while(checkServices()==False):
    print('Services not yet up')
    time.sleep(3)

app.run(host='0.0.0.0',port=8080)