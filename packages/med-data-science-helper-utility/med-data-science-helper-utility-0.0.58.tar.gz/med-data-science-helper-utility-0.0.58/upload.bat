if exist "dist" rmdir /s dist
python setup.py sdist
twine upload dist/* -u analitica.avanzada -p Windows2020!!!5
PAUSE