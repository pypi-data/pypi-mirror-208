# Executer les tests unitaires
```bash
python -m unittest discover --pattern=*.test.py
```

## Environement d'execution des tests unitaires du package
Afin d'exécuter les tests unitaire dans les meilleur conditions vous devez vous munir d'un serveur RabbitMQ
avec les spécifications suivant :

- Nom d'utilisateur : **guest**
- Mot de passe : **guest**
- Role de l'utilisateur **guest** : **administrator**


- Adresse IP du serveur RabbitMQ : **127.0.0.1**
- Ouvrir le port **5672**

## Build package
```bash
python -m build
```