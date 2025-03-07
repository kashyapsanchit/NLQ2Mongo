FROM python:3.10.12-slim

WORKDIR /app

COPY . /app

# Install the dependencies
RUN pip install -r requirements.txt

# Setup guardrails
# ARG GUARD_KEY

# RUN guardrails configure --enable-remote-inferencing --disable-metrics --token $GUARD_KEY
# RUN guardrails hub install hub://guardrails/toxic_language && \
#     guardrails hub install hub://guardrails/detect_pii

EXPOSE 8000

CMD ["python", "run.py"]