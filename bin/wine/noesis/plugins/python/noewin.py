import noesis
from ctypes import windll, Structure, sizeof, WINFUNCTYPE, pointer, byref, c_uint, c_int, c_long, c_ushort, c_char, create_unicode_buffer, cast, POINTER
from ctypes.wintypes import HWND, HANDLE, HBRUSH, LPCWSTR, WPARAM, LPARAM, MSG, RECT, POINT

def registerNoesisTypes():
	noesis.registerCleanupFunction(destroyAllWindows)
	return 1

SW_HIDE             = 0
SW_SHOWNORMAL       = 1
SW_NORMAL           = 1
SW_SHOWMINIMIZED    = 2
SW_SHOWMAXIMIZED    = 3
SW_MAXIMIZE         = 3
SW_SHOWNOACTIVATE   = 4
SW_SHOW             = 5
SW_MINIMIZE         = 6
SW_SHOWMINNOACTIVE  = 7
SW_SHOWNA           = 8
SW_RESTORE          = 9
SW_SHOWDEFAULT      = 10
SW_FORCEMINIMIZE    = 11
SW_MAX              = 11

CS_VREDRAW          = 0x0001
CS_HREDRAW          = 0x0002
CS_DBLCLKS          = 0x0008
CS_OWNDC            = 0x0020
CS_CLASSDC          = 0x0040
CS_PARENTDC         = 0x0080
CS_NOCLOSE          = 0x0200
CS_SAVEBITS         = 0x0800
CS_BYTEALIGNCLIENT  = 0x1000
CS_BYTEALIGNWINDOW  = 0x2000
CS_GLOBALCLASS      = 0x4000
CS_IME              = 0x00010000
CS_DROPSHADOW       = 0x00020000

WS_OVERLAPPED       = 0x00000000
WS_POPUP            = 0x80000000
WS_CHILD            = 0x40000000
WS_MINIMIZE         = 0x20000000
WS_VISIBLE          = 0x10000000
WS_DISABLED         = 0x08000000
WS_CLIPSIBLINGS     = 0x04000000
WS_CLIPCHILDREN     = 0x02000000
WS_MAXIMIZE         = 0x01000000
WS_CAPTION          = 0x00C00000
WS_BORDER           = 0x00800000
WS_DLGFRAME         = 0x00400000
WS_VSCROLL          = 0x00200000
WS_HSCROLL          = 0x00100000
WS_SYSMENU          = 0x00080000
WS_THICKFRAME       = 0x00040000
WS_GROUP            = 0x00020000
WS_TABSTOP          = 0x00010000

WS_MINIMIZEBOX      = 0x00020000
WS_MAXIMIZEBOX      = 0x00010000

WS_OVERLAPPEDWINDOW = WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX

WS_TILED            = WS_OVERLAPPED
WS_ICONIC           = WS_MINIMIZE
WS_SIZEBOX          = WS_THICKFRAME
WS_TILEDWINDOW      = WS_OVERLAPPEDWINDOW

WS_POPUPWINDOW      = WS_POPUP | WS_BORDER | WS_SYSMENU

WS_CHILDWINDOW      = WS_CHILD

WS_EX_DLGMODALFRAME     = 0x00000001
WS_EX_NOPARENTNOTIFY    = 0x00000004
WS_EX_TOPMOST           = 0x00000008
WS_EX_ACCEPTFILES       = 0x00000010
WS_EX_TRANSPARENT       = 0x00000020
WS_EX_MDICHILD          = 0x00000040
WS_EX_TOOLWINDOW        = 0x00000080
WS_EX_WINDOWEDGE        = 0x00000100
WS_EX_CLIENTEDGE        = 0x00000200
WS_EX_CONTEXTHELP       = 0x00000400
WS_EX_RIGHT             = 0x00001000
WS_EX_LEFT              = 0x00000000
WS_EX_RTLREADING        = 0x00002000
WS_EX_LTRREADING        = 0x00000000
WS_EX_LEFTSCROLLBAR     = 0x00004000
WS_EX_RIGHTSCROLLBAR    = 0x00000000
WS_EX_CONTROLPARENT     = 0x00010000
WS_EX_STATICEDGE        = 0x00020000
WS_EX_APPWINDOW         = 0x00040000
WS_EX_OVERLAPPEDWINDOW  = WS_EX_WINDOWEDGE | WS_EX_CLIENTEDGE
WS_EX_PALETTEWINDOW     = WS_EX_WINDOWEDGE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST
WS_EX_LAYERED           = 0x00080000
WS_EX_NOINHERITLAYOUT   = 0x00100000
WS_EX_LAYOUTRTL         = 0x00400000
WS_EX_COMPOSITED        = 0x02000000
WS_EX_NOACTIVATE        = 0x08000000

CW_USEDEFAULT       = 0x80000000

GWL_WNDPROC         = -4
GWL_HINSTANCE       = -6
GWL_HWNDPARENT      = -8
GWL_STYLE           = -16
GWL_EXSTYLE         = -20
GWL_USERDATA        = -21
GWL_ID              = -12

WHITE_BRUSH         = 0
LTGRAY_BRUSH        = 1
GRAY_BRUSH          = 2
DKGRAY_BRUSH        = 3
BLACK_BRUSH         = 4
NULL_BRUSH          = 5
HOLLOW_BRUSH        = NULL_BRUSH
WHITE_PEN           = 6
BLACK_PEN           = 7
NULL_PEN            = 8
OEM_FIXED_FONT      = 10
ANSI_FIXED_FONT     = 11
ANSI_VAR_FONT       = 12
SYSTEM_FONT         = 13
DEVICE_DEFAULT_FONT = 14
DEFAULT_PALETTE     = 15
SYSTEM_FIXED_FONT   = 16
DEFAULT_GUI_FONT    = 17
DC_BRUSH            = 18
DC_PEN              = 19

