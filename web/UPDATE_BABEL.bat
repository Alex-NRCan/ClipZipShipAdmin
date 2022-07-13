pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d translations -l en
pybabel update -i messages.pot -d translations -l fr
pybabel compile -d translations
python main.py
