for req in $(cat mac-homebrew-pkgs.txt); do brew install $req; done
for req in $(cat python-pkgs.txt); do pip install $req; done
