// utility functions
#include <opencv2/core.hpp>
#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>
#include <sys/stat.h>

using namespace std;
using namespace cv;

bool compare_point2f(const Point2f &v1, const Point2f &v2) {
  if (v1.x > v2.x) {
    return false;
  }
  else if (v1.x == v2.x and v1.y > v2.y) {
    return false;
  }
  return true;
}

vector<string> split (const string &s, char delim) {
  vector<string> result;
  stringstream ss (s);
  string item;

  while (getline (ss, item, delim)) {
    result.push_back (item);
  }
  return result;
}

vector<Point2f> rectify(vector<Point> v_old) {
  vector<Point2f> v_new;
  Point v0,v1,v2,v3;

  stable_sort(v_old.begin(), v_old.end(), compare_point2f);
  if (v_old[0].y < v_old[1].y) {
    v0 = v_old[0];
    v3 = v_old[1];
  }
  else {
    v0 = v_old[1];
    v3 = v_old[0];
  }

  if (v_old[2].y < v_old[3].y) {
    v1 = v_old[2];
    v2 = v_old[3];
  }
  else {
    v1 = v_old[3];
    v2 = v_old[2];
  }
  v_new.push_back(v0);
  v_new.push_back(v1);
  v_new.push_back(v2);
  v_new.push_back(v3);
  return v_new;
}

bool dir_exists(string s) {
  struct stat st;
  if(stat(s.c_str(),&st) == 0)
    if(st.st_mode and (S_IFDIR != 0))
      return true;
  return false;
}
