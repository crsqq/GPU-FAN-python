from __future__ import print_function
import os
import subprocess

class Gpufan:
    PATH = "/opt/gpufanshared/"
    GPUFAN_BIN = "/opt/gpufanshared/bin/centrality-gpu"


    def __init__(self, cmtype, elistFrom, nodes, elistTo=None, directed=False):
        """ Wrapper for gpufan-1.0

        :cmtype: b (betweenness), c (closeness), e (eccentric), s (stress)
        :nodes: number of vertices
        :elistFrom: either and edgelist or the first part (the from entries) of
        en edgelist, in the latter case you have to provide the second part
        through elistTo
        :directed: set to True if graph is directed
        """

        self.cmtype = cmtype
        self.directed = directed
        self.nodes = nodes
        if elistTo:
            self.edgelist = zip(elistFrom, elistTo)
        else:
            self.edgelist = elistFrom

        self.TMPGRAPH = Gpufan.PATH + "tmpGpufan.edgelist"
        self.TMPRESULT = Gpufan.PATH + "tmpGpufan.output"



    def writeEdgelist(self):
        with open(self.TMPGRAPH, 'w') as outfile:
            for item in self.edgelist:
                string = "%i\t%i\n" % item
                outfile.write(string)


    def runGPU(self):
        if self.directed:
            cmd = [Gpufan.GPUFAN_BIN, "-" + self.cmtype, '-g', self.TMPGRAPH, "-d", "-o", self.TMPRESULT]
        else:
            cmd = [Gpufan.GPUFAN_BIN, "-" + self.cmtype, '-g', self.TMPGRAPH, "-o", self.TMPRESULT]

        exitCode = subprocess.call(cmd)
        print(exitCode)

        self.result = self.readResults()


    def readResults(self):
        res = [0.0] * self.nodes
        with open(self.TMPRESULT, 'r') as result:
            result.readline()
            while(True):
                entry = result.readline().split()
                if entry[0].lower() == "time:":
                    break
                idx = int(entry[0])
                value = float(entry[1])
                res[idx] = value
            print(" ".join(entry))
        return res


    def cleanUp(self):
        os.remove(self.TMPGRAPH)
        os.remove(self.TMPRESULT)

    def runAll(self):
        self.writeEdgelist()
        self.runGPU()
        self.cleanUp()

        return self.result



def main():
    eL = [4,2,4,4,5]
    eR = [5,8,8,9,9]
    fan = Gpufan("c", elistFrom=eL, elistTo=eR, nodes=10)
    print( fan.runAll())


if __name__ == '__main__':
    main()
