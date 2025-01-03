#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------#
#   coded by Lululla  #
#    Up Levi45        #
#      01/09/2024     #
#       No coppy      #
# --------------------#
# Info http://Satellite-Forum.com
from __future__ import print_function

# local import
from . import Utils
from .Console import Console
from . import (
    _,
    wgetsts,
    getfreespace,
    installer_url,
    developer_url,
    epk,
    # MYIPK,
    # MYDEB,
    # adxdeb,
    # adxipk,
)

# enigma2 lib import
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.config import config
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel
from datetime import datetime
from enigma import (eTimer, getDesktop)
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import (
    SCOPE_PLUGINS,
    resolveFilename,
)
from twisted.web.client import getPage
from xml.dom import minidom
import codecs
import os
import socket
import sys
import time
import json


PY3 = sys.version_info.major >= 3
# Compatibility handling for urlopen
if sys.version_info[0] < 3:
    from urllib2 import urlopen, Request, URLError
    PY3 = False
else:
    from urllib.request import urlopen, Request
    from urllib.error import URLError
    PY3 = True


if sys.version_info >= (2, 7, 9):
    try:
        import ssl
        sslContext = ssl._create_unverified_context()
    except:
        sslContext = None


try:
    wgetsts()
except:
    pass


# set
currversion = '10.1-r28'
name_plug = 'Levi45 Addon'
desc_plug = 'Satellite-Forum.com Addons %s' % currversion
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('Levi45Addons'))
iconx = 'plugin.png'
AgentRequest = Utils.RequestAgent()
'''
eeppkk = MYIPK.replace('+', '').replace('-', '')
eeddeebb = MYDEB.replace('+', '').replace('-', '')
epk = adxipk.replace('+', '').replace('-', '')
edeb = adxdeb.replace('+', '').replace('-', '')
'''
screenwidth = getDesktop(0).size()
if screenwidth.width() == 2560:
    skin_path = plugin_path + '/res/skins/uhd/'
elif screenwidth.width() == 1920:
    skin_path = plugin_path + '/res/skins/fhd/'
else:
    skin_path = plugin_path + '/res/skins/hd/'


isDreamOS = False
if os.path.exists("/var/lib/dpkg/status"):
    isDreamOS = True


try:
    from twisted.internet import ssl
    from twisted.internet._sslverify import ClientTLSOptions
    sslverify = True
except:
    sslverify = False


if sslverify:
    class SNIFactory(ssl.ClientContextFactory):
        def __init__(self, hostname=None):
            self.hostname = hostname

        def getContext(self):
            ctx = self._contextFactory(self.method)
            if self.hostname:
                ClientTLSOptions(self.hostname, ctx)
            return ctx


def make_request(url):
    try:
        import requests
        response = requests.get(url, verify=False, timeout=5)
        if response.status_code == 200:
            link = requests.get(url, headers={'User-Agent': AgentRequest}, timeout=10, verify=False, stream=True).text
            return link
    except ImportError:
        req = Request(url)
        req.add_header('User-Agent', 'E2 Plugin Lululla')
        response = urlopen(req, None, 10)
        link = response.read().decode('utf-8')
        response.close()
        return link
    return