WM_NULL                         = 0x0000
WM_CREATE                       = 0x0001
WM_DESTROY                      = 0x0002
WM_MOVE                         = 0x0003
WM_SIZE                         = 0x0005
WM_ACTIVATE                     = 0x0006
WM_SETFOCUS                     = 0x0007
WM_KILLFOCUS                    = 0x0008
WM_ENABLE                       = 0x000A
WM_SETREDRAW                    = 0x000B
WM_SETTEXT                      = 0x000C
WM_GETTEXT                      = 0x000D
WM_GETTEXTLENGTH                = 0x000E
WM_PAINT                        = 0x000F
WM_CLOSE                        = 0x0010
WM_QUERYENDSESSION              = 0x0011
WM_QUERYOPEN                    = 0x0013
WM_ENDSESSION                   = 0x0016
WM_QUIT                         = 0x0012
WM_ERASEBKGND                   = 0x0014
WM_SYSCOLORCHANGE               = 0x0015
WM_SHOWWINDOW                   = 0x0018
WM_WININICHANGE                 = 0x001A
WM_SETTINGCHANGE                = WM_WININICHANGE
WM_DEVMODECHANGE                = 0x001B
WM_ACTIVATEAPP                  = 0x001C
WM_FONTCHANGE                   = 0x001D
WM_TIMECHANGE                   = 0x001E
WM_CANCELMODE                   = 0x001F
WM_SETCURSOR                    = 0x0020
WM_MOUSEACTIVATE                = 0x0021
WM_CHILDACTIVATE                = 0x0022
WM_QUEUESYNC                    = 0x0023
WM_GETMINMAXINFO                = 0x0024
WM_PAINTICON                    = 0x0026
WM_ICONERASEBKGND               = 0x0027
WM_NEXTDLGCTL                   = 0x0028
WM_SPOOLERSTATUS                = 0x002A
WM_DRAWITEM                     = 0x002B
WM_MEASUREITEM                  = 0x002C
WM_DELETEITEM                   = 0x002D
WM_VKEYTOITEM                   = 0x002E
WM_CHARTOITEM                   = 0x002F
WM_SETFONT                      = 0x0030
WM_GETFONT                      = 0x0031
WM_SETHOTKEY                    = 0x0032
WM_GETHOTKEY                    = 0x0033
WM_QUERYDRAGICON                = 0x0037
WM_COMPAREITEM                  = 0x0039
WM_GETOBJECT                    = 0x003D
WM_COMPACTING                   = 0x0041
WM_COMMNOTIFY                   = 0x0044
WM_WINDOWPOSCHANGING            = 0x0046
WM_WINDOWPOSCHANGED             = 0x0047
WM_POWER                        = 0x0048
WM_COPYDATA                     = 0x004A
WM_CANCELJOURNAL                = 0x004B
WM_NOTIFY                       = 0x004E
WM_INPUTLANGCHANGEREQUEST       = 0x0050
WM_INPUTLANGCHANGE              = 0x0051
WM_TCARD                        = 0x0052
WM_HELP                         = 0x0053
WM_USERCHANGED                  = 0x0054
WM_NOTIFYFORMAT                 = 0x0055
WM_CONTEXTMENU                  = 0x007B
WM_STYLECHANGING                = 0x007C
WM_STYLECHANGED                 = 0x007D
WM_DISPLAYCHANGE                = 0x007E
WM_GETICON                      = 0x007F
WM_SETICON                      = 0x0080
WM_NCCREATE                     = 0x0081
WM_NCDESTROY                    = 0x0082
WM_NCCALCSIZE                   = 0x0083
WM_NCHITTEST                    = 0x0084
WM_NCPAINT                      = 0x0085
WM_NCACTIVATE                   = 0x0086
WM_GETDLGCODE                   = 0x0087
WM_SYNCPAINT                    = 0x0088
WM_NCMOUSEMOVE                  = 0x00A0
WM_NCLBUTTONDOWN                = 0x00A1
WM_NCLBUTTONUP                  = 0x00A2
WM_NCLBUTTONDBLCLK              = 0x00A3
WM_NCRBUTTONDOWN                = 0x00A4
WM_NCRBUTTONUP                  = 0x00A5
WM_NCRBUTTONDBLCLK              = 0x00A6
WM_NCMBUTTONDOWN                = 0x00A7
WM_NCMBUTTONUP                  = 0x00A8
WM_NCMBUTTONDBLCLK              = 0x00A9
WM_NCXBUTTONDOWN                = 0x00AB
WM_NCXBUTTONUP                  = 0x00AC
WM_NCXBUTTONDBLCLK              = 0x00AD
WM_INPUT_DEVICE_CHANGE          = 0x00FE
WM_INPUT                        = 0x00FF
WM_KEYFIRST                     = 0x0100
WM_KEYDOWN                      = 0x0100
WM_KEYUP                        = 0x0101
WM_CHAR                         = 0x0102
WM_DEADCHAR                     = 0x0103
WM_SYSKEYDOWN                   = 0x0104
WM_SYSKEYUP                     = 0x0105
WM_SYSCHAR                      = 0x0106
WM_SYSDEADCHAR                  = 0x0107
WM_UNICHAR                      = 0x0109
#WM_KEYLAST                      = 0x0109
#WM_KEYLAST                      = 0x0108
WM_IME_STARTCOMPOSITION         = 0x010D
WM_IME_ENDCOMPOSITION           = 0x010E
WM_IME_COMPOSITION              = 0x010F
WM_IME_KEYLAST                  = 0x010F
WM_INITDIALOG                   = 0x0110
WM_COMMAND                      = 0x0111
WM_SYSCOMMAND                   = 0x0112
WM_TIMER                        = 0x0113
WM_HSCROLL                      = 0x0114
WM_VSCROLL                      = 0x0115
WM_INITMENU                     = 0x0116
WM_INITMENUPOPUP                = 0x0117
WM_GESTURE                      = 0x0119
WM_GESTURENOTIFY                = 0x011A
WM_MENUSELECT                   = 0x011F
WM_MENUCHAR                     = 0x0120
WM_ENTERIDLE                    = 0x0121
WM_MENURBUTTONUP                = 0x0122
WM_MENUDRAG                     = 0x0123
WM_MENUGETOBJECT                = 0x0124
WM_UNINITMENUPOPUP              = 0x0125
WM_MENUCOMMAND                  = 0x0126
WM_CHANGEUISTATE                = 0x0127
WM_UPDATEUISTATE                = 0x0128
WM_QUERYUISTATE                 = 0x0129
WM_CTLCOLORMSGBOX               = 0x0132
WM_CTLCOLOREDIT                 = 0x0133
WM_CTLCOLORLISTBOX              = 0x0134
WM_CTLCOLORBTN                  = 0x0135
WM_CTLCOLORDLG                  = 0x0136
WM_CTLCOLORSCROLLBAR            = 0x0137
WM_CTLCOLORSTATIC               = 0x0138
MN_GETHMENU                     = 0x01E1
WM_MOUSEFIRST                   = 0x0200
WM_MOUSEMOVE                    = 0x0200
WM_LBUTTONDOWN                  = 0x0201
WM_LBUTTONUP                    = 0x0202
WM_LBUTTONDBLCLK                = 0x0203
WM_RBUTTONDOWN                  = 0x0204
WM_RBUTTONUP                    = 0x0205
WM_RBUTTONDBLCLK                = 0x0206
WM_MBUTTONDOWN                  = 0x0207
WM_MBUTTONUP                    = 0x0208
WM_MBUTTONDBLCLK                = 0x0209
WM_MOUSEWHEEL                   = 0x020A
WM_XBUTTONDOWN                  = 0x020B
WM_XBUTTONUP                    = 0x020C
WM_XBUTTONDBLCLK                = 0x020D
WM_MOUSEHWHEEL                  = 0x020E
#WM_MOUSELAST                    = 0x020E
#WM_MOUSELAST                    = 0x020D
#WM_MOUSELAST                    = 0x020A
#WM_MOUSELAST                    = 0x0209
WM_PARENTNOTIFY                 = 0x0210
WM_ENTERMENULOOP                = 0x0211
WM_EXITMENULOOP                 = 0x0212
WM_NEXTMENU                     = 0x0213
WM_SIZING                       = 0x0214
WM_CAPTURECHANGED               = 0x0215
WM_MOVING                       = 0x0216
WM_POWERBROADCAST               = 0x0218
WM_USER                         = 0x0400

