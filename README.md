
# applique le differential privacy sur le résultat d'une requête à l'aide de la bibliothèque python appelée tumult

# *Installation de Tumult*

## Mettre en place un environment Python isolé

$ virtualenv -p /usr/bin/python3 env
=> regarder la commande virtualenv

## Aller dans l'environement Python isolé
$ . ./env/bin/activate

## Installer Tumutle :
 => Attention: il faut avoir installé sur la machine un runtime JAVA
  (en tant qu'adminitrateur: apt install default-jre-headless)
  
$ pip install tmlt.analytics

## Tester l'installation :
python3 -c "from tmlt.analytics.utils import check_installation; check_installation()"

# *Installation de termcolor pour colorer les messages de la console*

$ pip install termcolor

# *Installation de easygui pour la selection de fichiers*

$ pip install easygui

# *Installation de bokeh pour la visualisation 2D*

$ pip install bokeh

# *Utilisation*

## Charger l'environement Python
$ . ./env/bin/activate

