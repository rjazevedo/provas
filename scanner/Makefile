LIB=`pkg-config --libs zbar opencv`

PROG = scanner
FLAGS= -O2 -Wall -std=c++11 `pkg-config --cflags zbar opencv`
SRC = scanner.cpp
OBJ = scanner.o utils.o

all: $(OBJ) 
	g++ $(FLAGS) $(OBJ) -o $(PROG) -lm $(LIB)

.cpp.o:
	g++ $(FLAGS) -c $<

install:
	cp $(PROG) ../bin/

clean:
	rm *.o; rm *~; rm $(PROG)



