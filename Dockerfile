FROM debian

RUN apt update
RUN apt install -y vim curl
RUN apt install -y apache2 apache2-utils libapache2-mod-wsgi-py3
RUN apt install -y python3 python3-pip
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN mkdir /django && mkdir /django/macau
COPY ./ /django/macau
RUN pip install -r /django/macau/requirements.txt
RUN /django/macau/manage.py makemigrations && /django/macau/manage.py migrate 
RUN cp /django/macau/configs/macau.conf /etc/apache2/sites-available
RUN ln -s /etc/apache2/sites-available/macau.conf /etc/apache2/sites-enabled/macau.conf
RUN rm /etc/apache2/sites-enabled/000-default.conf
RUN chown -R www-data:www-data /django
RUN chown root:root /django/macau/entrypoint.sh
RUN chmod 700 /django/macau/entrypoint.sh

ENV USERNAME=admin
ENV EMAIL=admin@domain.example
ENV PASS=admin

CMD echo $USERNAME 


CMD /django/macau/entrypoint.sh $USERNAME $EMAIL $PASS


