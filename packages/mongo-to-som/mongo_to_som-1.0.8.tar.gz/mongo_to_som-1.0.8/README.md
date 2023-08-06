# Mongo to Som
A small library to analyze data from MongoDB with Self Organizing Map

### Installation
```
pip install mongo-to-som
```

### Get started
How to use library:

```Python
from mongo_to_som import mongotosom

# Instantiate Mongo to Som Library
mongotosom.mongo_to_som(num_rows, num_cols, max_steps, max_m_distance, max_learning_rate, url, port, db, collection)
```