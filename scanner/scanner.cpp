#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>
#include <zbar.h>

#include <iostream>
#include <fstream>
#include <ctype.h>
#include <getopt.h>
#include <libgen.h>
#include <dirent.h>
#include <sys/stat.h>
#include "utils.h"

using namespace cv;
using namespace std;

#define LOGFILE "./LOGBEST.txt"
#define DIR_RESULT "result"

// for logging best images
unsigned b_img, t_img, k_img, d_img, e_img;

// expected sizes of areas in sheet
const int HEIGHT_A4 = 1753;
const int WIDTH_A4 = 1240;
const int HEIGHT_ANSWERS = 470;
const int WIDTH_ANSWERS = 775;
const int MIN_RADIUS = 9;
const int MAX_RADIUS = 14;
const int EPSILON = 3;
const int MARK_MAX_VALUE = 3.14*255*(MAX_RADIUS+EPSILON)*(MAX_RADIUS+EPSILON);
const int MARK_MIN_VALUE = 0.2*MARK_MAX_VALUE;
const bool DRAW_AREAS = false;

bool flag_crop = false;
bool flag_debug = false;
bool flag_save_image = false;
bool flag_show_image = false;
bool flag_ignore_num_questions = false;

// image generators
int blur_values[] = {1,0};
int threshold_values[] = {0,1};
int kernel_size_values[] = {3,5};
int dilation_values[] = {0,1};
int erosion_values[] = {0,1};

int blur_values_qr[] = {1,0};
//int blur_values_qr[] = {1,0,2};
int threshold_values_qr[] = {0,1,2};
int kernel_size_values_qr[] = {3,5};
int dilation_values_qr[] = {0,1};
//int dilation_values_qr[] = {0,1,2};
int erosion_values_qr[] = {0,1};
//int erosion_values_qr[] = {0,1,2};

// logging
int count_failures;

// QR code
typedef struct {
  string type;
  string data;
  vector <Point> location;
} decodedQR;

class Image_transform {
public:
  int blur, threshold, kernel_size, dilation, erosion;
  Image_transform(int, int, int, int, int);
};
Image_transform::Image_transform(int b, int t, int k, int d, int e) {
  blur = b; threshold = t;  kernel_size = k; dilation = d; erosion = e;
}

inline string getCurrentDateTime(string s) {
  time_t now = time(0);
  struct tm  tstruct;
  char  buf[80];
  tstruct = *localtime(&now);
  if(s=="now")
    strftime(buf, sizeof(buf), "%Y-%m-%d %X", &tstruct);
  else if(s=="date")
    strftime(buf, sizeof(buf), "%Y-%m-%d", &tstruct);
  return string(buf);
};

inline void log(string logMsg, string detail_1 = "", string detail_2 = "") {
  //string filePath = LOGFILE+getCurrentDateTime("date")+".txt";
  string filePath = LOGFILE;
  string now = getCurrentDateTime("now");
  ofstream ofs(filePath.c_str(), std::ios_base::out | std::ios_base::app );
  ofs << now << '\t' << logMsg;
  if (detail_1 != "") {
    ofs << " (" << detail_1;
    if (detail_2 != "")
      ofs << " " << detail_2;
    ofs << ")";
  }
  ofs << endl;
  ofs.close();
}

void debug(string s) {
  if (flag_debug)
    cerr << "debug: " << s << endl;
}
 
bool extract_qr(Mat &im, decodedQR &qr_data) {
  zbar::ImageScanner scanner;
  //scanner.set_config(zbar::ZBAR_QRCODE, zbar::ZBAR_CFG_ENABLE, 1);
  //scanner.set_config(zbar::ZBAR_CODE128, zbar::ZBAR_CFG_ENABLE, 1);
  //leaving with NONE is marginally faster
  scanner.set_config(zbar::ZBAR_NONE, zbar::ZBAR_CFG_ENABLE, 1);
  // Wrap image data in a zbar image
  zbar::Image image(im.cols, im.rows, "Y800", (uchar *)im.data, im.cols * im.rows);
  scanner.scan(image);
  for (zbar::Image::SymbolIterator symbol = image.symbol_begin(); symbol != image.symbol_end(); ++symbol) {
    qr_data.type = symbol->get_type_name();
    if ((qr_data.type != "QR-Code") and (qr_data.type != "CODE-128")) continue;
    if (symbol->get_location_size() == 4) {
      for (int i = 0; i< symbol->get_location_size(); i++) {
	  qr_data.location.push_back(Point(symbol->get_location_x(i),symbol->get_location_y(i)));
	  //cout<< symbol->get_location_x(i)<<endl;
      }
      qr_data.data = symbol->get_data();
      return true;
    }
  }
  return false;
}


void gen_images_qr(vector<Image_transform> &image_transforms) {
  for(unsigned int e=0; e<sizeof(erosion_values_qr)/sizeof(int); e++) {
    for(unsigned int d=0; d<sizeof(dilation_values_qr)/sizeof(int); d++) {
      for(unsigned int k=0; k<sizeof(kernel_size_values_qr)/sizeof(int); k++) {
        for(unsigned int t=0; t<sizeof(threshold_values_qr)/sizeof(int); t++) {
          for(unsigned int b=0; b<sizeof(blur_values_qr)/sizeof(int); b++) {
            image_transforms.push_back(Image_transform(blur_values_qr[b], threshold_values_qr[t],
                                                       kernel_size_values_qr[k], dilation_values_qr[d], erosion_values_qr[e]));
          }
        }
      }
    }
  }
}

