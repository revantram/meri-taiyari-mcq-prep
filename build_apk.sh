#!/usr/bin/env bash
set -e

APP_DIR="/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app"
BUILD_DIR="${APP_DIR}/build"
ANDROID_JAR="/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/yuva-shakti-apk-build/android.jar"
KEYSTORE="/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/yuva-shakti-apk-build/release.keystore"

echo "==> 🧹 Setting up build workspace in ${BUILD_DIR}..."
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}/bin/classes" "${BUILD_DIR}/bin/dex" "${BUILD_DIR}/gen" "${BUILD_DIR}/res"

echo "==> 📦 Copying resources and assets..."
cp -r "${APP_DIR}/android/res/"* "${BUILD_DIR}/res/"
cp -r "${APP_DIR}/assets" "${BUILD_DIR}/assets"
cp "${APP_DIR}/android/AndroidManifest.xml" "${BUILD_DIR}/AndroidManifest.xml"

cd "${BUILD_DIR}"

echo "==> ⚙️ Compiling resources with AAPT2..."
aapt2 compile --dir res -o res.zip
aapt2 link -I "${ANDROID_JAR}" --manifest AndroidManifest.xml -o bin/base.apk -A assets --java gen res.zip

echo "==> ☕ Compiling Java sources..."
javac --release 8 -cp "${ANDROID_JAR}:gen" -d bin/classes "${APP_DIR}/android/src/com/meritaiyari/app/MainActivity.java" gen/com/meritaiyari/app/R.java

echo "==> ⚡ Converting to Dalvik Executable (DEX)..."
find bin/classes -name "*.class" | xargs d8 --lib "${ANDROID_JAR}" --output bin/dex/

echo "==> 📁 Packaging classes.dex..."
cd bin/dex
zip -u ../base.apk classes.dex
cd "${BUILD_DIR}"

echo "==> ✍️ Signing APK with apksigner..."
apksigner sign --ks "${KEYSTORE}" --ks-pass pass:yuvashakti123 --ks-key-alias yuvashakti --key-pass pass:yuvashakti123 --out "${APP_DIR}/MeriTaiyari_MCQ_Prep.apk" bin/base.apk

echo "==> 🚚 Copying to Download directory..."
mkdir -p /sdcard/Download 2>/dev/null || true
cp "${APP_DIR}/MeriTaiyari_MCQ_Prep.apk" /sdcard/Download/MeriTaiyari_MCQ_Prep.apk 2>/dev/null || true

echo "==> ✅ Android APK Successfully Built!"
ls -lh "${APP_DIR}/MeriTaiyari_MCQ_Prep.apk"
