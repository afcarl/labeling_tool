all: pdef sign

pdef:
	ppackage -i ./ build.pdef 

packp:
	packp3d -o labeltool.p3d -d ./src -r morepy -r tk

sign: 
	multify -S rll.crt -uvf labeltool.p3d

extract:
	multify -x -v -C extracted -f labeltool.p3d

repack:
	multify -v -c extracted -f labeltool.p3d 

run: 
	panda3d labeltool.p3d

