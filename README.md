mkdir /var/www/glosuj/assets/compressed

sudo chown -R :www-data /var/www/glosuj/logs
sudo chmod -R g+rw /var/www/glosuj/logs
sudo chown :www-data /var/www/glosuj/var
sudo chmod g+rw /var/www/glosuj/var
sudo chmod g+rw /var/www/glosuj/assets/compressed
sudo chown :www-data /var/www/glosuj/assets/compressed
sudo chmod -R g+rw /var/www/glosuj/data
sudo chown :www-data /var/www/glosuj/data


# Smoke test

 gunicorn --log-file=- website.wsgi:application
