###
# Copyright (c) 2012-2014, spline
# All rights reserved.
#
#
###

from supybot.test import *

class AssortedTestCase(PluginTestCase):
    plugins = ('Assorted',)
    
    def testAssorted(self):
        # advice, automeme, b64decode, b64encode, bash, bitcoin, bofh, callook
        # catfacts, catpix, chucknorris, debt, developerexcuses, dogecoin, fml, frink, fuckingdinner,
        # geoip, hackernews, hex2ip, hipster, kernel, litecoin, macvendor, megamillions, mortgage,
        # mydrunktexts, nerdman, pick, piglatin, powerball, randomfacts, slur, and woot
        self.assertNotError('advice')
        self.assertNotError('automeme')
        self.assertResponse('b64decode aGVsbG8=', 'hello')
        self.assertResponse('b64encode hello', 'aGVsbG8=')
        self.assertNotError('bash')
        self.assertNotError('bitcoin')
        self.assertNotError('bofh')
        self.assertNotError('callook W1JDD')
        self.assertNotError('catfacts')
        self.assertNotError('catpix')
        self.assertNotError('chucknorris')
        self.assertNotError('debt')
        self.assertNotError('developerexcuses')
        self.assertNotError('dogecoin')
        self.assertNotError('fml')


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
