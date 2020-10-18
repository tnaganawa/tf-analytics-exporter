FROM centos:8
RUN dnf install -y python3 curl && alternatives --set python /usr/bin/python3
RUN pip3 install prometheus_client requests
RUN cd /root/ && curl -O https://raw.githubusercontent.com/tnaganawa/tf-analytics-exporter/master/tf-analytics-exporter.py && chmod 755 tf-analytics-exporter.py
CMD ["/bin/bash", "-c", "/root/tf-analytics-exporter.py"]
