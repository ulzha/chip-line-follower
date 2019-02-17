BUILD=build
OPENCV_VERSION=3.2.0
FILES=$(BUILD)/cv2.cpp $(BUILD)/gen2.py $(BUILD)/hdr_parser.py $(BUILD)/pycompat.hpp

$(BUILD)/cv2_min.so: $(FILES)
	mkdir -p $(BUILD)/opencv2 # gen.py has opencv2/ hardcoded as the headers directory
	cp *.hpp $(BUILD)/opencv2
	ls -1 $(BUILD)/opencv2/*.hpp | tr '\n' ';' | head -c -1 > $(BUILD)/headers.txt
	sed -i -r "s/(ns_name.*)'cv'/\\1'cv2_min'/g" $(BUILD)/gen2.py # hack the namespace
	python3 $(BUILD)/gen2.py $(BUILD) $(BUILD)/headers.txt PYTHON3
	touch $(BUILD)/pyopencv_custom_headers.h # cv2.cpp has this name hardcoded
	sed -i 's/"cv2"/"cv2_min"/g' $(BUILD)/cv2.cpp # hack the MODULESTR
	sed -i 's/PyInit_cv2/PyInit_cv2_min/g' $(BUILD)/cv2.cpp # hack the module export function
	# TODO hack the docstring
	g++ -shared -rdynamic -g -O3 -Wall -fPIC \
		$(BUILD)/cv2.cpp cv2_min.cpp \
		`pkg-config --cflags --libs opencv` \
		`python3-config --includes --ldflags` \
		-Wno-unused-function \
		-o $@
		# -DNDEBUG -DPY_MAJOR_VERSION=3 \
		# -DMODULE_STR=cv2_min \

$(BUILD)/cv2.cpp: build
	wget -O $@ https://raw.githubusercontent.com/opencv/opencv/$(OPENCV_VERSION)/modules/python/src2/cv2.cpp

$(BUILD)/gen2.py: build
	wget -O $@ https://raw.githubusercontent.com/opencv/opencv/$(OPENCV_VERSION)/modules/python/src2/gen2.py

$(BUILD)/hdr_parser.py: build
	wget -O $@ https://raw.githubusercontent.com/opencv/opencv/$(OPENCV_VERSION)/modules/python/src2/hdr_parser.py

$(BUILD)/pycompat.hpp: build
	wget -O $@ https://raw.githubusercontent.com/opencv/opencv/$(OPENCV_VERSION)/modules/python/src2/pycompat.hpp

$(BUILD):
	mkdir $(BUILD)

.PHONY: clean

clean:
	rm -r $(BUILD)
