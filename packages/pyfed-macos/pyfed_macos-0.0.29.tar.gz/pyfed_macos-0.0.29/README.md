# PyFed
PyFed is an open-source framework for federated learning. PyFed is fairly straightforward and brief in comparison to other federated learning frameworks. Furthermore, it allows running federated learning algorithms with any Tensorflow dataset on any preprocessed dataset. PyFed introduces several methods of federated learning implementation such as running multiple processes on a single machine and training on various systems. In addition, PyFed employs Tensorboard to demonstrate the history of training of each client and assess loss and accuracy of each client per round.
</br>
PyFed implements FL using sockets, processes, and threads. Simply put, each client will run its particular process and tries to establish a socket connection with the server, which also has its specific process. 
Once initiated, each connection will be handled by one thread of the server's process. Each thread will communicate with its respective client to receive the trained weights per round. 
Once they receive the result of one round, threads will return the weights to the server's process, which will arrive at a new model using the mentioned weights. The server will send the new model to the clients using newly initiated threads.
</br>
PyFed is mainly based on two classes:
 
- __FL_Server__: which represents the server to which clients communicate in a federated learning problem. The __train()__ function of this class handles socket connections and the FL policy. </br>
- __FL_Client__: which represents each client in a federated learning network. An object of this class handles training procedure of any global model on any local data.

PyFed can run federated learning in 2 ways: 

1. Running FL only on one system and using separate processes.
2. Running FL on multiple systems. 

</br>
More details are mentioned in the Usage section.
</br>
Currently, PyFed is limited to FedAvg as its only federated learning policy; however, a broader range of configurations for FL experiments will be introduced in the future versions.

# Features
PyFed contains two critical classes: FL_Server and FL_Client, which are responsible for server and client actions in a federated learning problem, respectively. </br>
* __FL_Server.train()__ establishes a socket connections with clients and handles weight averaging. In addition, at the end of all rounds a tensorboard session will be started to reveal the efficancy of each client.
* __FL_Server.test()__ will test the final model on the given test data.
* __FL_Client.train()__ will initiate a training session for the client who runs the command. Each client will train the received model on its local dataset.

# Installation
## MacOS
    pip install pyfed-macos==0.0.28
## Windows, Linux
    pip install pyfed==0.0.28

# Usage
Utilizing PyFed is effortless and time efficient. Following are three approaches of running federated learning algorithms which can be implemented with PyFed. All of the examples below tackle the problem of classification on MNIST dataset.

## First Approach: Using FL_Experiment
__FL_Experiment__ can be used to test federated learning for an specific model and dataset as fast as possible. This model takes some configuration as its input, runs federated learning with just a few lines of code, and reports the results of each client along with the accuracy of the model on the test data. This class is for those who simply want to experiment with FL, just as the name suggests.
</br>
In the following code, we download the MNIST data, distribute it evenly between the server and the clients, and give it to the model to run it with multiple clients.

    from pyfed.experiment import FL_Experiment
    import tensorflow as tf
    from sklearn.datasets import fetch_openml
    import numpy as np
    import copy

    def fetch_mnist():
        mnist = fetch_openml("mnist_784", version=1)
        X, y = np.array(mnist["data"]), np.array(mnist["target"], dtype='int16')
        return X, y

    def distribute_data(X, y, num_clients):
        data_count = len(y) // (num_clients + 1)

        clients_data = []
        clients_target = []
        for i in range(num_clients):
            client_i_X = copy.deepcopy(X[data_count*i:data_count *(i + 1)])
            client_i_y = copy.deepcopy(y[data_count*i:data_count*(i + 1)])

            clients_data.append(client_i_X)
            clients_target.append(client_i_y)

        server_data, server_target = X[data_count *
                                    num_clients:], y[data_count*num_clients:]

        return clients_data, clients_target, server_data, server_target

    if __name__ == "__main__":
        lr = 3e-4
        num_clients = 3
        rounds = 2
        epochs = 5
        batch_size = 32
        port = 54321

        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.InputLayer((784,)))
        model.add(tf.keras.layers.Dense(500, activation='relu'))
        model.add(tf.keras.layers.Dense(1000, activation='relu'))
        model.add(tf.keras.layers.Dense(2000, activation='relu'))
        model.add(tf.keras.layers.Dense(1000, activation='relu'))
        model.add(tf.keras.layers.Dense(500, activation='relu'))
        model.add(tf.keras.layers.Dense(10, activation='softmax'))

        loss = "sparse_categorical_crossentropy"
        optimizer = tf.optimizers.Adam
        metrics = ["accuracy"]

        model.compile(loss=loss,
                    optimizer=optimizer(lr),
                    metrics=metrics)

        print("\n⏳ Downloading dataset...\n")
        data, target = fetch_mnist()
        print("\n📨 Distributing dataset...\n")
        clients_data, clients_target, server_data, server_target = distribute_data(data, target, num_clients)

        exp = FL_Experiment(num_clients=num_clients,
                            clients_data=clients_data,
                            clients_target=clients_target,
                            server_data=server_data,
                            server_target=server_target)

        exp.run(model=model,
                rounds = rounds,
                epochs=epochs,
                batch_size=batch_size,
                lr=lr,
                optimizer=optimizer,
                loss=loss,
                metrics=metrics)

