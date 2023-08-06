from pyfed.ml_socket import *


class FL_Server():
    def __init__(self, curr_model, num_clients, rounds, port=PORT, multi_system=False):
        """
        Creates a federated learning server that connects to various federated learning clients 
        in the same system or across multiple systems.
        As expected, it is also responsible for the implemented federated learning policy, 
        updating the recieved weights.
        """

        self.s = socket.socket()
        self.executor = concurrent.futures.ThreadPoolExecutor(num_clients)
        self.curr_model = curr_model
        self.num_clients = num_clients
        self.rounds = rounds
        self.port = port
        self.multi_system = multi_system
        self.results = []
        self.connections = []

    def __handle_client(self, c, model, send_rounds=False):
        """
        This function will be handed to each thread that handles each client. Before sending the model, it sends 
        the number of rounds the network is going to run.
        """

        if send_rounds:
            c.send(str(self.rounds).encode(FORMAT))
        ml_send(c, model)
        new_w = ml_recv(c, SIZE)
        return new_w

    def __initiate_socket(self):
        """
        Simply put, this prepares the socket for listening to a predefined number of clients.
        """

        self.s.bind(('', self.port))
        print("\n[BINDED] socket binded to %s.\n" % (self.port))

        self.s.listen(self.num_clients)
        print("\n[LISTENING] socket is listening.\n")

    def __accept_connection(self):
        """
        After receiving a connection from a client, the server creates a thread and lets it handle the communication.
        """

        c, addr = self.s.accept()
        self.connections.append(c)
        print("")
        print('[NEW CONNECTION] Got connection from', addr)
        res = self.executor.submit(
            self.__handle_client, c, copy.deepcopy(self.curr_model), True)
        self.results.append(res)

    def fl_policy(self, new_weights):
        """
        The federating learning policy responsible for updating trained weights is programmed in this function.
        In default, the policy is set to FedAvg; however, this policy can be altered to whichever algorithm you see fit. 
        To do that, you must be aware of its input and output.\n
        The input of this function is a list of trained weights received by the clients. Each item in this list is also a list 
        of weights of each layer. To illustrate, consider the following example:\n\n
        Model = {layer1, layer2, layer3}\n
        num_clients = 2\n
        new_weights = [[trained_layer1_c1, trained_layer2_c1, trained_layer3_c1],\n
                       [trained_layer1_c2, trained_layer2_c2, trained_layer3_c2]]\n\n

        After reaching to the new weights of your liking, simply add the following code:\n\n

        self.curr_model.set_weights(avg_weights)\n\n

        Remember, avg_weights is the variable consisting of your new weights for each layer, and it looks like 
        this:\n
        avg_weights = [avg_layer1, avg_layer2, avg_layer3]
        """

        avg_weights = []
        for layer in range(len(new_weights[0])):
            sum_layer = np.zeros_like(new_weights[0][layer])
            for new_weight in new_weights:
                sum_layer += new_weight[layer]
            avg_weights.append(sum_layer/self.num_clients)
        self.curr_model.set_weights(avg_weights)

    def __fl_loop(self):
        """
        As the name suggests, this function handles the federated learning loop. In each round, 
        it receives the trained weights, reaches a new model using the defined fl policy, and sends the new model 
        to the clients in the network using multiple threads. 
        """

        for i in range(self.rounds):
            new_weights = []
            for f in concurrent.futures.as_completed(self.results):
                model = f.result()
                new_weights.append(model.get_weights())

            self.fl_policy(new_weights)

            new_weights = []
            self.results = []

            if i != self.rounds - 1:
                for c in self.connections:
                    res = self.executor.submit(
                        self.__handle_client, c, copy.deepcopy(self.curr_model))
                    self.results.append(res)

            print(f'\n✅ ROUND {i+1} COMPLETED.\n')

    def __close_connections(self):
        """
        Simply closes all socket connections.
        """

        for c in self.connections:
            c.close()
        print("[CONNECTIONS CLOSED]")
        print("")

    def train(self):
        """
        As expected, this function trains a model in a federated learning network.\n
        """
        if not self.multi_system:
            if os.name == "nt":
                os.system("if exist pyfed_logs rmdir /s /q pyfed_logs")
            else:
                os.system(f'rm -rf ./pyfed_logs/')
        
        self.__initiate_socket()
        for _ in range(self.num_clients):
            self.__accept_connection()
            if len(self.connections) == self.num_clients:
                self.__fl_loop()
                self.__close_connections()
        self.s.close()

        if not self.multi_system:
            os.system(f'tensorboard --logdir={PATH}')

    def test(self, data, target, loss, optimizer, lr, metrics):
        """
        Simply tests a model on the given test data.\n
        """
        print("\n\n🔍 Testing...\n\n")
        self.curr_model.compile(loss=loss,
                                optimizer=optimizer(lr),
                                metrics=metrics)
        self.curr_model.evaluate(data, target)


class FL_Client():
    def __init__(self, name, data, target, server_ip=LOCAL_IP, server_port=PORT):
        """
        Creates a federated learning client that establishes a socket connection to a federated learning server.\n
        Thus, it can be used to train a Tensorflow model on its local dataset. Furthermore, it stores the history of 
        each round of training and display the overall training process using Tensorboard.
        """

        self.name = name
        self.data = data
        self.target = target
        self.server_ip = server_ip
        self.server_port = server_port
        self.s = socket.socket()

    def train(self, epochs, batch_size, lr, loss, optimizer, metrics):
        """
        Trains any recieved model on its predefined local dataset.
        """

        self.s.connect((self.server_ip, self.server_port))
        print(f"\n[NEW CONNECTION] to {self.server_ip}:{self.server_port}\n")

        if self.server_ip != LOCAL_IP:
            if os.name == "nt":
                os.system("if exist pyfed_logs rmdir /s /q pyfed_logs")
            else:
                os.system(f'rm -rf ./pyfed_logs/')

        rounds = int(self.s.recv(SIZE).decode(FORMAT))
        for i in range(rounds):
            log_dir = f"{PATH}/{self.name}/round_{i+1}/" + \
                datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            tensorboard_callback = tf.keras.callbacks.TensorBoard(
                log_dir=log_dir, update_freq="epoch")
            model = ml_recv(self.s, SIZE)
            model.compile(loss=loss,
                          optimizer=optimizer(lr),
                          metrics=metrics)
            model.fit(self.data,
                      self.target,
                      batch_size=batch_size,
                      epochs=epochs,
                      callbacks=[tensorboard_callback])
            ml_send(self.s, model)
            print(f'\n🛎️ ROUND {i+1} COMPLETED.\n')
        
        if self.server_port != LOCAL_IP:
            os.system(f'tensorboard --logdir={PATH}')

        self.s.close()
