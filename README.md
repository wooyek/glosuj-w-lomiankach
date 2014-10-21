# Głosuj w Łomiankach bez meldunku

Serwis pozwalający na wygenerowanie wniosku o wpisanie do rejestru wyborców
 
Serwis przygotowany przez [KKW Dialog Zmieni Łomianki](http://dialoglomianki.pl/)

Pomagamy naszym wyborcom zamieszkałym w Łomiankach w oddaniu głosu na [Witolda Gawdę](http://dialoglomianki.pl/witold-gawda.html) bez zmiany aktualnego meldunku.

### Instalacja w skrócie

mkdir /var/www/glosuj/assets/compressed
sudo chmod g+rw /var/www/glosuj/assets/compressed
sudo chown :www-data /var/www/glosuj/assets/compressed
sudo chown -R :www-data /var/www/glosuj/logs
sudo chmod -R g+rw /var/www/glosuj/logs
sudo chown :www-data /var/www/glosuj/var
sudo chmod g+rw /var/www/glosuj/var
sudo chmod -R g+rw /var/www/glosuj/data
sudo chown :www-data /var/www/glosuj/data

### Smoke test

gunicorn --log-file=- website.wsgi:application
