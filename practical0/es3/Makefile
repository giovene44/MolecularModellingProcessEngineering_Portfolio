# Makefile for es3.cpp

CXX := g++
CXXFLAGS := -std=c++17 -O2 -Wall
TARGET := es3
SRC := es3.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET) *.o

.PHONY: all clean