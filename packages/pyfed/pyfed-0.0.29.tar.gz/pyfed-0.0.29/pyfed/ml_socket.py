from pyfed.global_var import *

def parse_data(data):
        if isinstance(data, bytes):
            return data
        buffer = BytesIO()
        if isinstance(data, np.ndarray):
            np.save(buffer, data, allow_pickle=True)
        elif 'keras' in str(type(data)):
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            with h5py.File(buffer, 'w') as f:
                save_model(data, f, include_optimizer=False)
        elif 'sklearn' in str(type(data)):
            dump(data, buffer)
        buffer.seek(0)
        return buffer.read()


def load_data(file: BytesIO):
        data = file.read()[:-3]
        file.seek(0)
        if b'NUMPY' in data:
            return np.load(file)
        elif b'sklearn' in data:
            return load(file)
        elif b'HDF' in data:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            with h5py.File(file, 'r') as f:
                model = load_model(f, compile=False)
            return model
        else:
            return data
        

def ml_send(c, data):
        data = parse_data(data)
        result = c.send(data)
        c.send(b'End')
        c.recv(SIZE)
        return result


def ml_recv(c, bufsize):
        buffer = BytesIO()
        while True:
            data = c.recv(bufsize)
            if not data:
                break
            buffer.write(data)
            buffer.seek(-4, 2)
            if b'End' in buffer.read():
                c.send(b'Complete')
                break
        buffer.seek(0)
        return load_data(buffer)