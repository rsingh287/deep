import queue
from jupyter_client.manager import start_new_kernel

class PersistentJupyterKernel:
    def __init__(self):
        print("Starting kernel...")
        self.km, self.kc = start_new_kernel(kernel_name='python3')
        print("Kernel started.")
    
    def execute(self, code, timeout=10):
        self.kc.execute(code)
        
        output = []
        while True:
            try:
                msg = self.kc.get_iopub_msg(timeout=timeout)
                msg_type = msg['header']['msg_type']
                content = msg['content']
                
                if msg_type == 'stream':
                    output.append(content['text'])
                elif msg_type == 'execute_result':
                    output.append(content['data'].get('text/plain', ''))
                elif msg_type == 'display_data':
                    if 'text/html' in content['data']:
                        output.append("[HTML Display Data]")
                    else:
                        output.append("[Display Data Received]")
                elif msg_type == 'error':
                    output.append("\n".join(content['traceback']))
                elif msg_type == 'status' and content['execution_state'] == 'idle':
                    break
            except queue.Empty:
                output.append("\n[Execution Timeout]")
                break
        
        return "".join(output)

if __name__ == "__main__":
    k = PersistentJupyterKernel()
    print("Executing 'x = 10'...")
    print(k.execute("x = 10\nprint('x is', x)"))
    print("Executing 'print(x * 2)'...")
    print(k.execute("print(x * 2)"))
