# Code Walkthrough & Demo Video URL
https://drive.google.com/file/d/1nUQNhi3fF5jw2wZDu0Qkg8niKtjlY9Ya/view?usp=sharing

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
``` #----- Default SonarQube server
sonar.host.url=http://localhost:9000

#----- Default source code encoding
sonar.sourceEncoding=UTF-8

#Default sonarqube connection and project config
sonar.login=admin
sonar.password=admin
sonar.projectKey=myProject
```
* Create the dockerfile as present "Sonarqube" folder, the dockerfile copies the downloaded sonarscanner binary to the container and sets the Path variable to execute sonar-scanner command
* After navigating to the folder with dockerfile run - docker build -t adityadw/sonarqube_sonarscanner .
* docker push adityadw/sonarqube_sonarscanner
## Driver/GUI
* Under "Driver" folder the file "gui.py" deals with the logic for setting up interface for all other micro-services and checking whether the micro-services are up and running before presenting the webpage to the user
* The dockerfile under "Driver" bases itself on python3 image, installs flask and request libraries required to run above logic, copies the above code to container and specifies 4 parameters with the following default values. These are the IPs of the microservices the UI will be integrating. Presently, the default values are set to IPs given by my GKE deployment, these can be changed to refer to different deployment IPs (however, these will be written by kubernetes deployment file so better to modify there)
```
HADOOP_URL http://34.136.215.85:9870/
SPARK_URL http://34.135.56.132:8080/
JUPYTER_URL http://34.133.108.43:8888/
SONAR_URL http://35.222.228.36:9000/
```
* Navigate to folder containing dockerfile and run - docker build -t adityadw/gui .
* docker push adityadw/gui
## Apache Spark
* Using docker image from https://hub.docker.com/r/bitnami/spark/
## Apache Hadoop
* Using docker images - https://hub.docker.com/r/bde2020/hadoop-namenode (for master node), https://hub.docker.com/r/bde2020/hadoop-datanode (for worker node), both with tags - 2.0.0-hadoop3.2.1-java8

