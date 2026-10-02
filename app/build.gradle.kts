plugins {
    id("com.android.application")
}

android {
    namespace = "com.adot.holdemcoach"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.adot.holdemcoach"
        minSdk = 26
        targetSdk = 34
        versionCode = (System.getenv("GITHUB_RUN_NUMBER") ?: "1").toInt()
        versionName = "1.0." + (System.getenv("GITHUB_RUN_NUMBER") ?: "0")
    }

    // One fixed key for every build, so a new APK installs over the old one and keeps your saved game.
    // It is a personal sideload key, not meant for the Play Store.
    signingConfigs {
        create("holdem") {
            storeFile = file("holdem.keystore")
            storePassword = "holdemcoach"
            keyAlias = "holdem"
            keyPassword = "holdemcoach"
        }
    }

    buildTypes {
        getByName("debug") {
            signingConfig = signingConfigs.getByName("holdem")
        }
        getByName("release") {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("holdem")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation("androidx.webkit:webkit:1.12.1")
}
