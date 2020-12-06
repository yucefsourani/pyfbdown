#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pyfbdown.py
#  
#  Copyright 2020 youcef sourani <youssef.m.sourani@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
import gi
gi.require_version("Gtk","3.0")
gi.require_version('Gst', '1.0')
from gi.repository import Gtk,GLib,Gdk,GdkPixbuf,GObject,Gio,Pango,Gst
import os
import threading
import urllib.request as request
import re
import sys
import subprocess
import gettext
import json 

Gst.init(None)
Gst.init_check(None)

def get_correct_path(relative_path):
    if sys.platform.startswith('win'):
        if getattr(sys, 'frozen',False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
    else:
        exedir = os.path.dirname(sys.argv[0])
        p      = os.path.join(exedir,'..', 'share')
        if not os.path.exists(p):
            base_path = exedir
        else :
            base_path = p
            
    return os.path.join(base_path, relative_path)

if sys.platform.startswith('win'):
    import locale
    if os.getenv('LANG') is None:
        lang, enc = locale.getdefaultlocale()
        os.environ['LANG'] = lang
        
gettext.install('pyfbdown', localedir=get_correct_path('locale'))

authors_         = ["Youssef Sourani <youssef.m.sourani@gmail.com>"]
version_         = "1.0"
copyright_       = "Copyright © 2020 Youssef Sourani"
comments_        = "Facebook Videos Downloader"
website_         = "https://github.com/yucefsourani/pyfbdown"
translators_     = ("translator-credit")
appname          = "pyfbdown"
appwindowtitle   = "PyFBDown"
appid            = "com.github.yucefsourani.pyfbdown"
icon_            = get_correct_path("pixmaps/com.github.yucefsourani.pyfbdown.svg")
if not os.path.isfile(icon_):
    icon_ = None

default_metadata = """{{"current_links"           : [],"current_save_location"   : "{}"}}
""".format(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS))

default_metadata_file_name = os.path.join(GLib.get_user_config_dir(),"pyfbdown.json")

def get_metadata_info():
    if not os.path.isfile(default_metadata_file_name):
        default_metadata_dict = json.loads(default_metadata)
        with open(default_metadata_file_name,"w",encoding="utf-8") as mf:
            json.dump(default_metadata_dict,mf ,indent=4)
        return get_metadata_info()
    try:
        with open(default_metadata_file_name,encoding="utf-8") as mf:
            result = json.load(mf)
    except Exception as e:
        print(e)
        return False
    return result
    
def change_metadata_info(data):
    if not os.path.isfile(default_metadata_file_name) and os.path.exists(default_metadata_file_name):
        return False
    try:
        with open(default_metadata_file_name,"w",encoding="utf-8") as mf:
            result = json.dump(data,mf ,indent=4)
    except Exception as e:
        print(e)
        return False
    return result
    
MENU_XML="""
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="app-menu">
    <section>
      <item>
        <attribute name="action">app.about</attribute>
        <attribute name="label" translatable="yes">_About</attribute>
      </item>
      <item>
        <attribute name="action">app.quit</attribute>
        <attribute name="label" translatable="yes">_Quit</attribute>
        <attribute name="accel">&lt;Primary&gt;q</attribute>
    </item>
    </section>
  </menu>
</interface>
"""

css = b"""
        .h1 {
            font-size: 24px;
        }
        .h2 {
            font-weight: bold;
            font-size: 18px;
        }
        .h3 {
            font-size: 11px;
        }
        .h4 {
            color: alpha (@text_color, 0.7);
            font-weight: bold;
            text-shadow: 0 1px @text_shadow_color;
        }
        .h4 {
            padding-bottom: 6px;
            padding-top: 6px;
        }
        """



