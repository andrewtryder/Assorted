# -*- coding: utf-8 -*-
###
# Copyright (c) 2012-2013, spline
# All rights reserved.
#
#
###
# my libs
from lxml import etree
from BeautifulSoup import BeautifulSoup
import urllib2
from random import choice
import json
import re
import xml.dom.minidom
import base64
import socket
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree
# supybot libs
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('Assorted')

@internationalizeDocstring
class Assorted(callbacks.Plugin):
    """Add the help for "@plugin help Assorted" here
    This should describe *how* to use this plugin."""
    threaded = True

    # http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    def _size_fmt(self, num):
        for x in ['','k','M','B','T']:
            if num < 1000.0:
              return "%3.1f%s" % (num, x)
            num /= 1000.0

    def _myfloat(self,float_string):
        """It takes a float string ("1,23" or "1,234.567.890") and
        converts it to floating point number (1.23 or 1.234567890).
        """

        float_string = str(float_string)
        errormsg = "ValueError: Input must be decimal or integer string"
        try:
            if float_string.count(".") == 1 and float_string.count(",") == 0:
                return float(float_string)
            else:
                midle_string = list(float_string)
                while midle_string.count(".") != 0:
                    midle_string.remove(".")
                out_string = str.replace("".join(midle_string), ",", ".")
            return float(out_string)
        except ValueError, error:
            print "%s\n%s" %(errormsg, error)
            return None

    def _splitinput(self, txt, seps):
        default_sep = seps[0]
        for sep in seps[1:]:
            txt = txt.replace(sep, default_sep)
        return [i.strip() for i in txt.split(default_sep)]

    def _numToDottedQuad(self, n):
        try:
            n = long(n,16)
            d = 256 * 256 * 256
            q = []
            while d > 0:
                m,n = divmod(n,d)
                q.append(str(m))
                d = d/256
            return '.'.join(q)
        except:
            return False

    def _shortenUrl(self, url):
        posturi = "https://www.googleapis.com/urlshortener/v1/url"
        headers = {'Content-Type' : 'application/json'}
        data = {'longUrl' : url}

        # if google news is up, safe to assume this is also up?
        data = json.dumps(data)
        request = urllib2.Request(posturi,data,headers)
        response = urllib2.urlopen(request)
        response_data = response.read()
        shorturi = json.loads(response_data)['id']
        return shorturi

    def _rainbow(self, text):
        text = ''.join([ircutils.mircColor(x, random.choice(ircutils.mircColors.keys())) for x in text])
        return text

    def _red(self, string):

        return ircutils.mircColor(string, 'red')

    ####################
    # PUBLIC FUNCTIONS #
    ####################

    def slur(self, irc, msg, args):
        """
        Display a random racial slur from the racial slur database (rsdb.org)
        """

        url = 'http://www.rsdb.org/full'
        request = urllib2.Request(url)
        response = (urllib2.urlopen(request))
        html = response.read()
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES, fromEncoding='utf-8')
        div = soup.find('div', attrs={'id':'slurs'})
        rows = div.findAll('tr', attrs={'id':re.compile('slur_.*')})

        slurs = []

        for row in rows:
            tds = [item.getText().strip() for item in row.findAll('td')]
            slur = tds[0].encode('utf-8')
            group = tds[1].encode('utf-8')
            reasoning = tds[2].encode('utf-8')
            slurs.append("{0}({1}) :: {2}".format(slur, group, reasoning))

        randomslur = choice(slurs)
        irc.reply(randomslur)

    slur = wrap(slur)

    def hex2ip(self, irc, msg, args, optinput):
        """<hexip>
        Try and turn hexIP back into IP address.
        """

        ip = self._numToDottedQuad(optinput)
        if ip and len(optinput) == 8:
            record = socket.gethostbyaddr(ip)[0]  # do dns here.
            if record:
                reply = "HexIP: {0} = {1}({2})".format(optinput, ip, record)
            else:
                reply = "HexIP: {0} = {1}".format(optinput, ip)
        else:
            reply = "ERROR: {0} is an invalid HexIP".format(optinput)
        irc.reply(reply.encode('utf-8'))

    hex2ip = wrap(hex2ip, (['text']))

    def kernel(self, irc, msg, args):
        """
        Display the latest linux kernels from kernel.org.
        """

        url = 'https://www.kernel.org/releases.json'

        req = urllib2.Request(url)
        html = (urllib2.urlopen(req)).read()
        # parse json
        releases = json.loads(html)
        # parse json.
        lateststable = releases['latest_stable']['version']
        releases = releases['releases']
        output = []
        for release in releases:
            moniker = release['moniker']
            version = release['version']
            released = release['released']['isodate']
            if release['iseol']:
                output.append("{0} {1} (EOL) {2}".format(moniker, version, released))
            else:
                output.append("{0} {1} (EOL) {2}".format(moniker, version, released))
        # output
        irc.reply("The latest stable kernel is: {0}".format(lateststable))
        irc.reply("Others: {0}".format(" | ".join(output)))

    kernel = wrap(kernel)

    def b64decode(self, irc, msg, args, optstring):
        """Returns base64 decoded string."""

        irc.reply(base64.b64decode(optstring))

    b64decode = wrap(b64decode, [('somethingWithoutSpaces')])

    def b64encode(self, irc, msg, args, optstring):
        """Returns bas64 encoded string."""

        irc.reply(base64.b64encode(optstring))

    b64encode = wrap(b64encode, [('somethingWithoutSpaces')])

    def pigword(self, word):
        shouldCAP = (word[:1] == word[:1].upper())
        word = word.lower()

        letters = "qwertyuiopasdfghjklzxcvbnm"
        i = len(word) - 1
        while i >= 0 and letters.find(word[i]) == -1:
            i = i - 1
        if i == -1:
            return word
        punctuation = word[i+1:]
        word = word[:i+1]

        vowels = "aeiou"
        if vowels.find(word[0]) >= 0:
            word = word + "yay" + punctuation
        else:
            word = word[1:] + word[0] + "ay" + punctuation

        if shouldCAP:
            return word[:1].upper() + word[1:]
        else:
            return word

    def piglatin(self, irc, msg, args, optinput):
        """<text>
        Convert text from English to Pig Latin.
        """

        l = optinput.split(" ")
        for i in range(len(l)):
            l[i] = self.pigword(l[i])

        irc.reply(" ".join(l))

    piglatin = wrap(piglatin, [('text')])

    def _frinkcleanup(self, text):
        text = text.replace(' in ', ' -> ')
        text = text.replace(' to ', ' -> ')
        text = text.replace(' as ', ' -> ')
        text = text.replace(' over ', ' / ')
        return text

    def frink(self, irc, msg, args, optinput):
        """<expression>
        Use the Frink online calculator. Ex: 2+2
        """

        optinput = self._frinkcleanup(optinput)
        url = 'http://futureboy.us/fsp/frink.fsp?hideHelp=Hide+%27help%27+information+below&fromVal=' + utils.web.urlquote(optinput)

        try:
            req = urllib2.Request(url)
            req.add_header("User-Agent","Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0) Gecko/17.0 Firefox/17.0")
            r = urllib2.urlopen(req)
        except Exception, e:
            self.log.error("I could not open {0} error: {1}".format(url, e))
            irc.reply("ERROR: I could not open {0}".format(url))
            return

        result = r.read()
        r_result = re.compile(r'(?i)<A NAME=results>(.*?)</A>')
        r_tag = re.compile(r'<\S+.*?>')
        match = r_result.search(result)

        if not match:
            irc.reply("Calculation error looking up: {0}.".format(optinput))
            return

        result = match.group(1)
        result = r_tag.sub("", result) # strip span.warning tags
        result = result.replace("&gt;", ">")
        result = result.replace("(undefined symbol)", "(?) ")
        result = result.strip()

        irc.reply("{0} :: {1}".format(optinput,result))

    frink = wrap(frink, [('text')])

    def geoip(self, irc, msg, args, user):
        """<ip.address>
        Use a GeoIP API to lookup the location of an IP.
        """

        # Some logic to determine if input is a user, a hostname, or IP address.
        # All code here is from the generous Hoaas who uses it within his Patdown Supybot plugin.

        try:
            socket.inet_aton(user)
            ip = user
            input = None
            user = None

        except socket.error:
            # If it is a nick in the channel
            if ( irc.isNick(user) and user in irc.state.channels[msg.args[0]].users ):
                hostname = irc.state.nickToHostmask(user)
                hostname = hostname[hostname.find("@")+1:]
            # Possibly an hostname?
            else:
                hostname = user
                user = None
            try:
                __, __, ip = socket.gethostbyname_ex(hostname)
            except socket.herror:
                irc.reply("ALERT! ERROR! No srsly, not sure what this is.")
                return
            except socket.gaierror:
                irc.reply("No IP found. (it was a hostname, right?)")
                return

            ip = ip[0]


        jsonurl = 'http://freegeoip.net/json/%s' % (ip)

        self.log.info(jsonurl)

        try:
            request = urllib2.Request(jsonurl)
            response = urllib2.urlopen(request)
            response_data = response.read()
        except urllib2.HTTPError as err:
            if err.code == 404:
                irc.reply("Error 404")
                self.log.warning("Error 404 on: %s" % (jsonurl))
            elif err.code == 403:
                irc.reply("Error 403. Try waiting 60 minutes.")
                self.log.warning("Error 403 on: %s" %s (jsonurl))
            else:
                irc.reply("Error. Check the logs.")
            return

        try:
            jsondata = json.loads(response_data)
        except:
            irc.reply("Failed in loading JSON data for GeoIP.")
            return

        if len(jsondata) < 1:
            irc.reply("I found no JSON Data forGeoIP.")
            return

        city = jsondata.get('city', None)
        region_code = jsondata.get('region_code', None)
        region_name = jsondata.get('region_name', None)
        zipcode = jsondata.get('zipcode', None)
        longitude = jsondata.get('longitude', None)
        latitude = jsondata.get('latitude', None)
        ip = jsondata.get('ip', None)

        if ip != None and city != None and region_code != None:
            output = ircutils.bold(ircutils.underline(ip))
            output += " " + city + " " + region_code
            output += " (" + longitude + ", " + latitude + ") "


        irc.reply(output)

    geoip = wrap(geoip, [('somethingWithoutSpaces')])

    def mydrunktexts(self, irc, msg, args):
        """
        Display random text from mydrunktexts.com
        """

        url = 'http://mydrunktexts.com/random'

        try:
            request = urllib2.Request(url)
            u = urllib2.urlopen(request).read()
        except:
            irc.reply("Failed to open: %s" % url)
            return

        soup = BeautifulSoup(u,convertEntities=BeautifulSoup.HTML_ENTITIES)
        txt = soup.find('div', attrs={'class':'bubblecontent'}).getText() # <div class="bubblecontent">
        irc.reply(txt)

    mydrunktexts = wrap(mydrunktexts)

    def bash(self, irc, msg, args):
        """
        Display a random bash.org quote.
        """

        url = 'http://www.bash.org/?random1'

        try:
            request = urllib2.Request(url)
            u = urllib2.urlopen(request).read()
        except:
            irc.reply("Failed to open: %s" % url)
            return

        soup = BeautifulSoup(u,convertEntities=BeautifulSoup.HTML_ENTITIES)
        quotes = soup.findAll('p', attrs={'class':'qt'})
        quote = choice(quotes)
        num = quote.findPrevious('b')

        irc.reply("[{0}] {1}".format(self._red(num.getText()),quote.getText()))

    bash = wrap(bash)

    def fml(self, irc, msg, args, getopts):
        """
        Display a random fmylife.com entry.
        """

        url = 'http://api.betacie.com/view/random?key=4be9c43fc03fe&language=en'

        try:
            request = urllib2.Request(url)
            u = urllib2.urlopen(request)
        except:
            irc.reply("Failed to open: %s" % url)
            return

        tree = ElementTree.parse(u)
        document = tree.getroot()

        if document.find('code').text != "1":
            irc.reply("Something went wrong doing FML. Try again later.")
            return

        gender = tree.find('items/item/author').get('gender') # can be none
        country = tree.find('items/item/author').get('country')
        region = tree.find('items/item/author').get('region')
        category = tree.find('items/item/category').text.encode('utf-8')
        message = tree.find('items/item/text').text.encode('utf-8')
        link = tree.find('items/item/short_url').text

        irc.reply("FML: [{0}] {1}".format(category, message))

    fml = wrap(fml, [getopts({})])

    def powerball(self, irc, msg, args):
        """Show powerball numbers."""

        url = 'http://www.usamega.com'

        try:
            req = urllib2.Request(url)
            html = (urllib2.urlopen(req)).read()
        except:
            irc.reply("Failed to fetch: %s" % url)
            return

        html = html.replace('&nbsp;','')

        soup = BeautifulSoup(html)
        nextpbdate = soup.findAll('div', attrs={'class':'BluebarSmText'})[2]
        prevpbdate = soup.findAll('div', attrs={'class':'BluebarSmText'})[3]
        curjackpot = soup.findAll('td', attrs={'class':'JackpotText'})[1]
        prevpb = soup.findAll('td', attrs={'class':'ResultsText'})[1]

        output = "Current jackpot: {0} for {1} :: Previous numbers: {2} from: {3}".format(ircutils.bold(curjackpot.text),\
            nextpbdate.text, ircutils.bold(prevpb.text), prevpbdate.text)
        irc.reply(output)

    powerball = wrap(powerball)

    def megamillions(self, irc, msg, args):
        """Show megamillions numbers."""

        url = 'http://www.megamillions.com'

        try:
            req = urllib2.Request(url)
            html = (urllib2.urlopen(req)).read()
        except:
            irc.reply("Could not fetch: %s" % url)
            return

        html = html.replace('&nbsp;',' ')

        soup = BeautifulSoup(html)
        est = soup.find('div', attrs={'id':'estimated_amount'}).find('span', attrs={'class':'yellow_text'})
        dd = soup.find('div', attrs={'id':'estimated_amount'}).find('span', attrs={'class':'yellow_text_sm'})

        url = 'http://www.megamillions.com/numbers/'

        try:
            req = urllib2.Request(url)
            html = (urllib2.urlopen(req)).read()
        except:
            irc.reply("Could not fetch: %s" % url)
            return

        html = html.replace('&nbsp;',' ')
        soup = BeautifulSoup(html)

        prev = soup.find('h1')
        table = soup.find('table', attrs={'width':'90%'})
        images = table.findAll('img', attrs={'src': re.compile('\.\./images.*?')})
        prevnum = ' '.join(i['alt'] for i in images)

        output = "{0} {1} :: {2} are {3}".format(ircutils.bold(est.renderContents()), dd.renderContents(), prev.renderContents(), ircutils.bold(prevnum))
        irc.reply(output)

    megamillions = wrap(megamillions)

    def mortgage(self, irc, msg, args, state):
        """[state code]
        Returns latest mortgage rates summary from Zillow --
        http://www.zillow.com/howto/api/APIOverview.htm
        Optional: call with the two-letter state code to display specific rates.
        """

        # need an API key.
        apiKey = self.registryValue('apiKey')
        if not apiKey or apiKey == "Not set":
            irc.reply("API key not set. See 'config help plugins.Zillow.apiKey'.")
            return

        url = API_URL % ('GetRateSummary', apiKey)

        if state:
            url += "&state=%s" % state

        self.log.info(url)
        jsondata = web.getUrl(url, headers=HEADERS)
        response = json.loads(jsondata)

        try:
            message_code = response['message']['code']
            message_text = response['message']['text']
        except:
            irc.reply("Failed to get a valid JSON response from Zillow.")
            return

        if message_code != "0":
            irc.reply("Error on response. Message code: %s (%s)" % (message_code, message_text))
            return

        rates = response.get('response', None)

        if rates != None:

            o = "The average rate on a 30 year mortgage is %s. Last week it was %s. " + \
            "If you want a 15 year mortgage the average rate is %s. Last week it was %s. " + \
            "If you're crazy enough to want a 5-1 ARM the average rate is %s. Last week it was %s. "

            resp = o % (
                self._red(rates['today']['thirtyYearFixed']), self._red(rates['lastWeek']['thirtyYearFixed']),
                self._red(rates['today']['fifteenYearFixed']), self._red(rates['lastWeek']['fifteenYearFixed']),
                self._red(rates['today']['fiveOneARM']), self._red(rates['lastWeek']['fiveOneARM']))

            irc.reply(resp)
        else:
            irc.reply("Error: No rates found.")

    mortgage = wrap(mortgage, [optional('somethingWithoutSpaces')])

    def callook(self, irc, msg, args, optsign):
        """<callsign>
        Lookup specific callsign in radio DB.
        """

        url = 'http://callook.info/%s/json' % optsign

        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            response_data = response.read()
        except urllib2.HTTPError as err:
            if err.code == 404:
                irc.reply("Error 404")
                self.log.warning("Error 404 on: %s" % (jsonurl))
            elif err.code == 403:
                irc.reply("Error 403. Try waiting 60 minutes.")
                self.log.warning("Error 403 on: %s" %s (jsonurl))
            else:
                irc.reply("Error. Check the logs.")
            return

        try:
            jsondata = json.loads(response_data)
        except:
            irc.reply("Could not load JSON data.")
            self.log.info(jsondata)
            return

        status = jsondata.get('status')

        if status == "INVALID":
            irc.reply("%s is INVALID" % optsign)
            return

        if status == "VALID":
            lictype = jsondata.get('type')
            name = jsondata.get('name')
            grantDate = jsondata['otherInfo'].get('grantDate')
            operclass = jsondata['current'].get('operClass')

            output = "{0} {1} {2} {3}".format(lictype, name, grantDate, operclass)

            irc.reply(output)

    callook = wrap(callook, [('somethingWithoutSpaces')])

    def randomfacts(self, irc, msg, args):
        """Fetch a random fact from www.randomfunfacts.com"""

        url = 'http://www.randomfunfacts.com'

        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read()

        fact = re.search(r'<strong><i>(.*?)</i></strong>', the_page, re.I|re.S)

        irc.reply(fact.group(1))

    randomfacts = wrap(randomfacts)

    def automeme(self, irc, msg, args, number):
        """
        Display a meme from http://www.automeme.net
        Specify a number after the command [1-7] for more than one.
        """

        if number and (0 < number <= 7):
            number = number
        else:
            number = 1


        jsonurl = 'http://api.automeme.net/text.json?lines=%s' % number
        request = urllib2.Request(jsonurl)
        response = urllib2.urlopen(request)
        response_data = response.read()
        jsondata = json.loads(response_data)

        for meme in jsondata:
            irc.reply(meme)

    automeme = wrap(automeme, [optional("int")])


    def chucknorris(self, irc, msg, args, opts):
        """
        Grab a random ChuckNorris from icndb.com.
        Use --rainbow to display in a colorful way.
        """

        opts = dict(opts)

        api_url = 'http://api.icndb.com/jokes/random'

        try:
            req = urllib2.Request(api_url)
            stream = urllib2.urlopen(req)
            datas = stream.read()
        except urllib2.HTTPError, err:
            self.log.warning("Twitter trends: API returned http error %s" % err.code)
            return

        try:
            data = json.loads(datas)
        except:
            irc.reply("Error: Failed to parsed receive data.")
            self.log.warning("Error parsing: %s" % (data))
            return

        if (data['value']['joke']):
            joke = data['value']['joke']
        else:
            irc.reply("Missing output value.")
            self.log.warning(data)
            return

        # options for rainbow. Thanks to ProgVal for the syntax here.
        if 'rainbow' in opts:
            joke = self._rainbow(joke)

        irc.reply(joke)

    chucknorris = wrap(chucknorris, [getopts({'rainbow': ''})])

    def litecoin(self, irc, msg, args):
        """
        Return pretty-printed litecoin ticker in USD.
        """

        url = 'https://btc-e.com/api/2/ltc_usd/ticker'

        try:
            html = (urllib2.urlopen(url)).read()
        except:
            irc.error("Failure to retrieve ticker. Try again later.")
            return

        try:
            ticker = json.loads(html)
        except Exception:
            irc.reply("Failed to parse JSON from: {0}".format(url))
            return

        bitcoin = ticker['ticker']

        if not bitcoin:
            irc.reply("Error parsing btc-e.com API at {0}".format(url))
            return
        else:
            last = ircutils.mircColor(bitcoin['last'], 'green')
            vol = ircutils.mircColor(bitcoin['vol'], 'orange')
            low = ircutils.mircColor(bitcoin['low'], 'blue')
            high = ircutils.mircColor(bitcoin['high'], 'red')
            average = ircutils.mircColor(bitcoin['avg'], 'light blue')

            output = "Last trade: " + last
            output += "  24hr volume: " + vol
            output += "  low: " + low
            output += "  high: " + high
            output += "  average: " + average
            output += "  (figures all in USD)"

            irc.reply(output)

    litecoin = wrap(litecoin)

    def bitcoin(self, irc, msg, args):
        """
        Return pretty-printed mtgox ticker in USD.
        """

        url = 'https://data.mtgox.com/api/2/BTCUSD/money/ticker'

        try:
            html = (urllib2.urlopen(url)).read()
        except:
            irc.error("Failure to retrieve ticker. Try again later.")
            return

        ticker = json.loads(html)
        bitcoin = ticker['data']

        if not bitcoin:
            irc.reply("Error parsing mtgox API.")
            return
        else:
            last = ircutils.mircColor(bitcoin['last']['display'], 'green')
            vol = ircutils.mircColor(bitcoin['vol']['display'], 'orange')
            low = ircutils.mircColor(bitcoin['low']['display'], 'blue')
            high = ircutils.mircColor(bitcoin['high']['display'], 'red')

            output = "Last trade: " + last
            output += "  24hr volume: " + vol
            output += "  low: " + low
            output += "  high: " + high
            output += "  (figures all in USD)"

            irc.reply(output)

    bitcoin = wrap(bitcoin)

    def isitdown(self, irc, msg, args, url):
        """
        <url>: Returns the response from http://www.downforeveryoneorjustme.com/
        """
        site = 'http://downforeveryoneorjustme.com/'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        # strip the protocol because downforeveryoneorjustme.com is
        # too stupid to do that; we're smarter than that, damnit
        url = re.sub(r'^.*?://', r'', url)
        try:
            html = opener.open(site + url)
            html_str = html.read()
            soup = BeautifulSoup(html_str)
            response = soup.div.contents[0].strip()
            irc.reply(response, prefixNick=True)
        except HTTPError, oops:
            irc.reply("Hmm. downforeveryoneorjustme.com returned the following error: [%s]" % (str(oops)), prefixNick=True)
        except AttributeError:
            irc.reply("Hmm. downforeveryoneorjustme.com probably changed its response format; please update me.", prefixNick=True)
        except:
            irc.reply("Man, I have no idea; things blew up real good.", prefixNick=True)
    isitdown = wrap(isitdown, ['text'])

    def nerdman(self, irc, args, msg, opts):
        """
        Display one of nerdman's wonderful quotes.
        """

        opts = dict(opts)

        url = 'http://www.hockeydrunk.com/nerdman/random.php'

        # attempt to fetch data
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
        except URLError, e:
            irc.reply(ircutils.mircColor("ERROR:", 'red') + " fetching hockeydrunk.com URL: %s" % (e.reason))
            return
        except HTTPError, e:
            irc.reply(ircutils.mircColor("ERROR:", 'red') + " fetching hockeydrunk.com URL: %s" % (e.code))
            return

        try:
            response_data = response.read()
        except:
            irc.reply(ircutils.mircColor("ERROR:", 'red') + " Failed to read and parse XML response data.")
            return

        if 'rainbow' in opts:
           response_data = self._rainbow(response_data)


        if len(response_data) > 0:
            irc.reply(response_data)


    nerdman = wrap(nerdman, [getopts({'rainbow': ''})])

    def fuckingdinner(self, irc, msg, args, opts):
        """[--veg]

        What the fuck should I make for dinner? Pulls a receipe from http://whatthefuckshouldimakefordinner.com
        If --veg is given, a vegetarian meal will be selected."""

        url = 'http://www.whatthefuckshouldimakefordinner.com/'

        # input dict
        opts = dict(opts)

        # option for vegetarian
        if 'veg' in opts:
            url += 'veg.php'

        try:
            html = utils.web.getUrl(url)
        except utils.web.Error, e:
            irc.error(format('I couldn\'t reach the search page (%s).', e), Raise=True)

        soup = BeautifulSoup(html)
        results = soup.findAll('dt')

        if not results:
            irc.error('I could not the proper formatting on the page. Could %s be broken?' % url)
        else:
            out = results[0].dl.string + ' ' + ircutils.bold(results[1].a.string) + ': '
            out = re.sub(r'fucking', ircutils.underline('FUCKING'), out, re.I)
            out = re.sub(r'<[^>]*?>', '', out)
            out = re.sub(r'\n', '', out)
            out += ircutils.mircColor(self._shortenUrl(results[1].a['href']), 'blue')
            irc.reply(out.encode('utf-8'))

    fuckingdinner = wrap(fuckingdinner, [getopts({'veg': ''})])

    def winewoot(self, irc, msg, args):
        """ Display daily wine.woot.com deal."""

        url = "http://wine.woot.com/salerss.aspx"

        dom = xml.dom.minidom.parse(urllib2.urlopen(url))

        product = dom.getElementsByTagName("woot:product")[0].childNodes[0].data
        price = dom.getElementsByTagName("woot:price")[0].childNodes[0].data
        purchaseurl = dom.getElementsByTagName("woot:purchaseurl")[0].childNodes[0].data
        soldout = dom.getElementsByTagName("woot:soldout")[0].childNodes[0].data # false
        shipping = dom.getElementsByTagName("woot:shipping")[0].childNodes[0].data

        if soldout == 'false':
            output = ircutils.mircColor("IN STOCK ", "green")
        else:
            output = ircutils.mircColor("SOLDOUT ", "red")

        output += ircutils.underline(ircutils.bold("ITEM:")) + " " + product + " "
        output += ircutils.underline(ircutils.bold("PRICE:")) + " " + price + " (Shipping:" + shipping + ") "
        output += ircutils.underline(ircutils.bold("URL:")) + " " + self._shortenUrl(purchaseurl) + " "

        irc.reply(output)

    winewoot = wrap(winewoot)


    def woot(self, irc, msg, args):
        """ Display daily woot.com deal."""

        url = "http://www.woot.com/salerss.aspx"

        dom = xml.dom.minidom.parse(urllib2.urlopen(url))

        product = dom.getElementsByTagName("woot:product")[0].childNodes[0].data
        price = dom.getElementsByTagName("woot:price")[0].childNodes[0].data
        purchaseurl = dom.getElementsByTagName("woot:purchaseurl")[0].childNodes[0].data
        soldout = dom.getElementsByTagName("woot:soldout")[0].childNodes[0].data # false
        shipping = dom.getElementsByTagName("woot:shipping")[0].childNodes[0].data

        if soldout == 'false':
            output = ircutils.mircColor("IN STOCK ", "green")
        else:
            output = ircutils.mircColor("SOLDOUT ", "red")

        output += ircutils.underline(ircutils.bold("ITEM:")) + " " + product + " "
        output += ircutils.underline(ircutils.bold("PRICE:")) + " " + price + " (Shipping:" + shipping + ") "
        output += ircutils.underline(ircutils.bold("URL:")) + " " + self._shortenUrl(purchaseurl) + " "

        irc.reply(output)

    woot = wrap(woot)


    def pick(self, irc, msg, args, choices):
        """[choices]
        Picks a random item from choices. Separate the list by a comma.
        """

        choicelist = self._splitinput(choices, [','])

        output = "From the " + ircutils.mircColor(str(len(choicelist)), 'red') + " choice(s) you entered, "
        output += "I have selected: " + ircutils.bold(ircutils.underline(choice(choicelist)))

        irc.reply(output)

    pick = wrap(pick, ['text'])

    def advice(self, irc, msg, args):
        """Grab some advice from http://www.leonatkinson.com/random/
        """

        url = "http://www.leonatkinson.com/random/index.php/rest.html?method=advice"

        doc = etree.parse(url)

        quote = doc.find("quote").text
        author = doc.find("author").text
        date = doc.find("date").text

        output = "\"" + quote + "\""
        output += " " + ircutils.bold(ircutils.underline(author)) + " "
        output += "(" + date + ")"

        irc.reply(output)

    advice = wrap(advice)

    def debt(self, irc, msg, args):
        """Display the debt."""

        debt_page = urllib2.urlopen('http://www.treasurydirect.gov/NP/BPDLogin?application=np')
        soup = BeautifulSoup(debt_page)
        debt = soup.find('table',{'class':'data1'}).findAll('td')[3].contents
        asof = soup.find('table',{'class':'data1'}).findAll('td')[0].contents

        population_url = 'http://www.census.gov/main/www/popclock.html'
        population_page = urllib2.urlopen(population_url)

        soup = BeautifulSoup(population_page)
        population = soup.find('span',{'id':'usclocknum'}).contents

        # turn population and debt into float so we can divide into per_person
        strpopulation = str(population[0]).replace(",","")
        strdebt = str(debt[0]).replace(",", "")
        per_person = float(strdebt)/float(strpopulation)

        # format the output and clean it up
        asof = ircutils.underline(asof[0])

        # format debt
        debt = self._myfloat(strdebt)
        debt = ircutils.bold("$" + self._size_fmt(debt))

        # per_person + population just need millify + bold
        per_person = ircutils.bold("$" + self._size_fmt(float(per_person)))
        population = ircutils.bold("$" + self._size_fmt(float(strpopulation)))

        irc.reply("As of: %s the US Debt is %s or about %s per person for a population of %s"
        % (asof, debt, per_person, population))

    debt = wrap(debt)


Class = Assorted


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