void gen_images(vector<Image_transform> &image_transforms) {
  for(unsigned int e=0; e<sizeof(erosion_values)/sizeof(int); e++) {
    for(unsigned int d=0; d<sizeof(dilation_values)/sizeof(int); d++) {
      for(unsigned int k=0; k<sizeof(kernel_size_values)/sizeof(int); k++) {
        for(unsigned int t=0; t<sizeof(threshold_values)/sizeof(int); t++) {
          for(unsigned int b=0; b<sizeof(blur_values)/sizeof(int); b++) {
            image_transforms.push_back(Image_transform(blur_values[b], threshold_values[t],
                                                       kernel_size_values[k], dilation_values[d], erosion_values[e]));
          }
        }
      }
    }
  }
}

void show_image(Mat img, string title, double scale) {
  Mat imS;
  resize(img, imS, Size(img.cols/scale, img.rows/scale));
  namedWindow(title, WINDOW_AUTOSIZE);
  imshow(title, imS);
  waitKey(0);
}

Mat apply_image_transform(Mat image, Image_transform it) {
  Mat new_image = image.clone();
  //Mat kernel = getStructuringElement(MORPH_ELLIPSE,
  //Mat kernel = getStructuringElement(MORPH_CROSS,
  Mat kernel = getStructuringElement(MORPH_RECT,
                                     Size(it.kernel_size, it.kernel_size),
                                     Point(-1, -1) );
  //show_image(image, "original_image", 2);
  //imwrite("image_orig_c.tiff",image);
  if (it.threshold == 1) 
    threshold(image, new_image, 0, 255, THRESH_OTSU);
  else if (it.threshold == 2) 
    adaptiveThreshold(image, new_image, 255, ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY, 37, 2);
  //imwrite("image_threshold_c.tiff",image);

  if (it.erosion > 0) {
    erode(new_image, new_image, kernel, Point(-1,-1), it.erosion);
  }
  //imwrite("image_erosion_c.tiff",new_image);
  if (it.dilation > 0) {
    dilate(new_image, new_image, kernel, Point(-1,-1), it.dilation);
  }
  //imwrite("image_dilation_c.tiff",new_image);

  if (it.blur == 1)
    GaussianBlur(new_image, new_image, Size(it.kernel_size, it.kernel_size), 0, 0);
  if (it.blur == 2) {
    GaussianBlur(new_image, new_image, Size(it.kernel_size, it.kernel_size), 0, 0);
    GaussianBlur(new_image, new_image, Size(it.kernel_size, it.kernel_size), 0, 0);
  }
  //imwrite("image_blur_c.tiff",image);

  //show_image(new_image, "transformed_image", 2);
  b_img=it.blur; t_img=it.threshold; k_img=it.kernel_size ; d_img=it.dilation; e_img=it.erosion;
  return new_image;
}

bool compare_vec3f(const Vec3f &v1, const Vec3f &v2) {
  if (v1[0] < v2[0]) {
    return false;
  }
  else if (v1[0] == v2[0] and v1[1] < v2[1]) {
    return false;
  }
  return true;
}

vector<Vec3i> detect_circles(Mat img) {
  //detect circles in the image
  if (flag_show_image) show_image(img,"circles",2);
  vector<Vec3f> fcircles;
  vector<Vec3i> circles;
  HoughCircles(img, fcircles, HOUGH_GRADIENT, 1, 25, 40, 25, MIN_RADIUS, MAX_RADIUS);
  stable_sort(fcircles.begin(), fcircles.end(), compare_vec3f);
  // convert the (x, y) coordinates and radius of the circles to integers
  for (const auto& c : fcircles) {
    circles.push_back({cvRound(c[0]), cvRound(c[1]), cvRound(c[2])});
  }
  return circles;
}

vector<int> interpolate(vector<int> v) {
  vector<int> newv;
  for (unsigned int i=1; i<v.size()-1; i++) {
    if (v[i]==0 and v[i]<v[i-1] and v[i]<v[i+1]) {
      //newv.push_back((v[i-1]+v[i]+v[i+1])/3);
      //cout << (v[i-1]+v[i]+v[i+1])/3 << " ";
      if (v[i-1]>v[i+1])
        newv.push_back(v[i+1]);
      else
        newv.push_back(v[i-1]);
    }
    else
      newv.push_back(v[i]);
  }
  return newv;
}

vector<int> find_peaks(vector<int> v, int min_dist) {
  vector<int> newv;
  for (unsigned int i=1; i<v.size()-1; i++) {
    if (v[i]>0 and ((v[i]>v[i-1] and v[i]>v[i+1]) or (v[i]==v[i-1] and v[i]==v[i+1]))) {
      if (newv.size() == 0)
        newv.push_back(i);
      else if (i-newv[newv.size()-1]>(unsigned)min_dist)
        newv.push_back(i);
    }
  }
  return newv;
}

