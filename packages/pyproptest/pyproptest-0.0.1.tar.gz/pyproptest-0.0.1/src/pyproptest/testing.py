import inspect
import sys
import re

class tester:
    """
    class for creating testing objects to test modules.
    """
    def __init__(self, modules:list[str] = [], classes = [], n:str = "prop_", 
                 iters:int = 100, dumpfile:str = None) -> None:
        """
        constructor method.
        """
        if modules:
            self.loadFromModules(modules)
        elif classes:
            self.loadFromClasses(classes)
        self.setPattern(n)
        self.setIterations(iters)
        self.dumpFile = dumpfile

    @property
    def __funcs(self) -> None:
        """
        property representing list of test functions and generators used
        to generate arbitrary values for their parameters.
        """
        if self.__modules:
            return self.funcsFromModules()
        elif self.__classes:
            return self.funcsFromClasses()
        else:
            return []
        
    def funcsFromClasses(self) -> list:
        """
        identifies functions in specified classes.
        """
        testCases = dict()
        for testClass in self.__classes:
            method_list = filter (lambda x: self.__namePattern.match(x[0]), 
                                  inspect.getmembers(testClass))
            ts = filter(lambda x: self.__namePattern.match(x[0]), method_list)
            testCases[testClass.__name__] = tester.__validateFuncs(list(map(
                lambda x:(x[1](),x[0]), ts)))
        return testCases
        
    def funcsFromModules(self) -> list:
        """
        identifies functions in specified modules.
        """
        testCases = dict()
        for module in self.__modules:
            funcs = [(f, f.__name__) for _, f in inspect.getmembers(module)
                     if inspect.isfunction(f)]
            ts = filter(lambda x: self.__namePattern.match(x[1]), funcs)
            testCases[module.__name__] = tester.__validateFuncs(list(map(
                lambda x:(x[0](),x[1]), ts)))
        return testCases
    
    def setPattern(self, nameStruct: str) -> None:
        """
        sets the pattern used to identify property test functions. E.g. 
        'prop_' will identify functions which have names such as:
                -   pRoP_test1
                -   Prop_test2
                -   prop_test3
        """
        if type(nameStruct) != str:
            raise TypeError("invalid naming pattern")
        self.__namePattern = re.compile(f'^{nameStruct}', re.I)

    def loadFromModules(self, modules: list[str]) -> None:
        """
        sets the modules to identify test functions in.
        """
        self.__modules = []
        try:
            for module in modules:
                self.__modules.append(sys.modules[module])
        except KeyError:
            raise RuntimeError("module not found")
        self.__classes = []
        
    def loadFromClasses(self, classes: list):
        """
        sets the classes to identify test functions in.
        """
        self.__classes = classes
        self.__modules = []
        
    def setIterations(self, iters: int) -> None:
        """
        sets the number of arbitrary values to test each function with. E.g.
        a value of 100 would result in every function being tested for 100
        arbitrary pieces of data.
        """
        if type(iters) != int or iters <= 0:
            raise ValueError("invalid number of iters")
        self.__iters = iters

    def runTests(self) -> None:
        """
        Runs the tests in the specified module with the specified naming.
        """
        allFails = dict()
        fileObj = open(self.dumpFile, "w") if self.dumpFile else None
        funcsToTest = self.__funcs
        for group in funcsToTest:
            fails = []
            print(f'testing {group}:')
            for (gens, func), fname in funcsToTest[group]:
                print(f'\ttesting {fname}:\t\t', end = "")
                generators = list(map(lambda x: x(), gens))
                if not tester.__run(generators, func, self.__iters):
                    fails.append(fname)
            allFails[group] = fails
        self.__produceReport(fileObj, allFails, funcsToTest)

    def __produceReport(self, dumpfile, fails, funcsToTest):
        """
        produces final report of the results of testing
        """
        totTests = len([i for j in funcsToTest.values() for i in j])
        noFails = len([i for j in fails for i in fails[j]])
        sRate = round(100 * (totTests - noFails) / totTests, 2)

        print('=' * 50)
        print(f'{noFails} test(s) failed ({sRate}%):')
        for cname in fails:
            if len(fails[cname]):
                print(f'Failed tests in module - {cname}:')
            for tname in fails[cname]:
                print(f'\t* {tname}')
        print('=' * 50)
        
        if dumpfile:
            self.dumpToFile(fails, dumpfile, funcsToTest, noFails, sRate)

    def dumpToFile(self, fails, dumpfile, funcsToTest, noFails, sRate):
        """
        writes testing report to file if a descriptor exists.
        """
        dumpfile.write(f'{noFails} test(s) failed ({sRate}%):\n')
        for cname in fails:
            if len(fails[cname]):
                dumpfile.write(f'Failed tests in module - {cname}:\n')
            for tname in fails[cname]:
                dumpfile.write(f'\t* {tname}\n')
        dumpfile.close()

    @staticmethod
    def __validateFuncs(fs: list) -> list:
        """
        validates whether the number of generators provided is correct for
        each function.
        """
        if any([len(x[0][0]) != len(inspect.getfullargspec(x[0][1])[0]) 
                for x in fs]):
            raise RuntimeError("invalid number of generators provided")
        return fs
    
    @staticmethod
    def __run(gens: list, func, iters: int) -> bool:
        """
        runs specified function using generators and reports inaccuracies.
        """
        fails = []
        for i in range(iters):
            x = [next(g) for g in gens]
            try:
                if not func(*x):
                    fails.append(x)
            except:
                fails.append(x)
        print(f'ran {iters} test(s), with {len(fails)} failure(s)')
        tester.__printFails(fails)
        return len(fails) == 0

    @staticmethod
    def __printFails(fails: list) -> None:
        """
        prints out the values which caused errors (if any).
        """
        indent = '\t' * 2
        if len(fails):
            print(f'{indent}These include (args displayed as a list):')
        for i, val in enumerate(fails):
            if i == 5:
                break
            print(f'{indent}->\t{val}')