# Steps to deploy on GKE
* Create a Kubernetes cluster on GCP - gcloud container clusters create --machine-type n1-standard-2 --num-nodes 2 --zone us-central1-a --cluster-version latest adityadwkubernetescluster
## Jupyter Notebook
First we need to add jupyter notebook docker image to our container registry
* docker pull adityadw/jupyter_notebook
* docker tag adityadw/jupyter_notebook:latest gcr.io/genuine-grid-327615/adityadw/jupyter_notebook:1
* docker push gcr.io/genuine-grid-327615/adityadw/jupyter_notebook:1
* The Kubernetes deployment yaml file is located under "Kubernetes-config-files" folder as "jupyter_notebook_deployment.yaml" which refers to the imported image and sets the container port as 8888, create a new yaml file using GCP text editor and paste the files contents to it
* Run - kubectl apply -f jupyter_notebook_deployment.yaml
* Create a service deployment file similar to above method, this file is located under "Kubernetes-config-files" folder as "jupyter_service.yaml" and which sets the service type as loadbalancing and exposes port 8888 via public IP
* Run kubectl apply -f jupyter_service.yaml to create the service
## Apache Spark
Similar to above we do the following -
* docker pull bitnami/spark
* docker tag bitnami/spark:latest gcr.io/genuine-grid-327615/bitnami/spark:1
* docker push gcr.io/genuine-grid-327615/bitnami/spark:1
* The deployment yaml file is located under "Kubernetes-config-files" folder as "spark_deployment.yaml" which refers to the above imported image and sets container port as 8080
* kubectl apply -f spark_deployment.yaml
* The service deployment file is located under "Kubernetes-config-files" folder as "spark_service.yaml" which ets the service type as loadbalancing and exposes port 8080 via public IP
* To deply service - kubectl apply -f spark_service.yaml
## Apache Hadoop
First we get docker images of master and worker node loaded in container registry
* docker pull bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
* docker tag bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8 gcr.io/genuine-grid-327615/bde2020/hadoop-namenode:1
* docker push gcr.io/genuine-grid-327615/bde2020/hadoop-namenode:1
* docker pull bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
* docker tag bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8 gcr.io/genuine-grid-327615/bde2020/hadoop-datanode:1
* docker push gcr.io/genuine-grid-327615/bde2020/hadoop-datanode:1
* Create deployment yaml for master apache hadoop node as located in "Kubernetes-config-files" as hadoop_master.yaml. Here we have env section which sets our hadoop cluster’s name, hdfs location and other environment variables picked up from docker-compose’s env file here. The internal port to be exposed is 9870 and 9000. Replicas are also set to 1 for 1 master node
* kubectl apply -f hadoop_master.yaml
* Create the service file for hadoop master as located in "Kubernetes-config-files" as hadoop_master_service.yaml. Here again we have a loadbalancer service which maps internal port 9870 to external 9870 and similarly for port 9000 
* kubectl apply -f hadoop_master_service.yaml to create the service deployment
Now, we need to attach 2 worker nodes to this master node
* Create worker hadoop deployment as located in "Kubernetes-config-files" as hadoop_worker.yaml. Here there is an environment variable called Service_Precondition which points the hadoop worker to master using kubedns and its value is set to master-hadoop service that we deployed in the previous step. We copy the other remaining environment variables similar to the previous step from docker compose’s env file. Here we have set the replicas as 2 for two data-nodes.
* kubectl apply -f hadoop_worker.yaml which creates deployment with 2 replicas and this now connects to the master node
## Sonarqube and Sonarscanner
First, we will get the image loaded in container registry
* docker pull adityadw/sonarqube_sonarscanner
* docker tag adityadw/sonarqube_sonarscanner:latest gcr.io/genuine-grid-327615/adityadw/sonarqube_sonarscanner:1
* docker push gcr.io/genuine-grid-327615/adityadw/sonarqube_sonarscanner:1
* Create the sonarqube deployment as located in "Kubernetes-config-files" as sonarqube_deployment.yaml, exposing internal port 9000
* kubectl apply -f sonarqube_deployment.yaml
* Create sonarqube service as located in "Kubernetes-config-files" as sonarqube_service.yaml, mapping internal port 9000 to external port 9000. It’s of type LoadBalancer so that it can be accessed via public IP
* kubectl apply -f sonarqube_service.yaml - to deploy the service
## GUI
First, we will get the image loaded in container registry
* docker pull adityadw/gui
* docker tag adityadw/gui:latest gcr.io/genuine-grid-327615/adityadw/gui:1
* docker push gcr.io/genuine-grid-327615/adityadw/gui:1
* Create deployment yaml file as located in "Kubernetes-config-files" as gui_deployment.yaml with image referring to above imported image and environment variables which set the public IPs for hadoop, spark, jupyter and sonar respectively declared in the dockerfile and container port as 8080. The following env variables need to be configured according to public IPs received after deploying the above 4 micro-services - 
```
name: HADOOP_URL
value: http://34.136.215.85:9870/
name: SPARK_URL
value: http://34.135.56.132:8080/
name: JUPYTER_URL
value: http://34.135.31.100:8888/
name: SONAR_URL
value: http://35.222.228.36:9000/
```
* kubectl apply -f gui_deployment.yaml
* Create a load-balancer service to expose using public IP and map external port 8080 to target port 8080. The service file is located under "Kubernetes-config-files" as gui_service.yaml
* kubectl apply -f gui_service.yaml - to deploy the service

## For screenshots and detailed steps refer to - Cloud-Infra-Project-Readme.pdf
## Appendix
To run a sample Sonar-Scanner using the new password that was set, one can use kubectl get pods to get the pod ID of sonarqube and then the following two commands to run sample scan
kubectl exec --stdin --tty <pod-id> -- /bin/bash
sonar-scanner -D sonar.password='new_password'
For checkpoint related content please refer to folder "Checkpoint-files"

## References
https://hub.docker.com/_/microsoft-mmlspark-release, https://github.com/big-data-europe/docker-hadoop/blob/master/docker-compose.yml, https://www.datamechanics.co/blog-post/optimized-spark-docker-images-now-available, https://computingforgeeks.com/how-to-install-apache-spark-on-ubuntu-debian/, https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
https://www.geeksforgeeks.org/python-3-input-function/
https://stackoverflow.com/questions/27093612/in-a-dockerfile-how-to-update-path-environment-variable
https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
https://www.edureka.co/community/7415/copy-is-not-working-in-docker
https://github.com/mohamedfarag/14-848-extra-credit-project
https://github.com/rinormaloku/k8s-mastery/tree/master/resource-manifests
https://kubernetes.io/docs/tasks/debug-application-cluster/get-shell-running-container/
https://github.com/big-data-europe/docker-hadoop
https://flask.palletsprojects.com/en/2.0.x/quickstart/
https://github.com/rinormaloku/k8s-mastery/blob/master/sa-webapp/Dockerfile
https://www.w3schools.com/html/html_lists.asp
https://piazza.com/class/ksnwtglzkui2vr?cid=109