CB_GETEDITSEL               = 0x0140
CB_LIMITTEXT                = 0x0141
CB_SETEDITSEL               = 0x0142
CB_ADDSTRING                = 0x0143
CB_DELETESTRING             = 0x0144
CB_DIR                      = 0x0145
CB_GETCOUNT                 = 0x0146
CB_GETCURSEL                = 0x0147
CB_GETLBTEXT                = 0x0148
CB_GETLBTEXTLEN             = 0x0149
CB_INSERTSTRING             = 0x014A
CB_RESETCONTENT             = 0x014B
CB_FINDSTRING               = 0x014C
CB_SELECTSTRING             = 0x014D
CB_SETCURSEL                = 0x014E
CB_SHOWDROPDOWN             = 0x014F
CB_GETITEMDATA              = 0x0150
CB_SETITEMDATA              = 0x0151
CB_GETDROPPEDCONTROLRECT    = 0x0152
CB_SETITEMHEIGHT            = 0x0153
CB_GETITEMHEIGHT            = 0x0154
CB_SETEXTENDEDUI            = 0x0155
CB_GETEXTENDEDUI            = 0x0156
CB_GETDROPPEDSTATE          = 0x0157
CB_FINDSTRINGEXACT          = 0x0158
CB_SETLOCALE                = 0x0159
CB_GETLOCALE                = 0x015A
CB_GETTOPINDEX              = 0x015b
CB_SETTOPINDEX              = 0x015c
CB_GETHORIZONTALEXTENT      = 0x015d
CB_SETHORIZONTALEXTENT      = 0x015e
CB_GETDROPPEDWIDTH          = 0x015f
CB_SETDROPPEDWIDTH          = 0x0160
CB_INITSTORAGE              = 0x0161
CB_MULTIPLEADDSTRING        = 0x0163
CB_GETCOMBOBOXINFO          = 0x0164

CBN_ERRSPACE        = -1
CBN_SELCHANGE       = 1
CBN_DBLCLK          = 2
CBN_SETFOCUS        = 3
CBN_KILLFOCUS       = 4
CBN_EDITCHANGE      = 5
CBN_EDITUPDATE      = 6
CBN_DROPDOWN        = 7
CBN_CLOSEUP         = 8
CBN_SELENDOK        = 9
CBN_SELENDCANCEL    = 10

BST_UNCHECKED      = 0x0000
BST_CHECKED        = 0x0001
BST_INDETERMINATE  = 0x0002
BST_PUSHED         = 0x0004
BST_FOCUS          = 0x0008

BS_PUSHBUTTON       = 0x00000000
BS_DEFPUSHBUTTON    = 0x00000001
BS_CHECKBOX         = 0x00000002
BS_AUTOCHECKBOX     = 0x00000003
BS_RADIOBUTTON      = 0x00000004
BS_3STATE           = 0x00000005
BS_AUTO3STATE       = 0x00000006
BS_GROUPBOX         = 0x00000007
BS_USERBUTTON       = 0x00000008
BS_AUTORADIOBUTTON  = 0x00000009
BS_PUSHBOX          = 0x0000000A
BS_OWNERDRAW        = 0x0000000B
BS_TYPEMASK         = 0x0000000F
BS_LEFTTEXT         = 0x00000020
BS_TEXT             = 0x00000000
BS_ICON             = 0x00000040
BS_BITMAP           = 0x00000080
BS_LEFT             = 0x00000100
BS_RIGHT            = 0x00000200
BS_CENTER           = 0x00000300
BS_TOP              = 0x00000400
BS_BOTTOM           = 0x00000800
BS_VCENTER          = 0x00000C00
BS_PUSHLIKE         = 0x00001000
BS_MULTILINE        = 0x00002000
BS_NOTIFY           = 0x00004000
BS_FLAT             = 0x00008000
BS_RIGHTBUTTON      = BS_LEFTTEXT

ES_LEFT             = 0x0000
ES_CENTER           = 0x0001
ES_RIGHT            = 0x0002
ES_MULTILINE        = 0x0004
ES_UPPERCASE        = 0x0008
ES_LOWERCASE        = 0x0010
ES_PASSWORD         = 0x0020
ES_AUTOVSCROLL      = 0x0040
ES_AUTOHSCROLL      = 0x0080
ES_NOHIDESEL        = 0x0100
ES_OEMCONVERT       = 0x0400
ES_READONLY         = 0x0800
ES_WANTRETURN       = 0x1000
ES_NUMBER           = 0x2000

EN_SETFOCUS         = 0x0100
EN_KILLFOCUS        = 0x0200
EN_CHANGE           = 0x0300
EN_UPDATE           = 0x0400
EN_ERRSPACE         = 0x0500
EN_MAXTEXT          = 0x0501
EN_HSCROLL          = 0x0601
EN_VSCROLL          = 0x0602

CBS_SIMPLE            = 0x0001
CBS_DROPDOWN          = 0x0002
CBS_DROPDOWNLIST      = 0x0003
CBS_OWNERDRAWFIXED    = 0x0010
CBS_OWNERDRAWVARIABLE = 0x0020
CBS_AUTOHSCROLL       = 0x0040
CBS_OEMCONVERT        = 0x0080
CBS_SORT              = 0x0100
CBS_HASSTRINGS        = 0x0200
CBS_NOINTEGRALHEIGHT  = 0x0400
CBS_DISABLENOSCROLL   = 0x0800
CBS_UPPERCASE         = 0x2000
CBS_LOWERCASE         = 0x4000

LB_ADDSTRING            = 0x0180
LB_INSERTSTRING         = 0x0181
LB_DELETESTRING         = 0x0182
LB_SELITEMRANGEEX       = 0x0183
LB_RESETCONTENT         = 0x0184
LB_SETSEL               = 0x0185
LB_SETCURSEL            = 0x0186
LB_GETSEL               = 0x0187
LB_GETCURSEL            = 0x0188
LB_GETTEXT              = 0x0189
LB_GETTEXTLEN           = 0x018A
LB_GETCOUNT             = 0x018B
LB_SELECTSTRING         = 0x018C
LB_DIR                  = 0x018D
LB_GETTOPINDEX          = 0x018E
LB_FINDSTRING           = 0x018F
LB_GETSELCOUNT          = 0x0190
LB_GETSELITEMS          = 0x0191
LB_SETTABSTOPS          = 0x0192
LB_GETHORIZONTALEXTENT  = 0x0193
LB_SETHORIZONTALEXTENT  = 0x0194
LB_SETCOLUMNWIDTH       = 0x0195
LB_ADDFILE              = 0x0196
LB_SETTOPINDEX          = 0x0197
LB_GETITEMRECT          = 0x0198
LB_GETITEMDATA          = 0x0199
LB_SETITEMDATA          = 0x019A
LB_SELITEMRANGE         = 0x019B
LB_SETANCHORINDEX       = 0x019C
LB_GETANCHORINDEX       = 0x019D
LB_SETCARETINDEX        = 0x019E
LB_GETCARETINDEX        = 0x019F
LB_SETITEMHEIGHT        = 0x01A0
LB_GETITEMHEIGHT        = 0x01A1
LB_FINDSTRINGEXACT      = 0x01A2
LB_SETLOCALE            = 0x01A5
LB_GETLOCALE            = 0x01A6
LB_SETCOUNT             = 0x01A7
LB_INITSTORAGE          = 0x01A8
LB_ITEMFROMPOINT        = 0x01A9
LB_MULTIPLEADDSTRING    = 0x01B1

