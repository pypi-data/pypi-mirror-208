# ROUGH converter from bl-qt-tiger.h  to a custom Tcl list
#   (to be used by the demo-tiger.tcl)
# results are written to std
# you must capture stsdot and save it as "tiger-data.tcl"


#include "bl-qt-tiger.h"

#include <stdlib.h>
#include <stdio.h>


void convertData(const char* commands, int commandCount, const float* points, int pointCount) {
    size_t c = 0;
    size_t p = 0;

    float h = TigerData::height;
printf("set TigerData {\n");
    while (c < commandCount) {
printf(" { ");  // start of path

      // Fill params.
      char* fillRule = "XXX";
      switch (commands[c++]) {
        case 'N': fillRule = "NONE"; break;
        case 'F': fillRule = "NON_ZERO" ; break;
        case 'E': fillRule = "EVEN_ODD"; break;
      }
printf(" fill %s", fillRule);

      // Stroke params.
      char* hasStroke = "XXX";
      switch (commands[c++]) {
        case 'N': hasStroke = "false"; break;
        case 'S': hasStroke = "true"; break;
      }
printf(" stroke %s", hasStroke);

      char* strokeCap = "XXX";
      switch (commands[c++]) {
        case 'B': strokeCap = "BUTT"; break;
        case 'R': strokeCap = "ROUND"; break;
        case 'S': strokeCap = "SQUARE"; break;
      }
printf(" strokeCap %s", strokeCap);

      char* strokeJoin = "XXX";
      switch (commands[c++]) {
        case 'M': strokeJoin = "MITER_BEVEL"; break;
        case 'R': strokeJoin = "ROUND"; break;
        case 'B': strokeJoin = "BEVEL"; break;
      }
printf(" strokeJoin %s", strokeJoin);

printf(" strokeMiterLimit %f", points[p++]);  // ?? int or double
printf(" strokeWidth %f", points[p++]);  // ?? int or double

      // Stroke & Fill style.
printf(" strokeColor 0xFF%02x%02x%02x", int(points[p]*255), int(points[p+1]*255), int(points[p+2]*255) );
	p+=3;
printf("   fillColor 0xFF%02x%02x%02x", int(points[p]*255), int(points[p+1]*255), int(points[p+2]*255) );
	p+=3;


	// TO DO...   togli quel .h e sistemalo con una trasformazione reflex y
      // Path.
      int i, count = int(points[p++]);
printf(" geom {");
      for (i = 0 ; i < count; i++) {
        switch (commands[c++]) {
          case 'M':
printf(" M {%f %f}", points[p], h - points[p+1]);
            p += 2;
            break;
          case 'L':
printf(" L {%f %f}", points[p], h - points[p+1]);
            p += 2;
            break;
          case 'C':
printf(" C {%f %f %f %f %f %f}", points[p], h- points[p+1], points[p+2], h- points[p+3], points[p+4], h- points[p+5]);
            p += 6;
            break;
          case 'E':
printf(" Z {}");
            break;
        }
      }
printf(" }");  // end of geom

printf(" }\n");  // end of path

    }
printf("}\n"); // end of all paths
}



// ============================================================================
// [MainWindow]
// ============================================================================


// ============================================================================
// [Main]
// ============================================================================

#define ARRAY_SIZE(X) (sizeof(X) / sizeof(X[0]))

int main(int argc, char *argv[]) {

  convertData(
      TigerData::commands, ARRAY_SIZE(TigerData::commands),
      TigerData::points, ARRAY_SIZE(TigerData::points)
   );
}
