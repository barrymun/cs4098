LEX     = flex
LFLAGS  = -l
CC	= gcc
CFLAGS	= -I.. -g -Wall
LIBS	= ../pml/libpml.a  ../expr/libexpr.a 
LDFLAGS = 
OBJS	= common.o
SRCS	= 
LDFLAGS = 
PROG	= drugFind
YFLAGS	= -d

all:		$(PROG)

$(PROG):	$(OBJS) $(LIBS)
		$(CC) $(CFLAGS) -o $(PROG) main.c $(OBJS) $(LIBS)