vector<Vec3i> clean_circles(vector<Vec3i> circles) {
  //clean circles in the image
  int xmax = 0, ymax = 0;
  for (const auto& c : circles) {
    if (c[0] > xmax)
      xmax = c[0];
    if (c[1] > ymax)
      ymax = c[1];
  }
  xmax += 10;
  ymax += 10;
  //cout << "xmax" << xmax << endl;
  //cout << "ymax" << ymax << endl;
  vector<int> xhist, yhist;
  for (int i=0; i<xmax; i++)
    xhist.push_back(0);
  for (int i=0; i<ymax; i++)
    yhist.push_back(0);
  for (const auto& c : circles) {
    xhist[c[0]] += 1;
    yhist[c[1]] += 1;
  }
  if (flag_debug) {
    for (int i=0; i<xmax; i++)
      cout << xhist[i] << " ";
    cout << endl;
    for (int i=0; i<ymax; i++)
      cout << yhist[i] << " ";
    cout << endl;
  }
  vector<int> xhist_smooth = interpolate(xhist);
  vector<int> yhist_smooth = interpolate(yhist);
  if (flag_debug) {
    cout << endl;
    cout << endl;
    cout << "interpolate x" << endl;
    for (unsigned int i=0; i<xhist_smooth.size(); i++)
      cout << xhist_smooth[i] << " ";
    cout << endl;
    cout << "interpolate y" << endl;
    for (unsigned int i=0; i<yhist_smooth.size(); i++)
      cout << yhist_smooth[i] << " ";
    cout << endl;
    cout << endl;
  }
  
  vector<int> xpeaks = find_peaks(xhist_smooth,MIN_RADIUS);
  vector<int> ypeaks = find_peaks(yhist_smooth,MIN_RADIUS);
  
  if (flag_debug) {
    cout << "find peaks x" << endl;
    for (unsigned int i=0; i<xpeaks.size(); i++)
      cout << xpeaks[i] << " ";
    cout << endl;
    cout << "find peaks y" << endl;
    for (unsigned int i=0; i<ypeaks.size(); i++)
      cout << ypeaks[i] << " ";
    cout << endl;
    cout << endl;
  }
  
  // build grid of circles to group neighbouring circles
  Vec3i grid[ypeaks.size()][xpeaks.size()];
  for (unsigned int i=0; i<xpeaks.size(); i++)
    for (unsigned int j=0; j<ypeaks.size(); j++)
      grid[j][i] = Vec3i(0,0,0);
  
  int avg_radius = 0;
  int avg_num = 0;
  int foundx, foundy;
  int x, y, r;
  for (const auto& c : circles) {
    int MIN_DIST = 8;
    x = c[0];
    y = c[1];
    r = c[2];
    foundx = -1;
    foundy = -1;
    for (unsigned int i=0; i<xpeaks.size(); i++) {
      if ((x <= (xpeaks[i]+MIN_DIST)) and (x >= xpeaks[i]-MIN_DIST)) {
        foundx = i;
        break;
      }
    }
    if (foundx == -1)
      continue; // ignore this circle
    for (unsigned int j=0; j<xpeaks.size(); j++) {
      if ((y <= (ypeaks[j]+MIN_DIST)) and (y >= ypeaks[j]-MIN_DIST)) {
        foundy = j;
        break;
      }
    }
    if (foundy == -1)
      continue; // ignore this circle
    avg_radius += r;
    avg_num += 1;
    if (grid[foundy][foundx] == Vec3i(0,0,0))
      grid[foundy][foundx] = Vec3i(x, y, r);
    else {
      //if more than one circle at close distance, choose one
      if (abs(x-xpeaks[foundx]) + abs(y-ypeaks[foundy]) < abs(grid[foundy][foundx][0]-xpeaks[foundx]) + abs(grid[foundy][foundx][1]-ypeaks[foundy]))
        grid[foundy][foundx] = Vec3i(x, y, r);
    }
  }
  if (avg_num > 0)
    avg_radius = avg_radius/avg_num;
  else
    avg_radius = 0;
  
  if (flag_debug)
    cout << "avg_radius = " << avg_radius << endl;
  vector<Vec3i> cleaned_circles;
  for (unsigned int i=0; i<xpeaks.size(); i++) {
    for (unsigned int j=0; j<ypeaks.size(); j++) {
      if (grid[j][i] != Vec3i(0,0,0))
        cleaned_circles.push_back(Vec3i(grid[j][i][0],grid[j][i][1],avg_radius));
      else
        cleaned_circles.push_back(Vec3i(xpeaks[i],ypeaks[j],avg_radius));
    }
  }
  return cleaned_circles;
}