class addonsupdatesScreen(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        skin = os.path.join(skin_path, 'addonsupdatesScreen.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        info = 'Please Wait..'
        self.labeltext = ('')
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'DirectionActions'], {'cancel': self.close,
                                                           'red': self.close,
                                                           'ok': self.ok,
                                                           'up': self.Up,
                                                           'down': self.Down,
                                                           'left': self.Up,
                                                           'right': self.Down,
                                                           }, -1)
        self['text'] = ScrollLabel(info)

        def fetch_url(url, retries=3, initial_timeout=5):
            timeout = initial_timeout
            for i in range(retries):
                try:
                    fp = urlopen(url, timeout=timeout)
                    lines = fp.readlines()
                    fp.close()
                    labeltext = ""
                    for line in lines:
                        if PY3:
                            line = line.decode()  # Decode bytes to str in Python 3
                        labeltext += str(line)
                    return labeltext
                except socket.timeout:
                    print("Attempt failed: The connection timed out after %s seconds." % timeout)
                    timeout *= 2  # Double the timeout for the next attempt
                except URLError as e:
                    print("URL Error:", e)
                    break
                except Exception as e:
                    print("Error:", e)
                    break
            return None

        # Use the feature to get the text and update the interface
        # labeltext = fetch_url('http://levi45.spdns.eu/Addons/AddonsPanel/News.txt')
        labeltext = fetch_url('https://raw.githubusercontent.com/levi-45/Addon/main/News.txt')
        if labeltext:
            self['text'].setText(labeltext)
        else:
            self['text'].setText('unable to download updates')

    def ok(self):
        self.close()

    def Down(self):
        self['text'].pageDown()

    def Up(self):
        self['text'].pageUp()


class AboutScreen(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        skin = os.path.join(skin_path, 'AboutScreen.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self['text'] = ScrollLabel('')
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'DirectionActions'], {'cancel': self.close,
                                                           'red': self.close,
                                                           'ok': self.ok,
                                                           'left': self.Up,
                                                           'right': self.Down,
                                                           'up': self.Up,
                                                           'down': self.Down
                                                           }, -1)
        self.onFirstExecBegin.append(self.infoBox)

    def ok(self):
        self.close()

    def Down(self):
        self['text'].pageDown()

    def Up(self):
        self['text'].pageUp()

    def arckget(self):
        zarcffll = ''
        try:
            if os.path.exists("/usr/bin/apt-get"):
                zarcffll = os.popen('dpkg --print-architecture | grep -iE "arm|aarch64|mips|cortex|sh4|sh_4"').read().strip('\n\r')
            else:
                zarcffll = os.popen('opkg print-architecture | grep -iE "arm|aarch64|mips|cortex|h4|sh_4"').read().strip('\n\r')
        except Exception as e:
            print("Error ", e)
        return str(zarcffll)

    def infoBox(self):
        try:
            arkFull = ''
            if self.arckget():
                arkFull = self.arckget()
                print('arkget= ', arkFull)
            img = os.popen('cat /etc/issue').read().strip('\n\r')
            arc = os.popen('uname -m').read().strip('\n\r')
            python = os.popen('python -V').read().strip('\n\r')
            ifg = os.popen('wget -qO - ifconfig.me').read().strip('\n\r')
            img = img.replace('\\l', '')
            libs = os.popen('ls -l /usr/lib/libss*.*').read().strip('\n\r')
            if libs:
                libsssl = libs
            info = ' ---------------------------------------------------- \n'
            info += 'Levi45 Addons v. %s\n' % currversion
            info += ' --------------------------------------------------- \n'
            info += 'Your New Addons Mod. by @Lululla\n'
            info += 'Designs and Graphics by @oktus\n\n'
            info += 'Current IP Wan: %s\nImage Mounted: %sCpu: %s\nPython:%s\nArchitecture info: %s\nLibssl(oscam):\n%s\n' % (ifg, img, arc, python, arkFull, libsssl)
            self['text'].setText(info)
        except Exception as e:
            print("Error ", e)
            self['text'].setText(_(':) by Lululla '))


