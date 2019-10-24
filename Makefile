CC = gcc
CXX = g++
CXXLD = $(CXX)
LD = $(CXX)

CXXFLAGS= -std=gnu++11 -Wall -g

LDFLAGS= -L/usr/local/lib
LDLIBS= -lstdc++ -luhd -lboost_system -lpthread -lfftw3 -lfftw3_threads -lm
.phony: clean all

all: record fftProcess

record: record.o

record.o: record.cpp record.hpp

fftProcess.o: fftProcess.cpp fftProcess.hpp

fftProcess: fftProcess.o

clean:
	-rm -rf *.o record fftProcess
