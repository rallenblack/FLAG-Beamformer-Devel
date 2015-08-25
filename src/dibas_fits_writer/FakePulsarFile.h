//# Copyright (C) 2013 Associated Universities, Inc. Washington DC, USA.
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful, but
//# WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
//# General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
//#
//# Correspondence concerning GBT software should be addressed as follows:
//# GBT Operations
//# National Radio Astronomy Observatory
//# P. O. Box 2
//# Green Bank, WV 24944-0002 USA

#ifndef FAKEPULSARFILE
#define FAKEPULSARFILE

using namespace::std;

#include <string>
#include <vector>

/*
 A class responsible for reading, and parsing an ascii file produced
 by the 'fake' program.
*/
class FakePulsarFile 
{
public:
    FakePulsarFile(const char *path);
    bool parse();
    bool readFile();
    inline vector<vector<float>> getData() { return data; }
    inline int getNumSamples() { return fileNumSamples; }
    inline int getNumChans() { return fileNumChans; }
private:
    // TBF: can't get these functions to link!
    //vector<string> &splitThis(const string &s, char delim, vector<string> &elems);
    //vector<string> splitThat(const string &s, char delim);
    string filename;
    int fileNumSamples;
    int fileNumChans;
    vector<string> fileLines;
    vector<vector<float>> data;

};

#endif