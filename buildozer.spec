[app]

# (str) Title of your application
title = Asystent NK Dzielnicowego

# (str) Package name
package.name = asystent_nk

# (str) Package domain (needed for android/ios packaging)
package.domain = org.asystent.nk

# (source.dir) Source code where the main.py live
source.dir = .

# (source.include_exts) Source include extensions (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (version) Application versioning (method 1)
version = 1.0.0

# (string) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma seperated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,flet,sqlite3
android.enable_androidx = False

# (str) Supported orientation (landscape, sensorLandscape, portrait or sensorPortrait)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash of the application (image)
#presplash.filename = %(source.dir)s/data/presplash.png

# (string) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android app theme, default is ok for Kivy-based app
# android.theme = "@android:style/Theme.NoTitleBar"

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) Enable AndroidX support
#android.enable_androidx = True

# (bool) Add Java classes from .jar files in the libs folder
#android.add_src =

# (list) Pattern to whitelist for the whole project
#android.whitelist = lib-dynload/termios.so

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .so files to add to the libs so that they can be used by other Java classes:
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/androidv7/*.so
#android.add_libs_arm64_v8a = libs/android64/*.so

# (bool) Enable AndroidX support
#android.gradle_dependencies =

# (list) Java files to add to the android project (can be java or a directory)
#android.add_src =

# (list) Gradle dependencies
#android.gradle_dependencies =

# (list) Java classes to add as services to the manifest:
#android.services = org.test.myservice.MyService

# (list) Java classes to add as broadcast receivers:
#android.receivers = 

# (str) Java classes for OUYA console
#android.ouya.category = GAME
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) Launch message
#android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
#android.archs = arm64-v8a

# (int) overrides automatic versionCode (used in build.gradle)
# this is not the same as app version and should only be edited if you know what you're doing
# android.version_code = 1

# (list) Pattern to whitelist for the whole project
#android.whitelist = lib-dynload/termios.so

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .so files to add to the libs so that they can be used by other Java classes:
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/androidv7/*.so
#android.add_libs_arm64_v8a = libs/android64/*.so

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning (and wait for confirmation) when buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. where to put the built APK)
# bin_dir = ./bin