int confidence(Mat values) {
  vector<Mat> channels;
  Mat points, fpoints;
  Mat tmp = values.clone();
  Mat labels, centers;
  int  max=-1, max2=-1;
  
  // cout << "values: ";
  // for (int i=0; i< values.rows; i++) {
  //   cout << values.at<double>(0,i) << " ";
  // cout << endl;
  for (int i=0; i< values.rows; i++) {
    if (values.at<double>(0,i) > max) {
      max2 = max;
      max = values.at<double>(0,i);
    }
    else if (values.at<double>(0,i) > max2) {
      max2 = values.at<double>(0,i);
    }
  }
  
  //cout << "max=" << max << " max2=" << max2 << endl;
  if (max < MARK_MIN_VALUE) {
    //cout << "mark value too small" << endl;
    //cout << "returning -1" << endl;
    return -1;
  }
  if (max > 1.1*MARK_MAX_VALUE) {
    //cout << "mark value too large" << endl;
    //cout << "returning -1" << endl;
    return -1;
  }
  if ((max2 == -1) or (1.0*max2 > 2.0*max/3.0)) {
    //cout << "too little difference max,max2" << endl;
    //cout << "returning -1" << endl;
    return -1;
  }
  //cout << "fmax=" << 2.0*max/3.0 << " fmax2=" << 1.0*max2 << endl;
  
  //cout << "in confidence" << endl;
  //cout << values << endl << endl;
  //cout << fpoints << endl << endl;
  
  channels.push_back(tmp);
  channels.push_back(values);
  merge(channels, points);
  points.convertTo(fpoints,CV_32F);
  kmeans(fpoints, 2, labels,
         TermCriteria( TermCriteria::EPS+TermCriteria::COUNT, 10, 0.5),
         10, KMEANS_PP_CENTERS, centers);
  //   if (conf == 0) {// something is wrong
  //     cout << "confidence zero" << endl;
  //     cout << values << endl;
  //     cout << labels << endl;
  //     cout << "returning -1" << endl;
  //     return -1;
  //   }
  int num0=0, num1=0;
  for (int i=0; i<labels.rows; i++) {
    if (labels.at<int>(i,0) == 0)
      num0++;
    else
      num1++;
  }
  //cout << "num0=" << num0 << " num1=" << num1  << endl;
  int val = -1;
  if ((num0 == 1) and (num1 == labels.rows-1))
    val = 0;
  else if (num1 == 1 and (num0 == labels.rows-1))
    val = 1;
  else {
    //cout << "returning -1" << endl;
    return -1;
  }
  for (int i=0; i<labels.rows; i++) {
    if ((labels.at<int>(i,0) == val) and (values.at<double>(0,i) == max)) {
      //cout << "value=" << values.at<double>(0,i) << endl;
      //cout << "returning " << i << endl;
      return i;
    }
  }
  //cout << "returning -1" << endl;
  return -1;
}

int get_id_column(int column, vector<Vec3i> circles, Mat thresh_img) {
  //cout << "get_id_column" << endl;
  int x, y, r;
  Mat values;
  for (int i=0; i<10; i++) {
    Vec3i c = circles[column*10+i];
    x = c[0];
    y = c[1];
    r = c[2];
    if (flag_show_image) {
      Mat color_image;
      cvtColor(thresh_img, color_image, COLOR_GRAY2BGR);
      circle(color_image, Point(x, y), r, Scalar(255, 0, 255), 2);
      rectangle(color_image, Point(x-r-EPSILON, y-r-EPSILON),Point(x+r+EPSILON,y+r+EPSILON), Scalar(0, 0, 255), 1);
      show_image(color_image,"column",2);
    }
    Rect crop_rect = Rect(Point(x-r-EPSILON, y-r-EPSILON), Point(x+r+EPSILON, y+r+EPSILON));
    Mat crop = thresh_img(crop_rect);
    if (flag_show_image)
      show_image(crop,"cropped",2);
    values.push_back(sum(crop)[0]);
  }
  int best = confidence(values);
  return best;
}

string get_id_from_circles(int num_digits, bool id_check, vector<Vec3i> circles, Mat thresh_img) {
  //cout << "get_id_from_circles" << endl;
  string id;
  int check = (id_check ? 1 : 0);
  if ((unsigned)(num_digits+check)*10 != circles.size()) {
    if (flag_debug) log("incorrect number of circles found in reg", "circles.size() =", to_string(circles.size()));
    cout << "incorrect number of circles found in reg" << endl;
    //cout << num_digits << endl;
    //cout << check << endl;
    //cout << circles.size() << endl;
    if (id_check)
      return string(num_digits, '*')+"-*";
    else
      return string(num_digits, '*');
  }
  vector<int> id_vals;
  for (int i=0; i<num_digits+check; i++)
    id_vals.push_back(get_id_column(i,circles,thresh_img));
  //    cout << "id_vals: ";
  //    for (const auto& i : id_vals)
  //      cout << i << " " ;
  //    cout << endl;
  for (int i=0; i<num_digits; i++) {
    if (id_vals[i] == -1)
      id += "*";
    else {
      id += to_string(id_vals[i]);
    }
  }
  if (id_check) {
    if ((id_vals[id_vals.size()-1] == -1) or (id_vals[id_vals.size()-1] > 9))
      id += "-*";
    else {
      id += "-";
      id += 'A' + id_vals[id_vals.size()-1];
    }
  }
  //cout << "id=" << id << endl;
  return id;
}

