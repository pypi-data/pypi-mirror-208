FROM python:3.8 AS build_image
FROM google/cloud-sdk:latest AS gcloud_image

COPY --from=build_image ./ ./

# Install dvc dependecies
RUN pip3 install 'dvc==2.8.1'
RUN pip3 install 'dvc[gs]'

# Create virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY batch_files/requirements_batch.txt .
COPY requirements_docker.txt .

RUN . $VIRTUAL_ENV/bin/activate && \
      $VIRTUAL_ENV/bin/python3 -m pip install -r requirements_batch.txt && \
      $VIRTUAL_ENV/bin/python3 -m pip install -r requirements_docker.txt
RUN pip install wheel