class GstWidget(Gtk.EventBox):
    def __init__(self, link,parent):
        super().__init__()
        self.link = link
        self.parent= parent
        self.set_size_request(200, 100)
        #self.player = Gst.ElementFactory.make("playbin")
        #self.player.set_property("uri", link)

        self.connect('realize', self.on_realize)
        self.overlay = Gtk.Overlay()
        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK  | Gdk.EventMask.LEAVE_NOTIFY_MASK  )
        self.add(self.overlay)
        self.connect("leave-notify-event",self.on_leave)
        self.connect("enter-notify-event",self.on_enter)
        
        pix1 = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(get_correct_path("data"),"play.png"),32,32,True)
        self.playi = Gtk.Image.new_from_pixbuf(pix1 )
        self.play  = Gtk.EventBox()
        self.play.add(self.playi)
        self.play .set_halign(Gtk.Align.CENTER)
        self.play .set_valign(Gtk.Align.CENTER)
        #self.play.props.no_show_all = True
        self.play.add_events(Gdk.EventMask.BUTTON_PRESS_MASK )
        self.play.connect("button-press-event",self.on_play)

        pix2 = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(get_correct_path("data"),"stop.svg"),32,32,True)
        self.stopi = Gtk.Image.new_from_pixbuf(pix2)
        self.stop  = Gtk.EventBox()
        self.stop.add(self.stopi)
        self.stop .set_halign(Gtk.Align.CENTER)
        self.stop .set_valign(Gtk.Align.CENTER)
        #self.stop.props.no_show_all = True
        self.stop.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.stop.connect("button-press-event",self.on_stop)
        
        self.activate_image = self.play 

    def on_play(self,image,event):
        playerState = self.playbin.get_state(Gst.SECOND).state
        if playerState is not  Gst.State.PLAYING:
            self.playbin.set_state(Gst.State.PLAYING)
            self.activate_image  = self.stop
            self.overlay.add_overlay(self.stop)
            self.stop.show_all()
            
    def on_stop(self,image,event):
        playerState = self.playbin.get_state(Gst.SECOND).state
        if playerState <= Gst.State.PAUSED:
            self.playbin.set_state(Gst.State.PAUSED)
            self.activate_image  = self.play
            self.overlay.add_overlay(self.play)
            self.play.show_all()

    def on_leave(self,box,event):
        self.overlay.remove(self.activate_image)
        self.play.hide()
        self.stop.hide()
        
    def on_enter(self,box,event):
        playerState = self.playbin.get_state(Gst.SECOND).state
        if playerState <= Gst.State.PAUSED:
            self.activate_image  = self.play
            self.overlay.add_overlay(self.play)
            self.play.show_all()
        elif playerState is Gst.State.PLAYING:
            self.activate_image  = self.stop
            self.overlay.add_overlay(self.stop)
            self.stop.show_all()
                   
    def on_realize(self, widget):
        gtksink   = Gst.ElementFactory.make('gtksink')
        self.overlay.add(gtksink.props.widget)
        gtksink.props.widget.show()
        
        self.playbin   = Gst.ElementFactory.make("playbin")
        self.playbin.set_property('uri', self.link)
        self.playbin.set_property('force-aspect-ratio', True)
        self.playbin.set_property('video-sink',gtksink)

        
    """def on_realize(self, widget):
        self.playbin  = Gst.Pipeline()
        factory   = self.playbin.get_factory()
        
        self._bin = Gst.parse_bin_from_description("playbin uri={} video-sink=gtksink".format(self.link),True)        
        gtksink   = factory.make('gtksink')
        self.playbin.add(self._bin)
        self.playbin.add(gtksink)
        
        
        #self._bin.link(gtksink)
        self.overlay.add(gtksink.props.widget)
        gtksink.props.widget.show()"""


            
    """def on_realize(self, widget):
        playerFactory = self.player.get_factory()
        gtksink = playerFactory.make('gtksink')
        self.player.set_property("video-sink", gtksink)

        self.pack_start(gtksink.props.widget, True, True, 0)
        gtksink.props.widget.show()
        self.player.set_state(Gst.State.PLAYING)
        
    def on_btnPlay_clicked(self, widget=None):
        playerState = self.player.get_state(Gst.SECOND).state
        if playerState <= Gst.State.PAUSED:
            self.player.set_state(Gst.State.PLAYING)
            #self.btnPlay.set_label("Pause")
        elif playerState is Gst.State.PLAYING:
            self.player.set_state(Gst.State.PAUSED)
            #self.btnPlay.set_label("Play")"""

