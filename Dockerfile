
FROM python:alpine
ENV PYTHONUNBUFFERED 1


LABEL Name=cat_bread_chat_bot Version=0.0.1
EXPOSE 3000

WORKDIR /app
ADD . /app

# Using pip:
RUN python3 -m pip install -r requirements.txt
CMD ["python3", "-m", "cat_bread_chat_bot"]
