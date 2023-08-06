# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mocodo']

package_data = \
{'': ['*'],
 'mocodo': ['resources/colors/*',
            'resources/font_metrics.json',
            'resources/font_metrics.json',
            'resources/lorem/*',
            'resources/pristine_sandbox.mcd',
            'resources/pristine_sandbox.mcd',
            'resources/relation_templates/*',
            'resources/res/messages_de.mo',
            'resources/res/messages_de.mo',
            'resources/res/messages_de.mo',
            'resources/res/messages_de.mo',
            'resources/res/messages_fr.mo',
            'resources/res/messages_fr.mo',
            'resources/res/messages_fr.mo',
            'resources/res/messages_fr.mo',
            'resources/res/messages_fr.po',
            'resources/res/messages_fr.po',
            'resources/res/messages_fr.po',
            'resources/res/messages_fr.po',
            'resources/res/messages_zh.mo',
            'resources/res/messages_zh.mo',
            'resources/res/messages_zh.mo',
            'resources/res/messages_zh.mo',
            'resources/shapes/*']}

entry_points = \
{'console_scripts': ['mocodo = mocodo.__main__:main']}

setup_kwargs = {
    'name': 'mocodo',
    'version': '3.2.0',
    'description': 'Modélisation Conceptuelle de Données. Nickel. Ni souris.',
    'long_description': "**15 mai 2023.** Mocodo 3.2.0 prend en charge la [visualisation des contraintes sur associations](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Visualisation-des-contraintes-sur-associations).\n\n**11 mai 2023.** Ajout d'un tutoriel / galerie d'exemples dans la [version en ligne](https://www.mocodo.net) de Mocodo 3.1.2.\n\n**24 décembre 2022.** Mocodo 3.1.1 corrige la [gestion des collisions des SVG interactifs](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Éviter-qu'une-interaction-sur-un-SVG-ne-s'applique-à-un-autre).\n\n**14 décembre 2022.** Mocodo 3.1 améliore le passage au relationnel\xa0: prise en charge de [gabarits personnels dérivés des gabarits existants](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Dérivation-de-gabarits), traitement des [tables indépendantes réduites à leur clé primaire](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Suppression-des-tables-indépendantes-réduites-à-leur-clé-primaire), génération d'un [graphe des dépendances](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Graphe-des-dépendances) pour le tri topologique des tables, [etc](https://github.com/laowantong/mocodo/releases/tag/3.1.0).\n\n**11 septembre 2022.** Mocodo 3.0 introduit l'[héritage](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Héritage-(ou-spécialisation)), l'[agrégation](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Agrégation-(ou-pseudo-entité)), les [calques](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Héritage-(ou-spécialisation)), les [sorties PDF et PNG](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Héritage-(ou-spécialisation)), [etc](https://github.com/laowantong/mocodo/releases/tag/3.0).\n\n------\n\nDocumentation [au format HTML](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html) ou sous forme de [notebook](doc/fr_refman.ipynb) Jupyter.\n\n----\n\n![](https://cdn.rawgit.com/laowantong/mocodo/master/logos/banner.svg)\n\nMocodo est un logiciel d'aide à l'enseignement et à la conception des [bases de données relationnelles](https://fr.wikipedia.org/wiki/Base_de_données_relationnelle).\n\n- En entrée, il prend une description textuelle des entités et associations du modèle conceptuel de données ([MCD](https://fr.wikipedia.org/wiki/Modèle_entité-association)).\n- En sortie, il produit son diagramme entité-association en [SVG](https://fr.wikipedia.org/wiki/Scalable_Vector_Graphics) et son schéma relationnel ([MLD](\nhttps://fr.wikipedia.org/wiki/Merise_%28informatique%29#MLD_:_mod.C3.A8le_logique_des_donn.C3.A9es)) en [SQL](https://fr.wikipedia.org/wiki/Structured_Query_Language), [LaTeX](https://fr.wikipedia.org/wiki/LaTeX), [Markdown](https://fr.wikipedia.org/wiki/Markdown), etc.\n\nCi-dessous, un exemple d'utilisation sous [Jupyter Notebook](https://jupyter.org). L'appel du programme est en première ligne, sur un texte d'entrée donné lignes suivantes. Le cas est adapté de l'article fondateur de Peter Chen, [_The entity-relationship model—toward a unified view of data_](https://doi.org/10.1145/320434.320440) (ACM Trans. Database Syst. 1, 1, March 1976, pp. 9–36), avec en bonus une association de type hiérarchique et une contrainte d'inclusion.\n\n```\n%%mocodo --mld --colors brewer+1 --shapes copperplate --relations diagram markdown_data_dict\n\nAyant-droit: nom ayant-droit, lien\nDiriger, 0N Employé, 01 Projet\nRequérir, 1N Projet, 0N Pièce: qté requise\nPièce: réf. pièce, libellé pièce\nComposer, 0N [composée] Pièce, 0N [composante] Pièce: quantité\n\nDF1, _11 Ayant-droit, 0N Employé\nEmployé: matricule, nom employé\nProjet: num. projet, nom projet\nFournir, 1N Projet, 1N Pièce, 1N Société: qté fournie\n\nDépartement: num. département, nom département\nEmployer, 11 Employé, 1N Département\nTravailler, 0N Employé, 1N Projet\nSociété: num. société, raison sociale\nContrôler, 0N< [filiale] Société, 01 [mère] Société\n\n(I) --Fournir, ->Requérir, ..Pièce, Projet\n```\n\nEn sortie, le MCD (diagramme conceptuel) et le MLD (schéma relationnel) correspondants:\n\n![](https://cdn.rawgit.com/laowantong/mocodo/master/doc/readme_1.png)\n\n**Ayant-droit** (<ins>_#matricule_</ins>, <ins>nom ayant-droit</ins>, lien)<br>\n**Composer** (<ins>_#réf. pièce composée_</ins>, <ins>_#réf. pièce composante_</ins>, quantité)<br>\n**Département** (<ins>num. département</ins>, nom département)<br>\n**Employé** (<ins>matricule</ins>, nom employé, _#num. département_)<br>\n**Fournir** (<ins>_#num. projet_</ins>, <ins>_#réf. pièce_</ins>, <ins>_#num. société_</ins>, qté fournie)<br>\n**Pièce** (<ins>réf. pièce</ins>, libellé pièce)<br>\n**Projet** (<ins>num. projet</ins>, nom projet, _#matricule_)<br>\n**Requérir** (<ins>_#num. projet_</ins>, <ins>_#réf. pièce_</ins>, qté requise)<br>\n**Société** (<ins>num. société</ins>, raison sociale, _#num. société mère_)<br>\n**Travailler** (<ins>_#matricule_</ins>, <ins>_#num. projet_</ins>)\n\nL'appel précédent a également créé un fichier `mocodo_notebook/sandbox_data_dict.md` contenant le dictionnaire des données :\n\n- nom ayant-droit\n- lien\n- quantité\n- num. département\n- nom département\n- matricule\n- nom employé\n- qté fournie\n- réf. pièce\n- libellé pièce\n- num. projet\n- nom projet\n- qté requise\n- num. société\n- raison sociale\n\nAinsi que le diagramme relationnel, qui peut être visualisé par un nouvel appel:\n\n```\n%mocodo --input mocodo_notebook/sandbox.mld --colors brewer+1\n```\n\n![](https://cdn.rawgit.com/laowantong/mocodo/master/doc/readme_2.png)\n\nLa devise de Mocodo, «\xa0nickel, ni souris\xa0», en résume les principaux points forts:\n\n- description textuelle des données. L'utilisateur n'a pas à renseigner, placer et déplacer des éléments comme avec une lessive ordinaire. Il ne fournit rien de plus que les informations définissant son MCD. L'outil s'occupe tout seul du plongement\xa0;\n- propreté du rendu. La sortie se fait en vectoriel, prête à être affichée, imprimée, agrandie, exportée dans une multitude de formats sans perte de qualité\xa0;\n- rapidité des retouches. L'utilisateur rectifie les alignements en insérant des éléments invisibles, en dupliquant des coordonnées ou en ajustant des facteurs mutiplicatifs\xa0: là encore, il travaille sur une description textuelle, et non directement sur le dessin.\n\nMocodo est libre, gratuit et multiplateforme. Si vous l'aimez, répandez la bonne nouvelle en incluant l'un de ses logos dans votre support\xa0: cela augmentera ses chances d'attirer des contributeurs qui le feront évoluer.\n\nPour vous familiariser avec Mocodo, le mieux est d'utiliser [sa version en ligne](https://www.mocodo.net).\n",
    'author': 'Aristide Grange',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://www.mocodo.net',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
