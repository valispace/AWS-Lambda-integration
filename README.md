# Building and Packaging a AWS Lambda Layer 
Packaging Lambda function Layers with Valispace Python API and other code dependencies.

For more on AWS Lambda integration, see the [Documentation page](https://valispace.zendesk.com/knowledge/articles/360015142758/en-us).
### To-do:
1. Add a basic package layer with numpy and Valispace.
2. Add a basic Docker base image with numpy and Valispace.

## Pre-Requisites
- [Docker](https://www.docker.com/)


## To build package from scratch

1. Create a Dockerfile with Amazonlinux or valispace base image.
```
FROM amazonlinux:latest
RUN yum install -y python37 && \
    yum install -y python3-pip && \
    yum install -y zip && \
    yum clean all
RUN python3.7 -m pip install --upgrade pip && \
    python3.7 -m pip install virtualenv && \
    python3.7 -m pip install valispace
```

2. Build the Dockerfile.

`docker build -t "valispace:python_lambda" . `

3. Check docker image list

`docker image list`

4. Run the container in bash mode.

`docker run -it --name  valispace valispace:local_python_lambda bash`

5. Add necessary packages.

`bash> pip install valispace -t ./python`

`bash> pip install scipy -t ./python`

`bash> pip install numpy -t ./python`

6. Package it up.

`bash> zip -r python.zip ./python/`

7. Copy it to a local directory

`docker cp valispace:python.zip .`

### You can now upload this zip package as a Lambda layer.

If you run into problems, let us know through Issues, or by writing to us at contact-us[at]valispace.com