LBS_NOTIFY            = 0x0001
LBS_SORT              = 0x0002
LBS_NOREDRAW          = 0x0004
LBS_MULTIPLESEL       = 0x0008
LBS_OWNERDRAWFIXED    = 0x0010
LBS_OWNERDRAWVARIABLE = 0x0020
LBS_HASSTRINGS        = 0x0040
LBS_USETABSTOPS       = 0x0080
LBS_NOINTEGRALHEIGHT  = 0x0100
LBS_MULTICOLUMN       = 0x0200
LBS_WANTKEYBOARDINPUT = 0x0400
LBS_EXTENDEDSEL       = 0x0800
LBS_DISABLENOSCROLL   = 0x1000
LBS_NODATA            = 0x2000
LBS_NOSEL             = 0x4000
LBS_COMBOBOX          = 0x8000
LBS_STANDARD          = LBS_NOTIFY | LBS_SORT | WS_VSCROLL | WS_BORDER

LBN_ERRSPACE        = -2
LBN_SELCHANGE       = 1
LBN_DBLCLK          = 2
LBN_SELCANCEL       = 3
LBN_SETFOCUS        = 4
LBN_KILLFOCUS       = 5

SBS_HORZ                    = 0x0000
SBS_VERT                    = 0x0001
SBS_TOPALIGN                = 0x0002
SBS_LEFTALIGN               = 0x0002
SBS_BOTTOMALIGN             = 0x0004
SBS_RIGHTALIGN              = 0x0004
SBS_SIZEBOXTOPLEFTALIGN     = 0x0002
SBS_SIZEBOXBOTTOMRIGHTALIGN = 0x0004
SBS_SIZEBOX                 = 0x0008
SBS_SIZEGRIP                = 0x0010

BM_GETCHECK                 = 0x00F0
BM_SETCHECK                 = 0x00F1
BM_GETSTATE                 = 0x00F2
BM_SETSTATE                 = 0x00F3
BM_SETSTYLE                 = 0x00F4
BM_CLICK                    = 0x00F5

SBM_SETPOS                  = 0x00E0
SBM_GETPOS                  = 0x00E1
SBM_SETRANGE                = 0x00E2
SBM_SETRANGEREDRAW          = 0x00E6
SBM_GETRANGE                = 0x00E3
SBM_ENABLE_ARROWS           = 0x00E4
SBM_SETSCROLLINFO           = 0x00E9
SBM_GETSCROLLINFO           = 0x00EA
SBM_GETSCROLLBARINFO        = 0x00EB

SIF_RANGE           = 0x0001
SIF_PAGE            = 0x0002
SIF_POS             = 0x0004
SIF_DISABLENOSCROLL = 0x0008
SIF_TRACKPOS        = 0x0010
SIF_ALL             = SIF_RANGE | SIF_PAGE | SIF_POS | SIF_TRACKPOS

SB_HORZ             = 0
SB_VERT             = 1
SB_CTL              = 2
SB_BOTH             = 3

SB_LINEUP           = 0
SB_LINELEFT         = 0
SB_LINEDOWN         = 1
SB_LINERIGHT        = 1
SB_PAGEUP           = 2
SB_PAGELEFT         = 2
SB_PAGEDOWN         = 3
SB_PAGERIGHT        = 3
SB_THUMBPOSITION    = 4
SB_THUMBTRACK       = 5
SB_TOP              = 6
SB_LEFT             = 6
SB_BOTTOM           = 7
SB_RIGHT            = 7
SB_ENDSCROLL        = 8

ESB_ENABLE_BOTH     = 0x0000
ESB_DISABLE_BOTH    = 0x0003
ESB_DISABLE_LEFT    = 0x0001
ESB_DISABLE_RIGHT   = 0x0002
ESB_DISABLE_UP      = 0x0001
ESB_DISABLE_DOWN    = 0x0002
ESB_DISABLE_LTUP    = ESB_DISABLE_LEFT
ESB_DISABLE_RTDN    = ESB_DISABLE_RIGHT

DT_TOP                      = 0x00000000
DT_LEFT                     = 0x00000000
DT_CENTER                   = 0x00000001
DT_RIGHT                    = 0x00000002
DT_VCENTER                  = 0x00000004
DT_BOTTOM                   = 0x00000008
DT_WORDBREAK                = 0x00000010
DT_SINGLELINE               = 0x00000020
DT_EXPANDTABS               = 0x00000040
DT_TABSTOP                  = 0x00000080
DT_NOCLIP                   = 0x00000100
DT_EXTERNALLEADING          = 0x00000200
DT_CALCRECT                 = 0x00000400
DT_NOPREFIX                 = 0x00000800
DT_INTERNAL                 = 0x00001000
DT_EDITCONTROL              = 0x00002000
DT_PATH_ELLIPSIS            = 0x00004000
DT_END_ELLIPSIS             = 0x00008000
DT_MODIFYSTRING             = 0x00010000
DT_RTLREADING               = 0x00020000
DT_WORD_ELLIPSIS            = 0x00040000
DT_NOFULLWIDTHCHARBREAK     = 0x00080000
DT_HIDEPREFIX               = 0x00100000
DT_PREFIXONLY               = 0x00200000

FF_DONTCARE         = (0<<4)
FF_ROMAN            = (1<<4)
FF_SWISS            = (2<<4)
FF_MODERN           = (3<<4)
FF_SCRIPT           = (4<<4)
FF_DECORATIVE       = (5<<4)

FW_DONTCARE         = 0
FW_THIN             = 100
FW_EXTRALIGHT       = 200
FW_LIGHT            = 300
FW_NORMAL           = 400
FW_MEDIUM           = 500
FW_SEMIBOLD         = 600
FW_BOLD             = 700
FW_EXTRABOLD        = 800
FW_HEAVY            = 900
FW_ULTRALIGHT       = FW_EXTRALIGHT
FW_REGULAR          = FW_NORMAL
FW_DEMIBOLD         = FW_SEMIBOLD
FW_ULTRABOLD        = FW_EXTRABOLD
FW_BLACK            = FW_HEAVY

OUT_DEFAULT_PRECIS          = 0
OUT_STRING_PRECIS           = 1
OUT_CHARACTER_PRECIS        = 2
OUT_STROKE_PRECIS           = 3
OUT_TT_PRECIS               = 4
OUT_DEVICE_PRECIS           = 5
OUT_RASTER_PRECIS           = 6
OUT_TT_ONLY_PRECIS          = 7
OUT_OUTLINE_PRECIS          = 8
OUT_SCREEN_OUTLINE_PRECIS   = 9
OUT_PS_ONLY_PRECIS          = 10
CLIP_DEFAULT_PRECIS     = 0
CLIP_CHARACTER_PRECIS   = 1
CLIP_STROKE_PRECIS      = 2
CLIP_MASK               = 0xf
CLIP_LH_ANGLES          = (1<<4)
CLIP_TT_ALWAYS          = (2<<4)
CLIP_DFA_DISABLE        = (4<<4)
CLIP_EMBEDDED           = (8<<4)
DEFAULT_QUALITY         = 0
DRAFT_QUALITY           = 1
PROOF_QUALITY           = 2
NONANTIALIASED_QUALITY  = 3
ANTIALIASED_QUALITY     = 4
CLEARTYPE_QUALITY       = 5
CLEARTYPE_NATURAL_QUALITY       = 6
DEFAULT_PITCH           = 0
FIXED_PITCH             = 1
VARIABLE_PITCH          = 2
MONO_FONT               = 8