class DownloadYesOrNo(Gtk.MessageDialog):
    def __init__(self,msg,parent=None):
        Gtk.MessageDialog.__init__(self)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,"ReDownload File",Gtk.ResponseType.REJECT ,"Try Resume Download", Gtk.ResponseType.OK
        )
        self.props.message_type = Gtk.MessageType.QUESTION
        self.props.text         = msg
        self.p=parent
        if self.p != None:
            self.parent=self.p
            self.set_transient_for(self.p)
            self.set_modal(True)
            self.p.set_sensitive(False)
        else:
            self.set_position(Gtk.WindowPosition.CENTER)
            
    def check(self):
        rrun = self.run()
        if rrun == Gtk.ResponseType.OK:
            self.destroy()
            if self.p != None:
                self.p.set_sensitive(True)
            return "resume"
        elif rrun == Gtk.ResponseType.REJECT:
            self.destroy()
            if self.p != None:
                self.p.set_sensitive(True)
            return "redownload"
        else:
            if self.p != None:
                self.p.set_sensitive(True)
            self.destroy()
            return "cancel"
            
class YesOrNo(Gtk.MessageDialog):
    def __init__(self,msg,parent=None):
        Gtk.MessageDialog.__init__(self,buttons = Gtk.ButtonsType.OK_CANCEL)
        self.props.message_type = Gtk.MessageType.QUESTION
        self.props.text         = msg
        self.p=parent
        if self.p != None:
            self.parent=self.p
            self.set_transient_for(self.p)
            self.set_modal(True)
            self.p.set_sensitive(False)
        else:
            self.set_position(Gtk.WindowPosition.CENTER)
            
    def check(self):
        rrun = self.run()
        if rrun == Gtk.ResponseType.OK:
            self.destroy()
            if self.p != None:
                self.p.set_sensitive(True)
            return True
        else:
            if self.p != None:
                self.p.set_sensitive(True)
            self.destroy()
            return False