class AddonsGroups(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        skin = os.path.join(skin_path, 'AddonsGroups.xml')
        if os.path.exists("/var/lib/dpkg/status"):
            skin = os.path.join(skin_path, 'AddonsGroupsCvs.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Update'))
        self['key_green'].hide()
        self['key_yellow'] = Button(_('News'))
        self['key_blue'] = Button(_('About'))
        self.list = []
        self.names = []
        self['list'] = MenuList([])
        self['info'] = Label()
        self['fspace'] = Label()
        self.addon = 'emu'
        self.icount = 0
        self['info'].setText(_('Welcome , Please Wait..'))
        self.epk = epk
        self.timer = eTimer()
        if os.path.exists("/usr/bin/apt-get"):
            self.timer_conn = self.timer.timeout.connect(self.downloadxmlpage)
        else:
            self.timer.callback.append(self.downloadxmlpage)
        self.timer.start(500, 1)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'DirectionActions',
                                     'HotkeyActions',
                                     'InfobarEPGActions',
                                     'ChannelSelectBaseActions'], {'ok': self.okClicked,
                                                                   'back': self.close,
                                                                   'cancel': self.close,
                                                                   'blue': self.ShowAbout,
                                                                   'yellow': self.shownews,
                                                                   'green': self.update_me,
                                                                   'yellow_long': self.update_dev,
                                                                   'info_long': self.update_dev,
                                                                   'infolong': self.update_dev,
                                                                   'showEventInfoPlugin': self.update_dev,
                                                                   'red': self.close}, -1)
        self.Update = False
        self.timerc = eTimer()
        if os.path.exists('/var/lib/dpkg/status'):
            self.timerc_conn = self.timerc.timeout.connect(self.check_vers)
        else:
            self.timerc.callback.append(self.check_vers)
        self.timerc.start(1000, 1)

    def check_vers(self):
        try:
            remote_version = '0.0'
            remote_changelog = ''
            req = Utils.Request(Utils.b64decoder(installer_url), headers={'User-Agent': AgentRequest})
            page = Utils.urlopen(req).read()
            if PY3:
                data = page.decode("utf-8")
            else:
                data = page.encode("utf-8")
            if data:
                lines = data.split("\n")
                for line in lines:
                    if line.startswith("version"):
                        remote_version = line.split("=")
                        remote_version = line.split("'")[1]
                    if line.startswith("changelog"):
                        remote_changelog = line.split("=")
                        remote_changelog = line.split("'")[1]
                        break
            self.new_version = remote_version
            self.new_changelog = remote_changelog
            # if float(currversion) < float(remote_version):
            if currversion < remote_version:
                self.Update = True
                self['key_green'].show()
                self.mbox = self.session.open(MessageBox, _('New version %s is available\n\nChangelog: %s\n\nPress green button to start updating') % (self.new_version, self.new_changelog), MessageBox.TYPE_INFO, timeout=5)
        except Exception as e:
            print(e)

    def update_me(self):
        if self.Update is True:
            self.session.openWithCallback(self.install_update, MessageBox, _("New version %s is available.\n\nChangelog: %s \n\nDo you want to install it now?") % (self.new_version, self.new_changelog), MessageBox.TYPE_YESNO)
        else:
            self.session.open(MessageBox, _("Congrats! You already have the latest version..."),  MessageBox.TYPE_INFO, timeout=4)

    def update_dev(self):
        req = Utils.Request(Utils.b64decoder(developer_url), headers={'User-Agent': AgentRequest})
        page = Utils.urlopen(req).read()
        data = json.loads(page)
        remote_date = data['pushed_at']
        strp_remote_date = datetime.strptime(remote_date, '%Y-%m-%dT%H:%M:%SZ')
        remote_date = strp_remote_date.strftime('%Y-%m-%d')
        self.session.openWithCallback(self.install_update, MessageBox, _("Do you want to install update ( %s ) now?") % (remote_date), MessageBox.TYPE_YESNO)

    def install_update(self, answer=False):
        if answer:
            srtrt = Utils.b64decoder(installer_url)
            cmd = 'wget -q "--no-check-certificate" ' + str(srtrt) + ' -O - | /bin/sh'
            # self.session.open(Console, 'Upgrading...', cmdlist=('wget -q "--no-check-certificate" ' + Utils.b64decoder(installer_url) + ' -O - | /bin/sh'), finishedCallback=self.myCallback, closeOnSuccess=False)
            title = _("Upgrading...\nPlease Wait...")
            self.session.open(Console, _(title), [cmd], closeOnSuccess=False)
        else:
            self.session.open(MessageBox, _("Update Aborted!"),  MessageBox.TYPE_INFO, timeout=3)

    def myCallback(self, result=None):
        print('result:', result)
        return

    def ShowAbout(self):
        self.session.open(AboutScreen)

    def shownews(self):
        self.session.open(addonsupdatesScreen)

    def downloadxmlpage(self):
        url = self.epk
        if PY3:
            url = url.encode()
        if os.path.exists("/usr/bin/apt-get"):
            print('have a dreamOs!!!')
            self.data = checkGZIP(url)
            self._gotPageLoad(self.data)
        else:
            print('have a Atv-PLi - etc..!!!')
            getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print('are here error:', str(error))
        self['info'].setText(_('Addons Download Failure\nNo internet connection or server down !'))

    def _gotPageLoad(self, data):
        self.xml = data
        self.list = []
        self.names = []

        try:
            if self.xml:
                self.xmlparse = minidom.parseString(self.xml)
                
                for plugins in self.xmlparse.getElementsByTagName('plugins'):
                    plugin_content = str(plugins.getAttribute('cont')).lower()

                    if config.ParentalControl.configured.value and 'adult' in plugin_content:
                        continue

                    if not os.path.exists("/usr/bin/apt-get") and 'oe2.2' in plugin_content:
                        continue
                    if os.path.exists("/usr/bin/apt-get") and 'oe2.2' not in plugin_content:
                        continue

                    self.names.append(str(plugins.getAttribute('cont')))
                
                if self.names:
                    self['info'].setText('Select')
                    self["list"].l.setList(self.names)
                else:
                    self['info'].setText(_('No compatible plugins found'))
        except Exception as e:
            print('Error processing server addons data: ' + str(e))
            self['info'].setText(_('Error processing server addons data'))

        try:
            mfre = getfreespace()
            self['fspace'].setText(str(mfre))
        except Exception as e:
            print('Error getting free space: ' + str(e))

    def okClicked(self):
        selection = str(self['list'].getCurrent())
        self.session.open(AddonPackages, self.xmlparse, selection)


