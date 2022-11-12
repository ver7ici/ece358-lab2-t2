from random import getrandbits

# =================================================
# resource record mappings

RRType = ["Reserved", "A"]
RRClass = ["Reserved", "IN"]

# =================================================
# helper methods for converting between data types

def int2bin(i, n):
    return bin(i)[2:].zfill(n) 

def bin2hex(b):
    h = ""
    i = 0
    while i < len(b):
        n = 0
        for j in range(4):
            n += int(b[i+j]) * 2**(3-j)
        h += hex(n)[2:]
        i += 4
    return h    

def hex2bin(h):
    b = ""
    for c in h:
        b += int2bin(int(c, 16), 4)
    return b

def str2bin(s):
    b = bin(int.from_bytes(s.encode(), 'big'))[2:]
    return b.zfill((len(b) // 8 + 1) * 8)

def bin2str(b):
    n = int(b, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()

# =================================================

class record:
    def __init__(self, si, dn, ip, ttl=160, typ="A", clas="IN"):
        self.si = si
        self.dn = dn
        self.type = typ
        self.clas = clas
        self.ttl = ttl
        self.ip = ip

class message:
    def __init__(self, qname="", qtype="", qclass=""):
        self.header = self._header()
        self.question = self._question(qname, qtype, qclass)
        self.answer = None

    def setAnswer(self, rdata, ttl, type, clas):
        self.header.qr = 1 # response flag
        self.header.ancount = len(rdata.split(";"))
        self.answer = self._answer( rdata, ttl, type, clas)

    def encode(self):
        s = self.header.encode() + self.question.encode()
        if self.answer:
            s += self.answer.encode()
        return s

    def decode(self, h):
        self.header.decode(h[:24])

        i = 24
        while i < len(h):
            i += 1
            if h[i-1] == "0" and h[i] == "0":
                break
        i += 9
        self.question.decode(h[24:i])
        
        if self.header.qr:
            self.answer = self._answer()
            self.answer.decode(h[i:])

        
    def disp(self):
        s = self.encode()
        for i in range(len(s)):
            end = ""
            if i % 2 == 1:
                end = " "
            if i > 0 and i % 32 == 31:
                end = "\n"
            print(s[i], end=end)
        print()


    class _header:
        def __init__(self):
            self.id = getrandbits(16)

            # flags
            self.qr = 0
            self.opcode = 0 # standard query for this lab
            self.aa = 1 # authoritative answer for this lab
            self.tc = 0 # no truncation for this lab
            self.rd = 0 # no recursion for this lab
            self.ra = 0 # no recursion for this lab
            self.z = 0 # reserved
            self.rcode = 0 # no error handling for this lab
            
            self.qdcount = 1 # 1 question for this lab
            self.ancount = 0
            self.nscount = 0 # no name server records for this lab
            self.arcount = 0 # no additional records for this lab
        
        def encode(self):
            b = int2bin(self.id, 16)
            b += "".join([
                str(self.qr),
                int2bin(self.opcode, 4),
                str(self.aa),
                str(self.tc),
                str(self.rd),
                str(self.ra),
                int2bin(self.z, 3),
                int2bin(self.rcode, 4),
            ])
            b += "".join([int2bin(i, 16) for i in (
                self.qdcount,
                self.ancount,
                self.nscount,
                self.arcount,
            )])
            return bin2hex(b)

        def decode(self, h):
            self.id = int(hex2bin(h[:4]), 2)

            tagsb = hex2bin(h[4:8])
            self.qr = int(tagsb[0], 2)
            self.opcode = int(tagsb[1:5], 2)
            self.aa = int(tagsb[5], 2)
            self.tc = int(tagsb[6], 2)
            self.rd = int(tagsb[7], 2)
            self.ra = int(tagsb[8], 2)
            self.z = int(tagsb[9:12], 2)
            self.rcode = int(tagsb[12:], 2)

            self.qdcount = int(hex2bin(h[8:12]), 2)
            self.ancount = int(hex2bin(h[12:16]), 2)
            self.nscount = int(hex2bin(h[16:20]), 2)
            self.arcount = int(hex2bin(h[20:24]), 2)


    class _question:
        def __init__(self, qname, qtype="A", qclass="IN"):
            self.qname = qname
            self.qtype = qtype
            self.qclass = qclass

        def encode(self):
            b = ""
            labels = self.qname.split(".")
            for label in labels:
                b += int2bin(len(label), 8)
                b += str2bin(label)
            b += "0" * 8 # terminate name with null label
            b += int2bin(RRType.index(self.qtype), 16)
            b += int2bin(RRClass.index(self.qclass), 16)
            return bin2hex(b)

        def decode(self, h):
            labels = []
            i = 0
            while i < len(h):
                if h[i] == "0" and h[i+1] == "0":
                    break
                length = int(hex2bin(h[i:i+2]), 2) * 2
                labels.append(bin2str(hex2bin(h[i+2:i+2+length])))
                i += 2 + length
            self.qname = ".".join(labels)
            i += 2
            self.qtype = RRType[int(hex2bin(h[i:i+4]), 2)]
            self.qclass = RRClass[int(hex2bin(h[i+4:i+8]), 2)]

    class _answer:
        def __init__(self, rdata="", ttl="", typ="", clas=""):
            self.name = "c00c" # owner name for this lab
            self.type = typ
            self.clas = clas
            self.ttl = ttl
            self.rdlength = len(rdata)
            self.rdata = rdata

        def encode(self):
            b = hex2bin(self.name)
            b += int2bin(RRType.index(self.type), 16)
            b += int2bin(RRClass.index(self.clas), 16)
            b += int2bin(self.ttl, 32)
            b += int2bin(self.rdlength, 16)
            b += str2bin(self.rdata)
            return bin2hex(b)

        def decode(self, h):
            self.name = h[:4] # name is known to be "c00c"
            self.type = RRType[int(hex2bin(h[4:8]), 2)]
            self.clas = RRClass[int(hex2bin(h[8:12]), 2)]
            self.ttl = int(hex2bin(h[12:20]), 2)
            self.rdlength = int(hex2bin(h[20:24]), 2)
            self.rdata = bin2str(hex2bin(h[24:]))
    
    # authoritative and additional sections omitted for this lab
    




