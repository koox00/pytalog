apt-get -qqy update
apt-get -qqy install libpq-devel python-dev
apt-get -qqy install python-sqlalchemy
apt-get -qqy install python-pip
pip install virtualenv &&
cd /vagrant/pytalog &&
virtualenv env &&
. env/bin/activate
