FROM public.ecr.aws/lambda/python:3.9

# Install your dependencies
RUN yum install -y gcc-c++ pkgconfig poppler-cpp-devel python3-devel poppler-utils

COPY requirements.txt ./

RUN pip install -r ./requirements.txt

COPY ./src ./src
COPY ./test.py ./test.py
# COPY ./data ./data
RUN mkdir -p ./tmp

CMD ["src.handler.main"]