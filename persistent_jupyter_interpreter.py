import queue
import atexit
from jupyter_client.manager import start_new_kernel

class PersistentJupyterKernel:
    def __init__(self):
        self.km, self.kc = start_new_kernel(kernel_name='python3')
        atexit.register(self.shutdown)
    
    def shutdown(self):
        if self.km and self.kc:
            self.kc.stop_channels()
            self.km.shutdown_kernel(now=True)

    def execute(self, code, timeout=30):
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
                    # Get plain text or markdown
                    text_data = content['data'].get('text/plain', '')
                    if text_data:
                        output.append(text_data)
                elif msg_type == 'display_data':
                    # If matplotlib or df plots, we might get image/png or text/html
                    if 'image/png' in content['data']:
                        output.append("\n[Image/Chart Generated - Displayed in Notebook]\n")
                    elif 'text/html' in content['data']:
                        output.append("\n[HTML Data Generated]\n")
                    else:
                        output.append("\n[Display Data Received]\n")
                elif msg_type == 'error':
                    output.append("\n".join(content['traceback']))
                elif msg_type == 'status' and content['execution_state'] == 'idle':
                    break
            except queue.Empty:
                output.append("\n[Execution Timeout: Code took too long to run]")
                break
        
        return "".join(output)

# Global singleton
_global_kernel = None

def get_global_kernel():
    global _global_kernel
    if _global_kernel is None:
        _global_kernel = PersistentJupyterKernel()
    return _global_kernel
