# buildozer.spec - Có Backup/Share
[app]
title = SA LI GRID LIMIT
package.name = saligrid
package.domain = org.saligrid

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,zip

version = 0.3
requirements = python3,kivy==2.3.0,kivymd==1.2.0,plyer==2.1.0

[buildozer]
log_level = 2

[app]
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

android.enable_androidx = True

[p4a]
archs = arm64-v8a
