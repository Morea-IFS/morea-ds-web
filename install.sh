#!/bin/sh
python --version
sleep 2

echo "Deseja Continuar?"
read -p "Press enter to continue"""

echo "Criando Enviroment"
sleep 2
python3 -m venv env
. env/bin/activate

echo "Enviroment Criado!"
echo "Instalando dependencias!"

python3 -m pip install -r ./requirements.txt

echo "Dependencias instaladas!"
echo "Configurando Database!"

python3 manage.py makemigrations
python3 manage.py migrate

echo "Database Configurado!"
echo "Copiando Estaticos"

cp ./media /var/www/html/Morea/
python3 manage.py collectstatic --noinput

echo "Estaticos Copiados!"