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
    'version': '3.1.2',
    'description': 'Modélisation Conceptuelle de Données. Nickel. Ni souris.',
    'long_description': "**11 mai 2023.** Ajout d'un tutoriel / galerie d'exemples dans la [version en ligne](https://www.mocodo.net) de Mocodo 3.1.2.\n\n**24 décembre 2022.** Mocodo 3.1.1 corrige la [gestion des collisions des SVG interactifs](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Éviter-qu'une-interaction-sur-un-SVG-ne-s'applique-à-un-autre).\n\n**14 décembre 2022.** Mocodo 3.1 améliore le passage au relationnel\xa0: prise en charge de [gabarits personnels dérivés des gabarits existants](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Dérivation-de-gabarits), traitement des [tables indépendantes réduites à leur clé primaire](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Suppression-des-tables-indépendantes-réduites-à-leur-clé-primaire), génération d'un [graphe des dépendances](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Graphe-des-dépendances) pour le tri topologique des tables, [etc](https://github.com/laowantong/mocodo/releases/tag/3.1.0).\n\n**11 septembre 2022.** Mocodo 3.0 introduit l'[héritage](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Héritage-(ou-spécialisation)), l'[agrégation](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Agrégation-(ou-pseudo-entité)), les [calques](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Héritage-(ou-spécialisation)), les [sorties PDF et PNG](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html#Héritage-(ou-spécialisation)), [etc](https://github.com/laowantong/mocodo/releases/tag/3.0).\n\n------\n\n![](https://cdn.rawgit.com/laowantong/mocodo/master/logos/banner.svg)\n\nMocodo est un logiciel d'aide à l'enseignement et à la conception des [bases de données relationnelles](https://fr.wikipedia.org/wiki/Base_de_données_relationnelle).\n\n- En entrée, il prend une description textuelle des entités et associations du modèle conceptuel de données ([MCD](https://fr.wikipedia.org/wiki/Modèle_entité-association)).\n- En sortie, il produit son diagramme entité-association en [SVG](https://fr.wikipedia.org/wiki/Scalable_Vector_Graphics) et son schéma relationnel ([MLD](\nhttps://fr.wikipedia.org/wiki/Merise_%28informatique%29#MLD_:_mod.C3.A8le_logique_des_donn.C3.A9es)) en [SQL](https://fr.wikipedia.org/wiki/Structured_Query_Language), [LaTeX](https://fr.wikipedia.org/wiki/LaTeX), [Markdown](https://fr.wikipedia.org/wiki/Markdown), etc.\n\nCi-dessous, un exemple sous [Jupyter Notebook](https://jupyter.org). L'appel du programme se fait en première ligne, sur un texte d'entrée donné lignes suivantes.\n\n```\n%%mocodo --mld --colors brewer+1 --shapes copperplate --relations diagram markdown_data_dict\nDF, 11 Élève, 1N Classe\nClasse: Num. classe, Num. salle\nFaire Cours, 1N Classe, 1N Prof: Vol. horaire\nCatégorie: Code catégorie, Nom catégorie\n\nÉlève: Num. élève, Nom élève\nNoter, 1N Élève, 0N Prof, 0N Matière, 1N Date: Note\nProf: Num. prof, Nom prof\nRelever, 0N Catégorie, 11 Prof\n\nDate: Date\nMatière: Libellé matière\nEnseigner, 11 Prof, 1N Matière\n```\n\nEn sortie, le MCD (diagramme conceptuel) et le MLD (schéma relationnel) correspondants:\n\n![](https://cdn.rawgit.com/laowantong/mocodo/master/doc/readme_1.svg)\n\n**Catégorie** (<ins>Code catégorie</ins>, Nom catégorie)<br>\n**Classe** (<ins>Num. classe</ins>, Num. salle)<br>\n**Faire Cours** (<ins>_#Num. classe_</ins>, <ins>_#Num. prof_</ins>, Vol. horaire)<br>\n**Noter** (<ins>_#Num. élève_</ins>, <ins>_#Num. prof_</ins>, <ins>_#Libellé matière_</ins>, <ins>_#Date_</ins>, Note)<br>\n**Prof** (<ins>Num. prof</ins>, Nom prof, _#Code catégorie_, _#Libellé matière_)<br>\n**Élève** (<ins>Num. élève</ins>, Nom élève, _#Num. classe_)\n\nL'appel ci-dessus a également construit le dictionnaire des données:\n\n- Num. classe\n- Num. salle\n- Vol. horaire\n- Code catégorie\n- Nom catégorie\n- Num. élève\n- Nom élève\n- Note\n- Num. prof\n- Nom prof\n- Date\n- Libellé matière\n\nAinsi que le diagramme relationnel, qui peut être visualisé par un nouvel appel:\n\n```\n%mocodo --input mocodo_notebook/sandbox.mld --colors brewer+1\n```\n\n![](https://cdn.rawgit.com/laowantong/mocodo/f06f70a/doc/readme_2.svg)\n\nLa devise de Mocodo, «\xa0nickel, ni souris\xa0», en résume les principaux points forts:\n\n- description textuelle des données. L'utilisateur n'a pas à renseigner, placer et déplacer des éléments comme avec une lessive ordinaire. Il ne fournit rien de plus que les informations définissant son MCD. L'outil s'occupe tout seul du plongement;\n- propreté du rendu. La sortie se fait en vectoriel, prête à être affichée, imprimée, agrandie, exportée dans une multitude de formats sans perte de qualité;\n- rapidité des retouches. L'utilisateur rectifie les alignements en insérant des éléments invisibles, en dupliquant des coordonnées ou en ajustant des facteurs mutiplicatifs: là encore, il travaille sur une description textuelle, et non directement sur le dessin.\n\nMocodo est libre, gratuit et multiplateforme. Si vous l'aimez, répandez la bonne nouvelle en incluant l'un de ses logos dans votre support: cela multipliera ses chances d'attirer des contributeurs qui le feront évoluer.\n\nPour vous familiariser avec Mocodo, le mieux est d'utiliser [sa version en ligne](https://www.mocodo.net).\n\nPour en savoir plus, lisez la documentation [au format HTML](https://rawgit.com/laowantong/mocodo/master/doc/fr_refman.html) ou téléchargez-la [au format Jupyter Notebook](doc/fr_refman.ipynb).\n",
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