## Second Approach: Multiple Processes on a Single System
In this method, we create separate files in one system and run each of them simultaneasly to achieve federated learning. In this way, we have more control over each client and its local dataset, as opposed to using FL_Experiment. 

### data.py
This is for distributing data among clients and a server.

    import numpy as np
    from sklearn.datasets import fetch_openml

    num_clients = 3
    mnist = fetch_openml("mnist_784", version=1)
    X, y = np.array(mnist["data"]), np.array(mnist["target"], dtype='int16')
    data_count = len(y) // (num_clients + 1)

    for i in range(num_clients):
        client_i_X, client_i_y = X[data_count*i:data_count*(i + 1)], y[data_count*i:data_count*(i + 1)]
        np.save(f"./data_client_{i+1}.npy", client_i_X)
        np.save(f"./target_client_{i+1}.npy", client_i_y)

    server_i_X, server_i_y = X[data_count*num_clients:], y[data_count*num_clients:]
    np.save(f"./data_server.npy", server_i_X)
    np.save(f"./target_server.npy", server_i_y)


### server.py
    from pyfed.components import FL_Server
    import numpy as np
    import tensorflow as tf


    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.InputLayer((784,)))
    model.add(tf.keras.layers.Dense(500, activation='relu'))
    model.add(tf.keras.layers.Dense(1000, activation='relu'))
    model.add(tf.keras.layers.Dense(2000, activation='relu'))
    model.add(tf.keras.layers.Dense(1000, activation='relu'))
    model.add(tf.keras.layers.Dense(500, activation='relu'))
    model.add(tf.keras.layers.Dense(10, activation='softmax'))


    loss = "sparse_categorical_crossentropy"
    optimizer = tf.optimizers.Adam
    metrics = ["accuracy"]

    lr = 3e-4
    num_clients = 3
    rounds = 2

    model.compile(loss=loss,
                optimizer=optimizer(lr),
                metrics=metrics)

    data = np.load("./data_server.npy")
    target = np.load("./target_server.npy")


    server = FL_Server(curr_model=model,
                    num_clients=num_clients,
                    rounds=rounds)

    server.train()
    server.test(data, target, loss, optimizer, lr, metrics)

### client_1.py
    from pyfed.components import FL_Client
    import numpy as np
    import tensorflow as tf

    epochs = 5
    batch_size = 32
    lr = 3e-4

    loss = "sparse_categorical_crossentropy"
    optimizer = tf.optimizers.Adam
    metrics = ["accuracy"]

    data = np.load("./data_client_1.npy")
    target = np.load("./target_client_1.npy")

    client1 = FL_Client(name="client_1",
                        data=data,
                        target=target)

    client1.train(epochs, batch_size, lr, loss, optimizer, metrics)

Create __client_2.py__ and __client_3.py__ files just like the file above and change the data and target files to match the correct client. </br>

Now, run the server and clients files separately and simultaneously to get federated learning!

## Third Approach: Implementing FL Using Multiple Systems
PyFed is able to run FL algorithms across distinct systems. To do this, connect all systems to the same wifi network. Then, find the local ip of the computer which you would like to use as the server. And at last, create the following files accordingly to run federated learning across distinct machines.

### server.py
    from pyfed.components import FL_Server
    import numpy as np
    import tensorflow as tf


    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.InputLayer((784,)))
    model.add(tf.keras.layers.Dense(500, activation='relu'))
    model.add(tf.keras.layers.Dense(1000, activation='relu'))
    model.add(tf.keras.layers.Dense(2000, activation='relu'))
    model.add(tf.keras.layers.Dense(1000, activation='relu'))
    model.add(tf.keras.layers.Dense(500, activation='relu'))
    model.add(tf.keras.layers.Dense(10, activation='softmax'))


    loss = "sparse_categorical_crossentropy"
    optimizer = tf.optimizers.Adam
    metrics = ["accuracy"]

    lr = 3e-4
    num_clients = 3
    rounds = 2

    # The port which you would like to dedicate to the server.
    port = 54321

    model.compile(loss=loss,
                optimizer=optimizer(lr),
                metrics=metrics)

    data = np.load("./data_server.npy")
    target = np.load("./target_server.npy")

    server = FL_Server(curr_model=model,
                    num_clients=num_clients,
                    rounds=rounds,
                    port=port,
                    multi_system=True)

    server.train()
    server.test(data, target, loss, optimizer, lr, metrics)

### client_1.py
    from pyfed.components import FL_Client
    import numpy as np
    import tensorflow as tf

    epochs = 5
    batch_size = 32
    lr = 3e-4

    loss = "sparse_categorical_crossentropy"
    optimizer = tf.optimizers.Adam
    metrics = ["accuracy"]

    data = np.load("./data_client_1.npy")
    target = np.load("./target_client_1.npy")

    # The IP of the computer which runs server.py.
    server_ip = "192.168.1.153"
    # The port you selected in server.py.
    server_port = 54321

    client1 = FL_Client(name="client_1",
                        data=data,
                        target=target,
                        server_ip=server_ip,
                        server_port=server_port)

    client1.train(epochs, batch_size, lr, loss, optimizer, metrics)

__client_2.py__ and __client_3.py__ are just like __client_1.py__ but with different data and on different systems. Run each file at the same time to get federated learning on various systems!
# Files
Exact files of these examples can be found on the [GitHub repository](https://github.com/amirrezasokhankhosh/PyFed) of this package.