class AddonPackages(Screen):

    def __init__(self, session, xmlparse, selection):
        Screen.__init__(self, session)
        skin = os.path.join(skin_path, 'AddonPackages.xml')
        if os.path.exists("/var/lib/dpkg/status"):
            skin = os.path.join(skin_path, 'AddonPackagesCvs.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.xmlparse = xmlparse
        self.selection = selection
        self['info'] = Label()
        self['fspace'] = Label()
        self['info'].setText(_('Welcome , Please Wait..'))
        self.list = []
        adlist = []
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    adlist.append(str(plugin.getAttribute('name')))
                continue

        adlist.sort()

        self['list'] = MenuList(adlist)
        self['info'].setText('Select')
        try:
            mfre = getfreespace()
            self['fspace'].setText(str(mfre))
        except Exception as e:
            print(e)
        self['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.close,
                                                          'ok': self.msginstal,
                                                          }, -2)

    def msginstal(self):
        self.session.openWithCallback(self.selclicked, MessageBox, _('Do you install this plugin ?'), MessageBox.TYPE_YESNO)

    def selclicked(self, result):
        if not result:
            return
        try:
            selection_country = self['list'].getCurrent()
            for plugins in self.xmlparse.getElementsByTagName('plugins'):
                if str(plugins.getAttribute('cont')) == self.selection:
                    for plugin in plugins.getElementsByTagName('plugin'):
                        if str(plugin.getAttribute('name')) == selection_country:
                            self.com = str(plugin.getElementsByTagName('url')[0].childNodes[0].data).replace('"', '')
                            self.dom = str(plugin.getAttribute('name'))
                            
                            if ".deb" in self.com:
                                if not os.path.exists("/usr/bin/apt-get"):
                                    self.session.open(
                                        MessageBox,
                                        _('Unknown Image!'),
                                        MessageBox.TYPE_INFO,
                                        timeout=5
                                    )
                                    return
                                n2 = self.com.find("_")
                                self.dom = self.com[:n2]
                            
                            elif ".ipk" in self.com:
                                if os.path.exists("/usr/bin/apt-get"):
                                    self.session.open(
                                        MessageBox,
                                        _('Unknown Image!'),
                                        MessageBox.TYPE_INFO,
                                        timeout=5
                                    )
                                    return
                                n2 = self.com.find("_")
                                self.dom = self.com[:n2]
                            
                            elif any(ext in self.com for ext in [".zip", ".tar", ".gz", ".bz2"]):
                                self.dom = self.com
                            print('self.prombt self.com: ', self.com)
                            self.prombt()
                            return
                        else:
                            print('Return from prompt ')
                            self['info'].setText('Select')
        except Exception as e:
            print('Error in prompt:', e)
            self['info'].setText('Error')

    def prombt(self):
        self.plug = self.com.split("/")[-1]
        dest = "/tmp"
        if not os.path.exists(dest):
            os.system('ln -sf /var/volatile/tmp /tmp')
        self.folddest = dest + '/' + self.plug
        cmd2 = ""
        if ".deb" in self.plug:
            cmd2 = "dpkg -i " + self.folddest
        elif ".ipk" in self.plug:
            cmd2 = "opkg install --force-reinstall --force-overwrite '" + self.folddest + "'"
        elif ".zip" in self.plug:
            cmd2 = "unzip -o -q '" + self.folddest + "' -d /"
        elif ".tar" in self.plug and ".gz" in self.plug:
            cmd2 = "tar -xvf '" + self.folddest + "' -C /"
        elif ".bz2" in self.plug and ".gz" in self.plug:
            cmd2 = "tar -xjvf '" + self.folddest + "' -C /"
        cmd = (
            "wget --no-check-certificate -U '%s' -c '%s' -O '%s'; %s > /dev/null" % 
            (AgentRequest, self.com, self.folddest, cmd2)
        )
        title = _("Installing %s\nPlease Wait...") % self.dom
        self.session.open(Console, _(title), [cmd], closeOnSuccess=False)