ANSI_CHARSET            = 0
DEFAULT_CHARSET         = 1
SYMBOL_CHARSET          = 2
SHIFTJIS_CHARSET        = 128
HANGEUL_CHARSET         = 129
HANGUL_CHARSET          = 129
GB2312_CHARSET          = 134
CHINESEBIG5_CHARSET     = 136
OEM_CHARSET             = 255

CTLCOLOR_MSGBOX         = 0
CTLCOLOR_EDIT           = 1
CTLCOLOR_LISTBOX        = 2
CTLCOLOR_BTN            = 3
CTLCOLOR_DLG            = 4
CTLCOLOR_SCROLLBAR      = 5
CTLCOLOR_STATIC         = 6
CTLCOLOR_MAX            = 7

COLOR_SCROLLBAR         = 0
COLOR_BACKGROUND        = 1
COLOR_ACTIVECAPTION     = 2
COLOR_INACTIVECAPTION   = 3
COLOR_MENU              = 4
COLOR_WINDOW            = 5
COLOR_WINDOWFRAME       = 6
COLOR_MENUTEXT          = 7
COLOR_WINDOWTEXT        = 8
COLOR_CAPTIONTEXT       = 9
COLOR_ACTIVEBORDER      = 10
COLOR_INACTIVEBORDER    = 11
COLOR_APPWORKSPACE      = 12
COLOR_HIGHLIGHT         = 13
COLOR_HIGHLIGHTTEXT     = 14
COLOR_BTNFACE           = 15
COLOR_BTNSHADOW         = 16
COLOR_GRAYTEXT          = 17
COLOR_BTNTEXT           = 18
COLOR_INACTIVECAPTIONTEXT = 19
COLOR_BTNHIGHLIGHT      = 20
COLOR_3DDKSHADOW        = 21
COLOR_3DLIGHT           = 22
COLOR_INFOTEXT          = 23
COLOR_INFOBK            = 24
COLOR_HOTLIGHT          = 26
COLOR_GRADIENTACTIVECAPTION = 27
COLOR_GRADIENTINACTIVECAPTION = 28
COLOR_MENUHILIGHT       = 29
COLOR_MENUBAR           = 30
COLOR_DESKTOP           = COLOR_BACKGROUND
COLOR_3DFACE            = COLOR_BTNFACE
COLOR_3DSHADOW          = COLOR_BTNSHADOW
COLOR_3DHIGHLIGHT       = COLOR_BTNHIGHLIGHT
COLOR_3DHILIGHT         = COLOR_BTNHIGHLIGHT
COLOR_BTNHILIGHT        = COLOR_BTNHIGHLIGHT

IDC_ARROW           = 32512
IDC_IBEAM           = 32513
IDC_WAIT            = 32514
IDC_CROSS           = 32515
IDC_UPARROW         = 32516
IDC_SIZE            = 32640
IDC_ICON            = 32641
IDC_SIZENWSE        = 32642
IDC_SIZENESW        = 32643
IDC_SIZEWE          = 32644
IDC_SIZENS          = 32645
IDC_SIZEALL         = 32646
IDC_NO              = 32648
IDC_HAND            = 32649
IDC_APPSTARTING     = 32650
IDC_HELP            = 32651
IDI_APPLICATION     = 32512
IDI_HAND            = 32513
IDI_QUESTION        = 32514
IDI_EXCLAMATION     = 32515
IDI_ASTERISK        = 32516
IDI_WINLOGO         = 32517
IDI_SHIELD          = 32518
IDI_WARNING     = IDI_EXCLAMATION
IDI_ERROR       = IDI_HAND
IDI_INFORMATION = IDI_ASTERISK

TRANSPARENT         = 1
OPAQUE              = 2
BKMODE_LAST         = 2

MK_LBUTTON          = 0x0001
MK_RBUTTON          = 0x0002
MK_SHIFT            = 0x0004
MK_CONTROL          = 0x0008
MK_MBUTTON          = 0x0010

VK_BACK             = 0x08
VK_TAB              = 0x09
VK_CLEAR            = 0x0C
VK_RETURN           = 0x0D
VK_SHIFT            = 0x10
VK_CONTROL          = 0x11
VK_MENU             = 0x12
VK_PAUSE            = 0x13
VK_CAPITAL          = 0x14

MB_OK                      = 0x00000000
MB_OKCANCEL                = 0x00000001
MB_ABORTRETRYIGNORE        = 0x00000002
MB_YESNOCANCEL             = 0x00000003
MB_YESNO                   = 0x00000004
MB_RETRYCANCEL             = 0x00000005
MB_CANCELTRYCONTINUE       = 0x00000006
MB_ICONHAND                = 0x00000010
MB_ICONQUESTION            = 0x00000020
MB_ICONEXCLAMATION         = 0x00000030
MB_ICONASTERISK            = 0x00000040

IDOK                = 1
IDCANCEL            = 2
IDABORT             = 3
IDRETRY             = 4
IDIGNORE            = 5
IDYES               = 6
IDNO                = 7
IDCLOSE             = 8
IDHELP              = 9
IDTRYAGAIN          = 10
IDCONTINUE          = 11

DIB_RGB_COLORS      = 0
DIB_PAL_COLORS      = 1

SRCCOPY             = 0x00CC0020 #dest = source
SRCPAINT            = 0x00EE0086 #dest = source OR dest
SRCAND              = 0x008800C6 #dest = source AND dest
SRCINVERT           = 0x00660046 #dest = source XOR dest
SRCERASE            = 0x00440328 #dest = source AND (NOT dest)
NOTSRCCOPY          = 0x00330008 #dest = (NOT source)
NOTSRCERASE         = 0x001100A6 #dest = (NOT src) AND (NOT dest)
MERGECOPY           = 0x00C000CA #dest = (source AND pattern)
MERGEPAINT          = 0x00BB0226 #dest = (NOT source) OR dest
PATCOPY             = 0x00F00021 #dest = pattern
PATPAINT            = 0x00FB0A09 #dest = DPSnoo
PATINVERT           = 0x005A0049 #dest = pattern XOR dest
DSTINVERT           = 0x00550009 #dest = (NOT dest)
BLACKNESS           = 0x00000042 #dest = BLACK
WHITENESS           = 0x00FF0062 #dest = WHITE

def RGB(r,g,b):
	return int(r | (g << 8) | (b << 16))


kernel32 = windll.kernel32
gdi32 = windll.gdi32
user32 = windll.user32

WNDPROCTYPE = WINFUNCTYPE(c_int, HWND, c_uint, WPARAM, LPARAM)

#since we want to keep these objects alive outside of the python scope entirely, we keep a global dict of window handles and associated procs
liveWindows = {}

def getNoeWndForHWnd(hWnd):
	if hWnd in liveWindows:
		return liveWindows[hWnd]
	return None
	
def getNoesisWindowRect():
	hNoesisWnd = noesis.getWindowHandle()
	if hNoesisWnd:
		rect = RECT()
		if user32.GetWindowRect(hNoesisWnd, byref(rect)):
			return (rect.left, rect.top, rect.right, rect.bottom)
	return None

