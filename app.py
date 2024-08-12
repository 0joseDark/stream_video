import tkinter as tk
from threading import Thread
from flask import Flask, Response
import cv2
import subprocess
import os

class StreamingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Streaming")
        
        # Estado dos botões
        self.camera_on = False
        self.server_on = False
        
        # Botões da Interface
        self.camera_button = tk.Button(root, text="Ligar Câmera", command=self.toggle_camera)
        self.camera_button.pack(pady=10)
        
        self.server_button = tk.Button(root, text="Iniciar Servidor", command=self.toggle_server)
        self.server_button.pack(pady=10)
        
        self.exit_button = tk.Button(root, text="Sair", command=self.exit_app)
        self.exit_button.pack(pady=10)
    
    def toggle_camera(self):
        if not self.camera_on:
            self.camera_on = True
            self.camera_button.config(text="Desligar Câmera")
            self.start_camera()
        else:
            self.camera_on = False
            self.camera_button.config(text="Ligar Câmera")
            self.stop_camera()
    
    def start_camera(self):
        self.camera = cv2.VideoCapture(0)
        self.show_camera()
    
    def show_camera(self):
        if self.camera_on:
            ret, frame = self.camera.read()
            if ret:
                cv2.imshow("Câmera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.toggle_camera()
            self.root.after(10, self.show_camera)
    
    def stop_camera(self):
        if self.camera_on:
            self.camera.release()
            cv2.destroyAllWindows()
            self.camera_on = False
    
    def toggle_server(self):
        if not self.server_on:
            self.server_on = True
            self.server_button.config(text="Desligar Servidor")
            self.start_server()
        else:
            self.server_on = False
            self.server_button.config(text="Iniciar Servidor")
            self.stop_server()
    
    def start_server(self):
        self.server_thread = Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def run_server(self):
        app = Flask(__name__)

        def generate_frames():
            camera = cv2.VideoCapture(0)
            while True:
                success, frame = camera.read()
                if not success:
                    break
                else:
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        @app.route('/video_feed')
        def video_feed():
            return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
        app.run(host='0.0.0.0', port=5000, debug=False)
    
    def stop_server(self):
        if self.server_on:
            # Para o servidor Flask de maneira segura
            subprocess.run(["pkill", "-f", "flask"])
    
    def exit_app(self):
        self.stop_camera()
        self.stop_server()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = StreamingApp(root)
    root.mainloop()