def checkGZIP(url):
    url = url
    from io import StringIO
    import gzip
    import requests
    import sys
    if sys.version_info[0] == 3:
        from urllib.request import (urlopen, Request)
    else:
        from urllib2 import (urlopen, Request)

    hdr = {"User-Agent": AgentRequest}
    response = None
    request = Request(url, headers=hdr)
    try:
        response = urlopen(request, timeout=10)
        if response.info().get('Content-Encoding') == 'gzip':
            buffer = StringIO(response.read())
            deflatedContent = gzip.GzipFile(fileobj=buffer)
            if sys.version_info[0] == 3:
                return deflatedContent.read().decode('utf-8')
            else:
                return deflatedContent.read()
        else:
            if sys.version_info[0] == 3:
                return response.read().decode('utf-8')
            else:
                return response.read()

    except requests.exceptions.RequestException as e:
        print("Request error:", e)
    except Exception as e:
        print("Unexpected error:", e)
    return None


def main(session, **kwargs):
    session.open(AddonsGroups)


def menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(('Levi45 Addon'), main, 'Levi45 Addon', 44)]
    return []


def Plugins(**kwargs):
    list = []
    # list.append(PluginDescriptor(name=_(name_plug), description=_(desc_plug), where=[PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART], needsRestart=True, fnc=autostart))
    list.append(PluginDescriptor(name=name_plug, description=desc_plug, where=PluginDescriptor.WHERE_PLUGINMENU, icon=iconx, fnc=main))
    # list.append(PluginDescriptor(name=name_plug, description=desc_plug, where=PluginDescriptor.WHERE_MENU, icon=iconx, fnc=menu))
    # list.append(PluginDescriptor(name=name_plug, description=desc_plug, where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon=iconx, fnc=main))
    return list

# mod by Lululla
