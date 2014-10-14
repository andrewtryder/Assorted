###
# Copyright (c) 2012-2014, spline
# All rights reserved.
#
#
###

from supybot.test import *

class AssortedTestCase(PluginTestCase):
    plugins = ('Assorted',)
        
    def testAssortedRegexp(self):
        self.assertRegexp('kernel', '[latest stable|Others]', re.I)
    
    def testDebt(self):
        self.assertRegexp('debt', 'As of')
    
    def testbase64(self):
        self.assertResponse('b64decode aGVsbG8=', 'hello')
        self.assertResponse('b64encode hello', 'aGVsbG8=')

    def testHex2ip(self):
        self.assertResponse('hex2ip 0200A8C0', 'HexIP: 0200A8C0 = ANantes-654-1-213-192.w2-0.abo.wanadoo.fr(2.0.168.192)')
    
    def testAdvice(self):
        self.assertNotError('advice')
        
    def testBash(self):
        self.assertNotError('bash')
    
    def testCatCommands(self):
        self.assertNotError('catfacts')
        self.assertNotError('catpix')
    
    def testBofh(self):
        self.assertNotError('bofh')

    def testCallook(self):
        self.assertNotError('callook W1JDD')

    def testChucknorris(self):
        self.assertNotError('chucknorris')
    
    def testDeveloperexcuses(self):
        self.assertNotError('developerexcuses')
        
    def testCoins(self):
        self.assertNotError('dogecoin')
        self.assertNotError('litecoin')
        self.assertNotError('bitcoin')
        #self.assertResponse('frink 2+2', '2+2 :: 4')
        #self.assertNotError('fuckingdinner')
        #self.assertNotRegExp('geoip 209.94.100.100', 'ERROR')
        #self.assertResponse('macvendor 0023AE000022', '0023AE000000-0023AEFFFFFF :: Dell Inc. UNITED STATES')
        #self.assertNotError('macvendor 0023AE000022')
        #self.assertNotError('megamillions')
        #self.assertNotError('mortgage')
        #self.assertNotError('mydrunktexts')
        #self.assertNotError('nerdman')
        #self.assertNotError('pick 1,2')
        #self.assertResponse('piglatin hello to you', 'ellohay otay ouyay')
        #self.assertNotError('piglatin hello to you')
        #self.assertNotError('powerball')
        #self.assertNotError('randomfacts')
        #self.assertNotError('slur')
        #self.assertNotError('woot')
        #self.assertNotError('hackernews')
    
    #def testKernel(self):
    #    self.assertNotError('kernel')        

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
