# Docker Images URL
* Jupyter Notebook - https://hub.docker.com/r/adityadw/jupyter_notebook
* Sonarqube + Sonarscanner - https://hub.docker.com/r/adityadw/sonarqube_sonarscanner
* Driver/GUI - https://hub.docker.com/r/adityadw/gui
* Apache Spark - https://hub.docker.com/r/bitnami/spark/
* Apache Hadoop - https://hub.docker.com/r/bde2020/hadoop-namenode (for master node), https://hub.docker.com/r/bde2020/hadoop-datanode (for worker node), both with tags - 2.0.0-hadoop3.2.1-java8
# Steps to build the docker images
## Jupyter Notebook
* Base image on which the new image is created is - mcr.microsoft.com/mmlspark/release. Get this image using docker pull mcr.microsoft.com/mmlspark/release
* Create the dockerfile as listed in the folder "Jupyter" which adds command to run the Jupyter Notebook on top of base image
* Navigate to dockerfile directory
* docker build -t adityadw/jupyter_notebook .
* To test locally run - docker run -it -p 8888:8888 adityadw/jupyter_notebook and navigate to localhost:8888 and see if the jupyter notebook UI comes up
* Run docker push adityadw/jupyter_notebook to upload it to dockerhub
## SonarQube and SonarScanner
* Get the base image - docker pull sonarqube
* Download sonar-scanner for any platform which requires pre-installed JVM from here https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.6.2.2472.zip
* Edit sonar-scanner configuration file located under config folder adding the following parameters
''' #----- Default SonarQube server
sonar.host.url=http://localhost:9000

#----- Default source code encoding
sonar.sourceEncoding=UTF-8

#Default sonarqube connection and project config
sonar.login=admin
sonar.password=admin
sonar.projectKey=myProject
'''
* Create the dockerfile as present "Sonarqube" folder, the dockerfile copies the downloaded sonarscanner binary to the container and sets the Path variable to execute sonar-scanner command
* After navigating to the folder with dockerfile run - docker build -t adityadw/sonarqube_sonarscanner .
* docker push adityadw/sonarqube_sonarscanner
## Driver/GUI
* Under "Driver" folder the file "gui.py" deals with the logic for setting up interface for all other micro-services and checking whether the micro-services are up and running before presenting the webpage to the user
* The dockerfile under "Driver" bases itself on python3 image, installs flask and request libraries required to run above logic, copies the above code to container and specifies 4 parameters with the following default values. These are the IPs of the microservices the UI will be integrating. Presently, the default values are set to IPs given by my GKE deployment, these can be changed to refer to different deployment IPs (however, these will be written by kubernetes deployment file so better to modify there)
'''
HADOOP_URL http://34.136.215.85:9870/
SPARK_URL http://34.135.56.132:8080/
JUPYTER_URL http://34.133.108.43:8888/
SONAR_URL http://35.222.228.36:9000/
'''
* Navigate to folder containing dockerfile and run - docker build -t adityadw/gui .
* docker push adityadw/gui
## Apache Spark
* Using docker image from https://hub.docker.com/r/bitnami/spark/
## Apache Hadoop
* Using docker images - https://hub.docker.com/r/bde2020/hadoop-namenode (for master node), https://hub.docker.com/r/bde2020/hadoop-datanode (for worker node), both with tags - 2.0.0-hadoop3.2.1-java8