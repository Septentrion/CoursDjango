# Aggregate

### Introduction à l'agrégation

L'opération d'agrégation `aggregate` de MongoDB permet d'effectuer des calculs avancés et des transformations de données sur une collection. Elle permet de réaliser des opérations telles que le regroupement, le tri, le calcul de moyennes, de totaux, etc., sur les données stockées.

### Syntaxe de base de l'agrégation

La syntaxe de base de l'opération d'agrégation `aggregate` est la suivante :

```javascript
db.collection.aggregate([pipeline])
```

- `db.collection` : spécifie la collection sur laquelle effectuer l'opération d'agrégation.
- `pipeline` : une séquence de plusieurs étapes (stages) qui spécifient les différentes opérations d'agrégation à appliquer aux données. Chaque étape peut inclure un ou plusieurs opérateurs d'agrégation.

### Étapes (stages) de l'agrégation

  1. **`$match`** : Filtre les documents en fonction de critères spécifiques.
1. **`$project`** : Permet de sélectionner, d'exclure ou de renommer des champs, ainsi que de créer de nouveaux champs calculés.
1. **`$group`** : Regroupe les documents en fonction de certaines clés et effectue des calculs d'agrégation sur les données groupées.
2. **`$sort`** : Trie les documents en fonction des valeurs de champs spécifiques.
1. **`$limit`** : Limite le nombre de documents renvoyés par l'agrégation.
1. **`$skip`** : Ignore un certain nombre de documents au début de la sortie.
2. **`$unwind`** : Décompose les tableaux dans les documents en un document par élément du tableau.
1. **`$lookup`** : Effectue une jointure entre deux collections.

### Utilisation dans des cas pratiques

1. **Analyse de données** : Calcul de moyennes, totaux, nombres de documents, etc.
2. **Préparation de données** : Transformation et nettoyage des données avant analyse.
3. **Génération de rapports** : Création de rapports personnalisés à partir des données.

### Bonnes pratiques et optimisation

- Utilisez judicieusement les index pour optimiser les performances des opérations d'agrégation.
- Évitez les pipelines d'agrégation complexes autant que possible pour améliorer la lisibilité et la maintenance du code.

### 01 Exemple

Voici un exemple simple de l'opération d'agrégation `aggregate` :

```js
db.sales.aggregate([
    { $match: { date: { $gte: ISODate("2022-01-01"), $lt: ISODate("2023-01-01") } } }, // Filtre par date
    { $group: { _id: "$product", totalSales: { $sum: "$quantity" } } } // Regroupe par produit et calcule le total des ventes
])
```

Cet exemple filtre les ventes pour une année donnée, puis groupe les ventes par produit et calcule le total des ventes pour chaque produit.

## 02 Exemple de requête dans la collection restaurants.

1. Filtrer uniquement les restaurants qui ont été inspectés en 2014

```js
db.restaurants.aggregate([
  // Unwind pour dérouler le tableau des grades
  { $unwind: "$grades" },
  // Filtrer les grades qui ont une date en 2014
  { $match: { "grades.date": { $gte: ISODate("2014-01-01"), $lt: ISODate("2015-01-01") } } },
  // Regrouper par _id du restaurant pour rétablir la structure initiale
  { $group: { _id: "$_id", name: { $first: "$name" }, address: { $first: "$address" }, borough: { $first: "$borough" }, cuisine: { $first: "$cuisine" }, grades: { $push: "$grades" } } }
])

```

####  Utilisation de l'opération d'agrégation `$unwind` :
- L'opération `$unwind` est utilisée pour dérouler un tableau (array) contenu dans un document MongoDB.
- Dans notre cas, nous avons un tableau de grades dans chaque document de restaurant. Nous devons dérouler ce tableau pour pouvoir filtrer les dates d'inspection.

#### Filtrage des dates d'inspection avec `$match` :
- Une fois que nous avons déroulé le tableau des grades, nous utilisons l'opération `$match` pour filtrer les éléments en fonction de critères spécifiques.
- Nous utilisons `$match` pour sélectionner uniquement les documents où la date d'inspection est comprise entre le 1er janvier 2014 et le 1er janvier 2015.

#### Regroupement des résultats avec `$group` :
- Après avoir filtré les documents en fonction des dates d'inspection, nous utilisons l'opération `$group` pour regrouper les résultats.
- Dans notre cas, nous voulons regrouper les résultats par `_id` du restaurant et rétablir la structure initiale du document de restaurant en conservant les informations telles que le nom, l'adresse, le quartier, la cuisine, et les grades.
