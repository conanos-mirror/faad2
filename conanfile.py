from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from shutil import copyfile
import os

class Faad2Conan(ConanFile):
    name = "faad2"
    version = "2.7"
    description = "FAAD2 is an open source MPEG-4 and MPEG-2 AAC decoder"
    url = "https://github.com/conan-multimedia/faad2"
    homepage = "https://www.audiocoding.com/faad2.html"
    license = "GPLv2Plus"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    source_subfolder = "source_subfolder"

    def source(self):
        tools.get('http://sourceforge.net/projects/faac/files/faad2-src/{name}-{version}/{name}-{version}.tar.bz2'.format(name=self.name, version=self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):        
        with tools.chdir(self.source_subfolder):
            self.run("autoreconf -f -i")

            autotools = AutoToolsBuildEnvironment(self)
            _args = ["--prefix=%s/builddir"%(os.getcwd())]
            if self.options.shared:
                _args.extend(['--enable-shared=yes','--enable-static=no'])
            else:
                _args.extend(['--enable-shared=no','--enable-static=yes'])
            autotools.configure(args=_args)
            autotools.make(args=["-j4"])
            autotools.install()

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

