package com.husarp.recklessdriving;

import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;

import androidx.core.content.FileProvider;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * In-app updating for the Android build.
 *
 * Android will not let a sideloaded app replace itself silently - the system installer always asks
 * the player to confirm, and that is a platform guarantee, not something to work around. What this
 * removes is everything BEFORE that confirmation: no browser, no downloads folder, no hunting for
 * the file. The game fetches the APK itself and hands it straight to the installer.
 *
 * The APK goes to the app's own cache directory, which needs no storage permission, and is shared
 * through the FileProvider Capacitor already declares. A raw file:// URI would throw
 * FileUriExposedException on Android 7 and later.
 */
@CapacitorPlugin(name = "AppUpdate")
public class AppUpdatePlugin extends Plugin {

    /**
     * Batch 537: open a URL in the phone's browser.
     *
     * The game's own GITHUB button needs this because window.open() does nothing in an Android
     * WebView unless the host opts into multiple windows - so without a native route the button
     * would look fine and simply never do anything, which is the exact problem it was added to fix.
     *
     * FLAG_ACTIVITY_NEW_TASK is required: the intent is started from an Activity context but has to
     * launch the browser as its own task, or Android refuses it outright.
     */
    @PluginMethod
    public void openUrl(PluginCall call) {
        final String url = call.getString("url");
        if (url == null || url.isEmpty()) {
            call.reject("No URL was given");
            return;
        }
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            getContext().startActivity(intent);
            call.resolve();
        } catch (Exception e) {
            call.reject("Could not open the link: " + e.getMessage());
        }
    }

    @PluginMethod
    public void downloadAndInstall(PluginCall call) {
        final String url = call.getString("url");
        if (url == null || url.isEmpty()) {
            call.reject("No download URL was given");
            return;
        }

        // Checked before downloading, so a blocked permission does not waste 5 MB of the player's
        // data first. Sends them straight to the one settings screen that grants it.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                && !getContext().getPackageManager().canRequestPackageInstalls()) {
            Intent allow = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                    Uri.parse("package:" + getContext().getPackageName()));
            allow.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            getContext().startActivity(allow);
            call.reject("NEEDS_PERMISSION");
            return;
        }

        new Thread(() -> {
            HttpURLConnection conn = null;
            try {
                File apk = new File(getContext().getCacheDir(), "update.apk");
                if (apk.exists() && !apk.delete()) {
                    call.reject("Could not clear the previous download");
                    return;
                }

                conn = (HttpURLConnection) new URL(url).openConnection();
                conn.setInstanceFollowRedirects(true);   // GitHub redirects release assets to a CDN
                conn.setConnectTimeout(30000);
                conn.setReadTimeout(60000);
                conn.connect();

                int status = conn.getResponseCode();
                if (status / 100 != 2) {
                    call.reject("Download failed (HTTP " + status + ")");
                    return;
                }

                try (InputStream in = conn.getInputStream();
                     FileOutputStream out = new FileOutputStream(apk)) {
                    byte[] buffer = new byte[8192];
                    int read;
                    while ((read = in.read(buffer)) > 0) {
                        out.write(buffer, 0, read);
                    }
                }

                // A truncated download would fail to install with a confusing parser error, so
                // treat an implausibly small file as a failure here where the message can be clear.
                if (apk.length() < 100000) {
                    call.reject("The downloaded file looks incomplete (" + apk.length() + " bytes)");
                    return;
                }

                Uri uri = FileProvider.getUriForFile(
                        getContext(), getContext().getPackageName() + ".fileprovider", apk);

                Intent install = new Intent(Intent.ACTION_VIEW);
                install.setDataAndType(uri, "application/vnd.android.package-archive");
                install.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
                getContext().startActivity(install);

                JSObject result = new JSObject();
                result.put("handedToInstaller", true);
                call.resolve(result);
            } catch (Exception e) {
                call.reject(e.getMessage() != null ? e.getMessage() : e.toString());
            } finally {
                if (conn != null) conn.disconnect();
            }
        }).start();
    }
}