class WNDCLASSEX(Structure):
	_fields_ = [("cbSize", c_uint),
				("style", c_uint),
				("lpfnWndProc", WNDPROCTYPE),
				("cbClsExtra", c_int),
				("cbWndExtra", c_int),
				("hInstance", HANDLE),
				("hIcon", HANDLE),
				("hCursor", HANDLE),
				("hBrush", HBRUSH),
				("lpszMenuName", LPCWSTR),
				("lpszClassName", LPCWSTR),
				("hIconSm", HANDLE)]

class NMHDR(Structure):
	_fields_ = [("hwndFrom", HWND),
				("idFrom", c_uint),
				("code", c_uint)]
LPNMHDR = POINTER(NMHDR)
								
class PAINTSTRUCT(Structure):
	_fields_ = [('hdc', c_int),
				('fErase', c_int),
				('rcPaint', RECT),
				('fRestore', c_int),
				('fIncUpdate', c_int),
				('rgbReserved', c_char * 32)]

class BITMAPINFOHEADER(Structure):
	_fields_ = [("biSize", c_uint),
				("biWidth", c_long),
				("biHeight", c_long),
				("biPlanes", c_ushort),
				("biBitCount", c_ushort),
				("biCompression", c_uint),
				("biSizeImage", c_uint),
				("biXPelsPerMeter", c_long),
				("biYPelsPerMeter", c_long),
				("biClrUsed", c_uint),
				("biClrImportant", c_uint)]

class BITMAPINFO(Structure):
	_fields_ = [("bmiHeader", BITMAPINFOHEADER)]
				
def destroyAllWindows():
	global liveWindows
	for hWnd in liveWindows.keys():
		noeWnd = liveWindows[hWnd]
		noeWnd.freeResources()
	liveWindows = {}

def defaultWindowProc(hWnd, message, wParam, lParam):
	noeWnd = liveWindows[hWnd] if hWnd in liveWindows else None
	if message == WM_CLOSE:
		if noeWnd:
			noeWnd.freeResources()
			del liveWindows[hWnd]
		else:
			#somehow untracked, so just kill it
			user32.DestroyWindow(hWnd)	
		return 0
	elif message == WM_COMMAND:
		if noeWnd:
			controlId = (wParam & 0xFFFF)
			for userControl in noeWnd.userControls:
				if userControl.controlId == controlId and userControl.commandMethod:
					if userControl.commandMethod(noeWnd, userControl.controlId, wParam, lParam):
						return 0
	elif message == WM_CTLCOLORSTATIC:
		#gdi32.SetTextColor(wParam, RGB(0, 255, 0))
		#gdi32.SetBkColor(wParam, RGB(255, 0, 0))
		gdi32.SetBkMode(wParam, TRANSPARENT)
		return 0
	"""
	elif message == WM_NOTIFY:
		nmhdr = cast(lParam, LPNMHDR)[0]
		for userControl in noeWnd.userControls:
			if userControl.controlId == nmhdr.idFrom and userControl.notifyMethod:
				if userControl.notifyMethod(noeWnd, userControl.controlId, nmhdr.code):
					return 0
	"""
	
	r = user32.DefWindowProcW(hWnd, message, wParam, lParam)
	if noeWnd:
		for cb in noeWnd.userCallbacks:
			if cb.message == message:
				cb.method(noeWnd, cb.controlIndex, message, wParam, lParam)
	return r
	
def defaultCheckBoxCommandMethod(noeWnd, controlId, wParam, lParam):
	checkBox = noeWnd.getControlById(controlId)
	checkBox.setChecked(BST_CHECKED if checkBox.isChecked() == 0 else BST_UNCHECKED)

class NoeUserControlBase:
	def __init__(self, noeParentWnd, controlId, x, y, width, height, commandMethod):
		self.noeParentWnd = noeParentWnd
		self.controlId = controlId
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.commandMethod = commandMethod
	
class NoeUserStatic(NoeUserControlBase):
	def __init__(self, noeParentWnd, text, controlId, x, y, width, height):
		super().__init__(noeParentWnd, controlId, x, y, width, height, None)
		self.style = WS_VISIBLE | WS_CHILD
		self.hWnd = user32.CreateWindowExW(0, "STATIC", text, self.style, x, y, width, height, noeParentWnd.hWnd, self.controlId, noeParentWnd.hInst, 0)

class NoeUserButton(NoeUserControlBase):
	def __init__(self, noeParentWnd, name, controlId, x, y, width, height, commandMethod, defaultButton):
		super().__init__(noeParentWnd, controlId, x, y, width, height, commandMethod)
		self.name = name
		self.style = WS_TABSTOP | WS_VISIBLE | WS_CHILD
		if defaultButton:
			self.style |= BS_DEFPUSHBUTTON
		self.hWnd = user32.CreateWindowExW(0, "BUTTON", self.name, self.style, x, y, width, height, noeParentWnd.hWnd, self.controlId, noeParentWnd.hInst, 0)
	def setText(self, text):
		user32.SetWindowTextW(self.hWnd, text)

class NoeUserCheckBox(NoeUserControlBase):
	def __init__(self, noeParentWnd, name, controlId, x, y, width, height, commandMethod):
		super().__init__(noeParentWnd, controlId, x, y, width, height, commandMethod)
		self.name = name
		self.style = WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_CHECKBOX
		self.hWnd = user32.CreateWindowExW(0, "BUTTON", self.name, self.style, x, y, width, height, noeParentWnd.hWnd, self.controlId, noeParentWnd.hInst, 0)
	def isChecked(self):
		return user32.SendMessageW(self.hWnd, BM_GETCHECK, 0, 0)
	def setChecked(self, checkValue):
		user32.SendMessageW(self.hWnd, BM_SETCHECK, checkValue, 0)
		
class NoeUserEditBox(NoeUserControlBase):
	def __init__(self, noeParentWnd, text, controlId, x, y, width, height, isMultiLine, isReadOnly, commandMethod):
		super().__init__(noeParentWnd, controlId, x, y, width, height, commandMethod)
		self.style = WS_TABSTOP | WS_VISIBLE | WS_CHILD | ES_LEFT
		if isMultiLine:
			self.style |= ES_MULTILINE | WS_VSCROLL | ES_AUTOVSCROLL
		if isReadOnly:
			self.style |= ES_READONLY
		self.hWnd = user32.CreateWindowExW(WS_EX_CLIENTEDGE, "EDIT", text, self.style, x, y, width, height, noeParentWnd.hWnd, self.controlId, noeParentWnd.hInst, 0)
	def getText(self):
		l = user32.GetWindowTextLengthW(self.hWnd) + 1
		textBuffer = create_unicode_buffer(l)
		user32.GetWindowTextW(self.hWnd, textBuffer, l)
		return textBuffer.value
	def setText(self, text):
		user32.SetWindowTextW(self.hWnd, text)

