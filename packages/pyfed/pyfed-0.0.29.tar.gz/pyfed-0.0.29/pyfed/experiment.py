from pyfed.ml_socket import *

class Server:
    def __init__(self, s, curr_model, num_clients, rounds):
        self.s = s
        self.curr_model = curr_model
        self.num_clients = num_clients
        self.rounds = rounds
        self.results = []
        self.connections = []

    def __handle_client(self, c, send_rounds=False):
        if send_rounds:
            c.send(str(self.rounds).encode(FORMAT))
        ml_send(c, self.curr_model)
        num = ml_recv(c, SIZE)
        return num

    def __accept_conn(self):
        c, addr = self.s.accept()
        self.connections.append(c)

        res = self.th_executor.submit(self.__handle_client, c, True)
        self.results.append(res)

    def __fl_policy(self, new_weights):
        avg_weights = []
        for layer in range(len(new_weights[0])):
            sum_layer = np.zeros_like(new_weights[0][layer])
            for new_weight in new_weights:
                sum_layer += new_weight[layer]
            avg_weights.append(sum_layer/self.num_clients)
        self.curr_model.set_weights(avg_weights)

    def __fl_loop(self):
        for i in range(self.rounds):
            print(f'\n📣 RUNNING ROUND {i+1}.\n')

            new_weights = []
            for f in concurrent.futures.as_completed(self.results):
                model = f.result()
                new_weights.append(model.get_weights())
            
            self.__fl_policy(new_weights)

            self.results = []

            if i != self.rounds - 1:
                for c in self.connections:
                    res = self.th_executor.submit(self.__handle_client, c)
                    self.results.append(res)
            
            print(f'\n✅ ROUND {i+1} COMPLETED.\n')

    def __close_connections(self):
        for c in self.connections:
            c.close()

    def train_server(self):
        if os.name == "nt":
            os.system("if exist pyfed_logs rmdir /s /q pyfed_logs")
        else:
            os.system(f'rm -rf ./pyfed_logs/')
        
        self.th_executor = concurrent.futures.ThreadPoolExecutor(
            self.num_clients)

        for _ in range(self.num_clients):
            self.__accept_conn()

            if len(self.connections) == self.num_clients:
                self.__fl_loop()
                self.__close_connections()

        self.s.close()
        return self.curr_model


class Client:

    def __init__(self, name, data, target, server_ip=LOCAL_IP, server_port=PORT):
        self.name = name
        self.data = data
        self.target = target
        self.server_ip = server_ip
        self.server_port = server_port
        self.s = socket.socket()

    def train_client(self, epochs, batch_size, lr, loss, optimizer, metrics):
        self.s.connect((self.server_ip, self.server_port))

        rounds = int(self.s.recv(SIZE).decode(FORMAT))
        for i in range(rounds):
            log_dir = f"{PATH}/{self.name}/round_{i+1}/" + \
                datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            tensorboard_callback = tf.keras.callbacks.TensorBoard(
                log_dir=log_dir, update_freq="epoch")
            model = ml_recv(self.s, SIZE)
            model.compile(loss=loss,
                          optimizer=optimizer(lr),
                          metrics=metrics,)
            model.fit(self.data,
                      self.target,
                      batch_size=batch_size,
                      epochs=epochs,
                      callbacks=[tensorboard_callback],
                      verbose=0)
            ml_send(self.s, model)

        self.s.close()


class FL_Experiment:
    def __init__(self, num_clients, clients_data, clients_target, server_data, server_target, port=PORT):
        """
        Creates a federated learning experiment according to the essential factors it receives as inputs.\n
        An object of this class can create a federating learning network, train a model on distinct datasets, 
        evaluate the model on a test dataset, and present the training history using Tensorboard.
        """

        self.port = port
        self.num_clients = num_clients
        self.clients_data = clients_data
        self.clients_target = clients_target
        self.server_data = server_data
        self.server_target = server_target
        self.s = socket.socket()
        self.pr_executor = concurrent.futures.ProcessPoolExecutor(num_clients + 1)

    def __initiate_socket(self):
        self.s.bind(('', self.port))
        self.s.listen(self.num_clients)
    
    def run(self, model, rounds, epochs, batch_size, lr, optimizer, loss, metrics):
        """
        Initiates the federated learning experiment.
        """
        self.__initiate_socket()

        print("\n🏛️ Running Server...\n")
        server = Server(s=self.s,
                        curr_model=model,
                        num_clients=self.num_clients, 
                        rounds=rounds)
        server_res = self.pr_executor.submit(server.train_server)
        results = []
        results.append(server_res)

        print("\n💻 Running Clients...\n")
        for i in range(self.num_clients):
            client = Client(name=f"client_{i+1}",
                        data=self.clients_data[i],
                        target=self.clients_target[i],
                        server_port=self.port)
            self.pr_executor.submit(client.train_client, epochs, batch_size, lr, loss, optimizer, metrics)
        
        for f in concurrent.futures.as_completed(results):
            trained_model = f.result()
            trained_model.compile(loss=loss,
                            optimizer=optimizer(lr),
                            metrics=metrics)
            print("\n🔍 Testing...\n")
            trained_model.evaluate(self.server_data, self.server_target)
            os.system(f'tensorboard --logdir={PATH}')