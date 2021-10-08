FROM centos:7
USER root

RUN yum -y install python36 epel-release && yum -y install python36-setuptools && yum -y clean all && easy_install-3.6 pip

ADD . /opt/

RUN pip3 install -r /opt/requirements.txt
RUN cd /opt/ && python3 setup.py install

ENTRYPOINT ["python3"]
CMD ["/opt/dropboxgallery/app.py"]
