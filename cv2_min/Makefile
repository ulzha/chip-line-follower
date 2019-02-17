BUILD=build
OPENCV_VERSION=3.2.0
# the module name is inferred from the current directory; it must be a valid Python identifier and also match the cpp file name
NAME:=$(notdir $(CURDIR))
FILES=$(BUILD)/cv2.cpp $(BUILD)/gen2.py $(BUILD)/hdr_parser.py $(BUILD)/pycompat.hpp

$(BUILD)/$(NAME).so: $(FILES)
	mkdir -p $(BUILD)/opencv2 # gen.py has opencv2/ hardcoded as the headers directory
	cp *.hpp $(BUILD)/opencv2
	ls -1 $(BUILD)/opencv2/*.hpp | tr '\n' ';' | head -c -1 > $(BUILD)/headers.txt
	sed -i -r "s/(ns_name.*)'cv'/\\1'$(NAME)'/g" $(BUILD)/gen2.py # hack the namespace
	python3 $(BUILD)/gen2.py $(BUILD) $(BUILD)/headers.txt PYTHON3
	touch $(BUILD)/pyopencv_custom_headers.h # hack cv2.cpp's expectation on this file to exist
	sed -i 's/"cv2"/"$(NAME)"/g' $(BUILD)/cv2.cpp # hack the MODULESTR
	sed -i 's/PyInit_cv2/PyInit_$(NAME)/g' $(BUILD)/cv2.cpp # hack the module export function
	# TODO hack the docstring
	g++ -shared -rdynamic -g -O3 -Wall -fPIC \
		$(BUILD)/cv2.cpp $(NAME).cpp \
		`pkg-config --cflags --libs opencv` \
		`python3-config --includes --ldflags` \
		-Wno-unused-function \
		-o $@
		# -DNDEBUG -DPY_MAJOR_VERSION=3 \
		# -DMODULE_STR=$(NAME) \

$(BUILD)/cv2.cpp: $(BUILD)
	wget -O $@ https://raw.githubusercontent.com/opencv/opencv/$(OPENCV_VERSION)/modules/python/src2/cv2.cpp

$(BUILD)/gen2.py: $(BUILD)
	wget -O $@ https://raw.githubusercontent.com/opencv/opencv/$(OPENCV_VERSION)/modules/python/src2/gen2.py

$(BUILD)/hdr_parser.py: $(BUILD)
	wget -O $@ https://raw.githubusercontent.com/opencv/opencv/$(OPENCV_VERSION)/modules/python/src2/hdr_parser.py

$(BUILD)/pycompat.hpp: $(BUILD)
	wget -O $@ https://raw.githubusercontent.com/opencv/opencv/$(OPENCV_VERSION)/modules/python/src2/pycompat.hpp

$(BUILD):
	mkdir $(BUILD)

.PHONY: clean

clean:
	rm -r $(BUILD)
