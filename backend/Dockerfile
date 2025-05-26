FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies one by one
RUN pip install --no-cache-dir annotated-types==0.7.0
RUN pip install --no-cache-dir anyio==4.9.0
RUN pip install --no-cache-dir Authlib==1.5.2
RUN pip install --no-cache-dir cachetools==5.5.2
RUN pip install --no-cache-dir certifi==2025.4.26
RUN pip install --no-cache-dir cffi==1.17.1
RUN pip install --no-cache-dir charset-normalizer==3.4.2
RUN pip install --no-cache-dir click==8.1.7
RUN pip install --no-cache-dir colorama==0.4.6
RUN pip install --no-cache-dir cryptography==44.0.3
RUN pip install --no-cache-dir dnspython==2.7.0
RUN pip install --no-cache-dir email_validator==2.2.0
RUN pip install --no-cache-dir faiss-cpu==1.9.0
RUN pip install --no-cache-dir fastapi==0.115.2
RUN pip install --no-cache-dir fastapi-cli==0.0.7
RUN pip install --no-cache-dir filelock==3.16.1
RUN pip install --no-cache-dir fsspec==2025.3.1
RUN pip install --no-cache-dir google-ai-generativelanguage==0.6.15
RUN pip install --no-cache-dir google-api-core==2.21.0
RUN pip install --no-cache-dir google-api-python-client==2.149.0
RUN pip install --no-cache-dir google-auth==2.35.0
RUN pip install --no-cache-dir google-auth-httplib2==0.2.0
RUN pip install --no-cache-dir google-generativeai==0.8.5
RUN pip install --no-cache-dir googleapis-common-protos==1.65.0
RUN pip install --no-cache-dir greenlet==3.1.1
RUN pip install --no-cache-dir grpcio==1.66.2
RUN pip install --no-cache-dir grpcio-status==1.66.2
RUN pip install --no-cache-dir h11==0.14.0
RUN pip install --no-cache-dir httpcore==1.0.6
RUN pip install --no-cache-dir httplib2==0.22.0
RUN pip install --no-cache-dir httptools==0.6.4
RUN pip install --no-cache-dir httpx==0.27.2
RUN pip install --no-cache-dir huggingface-hub==0.26.1
RUN pip install --no-cache-dir idna==3.10
RUN pip install --no-cache-dir itsdangerous==2.2.0
RUN pip install --no-cache-dir Jinja2==3.1.4
RUN pip install --no-cache-dir joblib==1.4.2
RUN pip install --no-cache-dir markdown-it-py==3.0.0
RUN pip install --no-cache-dir MarkupSafe==2.1.5
RUN pip install --no-cache-dir mdurl==0.1.2
RUN pip install --no-cache-dir mpmath==1.3.0
RUN pip install --no-cache-dir networkx==3.4.2
RUN pip install --no-cache-dir numpy==2.1.2
RUN pip install --no-cache-dir orjson==3.10.7
RUN pip install --no-cache-dir packaging==24.1
RUN pip install --no-cache-dir pillow==11.0.0
RUN pip install --no-cache-dir prometheus_client==0.21.0
RUN pip install --no-cache-dir proto-plus==1.24.0
RUN pip install --no-cache-dir protobuf==5.28.2
RUN pip install --no-cache-dir psycopg2-binary==2.9.10
RUN pip install --no-cache-dir pyasn1==0.6.1
RUN pip install --no-cache-dir pyasn1_modules==0.4.1
RUN pip install --no-cache-dir pycparser==2.22
RUN pip install --no-cache-dir pydantic==2.9.2
RUN pip install --no-cache-dir pydantic-extra-types==2.9.0
RUN pip install --no-cache-dir pydantic-settings==2.5.2
RUN pip install --no-cache-dir pydantic_core==2.23.4
RUN pip install --no-cache-dir Pygments==2.18.0
RUN pip install --no-cache-dir pylatexenc==2.10
RUN pip install --no-cache-dir pyparsing==3.2.0
RUN pip install --no-cache-dir python-dotenv==1.0.1
RUN pip install --no-cache-dir python-multipart==0.0.12
RUN pip install --no-cache-dir PyYAML==6.0.2
RUN pip install --no-cache-dir regex==2024.9.11
RUN pip install --no-cache-dir requests==2.32.3
RUN pip install --no-cache-dir rich==13.9.2
RUN pip install --no-cache-dir rich-toolkit==0.3.0
RUN pip install --no-cache-dir rsa==4.9
RUN pip install --no-cache-dir safetensors==0.4.5
RUN pip install --no-cache-dir scikit-learn==1.5.2
RUN pip install --no-cache-dir scipy==1.14.1
RUN pip install --no-cache-dir sentence-transformers==3.2.1
RUN pip install --no-cache-dir setuptools==75.2.0
RUN pip install --no-cache-dir shellingham==1.5.4
RUN pip install --no-cache-dir sniffio==1.3.1
RUN pip install --no-cache-dir SQLAlchemy==2.0.36
RUN pip install --no-cache-dir starlette==0.40.0
RUN pip install --no-cache-dir sympy==1.14.0
RUN pip install --no-cache-dir threadpoolctl==3.5.0
RUN pip install --no-cache-dir tokenizers==0.20.1
RUN pip install --no-cache-dir torch==2.5.0
RUN pip install --no-cache-dir tqdm==4.66.5
RUN pip install --no-cache-dir transformers==4.46.0
RUN pip install --no-cache-dir typer==0.12.5
RUN pip install --no-cache-dir typing-inspection==0.9.0
RUN pip install --no-cache-dir typing_extensions==4.12.2
RUN pip install --no-cache-dir ujson==5.10.0
RUN pip install --no-cache-dir uritemplate==4.1.1
RUN pip install --no-cache-dir urllib3==2.2.3
RUN pip install --no-cache-dir uvicorn==0.32.0
RUN pip install --no-cache-dir watchfiles==0.25.0
RUN pip install --no-cache-dir websockets==13.1

# Copy the entire backend directory
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]