bool detect_rectangles(Mat image, int numdig, vector<Point> *reg_area, vector<Point> *answer_area) {
  Mat edged;
  vector<vector<Point> > contours;
  vector<Vec4i> hierarchy;
  vector<Point> approx;
  double p;
  vector<Image_transform> image_transforms;
  gen_images(image_transforms);
  Mat new_image;
  
  //cout << "entering detect_rectangles" << endl;
  bool found = false;
  for (const auto& i : image_transforms) {
    new_image = apply_image_transform(image, i);
    Canny(new_image, edged, 0, 50);
    if (flag_show_image) {
      show_image(new_image, "new_image", 2);
      show_image(edged, "edged", 2);
    }
    ////////////////////
    // find answer area
    ////////////////////
    findContours(edged, contours, hierarchy, RETR_LIST, CHAIN_APPROX_NONE, Point(0, 0));
    //findContours(edged, contours, hierarchy, RETR_LIST, CHAIN_APPROX_SIMPLE, Point(0, 0));
    sort(contours.begin(), contours.end(), [](const vector<Point>& c1, const vector<Point>& c2){
      return contourArea(c1, false) > contourArea(c2, false);
    });
    int expected_area_answers = HEIGHT_ANSWERS*WIDTH_ANSWERS;
    //cout << "expected area answers = " << expected_area_answers << endl;
    int c_answer_area_idx = -1;
    float standard = float(HEIGHT_ANSWERS)/float(WIDTH_ANSWERS);
    for (const auto& c : contours) {
      c_answer_area_idx += 1;
      if (flag_show_image) {
        Mat color_image;
        cvtColor(new_image, color_image, COLOR_GRAY2BGR);
        drawContours(color_image, contours, c_answer_area_idx, Scalar(0,255,0), 3);
        show_image(color_image,"contours",2);
      }

      p = arcLength(c, true);
      approxPolyDP(c, approx, 0.02 * p, true);
      if (approx.size() == 4) {
        double a = contourArea(approx);
	if (flag_debug)
	  cout << "area = " << a << endl;
        if (a > 1.5*expected_area_answers) { // rectangle is maybe the whole page?
	  cout << "too big" << endl;
          if (flag_debug) {
	    log("a > 1.5*expected_area_answers");
	    cout << "too big" << endl;
	  }
          continue;
        }
        if (a < 0.5*expected_area_answers) { // rectangle is too small
          if (flag_debug) {
	    log("a < 0.5*expected_area_answers");
	    cout << "too small" << endl;
	  }
          break;
        }
        Rect br = boundingRect(approx);
	if (flag_debug) {
	  cout << "width: " << br.width << "height: " << br.height << endl;
	  cout << "area contour = " << contourArea(c) << endl;
	}
        double ar = 1.0*br.height/br.width;
        if (ar >= 0.90*standard and ar <= 1.1*standard) {
	  if (flag_debug)
	    cout << "right shape " << "ar=" << ar << " standard=" << standard << endl;
          found = true;
          break;
        }
	else {
	  cout << "not right shape " << "ar=" << ar << " standard=" << standard << endl;
          if (flag_debug) {
	    log("not the right shape");	  
	    cout << "not right shape " << "ar=" << ar << " standard=" << standard << endl;
	  }
	}
      }
    }
    if (!found) {
      if (flag_debug) log("detect_rectangles, answer area not found, try another image");
      continue;
    }
    *answer_area = approx;
    //cout << "largest_area " << largest_area << endl;
    if (found) break;
  }
  return found;
}

vector<int> get_answers_batch(int num_alternatives, int rows, int start, int num, vector<Vec3i>circles, Mat thresh_img) {
  vector<int> answers;
  int x, y, r;
  
  start *= num_alternatives;
  for (int i=0; i<num; i++) {
    Mat values;
    for (int j=0; j<num_alternatives; j++) {
      Vec3i c = circles[start+i+j*rows];
      x = c[0];
      y = c[1];
      r = c[2];
      if (flag_show_image) {
        Mat color_image;
        cvtColor(thresh_img, color_image, COLOR_GRAY2BGR);
        circle(color_image, Point(x, y), r, Scalar(255, 0, 255), 2);
        rectangle(color_image, Point(x-r-EPSILON, y-r-EPSILON),Point(x+r+EPSILON,y+r+EPSILON), Scalar(0, 0, 255), 1);
        show_image(color_image,"column",2);
      }
      Rect crop_rect = Rect(Point(x-r-EPSILON,y-r-EPSILON), Point(x+r+EPSILON,y+r+EPSILON));
      Mat crop = thresh_img(crop_rect);
      if (flag_show_image)
        show_image(crop,"cropped",2);
      values.push_back(sum(crop)[0]);
      //avalues.push_back(int(np.sum(crop)/(h*w)))
    }
    
    //cout << "get_answers_batch" << endl;
    //cout << values << endl;
    int best = confidence(values);
    answers.push_back(best);
  }
  return(answers);
}

vector<int> get_answers(int num_questions, int num_alternatives, vector<Vec3i> circles, Mat thresh_img) {
  vector<int> answers, answers1;
  unsigned int num_expected_circles;
  // sheet with 25, 50 and 70 questions are not full, but circles are added in processing
  //num_expected_circles = {5:25,10:50,15:75,20:100,25:125,30:150,40:200,50:300,60:300,70:400,80:400,90:450,100:500}
//   if (num_questions == 90)
//     num_expected_circles = 500; // 5 * 100
//   else if (num_questions == 70)
//     num_expected_circles = 400; // 5 * 80
//   else
    num_expected_circles = 5*num_questions;
  if (num_expected_circles != circles.size()) {
    if (flag_debug) log("incorrect number of circles found in answers", "circles.size() =", to_string(circles.size()));
    return answers;
  }
  // one column only for univesp
  answers = get_answers_batch(num_alternatives, num_questions, 0, num_questions, circles, thresh_img);
  
  return answers;
}

