### Build and install packages
FROM python:3.8 as build-python

RUN apt-get -y update \
  && apt-get install -y gettext \
  # Cleanup apt cache
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
RUN groupadd -r django && useradd -r -g django django

RUN apt-get update \
  && apt-get install -y \
  libcairo2 \
  libgdk-pixbuf2.0-0 \
  liblcms2-2 \
  libopenjp2-7 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libssl3 \
  libtiff6 \
  libwebp7 \
  libxml2 \
  libpq5 \
  shared-mime-info \
  mime-support \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*


RUN echo 'image/webp webp' >> /etc/mime.types
RUN echo 'image/avif avif' >> /etc/mime.types

RUN mkdir -p /app/media /app/django_static /app/data-app \
  && chown -R django:django /app/

COPY . /app
WORKDIR /app
RUN python manage.py collectstatic --no-input

EXPOSE 8000
ENV PYTHONUNBUFFERED 1
RUN pip install uvicorn

CMD ["gunicorn", "--bind", ":8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "tealcrm.asgi:application"]

