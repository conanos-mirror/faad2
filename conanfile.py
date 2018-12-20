from conans import ConanFile, tools, AutoToolsBuildEnvironment,MSBuild
from conanos.build import config_scheme
import os, shutil

class Faad2Conan(ConanFile):
    name = "faad2"
    version = '2.8.8'
    description = "FAAD2 is an open source MPEG-4 and MPEG-2 AAC decoder"
    url = "https://github.com/conanos/faad2"
    homepage = "https://www.audiocoding.com/"
    license = "GPL-2+"
    msvc_projs = ["libfaad.vcxproj", "libfaad2_dll.vcxproj"]
    exports = ["COPYING"] + msvc_projs
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        url_ = 'https://nchc.dl.sourceforge.net/project/faac/faad2-src/faad2-2.8.0/faad2-{version}.tar.gz'
        tools.get( url_.format(version=self.version) )
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        if self.settings.os == 'Windows':
            for proj in self.msvc_projs:
                shutil.copy2(os.path.join(self.source_folder,proj), os.path.join(self.source_folder,self._source_subfolder,"project","msvc",proj))

    def build(self):
        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder,"project","msvc")):
                msbuild = MSBuild(self)
                msbuild.build("libfaad.vcxproj",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'})
                if self.options.shared:
                    msbuild.build("libfaad2_dll.vcxproj",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'})

        #with tools.chdir(self.source_subfolder):
        #    self.run("autoreconf -f -i")

        #    autotools = AutoToolsBuildEnvironment(self)
        #    _args = ["--prefix=%s/builddir"%(os.getcwd())]
        #    if self.options.shared:
        #        _args.extend(['--enable-shared=yes','--enable-static=no'])
        #    else:
        #        _args.extend(['--enable-shared=no','--enable-static=yes'])
        #    autotools.configure(args=_args)
        #    autotools.make(args=["-j4"])
        #    autotools.install()

    def package(self):
        #if tools.os_info.is_linux:
        #    with tools.chdir(self.source_subfolder):
        #        self.copy("*", src="%s/builddir"%(os.getcwd()))
        if self.options.shared:
            platforms={'x86': 'Win32', 'x86_64': 'x64'}
            output_rpath = os.path.join("project","msvc",platforms.get(str(self.settings.arch)), str(self.settings.build_type))
            self.copy("libfaad2_dll.*", dst=os.path.join(self.package_folder,"lib"),
                      src=os.path.join(self.build_folder, self._source_subfolder, output_rpath), excludes=["libfaad2_dll.dll","libfaad2_dll.tlog"])
            self.copy("libfaad2_dll.dll", dst=os.path.join(self.package_folder,"bin"),
                      src=os.path.join(self.build_folder, self._source_subfolder, output_rpath))
        else:
            self.copy("libfaad.*", dst=os.path.join(self.package_folder,"lib"),
                      src=os.path.join(self.build_folder, self._source_subfolder, output_rpath), excludes=["libfaad.tlog"])

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

