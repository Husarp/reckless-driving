package com.husarp.recklessdriving;

import android.app.DownloadManager;
import android.content.Context;
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
 * Batch 582, direct decision: the game downloads the new APK over its OWN connection (progress through
 * progress()) and hands it to Android's installer itself. That needs "allow Reckless Driving to install
 * unknown apps" once. Batch 579 tried Android's download service with the player opening the file from
 * Downloads instead: it still needed the same permission (for the Files / Downloads app), took more taps,
 * and on a phone with a firewall the download service never started at all. This is how sideloaded apps
 * that update themselves (Signal's and Telegram's website builds, F-Droid) do it.
 *
 * Android still shows its own "Update?" confirmation - a sideloaded app can never replace itself
 * silently - and only an APK signed with the same key installs over this one.
 *
 * The APK goes to the app's own cache directory, which needs no storage permission, and is shared through
 * the FileProvider Capacitor already declares. A raw file:// URI would throw FileUriExposedException on
 * Android 7 and later.
 */
@CapacitorPlugin(name = "AppUpdate")
public class AppUpdatePlugin extends Plugin {

    // one download at a time; written by the download thread, read by progress()
    private volatile String dlStatus = "idle";   // idle / running / done / failed
    private volatile long dlDone = 0, dlTotal = -1;
    private volatile String dlError = null;

    private File apkFile() {
        return new File(getContext().getCacheDir(), "update.apk");
    }

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

    /** Starts downloading `url` into the cache. Resolves at once; progress() tells how it goes. */
    @PluginMethod
    public void download(PluginCall call) {
        final String url = call.getString("url");
        if (url == null || url.isEmpty()) {
            call.reject("No download URL was given");
            return;
        }
        if (!"running".equals(dlStatus)) {
            dlStatus = "running";
            dlDone = 0;
            dlTotal = -1;
            dlError = null;
            new Thread(() -> {
                HttpURLConnection conn = null;
                try {
                    File apk = apkFile();
                    if (apk.exists() && !apk.delete()) throw new Exception("Could not clear the previous download");

                    conn = (HttpURLConnection) new URL(url).openConnection();
                    conn.setInstanceFollowRedirects(true);   // GitHub redirects release files to a CDN
                    conn.setConnectTimeout(30000);
                    conn.setReadTimeout(60000);
                    conn.connect();

                    int status = conn.getResponseCode();
                    if (status / 100 != 2) throw new Exception("Download failed (HTTP " + status + ")");
                    dlTotal = conn.getContentLength();

                    try (InputStream in = conn.getInputStream();
                         FileOutputStream out = new FileOutputStream(apk)) {
                        byte[] buffer = new byte[8192];
                        int read;
                        while ((read = in.read(buffer)) > 0) {
                            out.write(buffer, 0, read);
                            dlDone += read;
                        }
                    }

                    // A truncated download would fail to install with a confusing parser error, so
                    // treat an implausibly small file as a failure here where the message can be clear.
                    if (apk.length() < 100000) {
                        throw new Exception("The downloaded file looks incomplete (" + apk.length() + " bytes)");
                    }
                    dlStatus = "done";
                } catch (Exception e) {
                    dlError = e.getMessage() != null ? e.getMessage() : e.toString();
                    dlStatus = "failed";
                } finally {
                    if (conn != null) conn.disconnect();
                }
            }).start();
        }
        call.resolve();
    }

    /** How the download is doing: status running / done / failed, and its bytes so far out of the whole. */
    @PluginMethod
    public void progress(PluginCall call) {
        JSObject o = new JSObject();
        o.put("status", dlStatus);
        o.put("done", dlDone);
        o.put("total", dlTotal);
        if (dlError != null) o.put("error", dlError);
        call.resolve(o);
    }

    /**
     * Hands the downloaded APK to Android's installer. Without the "install unknown apps" permission it
     * rejects with NEEDS_PERMISSION - and, when `openSettings` is true, first opens the one settings
     * screen that grants it. The game calls it again, with openSettings false, when the player comes back.
     */
    @PluginMethod
    public void install(PluginCall call) {
        File apk = apkFile();
        if (!apk.exists()) {
            call.reject("The downloaded update is gone - press UPDATE again");
            return;
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                && !getContext().getPackageManager().canRequestPackageInstalls()) {
            if (call.getBoolean("openSettings", true)) {
                Intent allow = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                        Uri.parse("package:" + getContext().getPackageName()));
                allow.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                getContext().startActivity(allow);
            }
            call.reject("NEEDS_PERMISSION");
            return;
        }
        try {
            Uri uri = FileProvider.getUriForFile(
                    getContext(), getContext().getPackageName() + ".fileprovider", apk);
            Intent install = new Intent(Intent.ACTION_VIEW);
            install.setDataAndType(uri, "application/vnd.android.package-archive");
            install.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
            getContext().startActivity(install);
            call.resolve();
        } catch (Exception e) {
            call.reject(e.getMessage() != null ? e.getMessage() : e.toString());
        }
    }

    /**
     * The downloaded file gone - the new version runs, so the file that brought it is not needed. A
     * numeric `id` is a download from 3.34.0-3.34.2, which used Android's download service: that one is
     * cancelled too, with its file in Downloads (on a phone where it never started, it would otherwise
     * sit in the queue for good).
     */
    @PluginMethod
    public void remove(PluginCall call) {
        try {
            DownloadManager m = (DownloadManager) getContext().getSystemService(Context.DOWNLOAD_SERVICE);
            if (m != null) m.remove(Long.parseLong(call.getString("id", "")));
        } catch (RuntimeException e) {
            // not a download-service id, or gone already
        }
        apkFile().delete();
        call.resolve();
    }
}
