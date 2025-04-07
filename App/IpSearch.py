import cv2
import socket
import time

def is_rtsp_port_open(ip, port=554, timeout=1):
    """
    Vérifie si le port RTSP (554) est ouvert sur l'IP donnée.
    Retourne True si le port est ouvert, sinon False.
    """
import socket

def is_rtsp_port_open(ip, port=554, timeout=1):
    """
    Vérifie si le port RTSP (554) est ouvert sur l'IP donnée.
    Retourne True si le port est ouvert, sinon False.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def find_valid_rtsp_ip(timeout=3):

    tab_ip = ["169.254.77.146", "169.254.27.214", "169.254.61.84", "169.254.56.5"]
    for ip in tab_ip:
        print(f"Test du port RTSP sur {ip}")
        
        if not is_rtsp_port_open(ip):
            print(f"Port RTSP fermé sur {ip}, on passe à l'IP suivante")
            continue
        
        rtsp_url = f"rtsp://admin:vision29@{ip}/Streaming/channels/201"

        cap = cv2.VideoCapture(rtsp_url)
        start_time = time.time()

        while time.time() - start_time < timeout:
            ret, _ = cap.read()
            if ret:
                print(f"Connexion réussie avec {ip} !")
                cap.release()
                return ip  

        cap.release()

    print("Aucune IP valide trouvée.")
    return None  
