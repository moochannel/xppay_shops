FROM python:3.6-onbuild

EXPOSE 8000
ENV \
    DJANGO_SETTINGS_MODULE=xppay.settings_production
RUN \
    chmod +x /usr/src/app/docker-entrypoint.sh
WORKDIR /usr/src/app/xppay
ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]
CMD ["gunicorn", "-k", "gevent", "-w", "3", "--timeout=600", \
    "--bind=0.0.0.0:8000", "--access-logfile=-", "--error-logfile=-", \
    "xppay.wsgi"]