class NoeUserComboBox(NoeUserControlBase):
	def __init__(self, noeParentWnd, controlId, x, y, width, height, style, commandMethod):
		super().__init__(noeParentWnd, controlId, x, y, width, height, commandMethod)
		self.style = WS_TABSTOP | WS_VISIBLE | WS_CHILD | WS_VSCROLL | style
		self.hWnd = user32.CreateWindowExW(0, "COMBOBOX", 0, self.style, x, y, width, height, noeParentWnd.hWnd, self.controlId, noeParentWnd.hInst, 0)
	def addString(self, text):
		user32.SendMessageW(self.hWnd, CB_ADDSTRING, 0, text)
	def removeString(self, text):
		textIndex = self.getStringIndex(text)
		if textIndex >= 0:
			user32.SendMessageW(self.hWnd, CB_DELETESTRING, textIndex, 0)
	def selectString(self, text):
		user32.SendMessageW(self.hWnd, CB_SELECTSTRING, -1, text)
	def resetContent(self):
		return user32.SendMessageW(self.hWnd, CB_RESETCONTENT, 0, 0)	
	def getStringIndex(self, text):
		return user32.SendMessageW(self.hWnd, CB_FINDSTRING, -1, text)
	def getSelectionIndex(self):
		return user32.SendMessageW(self.hWnd, CB_GETCURSEL, 0, 0)
	def getStringForIndex(self, index):
		if index < 0:
			return None
		l = user32.SendMessageW(self.hWnd, CB_GETLBTEXTLEN, index, 0) + 1
		textBuffer = create_unicode_buffer(l)
		user32.SendMessageW(self.hWnd, CB_GETLBTEXT, index, textBuffer)
		return textBuffer.value
	def getStringCount(self):
		return user32.SendMessageW(self.hWnd, CB_GETCOUNT, 0, 0)
		
class NoeUserListBox(NoeUserControlBase):
	def __init__(self, noeParentWnd, controlId, x, y, width, height, style, commandMethod):
		super().__init__(noeParentWnd, controlId, x, y, width, height, commandMethod)
		self.style = WS_TABSTOP | WS_VISIBLE | WS_CHILD | WS_VSCROLL | style
		if commandMethod is not None:
			self.style |= LBS_NOTIFY
		self.hWnd = user32.CreateWindowExW(WS_EX_CLIENTEDGE, "LISTBOX", 0, self.style, x, y, width, height, noeParentWnd.hWnd, self.controlId, noeParentWnd.hInst, 0)
	def addString(self, text):
		user32.SendMessageW(self.hWnd, LB_ADDSTRING, 0, text)
	def removeString(self, text):
		textIndex = self.getStringIndex(text)
		if textIndex >= 0:
			user32.SendMessageW(self.hWnd, LB_DELETESTRING, textIndex, 0)
	def selectString(self, text):
		user32.SendMessageW(self.hWnd, LB_SELECTSTRING, -1, text)
	def resetContent(self):
		return user32.SendMessageW(self.hWnd, LB_RESETCONTENT, 0, 0)	
	def getStringIndex(self, text):
		return user32.SendMessageW(self.hWnd, LB_FINDSTRING, -1, text)
	def getSelectionIndex(self):
		return user32.SendMessageW(self.hWnd, LB_GETCURSEL, 0, 0)
	def getStringForIndex(self, index):
		if index < 0:
			return None
		l = user32.SendMessageW(self.hWnd, LB_GETTEXTLEN, index, 0) + 1
		textBuffer = create_unicode_buffer(l)
		user32.SendMessageW(self.hWnd, LB_GETTEXT, index, textBuffer)
		return textBuffer.value
	def getStringCount(self):
		return user32.SendMessageW(self.hWnd, LB_GETCOUNT, 0, 0)
	def getMultiSelectionIndices(self):
		selCount = self.getMultiSelectionCount()
		if selCount <= 0:
			return []
		else:
			selIndices = (c_int * selCount)()
			selCount = user32.SendMessageW(self.hWnd, LB_GETSELITEMS, selCount, byref(selIndices))
			if selCount <= 0:
				return []
			return [selIndices[i] for i in range(0, selCount)]
	def getMultiSelectionCount(self):
		return user32.SendMessageW(self.hWnd, LB_GETSELCOUNT, 0, 0)

