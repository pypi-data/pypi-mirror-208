#  Copyright (c) Kuba Szczodrzyński 2023-1-2.

import json
import sys
import threading
from logging import debug, info
from os import makedirs
from os.path import dirname, isfile, join

import wx
import wx.adv
import wx.xrc
from click import get_app_dir

from ltchiptool.util.logging import LoggingHandler
from ltchiptool.util.lvm import LVM

from .panels.about import AboutPanel
from .panels.base import BasePanel
from .panels.flash import FlashPanel
from .panels.log import LogPanel
from .panels.upk import UpkPanel
from .utils import with_target


# noinspection PyPep8Naming
class MainFrame(wx.Frame):
    panels: dict[str, BasePanel]
    init_params: dict

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        sys.excepthook = self.OnException
        threading.excepthook = self.OnException
        LoggingHandler.get().exception_hook = self.ShowExceptionMessage

        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            xrc = join(sys._MEIPASS, "ltchiptool.xrc")
            icon = join(sys._MEIPASS, "ltchiptool.ico")
        else:
            xrc = join(dirname(__file__), "ltchiptool.xrc")
            icon = join(dirname(__file__), "ltchiptool.ico")

        try:
            with open(xrc, "r") as f:
                xrc_str = f.read()
                xrc_str = xrc_str.replace("<object>", '<object class="notebookpage">')
            res = wx.xrc.XmlResource()
            res.LoadFromBuffer(xrc_str.encode())
        except SystemError:
            raise FileNotFoundError(f"Couldn't load the layout file '{xrc}'")

        try:
            # try to find LT directory or local data snapshot
            LVM.get().require_version()
        except Exception as e:
            wx.MessageBox(message=str(e), caption="Error", style=wx.ICON_ERROR)
            wx.Exit()
            return

        self.config_file = join(get_app_dir("ltchiptool"), "config.json")
        self.loaded = False
        self.panels = {}
        self.init_params = {}

        # initialize logging
        self.Log = LogPanel(res, self)
        self.panels["log"] = self.Log
        # main window layout
        self.Notebook = wx.Notebook(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.Notebook, flag=wx.EXPAND)
        sizer.Add(self.Log, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)

        try:
            self.SetMenuBar(res.LoadMenuBar("MainMenuBar"))

            self.Flash = FlashPanel(res, self.Notebook)
            self.panels["flash"] = self.Flash
            self.Notebook.AddPage(self.Flash, "Flashing")

            self.Upk = UpkPanel(res, self.Notebook)
            self.panels["upk"] = self.Upk
            self.Notebook.AddPage(self.Upk, "UPK2ESPHome")

            self.About = AboutPanel(res, self.Notebook)
            self.panels["about"] = self.About
            self.Notebook.AddPage(self.About, "About")

            self.loaded = True
        except Exception as e:
            LoggingHandler.get().emit_exception(e)

        self.Bind(wx.EVT_SHOW, self.OnShow)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_MENU, self.OnMenu)

        self.SetSize((700, 800))
        self.SetMinSize((600, 700))
        self.SetIcon(wx.Icon(icon, wx.BITMAP_TYPE_ICO))
        self.CreateStatusBar()

    @property
    def _settings(self) -> dict:
        if not isfile(self.config_file):
            return dict()
        with open(self.config_file, "r") as f:
            return json.load(f)

    @_settings.setter
    def _settings(self, value: dict):
        makedirs(dirname(self.config_file), exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(value, f, indent="\t")

    # noinspection PyPropertyAccess
    def GetSettings(self) -> dict:
        pos: wx.Point = self.GetPosition()
        size: wx.Size = self.GetSize()
        page: int = self.Notebook.GetSelection()
        return dict(
            pos=[pos.x, pos.y],
            size=[size.x, size.y],
            page=page,
        )

    def SetSettings(
        self,
        pos: tuple[int, int] = None,
        size: tuple[int, int] = None,
        page: int = None,
        **_,
    ):
        if pos:
            self.SetPosition(pos)
        if size:
            self.SetSize(size)
        if page is not None:
            self.Notebook.SetSelection(page)

    @staticmethod
    def OnException(*args):
        if isinstance(args[0], type):
            LoggingHandler.get().emit_exception(args[1])
        else:
            LoggingHandler.get().emit_exception(args[0].exc_value)

    @staticmethod
    def ShowExceptionMessage(e):
        wx.MessageBox(
            message=str(e),
            caption="Error",
            style=wx.ICON_ERROR,
        )

    def OnShow(self, *_):
        settings = self._settings
        self.SetSettings(**settings.get("main", {}))
        for name, panel in self.panels.items():
            panel.SetSettings(**settings.get(name, {}))
            panel.SetInitParams(**self.init_params)
        if settings:
            info(f"Loaded settings from {self.config_file}")
        for name, panel in self.panels.items():
            panel.OnShow()

    def OnClose(self, *_):
        if not self.loaded:
            # avoid writing partial settings in case of loading failure
            self.Destroy()
            return
        settings = dict(
            main=self.GetSettings(),
        )
        for name, panel in self.panels.items():
            panel.OnClose()
            settings[name] = panel.GetSettings() or {}
        self._settings = settings
        info(f"Saved settings to {self.config_file}")
        self.Destroy()

    @with_target
    def OnMenu(self, event: wx.CommandEvent, target: wx.Menu):
        if not isinstance(target, wx.Menu):
            # apparently EVT_MENU fires on certain key-presses too
            return
        item: wx.MenuItem = target.FindItemById(event.GetId())
        if not item:
            return
        title = target.GetTitle()
        label = item.GetItemLabel()
        checked = item.IsChecked() if item.IsCheckable() else False

        match (title, label):
            case ("File", "Quit"):
                self.Close(True)

            case ("Debug", "Print settings"):
                debug(f"Main settings: {self.GetSettings()}")
                for name, panel in self.panels.items():
                    debug(f"Panel '{name}' settings: {panel.GetSettings()}")

            case _:
                for panel in self.panels.values():
                    panel.OnMenu(title, label, checked)