class DownloadFile(GObject.Object,threading.Thread):
    __gsignals__ = { "break"     : (GObject.SignalFlags.RUN_LAST, None, ())
    }
    
    def __init__(self,parent,progressbar,button,link,location=None,filename=None,fsize=None,cancel_button=None,close_button=None,mode="w",header={"User-Agent":"Mozilla/5.0"}):
        GObject.Object.__init__(self)
        threading.Thread.__init__(self)
        self.parent        = parent
        self.progressbar   = progressbar
        self.button        = button
        self.link          = link
        self.location      = location
        self.filename      = filename
        self.fsize         = fsize
        self.break_        = False
        self.cancel_button = cancel_button
        self.close_button  = close_button
        self.mode          = mode
        self.header        = header
        self.connect("break",self.on_break)

        
    def on_break(self,s):
        self.break_ = True        
            
    def run(self):
        self.break_ = False
        GLib.idle_add(self.progressbar.show)
        GLib.idle_add(self.button.set_sensitive,False)
        GLib.idle_add(self.close_button.set_sensitive,False)
        saveas_location = os.path.join(self.location,self.filename) 
        ch = 64*1024 
        try:
            with open(saveas_location, self.mode) as op:
                if self.mode == "wb":
                    current_size = 0
                else:
                    op.seek(0,os.SEEK_END)
                    current_size = op.tell()
                psize = current_size
                if current_size == int(self.fsize):
                    GLib.idle_add(self.progressbar.set_fraction,0.0)
                    GLib.idle_add(self.progressbar.set_text,_("Done"))
                    GLib.idle_add(self.button.set_sensitive,True)
                    GLib.idle_add(self.close_button.set_sensitive,True)
                    GLib.idle_add(self.cancel_button.set_sensitive,False)
                    try:
                        op.close()
                    except Exception as e:
                        pass
                    return
                if "Range" in self.header.keys():
                    self.header["Range"] = "bytes={}-{}".format(current_size,self.fsize)
                else:
                    self.header.setdefault("Range", "bytes={}-{}".format(current_size,self.fsize))
                
                url   = request.Request(self.link,headers=self.header)
                opurl = request.urlopen(url,timeout=10)

                while True:
                    if self.break_:
                        GLib.idle_add(self.progressbar.set_fraction,0.0)
                        GLib.idle_add(self.progressbar.set_text,_("Canceled"))
                        GLib.idle_add(self.button.set_sensitive,True)
                        GLib.idle_add(self.close_button.set_sensitive,True)
                        GLib.idle_add(self.cancel_button.set_sensitive,False)
                        try:
                            op.close()
                            opurl.close()
                        except Exception as e:
                            pass
                        return
                    op.flush()
                    if psize >=int(self.fsize):
                        break
                    n = int(self.fsize)-psize
                    if n<ch:
                        ch = n

                    chunk = opurl.read(ch)

                    count = int((psize*100)//int(self.fsize))
                    fraction = count/100
                    op.write(chunk)
                    psize += ch
                    GLib.idle_add(self.progressbar.set_fraction,fraction)
                    GLib.idle_add(self.progressbar.set_text,str(count)+"%"+" "+str(psize)+"/"+self.fsize+" B")
                
            GLib.idle_add(self.progressbar.set_fraction,1.0)
            GLib.idle_add(self.progressbar.set_text,_("Done"))
        except Exception as e:
            print(e)
            GLib.idle_add(self.progressbar.set_fraction,0.0)
            GLib.idle_add(self.progressbar.set_text,_("Fail"))
            GLib.idle_add(self.button.set_sensitive,True)
            GLib.idle_add(self.close_button.set_sensitive,True)
            GLib.idle_add(self.cancel_button.set_sensitive,False)
            return False
        finally:
            try:
                opurl.close()
            except Exception as e:
                pass
            
        GLib.idle_add(self.progressbar.set_fraction,0.0)
        GLib.idle_add(self.button.set_sensitive,True)
        GLib.idle_add(self.close_button.set_sensitive,True)
        GLib.idle_add(self.cancel_button.set_sensitive,False)

class FBDownloader(Gtk.ApplicationWindow):
    __gsignals__ = { "ongetlinksdone"     : (GObject.SignalFlags.RUN_LAST, None, (str,))
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if icon_:
            self.set_icon(GdkPixbuf.Pixbuf.new_from_file(icon_))
        self.set_border_width(10)
        self.set_size_request(800, 600)

        self.mainvbox = Gtk.VBox()
        self.add(self.mainvbox)
        
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        

        self.config__ = get_metadata_info()
        
        self.make_header()
        self.make_entry()

        self.connect("ongetlinksdone",self.on_get_links_done)
        self.show_all()
        
        for i in self.config__["current_links"]:
            self.make_listbox_row(i)

        
    def make_header(self):
        self.headerbar = Gtk.HeaderBar.new()
        self.headerbar.props.decoration_layout = "menu:minimize,maximize,close"
        self.headerbar.props.title = self.props.title
        self.headerbar.props.decoration_layout_set = True
        self.headerbar.props.show_close_button = True
        self.headerbar.props.has_subtitle = False
        self.set_titlebar(self.headerbar)
        
        self.pastebutton = Gtk.Button.new_from_icon_name("edit-paste-symbolic", Gtk.IconSize.MENU)
        self.pastebutton.props.tooltip_text = _("Paste URL")
        
        self.pastebutton.connect("clicked",self.on_paste_button_clicked)
        self.headerbar.pack_end(self.pastebutton)
        
        self.__spinner = Gtk.Spinner()
        self.__spinner.props.no_show_all = True
        self.headerbar.pack_end(self.__spinner)
    
    def on_paste_button_clicked(self,button):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD  )
        text = clipboard.wait_for_text()
        if text:
            self.download_entry.set_text(text)
            
    def make_entry(self):
        folder = self.config__["current_save_location"]
        if not os.path.isdir(folder):
            folder = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS)
            self.config__["current_save_location"] = folder
        self.folder = "file://"+folder 
        self.choicefolder = Gtk.FileChooserButton(action="select-folder")
        self.choicefolder.set_uri(self.folder)
        self.choicefolder.set_margin_start(10)
        self.choicefolder.set_margin_end(10)
        self.choicefolder.set_margin_top(10)
        self.choicefolder.set_margin_bottom(10)
        self.choicefolder.props.tooltip_text = _("Saves Video Location")
        
        self.entry_hbox = Gtk.HBox()
        self.entry_hbox.set_margin_start(10)
        self.entry_hbox.set_margin_end(10)
        self.entry_hbox.set_margin_top(10)
        self.entry_hbox.set_margin_bottom(10)
        self.entry_hbox.props.spacing = 10
        self.mainvbox.pack_start(self.entry_hbox,False,False,0)
        self.mainvbox.pack_start(self.choicefolder,False,False,0)
        
        self.url_label = Gtk.Label()
        self.url_label.get_style_context().add_class("h1")
        self.url_label.props.label = _("URL")
        self.url_label.props.ellipsize = Pango.EllipsizeMode.END
        self.entry_hbox.pack_start(self.url_label,False,False,0)
        
        
        self.download_entry = Gtk.Entry()
        self.download_entry.props.placeholder_text = _("Enter Facebook Video Url...")
        self.download_entry.props.tooltip_text = _("Enter Facebook Video Url...")
        self.download_entry.set_input_purpose(Gtk.InputPurpose.URL)
        self.download_entry.set_has_frame(True)
        self.download_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY ,"edit-clear-symbolic")
        self.download_entry.connect("icon_press",self.on_entry_icon_press)
        self.entry_hbox.pack_start(self.download_entry,True,True,0)
        

        
        self.info_button = Gtk.Button()
        self.info_button.props.label = _("Get Info")
        self.info_button.connect("clicked",self.on_info_button_clicked)
        self.entry_hbox.pack_start(self.info_button,True,True,0)
        


        
        self.sw = Gtk.ScrolledWindow()
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.BROWSE )
        self.mainvbox.pack_start(self.sw,True,True,0)
        self.sw.add(self.listbox)
    
    def on_info_button_clicked(self,button):
        url = self.download_entry.get_text().strip()
        if not url:
            return 
        if any( [True for i in self.config__["current_links"] if url in i[0] ]):
            return 
        button.set_sensitive(False)
        self.get_links_t(url)

        
    def on_entry_icon_press(self,entry, icon_pos, event):
        if event.button == 1:
            self.download_entry.set_text("")

    def get_links_t(self,url):
        self.__spinner.show()
        self.__spinner.start()
        t = threading.Thread(target=self.get_links,args=(url,))
        t.setDaemon(True)
        t.start()
        
    def get_links(self,url):
        result = ""
        try:
            req    = request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
            opurl  = request.urlopen(req,timeout=10)
            html   = opurl.read().decode('utf-8')
            hd     = re.search('hd_src:"(.+?)"',html)
            sd     = re.search('sd_src:"(.+?)"',html)
            if hd:
                rlt    = hd[1]
                req2   = request.Request(rlt,headers={"User-Agent":"Mozilla/5.0"})
                opurl2 = request.urlopen(req2,timeout=10)          
                size   = int(opurl2.headers["Content-Length"])
                sizes  = round(int(opurl2.headers["Content-Length"])/1024/1024,2)
                result+= "HD-{}MB_{} ".format(str(sizes),os.path.basename(rlt.split("?")[0]))+rlt+" "+url + " "+str(size)+ " "
            if sd:
                rlt    = sd[1]
                req2   = request.Request(rlt,headers={"User-Agent":"Mozilla/5.0"})
                opurl2 = request.urlopen(req2,timeout=10)          
                size   = int(opurl2.headers["Content-Length"])
                sizes  = round(int(opurl2.headers["Content-Length"])/1024/1024,2)
                result+= "SD-{}MB_{} ".format(str(sizes),os.path.basename(rlt.split("?")[0]))+rlt+" "+url + " "+str(size)+ " "
        except Exception as e :
            print(e)
        GLib.idle_add(self.info_button.set_sensitive,True)
        GLib.idle_add(self.emit,"ongetlinksdone",result)
   
    def on_get_links_done(self,mainwindow,links):
        self.__spinner.stop()
        self.__spinner.hide()
        if not links:
            return
            
        result = []
        links = links.split()
        links = [i for i in links if i]
        for i in range(0,len(links)):
            if i==0 :
                result.append([links[i].split("_",1)[0],links[i],links[i+1],links[i+2],links[i+3]])
        self.config__["current_links"].append(result)
        change_metadata_info(self.config__)
        self.make_listbox_row(result)



    def make_listbox_row(self,result):
        row = Gtk.ListBoxRow()
        v   = Gtk.VBox()
        v.props.spacing = 10
        h   = Gtk.HBox()
        h.set_margin_start(10)
        h.set_margin_end(10)
        h.set_margin_top(10)
        h.set_margin_bottom(10)
        h.props.spacing = 10
        row.add(v)
        self.listbox.add(row)
        label = Gtk.Label()
        label.set_margin_top(10)
        label.set_margin_bottom(10)
        label.props.label = result[0][1].split("_",1)[-1]
        label.props.ellipsize = Pango.EllipsizeMode.END
        v.pack_start(label,True,True,0)
        v.pack_start(h,True,True,0)
        v1 = Gtk.VBox()
        v2 = Gtk.VBox()
        v3 = Gtk.VBox()
        #ggg = GstWidget(result[0][-1],self) # fix later
        #v1.pack_start(ggg,False,False,0)
        h.pack_start(v1,False,False,0)
        store = Gtk.ListStore(str,str,str,str,str)
        for i in result:
            store.append(i)
        
        combo = Gtk.ComboBoxText.new()
        combo.set_model(store)
        combo.set_entry_text_column(0)
        combo.set_active(0)
        close_button = Gtk.Button()
        close_button.props.label = _("Remove Task")
        button = Gtk.Button()
        button.props.label = _("Download")
        cancel_button = Gtk.Button()
        cancel_button.props.label = _("Cancel")
        cancel_button.set_sensitive(False)
        v2.pack_start(combo,True,False,0)
        v2.pack_start(close_button,True,False,0)
        v3.pack_start(button,True,False,0)
        v3.pack_start(cancel_button,True,False,0)
        h.pack_start(v2,False,False,0)
        h.pack_start(v3,False,False,0)
        progb = Gtk.ProgressBar()
        progb.set_show_text(True)
        progb.set_margin_bottom(10)
        v.pack_start(progb,True,True,0)
        button.connect("clicked",self.on_download,progb,store,combo,cancel_button,close_button)
        close_button.connect("clicked",self.on_close,row,result)
        self.show_all()
        progb.hide()
        
    def on_close(self,button,row,result):
        check = YesOrNo(_("Are You Sure You Want To Remove This Task?"),self)
        check = check.check()
        if  not check:
            return

        self.listbox.remove(row)
        row.destroy()
        self.config__["current_links"].remove(result)
        change_metadata_info(self.config__)

        
    def on_download(self,button,progressbar,store,combo,cancel_button,close_button):
        mode = "wb"
        saveas_location = os.path.join(self.choicefolder.get_uri()[7:],store[combo.get_active_iter()][1])

        if  os.path.exists(saveas_location):
            if os.stat(saveas_location).st_size == int(store[combo.get_active_iter()][4]):
                progressbar.set_text("{} Already Exists".format(saveas_location))
                progressbar.show()
                return
            yn = DownloadYesOrNo(_("{} Already Exists".format(saveas_location)),self)
            check = yn.check()
            if  check=="cancel":
                return
            elif check=="resume":
                mode = "ab"

                
        t = DownloadFile(self,progressbar,button,store[combo.get_active_iter()][2],self.choicefolder.get_uri()[7:],store[combo.get_active_iter()][1],store[combo.get_active_iter()][4],cancel_button,close_button,mode)
        t.setDaemon(True)
        cancel_button.connect("clicked",self.on_cancel_button_clicked,t)
        cancel_button.set_sensitive(True)
        t.start()
        
    def on_cancel_button_clicked(self,button,t):
        t.emit("break")
        button.set_sensitive(False)
        

        