class NoeUserScrollBar(NoeUserControlBase):
	def __init__(self, noeParentWnd, controlId, x, y, width, height, isHorizontal, commandMethod):
		super().__init__(noeParentWnd, controlId, x, y, width, height, None)
		self.scrollUpdateMethod = commandMethod #special-case for scrolls, reappropriate the command method
		self.style = WS_TABSTOP | WS_VISIBLE | WS_CHILD | SBS_SIZEBOXBOTTOMRIGHTALIGN
		barStyle = SBS_HORZ if isHorizontal else SBS_VERT
		self.style |= barStyle
		self.hWnd = user32.CreateWindowExW(0, "SCROLLBAR", 0, self.style, x, y, width, height, noeParentWnd.hWnd, self.controlId, noeParentWnd.hInst, 0)
		self.setScrollMinMax(1, 10)
		#user32.SendMessageW(self.hWnd, SBM_ENABLE_ARROWS, ESB_ENABLE_BOTH, 0)
	def setScrollMinMax(self, minVal, maxVal):
		self.minVal = int(minVal)
		self.maxVal = int(maxVal)
		user32.SetScrollRange(self.hWnd, SB_CTL, self.minVal, self.maxVal, 1)
	def setScrollValue(self, val):
		val = min(val, self.maxVal)
		val = max(val, self.minVal)
		user32.SetScrollPos(self.hWnd, SB_CTL, int(val), 1)
	def getScrollValue(self):
		return user32.GetScrollPos(self.hWnd, SB_CTL)
	#typical functionality required for scrollbar handling
	def DefaultScrollCallback(noeWnd, controlIndex, message, wParam, lParam):
		scroll = noeWnd.getControlByIndex(controlIndex)
		if scroll.hWnd == lParam:
			scrollType = (wParam & 0xFFFF)
			oldValue = scroll.getScrollValue()
			if scrollType == SB_THUMBPOSITION or scrollType == SB_THUMBTRACK:
				scrollIndex = (wParam >> 16)
				scroll.setScrollValue(scrollIndex)
			else:
				largeAmount = max(int(scroll.maxVal - scroll.minVal) // 4, 1)
				movement = 0
				if scrollType == SB_LEFT or scrollType == SB_LINELEFT:
					movement = -1
				elif scrollType == SB_RIGHT or scrollType == SB_LINERIGHT:
					movement = 1
				elif scrollType == SB_PAGELEFT:
					movement = -largeAmount
				elif scrollType == SB_PAGERIGHT:
					movement = largeAmount
				
				if movement != 0:
					scroll.setScrollValue(oldValue + movement)
					
			if scroll.scrollUpdateMethod:
				scroll.scrollUpdateMethod(noeWnd, scroll.controlId, oldValue, scroll.getScrollValue(), scrollType)
			return True
			
		return False
	
class NoeUserControlCallback:
	def __init__(self, controlIndex, message, method):
		self.controlIndex = controlIndex
		self.message = message
		self.method = method

class NoeUserWindow:
	def __init__(self, windowName, windowClassName, windowWidth = 0, windowHeight = 0, windowProc = defaultWindowProc, style = WS_CAPTION | WS_SYSMENU, exStyle = WS_EX_TOOLWINDOW):
		self.hWnd = None
		self.hFont = None
		self.windowProc = WNDPROCTYPE(windowProc)
		self.windowName = windowName
		self.windowClassName = windowClassName
		self.hInst = kernel32.GetModuleHandleW(0)
		self.x = CW_USEDEFAULT
		self.y = CW_USEDEFAULT
		self.width = CW_USEDEFAULT if windowWidth <= 0 else windowWidth
		self.height = CW_USEDEFAULT if windowHeight <= 0 else windowHeight
		self.style = WS_CAPTION | WS_SYSMENU | WS_POPUP
		self.exStyle = exStyle
		self.enableParentOnDestruction = False
		self.currentControlId = 100
		self.userControls = []
		self.userCallbacks = []
		self.userIcon = None
		
	def resetContent(self):
		for userControl in self.userControls:
			if userControl.hWnd:
				user32.DestroyWindow(userControl.hWnd)
		self.currentControlId = 100
		self.userControls = []
		self.userCallbacks = []
		
	def doModal(self):
		if self.hParentWnd:
			self.enableParentOnDestruction = True
			user32.EnableWindow(self.hParentWnd, 0)
			
		while self.hWnd:
			msg = MSG()
			pMsg = pointer(msg)
			while self.hWnd and user32.GetMessageW(pMsg, 0, 0, 0) != 0:
				if not user32.IsDialogMessage(self.hWnd, pMsg):
					user32.TranslateMessage(pMsg)
					user32.DispatchMessageW(pMsg)

	def closeWindow(self):
		if self.hWnd in liveWindows:
			del liveWindows[self.hWnd]
		self.freeResources()
		
	def freeResources(self):
		if self.enableParentOnDestruction and self.hParentWnd:
			user32.EnableWindow(self.hParentWnd, 1)
		self.enableParentOnDestruction = False
		self.hParentWnd = None
		
		for userControl in self.userControls:
			if userControl.hWnd:
				user32.DestroyWindow(userControl.hWnd)
		user32.DestroyWindow(self.hWnd)
		self.hWnd = None
		if user32.UnregisterClassW(self.windowClassName, self.hInst) == 0:
			print("Failed to unregister class:", self.windowClassName)
		if self.hFont:
			gdi32.DeleteObject(self.hFont)
			self.hFont = None

	def createWindow(self):		 
		windowClass = WNDCLASSEX()
		windowClass.cbSize = sizeof(WNDCLASSEX)
		windowClass.style = CS_HREDRAW | CS_VREDRAW
		windowClass.lpfnWndProc = self.windowProc
		windowClass.cbClsExtra = 0
		windowClass.cbWndExtra = 0
		windowClass.hInstance = self.hInst
		windowClass.hIcon = user32.LoadIconW(0, IDI_INFORMATION) if not self.userIcon else self.userIcon
		windowClass.hCursor = user32.LoadCursorW(0, IDC_ARROW);
		windowClass.hBrush = user32.GetSysColorBrush(COLOR_WINDOW) #COLOR_MENU
		if not windowClass.hBrush:
			windowClass.hBrush = gdi32.GetStockObject(WHITE_BRUSH)
		windowClass.lpszMenuName = 0
		windowClass.lpszClassName = self.windowClassName
		windowClass.hIconSm = 0

		if user32.RegisterClassExW(byref(windowClass)) == 0:
			return False

		hParentWnd = noesis.getWindowHandle()
		hWnd = user32.CreateWindowExW(	self.exStyle,
										self.windowClassName,
										self.windowName,
										self.style,
										self.x,
										self.y,
										self.width,
										self.height,
										hParentWnd,
										0,
										self.hInst,
										0 )
		if not hWnd:
			return False

		user32.ShowWindow(hWnd, SW_SHOW)
		self.hWnd = hWnd
		self.hParentWnd = hParentWnd
		liveWindows[hWnd] = self
		return True
		
	def setFont(self, fontName, size):
		if self.hWnd:
			hFont = gdi32.CreateFontW(	-size, #height
										0, #width
										0, #angle of escapement
										0, #orientation angle
										FW_NORMAL, #weight
										0, #italic
										0, #underline
										0, #strikeout
										ANSI_CHARSET, #char set
										OUT_TT_PRECIS, #output precision
										CLIP_DEFAULT_PRECIS, #clipping precision
										ANTIALIASED_QUALITY, #output quality
										FF_DONTCARE | DEFAULT_PITCH, #family and pitch
										fontName )
			if hFont:
				if self.hFont:
					gdi32.DeleteObject(self.hFont)		
				self.hFont = hFont
				user32.SendMessageW(self.hWnd, WM_SETFONT, hFont, 1)

	def addUserControlMessageCallback(self, controlIndex, message, method):
		cb = NoeUserControlCallback(controlIndex, message, method)
		self.userCallbacks.append(cb)

	def getControlByIndex(self, controlIndex):
		return self.userControls[controlIndex]
		
	def getControlById(self, controlId):
		for userControl in self.userControls:
			if userControl.controlId == controlId:
				return userControl
		return None
		
	def enableControlByIndex(self, controlIndex, enabled = True):
		user32.EnableWindow(self.userControls[controlIndex].hWnd, enabled)
				
	def setupChildWindow(self, hChildWnd):
		if self.hFont:
			user32.SendMessageW(hChildWnd, WM_SETFONT, self.hFont, 1)			

	def addControl(self, newControl):
		self.setupChildWindow(newControl.hWnd)
		self.currentControlId += 1
		self.userControls.append(newControl)
		return len(self.userControls) - 1

	def createStatic(self, text, x, y, width, height):
		if self.hWnd:
			newStatic = NoeUserStatic(self, text, self.currentControlId, x, y, width, height)
			return self.addControl(newStatic)
		return -1
		
	def createButton(self, name, x, y, width, height, commandMethod, defaultButton = False):
		if self.hWnd:
			newButton = NoeUserButton(self, name, self.currentControlId, x, y, width, height, commandMethod, defaultButton)
			return self.addControl(newButton)
		return -1

	def createCheckBox(self, name, x, y, width, height, commandMethod = defaultCheckBoxCommandMethod):
		if self.hWnd:
			newCheckBox = NoeUserCheckBox(self, name, self.currentControlId, x, y, width, height, commandMethod)
			return self.addControl(newCheckBox)
		return -1
		
	def createEditBox(self, x, y, width, height, text = "", commandMethod = None, isMultiLine = True, isReadOnly = False):
		if self.hWnd:
			newEditBox = NoeUserEditBox(self, text, self.currentControlId, x, y, width, height, isMultiLine, isReadOnly, commandMethod)
			return self.addControl(newEditBox)
		return -1

	def createComboBox(self, x, y, width, height, commandMethod = None, style = CBS_SORT | CBS_DROPDOWNLIST):
		if self.hWnd:
			newComboBox = NoeUserComboBox(self, self.currentControlId, x, y, width, height, style, commandMethod)
			return self.addControl(newComboBox)
		return -1

	def createListBox(self, x, y, width, height, commandMethod = None, style = LBS_SORT):
		if self.hWnd:
			newListBox = NoeUserListBox(self, self.currentControlId, x, y, width, height, style, commandMethod)
			return self.addControl(newListBox)
		return -1

	def createScrollBar(self, x, y, width, height, commandMethod = None, isHorizontal = True, registerCallback = True):
		if self.hWnd:
			newScrollBar = NoeUserScrollBar(self, self.currentControlId, x, y, width, height, isHorizontal, commandMethod)
			scrollIndex = self.addControl(newScrollBar)
			if registerCallback:
				msgType = WM_HSCROLL if isHorizontal else WM_VSCROLL
				self.addUserControlMessageCallback(scrollIndex, msgType, NoeUserScrollBar.DefaultScrollCallback)
			
			return scrollIndex
		return -1
