import java.util.Properties

plugins {
    id("com.android.application")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

// Chave de assinatura da Play Store: le de android/key.properties, que NAO
// e versionado (ver .gitignore). Gerar com:
//   keytool -genkey -v -keystore upload-keystore.jks -keyalg RSA -keysize 2048 \
//     -validity 10000 -alias upload
// Guarde o .jks e as senhas para sempre — sem eles nao da pra atualizar o
// app publicado. Ver docs/PUBLICAR.md para o passo a passo completo.
val keyPropertiesFile = rootProject.file("key.properties")
val keyProperties = Properties()
val temChaveDeAssinatura = keyPropertiesFile.exists()
if (temChaveDeAssinatura) {
    keyProperties.load(keyPropertiesFile.inputStream())
}

android {
    namespace = "com.eduardoaragao.editais_app"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    defaultConfig {
        applicationId = "com.eduardoaragao.editais_app"
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    signingConfigs {
        if (temChaveDeAssinatura) {
            create("release") {
                storeFile = file(keyProperties.getProperty("storeFile"))
                storePassword = keyProperties.getProperty("storePassword")
                keyAlias = keyProperties.getProperty("keyAlias")
                keyPassword = keyProperties.getProperty("keyPassword")
            }
        }
    }

    buildTypes {
        release {
            // Sem key.properties (ex.: build de teste local), cai nas chaves
            // de debug — `flutter build appbundle` funciona, mas o pacote
            // resultante NAO pode ser enviado a Play Store.
            signingConfig = if (temChaveDeAssinatura) {
                signingConfigs.getByName("release")
            } else {
                signingConfigs.getByName("debug")
            }
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}
