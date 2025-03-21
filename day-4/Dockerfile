FROM public.ecr.aws/lambda/python:3.9

# Install dependencies
RUN yum install -y unzip tar gzip curl \
    && curl -LO "https://dl.k8s.io/release/v1.27.1/bin/linux/arm64/kubectl" \
    && chmod +x kubectl && mv kubectl /usr/local/bin/ \
    && curl -o aws-iam-authenticator https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/latest/download/aws-iam-authenticator-linux-arm64 \
    && chmod +x aws-iam-authenticator && mv aws-iam-authenticator /usr/local/bin/

# Set working directory
WORKDIR /var/task

# Copy Lambda function code
COPY lambda_function.py .

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run the Lambda function
CMD ["lambda_function.lambda_handler"]
