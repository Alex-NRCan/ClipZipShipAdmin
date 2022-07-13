echo pip install Sphinx
echo pip install sphinxcontrib-napoleon
echo pip install sphinx-rtd-theme

cd C:\Users\alexandre.roy\pygeoapi\pygeoapi-admin\docs

call sphinx-apidoc -o ../docs/source_api ..\core
call sphinx-apidoc -o ../docs/source_api ..\api
call make_api clean
call make_api html

call sphinx-apidoc -o ../docs/source_web ..\core
call sphinx-apidoc -o ../docs/source_web ..\web
call make_web clean
call make_web html

cd C:\Users\alexandre.roy\pygeoapi\pygeoapi-admin