vector<int> get_answers_from_answer_area(Mat answer_area_img, int num_questions, int num_alternatives) {
  vector<Image_transform> image_transforms;
  Mat new_image;
  vector<Vec3i> circles;
  Mat thresh_img;
  vector<int> best_answer(num_questions, -1);
  int best_answer_failures = num_questions;
  
  if (flag_show_image) show_image(answer_area_img, "get_answers_from_answer_area", 2);
  gen_images(image_transforms);
  for (const auto& i : image_transforms) {
    new_image = apply_image_transform(answer_area_img, i);
    //cout << "blur=" << i.blur << " threshold=" << i.threshold << " kernel_size=" << i.kernel_size;
    //cout << " dilation=" << i.dilation << " erosion=" << i.erosion << endl;
    
    if (flag_show_image) show_image(new_image, "image_answer_area", 2);
    circles = detect_circles(new_image);
    //cout << "num_circles detected" << circles.size() << endl;
    Mat output;
    if (flag_show_image) {
      cvtColor(new_image, output, COLOR_GRAY2RGB);
      for (const auto& c : circles) {
        circle(output, Point(c[0], c[1]), c[2], Scalar(255,0,255), 3);
      }
      show_image(output,"circles_answer_area",2);
    }
    circles = clean_circles(circles);
    //cout << "num_circles after cleaning" << circles.size() << endl;
    if (flag_show_image) {
      for (const auto& c : circles) {
        circle(output, Point(c[0], c[1]), c[2], Scalar(0,255,255), 2);
      }
      show_image(output,"circles_answer_area",2);
    }
    threshold(new_image, thresh_img, 0, 255, THRESH_BINARY_INV + THRESH_OTSU);
    if (flag_show_image) show_image(thresh_img,"threshold",1);
    // erase circunferences from image
    for (const auto& c : circles) {
      circle(thresh_img, Point(c[0], c[1]), c[2]+2, Scalar(0,0,0), 4);
    }
    if (flag_show_image) show_image(thresh_img,"erased",2);
    vector<int>answers = get_answers(num_questions, num_alternatives, circles, thresh_img);
    //     cout << "in get_answers_from_answer_area" << endl;
    //     for (int a : answers)
    //       cout << a << " " ;
    //     cout << endl;
    if (answers.size() == (unsigned) num_questions) {
      count_failures = 0;
      for (int a : answers)
        if (a == -1) count_failures++;
      if (count_failures == 0) {
        log("best image for answer, "+to_string(b_img) + ", " + to_string(t_img) + ", " + to_string(k_img) + ", " + to_string(d_img) + ", " + to_string(e_img));
	log("failures = " + to_string(count_failures));
	if (flag_show_image) show_image(new_image,"best_image",2);
        return(answers);
      }
      if (count_failures < best_answer_failures) {
        best_answer = answers;
        best_answer_failures = count_failures;
      }
    }
  }
  log("failures = " + to_string(count_failures));
  return best_answer;
}

void get_id_from_qrcode(Mat reg_area_img, string *id, vector<Point> *location) {
  //show_image(reg_area_img, "extract_id_from_qr_code", 2);
  vector<Image_transform> image_transforms;
  gen_images_qr(image_transforms);
  Mat new_image;
  decodedQR qr_data;
  for (const auto& i : image_transforms) {
    new_image = apply_image_transform(reg_area_img, i);
    if (extract_qr(new_image, qr_data)) {
      log("best image for id qr code, "+to_string(b_img) + ", " + to_string(t_img) + ", " + to_string(k_img) + ", " + to_string(d_img) + ", " + to_string(e_img));
      *id = qr_data.data;
      *location = qr_data.location;
      return;
    }
  }
  cerr << "get_id_from_qrcode failed" << endl;
  *id = "";
}

vector<int> get_present_not_present(Mat area_img) {
  vector<Image_transform> image_transforms;
  Mat new_image;
  vector<Vec3i> circles;
  Mat thresh_img;
  vector<int> answer;

  if (flag_show_image) show_image(area_img, "get_present_not_present", 1);
  gen_images(image_transforms);
  for (const auto& i : image_transforms) {
    new_image = apply_image_transform(area_img, i);
    
    if (flag_show_image) show_image(new_image, "image_present_area", 2);
    circles = detect_circles(new_image);
    //cout << "num_circles detected" << circles.size() << endl;
    Mat output;
    if (flag_show_image) {
      cvtColor(new_image, output, COLOR_GRAY2RGB);
      for (const auto& c : circles) {
        circle(output, Point(c[0], c[1]), c[2], Scalar(255,0,255), 3);
      }
      show_image(output,"circles_present_area",1);
    }
    circles = clean_circles(circles);
    //cout << "num_circles after cleaning=" << circles.size() << endl;
    if (circles.size() != 2) continue;
    if (flag_show_image) {
      for (const auto& c : circles) {
        circle(output, Point(c[0], c[1]), c[2], Scalar(0,255,255), 2);
      }
      show_image(output,"circles_answer_area",2);
    }
    threshold(new_image, thresh_img, 0, 255, THRESH_BINARY_INV + THRESH_OTSU);
    if (flag_show_image) show_image(thresh_img,"threshold",1);
    // erase circunferences from image
    for (const auto& c : circles) {
      circle(thresh_img, Point(c[0], c[1]), c[2]+2, Scalar(0,0,0), 4);
    }
    if (flag_show_image) show_image(thresh_img,"erased",1);

    // prepare answer
    for (int i=0; i<2; i++) {
      Vec3i c = circles[i];
      int x = c[0];
      int y = c[1];
      int r = c[2];
      if (flag_show_image) {
	Mat color_image;
	cvtColor(thresh_img, color_image, COLOR_GRAY2BGR);
	circle(color_image, Point(x, y), r, Scalar(255, 0, 255), 2);
	rectangle(color_image, Point(x-r-EPSILON, y-r-EPSILON),Point(x+r+EPSILON,y+r+EPSILON), Scalar(0, 0, 255), 1);
	show_image(color_image,"column",1);
      }
      Rect crop_rect = Rect(Point(x-r-EPSILON,y-r-EPSILON), Point(x+r+EPSILON,y+r+EPSILON));
      Mat crop = thresh_img(crop_rect);
      if (flag_show_image)
	show_image(crop,"cropped",1);
      answer.push_back(sum(crop)[0]);
    }
    //cout << answer << endl;
    return answer;
  }
  return answer;
}

