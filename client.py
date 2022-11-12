from socket import *
import mydns as dns

HOST = "127.0.0.1"
PORT = 10069

def main():
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    while True:
        domain = input("Enter domain name: ")
        if domain == "end":
            break

        request = dns.message(domain, "A", "IN")
        clientSocket.sendto(request.encode().encode(), (HOST, PORT))
        data, addr = clientSocket.recvfrom(2048)
        response = dns.message()
        response.decode(data.decode())
        ips = response.answer.rdata.split(";")
        for ip in ips:
            print("{}: type {}, class {}, TTL {}, addr ({}) {}".format(
                response.question.qname,
                response.answer.type,
                response.answer.clas,
                response.answer.ttl,
                len(ip.encode()),
                ip,
            ))

    clientSocket.close()
    print("Session ended")

if __name__ == "__main__":
    main()