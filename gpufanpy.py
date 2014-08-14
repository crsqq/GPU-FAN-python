from __future__ import print_function
import os
import subprocess

class Gpufan:
    PATH = "/home/martin/ip_srv/"
    GPUFAN_BIN = "gpufan/centrality-gpu"


    def __init__(self, cmtype, elistFrom, nodes, elistTo=None, directed=False):
        """ Wrapper for gpufan-1.0

        :cmtype: b (betweenness), c (closeness), e (eccentric), s (stress)
        :nodes: number of vertices
        :elitFrom: either and edgelist or the first part (the from entries) of
        en edgelist, in the latter case you have to provide the second part
        through elistTo
        :directed: set to True if graph is directed
        """

        self.cmtype = cmtype
        self.directed = directed
        self.nodes = nodes
        if elistTo != None:
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
            cmdArgs = [Gpufan.GPUFAN_BIN, "-" + self.cmtype, '-g', self.TMPGRAPH, "-d",
                    "-o", self.TMPRESULT]
        else:
            cmdArgs = [Gpufan.GPUFAN_BIN, "-" + self.cmtype, '-g', self.TMPGRAPH, "-o",
                    self.TMPRESULT]
            proc = subprocess.Popen(cmdArgs,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                    )
            proc.wait()

        res = self.readResults()
        self.result = res
        #print proc.communicate()


    def readResults(self):
        res = [0.0] * self.nodes
        with open("tmpGpufan.output", 'r') as result:
            result.readline()
            for i in range(0, self.nodes):
                entry = result.readline().split()
                idx = int(entry[0])
                value = float(entry[1])
                res[idx] = value
#            print result.readline()
            print(result.readline())
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


if __name__ == '__main__':
    main()
