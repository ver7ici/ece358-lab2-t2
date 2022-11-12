from socket import *
import mydns as dns

HOST = "127.0.0.1"
PORT = 10069

table = [
    dns.record(1,    "google.com",  "192.165.1.1;192.165.1.10",  260),
    dns.record(2,   "youtube.com",  "192.165.1.2"),
    dns.record(3,  "uwaterloo.ca",  "192.165.1.3"),
    dns.record(4, "wikipedia.org",  "192.165.1.4"),
    dns.record(5,     "amazon.ca",  "192.165.1.5")
]

def main():
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((HOST, PORT))
    print("The server is ready to receive")

    while True:
        data, addr = serverSocket.recvfrom(2048)
        query = dns.message()
        query.decode(data.decode())
        print("Request:")
        query.disp()

        rr = [r for r in table if r.dn == query.question.qname][0]
        response = query
        response.setAnswer(rr.ip, rr.ttl, rr.type, rr.clas)
        print("Response:")
        response.disp()

        serverSocket.sendto(response.encode().encode(), addr)

if __name__ == "__main__":
    main()