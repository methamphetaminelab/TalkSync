import os
import sys

def main(paths):
    clients = []

    for path in paths["clients"]:
        for client in os.listdir(path):
            clients.append(client)
            print(f"[{len(clients)}] - {client}")

    client = int(input("Select client: "))
    os.system(f"python {os.path.join(paths['clients'][0], clients[client - 1])}")

if __name__ == "__main__":
    paths = {
        "clients": [
            "client-cli/"],
    }

    main(paths)