void process(Mat image, int expected_num_questions, int expected_num_alternatives, string *id, string *result_log) {
  int w = image.cols;
  int h = image.rows;
  if (flag_debug) {
    fprintf(stderr, "h = %d, w = %d\n", h, w);
  }
  // ***********************************************
  // set dummy variables 
  // ***********************************************
  int ndig = 0;
  int sheet_num_questions = expected_num_questions;
  int sheet_num_alternatives = expected_num_alternatives;

  // *************************
  // process qr_code
  // *************************
  // Rect EXPECTED_QR_LOCATION = Rect(Point(WIDTH_A4/2+340,90), Point(WIDTH_A4/2+500,245));
  Rect crop_rect = Rect(Point(WIDTH_A4/2,0), Point(WIDTH_A4,HEIGHT_A4/2));
  Mat crop_qr_code = image(crop_rect);
  vector<Point> location;

  //show_image(crop_qr_code,"cropped",2);
  get_id_from_qrcode(crop_qr_code, id, &location);
  if (flag_debug) {
    for (const auto& p : location) {
      cout << "x=" << p.x << " y=" << p.y << endl;
    }
    cout << *id << endl;
  }

  //crop_qr_code = image(EXPECTED_QR_LOCATION);
  //show_image(crop_qr_code,"cropped",0.5);
  


  // ****************************************
  // check if sheet is valid (find circles "present/not present"
  // ****************************************
  Point A, B, M, N, m, n;
  A.x = WIDTH_A4/2 + 340;
  A.y = 90;
  B.x = WIDTH_A4/2 + 500;
  B.y = 245;
  M.x = 450;
  M.y = 120;
  N.x = 900;
  N.y = 100; 
  m.x = M.x*(location[3].x - location[0].x)/(B.x - A.x); 
  n.x = N.x*(location[2].x - location[1].x)/(B.x - A.x); 
  // TO DO: deal with rotation
  if (location[3].y == location[0].y) {
    m.y = location[0].y + 30;
    n.y = location[2].y - 30;
  }
  else {
    m.y = location[0].y + 15;
    n.y = location[2].y - 10;
  }
//   cout << "A = " << A.x << ", " << A.y << endl;
//   cout << "B = " << B.x << ", " << B.y << endl;
//   cout << "m = " << m.x << ", " << m.y << endl;
//   cout << "n = " << n.x << ", " << n.y << endl;
  crop_rect = Rect(m, n);
  Mat crop_present_area = image(crop_rect);
  if (flag_debug) show_image(crop_present_area,"cropped",1);

  vector<int> present_answers = get_present_not_present(crop_present_area);
  int MIN_VALUE = 80000; // heuristic!
  if (present_answers.size() != 0 && present_answers[0] > MIN_VALUE) {
    *result_log = string("Ausente\n");
    if (flag_debug) cout << "ausente" << endl;
    return;
  }
  if (present_answers.size() != 0 && present_answers[1] > MIN_VALUE) {
    *result_log = string("Desclassificado\n");
    if (flag_debug) cout << "desclassificado" << endl;
    return;
  }

  // ***********************************************
  // detect two main areas, answers and registration
  // ***********************************************
  vector<Point> reg_area, answer_area;
  bool found_rect = detect_rectangles(image, ndig, &reg_area, &answer_area);
  if (!found_rect) {
    log("erro ao processar a folha, não encontrou área de marcação");
    *result_log = string("erro ao processar a folha, nnão encontrou área de marcação.");
    cerr << "erro ao processar a folha, não encontrou área de marcação" << endl;
    return;
  }
  if (DRAW_AREAS) {
    Mat color_image;
    vector<vector<Point> > contourVect;
    contourVect.push_back(reg_area);
    contourVect.push_back(answer_area);
    cvtColor(image, color_image, COLOR_GRAY2BGR);
    drawContours(color_image, contourVect, 0, Scalar(0, 255, 255), 2);
    drawContours(color_image, contourVect, 1, Scalar(255, 0, 255), 2);
    show_image(color_image,"contours_answers_color",2);
  }
  // ****************************************
  // resize main areas to original dimensions
  // ****************************************
  // answers area
  vector<Point2f> answer_area_rectified = rectify(answer_area);
  vector<Point2f> pts2 = {Point2f(0,0),Point2f(WIDTH_ANSWERS,0),Point2f(WIDTH_ANSWERS,HEIGHT_ANSWERS),Point2f(0,HEIGHT_ANSWERS)};
  Mat Matrix = getPerspectiveTransform(answer_area_rectified,pts2);
  Mat answer_area_image;
  warpPerspective(image,answer_area_image,Matrix,Size(WIDTH_ANSWERS,HEIGHT_ANSWERS));

  // not used
  Mat reg_area_image;


  // *************************
  // process answers
  // *************************
  //cout << endl << "processing answers" << endl;
  vector<int> answers = get_answers_from_answer_area(answer_area_image, sheet_num_questions, sheet_num_alternatives);
  ostringstream result_txt;
  int i = 1;
  char result[] = {'A', 'B', 'C', 'D', 'E'};
  for (int a : answers) {
    if (a == -1)
      result_txt << i << ". X" << endl;
    else
      result_txt << i << ". " << result[a] << endl;
    i += 1;
  }
  *result_log = result_txt.str();
  //cout << *result_log;
  return;
}


