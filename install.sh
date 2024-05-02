#!/bin/sh

###############################
# Programa: install.sh
# Desenvolvido por: Vineees (@thevinisouza)
# Data de Criacao: 12/05/2024
# Versao: 1.0.0
###############################

python --version
sleep 2
echo "Antes de Iniciar a Instalação Verique se Já Configurou o .env!"
echo""
echo "Deseja Continuar?"
read -p "Press enter to continue"""

echo "Instalando Pacotes!"
sleep 2
sudo apt install nginx
sudo apt install cron

echo "Criando Enviroment"
sleep 2
# Create environment
python3 -m venv env
# Enter environment
. env/bin/activate
echo "Enviroment Criado!"

echo "Instalando dependencias!"
# Install Deps
python3 -m pip install -r ./requirements.txt
echo "Dependencias instaladas!"

echo "Configurando Database!"
python3 manage.py makemigrations
python3 manage.py migrate
echo "Database Configurada!"

echo "Copiando Estaticos"
read -p “Informe o caminho completo para o diretorio dos estaticos (Ex:/var/www/html/morea/): “ STATICFOLDER
cp ./media $STATICFOLDER
python3 manage.py collectstatic --noinput

echo "Estaticos Copiados!"

echo "Iniciando Configuração do Web Server"
read -p “Porta para hospedar o Serviço: “ NGINXPORT
read -p “Nome no qual o Nginx escutara o request (localhost, domain.net, 192.168.1.1, etc...): “ NGINXDOMAIN
sed -i '3s/CHANGE-PORT/$NGINXPORT/' ./config/morea.conf
sed -i '3s/CHANGE-DOMAIN/$NGINXDOMAIN/' ./config/morea.conf
sed -i '3s/CHANGE-STATIC/$STATICFOLDER/' ./config/morea.conf
cp ./config/morea.conf /etc/nginx/sites-available
ln -s /etc/nginx/sites-available/morea.conf /etc/nginx/sites-enabled/
