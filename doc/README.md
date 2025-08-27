# Documentation de C3PO

## TL;DR

Exécuter:

```bash
pip install -r ./requirements.txt
make html
```

## Prérequis Python

- les prérequis listés dans `requirements.txt`

## Contenu du répertoire doc/

Ce répertoire contient :

- Makefile
- requirements.txt
- source/

### Le fichier Makefile

Permet de lancer la commande "make html" pour générer la documentation de C3PO.

Pour supprimer le répertoire de compilation "build", on peut lancer la commande :

```bash
make clean
```

ou

```bash
rm -r build/
```

### Le fichier requirements.txt

Contient les versions des prérequis nécessaires pour générer les documentations C3PO et ReadTheDoc.

### Le répertoire source/

Le répertoire "source/" contient :

- code\_integration.rst
    Contient le chapitre "How to use a code with C3PO".

- mainpage.rst
    Contient le chapitre "C3PO documentation".

- index.rst
    Fichier principal de la documentation. Contient la table des matières principale de la
    documentation.

- conf.py
    Script de configuration du projet Sphinx.

- \_apidoc\_templates/
    Répertoire qui contient les templates des fichiers .rst du projet Sphinx.

Les fichiers .rst sont générés automatiquement par la commande "make html" via le script de
configuration "conf.py".

## Ajout de code

### Ajout d'une fonction

Si un script Python ne contient que des fonctions, elles seront automatiquement détectées par
Sphinx. Il n'est pas nécessaire de les importées depuis le fichier `c3po/__init__.py`.

Il en va de même si une fonction est ajouté dans un scipt déjà existant.

### Ajout d'une classe

Si la classe est ajoutée dans un script Python existant, et que ce dernier est appelé par
`c3po/__init__.py`, il n'y a aucun problème. Elle sera détectée par Sphinx.

Si la classe est ajoutée dans un nouveau script, le fichier `doc/source/conf.py` se chargera de
charger la nouvelle classe dans `c3po/__init__.py`.

### Docstrings

Dans un script Python qui contient une classe, si l'on fait référence à une de ses méthodes, Sphinx
saura créé un lien vers la méthode en question :

```rst
:meth:`methode`
```

Dans le cas où la classe hérite d'une classe parente, et que l'on souhaite faire référence à une
méthode que la classe fille ne surcharge pas, on peut :

- Faire un lien explicite vers la classe parente :

  ```rst
  :meth:`.class_parente.methode`
  ```

- Utiliser une substitution définie directement dans la docstring :

  ```rst
  :meth:`methode <~classe_parente.methode>`
  ```

- Utiliser une substitution définie à la fin du fichier .rst du module (Ces substitutions sont
  définies dans le template pour être automatiquement ajoutées dans les fichiers .rst
  correspondants) :

  ```rst
  |substitution_methode|
  
  .. |substitution_methode| replace:: :meth:`.class_parente.methode`
  ```

  Cette solution est pratique lorsque l'on a plusieurs occurences d'une même substitution.

  Elle est également pratique si une méthode fille ne surcharge pas la docstring de la méthode mère.

  **Exemple :**

  - `Fichier1.py`

    ```python
    class Mere(object):
        ...
        def methode1():
            # Lien vers methode2 bien créé.
            """
            Voir :meth:`methode2` 
            """
            ...
    
        def methode2():
            ...
    ```

  - `Fichier2.py`

    ```python
    from Fichier1 import Mere

    class Fille(Mere):
        ...
        def methode1(): # <- Méthode surchargée
            ...         # <- Docstring pas surchargée, donc docstring Mere.
                        # <- Aucun lien vers methode2 car elle n'est pas
                        #    surchargée par la classe Fille.
    ```

  - `Fichier3.py`

    ```python
    from Fichier1 import Mere

    class Fille2(Mere):
        ...
        def methode1(): # <- Méthode surchargée
            ...         # <- Docstring pas surchargée, donc docstring Mere.
                        # <- Lien vers methode2 créé car elle est surchargée.


        def methode2(): # <- Méthode surchargée
            ...
    ```

  **Solution :**

  - `Fichier1.py`

    ```python
    class Mere(object):
        ...
        def methode1():
            # Lien vers methode2 bien créé grâce à la docstring.
            """
            Voir |methode2|
            """
    
        def methode2():
            ...
    ```

  - `Fichier2.py`

    ```python
    from Fichier1 import Mere

    class Fille(Mere):
        ...
        def methode1(): # <- Méthode surchargée
            ...         # <- Docstring pas surchargée, donc docstring Mere.
                        # <- Lien créé vers methode2 de Mere grâce à la substitution.
    ```

  - `Fichier3.py`

    ```python
    from Fichier1 import Mere

    class Fille2(Mere):
        ...
        def methode1(): # <- Méthode surchargée
            ...         # <- Docstring pas surchargée, donc docstring Mere.
                        # <- Lien créé vers methode2 de Mere grâce à la substitution.

        def methode2(): # <- Méthode surchargée
            ...
    ```


  - `Fichier1.rst`

    ```rst
    Fichier1
    ========

    ...

    .. |methode2| replace:: :meth:`~Mere.methode2`
    ```

  - `Fichier2.rst`

    ```rst
    Fichier2
    ========

    ...

    .. |methode2| replace:: :meth:`~Mere.methode2`
    ```

  - `Fichier3.rst`

    ```rst
    Fichier3
    ========

    ...

    .. |methode2| replace:: :meth:`~Fille2.methode2`
    ```

### Les importations

Si dans un script Python un module externe est importé, il est nécessaire que ce module soit présent
dans l'environnement virtuel Python qui contient Sphinx.

Dans le cas contraire, il faut ajouter le module externe à la liste `autodoc_mock_imports`, au
risque d'avoir des erreurs lors de la génération de la documentation.
