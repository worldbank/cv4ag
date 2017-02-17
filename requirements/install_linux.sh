for req in $(cat requirements/linux-deb-pkgs.txt); do apt install $req; done
for req in $(cat requirements/python-pkgs.txt); do pip install $req; done
