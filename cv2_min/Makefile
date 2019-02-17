# This approach was informed by https://www.learnopencv.com/how-to-convert-your-opencv-c-code-into-a-python-module/. Avoids cmake hassle.
# Advice on getting the C++ code right can be found in the OpenCV-Python Bindings tutorial here: https://github.com/opencv/opencv/blob/3.2.0/doc/py_tutorials/py_bindings/py_bindings_basics/py_bindings_basics.markdown#how-to-extend-new-modules-to-python - it documents the CV_EXPORT* macros that mark declarations in .hpp files for exporting to Python.
BUILD=build
OPENCV_VERSION=3.2.0
# the module name is inferred from the current directory so it must be snake_case
NAME:=$(notdir $(CURDIR))

test: $(BUILD)/$(NAME).so
	PYTHONPATH=$(BUILD) ./test.py

$(BUILD)/$(NAME).so: $(BUILD)/cv2.cpp $(BUILD)/gen2.py $(BUILD)/hdr_parser.py $(BUILD)/pycompat.hpp
	ls -1 $(CURDIR)/*.hpp | tr '\n' ';' | head -c -1 > $(BUILD)/headers.txt
	sed -i "s|hdr\\[.*'opencv2/'.*\\]|hdr.split('cv2_min/')[1]|g" $(BUILD)/gen2.py # hack gen2.py's expectation on the module whereabouts
	sed -i -r "s/(ns_name.*)'cv'/\\1'$(NAME)'/g" $(BUILD)/gen2.py # hack the namespace
	python3 $(BUILD)/gen2.py $(BUILD) $(BUILD)/headers.txt PYTHON3
	touch $(BUILD)/pyopencv_custom_headers.h # hack cv2.cpp's expectation on this file to exist
	sed -i 's/"cv2"/"$(NAME)"/g' $(BUILD)/cv2.cpp # hack the MODULESTR
	sed -i 's/PyInit_cv2/PyInit_$(NAME)/g' $(BUILD)/cv2.cpp # hack the module export function
	sed -i 's/^  PUBLISH.*//g' $(BUILD)/cv2.cpp # hack away unwanted constants
	sed -i 's/^    special_methods.*//g' $(BUILD)/cv2.cpp # hack away unwanted methods
	sed -i 's/"Python wrapper for OpenCV."/"Python wrapper for $(NAME) C++ thingy based on OpenCV."/g' $(BUILD)/cv2.cpp # hack the docstring
	g++ -shared -rdynamic -g -O3 -Wall -fPIC \
		$(BUILD)/cv2.cpp *.cpp -I. \
		`pkg-config --cflags --libs opencv` \
		`python3-config --includes --ldflags` \
		-o $@

$(BUILD)/cv2.cpp: $(BUILD)
	wget -O $@ https://raw.githubusercontent.com/opencv/opencv/$(OPENCV_VERSION)/modules/python/src2/cv2.cpp

$(BUILD)/gen2.py: $(BUILD)
	wget -O $@ https://raw.githubusercontent.com/opencv/opencv/$(OPENCV_VERSION)/modules/python/src2/gen2.py

$(BUILD)/hdr_parser.py: $(BUILD)
	wget -O $@ https://raw.githubusercontent.com/opencv/opencv/$(OPENCV_VERSION)/modules/python/src2/hdr_parser.py

$(BUILD)/pycompat.hpp: $(BUILD)
	wget -O $@ https://raw.githubusercontent.com/opencv/opencv/$(OPENCV_VERSION)/modules/python/src2/pycompat.hpp

$(BUILD):
	mkdir $@

.PHONY: clean

clean:
	rm -r $(BUILD)
