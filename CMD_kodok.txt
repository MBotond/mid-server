py -3 -m venv venv
venv\Scripts\activate

pip install Flask
pip install requests
pip install flask-cors 

set FLASK_APP=main.py
flask run