int process_a_file(string filename, int expected_num_questions, int expected_num_alternatives) {
  String imageName(filename);
  Mat image;
  image = imread(imageName);
  //imwrite("image_init_c.tiff",image);
  if (image.empty()) {
    cerr <<  "Could not open or find the image " << imageName << endl ;
    log("Could not open or find the image", imageName);
    return -1;
  }
  cvtColor(image, image, COLOR_BGR2GRAY);
  resize(image, image, Size(WIDTH_A4, HEIGHT_A4));

  if (flag_show_image)
    show_image(image, "image", 2);
  
  string id("ERRO");
  string result_log("Error\n");
  try {
    process(image, expected_num_questions, expected_num_alternatives, &id, &result_log);
    cout << "result_log: " << endl << result_log << endl;
  } catch (const std::exception& e) {
    result_log = "um erro não identificado ocorreu ao processar arquivo.";
    cerr << "Exception in process()" << e.what();
    log("exception in process()", e.what());
  }
  
  string homedir = dirname((char *)imageName.c_str());
  string fnamefull = basename((char *)imageName.c_str());
  size_t lastindex = fnamefull.find_last_of(".");
  string fname = fnamefull.substr(0, lastindex);

  string resultdir = homedir + "/" + DIR_RESULT;
  if (!dir_exists(resultdir)) {
    try {
      mkdir(resultdir.c_str(), S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
    } catch (const std::exception& e) {
      result_log = "um erro não identificado ocorreu ao processar arquivo.";
      cerr << "Exception when creating result directory" << e.what();
      log("exception when creating result directory", e.what());
    }
  }

  string result_name = fname + ".txt";
  //cout << "num_id=" << num_id << endl;
  //cout << "result_name=" << result_name << endl;
  //cout << "image_name=" << image_name << endl;
  ofstream resfile (resultdir+"/"+result_name);
  if (resfile.is_open()) {
    resfile << result_log;
    resfile.close();
  }
  else {
    cerr << "Cannot write result file";
    log("Cannot write result file");
    return -1;
  }
  return 0;
}

int main( int argc, char** argv ) {
  int opt;
  int num_questions, num_alternatives;
  
  while ((opt = getopt(argc,argv,"cdns")) != EOF) {
    switch(opt) {
      case 'c': flag_crop = true; break;
      case 'd': flag_debug = true; cout << " debugging " << endl ; break;
      case 'n': flag_ignore_num_questions = true; break;
      case 's': flag_show_image = true; break;
      case '?': fprintf(stderr, "usage: %s\n [-c -d -s] num_questions image_file\n\t-d for debug\n\t-d for debug\n\t-s for showing images\n", argv[0]); exit(-1);
      default: ;
    }
  }
  
  if (optind >= argc) {
    cerr << "expected number or questions" << endl;
    exit(-1);
  }
  num_questions = atoi(argv[optind++]);
  num_alternatives = 5;
  if (optind >= argc) {
    cerr << "expected image_file" << endl;
    exit(-1);
  }
  // make a list of files
  // first argument may be a directory
  struct stat s;
  DIR *dir;
  struct dirent *ent;
  vector<string> filenames;

  if ((optind == argc-1) and (stat(argv[optind],&s) == 0)) {
      if (s.st_mode & S_IFDIR) {
	if ((dir = opendir (argv[optind])) != NULL) {
	  while ((ent = readdir (dir)) != NULL) {
	    filenames.push_back(String(argv[optind])+String(ent->d_name));
	  }
	  closedir(dir);
	} else {
	  perror ("could not open directory");
	  return EXIT_FAILURE;
	}
      }
      else if( s.st_mode & S_IFREG ) {
	filenames.push_back(argv[optind++]);
      } // else ignore
  }
  else while (optind < argc)
	 filenames.push_back(String(argv[optind++]));

  for (const auto& fname : filenames) {
    cerr << "processing " << fname << endl;
    log("processing ", fname);
    process_a_file(fname, num_questions, num_alternatives);
  }
  return 0;
}
