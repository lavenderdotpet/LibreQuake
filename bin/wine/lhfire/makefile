##### Win32 variables #####

WIN32_EXE=lhfire.exe
WIN32_LDFLAGS=

##### Unix variables #####

UNIX_EXE=lhfire
UNIX_LDFLAGS=-lm

##### Common variables #####

OBJECTS= frame.o framebuffer.o main.o math.o particle.o render.o script.o

CC=gcc
CFLAGS=-Wall -O2 -Icommon

ifdef windir
CMD_RM=del
else
CMD_RM=rm -f
endif

##### Commands #####

.PHONY: all mingw clean

all:
ifdef windir
	$(MAKE) EXE=$(WIN32_EXE) LDFLAGS="$(WIN32_LDFLAGS)" $(WIN32_EXE)
else
	$(MAKE) EXE=$(UNIX_EXE) LDFLAGS="$(UNIX_LDFLAGS)" $(UNIX_EXE)
endif

mingw:
	$(MAKE) EXE=$(WIN32_EXE) LDFLAGS="$(WIN32_LDFLAGS)" $(WIN32_EXE)

.c.o:
	$(CC) $(CFLAGS) -c $*.c -o $*.o

$(EXE): $(OBJECTS)
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	-$(CMD_RM) $(WIN32_EXE)
	-$(CMD_RM) $(UNIX_EXE)
	-$(CMD_RM) *.o
	-$(CMD_RM) *.d

.PHONY: clean

-include *.d
