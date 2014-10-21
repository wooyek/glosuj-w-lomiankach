pybabel extract -F babel.cfg -o .tmp\messages.pot .
pybabel init -i .tmp\messages.pot -d translations -l pl
pybabel update -i .tmp\messages.pot -d translations
