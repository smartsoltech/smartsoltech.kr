# Dockerfile for Django Application

# Base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the project files to the container
COPY . /app/

# Replace the template file inside the container
COPY patch/fieldset.html /usr/local/lib/python3.10/site-packages/jazzmin/templates/admin/includes/fieldset.html

# Collect static files
RUN python smartsoltech/manage.py collectstatic --noinput || true

# Expose the port for the Django application
EXPOSE 8000

# Start the Django server
CMD ["python", "smartsoltech/manage.py", "runserver", "0.0.0.0:8000"]