class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id=appid,
                         flags=Gio.ApplicationFlags(0),
                         **kwargs)
        self.window = None
        
    def do_startup(self):
        Gtk.Application.do_startup(self)
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)
        builder = Gtk.Builder.new_from_string(MENU_XML, -1)
        self.set_app_menu(builder.get_object("app-menu"))
        
    def do_activate(self):
        if not self.window:
            self.window = FBDownloader(application=self, title=appwindowtitle)
            self.window.connect("delete-event",self.on_quit)
        self.window.present()

    def on_quit(self, action, param=None):
        if threading.active_count()>1:
            check = YesOrNo(_("Tasks Running In Background,Are You Sure You Want To Exit?"),self.window)
            check = check.check()
            if  check:
                self.quit()
            else:
                return True
                    
        self.window.config__["current_save_location"] = self.window.choicefolder.get_uri()[7:]
        change_metadata_info(self.window.config__)
        self.quit()

    def on_about(self,a,p):
        about = Gtk.AboutDialog(parent=self.window,transient_for=self.window, modal=True)
        about.set_program_name(appwindowtitle)
        about.set_version(version_)
        about.set_copyright(copyright_)
        about.set_comments(comments_)
        about.set_website(website_)
        if icon_:
            logo_=GdkPixbuf.Pixbuf. new_from_file_at_scale(icon_,200,200,True)
            about.set_logo(logo_)
        about.set_authors(authors_)
        about.set_license_type(Gtk.License.GPL_3_0)
        if translators_ != "translator-credits":
            about.set_translator_credits(translators_)
        about.run()
        about.destroy()


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)

