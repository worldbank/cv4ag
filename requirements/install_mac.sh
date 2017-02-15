for req in $(cat requirements/mac-homebrew-pkgs.txt); do brew install $req; done
for req in $(cat requirements/python-pkgs.txt); do pip install $req; done
