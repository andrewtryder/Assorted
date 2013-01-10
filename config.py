###
# Copyright (c) 2013, spline
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.registry as registry
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('Assorted')

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Assorted', True)


Assorted = conf.registerPlugin('Assorted')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Assorted, 'someConfigVariableName',
#     registry.Boolean(False, _("""Help for someConfigVariableName.""")))
conf.registerGlobalValue(Assorted, 'apiKey', registry.String('Not set', """API key to use http://www.zillow.com/howto/api/APIOverview.htm """, private=True))



# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=250:
