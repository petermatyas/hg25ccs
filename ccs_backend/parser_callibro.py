import re



class CabrilloParserException(Exception):
    """CabrilloParserException is the catch-all exception for this library."""


class InvalidLogException(CabrilloParserException):
    """InvalidLogException occurs if there is an error reading the log
    file.
    """


class InvalidQSOException(CabrilloParserException):
    """InvalidLogException occurs if there is an error parsing an individual
    QSO.
    """

class QSO():
    frequency = 0




class Callibro():
    def __init__(self, filePath):
        self.filePath = filePath
        self.__content = None
        self.header = dict()    
        self.logs = list()


    def __readFile(self):
        with open(self.filePath, "r", encoding="ISO-8859-1") as file:
            self.__content = file.read()

    def parse(self):
        self.__readFile()

        self.__content = self.__content.rstrip()        # remove end white spaces

        contentLines = self.__content.split("\n")

        if contentLines[0] != "START-OF-LOG: 3.0":
            raise InvalidLogException("error start of file")

        if contentLines[-1] != "END-OF-LOG:":
            raise InvalidLogException("error end of log")

        self.parseHeader()
        self.parseQSO()

    def parseHeader(self):
        headerKeywords = ["NAME", "GRID-LOCATOR"]
        for i in headerKeywords:
            try:
                res = re.findall(f"{i}: (.+)", self.__content)[0]
            except:
                res = None

            self.header[i] = res

    def parseQSO(self):    
        qsos = re.findall("QSO:.+|X-QSO:.+", self.__content)

        qso = QSO()
        for line in qsos:
            qso.frequency = int(line[4:11].strip())
            qso.mode = line[11:14].strip()
            self.logs.append(qso)



path = "/home/ha1mp/Downloads/HG225CCS 18m_ya_1786808476.log"
cab = Callibro(path)
cab.parse()
print(cab.header)
print(cab.logs)
        










