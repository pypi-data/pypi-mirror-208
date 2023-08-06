import pandas as pd
from sklearn.impute import KNNImputer
from pymongo import MongoClient
import numpy as np
import csv
from numpy.ma.core import ceil
from scipy.spatial import distance #distance calculation
from sklearn.preprocessing import MinMaxScaler #normalisation
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from matplotlib import colors
import time


class mongo_to_som:
  def __init__(self, num_rows, num_cols, max_steps, max_m_distance, max_learning_rate, url, port, db, collection):
    self.num_rows = num_rows
    self.num_cols = num_cols
    self.max_steps = max_steps
    self.url = url
    self.port = port
    self.db = db
    self.collection = collection
    self.max_m_distance = max_m_distance
    self.max_learning_rate = max_learning_rate

    start_time = time.time()

    client = MongoClient(self.url, self.port)
    db = client[self.db]
    collection = db[self.collection]

    data = list(collection.find())
    df = pd.DataFrame(data)

    # Calculate percentage of non-null values in each column
    threshold = 0.9
    col_perc = df.count() / df.shape[0]

    # Filter columns based on percentage threshold
    keep_cols = col_perc[col_perc >= threshold].index.tolist()
    # Keep only the desired columns
    data = list(collection.find({}, {'_id': 0, **{col: 1 for col in keep_cols}}))
    df = pd.DataFrame(data)

    missing_cols = df.columns[df.isna().any()].tolist()

    if len(missing_cols) > 0:
      imputer = KNNImputer(n_neighbors=5)
      imputed_values = imputer.fit_transform(df[missing_cols])
      imputed_values = [[round(val, 3) for val in row] for row in imputed_values]

      df.loc[:, missing_cols] = imputed_values

    df.iloc[:, 1:].to_csv("output.txt", sep=',', index=False, header=False)

    with open('output.txt', 'r') as file:
      reader = csv.reader(file, delimiter=',')
      num_cols_txt = len(next(reader))

    data_file = "output.txt"
    data_x = np.loadtxt(data_file, delimiter=",", skiprows=0, usecols=range(1, num_cols_txt), dtype=np.float64)
    data_y = np.loadtxt(data_file, delimiter=",", skiprows=0, usecols=(num_cols_txt - 1,), dtype=np.int64)

    # train and test split
    train_x, test_x, train_y, test_y = train_test_split(data_x, data_y, test_size=0.2, random_state=42)
    print(train_x.shape, train_y.shape, test_x.shape, test_y.shape)  # check the shapes

    # main function

    train_x_norm = self.minmax_scaler(train_x)  # normalisation

    # initialising self-organising map
    num_dims = train_x_norm.shape[1]  # numnber of dimensions in the input data
    np.random.seed(40)
    som = np.random.random_sample(size=(self.num_rows, self.num_cols, num_dims))  # map construction

    # start training iterations
    for step in range(max_steps):
      if (step + 1) % 1000 == 0:
        print("Iteration: ", step + 1)  # print out the current iteration for every 1k
      learning_rate, neighbourhood_range = self.decay(step, max_steps, self.max_learning_rate, self.max_m_distance)

      t = np.random.randint(0, high=train_x_norm.shape[0])  # random index of traing data
      winner = self.winning_neuron(train_x_norm, t, som, self.num_rows, self.num_cols)
      for row in range(self.num_rows):
        for col in range(self.num_cols):
          if self.m_distance([row, col], winner) <= neighbourhood_range:
            som[row][col] += learning_rate * (train_x_norm[t] - som[row][col])  # update neighbour's weight

    print("SOM training completed")

    # collecting labels

    label_data = train_y
    map = np.empty(shape=(self.num_rows, self.num_cols), dtype=object)

    for row in range(self.num_rows):
      for col in range(self.num_cols):
        map[row][col] = []  # empty list to store the label

    for t in range(train_x_norm.shape[0]):
      if (t + 1) % 1000 == 0:
        print("sample data: ", t + 1)
      winner = self.winning_neuron(train_x_norm, t, som, self.num_rows, self.num_cols)
      map[winner[0]][winner[1]].append(label_data[t])  # label of winning neuron

    # construct label map
    label_map = np.zeros(shape=(self.num_rows, self.num_cols), dtype=np.int64)
    for row in range(self.num_rows):
      for col in range(self.num_cols):
        label_list = map[row][col]
        if len(label_list) == 0:
          label = 2
        else:
          label = max(label_list, key=label_list.count)
        label_map[row][col] = label

    title = ('Iteration ' + str(max_steps))
    cmap = colors.ListedColormap(['tab:green', 'tab:red', 'tab:orange'])
    plt.imshow(label_map, cmap=cmap, extent=[0, self.num_cols, self.num_rows, 0])
    plt.colorbar()
    plt.title(title)

    end_time = time.time()
    time_difference = end_time - start_time
    time_difference_rounded = round(time_difference)
    print("Tool was running: ", time_difference_rounded, "seconds")
    plt.show()

    # reshape SOM into 3D array
    som_3d = som.reshape(self.num_rows * self.num_cols, num_dims)

    # create 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(som_3d[:, 0], som_3d[:, 1], som_3d[:, 2], c=label_map.flatten(), cmap='viridis')
    ax.set_xlabel('Axis X')
    ax.set_ylabel('Axis Y')
    ax.set_zlabel('Axis Z')
    plt.show()

    # create 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(som_3d[:, 0], som_3d[:, 1], som_3d[:, 2], c=label_map.flatten(), cmap='viridis')

    # add lines between neighboring nodes
    for i in range(self.num_rows):
      for j in range(self.num_cols):
        if j < self.num_cols - 1:
          # add line between current node and its right neighbor
          ax.plot([som[i][j][0], som[i][j + 1][0]], [som[i][j][1], som[i][j + 1][1]], [som[i][j][2], som[i][j + 1][2]],
                  color='black', linewidth=0.5)
        if i < self.num_rows - 1:
          # add line between current node and its bottom neighbor
          ax.plot([som[i][j][0], som[i + 1][j][0]], [som[i][j][1], som[i + 1][j][1]], [som[i][j][2], som[i + 1][j][2]],
                  color='black', linewidth=0.5)

    plt.show()


  # Data Normalisation
  def minmax_scaler(self, data):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)
    return scaled

  # Euclidean distance
  def e_distance(self, x, y):
    return distance.euclidean(x, y)

  # Manhattan distance
  def m_distance(self, x, y):
    return distance.cityblock(x, y)

  # Best Matching Unit search
  def winning_neuron(self, data, t, som, num_rows, num_cols):
    winner = [0, 0]
    shortest_distance = np.sqrt(data.shape[1])  # initialise with max distance
    input_data = data[t]
    for row in range(num_rows):
      for col in range(num_cols):
        distance = self.e_distance(som[row][col], data[t])
        if distance < shortest_distance:
          shortest_distance = distance
          winner = [row, col]
    return winner

  # Learning rate and neighbourhood range calculation
  def decay(self, step, max_steps, max_learning_rate, max_m_distance):
    coefficient = 1.0 - (np.float64(step) / self.max_steps)
    learning_rate = coefficient * max_learning_rate
    neighbourhood_range = ceil(coefficient * max_m_distance)
    return learning_rate, neighbourhood_range
